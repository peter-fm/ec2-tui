"""Combined controls bar with region selector and filters."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input, Select, Static

from .filter_bar import FilterChanged
from .region_selector import RegionChanged
from ..services.ec2_service import EC2Service


class ControlsBar(Horizontal):
    """Combined controls bar for region, name filter, and status filter."""

    def __init__(self, default_region: str = "eu-west-1") -> None:
        """Initialize controls bar."""
        super().__init__()
        self.default_region = default_region

    def compose(self) -> ComposeResult:
        """Compose controls bar widgets."""
        # Region selector
        regions = EC2Service.get_available_regions()
        yield Static("Region:", classes="control-label")
        yield Select(
            [(region, region) for region in regions],
            value=self.default_region,
            id="region-select",
            classes="region-select",
        )

        # Name filter
        yield Static("Filter:", classes="control-label")
        yield Input(placeholder="Instance name...", id="name-filter", classes="name-filter")

        # Status filter
        yield Static("Status:", classes="control-label")
        yield Select(
            [
                ("All", "all"),
                ("Running", "running"),
                ("Stopped", "stopped"),
                ("Pending", "pending"),
                ("Stopping", "stopping"),
            ],
            value="all",
            id="status-filter",
            classes="status-select",
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        if event.input.id == "name-filter":
            self.post_message(FilterChanged(name_filter=event.value, status_filter=None))

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changes."""
        if event.select.id == "status-filter":
            self.post_message(FilterChanged(name_filter=None, status_filter=str(event.value)))
        elif event.select.id == "region-select":
            self.post_message(RegionChanged(str(event.value)))
