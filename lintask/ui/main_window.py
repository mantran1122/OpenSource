"""Main Window hosting tabs, background worker threads, and System Tray integration."""
import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSystemTrayIcon, QApplication
from qfluentwidgets import (
    FluentWindow,
    FluentIcon,
    NavigationItemPosition,
    TitleLabel,
    CaptionLabel,
    RoundMenu,
    Action,
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
        self.icon_path = os.path.join(root_dir, "assets", "icons", "lintask.svg")
        if os.path.exists(self.icon_path):
            self.setWindowIcon(QIcon(self.icon_path))

        # System Tray Configuration
        self.minimize_to_tray = True
        self._tray_notification_shown = False
        self._setup_tray(self.icon_path)

        # Connect signals
        self.collector.snapshot_ready.connect(self.performance_tab.update_snapshot)
        self.collector.snapshot_ready.connect(self._update_tray_tooltip)
        self.collector.processes_ready.connect(self.processes_tab.update_processes)
        self.collector.start()

    def _setup_tray(self, icon_path: str):
        """Configure System Tray Icon on Linux panel/taskbar."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self.tray_icon = QSystemTrayIcon(self)
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        self.tray_icon.setToolTip("LinTask Manager\nCPU: --% | RAM: --%")

        # Context Menu for Tray Icon
        tray_menu = RoundMenu(parent=self)

        act_open = Action(FluentIcon.APPLICATION, "Open LinTask Manager", self)
        act_open.triggered.connect(self._show_and_activate)
        tray_menu.addAction(act_open)

        act_perf = Action(FluentIcon.SPEED_HIGH, "Performance", self)
        act_perf.triggered.connect(lambda: self._switch_and_show(self.performance_tab))
        tray_menu.addAction(act_perf)

        act_proc = Action(FluentIcon.APPLICATION, "Processes", self)
        act_proc.triggered.connect(lambda: self._switch_and_show(self.processes_tab))
        tray_menu.addAction(act_proc)

        tray_menu.addSeparator()

        act_exit = Action(FluentIcon.CLOSE, "Exit LinTask", self)
        act_exit.triggered.connect(self._force_quit)
        tray_menu.addAction(act_exit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        """Clicking the tray icon toggles between showing and hiding the window."""
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            if self.isVisible() and not self.isMinimized():
                self.hide()
            else:
                self._show_and_activate()

    def _show_and_activate(self):
        """Restore window and bring it to foreground."""
        self.show()
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _switch_and_show(self, interface):
        """Switch to specified tab and activate window."""
        self.switchTo(interface)
        self._show_and_activate()

    def _update_tray_tooltip(self, snapshot):
        """Update live system metrics in tray tooltip."""
        if hasattr(self, "tray_icon") and self.tray_icon.isVisible():
            cpu_p = snapshot.cpu.overall_percent
            mem_p = snapshot.memory.percent
            self.tray_icon.setToolTip(
                f"LinTask Manager\nCPU: {cpu_p:.1f}%\nRAM: {mem_p:.1f}%\nClick to open"
            )

    def _force_quit(self):
        """Explicitly quit application and terminate worker threads."""
        self.minimize_to_tray = False
        if hasattr(self, "collector"):
            self.collector.stop()
        if hasattr(self, "tray_icon"):
            self.tray_icon.hide()
        QApplication.quit()

    def closeEvent(self, event):
        """Minimize to system tray when closed, or quit if tray not active."""
        if getattr(self, "minimize_to_tray", False) and hasattr(self, "tray_icon") and self.tray_icon.isVisible():
            event.ignore()
            self.hide()
            if not self._tray_notification_shown:
                self.tray_icon.showMessage(
                    "LinTask Manager",
                    "LinTask is still monitoring in the background.\nClick the tray icon to restore.",
                    QSystemTrayIcon.MessageIcon.Information,
                    2500,
                )
                self._tray_notification_shown = True
        else:
            self._force_quit()
            super().closeEvent(event)
