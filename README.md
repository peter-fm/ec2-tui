# EC2 TUI - AWS EC2 Terminal User Interface

A modern terminal user interface (TUI) for managing AWS EC2 instances.

## Features

- List and manage EC2 instances across regions
- Start and stop instances
- Change instance types (on stopped instances)
- Automatic retry on insufficient capacity errors with live countdown
- Desktop notifications for instance state changes
- Filter instances by name and status
- Real-time retry progress tracking
- Automatic theme syncing with Omarchy (or use custom themes)
- Uses existing AWS CLI credentials and profiles

## Installation

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- AWS CLI configured with credentials
- `notify-send` for desktop notifications (optional, Linux only)

### Install Dependencies

```bash
uv sync
```

### Create Launcher Script

To run EC2 TUI from anywhere with a single command, create a symlink to the launcher script:

```bash
ln -s /home/pete/projects/tools/ec2-tui/ec2-tui ~/.local/bin/ec2-tui
```

Make sure `~/.local/bin` is in your PATH. Then you can run:

```bash
ec2-tui
```

## Configuration

EC2 TUI looks for configuration in the following locations (in order):
1. `./config.toml` (current directory)
2. `~/.config/ec2-tui/config.toml` (user config directory)

If no configuration file exists, default values will be used.

### Create Configuration File

Copy the example configuration:

```bash
cp config.toml.example ~/.config/ec2-tui/config.toml
```

Edit the configuration file to customize settings:

```toml
[ui]
default_region = "us-east-1"        # Default AWS region on startup
refresh_interval_seconds = 30       # Auto-refresh interval (0 to disable)
theme = "omarchy"                   # "omarchy" for auto-sync, or specific theme name

[retry]
enabled = true                      # Enable automatic retry on capacity errors
interval_seconds = 60               # Seconds between retry attempts
max_attempts = 60                   # Maximum retry attempts (60 = 1 hour)

[notifications]
enabled = true                      # Enable desktop notifications
urgency = "normal"                  # Notification urgency: low, normal, critical

[saved_instance_types]
types = ["t3.micro", "t3.small", "m5.large"]  # Quick-select instance types

[aws]
use_cli_credentials = true          # Use AWS CLI credentials
# profile = "my-profile"            # Optional: specify AWS profile
```

## Usage

### Run the Application

If you created the launcher script:

```bash
ec2-tui
```

Or directly from the project directory:

```bash
uv run python main.py
```

### Theming

EC2 TUI supports automatic theme syncing with [Omarchy](https://github.com/swaits/omarchy) terminal theme manager, or you can set a specific theme.

#### Automatic Theme Syncing with Omarchy

By default, EC2 TUI automatically detects and uses your current Omarchy theme:

1. EC2 TUI reads `~/.config/omarchy/current/theme/ghostty.conf`
2. Maps the theme to a compatible Textual theme
3. Updates the theme in real-time when you change it in Omarchy

Supported Omarchy themes:
- Nord, Gruvbox, Flexoki, Catppuccin (Latte/Mocha)
- Tokyo Night, Dracula, Monokai
- Rose Pine (Dawn/Moon), Everforest, Kanagawa
- And more (see [ec2_tui/utils/theme.py](ec2_tui/utils/theme.py#L52-L74) for full list)

#### Custom Theme

To use a specific theme instead of Omarchy auto-sync, set `theme` in your config:

```toml
[ui]
theme = "nord"  # Use Nord theme instead of auto-syncing
```

Available Textual themes:
- `nord`, `gruvbox`, `flexoki`
- `catppuccin-mocha`, `catppuccin-latte`
- `dracula`, `tokyo-night`, `monokai`
- `solarized-light`, `textual-dark`, `textual-light`, `textual-ansi`

#### Live Theme Updates

When using `theme = "omarchy"`, EC2 TUI watches for theme changes and updates automatically while running. No need to restart the app when you change your Omarchy theme!

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `s` | Start selected instance |
| `S` (Shift+s) | Stop selected instance |
| `t` | Change instance type (stopped instances only) |
| `r` or `F5` | Refresh instance list |
| `c` | Cancel retry for selected instance |
| `q` | Quit application |
| Up/Down arrows | Navigate instance list |

### Filtering Instances

- **Name Filter**: Type in the name filter field to search instances by name
- **Status Filter**: Select from dropdown to filter by state (all, running, stopped, pending, stopping)

### Changing Regions

Use the region selector dropdown in the controls bar to switch between AWS regions. Active retries will be cancelled when changing regions.

### Changing Instance Types

1. Select an instance (must be in `stopped` state)
2. Press `t` to open the instance type modal
3. Either:
   - Click a quick-select button for saved instance types
   - Type a custom instance type (e.g., `t3.medium`, `m5.xlarge`)
4. Click "Change" to apply

Validated instance types are automatically saved to your configuration for quick access later.

### Retry Mechanism

When starting an instance fails due to insufficient capacity:

1. EC2 TUI automatically schedules retry attempts
2. Retries occur every 60 seconds (configurable) for up to 1 hour (configurable)
3. Progress is displayed in the "Active Retries" panel
4. Desktop notification sent when instance successfully starts
5. You can cancel retries at any time by selecting the instance and pressing `c`

### AWS Credentials and Profiles

EC2 TUI uses the AWS CLI credential chain:
1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. AWS CLI credentials file (`~/.aws/credentials`)
3. IAM role (if running on EC2)

To configure AWS credentials:

```bash
aws configure
```

To use a specific AWS profile, set it in your configuration:

```toml
[aws]
use_cli_credentials = true
profile = "my-profile"  # Optional: specify AWS profile name
```

## Development

### Project Structure

```
ec2-tui/
├── ec2_tui/
│   ├── app.py                    # Main application
│   ├── config/                   # Configuration management
│   ├── models/                   # Data models
│   ├── services/                 # Business logic
│   ├── widgets/                  # UI components
│   ├── screens/                  # Screen layouts
│   └── utils/                    # Utilities and exceptions
├── tests/                        # Unit tests
├── config.toml.example           # Example configuration
├── main.py                       # Entry point
└── pyproject.toml                # Project metadata
```

### Running Tests

```bash
uv run pytest
```

### Code Quality

```bash
# Linting
uv run ruff check .

# Formatting
uv run ruff format .

# Type checking
uv run mypy ec2_tui/
```

## Troubleshooting

### Notification Issues

If desktop notifications aren't working:
- Ensure `notify-send` is installed: `which notify-send`
- Install: `sudo apt install libnotify-bin` (Debian/Ubuntu) or `sudo pacman -S libnotify` (Arch)
- Set `notifications.enabled = false` in config to disable

### AWS Credential Errors

If you see "AWS credentials not found":
1. Run `aws configure` to set up credentials
2. Verify credentials: `aws ec2 describe-instances --region us-east-1`
3. Check IAM permissions include `ec2:DescribeInstances`, `ec2:StartInstances`, `ec2:StopInstances`, `ec2:ModifyInstanceAttribute`

### Permission Denied Errors

Ensure your AWS IAM user/role has the following permissions:
- `ec2:DescribeInstances`
- `ec2:DescribeInstanceTypes`
- `ec2:StartInstances`
- `ec2:StopInstances`
- `ec2:ModifyInstanceAttribute`

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or pull request.
