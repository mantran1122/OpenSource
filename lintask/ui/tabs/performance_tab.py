"""Performance Tab displaying real-time graphs and hardware statistics with Fluent Design."""
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QStackedWidget,
    QFrame,
)
from qfluentwidgets import (
    TitleLabel,
    SubtitleLabel,
    CaptionLabel,
    BodyLabel,
    CardWidget,
)

from ..widgets.live_graph import LiveGraphWidget, MultiLineGraphWidget
from ..widgets.stat_card import StatCard
from ...models.metrics import SystemSnapshot
from ...utils.formatters import (
    format_bytes,
    format_speed,
    format_uptime,
    format_freq,
    format_percent,
)


def _add_info_item(grid: QGridLayout, row: int, col: int, title: str, default_val: str = "--") -> BodyLabel:
    """Helper to create and add a Windows Task Manager-style metric label-value pair directly into a grid."""
    container = QFrame()
    container.setStyleSheet("background: transparent;")
    layout = QVBoxLayout(container)
    layout.setContentsMargins(6, 4, 6, 4)
    layout.setSpacing(2)

    title_lbl = CaptionLabel(title)
    title_lbl.setStyleSheet("color: #a1a1aa; font-size: 11px;")
    layout.addWidget(title_lbl)

    val_lbl = BodyLabel(default_val)
    val_lbl.setStyleSheet("color: #f4f4f5; font-size: 15px; font-weight: 600;")
    layout.addWidget(val_lbl)

    grid.addWidget(container, row, col)
    return val_lbl


