"""Settings Tab for configuring update speed, themes, desktop integration, and project info."""
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
)
from qfluentwidgets import (
    TitleLabel,
    SubtitleLabel,
    CaptionLabel,
    CardWidget,
    ComboBox,
    PushButton,
    PrimaryPushButton,
    SmoothScrollArea,
    FluentIcon,
    IconWidget,
    InfoBar,
    InfoBarPosition,
    setTheme,
    Theme,
)

from ...utils.desktop_integration import (
    is_shortcut_installed,
    install_shortcut,
    remove_shortcut,
)


def _create_setting_card(icon: FluentIcon, title: str, description: str, right_widget: QWidget) -> CardWidget:
    """Helper to create a Fluent setting card with icon, title, description and right control."""
    card = CardWidget()
    card.setFixedHeight(72)
    layout = QHBoxLayout(card)
    layout.setContentsMargins(16, 12, 16, 12)
    layout.setSpacing(14)

    # Left Icon
    icon_widget = IconWidget(icon)
    icon_widget.setFixedSize(22, 22)
    layout.addWidget(icon_widget)

    # Info Text
    text_layout = QVBoxLayout()
    text_layout.setSpacing(2)
    text_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

    t_lbl = SubtitleLabel(title)
    t_lbl.setStyleSheet("font-size: 13px; font-weight: 600; color: #f4f4f5;")
    text_layout.addWidget(t_lbl)

    d_lbl = CaptionLabel(description)
    d_lbl.setStyleSheet("font-size: 11px; color: #a1a1aa;")
    text_layout.addWidget(d_lbl)

    layout.addLayout(text_layout, 1)

    # Right Widget
    layout.addWidget(right_widget)
    return card


