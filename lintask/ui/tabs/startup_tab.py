"""Startup Apps tab showing autostart desktop entries with Fluent toggles."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QFileDialog,
)
from qfluentwidgets import (
    TitleLabel,
    SubtitleLabel,
    CaptionLabel,
    SearchLineEdit,
    PrimaryPushButton,
    PushButton,
    TransparentToolButton,
    SwitchButton,
    CardWidget,
    SmoothScrollArea,
    FluentIcon,
    InfoBar,
    InfoBarPosition,
    MessageBoxBase,
    LineEdit,
)
from typing import List

from ...core.startup_mgr import StartupManager
from ...models.startup_item import StartupItem


class AddStartupDialog(MessageBoxBase):
    """Fluent dialog to input new startup application details."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("Add Startup Application", self)
        self.titleLabel.setStyleSheet("font-size: 16px; font-weight: bold; color: #f4f4f5;")

        self.name_edit = LineEdit(self)
        self.name_edit.setPlaceholderText("Application Name (e.g. My Script)")

        cmd_layout = QHBoxLayout()
        self.cmd_edit = LineEdit(self)
        self.cmd_edit.setPlaceholderText("Executable or command (e.g. /usr/bin/discord)")
        self.browse_btn = PushButton("Browse...", self)
        self.browse_btn.clicked.connect(self._browse_file)
        cmd_layout.addWidget(self.cmd_edit, 1)
        cmd_layout.addWidget(self.browse_btn)

        self.comment_edit = LineEdit(self)
        self.comment_edit.setPlaceholderText("Optional description")

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.name_edit)
        self.viewLayout.addLayout(cmd_layout)
        self.viewLayout.addWidget(self.comment_edit)

        self.widget.setMinimumWidth(440)

    def _browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Executable", "/usr/bin")
        if file_path:
            self.cmd_edit.setText(file_path)


class StartupItemCard(CardWidget):
    """Card widget representing an autostart application."""

    def __init__(self, item: StartupItem, on_toggle, on_delete, parent=None):
        super().__init__(parent)
        self.item = item
        self.on_toggle = on_toggle
        self.on_delete = on_delete

        self.setFixedHeight(74)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(16)

        # 1. Left circular initial badge
        badge = QLabel(item.name[0].upper() if item.name else "A")
        badge.setFixedSize(38, 38)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet("""
            background-color: #0284c7;
            color: #ffffff;
            font-size: 16px;
            font-weight: bold;
            border-radius: 19px;
        """)
        layout.addWidget(badge)

        # 2. Middle info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        info_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Name + Scope Badge
        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        name_lbl = SubtitleLabel(item.name)
        name_lbl.setStyleSheet("font-size: 14px; font-weight: 600; color: #f4f4f5;")
        title_row.addWidget(name_lbl)

        scope_text = "System" if item.is_system else "User"
        scope_color = "#38bdf8" if not item.is_system else "#a1a1aa"
        scope_bg = "#0c4a6e" if not item.is_system else "#27272a"
        scope_badge = QLabel(scope_text)
        scope_badge.setStyleSheet(f"""
            background-color: {scope_bg};
            color: {scope_color};
            font-size: 10px;
            font-weight: 600;
            padding: 1px 6px;
            border-radius: 4px;
        """)
        title_row.addWidget(scope_badge)
        title_row.addStretch()
        info_layout.addLayout(title_row)

        # Command / Exec
        cmd_lbl = CaptionLabel(item.command or item.comment or "No command specified")
        cmd_lbl.setStyleSheet("font-size: 11px; color: #71717a; font-family: monospace;")
        info_layout.addWidget(cmd_lbl)

        layout.addLayout(info_layout, 1)

        # 3. Right: Switch Toggle
        self.switch_btn = SwitchButton()
        self.switch_btn.setChecked(item.enabled)
        self.switch_btn.setOnText("Enabled")
        self.switch_btn.setOffText("Disabled")
        self.switch_btn.checkedChanged.connect(lambda checked: self.on_toggle(self.item, checked))
        layout.addWidget(self.switch_btn)

        # 4. Delete action (only if not a pure system file)
        self.del_btn = TransparentToolButton(FluentIcon.DELETE, self)
        self.del_btn.setToolTip("Delete Startup Item")
        self.del_btn.clicked.connect(lambda: self.on_delete(self.item))
        layout.addWidget(self.del_btn)


