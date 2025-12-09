"""Footer widget showing keyboard shortcuts."""

from textual.widgets import Static


class Footer(Static):
    """Footer widget displaying keyboard shortcuts."""

    def compose(self):
        """Compose footer content."""
        shortcuts = [
            ("s", "Start"),
            ("S", "Stop"),
            ("t", "Type"),
            ("r/F5", "Refresh"),
            ("c", "Cancel Retry"),
            ("q", "Quit"),
        ]

        shortcut_text = " | ".join([f"[b]{key}[/b]:{action}" for key, action in shortcuts])
        yield Static(shortcut_text, id="shortcuts")
