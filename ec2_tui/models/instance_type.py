"""Instance type validation utilities."""

import re


def is_valid_instance_type_format(instance_type: str) -> bool:
    """
    Check if instance type follows valid AWS instance type format.

    Format: family.size (e.g., t3.medium, m5.xlarge, c5n.18xlarge)

    Args:
        instance_type: Instance type string to validate.

    Returns:
        True if format is valid.
    """
    # Pattern: lowercase letters/numbers, optional letters, dot, size
    pattern = r"^[a-z][a-z0-9]*[a-z]?\.[a-z0-9]+$"
    return bool(re.match(pattern, instance_type.lower()))
