"""Data structure representing a systemd service."""
from dataclasses import dataclass


@dataclass
class ServiceItem:
    name: str
    load_state: str
    active_state: str
    sub_state: str
    description: str

    @property
    def is_running(self) -> bool:
        return self.active_state.lower() == "active"

    @property
    def is_failed(self) -> bool:
        return self.active_state.lower() == "failed"

