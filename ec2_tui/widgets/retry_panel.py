"""Retry panel widget showing active retry tasks."""

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Static

from ..models.retry_task import RetryTask


class RetryPanel(VerticalScroll):
    """Panel showing active retry tasks."""

    retry_tasks: reactive[dict[str, RetryTask]] = reactive(dict, always_update=True)

    def compose(self) -> ComposeResult:
        """Compose retry panel."""
        yield Static("Active Retries", id="retry-header")
        yield Static("No active retries", id="retry-content")

    def watch_retry_tasks(self, retry_tasks: dict[str, RetryTask]) -> None:
        """Update display when retry tasks change."""
        content = self.query_one("#retry-content", Static)

        if not retry_tasks:
            content.update("No active retries")
            return

        lines = []
        for task_id, task in retry_tasks.items():
            status = task.get_status_display()
            progress = task.get_progress_text()
            time_until = task.get_time_until_next()

            line = (
                f"• {task.instance_name} ({task.instance_id}): "
                f"{progress}, next in {time_until} [press 'c' to cancel]"
            )
            lines.append(line)

        content.update("\n".join(lines))

    def update_retry_tasks(self, retry_tasks: dict[str, RetryTask]) -> None:
        """Update retry tasks."""
        self.retry_tasks = retry_tasks