class SettingsTab(QWidget):
    """Settings and About tab styled with Windows 11 Fluent Design."""

    def __init__(self, main_window=None, parent=None):
        super().__init__(parent)
        self.main_window = main_window

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Header Title
        title_lbl = TitleLabel("Settings")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: 700; color: #f4f4f5;")
        main_layout.addWidget(title_lbl)

        # Scrollable Settings Container
        scroll = SmoothScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background: transparent;")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(18)

        # ---------------- Section 1: Monitoring ----------------
        sec1_title = CaptionLabel("MONITORING & PERFORMANCE")
        sec1_title.setStyleSheet("font-weight: bold; color: #71717a; font-size: 11px; letter-spacing: 0.5px;")
        layout.addWidget(sec1_title)

        # Update Speed ComboBox
        self.speed_combo = ComboBox()
        self.speed_combo.addItems([
            "High (0.5 sec)",
            "Normal (1.0 sec) - Recommended",
            "Eco / Power Saving (2.0 sec)",
        ])
        self.speed_combo.setCurrentIndex(1)
        self.speed_combo.currentIndexChanged.connect(self._on_speed_changed)
        self.speed_combo.setFixedWidth(220)

        card_speed = _create_setting_card(
            FluentIcon.UPDATE,
            "Update Frequency",
            "Controls how frequently metrics and graphs are sampled from system sensors.",
            self.speed_combo,
        )
        layout.addWidget(card_speed)

        # ---------------- Section 2: Appearance ----------------
        sec2_title = CaptionLabel("APPEARANCE")
        sec2_title.setStyleSheet("font-weight: bold; color: #71717a; font-size: 11px; letter-spacing: 0.5px;")
        layout.addWidget(sec2_title)

        # Theme ComboBox
        self.theme_combo = ComboBox()
        self.theme_combo.addItems(["Dark Theme", "Light Theme"])
        self.theme_combo.setCurrentIndex(0)
        self.theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        self.theme_combo.setFixedWidth(220)

        card_theme = _create_setting_card(
            FluentIcon.PALETTE,
            "Application Theme",
            "Switch between Fluent Dark Mode and Light Mode.",
            self.theme_combo,
        )
        layout.addWidget(card_theme)

        # ---------------- Section 3: Desktop Integration ----------------
        sec3_title = CaptionLabel("SYSTEM INTEGRATION")
        sec3_title.setStyleSheet("font-weight: bold; color: #71717a; font-size: 11px; letter-spacing: 0.5px;")
        layout.addWidget(sec3_title)

        # Shortcut Button
        self.shortcut_btn = PushButton()
        self._update_shortcut_btn()
        self.shortcut_btn.clicked.connect(self._on_shortcut_clicked)
        self.shortcut_btn.setFixedWidth(220)

        self.card_shortcut = _create_setting_card(
            FluentIcon.APPLICATION,
            "Linux Application Launcher",
            "Add or remove LinTask Manager shortcut in your system application menu.",
            self.shortcut_btn,
        )
        layout.addWidget(self.card_shortcut)

        # ---------------- Section 4: About ----------------
        sec4_title = CaptionLabel("ABOUT & OPEN SOURCE")
        sec4_title.setStyleSheet("font-weight: bold; color: #71717a; font-size: 11px; letter-spacing: 0.5px;")
        layout.addWidget(sec4_title)

        # About Card
        about_card = CardWidget()
        about_card.setFixedHeight(82)
        about_layout = QHBoxLayout(about_card)
        about_layout.setContentsMargins(16, 12, 16, 12)
        about_layout.setSpacing(14)

        icon_github = IconWidget(FluentIcon.GITHUB)
        icon_github.setFixedSize(24, 24)
        about_layout.addWidget(icon_github)

        about_text = QVBoxLayout()
        about_text.setSpacing(2)
        about_text.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        title_about = SubtitleLabel("LinTask Manager  •  v0.1.0")
        title_about.setStyleSheet("font-size: 13px; font-weight: 600; color: #f4f4f5;")
        about_text.addWidget(title_about)

        desc_about = CaptionLabel("Open source, Windows-style Task Manager for Linux  •  GPL-3.0 License")
        desc_about.setStyleSheet("font-size: 11px; color: #a1a1aa;")
        about_text.addWidget(desc_about)
        about_layout.addLayout(about_text, 1)

        github_btn = PrimaryPushButton("GitHub Repo", icon=FluentIcon.LINK)
        github_btn.setFixedWidth(140)
        github_btn.clicked.connect(self._open_github)
        about_layout.addWidget(github_btn)

        layout.addWidget(about_card)

        layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll, 1)

    def _on_speed_changed(self, index: int):
        intervals = [0.5, 1.0, 2.0]
        if index < len(intervals) and self.main_window and hasattr(self.main_window, "collector"):
            new_interval = intervals[index]
            self.main_window.collector.interval_sec = new_interval
            InfoBar.success(
                "Update Frequency Changed",
                f"Sampling interval set to {new_interval}s.",
                duration=2000,
                parent=self,
                position=InfoBarPosition.TOP_RIGHT,
            )

    def _on_theme_changed(self, index: int):
        if index == 0:
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.LIGHT)

    def _update_shortcut_btn(self):
        if is_shortcut_installed():
            self.shortcut_btn.setText("Remove from Menu")
        else:
            self.shortcut_btn.setText("Add to App Menu")

    def _on_shortcut_clicked(self):
        if is_shortcut_installed():
            success, msg = remove_shortcut()
            if success:
                InfoBar.info("Removed", msg, duration=2500, parent=self, position=InfoBarPosition.TOP_RIGHT)
            else:
                InfoBar.error("Error", msg, duration=3500, parent=self, position=InfoBarPosition.TOP_RIGHT)
        else:
            success, msg = install_shortcut()
            if success:
                InfoBar.success("Installed", msg, duration=2500, parent=self, position=InfoBarPosition.TOP_RIGHT)
            else:
                InfoBar.error("Error", msg, duration=3500, parent=self, position=InfoBarPosition.TOP_RIGHT)
        self._update_shortcut_btn()

    def _open_github(self):
        QDesktopServices.openUrl(QUrl("https://github.com/your-username/LinTask-Manager"))