class StartupTab(QWidget):
    """Tab to list, search, add, toggle, and manage startup applications."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mgr = StartupManager()
        self._all_items: List[StartupItem] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header Title
        title_lbl = TitleLabel("Startup Apps")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: 700; color: #f4f4f5;")
        layout.addWidget(title_lbl)

        # Top Action Bar: Search + Add + Refresh
        action_bar = QHBoxLayout()
        action_bar.setSpacing(10)

        self.search_input = SearchLineEdit()
        self.search_input.setPlaceholderText("Filter startup apps by name or command...")
        self.search_input.textChanged.connect(self._filter_items)
        action_bar.addWidget(self.search_input, 1)

        self.add_btn = PrimaryPushButton("Add App", icon=FluentIcon.ADD)
        self.add_btn.clicked.connect(self._open_add_dialog)
        action_bar.addWidget(self.add_btn)

        self.refresh_btn = PushButton("Refresh", icon=FluentIcon.SYNC)
        self.refresh_btn.clicked.connect(self.reload_items)
        action_bar.addWidget(self.refresh_btn)

        layout.addLayout(action_bar)

        # Scroll Area holding the cards
        self.scroll_area = SmoothScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none; background: transparent;")

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)
        self.cards_layout.addStretch()

        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area, 1)

        # Initial Load
        self.reload_items()

    def reload_items(self):
        """Scan autostart directories and populate cards."""
        self._all_items = self.mgr.scan_startup_items()
        self._filter_items(self.search_input.text())

    def _render_cards(self, items: List[StartupItem]):
        """Clear and rebuild card widgets."""
        # Clear existing items except the stretch
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not items:
            empty_lbl = CaptionLabel("No startup applications found matching your criteria.")
            empty_lbl.setStyleSheet("color: #71717a; font-size: 13px; padding: 20px;")
            empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cards_layout.insertWidget(0, empty_lbl)
            return

        for item in items:
            card = StartupItemCard(item, on_toggle=self._on_toggle, on_delete=self._on_delete, parent=self)
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)

    def _filter_items(self, query: str):
        query = query.strip().lower()
        if not query:
            self._render_cards(self._all_items)
            return

        filtered = [
            it for it in self._all_items
            if query in it.name.lower() or query in it.command.lower() or query in it.comment.lower()
        ]
        self._render_cards(filtered)

    def _on_toggle(self, item: StartupItem, enabled: bool):
        success, msg = self.mgr.set_enabled(item, enabled)
        if success:
            item.enabled = enabled
            InfoBar.success("Success", msg, duration=2000, parent=self, position=InfoBarPosition.TOP_RIGHT)
        else:
            InfoBar.error("Error", msg, duration=3500, parent=self, position=InfoBarPosition.TOP_RIGHT)

    def _on_delete(self, item: StartupItem):
        success, msg = self.mgr.delete_startup_item(item)
        if success:
            InfoBar.success("Deleted", msg, duration=2000, parent=self, position=InfoBarPosition.TOP_RIGHT)
            self.reload_items()
        else:
            InfoBar.warning("Cannot Delete", msg, duration=3500, parent=self, position=InfoBarPosition.TOP_RIGHT)

    def _open_add_dialog(self):
        dialog = AddStartupDialog(self.window())
        if dialog.exec():
            name = dialog.name_edit.text()
            cmd = dialog.cmd_edit.text()
            comment = dialog.comment_edit.text()
            success, msg = self.mgr.add_startup_item(name, cmd, comment)
            if success:
                InfoBar.success("App Added", msg, duration=2500, parent=self, position=InfoBarPosition.TOP_RIGHT)
                self.reload_items()
            else:
                InfoBar.error("Failed", msg, duration=3500, parent=self, position=InfoBarPosition.TOP_RIGHT)

