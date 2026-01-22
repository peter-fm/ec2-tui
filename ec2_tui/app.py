"""Main EC2 TUI application."""

import asyncio
from typing import Optional

from textual import work
from textual.app import App
from textual.reactive import reactive

from .config import Config, load_config, save_config
from .models.instance import Instance
from .screens.main_screen import MainScreen
from .services.ec2_service import EC2Service
from .services.notification_service import NotificationService
from .services.retry_service import (
    RetryService,
    RetryTaskCancelled,
    RetryTaskCompleted,
    RetryTaskUpdated,
)
from .utils.exceptions import (
    AWSError,
    ConfigurationError,
    InsufficientCapacityError,
    ValidationError,
)
from .utils.theme import get_textual_theme, watch_theme_changes
from .widgets.filter_bar import FilterChanged
from .widgets.instance_table import InstanceTable
from .widgets.instance_type_modal import InstanceTypeModal
from .widgets.region_selector import RegionChanged
from .widgets.retry_panel import RetryPanel


class EC2TUIApp(App):
    """EC2 TUI application."""

    TITLE = "EC2 TUI Manager"
    CSS_PATH = "app.tcss"

    # Reactive attributes
    instances: reactive[list[Instance]] = reactive(list, init=False)
    current_region: reactive[str] = reactive("", init=False)
    name_filter: reactive[str] = reactive("", init=False)
    status_filter: reactive[str] = reactive("all", init=False)

    def __init__(self, profile: Optional[str] = None, region: Optional[str] = None):
        """Initialize application.

        Args:
            profile: AWS CLI profile name (overrides config file).
            region: AWS region (overrides config file).
        """
        super().__init__()

        # Load configuration first
        try:
            self.config = load_config()
        except ConfigurationError as e:
            print(f"Configuration error: {e}")
            self.config = Config()

        # Override config with CLI arguments
        if profile is not None:
            self.config.aws.profile = profile
        if region is not None:
            self.config.ui.default_region = region

        # Set initial region
        self.current_region = self.config.ui.default_region

        # Initialize services
        self.ec2_service: Optional[EC2Service] = None
        self.notification_service = NotificationService(
            enabled=self.config.notifications.enabled,
            urgency=self.config.notifications.urgency,
        )
        self.retry_service: Optional[RetryService] = None

        # Auto-refresh timer
        self.refresh_timer: Optional[asyncio.Task] = None

    def on_mount(self) -> None:
        """Initialize app on mount."""
        # Set theme based on configuration (must be done after app is mounted)
        self.theme = get_textual_theme(self.config.ui.theme)

        # Initialize services with current region
        self._initialize_services()

        # Push main screen with configured default region
        self.push_screen(MainScreen(default_region=self.current_region))

        # Start auto-refresh timer
        if self.config.ui.refresh_interval_seconds > 0:
            self.set_interval(
                self.config.ui.refresh_interval_seconds,
                self.refresh_instances,
            )

        # Start retry panel update timer (update every second for countdown)
        self.set_interval(1, self._update_retry_panel)

        # Start theme watcher
        asyncio.create_task(watch_theme_changes(self))

    def _initialize_services(self) -> None:
        """Initialize EC2 and retry services."""
        try:
            self.ec2_service = EC2Service(
                region=self.current_region,
                profile=self.config.aws.profile,
            )
            self.retry_service = RetryService(
                ec2_service=self.ec2_service,
                notification_service=self.notification_service,
                interval_seconds=self.config.retry.interval_seconds,
                max_attempts=self.config.retry.max_attempts,
            )
            self.retry_service.set_app(self)

        except ConfigurationError as e:
            self.notify(str(e), severity="error", timeout=10)
            self.exit(1)

    @work(exclusive=True)
    async def refresh_instances(self) -> None:
        """Refresh instance list from AWS."""
        if self.ec2_service is None:
            return

        try:
            # Try to get the table, but don't fail if it's not mounted yet
            try:
                # Query from the current screen, not the app
                screen = self.screen
                table = screen.query_one(InstanceTable)
                table.loading = True
            except Exception:
                table = None

            # Fetch instances
            instances = await asyncio.to_thread(
                self.ec2_service.list_instances,
                name_filter=self.name_filter,
                status_filter=self.status_filter,
            )

            # Update reactive state
            self.instances = instances

            # Update table if available
            if table is not None:
                table.update_instances(instances)
                table.loading = False

        except AWSError as e:
            self.notify(f"Error fetching instances: {e}", severity="error")
            try:
                table = self.screen.query_one(InstanceTable)
                table.loading = False
            except Exception:
                pass

    @work
    async def start_instance(self, instance_id: str, instance_name: str) -> None:
        """Start an EC2 instance."""
        if self.ec2_service is None:
            return

        self.notify(f"Starting instance {instance_name}...", severity="information")

        try:
            await asyncio.to_thread(self.ec2_service.start_instance, instance_id)
            self.notify(f"Started instance {instance_name}", severity="information")
            await asyncio.sleep(2)  # Wait for state to update
            self.refresh_instances()

        except InsufficientCapacityError as e:
            if self.config.retry.enabled and self.retry_service is not None:
                # Schedule retry
                task_id = self.retry_service.schedule_retry(instance_id, instance_name)
                self.notify(
                    f"Insufficient capacity. Retrying every {self.config.retry.interval_seconds}s",
                    severity="warning",
                )
                self._update_retry_panel()
            else:
                self.notify(str(e), severity="error")

        except AWSError as e:
            self.notify(f"Error starting instance: {e}", severity="error")

    @work
    async def stop_instance(self, instance_id: str, instance_name: str) -> None:
        """Stop an EC2 instance."""
        if self.ec2_service is None:
            return

        self.notify(f"Stopping instance {instance_name}...", severity="information")

        try:
            await asyncio.to_thread(self.ec2_service.stop_instance, instance_id)
            self.notify(f"Stopped instance {instance_name}", severity="information")
            await asyncio.sleep(2)  # Wait for state to update
            self.refresh_instances()

        except AWSError as e:
            self.notify(f"Error stopping instance: {e}", severity="error")

    @work
    async def change_instance_type(
        self, instance_id: str, instance_name: str, new_type: str
    ) -> None:
        """Change instance type."""
        if self.ec2_service is None:
            return

        try:
            # Validate instance type
            is_valid = await asyncio.to_thread(
                self.ec2_service.validate_instance_type, new_type
            )

            if not is_valid:
                self.notify(
                    f"Instance type '{new_type}' not found or invalid",
                    severity="error",
                )
                return

            # Change instance type
            await asyncio.to_thread(
                self.ec2_service.change_instance_type, instance_id, new_type
            )

            # Save to config if not already there
            if new_type not in self.config.saved_instance_types.types:
                self.config.save_instance_type(new_type)
                save_config(self.config)

            self.notify(
                f"Changed {instance_name} to {new_type}",
                severity="information",
            )
            await asyncio.sleep(1)
            self.refresh_instances()

        except ValidationError as e:
            self.notify(str(e), severity="error")
        except AWSError as e:
            self.notify(f"Error changing instance type: {e}", severity="error")

    def _update_retry_panel(self) -> None:
        """Update retry panel with current retry tasks."""
        if self.retry_service is None:
            return

        try:
            retry_panel = self.screen.query_one(RetryPanel)
            retry_tasks = self.retry_service.get_active_retries()
            retry_panel.update_retry_tasks(retry_tasks)
        except Exception:
            pass  # Panel might not be mounted yet

    def on_retry_task_updated(self, message: RetryTaskUpdated) -> None:
        """Handle retry task update."""
        self._update_retry_panel()

    def on_retry_task_completed(self, message: RetryTaskCompleted) -> None:
        """Handle retry task completion."""
        self._update_retry_panel()
        if message.success:
            self.refresh_instances()

    def on_retry_task_cancelled(self, message: RetryTaskCancelled) -> None:
        """Handle retry task cancellation."""
        self._update_retry_panel()

    def on_filter_changed(self, message: FilterChanged) -> None:
        """Handle filter changes."""
        if message.name_filter is not None:
            self.name_filter = message.name_filter
        if message.status_filter is not None:
            self.status_filter = message.status_filter
        self.refresh_instances()

    def on_region_changed(self, message: RegionChanged) -> None:
        """Handle region changes."""
        # Check if there are active retries
        if self.retry_service and self.retry_service.get_active_retries():
            # Cancel all retries
            self.retry_service.cancel_all()
            self.notify("All retries cancelled due to region change", severity="warning")

        # Update region
        self.current_region = message.region

        # Reinitialize services
        self._initialize_services()

        # Refresh instances
        self.refresh_instances()

    def action_start_instance(self) -> None:
        """Start selected instance."""
        table = self.screen.query_one(InstanceTable)
        instance = table.get_selected_instance()

        if instance is None:
            self.notify("No instance selected", severity="warning")
            return

        if instance.state == "running":
            self.notify("Instance is already running", severity="warning")
            return

        self.start_instance(instance.instance_id, instance.name)

    def action_stop_instance(self) -> None:
        """Stop selected instance."""
        table = self.screen.query_one(InstanceTable)
        instance = table.get_selected_instance()

        if instance is None:
            self.notify("No instance selected", severity="warning")
            return

        if instance.state == "stopped":
            self.notify("Instance is already stopped", severity="warning")
            return

        self.stop_instance(instance.instance_id, instance.name)

    def action_change_type(self) -> None:
        """Show instance type change modal."""
        table = self.screen.query_one(InstanceTable)
        instance = table.get_selected_instance()

        if instance is None:
            self.notify("No instance selected", severity="warning")
            return

        if instance.state != "stopped":
            self.notify(
                "Instance must be stopped to change type",
                severity="error",
            )
            return

        # Show modal
        modal = InstanceTypeModal(
            instance_id=instance.instance_id,
            instance_name=instance.name,
            current_type=instance.instance_type,
            saved_types=self.config.saved_instance_types.types,
        )

        def handle_modal_result(result: str | None) -> None:
            if result:
                self.change_instance_type(
                    instance.instance_id, instance.name, result
                )

        self.push_screen(modal, handle_modal_result)

    def action_cancel_retry(self) -> None:
        """Cancel active retry for selected instance."""
        table = self.screen.query_one(InstanceTable)
        instance = table.get_selected_instance()

        if instance is None or self.retry_service is None:
            return

        # Find retry task for this instance
        retries = self.retry_service.get_active_retries()
        for task_id, task in retries.items():
            if task.instance_id == instance.instance_id:
                self.retry_service.cancel_retry(task_id)
                self.notify(f"Cancelled retry for {instance.name}", severity="information")
                self._update_retry_panel()
                return

    # Keyboard bindings
    BINDINGS = [
        ("s", "start_instance", "Start"),
        ("S", "stop_instance", "Stop"),
        ("t", "change_type", "Change Type"),
        ("r", "refresh_instances", "Refresh"),
        ("f5", "refresh_instances", "Refresh"),
        ("c", "cancel_retry", "Cancel Retry"),
        ("q", "quit", "Quit"),
    ]


def main(profile: Optional[str] = None, region: Optional[str] = None) -> None:
    """Main entry point.

    Args:
        profile: AWS CLI profile name (overrides config file).
        region: AWS region (overrides config file).
    """
    app = EC2TUIApp(profile=profile, region=region)
    app.run()


if __name__ == "__main__":
    main()
