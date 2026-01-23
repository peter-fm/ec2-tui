"""Default configuration values for EC2 TUI."""

DEFAULT_CONFIG = {
    "ui": {
        "default_region": "eu-west-1",
        "refresh_interval_seconds": 30,
        "theme": "omarchy",  # Auto-detects Omarchy on Arch Linux, falls back to textual-dark
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
    "pricing": {
        # Pricing data per region (USD per hour, on-demand Linux pricing)
        # Structure: {instance_type: {"price": float, "gpus": int, "vcpus": int, "memory_gb": float}}
        "eu-west-1": {
            # T3 instances (burstable)
            "t3.nano": {"price": 0.0059, "gpus": 0, "vcpus": 2, "memory_gb": 0.5},
            "t3.micro": {"price": 0.0118, "gpus": 0, "vcpus": 2, "memory_gb": 1},
            "t3.small": {"price": 0.0236, "gpus": 0, "vcpus": 2, "memory_gb": 2},
            "t3.medium": {"price": 0.0472, "gpus": 0, "vcpus": 2, "memory_gb": 4},
            "t3.large": {"price": 0.0944, "gpus": 0, "vcpus": 2, "memory_gb": 8},
            "t3.xlarge": {"price": 0.1888, "gpus": 0, "vcpus": 4, "memory_gb": 16},
            "t3.2xlarge": {"price": 0.3776, "gpus": 0, "vcpus": 8, "memory_gb": 32},
            # T2 instances (burstable)
            "t2.nano": {"price": 0.0065, "gpus": 0, "vcpus": 1, "memory_gb": 0.5},
            "t2.micro": {"price": 0.013, "gpus": 0, "vcpus": 1, "memory_gb": 1},
            "t2.small": {"price": 0.026, "gpus": 0, "vcpus": 1, "memory_gb": 2},
            "t2.medium": {"price": 0.052, "gpus": 0, "vcpus": 2, "memory_gb": 4},
            "t2.large": {"price": 0.104, "gpus": 0, "vcpus": 2, "memory_gb": 8},
            "t2.xlarge": {"price": 0.208, "gpus": 0, "vcpus": 4, "memory_gb": 16},
            "t2.2xlarge": {"price": 0.416, "gpus": 0, "vcpus": 8, "memory_gb": 32},
            # M5 instances (general purpose)
            "m5.large": {"price": 0.107, "gpus": 0, "vcpus": 2, "memory_gb": 8},
            "m5.xlarge": {"price": 0.214, "gpus": 0, "vcpus": 4, "memory_gb": 16},
            "m5.2xlarge": {"price": 0.428, "gpus": 0, "vcpus": 8, "memory_gb": 32},
            "m5.4xlarge": {"price": 0.856, "gpus": 0, "vcpus": 16, "memory_gb": 64},
            "m5.8xlarge": {"price": 1.712, "gpus": 0, "vcpus": 32, "memory_gb": 128},
            "m5.12xlarge": {"price": 2.568, "gpus": 0, "vcpus": 48, "memory_gb": 192},
            "m5.16xlarge": {"price": 3.424, "gpus": 0, "vcpus": 64, "memory_gb": 256},
            "m5.24xlarge": {"price": 5.136, "gpus": 0, "vcpus": 96, "memory_gb": 384},
            # M6i instances (general purpose, latest gen)
            "m6i.large": {"price": 0.107, "gpus": 0, "vcpus": 2, "memory_gb": 8},
            "m6i.xlarge": {"price": 0.214, "gpus": 0, "vcpus": 4, "memory_gb": 16},
            "m6i.2xlarge": {"price": 0.428, "gpus": 0, "vcpus": 8, "memory_gb": 32},
            "m6i.4xlarge": {"price": 0.856, "gpus": 0, "vcpus": 16, "memory_gb": 64},
            "m6i.8xlarge": {"price": 1.712, "gpus": 0, "vcpus": 32, "memory_gb": 128},
            "m6i.12xlarge": {"price": 2.568, "gpus": 0, "vcpus": 48, "memory_gb": 192},
            "m6i.16xlarge": {"price": 3.424, "gpus": 0, "vcpus": 64, "memory_gb": 256},
            "m6i.24xlarge": {"price": 5.136, "gpus": 0, "vcpus": 96, "memory_gb": 384},
            "m6i.32xlarge": {"price": 6.848, "gpus": 0, "vcpus": 128, "memory_gb": 512},
            # C5 instances (compute optimized)
            "c5.large": {"price": 0.095, "gpus": 0, "vcpus": 2, "memory_gb": 4},
            "c5.xlarge": {"price": 0.19, "gpus": 0, "vcpus": 4, "memory_gb": 8},
            "c5.2xlarge": {"price": 0.38, "gpus": 0, "vcpus": 8, "memory_gb": 16},
            "c5.4xlarge": {"price": 0.76, "gpus": 0, "vcpus": 16, "memory_gb": 32},
            "c5.9xlarge": {"price": 1.71, "gpus": 0, "vcpus": 36, "memory_gb": 72},
            "c5.12xlarge": {"price": 2.28, "gpus": 0, "vcpus": 48, "memory_gb": 96},
            "c5.18xlarge": {"price": 3.42, "gpus": 0, "vcpus": 72, "memory_gb": 144},
            "c5.24xlarge": {"price": 4.56, "gpus": 0, "vcpus": 96, "memory_gb": 192},
            # R5 instances (memory optimized)
            "r5.large": {"price": 0.141, "gpus": 0, "vcpus": 2, "memory_gb": 16},
            "r5.xlarge": {"price": 0.282, "gpus": 0, "vcpus": 4, "memory_gb": 32},
            "r5.2xlarge": {"price": 0.564, "gpus": 0, "vcpus": 8, "memory_gb": 64},
            "r5.4xlarge": {"price": 1.128, "gpus": 0, "vcpus": 16, "memory_gb": 128},
            "r5.8xlarge": {"price": 2.256, "gpus": 0, "vcpus": 32, "memory_gb": 256},
            "r5.12xlarge": {"price": 3.384, "gpus": 0, "vcpus": 48, "memory_gb": 384},
            "r5.16xlarge": {"price": 4.512, "gpus": 0, "vcpus": 64, "memory_gb": 512},
            "r5.24xlarge": {"price": 6.768, "gpus": 0, "vcpus": 96, "memory_gb": 768},
            # P3 instances (GPU - NVIDIA V100)
            "p3.2xlarge": {"price": 3.672, "gpus": 1, "vcpus": 8, "memory_gb": 61},
            "p3.8xlarge": {"price": 14.688, "gpus": 4, "vcpus": 32, "memory_gb": 244},
            "p3.16xlarge": {"price": 29.376, "gpus": 8, "vcpus": 64, "memory_gb": 488},
            # G4 instances (GPU - NVIDIA T4)
            "g4dn.xlarge": {"price": 0.632, "gpus": 1, "vcpus": 4, "memory_gb": 16},
            "g4dn.2xlarge": {"price": 0.902, "gpus": 1, "vcpus": 8, "memory_gb": 32},
            "g4dn.4xlarge": {"price": 1.445, "gpus": 1, "vcpus": 16, "memory_gb": 64},
            "g4dn.8xlarge": {"price": 2.611, "gpus": 1, "vcpus": 32, "memory_gb": 128},
            "g4dn.12xlarge": {"price": 4.694, "gpus": 4, "vcpus": 48, "memory_gb": 192},
            "g4dn.16xlarge": {"price": 5.222, "gpus": 1, "vcpus": 64, "memory_gb": 256},
            # G5 instances (GPU - NVIDIA A10G)
            "g5.xlarge": {"price": 1.207, "gpus": 1, "vcpus": 4, "memory_gb": 16},
            "g5.2xlarge": {"price": 1.454, "gpus": 1, "vcpus": 8, "memory_gb": 32},
            "g5.4xlarge": {"price": 1.949, "gpus": 1, "vcpus": 16, "memory_gb": 64},
            "g5.8xlarge": {"price": 2.938, "gpus": 1, "vcpus": 32, "memory_gb": 128},
            "g5.12xlarge": {"price": 6.806, "gpus": 4, "vcpus": 48, "memory_gb": 192},
            "g5.16xlarge": {"price": 3.917, "gpus": 1, "vcpus": 64, "memory_gb": 256},
            "g5.24xlarge": {"price": 9.773, "gpus": 4, "vcpus": 96, "memory_gb": 384},
            "g5.48xlarge": {"price": 19.546, "gpus": 8, "vcpus": 192, "memory_gb": 768},
        },
    },
}
