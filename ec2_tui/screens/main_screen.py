"""Main screen composing all widgets."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Header

from ..widgets.controls_bar import ControlsBar
from ..widgets.footer import Footer
from ..widgets.instance_table import InstanceTable
from ..widgets.retry_panel import RetryPanel


class MainScreen(Screen):
    """Main application screen."""

    CSS = """
    MainScreen {
        layout: vertical;
    }

    #controls-container {
        height: auto;
        padding: 0 1;
    }

    #table-container {
        height: 1fr;
        padding: 0 1;
    }

    #retry-container {
        height: auto;
        max-height: 10;
        padding: 0 1;
    }

    #footer-container {
        height: auto;
        dock: bottom;
        padding: 1;
        background: $boost;
    }
    """

    def __init__(self, default_region: str = "eu-west-1"):
        """Initialize main screen with default region."""
        super().__init__()
        self.default_region = default_region

    def compose(self) -> ComposeResult:
        """Compose main screen layout."""
        yield Header(show_clock=True)

        with Container(id="table-container"):
            yield InstanceTable()

        with Container(id="retry-container"):
            yield RetryPanel()

        with Container(id="controls-container"):
            yield ControlsBar(default_region=self.default_region)

        with Container(id="footer-container"):
            yield Footer()

    def on_mount(self) -> None:
        """Set focus to instance table on mount."""
        # Use call_after_refresh to ensure focus happens after all widgets are ready
        self.call_after_refresh(self._set_initial_focus)

    def _set_initial_focus(self) -> None:
        """Set initial focus to the instance table."""
        try:
            table = self.query_one(InstanceTable)
            table.focus()
        except Exception:
            pass  # Table might not be ready yet
