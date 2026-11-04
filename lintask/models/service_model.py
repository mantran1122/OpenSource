"""Table Model and Filter Proxy for systemd Services."""
from typing import List, Optional
from PyQt6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
    QSortFilterProxyModel,
)
from PyQt6.QtGui import QColor

from .service_item import ServiceItem


class ServiceTableModel(QAbstractTableModel):
    """QAbstractTableModel for rendering systemd services with color-coded statuses."""

    COLUMNS = [
        "Service Name",
        "Status",
        "Sub State",
        "Load State",
        "Description",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._services: List[ServiceItem] = []

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._services)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.COLUMNS)

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.COLUMNS[section]
        return None

    def get_service_at(self, row: int) -> Optional[ServiceItem]:
        if 0 <= row < len(self._services):
            return self._services[row]
        return None

    def update_services(self, services: List[ServiceItem]):
        """Replace service list with updated scan."""
        self.beginResetModel()
        self._services = services
        self.endResetModel()

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < len(self._services)):
            return None

        service = self._services[index.row()]
        col = index.column()

        # 1. Text display
        if role == Qt.ItemDataRole.DisplayRole:
            if col == 0:
                return service.name
            elif col == 1:
                return service.active_state.capitalize()
            elif col == 2:
                return service.sub_state
            elif col == 3:
                return service.load_state
            elif col == 4:
                return service.description

        # 2. Raw value for sorting
        elif role == Qt.ItemDataRole.UserRole:
            if col == 0:
                return service.name.lower()
            elif col == 1:
                return service.active_state.lower()
            elif col == 2:
                return service.sub_state.lower()
            elif col == 3:
                return service.load_state.lower()
            elif col == 4:
                return service.description.lower()

        # 3. Status Color Tinting
        elif role == Qt.ItemDataRole.BackgroundRole:
            if col == 1:
                if service.is_running:
                    return QColor(16, 185, 129, 40)  # Subtle emerald green
                elif service.is_failed:
                    return QColor(239, 68, 68, 50)   # Subtle red
                else:
                    return QColor(113, 113, 122, 20) # Subtle gray

        # 4. Alignment
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if col in [1, 2, 3]:
                return Qt.AlignmentFlag.AlignCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        return None


class ServiceFilterProxyModel(QSortFilterProxyModel):
    """Filter and sort proxy for systemd services."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSortRole(Qt.ItemDataRole.UserRole)
        self.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._filter_query = ""
        self._status_filter = "all"  # "all", "active", "inactive", "failed"

    def set_filter_query(self, query: str):
        self._filter_query = query.strip().lower()
        self.invalidateFilter()

    def set_status_filter(self, status: str):
        self._status_filter = status.lower()
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        model = self.sourceModel()
        name_idx = model.index(source_row, 0, source_parent)
        status_idx = model.index(source_row, 1, source_parent)
        desc_idx = model.index(source_row, 4, source_parent)

        name = str(model.data(name_idx, Qt.ItemDataRole.DisplayRole) or "").lower()
        status = str(model.data(status_idx, Qt.ItemDataRole.DisplayRole) or "").lower()
        desc = str(model.data(desc_idx, Qt.ItemDataRole.DisplayRole) or "").lower()

        # Check status filter
        if self._status_filter != "all" and status != self._status_filter:
            return False

        # Check search query
        if self._filter_query:
            if self._filter_query not in name and self._filter_query not in desc:
                return False

        return True

