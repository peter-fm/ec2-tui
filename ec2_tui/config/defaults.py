"""Default configuration values for EC2 TUI."""

DEFAULT_CONFIG = {
    "ui": {
        "default_region": "us-east-1",
        "refresh_interval_seconds": 30,
        "theme": "dark",
    },
    "retry": {
        "enabled": True,
        "interval_seconds": 60,
        "max_attempts": 60,
    },
    "notifications": {
        "enabled": True,
        "urgency": "normal",
    },
    "saved_instance_types": {
        "types": [
            "t3.micro",
            "t3.small",
            "t3.medium",
            "t3.large",
            "m5.large",
            "m5.xlarge",
            "m5.2xlarge",
        ],
    },
    "aws": {
        "use_cli_credentials": True,
        "profile": None,
    },
}
