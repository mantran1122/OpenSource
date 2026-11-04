"""Application entrypoint helper."""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from .ui.main_window import MainWindow
from .utils.desktop_integration import install_shortcut


def main():
    """Run LinTask Manager application."""
    app = QApplication(sys.argv)
    app.setApplicationName("LinTask Manager")
    app.setApplicationDisplayName("LinTask Manager")
    app.setOrganizationName("LinTask")
    
    # Associate running application with desktop file (omitting .desktop per Qt guideline)
    # This enables docks/taskbars to recognize the process and display its native icon.
    app.setDesktopFileName("lintask")

    # Ensure desktop shortcut and taskbar integrations are active
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
