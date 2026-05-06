import json
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath

from src.ui.theme import THEME


class LiveTrafficWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 200)
        self.data = [0] * 30
        self.previous_packets = 0
        self.y_axis_max = 1000
        self.is_scanning = False
        self.scan_timer = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        # self.timer.start(1000)  # 1s  # Disabled for performance

    def update_data(self):
        current_packets = 0
        packets = []
        try:
            with open('packet_data.json', 'r') as f:
                packet_data = json.load(f)
            current_packets = packet_data.get('packet_count', 0)
            packets = packet_data.get('packets', [])[-500:]
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        pps = max(0, current_packets - self.previous_packets)
        self.previous_packets = current_packets
        self.data.append(pps)
        max_pps = max(self.data)
        if max_pps > 0.8 * self.y_axis_max:
            self.y_axis_max *= 2
        elif max_pps < 0.2 * self.y_axis_max and self.y_axis_max > 1000:
            self.y_axis_max //= 2
        self.update()  # Force redraw

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        
        # Define chart area with margins for axes
        chart_left = rect.left() + 50
        chart_top = rect.top() + 20
        chart_right = rect.right() - 20
        chart_bottom = rect.bottom() - 50
        chart_rect = QRectF(chart_left, chart_top, chart_right - chart_left, chart_bottom - chart_top)
        width = chart_rect.width()
        height = chart_rect.height()
        
        # Y-Axis
        painter.setPen(QPen(QColor(100, 100, 100)))
        painter.drawLine(int(chart_rect.left()), int(chart_rect.top()), int(chart_rect.left()), int(chart_rect.bottom()))
        
        # Y-Labels
        mono_font = QFont("Monospace", 8)
        painter.setFont(mono_font)
        painter.setPen(QPen(Qt.GlobalColor.white))
        # Max at top
        painter.drawText(int(chart_rect.left() - 30), int(chart_rect.top() + 5), str(self.y_axis_max))
        painter.drawText(int(chart_rect.left() + 10), int(chart_rect.top() + 5), "Pkts/s")
        # Half at middle
        painter.drawText(int(chart_rect.left() - 30), int(chart_rect.center().y() + 3), str(self.y_axis_max // 2))
        # 0 at bottom
        painter.drawText(int(chart_rect.left() - 30), int(chart_rect.bottom() + 3), "0")
        
        # X-Axis
        painter.setPen(QPen(QColor(100, 100, 100)))
        painter.drawLine(int(chart_rect.left()), int(chart_rect.bottom()), int(chart_rect.right()), int(chart_rect.bottom()))
        
        # X-Labels
        painter.setPen(QPen(QColor(THEME['text_secondary'])))
        painter.setFont(QFont(THEME['font_mono'].strip("'"), 9))
        # -15s at left
        painter.drawText(int(chart_rect.left() - 10), int(chart_rect.bottom() + 20), "-15 s")
        # -7.5s at center
        painter.drawText(int(chart_rect.center().x() - 15), int(chart_rect.bottom() + 20), "-7.5 s")
        # NOW at right
        painter.drawText(int(chart_rect.right() - 25), int(chart_rect.bottom() + 20), "Now")

        # Draw the path with Bézier - using teal colors from mockup
        stroke_color = THEME['primary']
        path = QPainterPath()
        path.moveTo(chart_rect.left(), chart_rect.bottom())
        num_points = len(self.data)
        for i in range(num_points):
            x = chart_rect.left() + i * (width / (num_points - 1)) if num_points > 1 else chart_rect.left()
            y = chart_rect.bottom() - (self.data[i] / self.y_axis_max) * height
            if i == 0:
                path.lineTo(x, y)
            else:
                prev_x = chart_rect.left() + (i-1) * (width / (num_points - 1))
                prev_y = chart_rect.bottom() - (self.data[i-1] / self.y_axis_max) * height
                cx = (prev_x + x) / 2
                cy = (prev_y + y) / 2
                path.quadTo(cx, cy, x, y)
        path.lineTo(chart_rect.right(), chart_rect.bottom())
        path.closeSubpath()

        # Gradient fill
        gradient = QLinearGradient(0, chart_rect.top(), 0, chart_rect.bottom())
        gradient.setColorAt(0, QColor(0, 242, 254, 77))
        gradient.setColorAt(1, QColor(0, 242, 254, 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)

        # Draw the line
        painter.setPen(QPen(QColor(stroke_color), 1.5))
        for i in range(1, num_points):
            x1 = chart_rect.left() + (i-1) * (width / (num_points - 1))
            y1 = chart_rect.bottom() - (self.data[i-1] / self.y_axis_max) * height
            x2 = chart_rect.left() + i * (width / (num_points - 1))
            y2 = chart_rect.bottom() - (self.data[i] / self.y_axis_max) * height
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
