"""Application entrypoint helper."""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from .ui.main_window import MainWindow
from .utils.desktop_integration import is_shortcut_installed, install_shortcut


def main():
    """Run LinTask Manager application."""
    app = QApplication(sys.argv)
    app.setApplicationName("LinTask Manager")
    app.setApplicationDisplayName("LinTask Manager")
    app.setOrganizationName("LinTask")
    
    # Associate running application with ~/.local/share/applications/lintask.desktop
    # This allows Linux Docks/Taskbars (GNOME Dash, KDE Taskbar, Ubuntu Dock) to recognize
    # the application, show its native icon, and allow 1-click "Pin to Taskbar/Dash"
    app.setDesktopFileName("lintask.desktop")

    # Auto-register desktop shortcut silently on first run if not already present
    if not is_shortcut_installed():
        install_shortcut()

    # Prevent quitting when window is minimized to system tray
    app.setQuitOnLastWindowClosed(False)

    # Set default clean system font
    font = QFont("Inter, Ubuntu, Segoe UI, sans-serif", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
