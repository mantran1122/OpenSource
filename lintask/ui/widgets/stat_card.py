"""Sidebar summary card widget with integrated live mini sparkline graph."""
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from qfluentwidgets import (
    CardWidget,
    SubtitleLabel,
    BodyLabel,
    CaptionLabel,
)

from .live_graph import MiniSparklineWidget


class StatCard(CardWidget):
    """Clickable modern Fluent card displaying metric overview with live mini sparkline graph."""

    card_clicked = pyqtSignal(str)

    def __init__(
        self,
        card_id: str,
        title: str,
        subtitle: str = "",
        accent_color: str = "#0078d4",
        fixed_range_y: Optional[tuple] = (0, 100),
        parent=None,
    ):
        super().__init__(parent)
        self.card_id = card_id
        self.accent_color = accent_color
        self._is_active = False

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(102)

        # Connect CardWidget's native clicked signal to emit card_id
        self.clicked.connect(lambda: self.card_clicked.emit(self.card_id))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 8)
        layout.setSpacing(3)

        # Header: Title + Subtitle
        header_layout = QHBoxLayout()
        self.title_label = SubtitleLabel(title)
        self.title_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #f4f4f5;")
        header_layout.addWidget(self.title_label)

        self.subtitle_label = CaptionLabel(subtitle)
        self.subtitle_label.setStyleSheet("color: #a1a1aa; font-size: 11px;")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        header_layout.addWidget(self.subtitle_label)

        layout.addLayout(header_layout)

        # Primary value label
        self.val_label = BodyLabel("--")
        self.val_label.setStyleSheet("font-size: 13px; font-weight: 500; color: #e4e4e7;")
        layout.addWidget(self.val_label)

        # Integrated live mini sparkline graph (replaces static progress bar)
        self.sparkline = MiniSparklineWidget(
            max_points=40,
            fixed_range_y=fixed_range_y,
            line_color=accent_color,
            fill_color=accent_color + "25",
            parent=self,
        )
        self.sparkline.setFixedHeight(36)
        layout.addWidget(self.sparkline)

        self._update_style()

    def set_active(self, active: bool):
        """Set whether this card is currently selected."""
        self._is_active = active
        self._update_style()

    def update_data(self, val_text: str, graph_val: float = 0.0, subtitle: str = ""):
        """Update metrics and push point into mini sparkline."""
        self.val_label.setText(val_text)
        self.sparkline.push_value(graph_val)
        if subtitle:
            self.subtitle_label.setText(subtitle)

    def _update_style(self):
        if self._is_active:
            self.setStyleSheet(f"""
                StatCard {{
                    background-color: #2d2d30;
                    border: 1px solid #3f3f46;
                    border-left: 4px solid {self.accent_color};
                    border-radius: 6px;
                }}
            """)
        else:
            self.setStyleSheet("""
                StatCard {
                    background-color: #202023;
                    border: 1px solid #27272a;
                    border-left: 4px solid transparent;
                    border-radius: 6px;
                }
                StatCard:hover {
                    background-color: #27272a;
                    border: 1px solid #3f3f46;
                }
            """)
