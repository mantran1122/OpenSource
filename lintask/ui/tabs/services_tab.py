"""Services Tab for listing, filtering and controlling systemd services."""
from typing import List, Optional
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QHeaderView,
    QApplication,
)
from qfluentwidgets import (
    TitleLabel,
    CaptionLabel,
    SearchLineEdit,
    ComboBox,
    PrimaryPushButton,
    PushButton,
    TableView,
    RoundMenu,
    Action,
    FluentIcon,
    InfoBar,
    InfoBarPosition,
)

from ...core.service_mgr import ServiceManager
from ...models.service_item import ServiceItem
from ...models.service_model import ServiceTableModel, ServiceFilterProxyModel


class ServicesTab(QWidget):
    """Systemd services management tab styled with Windows 11 Fluent UI."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mgr = ServiceManager()
        self._all_services: List[ServiceItem] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # 1. Header Title
        title_lbl = TitleLabel("Services")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: 700; color: #f4f4f5;")
        layout.addWidget(title_lbl)

        # 2. Action Bar: Search + Filter + Action Buttons
        action_bar = QHBoxLayout()
        action_bar.setSpacing(10)

        # Search Bar
        self.search_input = SearchLineEdit()
        self.search_input.setPlaceholderText("Search service name or description...")
        self.search_input.textChanged.connect(self._on_search_changed)
        action_bar.addWidget(self.search_input, 1)

        # Status Filter ComboBox
        self.status_combo = ComboBox()
        self.status_combo.addItems(["All Services", "Active (Running)", "Inactive (Stopped)", "Failed"])
        self.status_combo.setCurrentIndex(0)
        self.status_combo.currentIndexChanged.connect(self._on_status_filter_changed)
        self.status_combo.setFixedWidth(160)
        action_bar.addWidget(self.status_combo)

        # Action Buttons
        self.start_btn = PrimaryPushButton("Start", icon=FluentIcon.PLAY)
        self.start_btn.clicked.connect(self._start_selected_service)
        action_bar.addWidget(self.start_btn)

        self.stop_btn = PushButton("Stop", icon=FluentIcon.PAUSE)
        self.stop_btn.clicked.connect(self._stop_selected_service)
        action_bar.addWidget(self.stop_btn)

        self.restart_btn = PushButton("Restart", icon=FluentIcon.SYNC)
        self.restart_btn.clicked.connect(self._restart_selected_service)
        action_bar.addWidget(self.restart_btn)

        layout.addLayout(action_bar)

        # 3. Services Table with Proxy Model
        self.source_model = ServiceTableModel(self)
        self.proxy_model = ServiceFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.source_model)

        self.table = TableView(self)
        self.table.setModel(self.proxy_model)
        self.table.setSortingEnabled(True)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(TableView.SelectionBehavior.SelectRows)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.table, 1)

        # 4. Bottom Status Count
        bottom_bar = QHBoxLayout()
        self.status_lbl = CaptionLabel("0 services")
        self.status_lbl.setStyleSheet("color: #a1a1aa; font-size: 12px;")
        bottom_bar.addWidget(self.status_lbl)
        bottom_bar.addStretch()

        self.refresh_btn = PushButton("Refresh", icon=FluentIcon.SYNC)
        self.refresh_btn.clicked.connect(self.reload_services)
        bottom_bar.addWidget(self.refresh_btn)

        layout.addLayout(bottom_bar)

        # Initial Load
        self.reload_services()

    def reload_services(self):
        """Scan systemd services in background and populate table."""
        self._all_services = self.mgr.scan_services()
        self.source_model.update_services(self._all_services)

        running_count = sum(1 for s in self._all_services if s.is_running)
        failed_count = sum(1 for s in self._all_services if s.is_failed)
        self.status_lbl.setText(
            f"{len(self._all_services)} services total  •  {running_count} running  •  {failed_count} failed"
        )

    def _on_search_changed(self, text: str):
        self.proxy_model.set_filter_query(text)

    def _on_status_filter_changed(self, index: int):
        mapping = {0: "all", 1: "active", 2: "inactive", 3: "failed"}
        self.proxy_model.set_status_filter(mapping.get(index, "all"))

    def _get_selected_service(self) -> Optional[ServiceItem]:
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return None
        proxy_idx = selected[0]
        source_idx = self.proxy_model.mapToSource(proxy_idx)
        return self.source_model.get_service_at(source_idx.row())

    def _show_context_menu(self, pos: QPoint):
        service = self._get_selected_service()
        if not service:
            return

        menu = RoundMenu(parent=self)

        # Start / Stop / Restart
        if service.is_running:
            act_stop = Action(FluentIcon.PAUSE, f"Stop ({service.name})", self)
            act_stop.triggered.connect(lambda: self._do_action("stop", service.name))
            menu.addAction(act_stop)
        else:
            act_start = Action(FluentIcon.PLAY, f"Start ({service.name})", self)
            act_start.triggered.connect(lambda: self._do_action("start", service.name))
            menu.addAction(act_start)

        act_restart = Action(FluentIcon.SYNC, "Restart Service", self)
        act_restart.triggered.connect(lambda: self._do_action("restart", service.name))
        menu.addAction(act_restart)

        menu.addSeparator()

        # Enable / Disable at boot
        act_enable = Action(FluentIcon.POWER_BUTTON, "Enable (Start at boot)", self)
        act_enable.triggered.connect(lambda: self._do_action("enable", service.name))
        menu.addAction(act_enable)

        act_disable = Action(FluentIcon.CLOSE, "Disable from boot", self)
        act_disable.triggered.connect(lambda: self._do_action("disable", service.name))
        menu.addAction(act_disable)

        menu.addSeparator()

        # Copy Service Name
        act_copy = Action(FluentIcon.COPY, f"Copy Name ('{service.name}')", self)
        act_copy.triggered.connect(lambda: self._copy_to_clipboard(service.name))
        menu.addAction(act_copy)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    # ----------------- Actions & Toasts -----------------

    def _start_selected_service(self):
        s = self._get_selected_service()
        if s:
            self._do_action("start", s.name)

    def _stop_selected_service(self):
        s = self._get_selected_service()
        if s:
            self._do_action("stop", s.name)

    def _restart_selected_service(self):
        s = self._get_selected_service()
        if s:
            self._do_action("restart", s.name)

    def _do_action(self, action: str, service_name: str):
        actions_map = {
            "start": self.mgr.start_service,
            "stop": self.mgr.stop_service,
            "restart": self.mgr.restart_service,
            "enable": self.mgr.enable_service,
            "disable": self.mgr.disable_service,
        }
        func = actions_map.get(action)
        if not func:
            return

        success, msg = func(service_name)
        if success:
            InfoBar.success("Success", msg, duration=2500, parent=self, position=InfoBarPosition.TOP_RIGHT)
            self.reload_services()
        else:
            InfoBar.error("Action Failed", msg, duration=4000, parent=self, position=InfoBarPosition.TOP_RIGHT)

    def _copy_to_clipboard(self, text: str):
        QApplication.clipboard().setText(text)
        InfoBar.info("Copied", f"Copied '{text}' to clipboard", duration=1500, parent=self, position=InfoBarPosition.TOP_RIGHT)

