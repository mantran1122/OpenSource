"""Data model representing a Startup Application (.desktop entry)."""
from dataclasses import dataclass


@dataclass
class StartupItem:
    file_name: str
    name: str
    command: str
    comment: str
    icon: str
    is_system: bool
    enabled: bool
    file_path: str

