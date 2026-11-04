"""Utility functions for LinTask."""
from .formatters import (
    format_bytes,
    format_speed,
    format_uptime,
    format_freq,
    format_percent,
)
from .desktop_integration import (
    is_shortcut_installed,
    install_shortcut,
    remove_shortcut,
)

__all__ = [
    "format_bytes",
    "format_speed",
    "format_uptime",
    "format_freq",
    "format_percent",
    "is_shortcut_installed",
    "install_shortcut",
    "remove_shortcut",
]
