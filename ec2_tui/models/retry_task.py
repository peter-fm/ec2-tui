"""Retry task data model."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class RetryTask:
    """Represents an active retry task for starting an instance."""

    task_id: str
    instance_id: str
    instance_name: str
    attempts: int = 0
    max_attempts: int = 60
    interval_seconds: int = 60
    next_retry_at: Optional[datetime] = None
    started_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, waiting, attempting, success, failed, cancelled

    def get_progress_text(self) -> str:
        """Get progress text for display."""
        return f"Attempt {self.attempts}/{self.max_attempts}"

    def get_time_until_next(self) -> str:
        """Get time remaining until next retry attempt."""
        if self.next_retry_at is None:
            return "N/A"

        now = datetime.now()
        if self.next_retry_at <= now:
            return "now"

        delta = self.next_retry_at - now
        seconds = int(delta.total_seconds())

        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"

    def get_status_display(self) -> str:
        """Get status text for display."""
        status_map = {
            "pending": "Pending",
            "waiting": "Waiting",
            "attempting": "Attempting",
            "success": "Success",
            "failed": "Failed",
            "cancelled": "Cancelled",
        }
        return status_map.get(self.status, self.status)
