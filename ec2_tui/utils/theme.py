"""Theme detection and mapping from Omarchy."""

import asyncio
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import EC2TUIApp


def get_omarchy_theme() -> Optional[str]:
    """
    Get the current theme from Omarchy ghostty config.

    Returns:
        Theme name if found, None otherwise.
    """
    ghostty_conf = Path.home() / ".config" / "omarchy" / "current" / "theme" / "ghostty.conf"

    if not ghostty_conf.exists():
        return None

    try:
        with open(ghostty_conf) as f:
            for line in f:
                line = line.strip()
                if line.startswith("theme"):
                    # Parse "theme = Nord" format
                    parts = line.split("=", 1)
                    if len(parts) == 2:
                        theme_name = parts[1].strip()
                        return theme_name.lower()
        return None
    except Exception:
        return None


def map_theme_to_textual(omarchy_theme: Optional[str]) -> str:
    """
    Map Omarchy theme name to Textual theme name.

    Args:
        omarchy_theme: Theme name from Omarchy config.

    Returns:
        Textual theme name.
    """
    if not omarchy_theme:
        return "textual-dark"

    # Direct mappings for themes with same names
    direct_mappings = {
        "nord": "nord",
        "gruvbox": "gruvbox",
        "flexoki": "flexoki",
        "catppuccin-latte": "catppuccin-latte",
    }

    # Special mappings for themes with different names
    special_mappings = {
        "catppuccin": "catppuccin-mocha",
        "tokyo-night": "tokyo-night",
        "dracula": "dracula",
        "monokai": "monokai",
        "everforest": "gruvbox",  # Similar aesthetic
        "kanagawa": "tokyo-night",  # Similar aesthetic
        "matte-black": "textual-dark",
        "hackerman": "textual-ansi",
        "ethereal": "textual-dark",
        "flexoki-light": "flexoki",
        "rose pine": "textual-dark",  # Rose Pine (dark)
        "rose pine dawn": "solarized-light",  # Rose Pine Dawn (light)
        "rose pine moon": "textual-dark",  # Rose Pine Moon (dark)
    }

    # Check direct mapping first
    if omarchy_theme in direct_mappings:
        return direct_mappings[omarchy_theme]

    # Check special mapping
    if omarchy_theme in special_mappings:
        return special_mappings[omarchy_theme]

    # Default fallback
    return "textual-dark"


def get_textual_theme(config_theme: Optional[str] = None) -> str:
    """
    Get the appropriate Textual theme based on config or Omarchy.

    Args:
        config_theme: Theme from config. If "omarchy" or None, uses Omarchy theme.

    Returns:
        Textual theme name to use.
    """
    # If config specifies "omarchy" or is not set, use Omarchy theme detection
    if config_theme is None or config_theme == "omarchy":
        omarchy_theme = get_omarchy_theme()
        return map_theme_to_textual(omarchy_theme)

    # Otherwise, use the specific theme name from config
    return config_theme


async def watch_theme_changes(app: "EC2TUIApp") -> None:
    """
    Watch for changes to the Omarchy theme config and update the app theme.

    Only watches if config theme is set to "omarchy".

    Args:
        app: The EC2TUI app instance to update.
    """
    # Only watch if using Omarchy theme detection
    if app.config.ui.theme != "omarchy":
        return

    ghostty_conf = Path.home() / ".config" / "omarchy" / "current" / "theme" / "ghostty.conf"

    if not ghostty_conf.exists():
        return

    last_theme = get_textual_theme(app.config.ui.theme)

    while True:
        await asyncio.sleep(1)  # Check every second

        try:
            current_theme = get_textual_theme(app.config.ui.theme)
            if current_theme != last_theme:
                app.theme = current_theme
                last_theme = current_theme
        except Exception:
            # Ignore errors and continue watching
            pass
