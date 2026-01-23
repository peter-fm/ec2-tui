"""Modal dialog for changing instance type."""

from typing import Optional

from textual.app import ComposeResult
from textual.containers import Grid, Vertical
from textual.message import Message
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Label, Static


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
        width: 90;
        height: auto;
        border: thick $background 80%;
        background: $surface;
        padding: 1 2;
    }

    #instance-type-table {
        height: 15;
        border: solid $primary;
        margin: 1 0;
    }

    #instance-type-table > .datatable--header {
        background: $boost;
        color: $text;
        text-style: bold;
    }

    #instance-type-table > .datatable--cursor {
        background: $secondary;
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
        pricing_data: Optional[dict[str, dict]] = None,
    ) -> None:
        """
        Initialize modal.

        Args:
            instance_id: Instance ID.
            instance_name: Instance name.
            current_type: Current instance type.
            saved_types: List of saved instance types for quick select.
            pricing_data: Optional pricing data dict {instance_type: {"price": float, "gpus": int}}.
        """
        super().__init__()
        self.instance_id = instance_id
        self.instance_name = instance_name
        self.current_type = current_type
        self.saved_types = saved_types
        self.pricing_data = pricing_data or {}

    def compose(self) -> ComposeResult:
        """Compose modal dialog."""
        with Vertical(id="instance-type-dialog"):
            yield Label(f"Change Instance Type")
            yield Static(f"Instance: {self.instance_name} ({self.instance_id})")

            # Show current type with pricing if available
            current_info = self._format_type_info(self.current_type)
            yield Static(f"Current Type: {current_info}")

            yield DataTable(id="instance-type-table", zebra_stripes=True, cursor_type="row")

            with Grid(id="buttons"):
                yield Button("Change", variant="primary", id="change-button")
                yield Button("Cancel", id="cancel-button")

    def on_mount(self) -> None:
        """Set up table when modal mounts."""
        table = self.query_one("#instance-type-table", DataTable)

        # Add columns
        table.add_columns("Type", "vCPUs", "RAM (GB)", "GPUs", "Price/hr")

        # Populate table with saved types
        self._populate_table(table)

    def _populate_table(self, table: DataTable) -> None:
        """
        Populate table with saved instance types and their info.

        Args:
            table: DataTable widget to populate.
        """
        current_row_index = None

        for idx, instance_type in enumerate(self.saved_types):
            # Get pricing info
            vcpu_str = "-"
            ram_str = "-"
            gpu_str = "-"
            price_str = "-"

            if instance_type in self.pricing_data:
                info = self.pricing_data[instance_type]
                if isinstance(info, dict):
                    # vCPUs
                    vcpus = info.get("vcpus")
                    if vcpus is not None:
                        vcpu_str = str(vcpus)

                    # RAM
                    memory_gb = info.get("memory_gb")
                    if memory_gb is not None:
                        # Format nicely: 0.5 -> "0.5", 8.0 -> "8", 16 -> "16"
                        if memory_gb < 1:
                            ram_str = f"{memory_gb:.1f}"
                        else:
                            ram_str = f"{int(memory_gb)}" if memory_gb == int(memory_gb) else f"{memory_gb:.1f}"

                    # GPUs
                    gpu_count = info.get("gpus", 0)
                    if gpu_count > 0:
                        gpu_str = str(int(gpu_count))

                    # Price
                    price = info.get("price")
                    if price is not None:
                        price_str = f"${price:.4f}"

            # Add row: Type, vCPUs, RAM, GPUs, Price
            table.add_row(instance_type, vcpu_str, ram_str, gpu_str, price_str, key=instance_type)

            # Track current type row index for cursor positioning
            if instance_type == self.current_type:
                current_row_index = idx

        # Move cursor to current type if found
        if current_row_index is not None:
            table.move_cursor(row=current_row_index)

    def _format_type_info(self, instance_type: str) -> str:
        """Format instance type with pricing and GPU info if available."""
        if instance_type in self.pricing_data:
            info = self.pricing_data[instance_type]
            if isinstance(info, dict):
                price = info.get("price")
                gpu_count = info.get("gpus", 0)

                parts = [instance_type]
                if gpu_count > 0:
                    parts.append(f"{gpu_count} GPU{'s' if gpu_count > 1 else ''}")
                if price is not None:
                    parts.append(f"${price:.4f}/hr")

                return " ".join(parts)
        return instance_type

    def _get_selected_instance_type(self) -> Optional[str]:
        """
        Get the currently selected instance type from the table.

        Returns:
            Selected instance type string, or None if no selection.
        """
        table = self.query_one("#instance-type-table", DataTable)

        if table.cursor_row is None or table.cursor_row < 0:
            return None

        # Get the first column value (instance type) from the selected row
        try:
            row = table.get_row_at(table.cursor_row)
            if row and len(row) > 0:
                return str(row[0])
        except Exception:
            pass

        return None

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-button":
            self.dismiss()
        elif event.button.id == "change-button":
            # Get selected instance type from table
            selected_type = self._get_selected_instance_type()
            if selected_type:
                self.dismiss(selected_type)
