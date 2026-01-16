"""Region selector widget."""

from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Select, Static

from ..services.ec2_service import EC2Service


class RegionChanged(Message):
    """Message posted when region changes."""

    def __init__(self, region: str) -> None:
        """Initialize message."""
        self.region = region
        super().__init__()


class RegionSelector(Horizontal):
    """Widget for selecting AWS region."""

    def __init__(self, default_region: str = "eu-west-1"):
        """Initialize region selector with default region."""
        super().__init__()
        self.default_region = default_region
        self._suppress_change_event = False

    def compose(self):
        """Compose region selector."""
        regions = EC2Service.get_available_regions()
        yield Static("Region:", classes="region-label")
        yield Select(
            [(region, region) for region in regions],
            value=self.default_region,
            id="region-select",
        )

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle region selection change."""
        if event.select.id == "region-select" and not self._suppress_change_event:
            self.post_message(RegionChanged(str(event.value)))

    def set_region(self, region: str) -> None:
        """Set the selected region without triggering change event."""
        self._suppress_change_event = True
        try:
            select = self.query_one("#region-select", Select)
            select.value = region
        finally:
            self._suppress_change_event = False
