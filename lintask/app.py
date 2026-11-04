"""Application entrypoint helper."""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont
from .ui.main_window import MainWindow


def main():
    """Run LinTask Manager application."""
    app = QApplication(sys.argv)
    app.setApplicationName("LinTask Manager")
    app.setOrganizationName("LinTask")

    # Set default clean system font
    font = QFont("Inter, Ubuntu, Segoe UI, sans-serif", 10)
    app.setFont(font)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()

