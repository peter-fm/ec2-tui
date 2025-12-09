"""Filter bar widget for filtering instances."""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Input, Select, Static


class FilterBar(Horizontal):
    """Filter bar for filtering EC2 instances."""

    def compose(self) -> ComposeResult:
        """Compose filter bar widgets."""
        yield Static("Filter:", classes="filter-label")
        yield Input(placeholder="Instance name...", id="name-filter")
        yield Static("Status:", classes="filter-label")
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
        )

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes."""
        if event.input.id == "name-filter":
            self.post_message(FilterChanged(name_filter=event.value, status_filter=None))

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle select changes."""
        if event.select.id == "status-filter":
            self.post_message(FilterChanged(name_filter=None, status_filter=str(event.value)))


class FilterChanged(Message):
    """Message posted when filters change."""

    def __init__(self, name_filter: str | None, status_filter: str | None) -> None:
        """Initialize message."""
        self.name_filter = name_filter
        self.status_filter = status_filter
        super().__init__()
