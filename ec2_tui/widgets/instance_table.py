"""Instance table widget for displaying EC2 instances."""

from textual.reactive import reactive
from textual.widgets import DataTable

from ..models.instance import Instance


class InstanceTable(DataTable):
    """DataTable widget for displaying EC2 instances."""

    instances: reactive[list[Instance]] = reactive(list)
    loading: reactive[bool] = reactive(False)

    def on_mount(self) -> None:
        """Initialize table on mount."""
        self.cursor_type = "row"
        self.zebra_stripes = True

        # Add columns
        self.add_columns(
            "Name",
            "Instance ID",
            "Status",
            "Type",
            "Internal IP",
            "AZ",
        )

        # Trigger initial data load after mounting is complete
        self.call_after_refresh(self.app.refresh_instances)

    def watch_instances(self, instances: list[Instance]) -> None:
        """Update table when instances change."""
        self.clear()

        if not instances:
            # Add a placeholder row when no instances
            self.add_row(
                "No instances found",
                "-",
                "-",
                "-",
                "-",
                "-",
                key="no-instances",
            )
        else:
            for instance in instances:
                self.add_row(
                    instance.name,
                    instance.instance_id,
                    instance.state,
                    instance.instance_type,
                    instance.private_ip or "-",
                    instance.availability_zone or "-",
                    key=instance.instance_id,
                )

    def watch_loading(self, loading: bool) -> None:
        """Update loading state."""
        if loading:
            self.loading = True
        else:
            self.loading = False

    def get_selected_instance_id(self) -> str | None:
        """Get the currently selected instance ID."""
        if self.cursor_row >= 0 and self.cursor_row < len(self.instances):
            return self.instances[self.cursor_row].instance_id
        return None

    def get_selected_instance(self) -> Instance | None:
        """Get the currently selected instance."""
        if self.cursor_row >= 0 and self.cursor_row < len(self.instances):
            return self.instances[self.cursor_row]
        return None

    def update_instances(self, instances: list[Instance]) -> None:
        """Update the instances list."""
        self.instances = instances