class PerformanceTab(QWidget):
    """Windows 11-style Performance Tab with live graphs and system specs."""

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(18)

        # ----------------- Left Sidebar -----------------
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(280)
        sidebar_frame.setStyleSheet("background: transparent;")
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(8)

        self.cards = {
            "cpu": StatCard("cpu", "CPU", "% utilization", accent_color="#0078d4", fixed_range_y=(0, 100)),
            "memory": StatCard("memory", "Memory", "In use", accent_color="#8b5cf6", fixed_range_y=(0, 100)),
            "disk": StatCard("disk", "Disk", "Throughput", accent_color="#10b981", fixed_range_y=None),
            "network": StatCard("network", "Network", "Throughput", accent_color="#f59e0b", fixed_range_y=None),
        }

        for card in self.cards.values():
            card.card_clicked.connect(self._on_card_clicked)
            sidebar_layout.addWidget(card)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar_frame)

        # ----------------- Right Content Area -----------------
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        main_layout.addWidget(self.stack, 1)

        # Page 0: CPU
        self.cpu_page = self._build_cpu_page()
        self.stack.addWidget(self.cpu_page)

        # Page 1: Memory
        self.mem_page = self._build_memory_page()
        self.stack.addWidget(self.mem_page)

        # Page 2: Disk
        self.disk_page = self._build_disk_page()
        self.stack.addWidget(self.disk_page)

        # Page 3: Network
        self.net_page = self._build_network_page()
        self.stack.addWidget(self.net_page)

        # Initial selection
        self.cards["cpu"].set_active(True)
        self.current_page_id = "cpu"

    # ----------------- Page Builders -----------------

    def _build_cpu_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Header: Model & Current overall load
        header = QHBoxLayout()
        self.cpu_title_lbl = TitleLabel("CPU")
        self.cpu_title_lbl.setStyleSheet("font-size: 22px; font-weight: 700; color: #f4f4f5;")
        header.addWidget(self.cpu_title_lbl)

        self.cpu_model_lbl = CaptionLabel("Detecting CPU...")
        self.cpu_model_lbl.setStyleSheet("font-size: 13px; color: #a1a1aa;")
        self.cpu_model_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(self.cpu_model_lbl)
        layout.addLayout(header)

        # Graph
        self.cpu_graph = LiveGraphWidget(
            title="% Utilization (Last 60 Seconds)",
            fixed_range_y=(0, 100),
            line_color="#0078d4",
            fill_color="#0078d425",
        )
        layout.addWidget(self.cpu_graph, 1)

        # Spec Grid inside Fluent CardWidget
        grid_card = CardWidget()
        grid = QGridLayout(grid_card)
        grid.setContentsMargins(16, 12, 16, 12)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(10)

        self.cpu_util_val = _add_info_item(grid, 0, 0, "Utilization")
        self.cpu_speed_val = _add_info_item(grid, 0, 1, "Speed")
        self.cpu_processes_val = _add_info_item(grid, 0, 2, "Processes")
        self.cpu_threads_val = _add_info_item(grid, 1, 0, "Threads")
        self.cpu_uptime_val = _add_info_item(grid, 1, 1, "Up time")
        self.cpu_cores_val = _add_info_item(grid, 1, 2, "Cores / Threads")

        layout.addWidget(grid_card)
        return page

    def _build_memory_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        header = QHBoxLayout()
        self.mem_title_lbl = TitleLabel("Memory")
        self.mem_title_lbl.setStyleSheet("font-size: 22px; font-weight: 700; color: #f4f4f5;")
        header.addWidget(self.mem_title_lbl)

        self.mem_capacity_lbl = CaptionLabel("-- / -- GB")
        self.mem_capacity_lbl.setStyleSheet("font-size: 13px; color: #a1a1aa;")
        self.mem_capacity_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(self.mem_capacity_lbl)
        layout.addLayout(header)

        self.mem_graph = LiveGraphWidget(
            title="Memory Usage (Last 60 Seconds)",
            fixed_range_y=(0, 100),
            line_color="#8b5cf6",
            fill_color="#8b5cf625",
        )
        layout.addWidget(self.mem_graph, 1)

        grid_card = CardWidget()
        grid = QGridLayout(grid_card)
        grid.setContentsMargins(16, 12, 16, 12)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(10)

        self.mem_in_use_val = _add_info_item(grid, 0, 0, "In use")
        self.mem_available_val = _add_info_item(grid, 0, 1, "Available")
        self.mem_cached_val = _add_info_item(grid, 0, 2, "Cached")
        self.mem_buffers_val = _add_info_item(grid, 1, 0, "Buffers")
        self.mem_swap_val = _add_info_item(grid, 1, 1, "Swap in use")
        self.mem_total_val = _add_info_item(grid, 1, 2, "Total RAM")

        layout.addWidget(grid_card)
        return page

    def _build_disk_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title_lbl = TitleLabel("Disk I/O")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: 700; color: #f4f4f5;")
        header.addWidget(title_lbl)
        layout.addLayout(header)

        self.disk_graph = MultiLineGraphWidget(
            title="Disk Throughput (Last 60 Seconds)",
            labels=["Read Speed", "Write Speed"],
            colors=["#0078d4", "#10b981"],
        )
        layout.addWidget(self.disk_graph, 1)

        grid_card = CardWidget()
        grid = QGridLayout(grid_card)
        grid.setContentsMargins(16, 12, 16, 12)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(10)

        self.disk_read_val = _add_info_item(grid, 0, 0, "Read Speed")
        self.disk_write_val = _add_info_item(grid, 0, 1, "Write Speed")
        self.disk_part_summary = _add_info_item(grid, 0, 2, "Primary Partition (/)")

        layout.addWidget(grid_card)
        return page

    def _build_network_page(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        header = QHBoxLayout()
        title_lbl = TitleLabel("Network")
        title_lbl.setStyleSheet("font-size: 22px; font-weight: 700; color: #f4f4f5;")
        header.addWidget(title_lbl)
        layout.addLayout(header)

        self.net_graph = MultiLineGraphWidget(
            title="Network Throughput (Last 60 Seconds)",
            labels=["Send (Upload)", "Receive (Download)"],
            colors=["#f59e0b", "#10b981"],
        )
        layout.addWidget(self.net_graph, 1)

        grid_card = CardWidget()
        grid = QGridLayout(grid_card)
        grid.setContentsMargins(16, 12, 16, 12)
        grid.setHorizontalSpacing(24)
        grid.setVerticalSpacing(10)

        self.net_send_val = _add_info_item(grid, 0, 0, "Send Speed")
        self.net_recv_val = _add_info_item(grid, 0, 1, "Receive Speed")

        layout.addWidget(grid_card)
        return page

    # ----------------- Interaction & Updates -----------------

    def _on_card_clicked(self, card_id: str):
        self.current_page_id = card_id
        for cid, card in self.cards.items():
            card.set_active(cid == card_id)

        index_map = {"cpu": 0, "memory": 1, "disk": 2, "network": 3}
        self.stack.setCurrentIndex(index_map.get(card_id, 0))

    def update_snapshot(self, snapshot: SystemSnapshot):
        """Called whenever the background MetricsCollector emits a new snapshot."""
        # 1. Update Cards with live mini sparkline graphs
        cpu = snapshot.cpu
        self.cards["cpu"].update_data(
            val_text=f"{format_percent(cpu.overall_percent)} {format_freq(cpu.current_freq_mhz)}",
            graph_val=cpu.overall_percent,
        )

        mem = snapshot.memory
        mem_used_gb = format_bytes(mem.used)
        mem_total_gb = format_bytes(mem.total)
        self.cards["memory"].update_data(
            val_text=f"{mem_used_gb} ({format_percent(mem.percent, 0)})",
            graph_val=mem.percent,
            subtitle=f"{mem_total_gb} Total",
        )

        disk = snapshot.disk
        total_disk_speed = disk.read_bytes_sec + disk.write_bytes_sec
        total_disk_kb = total_disk_speed / 1024.0
        self.cards["disk"].update_data(
            val_text=format_speed(total_disk_speed),
            graph_val=total_disk_kb,
            subtitle="I/O",
        )

        net = snapshot.network
        total_net_speed = net.bytes_sent_sec + net.bytes_recv_sec
        total_net_kb = total_net_speed / 1024.0
        self.cards["network"].update_data(
            val_text=format_speed(total_net_speed),
            graph_val=total_net_kb,
            subtitle="Throughput",
        )

        # 2. Update Graphs
        self.cpu_graph.push_value(cpu.overall_percent)
        self.mem_graph.push_value(mem.percent)
        self.disk_graph.push_values([
            disk.read_bytes_sec / 1024.0,
            disk.write_bytes_sec / 1024.0,
        ])
        self.net_graph.push_values([
            net.bytes_sent_sec / 1024.0,
            net.bytes_recv_sec / 1024.0,
        ])

        # 3. Update Detailed Texts
        self.cpu_model_lbl.setText(cpu.cpu_model_name)
        self.cpu_util_val.setText(format_percent(cpu.overall_percent))
        self.cpu_speed_val.setText(format_freq(cpu.current_freq_mhz))
        self.cpu_processes_val.setText(str(cpu.process_count))
        self.cpu_threads_val.setText(str(cpu.thread_count))
        self.cpu_uptime_val.setText(format_uptime(cpu.uptime_seconds))
        self.cpu_cores_val.setText(f"{cpu.total_physical_cores} Cores / {cpu.total_logical_cores} Threads")

        self.mem_capacity_lbl.setText(f"{mem_used_gb} / {mem_total_gb}")
        self.mem_in_use_val.setText(f"{mem_used_gb} ({format_percent(mem.percent)})")
        self.mem_available_val.setText(format_bytes(mem.available))
        self.mem_cached_val.setText(format_bytes(mem.cached))
        self.mem_buffers_val.setText(format_bytes(mem.buffers))
        self.mem_swap_val.setText(f"{format_bytes(mem.swap_used)} / {format_bytes(mem.swap_total)}")
        self.mem_total_val.setText(mem_total_gb)

        self.disk_read_val.setText(format_speed(disk.read_bytes_sec))
        self.disk_write_val.setText(format_speed(disk.write_bytes_sec))
        if disk.partitions:
            root_p = next((p for p in disk.partitions if p.mountpoint == "/"), disk.partitions[0])
            self.disk_part_summary.setText(f"{format_bytes(root_p.used)} / {format_bytes(root_p.total)} ({root_p.percent}%)")

        self.net_send_val.setText(format_speed(net.bytes_sent_sec))
        self.net_recv_val.setText(format_speed(net.bytes_recv_sec))
