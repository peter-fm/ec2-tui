"""Desktop notification service using notify-send."""

import shutil
import subprocess
from typing import Optional


class NotificationService:
    """Desktop notification service using notify-send."""

    def __init__(self, enabled: bool = True, urgency: str = "normal"):
        """
        Initialize notification service.

        Args:
            enabled: Whether notifications are enabled.
            urgency: Default urgency level (low, normal, critical).
        """
        self.enabled = enabled
        self.default_urgency = urgency
        self.notify_send_available = shutil.which("notify-send") is not None

        if enabled and not self.notify_send_available:
            print("Warning: notify-send not available. Notifications disabled.")

    def send_notification(
        self,
        title: str,
        message: str,
        urgency: Optional[str] = None,
        icon: Optional[str] = None,
    ) -> None:
        """
        Send desktop notification.

        Args:
            title: Notification title.
            message: Notification message.
            urgency: Urgency level (low, normal, critical). Uses default if None.
            icon: Icon name or path.
        """
        if not self.enabled or not self.notify_send_available:
            return

        try:
            cmd = ["notify-send"]

            if urgency is None:
                urgency = self.default_urgency

            if urgency:
                cmd.extend(["--urgency", urgency])

            if icon:
                cmd.extend(["--icon", icon])

            cmd.extend([title, message])

            subprocess.run(cmd, check=False, capture_output=True)

        except Exception as e:
            # Don't fail if notification fails
            print(f"Notification error: {e}")

    def notify_instance_started(self, instance_id: str, instance_name: str) -> None:
        """
        Notify that instance started successfully.

        Args:
            instance_id: Instance ID.
            instance_name: Instance name.
        """
        self.send_notification(
            title="EC2 Instance Started",
            message=f"{instance_name} ({instance_id}) is now running",
            urgency="normal",
            icon="dialog-information",
        )

    def notify_instance_failed(self, instance_id: str, error: str) -> None:
        """
        Notify that instance start failed.

        Args:
            instance_id: Instance ID.
            error: Error message.
        """
        self.send_notification(
            title="EC2 Instance Failed",
            message=f"Failed to start {instance_id}: {error}",
            urgency="critical",
            icon="dialog-error",
        )

    def notify_retry_max_attempts(self, instance_name: str) -> None:
        """
        Notify that retry reached maximum attempts.

        Args:
            instance_name: Instance name.
        """
        self.send_notification(
            title="EC2 Retry Failed",
            message=f"Max retry attempts reached for {instance_name}",
            urgency="critical",
            icon="dialog-warning",
        )
