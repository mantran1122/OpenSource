"""High-performance real-time graph widget matching Fluent Design dark theme."""
from collections import deque
from typing import List, Optional

import pyqtgraph as pg
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import CaptionLabel

# Configure pyqtgraph global settings
pg.setConfigOption("antialias", True)
pg.setConfigOption("background", "#202023")
pg.setConfigOption("foreground", "#71717a")


class MiniSparklineWidget(QWidget):
    """Ultra-lightweight mini sparkline graph without axes for sidebar cards."""

    def __init__(
        self,
        max_points: int = 40,
        fixed_range_y: Optional[tuple] = (0, 100),
        line_color: str = "#0078d4",
        fill_color: Optional[str] = "#0078d425",
        parent=None,
    ):
        super().__init__(parent)
        self.max_points = max_points
        self.fixed_range_y = fixed_range_y
        self.data_buffer = deque([0.0] * max_points, maxlen=max_points)
        self.x_axis_values = list(range(-max_points + 1, 1))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.hideButtons()
        self.plot_widget.getAxis("left").hide()
        self.plot_widget.getAxis("bottom").hide()
        self.plot_widget.showGrid(x=False, y=False)
        self.plot_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.plot_widget.setStyleSheet("background: transparent; border: none;")

        if fixed_range_y:
            self.plot_widget.setYRange(fixed_range_y[0], fixed_range_y[1], padding=0)

        pen = pg.mkPen(color=line_color, width=1.5)
        brush = pg.mkBrush(fill_color) if fill_color else None

        self.curve = self.plot_widget.plot(
            self.x_axis_values,
            list(self.data_buffer),
            pen=pen,
            fillLevel=0,
            fillBrush=brush,
        )

        layout.addWidget(self.plot_widget)

    def push_value(self, value: float):
        self.data_buffer.append(value)
        self.curve.setData(self.x_axis_values, list(self.data_buffer))

        if not self.fixed_range_y:
            max_val = max(self.data_buffer)
            target_max = max(1.0, max_val * 1.25)
            self.plot_widget.setYRange(0, target_max, padding=0.05)


class LiveGraphWidget(QWidget):
    """Real-time scrolling line graph maintaining the last 60 data points."""

    def __init__(
        self,
        title: str = "",
        max_points: int = 60,
        fixed_range_y: Optional[tuple] = (0, 100),
        line_color: str = "#0078d4",  # Windows 11 Fluent Blue
        fill_color: Optional[str] = "#0078d420",
        y_unit: str = "%",
        parent=None,
    ):
        super().__init__(parent)
        self.max_points = max_points
        self.fixed_range_y = fixed_range_y
        self.y_unit = y_unit

        self.data_buffer = deque([0.0] * max_points, maxlen=max_points)
        self.x_axis_values = list(range(-max_points + 1, 1))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        if title:
            self.header_label = CaptionLabel(title)
            self.header_label.setStyleSheet("color: #a1a1aa; font-weight: 600; font-size: 12px;")
            layout.addWidget(self.header_label)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(x=True, y=True, alpha=0.1)
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.hideButtons()
        self.plot_widget.setStyleSheet("border: 1px solid #27272a; border-radius: 6px;")

        axis_bottom = self.plot_widget.getAxis("bottom")
        axis_bottom.setStyle(showValues=False)
        axis_left = self.plot_widget.getAxis("left")
        axis_left.setWidth(40)

        if fixed_range_y:
            self.plot_widget.setYRange(fixed_range_y[0], fixed_range_y[1], padding=0)

        pen = pg.mkPen(color=line_color, width=2)
        brush = pg.mkBrush(fill_color) if fill_color else None

        self.curve = self.plot_widget.plot(
            self.x_axis_values,
            list(self.data_buffer),
            pen=pen,
            fillLevel=0,
            fillBrush=brush,
        )

        layout.addWidget(self.plot_widget)

    def push_value(self, value: float):
        """Append a new data point and refresh graph curve."""
        self.data_buffer.append(value)
        self.curve.setData(self.x_axis_values, list(self.data_buffer))

        if not self.fixed_range_y:
            max_val = max(self.data_buffer)
            target_max = max(10.0, max_val * 1.25)
            self.plot_widget.setYRange(0, target_max, padding=0.05)


class MultiLineGraphWidget(QWidget):
    """Real-time graph widget supporting multiple colored lines."""

    def __init__(
        self,
        title: str = "",
        max_points: int = 60,
        labels: List[str] = None,
        colors: List[str] = None,
        parent=None,
    ):
        super().__init__(parent)
        self.max_points = max_points
        self.labels = labels or ["Line 1", "Line 2"]
        self.colors = colors or ["#0078d4", "#10b981"]

        self.buffers = [deque([0.0] * max_points, maxlen=max_points) for _ in self.labels]
        self.x_axis_values = list(range(-max_points + 1, 1))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        if title:
            self.header_label = CaptionLabel(title)
            self.header_label.setStyleSheet("color: #a1a1aa; font-weight: 600; font-size: 12px;")
            layout.addWidget(self.header_label)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(x=True, y=True, alpha=0.1)
        self.plot_widget.setMouseEnabled(x=False, y=False)
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.hideButtons()
        self.plot_widget.setStyleSheet("border: 1px solid #27272a; border-radius: 6px;")
        self.plot_widget.addLegend(offset=(10, 10))

        self.curves = []
        for i, (label, color) in enumerate(zip(self.labels, self.colors)):
            pen = pg.mkPen(color=color, width=2)
            curve = self.plot_widget.plot(
                self.x_axis_values,
                list(self.buffers[i]),
                pen=pen,
                name=label,
            )
            self.curves.append(curve)

        layout.addWidget(self.plot_widget)

    def push_values(self, values: List[float]):
        """Push values for each line."""
        all_max = 1.0
        for i, val in enumerate(values):
            if i < len(self.buffers):
                self.buffers[i].append(val)
                self.curves[i].setData(self.x_axis_values, list(self.buffers[i]))
                all_max = max(all_max, max(self.buffers[i]))

        self.plot_widget.setYRange(0, all_max * 1.25, padding=0.05)
