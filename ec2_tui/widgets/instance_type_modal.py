"""Modal dialog for changing instance type."""

from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Label, Static


class InstanceTypeSelected(Message):
    """Message posted when instance type is selected."""

    def __init__(self, instance_type: str) -> None:
        """Initialize message."""
        self.instance_type = instance_type
        super().__init__()


class InstanceTypeModal(ModalScreen):
    """Modal screen for changing instance type."""

    CSS = """
    InstanceTypeModal {
        align: center middle;
    }

    #instance-type-dialog {
        width: 60;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #quick-select {
        height: auto;
        margin: 1 0;
    }

    .quick-button {
        margin: 0 1 0 0;
    }

    #buttons {
        width: 100%;
        height: auto;
        align: center middle;
        margin: 1 0 0 0;
    }
    """

    def __init__(
        self,
        instance_id: str,
        instance_name: str,
        current_type: str,
        saved_types: list[str],
    ) -> None:
        """
        Initialize modal.

        Args:
            instance_id: Instance ID.
            instance_name: Instance name.
            current_type: Current instance type.
            saved_types: List of saved instance types for quick select.
        """
        super().__init__()
        self.instance_id = instance_id
        self.instance_name = instance_name
        self.current_type = current_type
        self.saved_types = saved_types

    def compose(self) -> ComposeResult:
        """Compose modal dialog."""
        with Vertical(id="instance-type-dialog"):
            yield Label(f"Change Instance Type")
            yield Static(f"Instance: {self.instance_name} ({self.instance_id})")
            yield Static(f"Current Type: {self.current_type}")

            yield Label("Quick Select:", id="quick-select-label")
            with Grid(id="quick-select"):
                for instance_type in self.saved_types:
                    yield Button(instance_type, classes="quick-button")

            yield Label("Or enter custom type:")
            yield Input(placeholder="e.g., t3.medium, m5.xlarge", id="custom-type-input")

            with Grid(id="buttons"):
                yield Button("Change", variant="primary", id="change-button")
                yield Button("Cancel", id="cancel-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-button":
            self.dismiss()
        elif event.button.id == "change-button":
            # Get custom input
            custom_input = self.query_one("#custom-type-input", Input)
            if custom_input.value:
                self.dismiss(custom_input.value)
        elif event.button.classes and "quick-button" in event.button.classes:
            # Quick select button - convert label to string
            label = event.button.label
            self.dismiss(str(label) if label else None)
