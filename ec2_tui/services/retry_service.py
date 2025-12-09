"""Retry service for handling instance start retries."""

import asyncio
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from textual.message import Message

from ..models.retry_task import RetryTask
from ..utils.exceptions import InsufficientCapacityError

if TYPE_CHECKING:
    from .ec2_service import EC2Service
    from .notification_service import NotificationService


class RetryTaskUpdated(Message):
    """Posted when retry task state changes."""

    def __init__(self, task_id: str) -> None:
        """Initialize message."""
        self.task_id = task_id
        super().__init__()


class RetryTaskCompleted(Message):
    """Posted when retry task completes (success or failure)."""

    def __init__(self, task_id: str, success: bool, error: str = "") -> None:
        """Initialize message."""
        self.task_id = task_id
        self.success = success
        self.error = error
        super().__init__()


class RetryTaskCancelled(Message):
    """Posted when retry task is cancelled."""

    def __init__(self, task_id: str) -> None:
        """Initialize message."""
        self.task_id = task_id
        super().__init__()


class RetryService:
    """Manages retry tasks for instance start operations."""

    def __init__(
        self,
        ec2_service: "EC2Service",
        notification_service: "NotificationService",
        interval_seconds: int = 60,
        max_attempts: int = 60,
    ):
        """
        Initialize retry service.

        Args:
            ec2_service: EC2 service instance.
            notification_service: Notification service instance.
            interval_seconds: Seconds between retry attempts.
            max_attempts: Maximum number of retry attempts.
        """
        self.ec2_service = ec2_service
        self.notification_service = notification_service
        self.interval_seconds = interval_seconds
        self.max_attempts = max_attempts

        self.tasks: dict[str, asyncio.Task] = {}
        self.retry_data: dict[str, RetryTask] = {}
        self._app = None

    def set_app(self, app) -> None:
        """Set reference to main app for posting messages."""
        self._app = app

    def schedule_retry(self, instance_id: str, instance_name: str) -> str:
        """
        Schedule a retry task for an instance.

        Args:
            instance_id: Instance ID to retry.
            instance_name: Instance name for display.

        Returns:
            Task ID for tracking.
        """
        task_id = f"retry-{instance_id}-{datetime.now().timestamp()}"

        retry_task = RetryTask(
            task_id=task_id,
            instance_id=instance_id,
            instance_name=instance_name,
            max_attempts=self.max_attempts,
            interval_seconds=self.interval_seconds,
            next_retry_at=datetime.now() + timedelta(seconds=self.interval_seconds),
        )

        self.retry_data[task_id] = retry_task

        # Create asyncio task for the retry loop
        async_task = asyncio.create_task(self._execute_retry_loop(task_id))
        self.tasks[task_id] = async_task

        return task_id

    async def _execute_retry_loop(self, task_id: str) -> None:
        """
        Execute the retry loop for a specific task.

        Args:
            task_id: Task ID to execute.
        """
        retry_task = self.retry_data[task_id]

        while retry_task.attempts < retry_task.max_attempts:
            try:
                # Increment attempt counter first
                retry_task.attempts += 1

                # Wait for the interval
                retry_task.next_retry_at = datetime.now() + timedelta(
                    seconds=retry_task.interval_seconds
                )
                retry_task.status = "waiting"
                self._post_message(RetryTaskUpdated(task_id))

                await asyncio.sleep(retry_task.interval_seconds)

                # Attempt to start instance
                retry_task.status = "attempting"
                self._post_message(RetryTaskUpdated(task_id))

                # Run EC2 start in thread pool (boto3 is synchronous)
                await asyncio.to_thread(
                    self.ec2_service.start_instance, retry_task.instance_id
                )

                # Success!
                retry_task.status = "success"
                self._post_message(RetryTaskCompleted(task_id, success=True))

                # Send notification
                self.notification_service.notify_instance_started(
                    retry_task.instance_id, retry_task.instance_name
                )

                # Clean up
                del self.retry_data[task_id]
                del self.tasks[task_id]
                return

            except InsufficientCapacityError:
                # Expected error, continue retrying
                retry_task.status = "waiting"
                self._post_message(RetryTaskUpdated(task_id))
                continue

            except asyncio.CancelledError:
                # Task was cancelled
                retry_task.status = "cancelled"
                self._post_message(RetryTaskCancelled(task_id))
                if task_id in self.retry_data:
                    del self.retry_data[task_id]
                if task_id in self.tasks:
                    del self.tasks[task_id]
                return

            except Exception as e:
                # Unexpected error, stop retrying
                retry_task.status = "failed"
                self._post_message(RetryTaskCompleted(task_id, success=False, error=str(e)))
                self.notification_service.notify_instance_failed(retry_task.instance_id, str(e))

                # Clean up
                if task_id in self.retry_data:
                    del self.retry_data[task_id]
                if task_id in self.tasks:
                    del self.tasks[task_id]
                return

        # Max attempts reached
        retry_task.status = "failed"
        self._post_message(
            RetryTaskCompleted(task_id, success=False, error="Max attempts reached")
        )
        self.notification_service.notify_retry_max_attempts(retry_task.instance_name)

        # Clean up
        if task_id in self.retry_data:
            del self.retry_data[task_id]
        if task_id in self.tasks:
            del self.tasks[task_id]

    def cancel_retry(self, task_id: str) -> None:
        """
        Cancel an active retry task.

        Args:
            task_id: Task ID to cancel.
        """
        if task_id in self.tasks:
            self.tasks[task_id].cancel()

    def cancel_all(self) -> None:
        """Cancel all active retry tasks."""
        for task_id in list(self.tasks.keys()):
            self.cancel_retry(task_id)

    def get_active_retries(self) -> dict[str, RetryTask]:
        """
        Get all active retry tasks.

        Returns:
            Dictionary mapping task ID to RetryTask.
        """
        # Return a new dict to trigger reactive updates
        # Note: We return the same task objects, but a new dict container
        # This ensures the reactive property detects the change
        return dict(self.retry_data)

    def _post_message(self, message: Message) -> None:
        """Post a message to the app."""
        if self._app is not None:
            self._app.post_message(message)
