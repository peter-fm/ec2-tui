"""AWS EC2 service wrapper."""

from typing import Optional, TYPE_CHECKING

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

from ..models.instance import Instance
from ..models.instance_type import is_valid_instance_type_format
from ..utils.exceptions import (
    AWSError,
    ConfigurationError,
    InsufficientCapacityError,
    ValidationError,
)

if TYPE_CHECKING:
    from ..config.config import Config as AppConfig


class EC2Service:
    """AWS EC2 service wrapper."""

    def __init__(self, region: str, profile: Optional[str] = None, app_config: Optional["AppConfig"] = None):
        """
        Initialize EC2 service.

        Args:
            region: AWS region name.
            profile: AWS CLI profile name (None for default).
            app_config: Application configuration for pricing data (optional).

        Raises:
            ConfigurationError: If AWS credentials are not configured.
        """
        try:
            session = boto3.Session(profile_name=profile, region_name=region)

            config = Config(retries={"max_attempts": 3, "mode": "standard"})

            self.ec2 = session.client("ec2", config=config)
            self.region = region
            self.app_config = app_config

        except NoCredentialsError:
            raise ConfigurationError(
                "AWS credentials not found. "
                "Please configure AWS CLI credentials in ~/.aws/credentials"
            )

    def list_instances(
        self, name_filter: str = "", status_filter: str = "all"
    ) -> list[Instance]:
        """
        List EC2 instances with optional filtering.

        Args:
            name_filter: Filter by instance name (case-insensitive substring).
            status_filter: Filter by status ("all", "running", "stopped", etc.).

        Returns:
            List of Instance objects.

        Raises:
            AWSError: If AWS API call fails.
        """
        try:
            # Build filters for API call
            filters = []
            if status_filter != "all":
                filters.append({"Name": "instance-state-name", "Values": [status_filter]})

            # Call AWS API
            response = self.ec2.describe_instances(Filters=filters)

            # Parse instances
            instances = []
            for reservation in response["Reservations"]:
                for instance_data in reservation["Instances"]:
                    instance_type = instance_data["InstanceType"]

                    # Get pricing info from config if available
                    price_per_hour = None
                    gpu_count = 0
                    if self.app_config:
                        price_per_hour = self.app_config.get_price(self.region, instance_type)
                        gpu_count = self.app_config.get_gpu_count(self.region, instance_type)

                    instance = Instance.from_boto3(
                        instance_data,
                        self.region,
                        price_per_hour=price_per_hour,
                        gpu_count=gpu_count
                    )

                    # Apply name filter
                    if instance.matches_filter(name_filter, "all"):
                        instances.append(instance)

            return instances

        except ClientError as e:
            raise self._handle_aws_error(e)

    def start_instance(self, instance_id: str) -> dict:
        """
        Start an EC2 instance.

        Args:
            instance_id: Instance ID to start.

        Returns:
            Response from AWS API.

        Raises:
            InsufficientCapacityError: If there is insufficient capacity.
            AWSError: If AWS API call fails.
        """
        try:
            response = self.ec2.start_instances(InstanceIds=[instance_id])
            return response

        except ClientError as e:
            raise self._handle_aws_error(e)

    def stop_instance(self, instance_id: str) -> dict:
        """
        Stop an EC2 instance.

        Args:
            instance_id: Instance ID to stop.

        Returns:
            Response from AWS API.

        Raises:
            AWSError: If AWS API call fails.
        """
        try:
            response = self.ec2.stop_instances(InstanceIds=[instance_id])
            return response

        except ClientError as e:
            raise self._handle_aws_error(e)

    def change_instance_type(self, instance_id: str, instance_type: str) -> dict:
        """
        Change the instance type of a stopped instance.

        Args:
            instance_id: Instance ID to modify.
            instance_type: New instance type (e.g., "t3.medium").

        Returns:
            Response from AWS API.

        Raises:
            ValidationError: If instance type is invalid.
            AWSError: If AWS API call fails (e.g., instance is running).
        """
        # Validate instance type format
        if not is_valid_instance_type_format(instance_type):
            raise ValidationError(
                f"Invalid instance type format: {instance_type}. "
                f"Expected format like 't3.medium' or 'm5.xlarge'"
            )

        try:
            response = self.ec2.modify_instance_attribute(
                InstanceId=instance_id,
                InstanceType={"Value": instance_type},
            )
            return response

        except ClientError as e:
            raise self._handle_aws_error(e)

    def validate_instance_type(self, instance_type: str) -> bool:
        """
        Validate if an instance type exists in AWS.

        Args:
            instance_type: Instance type to validate.

        Returns:
            True if instance type is valid.

        Raises:
            ValidationError: If instance type format is invalid.
            AWSError: If AWS API call fails.
        """
        # First check format
        if not is_valid_instance_type_format(instance_type):
            raise ValidationError(f"Invalid instance type format: {instance_type}")

        try:
            # Query AWS for this instance type
            response = self.ec2.describe_instance_types(InstanceTypes=[instance_type])

            return len(response.get("InstanceTypes", [])) > 0

        except ClientError as e:
            # InvalidInstanceType.NotFound means it doesn't exist
            if e.response["Error"]["Code"] == "InvalidInstanceType.NotFound":
                return False
            raise self._handle_aws_error(e)

    @staticmethod
    def get_available_regions() -> list[str]:
        """
        Get list of available AWS regions.

        Returns:
            List of region names.
        """
        # Common AWS regions
        return [
            "eu-west-1",
            "us-east-2",
            "us-west-1",
            "us-west-2",
            "eu-west-1",
            "eu-west-2",
            "eu-west-3",
            "eu-central-1",
            "ap-southeast-1",
            "ap-southeast-2",
            "ap-northeast-1",
            "ap-northeast-2",
            "ap-south-1",
            "sa-east-1",
            "ca-central-1",
        ]

    def _handle_aws_error(self, error: ClientError) -> Exception:
        """
        Convert boto3 ClientError to appropriate custom exception.

        Args:
            error: boto3 ClientError.

        Returns:
            Custom exception.
        """
        error_code = error.response["Error"]["Code"]
        error_message = error.response["Error"]["Message"]

        if error_code == "InsufficientInstanceCapacity":
            return InsufficientCapacityError(
                f"AWS does not have enough capacity for the requested instance type "
                f"in this availability zone"
            )
        elif error_code in ["InvalidParameterValue", "InvalidInstanceType"]:
            return ValidationError(error_message)
        elif error_code == "IncorrectInstanceState":
            return ValidationError(
                f"Cannot perform this operation on instance in current state: {error_message}"
            )
        else:
            return AWSError(f"{error_code}: {error_message}")
