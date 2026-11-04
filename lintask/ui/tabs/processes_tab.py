"""Advanced Processes Tab with Fluent TableView, numeric sorting, heatmap, and context menu."""
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QHeaderView,
)
from qfluentwidgets import (
    SearchLineEdit,
    PrimaryPushButton,
    PushButton,
    TableView,
    CaptionLabel,
    TitleLabel,
    RoundMenu,
    Action,
    FluentIcon,
    InfoBar,
    InfoBarPosition,
)
from typing import List

from ...models.process_info import ProcessInfo
from ...models.process_model import ProcessTableModel, ProcessFilterProxyModel
from ...core.process_mgr import ProcessManager


class ProcessesTab(QWidget):
    """Processes table tab styled with QFluentWidgets and Windows 11 Fluent UX."""

    def __init__(self, process_mgr: ProcessManager = None, parent=None):
        super().__init__(parent)
        self.process_mgr = process_mgr or ProcessManager()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        # Header Title
        title_lbl = TitleLabel("Processes")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: 700; color: #f4f4f5;")
        layout.addWidget(title_lbl)

        # Top Bar: Search input + Actions
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        self.search_input = SearchLineEdit()
        self.search_input.setPlaceholderText("Search process name, PID, or user...")
        self.search_input.textChanged.connect(self._on_search_changed)
        top_bar.addWidget(self.search_input, 1)

        self.end_task_btn = PrimaryPushButton("End Task")
        self.end_task_btn.setStyleSheet("""
            PrimaryPushButton {
                background-color: #ef4444;
                border: 1px solid #dc2626;
                color: #ffffff;
                font-weight: 600;
                border-radius: 5px;
                padding: 6px 16px;
            }
            PrimaryPushButton:hover {
                background-color: #dc2626;
            }
            PrimaryPushButton:pressed {
                background-color: #b91c1c;
            }
        """)
        self.end_task_btn.clicked.connect(self._end_selected_task)
        top_bar.addWidget(self.end_task_btn)

        layout.addLayout(top_bar)

        # ----------------- Table View with Proxy Model -----------------
        self.source_model = ProcessTableModel(self)
        self.proxy_model = ProcessFilterProxyModel(self)
        self.proxy_model.setSourceModel(self.source_model)

        self.table = TableView(self)
        self.table.setModel(self.proxy_model)
        self.table.setSortingEnabled(True)

        # Header adjustments
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # PID
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # CPU %
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Memory
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Disk I/O
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # User
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Threads

        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(TableView.SelectionBehavior.SelectRows)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        # Default sort: CPU % descending (col 3)
        self.table.sortByColumn(3, Qt.SortOrder.DescendingOrder)

        layout.addWidget(self.table, 1)

        # Bottom Bar: Status count
        bottom_bar = QHBoxLayout()
        self.status_lbl = CaptionLabel("0 processes running")
        self.status_lbl.setStyleSheet("color: #a1a1aa; font-size: 12px;")
        bottom_bar.addWidget(self.status_lbl)
        bottom_bar.addStretch()

        layout.addLayout(bottom_bar)

    def update_processes(self, processes: List[ProcessInfo]):
        """Slot called from background MetricsCollector thread."""
        self.source_model.update_processes(processes)
        self.status_lbl.setText(f"{len(processes)} processes running")

    def _on_search_changed(self, text: str):
        self.proxy_model.set_filter_query(text)

    def _get_selected_process(self) -> ProcessInfo | None:
        """Helper to get the ProcessInfo object of the currently selected row."""
        selected_indexes = self.table.selectionModel().selectedRows()
        if not selected_indexes:
            return None
        proxy_idx = selected_indexes[0]
        source_idx = self.proxy_model.mapToSource(proxy_idx)
        return self.source_model.get_process_at(source_idx.row())

    def _show_context_menu(self, pos: QPoint):
        """Display Windows 11 Fluent context menu on right-click."""
        proc = self._get_selected_process()
        if not proc:
            return

        menu = RoundMenu(parent=self)

        # End Task
        act_end = Action(FluentIcon.DELETE, f"End Task ({proc.name})", self)
        act_end.triggered.connect(lambda: self._do_terminate(proc.pid))
        menu.addAction(act_end)

        # Force Kill
        act_kill = Action(FluentIcon.CLOSE, "Force Kill (SIGKILL)", self)
        act_kill.triggered.connect(lambda: self._do_force_kill(proc.pid))
        menu.addAction(act_kill)

        menu.addSeparator()

        # Pause / Resume
        if proc.status.lower() == "stopped":
            act_pause = Action(FluentIcon.PLAY, "Resume Process (SIGCONT)", self)
            act_pause.triggered.connect(lambda: self._do_resume(proc.pid))
        else:
            act_pause = Action(FluentIcon.PAUSE, "Pause Process (SIGSTOP)", self)
            act_pause.triggered.connect(lambda: self._do_pause(proc.pid))
        menu.addAction(act_pause)

        # Priority Submenu
        priority_menu = RoundMenu("Set Priority", self)
        priorities = [
            ("High (-10)", -10),
            ("Above Normal (-5)", -5),
            ("Normal (0)", 0),
            ("Below Normal (5)", 5),
            ("Low (10)", 10),
        ]
        for name, nice_val in priorities:
            act_p = Action(name, self)
            act_p.triggered.connect(lambda _, nv=nice_val: self._do_set_priority(proc.pid, nv))
            priority_menu.addAction(act_p)
        menu.addMenu(priority_menu)

        menu.addSeparator()

        # Open File Location
        act_open_loc = Action(FluentIcon.FOLDER, "Open File Location", self)
        act_open_loc.triggered.connect(lambda: self._do_open_location(proc.pid))
        menu.addAction(act_open_loc)

        # Copy Info
        act_copy_pid = Action(FluentIcon.COPY, f"Copy PID ({proc.pid})", self)
        act_copy_pid.triggered.connect(lambda: self._copy_to_clipboard(str(proc.pid)))
        menu.addAction(act_copy_pid)

        menu.exec(self.table.viewport().mapToGlobal(pos))

    # ----------------- Actions & Toast Notifications -----------------

    def _end_selected_task(self):
        proc = self._get_selected_process()
        if proc:
            self._do_terminate(proc.pid)

    def _do_terminate(self, pid: int):
        success, msg = self.process_mgr.terminate_process(pid)
        if success:
            InfoBar.success("Success", msg, duration=2500, parent=self, position=InfoBarPosition.TOP_RIGHT)
        else:
            InfoBar.error("Failed", msg, duration=3500, parent=self, position=InfoBarPosition.TOP_RIGHT)

    def _do_force_kill(self, pid: int):
        success, msg = self.process_mgr.kill_process(pid)
        if success:
            InfoBar.success("Success", msg, duration=2500, parent=self, position=InfoBarPosition.TOP_RIGHT)
        else:
            InfoBar.error("Failed", msg, duration=3500, parent=self, position=InfoBarPosition.TOP_RIGHT)

    def _do_pause(self, pid: int):
        success, msg = self.process_mgr.pause_process(pid)
        if success:
            InfoBar.info("Paused", msg, duration=2500, parent=self, position=InfoBarPosition.TOP_RIGHT)
        else:
            InfoBar.warning("Warning", msg, duration=3000, parent=self, position=InfoBarPosition.TOP_RIGHT)

    def _do_resume(self, pid: int):
        success, msg = self.process_mgr.resume_process(pid)
        if success:
            InfoBar.info("Resumed", msg, duration=2500, parent=self, position=InfoBarPosition.TOP_RIGHT)
        else:
            InfoBar.warning("Warning", msg, duration=3000, parent=self, position=InfoBarPosition.TOP_RIGHT)

    def _do_set_priority(self, pid: int, nice_val: int):
        success, msg = self.process_mgr.set_priority(pid, nice_val)
        if success:
            InfoBar.success("Priority Updated", msg, duration=2500, parent=self, position=InfoBarPosition.TOP_RIGHT)
        else:
            InfoBar.error("Permission Denied", msg, duration=3500, parent=self, position=InfoBarPosition.TOP_RIGHT)

    def _do_open_location(self, pid: int):
        success, msg = self.process_mgr.open_file_location(pid)
        if not success:
            InfoBar.warning("Notice", msg, duration=3000, parent=self, position=InfoBarPosition.TOP_RIGHT)

    def _copy_to_clipboard(self, text: str):
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)
        InfoBar.info("Copied", f"Copied '{text}' to clipboard", duration=1500, parent=self, position=InfoBarPosition.TOP_RIGHT)
