import json
import time
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath

from src.ui.theme import THEME


class LiveTrafficWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.data = [0] * 50
        self.y_axis_max = 50
        self.network_status = "Disconnected"
        self.is_scanning = False
        self.scan_timer = 0
        self.previous_packets = []
        self.elapsed_time = 0  # Track elapsed time for dynamic axis
        self.setMinimumSize(300, 200)
        self.setMouseTracking(True)
        
        # Set up timer for updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(300)  # 0.3s for smoother visualization
        self.network_status = "Disconnected" #Add network status tracking

    def update_data(self):
        # Update elapsed time for dynamic axis
        self.elapsed_time += 0.3  # 300ms = 0.3 seconds per update
        
        current_packets = 0
        packets = []
        try:
            with open('packet_data.json', 'r') as f:
                packet_data = json.load(f)
            current_packets = packet_data.get('packet_count', 0)
            packets = packet_data.get('packets', [])[-500:]
            
            # Update network status based on sniffer status - with improved logic
            status = packet_data.get('status', 'stopped')
            
            # More robust status detection
            if status == 'running':
                # Check if we have actual packet flow in recent time window
                recent_time = packets[-1].get('timestamp', 0) if packets else 0
                current_time = recent_time
                # Check if we have recent packets (within last 8 seconds)
                recent_packets = [p for p in packets if current_time - p.get('timestamp', 0) < 8]
                
                if recent_packets:
                    self.network_status = "Connected"
                    self.is_scanning = False
                    self.scan_timer = 0
                else:
                    # No recent packets - check if we should show disconnected
                    if not self.is_scanning:
                        self.scan_timer += 1
                        if self.scan_timer > 6:  # 6 seconds without packets (3 seconds * 2)
                            self.network_status = "Disconnected"
                            self.is_scanning = True
            elif status == 'stopped':
                if self.network_status != "Disconnected":
                    self.network_status = "Disconnected"
                self.scan_timer = 0
                
            self.previous_packets = current_packets
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            # Only disconnect on actual file errors, not temporary issues
            if self.network_status != "Disconnected":
                self.network_status = "Disconnected"
            self.scan_timer = 0
            # Error logged silently
        except Exception as e:
            # Unexpected error caught silently
            self.scan_timer = 0
            
        # Calculate actual packets per second from recent packets
        if len(packets) > 0:
            # Count packets in the last second
            current_time = packets[-1].get('timestamp', 0)
            recent_packets = [p for p in packets if current_time - p.get('timestamp', 0) <= 1.0]
            pps = len(recent_packets)
        else:
            pps = 0
            
        self.data.append(pps)
        
        # Remove old data instead of compressing - keep only last 15 points
        if len(self.data) > 15:
            self.data = self.data[-15:]
            
        max_pps = max(self.data) if self.data else 0
        
        # Improved auto-adjustment logic
        if max_pps > 0.9 * self.y_axis_max:
            # Scale up quickly when approaching limit
            self.y_axis_max = max_pps * 1.5
        elif max_pps < 0.1 * self.y_axis_max and self.y_axis_max > 5:
            # Scale down when much lower than current max
            self.y_axis_max = max(max_pps * 2, 5)
        elif max_pps < 0.3 * self.y_axis_max and self.y_axis_max > 10:
            # Gentle scale down for moderate underutilization
            self.y_axis_max = max(max_pps * 1.5, 10)
            
        # Ensure reasonable bounds
        self.y_axis_max = max(min(self.y_axis_max, 1000), 5)
        
        self.update()  # Force redraw

    def set_network_status(self, status):
        """Update network connection status."""
        self.network_status = status
        self.update() 

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

        status_color = QColor(76, 175, 80) if self.network_status == "Connected" else QColor(255, 107, 107)
        painter.setPen(QPen(status_color))
        painter.setFont(QFont(THEME['font_mono'].strip('"'), 10))
        status_text = f"Status: {self.network_status}"
        painter.drawText(int(chart_rect.left() + 100), int(chart_rect.top()), status_text)
        
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
        
        # X-Labels with dynamic time calculation
        painter.setPen(QPen(QColor(THEME['text_secondary'])))
        painter.setFont(QFont(THEME['font_mono'].strip("'"), 9))
        
        # Calculate current time for dynamic labels
        import time
        current_time = time.time()
        
        # No time labels - clean graph without axis labels

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
