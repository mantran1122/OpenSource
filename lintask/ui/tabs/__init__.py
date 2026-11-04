"""Tab pages for the main window."""
from .performance_tab import PerformanceTab
from .processes_tab import ProcessesTab
from .startup_tab import StartupTab
from .services_tab import ServicesTab
from .settings_tab import SettingsTab

__all__ = [
    "PerformanceTab",
    "ProcessesTab",
    "StartupTab",
    "ServicesTab",
    "SettingsTab",
]
