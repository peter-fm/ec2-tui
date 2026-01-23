"""EC2 Instance data model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Instance:
    """Represents an EC2 instance."""

    instance_id: str
    name: str
    state: str
    instance_type: str
    private_ip: Optional[str] = None
    availability_zone: Optional[str] = None
    region: Optional[str] = None
    launch_time: Optional[datetime] = None
    price_per_hour: Optional[float] = None
    gpu_count: int = 0

    @classmethod
    def from_boto3(cls, instance_data: dict, region: str, price_per_hour: Optional[float] = None, gpu_count: int = 0) -> "Instance":
        """
        Create Instance from boto3 describe_instances response.

        Args:
            instance_data: Instance data from boto3.
            region: AWS region name.
            price_per_hour: Price per hour for this instance type (optional).
            gpu_count: Number of GPUs for this instance type (optional).

        Returns:
            Instance object.
        """
        # Extract name from tags
        name = ""
        if "Tags" in instance_data:
            for tag in instance_data["Tags"]:
                if tag["Key"] == "Name":
                    name = tag["Value"]
                    break

        # If no Name tag, use instance ID
        if not name:
            name = instance_data["InstanceId"]

        # Extract launch time
        launch_time = instance_data.get("LaunchTime")

        return cls(
            instance_id=instance_data["InstanceId"],
            name=name,
            state=instance_data["State"]["Name"],
            instance_type=instance_data["InstanceType"],
            private_ip=instance_data.get("PrivateIpAddress"),
            availability_zone=instance_data.get("Placement", {}).get("AvailabilityZone"),
            region=region,
            launch_time=launch_time,
            price_per_hour=price_per_hour,
            gpu_count=gpu_count,
        )

    def matches_filter(self, name_filter: str = "", status_filter: str = "all") -> bool:
        """
        Check if instance matches the given filters.

        Args:
            name_filter: Filter by instance name (case-insensitive substring match).
            status_filter: Filter by status ("all", "running", "stopped", etc.).

        Returns:
            True if instance matches filters.
        """
        # Check name filter
        if name_filter and name_filter.lower() not in self.name.lower():
            return False

        # Check status filter
        if status_filter != "all" and self.state != status_filter:
            return False

        return True

    def get_status_color(self) -> str:
        """Get color for instance status display."""
        status_colors = {
            "running": "green",
            "stopped": "red",
            "pending": "yellow",
            "stopping": "yellow",
            "terminated": "dark_red",
            "terminating": "dark_red",
        }
        return status_colors.get(self.state, "white")

    def get_uptime_hours(self) -> Optional[float]:
        """
        Calculate uptime in hours since launch.

        Returns:
            Hours since launch, or None if launch_time is not available.
        """
        if not self.launch_time:
            return None

        # Make launch_time timezone aware if it isn't already
        if self.launch_time.tzinfo is None:
            from datetime import timezone
            launch_time = self.launch_time.replace(tzinfo=timezone.utc)
        else:
            launch_time = self.launch_time

        now = datetime.now(launch_time.tzinfo)
        delta = now - launch_time
        return delta.total_seconds() / 3600

    def get_estimated_spend(self) -> Optional[float]:
        """
        Calculate estimated spend based on uptime and price per hour.
        Only calculates for running instances.

        Returns:
            Estimated spend in USD, or None if data is not available.
        """
        if self.state != "running":
            return None

        if not self.price_per_hour:
            return None

        uptime_hours = self.get_uptime_hours()
        if uptime_hours is None:
            return None

        return uptime_hours * self.price_per_hour
