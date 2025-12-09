"""EC2 Instance data model."""

from dataclasses import dataclass
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

    @classmethod
    def from_boto3(cls, instance_data: dict, region: str) -> "Instance":
        """
        Create Instance from boto3 describe_instances response.

        Args:
            instance_data: Instance data from boto3.
            region: AWS region name.

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

        return cls(
            instance_id=instance_data["InstanceId"],
            name=name,
            state=instance_data["State"]["Name"],
            instance_type=instance_data["InstanceType"],
            private_ip=instance_data.get("PrivateIpAddress"),
            availability_zone=instance_data.get("Placement", {}).get("AvailabilityZone"),
            region=region,
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
