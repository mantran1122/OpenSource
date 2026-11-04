"""High-performance Table Model with Windows 11 Heatmap styling and numeric sorting."""
from typing import List, Optional
from PyQt6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
    QSortFilterProxyModel,
)
from PyQt6.QtGui import QColor

from .process_info import ProcessInfo
from ..utils.formatters import format_bytes, format_speed


class ProcessTableModel(QAbstractTableModel):
    """QAbstractTableModel for rendering processes with real-time updates and heatmap tints."""

    COLUMNS = [
        "Name",
        "PID",
        "Status",
        "CPU %",
        "Memory",
        "Disk I/O",
        "User",
        "Threads",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._processes: List[ProcessInfo] = []

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._processes)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.COLUMNS)

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.COLUMNS[section]
        return None

    def get_process_at(self, row: int) -> Optional[ProcessInfo]:
        if 0 <= row < len(self._processes):
            return self._processes[row]
        return None

    def update_processes(self, processes: List[ProcessInfo]):
        """Replace process dataset with fresh scan."""
        self.beginResetModel()
        self._processes = processes
        self.endResetModel()

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._processes)):
            return None

        proc = self._processes[index.row()]
        col = index.column()

        # 1. Text Display
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return proc.name
            elif col == 1:
                return str(proc.pid)
            elif col == 2:
                return proc.status.capitalize()
            elif col == 3:
                return f"{proc.cpu_percent:.1f}%"
            elif col == 4:
                return format_bytes(proc.memory_bytes)
            elif col == 5:
                total_io = proc.disk_read_bytes_sec + proc.disk_write_bytes_sec
                return format_speed(total_io) if total_io > 0 else "0 B/s"
            elif col == 6:
                return proc.user
            elif col == 7:
                return str(proc.num_threads)

        # 2. Raw Value for Precise Sorting (UserRole)
        elif role == Qt.ItemDataRole.UserRole:
            if col == 0:
                return proc.name.lower()
            elif col == 1:
                return proc.pid
            elif col == 2:
                return proc.status
            elif col == 3:
                return proc.cpu_percent
            elif col == 4:
                return proc.memory_bytes
            elif col == 5:
                return proc.disk_read_bytes_sec + proc.disk_write_bytes_sec
            elif col == 6:
                return proc.user.lower()
            elif col == 7:
                return proc.num_threads

        # 3. Windows 11 Style Heatmap Background Tinting
        elif role == Qt.ItemDataRole.BackgroundRole:
            # CPU Heatmap Tint
            if col == 3:
                if proc.cpu_percent >= 50.0:
                    return QColor(239, 68, 68, 55)  # Soft red
                elif proc.cpu_percent >= 20.0:
                    return QColor(245, 158, 11, 50)  # Soft amber
                elif proc.cpu_percent >= 5.0:
                    return QColor(0, 120, 212, 40)   # Soft blue
            # Memory Heatmap Tint
            elif col == 4:
                # > 1.5 GB
                if proc.memory_bytes >= 1.5 * 1024 * 1024 * 1024:
                    return QColor(139, 92, 246, 50)  # Soft purple
                elif proc.memory_bytes >= 500 * 1024 * 1024:
                    return QColor(139, 92, 246, 25)

        # 4. Text Alignment
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if col in [3, 4, 5, 7]:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            elif col == 1:
                return Qt.AlignmentFlag.AlignCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        return None


class ProcessFilterProxyModel(QSortFilterProxyModel):
    """Sort and filter proxy model supporting search queries and numeric sorting."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSortRole(Qt.ItemDataRole.UserRole)  # Sort by raw numbers!
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._filter_query = ""

    def set_filter_query(self, query: str):
        self._filter_query = query.strip().lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if not self._filter_query:
            return True

        model = self.sourceModel()
        name_idx = model.index(source_row, 0, source_parent)
        pid_idx = model.index(source_row, 1, source_parent)
        user_idx = model.index(source_row, 6, source_parent)

        name = str(model.data(name_idx, Qt.ItemDataRole.DisplayRole) or "").lower()
        pid = str(model.data(pid_idx, Qt.ItemDataRole.DisplayRole) or "")
        user = str(model.data(user_idx, Qt.ItemDataRole.DisplayRole) or "").lower()

        return (
            self._filter_query in name
            or self._filter_query in pid
            or self._filter_query in user
        )

