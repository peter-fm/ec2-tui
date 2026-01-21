"""EC2 TUI application entry point."""

import argparse

from ec2_tui.app import main


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="EC2 TUI - Terminal-based AWS EC2 instance management"
    )
    parser.add_argument(
        "-p", "--profile",
        help="AWS CLI profile name to use",
        default=None,
    )
    parser.add_argument(
        "-r", "--region",
        help="AWS region to use",
        default=None,
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(profile=args.profile, region=args.region)
