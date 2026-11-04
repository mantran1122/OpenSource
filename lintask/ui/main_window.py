"""Main Window hosting tabs and background worker threads using FluentWindow."""
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import (
    FluentWindow,
    FluentIcon,
    NavigationItemPosition,
    TitleLabel,
    CaptionLabel,
    setTheme,
    Theme,
)

from .tabs.performance_tab import PerformanceTab
from .tabs.processes_tab import ProcessesTab
from .tabs.startup_tab import StartupTab
from .tabs.services_tab import ServicesTab
from .tabs.settings_tab import SettingsTab
from ..core.collector import MetricsCollector


class MainWindow(FluentWindow):
    """Main Application Window for LinTask Manager based on Windows 11 Fluent Design."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LinTask Manager")
        self.resize(1140, 760)
        self.setMinimumSize(900, 600)

        # Force Modern Dark Theme
        setTheme(Theme.DARK)

        # Initialize background collector thread
        self.collector = MetricsCollector(interval_sec=1.0)

        # 1. Performance Tab (Primary)
        self.performance_tab = PerformanceTab(self)
        self.performance_tab.setObjectName("performanceTab")
        self.addSubInterface(
            self.performance_tab,
            FluentIcon.SPEED_HIGH,
            "Performance",
            position=NavigationItemPosition.TOP,
        )

        # 2. Processes Tab
        self.processes_tab = ProcessesTab(process_mgr=self.collector.process_mgr, parent=self)
        self.processes_tab.setObjectName("processesTab")
        self.addSubInterface(
            self.processes_tab,
            FluentIcon.APPLICATION,
            "Processes",
            position=NavigationItemPosition.TOP,
        )

        # 3. Startup Apps Tab
        self.startup_tab = StartupTab(self)
        self.startup_tab.setObjectName("startupTab")
        self.addSubInterface(
            self.startup_tab,
            FluentIcon.POWER_BUTTON,
            "Startup Apps",
            position=NavigationItemPosition.TOP,
        )

        # 4. Services Tab
        self.services_tab = ServicesTab(self)
        self.services_tab.setObjectName("servicesTab")
        self.addSubInterface(
            self.services_tab,
            FluentIcon.SYNC,
            "Services",
            position=NavigationItemPosition.TOP,
        )

        # 5. Settings Tab (Pinned to bottom)
        self.settings_tab = SettingsTab(main_window=self, parent=self)
        self.settings_tab.setObjectName("settingsTab")
        self.addSubInterface(
            self.settings_tab,
            FluentIcon.SETTING,
            "Settings",
            position=NavigationItemPosition.BOTTOM,
        )

        # Set Window Icon
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(root_dir, "assets", "icons", "lintask.svg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Connect signals
        self.collector.snapshot_ready.connect(self.performance_tab.update_snapshot)
        self.collector.processes_ready.connect(self.processes_tab.update_processes)
        self.collector.start()

    def closeEvent(self, event):
        """Ensure background collector stops cleanly when closing window."""
        if hasattr(self, "collector"):
            self.collector.stop()
        super().closeEvent(event)
