import sys
import os
import json
import math

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QListWidget, QTextEdit, QLineEdit, QSplitter, QScrollArea)
from PyQt6.QtCore import QTimer, Qt, QRectF
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPainterPath, QLinearGradient

import joblib
import pandas as pd
import numpy as np

from src.ml.feature_extractor import FeatureExtractor

from src.ai.ollama_client import OllamaClient
from src.ai.prompts import GENERAL_PROMPT, EXPLANATION_PROMPT, TECHNICAL_ANALYSIS_PROMPT
from src.ai.utils import format_packet_log

class ThreatGauge(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.threat_level = 0.0
        self.setMinimumSize(300, 200)

    def setThreatLevel(self, level):
        self.threat_level = max(0.0, min(1.0, level))
        self.update()

    def get_color(self, value):
        return QColor(0, 255, 0)  # Always green

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(20, 20, -20, -20)  # reduced padding
        center = rect.center()
        radius = min(rect.width(), rect.height()) / 2 - 10  # reduced margin

        # Subtle background shadow arc
        shadow_color = QColor(0, 0, 0, 30)
        painter.setPen(QPen(shadow_color, 4))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect.adjusted(2, 2, -2, -2), 0, 180*16)

        # Thin semi-circular track with gradient
        painter.setPen(QPen(Qt.GlobalColor.white, 2))  # base
        painter.drawArc(rect.adjusted(5, 5, -5, -5), 0, 180*16)

        # Gradient segments: from teal to amber to crimson
        teal = QColor(45, 212, 191)  # #2DD4BF
        amber = QColor(255, 191, 0)  # deep amber
        crimson = QColor(220, 20, 60)  # soft crimson
        segments = 18  # every 10 degrees
        for i in range(segments):
            angle_start = i * 10
            if i < 6:
                color = self.interpolate_color(teal, amber, i / 5.0)
            elif i < 12:
                color = self.interpolate_color(amber, crimson, (i - 6) / 5.0)
            else:
                color = crimson
            painter.setPen(QPen(color, 2))
            painter.drawArc(rect.adjusted(5, 5, -5, -5), angle_start*16, 10*16)

        # Tick marks every 10%
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        for i in range(0, 19, 2):  # every 10%
            angle = i * 10
            rad = math.radians(angle)
            inner_x = center.x() + (radius - 5) * math.cos(rad)
            inner_y = center.y() - (radius - 5) * math.sin(rad)
            outer_x = center.x() + (radius + 3) * math.cos(rad)
            outer_y = center.y() - (radius + 3) * math.sin(rad)
            painter.drawLine(int(inner_x), int(inner_y), int(outer_x), int(outer_y))

        # Hollow center point
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, 2, 2)

        # Needle
        angle_rad = self.threat_level * math.pi
        needle_x = center.x() + radius * math.cos(angle_rad - math.pi/2)
        needle_y = center.y() + radius * math.sin(angle_rad - math.pi/2)
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawLine(int(center.x()), int(center.y()), int(needle_x), int(needle_y))

        # Center typography
        painter.setPen(QPen(Qt.GlobalColor.white))
        # "THREAT" above center
        font = QFont("Monospace", 8, QFont.Weight.Thin)
        painter.setFont(font)
        painter.drawText(int(center.x() - 20), int(center.y() - 25), "THREAT")
        # Percentage underneath the gauge
        font.setPointSize(18)
        painter.setFont(font)
        level_text = f"{int(self.threat_level * 100)}%"
        painter.drawText(int(center.x() - 20), int(center.y() + radius + 15), level_text)

    def interpolate_color(self, c1, c2, t):
        r = int(c1.red() + (c2.red() - c1.red()) * t)
        g = int(c1.green() + (c2.green() - c1.green()) * t)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * t)
        return QColor(r, g, b)

class StatusCore(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(200, 200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect()
        # No background fill to avoid square box appearance

        # Circle centered with radius 80
        center = rect.center()
        radius = 80

        # Outer circle: thin 1px solid muted teal
        muted_teal = QColor(30, 41, 59)  # #1E293B
        painter.setPen(QPen(muted_teal, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, radius, radius)

        # Inner circle: thicker dashed primary teal
        primary_teal = QColor(45, 212, 191)  # #2DD4BF
        pen = QPen(primary_teal, 3)
        pen.setDashPattern([4.0, 4.0])
        painter.setPen(pen)
        painter.drawEllipse(center, radius - 20, radius - 20)

        # Core: simple 'S' in center
        painter.setPen(QPen(Qt.GlobalColor.white))
        font = QFont("Arial", 48, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "S")

        # Text: horizontal centered 'SYSTEM SAFE'
        painter.setPen(QPen(Qt.GlobalColor.white))
        font = QFont("Arial", 14)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        painter.setFont(font)
        painter.drawText(QRectF(rect.left(), center.y() + 30, rect.width(), 30), Qt.AlignmentFlag.AlignCenter, "SYSTEM SAFE")

class PacketWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 200)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Define margins for labels
        left_margin = 60
        top_margin = 40
        right_margin = 20
        bottom_margin = 60
        chart_rect = self.rect().adjusted(left_margin, top_margin, -right_margin, -bottom_margin)
        width = chart_rect.width()
        height = chart_rect.height()

        # Legend in top-left (removed as per request)

        # Y-axis
        painter.setPen(QPen(Qt.GlobalColor.white, 1))
        painter.drawLine(chart_rect.left(), chart_rect.top(), chart_rect.left(), chart_rect.bottom())
        # Y-label
        painter.save()
        painter.translate(chart_rect.left() - 40, chart_rect.center().y())
        painter.rotate(-90)
        painter.drawText(0, 0, "Pkts/sec")
        painter.restore()
        # Y-markers
        font = QFont("Arial", 8)
        painter.setFont(font)
        for val in [0, 20, 40, 60]:
            y = chart_rect.bottom() - (val / 60) * height
            painter.drawLine(chart_rect.left() - 5, int(y), chart_rect.left(), int(y))
            painter.drawText(chart_rect.left() - 25, int(y) + 4, str(val))

        # X-axis
        painter.drawLine(chart_rect.left(), chart_rect.bottom(), chart_rect.right(), chart_rect.bottom())
        # X-label
        painter.drawText(chart_rect.center().x() - 50, chart_rect.bottom() + 35, "Timeline (Last 15 min)")
        # X-markers
        time_labels = ["-15m", "-10m", "-5m", "Now"]
        num_labels = len(time_labels)
        for i, label in enumerate(time_labels):
            x = chart_rect.left() + i * (width / (num_labels - 1))
            painter.drawLine(int(x), chart_rect.bottom(), int(x), chart_rect.bottom() + 5)
            painter.drawText(int(x) - 10, chart_rect.bottom() + 15, label)

        # Ultra-thin horizontal grid lines aligned with Y-markers
        painter.setPen(QPen(QColor(100, 100, 100, 25)))
        for val in [0, 20, 40, 60]:
            y = chart_rect.bottom() - (val / 60) * height
            painter.drawLine(chart_rect.left(), int(y), chart_rect.right(), int(y))

        # Average baseline (if needed, but now grid covers)
        avg_y = chart_rect.top() + height / 2
        painter.setPen(QPen(QColor(150, 150, 150, 50), 1))
        painter.drawLine(chart_rect.left(), int(avg_y), chart_rect.right(), int(avg_y))

        # Sample data
        data_points = [100, 150, 200, 250, 300, 350, 300, 250, 200, 150, 100, 80, 60, 40, 20]
        num_points = len(data_points)
        step_x = width / (num_points - 1)

        # Create smooth path
        path = QPainterPath()
        path.moveTo(chart_rect.left(), chart_rect.bottom())
        for i, val in enumerate(data_points):
            x = chart_rect.left() + i * step_x
            y = chart_rect.bottom() - (val / 400) * height
            path.lineTo(x, y)
        path.lineTo(chart_rect.right(), chart_rect.bottom())
        path.closeSubpath()

        # Vertical gradient fill
        gradient = QLinearGradient(0, chart_rect.top(), 0, chart_rect.bottom())
        gradient.setColorAt(0, QColor(0, 242, 254, 77))
        gradient.setColorAt(1, QColor(0, 242, 254, 0))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(path)

        # Glowing line
        painter.setPen(QPen(QColor(0, 242, 254, 100), 4))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for i in range(1, num_points):
            x1 = chart_rect.left() + (i-1) * step_x
            y1 = chart_rect.bottom() - (data_points[i-1] / 400) * height
            x2 = chart_rect.left() + i * step_x
            y2 = chart_rect.bottom() - (data_points[i] / 400) * height
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Main line
        painter.setPen(QPen(QColor(0, 242, 254), 1.5))
        for i in range(1, num_points):
            x1 = chart_rect.left() + (i-1) * step_x
            y1 = chart_rect.bottom() - (data_points[i-1] / 400) * height
            x2 = chart_rect.left() + i * step_x
            y2 = chart_rect.bottom() - (data_points[i] / 400) * height
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        # Glowing dot at peak
        max_val = max(data_points)
        max_index = data_points.index(max_val)
        peak_x = chart_rect.left() + max_index * step_x
        peak_y = chart_rect.bottom() - (max_val / 400) * height
        glow_color = QColor(0, 242, 254, 150)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow_color))
        painter.drawEllipse(int(peak_x - 3), int(peak_y - 3), 6, 6)
        painter.setBrush(QBrush(QColor(0, 242, 254)))
        painter.drawEllipse(int(peak_x - 2), int(peak_y - 2), 4, 4)
        # Label
        painter.setPen(QPen(QColor(0, 242, 254)))
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(int(peak_x - 15), int(peak_y - 10), "428 p/s")

class WatchdogDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WATCHDOG AI Dashboard")
        self.setGeometry(100, 100, 1200, 1000)

        # Load ML
        try:
            self.model = joblib.load('models/random_forest_model.pkl')
            self.extractor = FeatureExtractor()
        except Exception as e:
            print(f"Failed to load ML model: {e}")
            self.model = None
            self.extractor = None

        self.ai_client = OllamaClient()

        self.status_core = StatusCore()
        self.packet_widget = PacketWidget()
        self.threat_gauge = ThreatGauge()
        self.threat_gauge.setThreatLevel(0.2)

        self.status_card = QWidget()
        self.status_card.setStyleSheet("background-color: #1e293b; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px;")
        status_layout = QVBoxLayout(self.status_card)
        status_layout.setContentsMargins(24, 24, 24, 24)
        status_title = QLabel("SYSTEM STATUS")
        status_title.setStyleSheet("color: gray; font-family: Monospace; font-size: 10px; text-transform: uppercase;")
        status_layout.addWidget(status_title)
        status_layout.addWidget(self.status_core)

        self.packet_card = QWidget()
        self.packet_card.setStyleSheet("background-color: #1e293b; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px;")
        packet_layout = QVBoxLayout(self.packet_card)
        packet_layout.setContentsMargins(24, 24, 24, 24)
        packet_title = QLabel("NETWORK TRAFFIC")
        packet_title.setStyleSheet("color: gray; font-family: Monospace; font-size: 10px; text-transform: uppercase;")
        packet_layout.addWidget(packet_title)
        packet_layout.addWidget(self.packet_widget)

        self.threat_card = QWidget()
        self.threat_card.setStyleSheet("background-color: #1e293b; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px;")
        threat_layout = QVBoxLayout(self.threat_card)
        threat_layout.setContentsMargins(24, 24, 24, 24)
        threat_title = QLabel("RISK ANALYSIS")
        threat_title.setStyleSheet("color: gray; font-family: Monospace; font-size: 10px; text-transform: uppercase;")
        threat_layout.addWidget(threat_title)
        threat_layout.addWidget(self.threat_gauge)

        # Splitter for table and chat
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Src IP", "Dst IP", "Protocol", "Length"])
        self.table.setContentsMargins(0, 24, 0, 24)  # py-6 vertical padding
        self.table.verticalHeader().setDefaultSectionSize(50)  # increase row height for breathing room
        splitter.addWidget(self.table)

        # Right: AI Intelligence Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(400)
        self.sidebar.setStyleSheet("background-color: rgba(15, 23, 42, 0.5); border-left: 1px solid rgba(255, 255, 255, 0.05);")

        # Define widgets first
        header_label = QLabel("FORENSIC ASSISTANT")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setStyleSheet("color: white;")

        sub_label = QLabel("Powered by Ollama/Llama 3")
        sub_label.setFont(QFont("Arial", 10))
        sub_label.setStyleSheet("color: gray;")

        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("border: none; background-color: transparent;")
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_scroll.setWidget(self.chat_widget)

        # Input Field and Send at bottom
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.chat_input)

        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet("background-color: #2DD4BF; color: white; border: none; padding: 8px;")
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)

        sidebar_grid = QGridLayout(self.sidebar)
        sidebar_grid.setContentsMargins(16, 16, 16, 16)

        # Header row 0 (auto)
        sidebar_grid.addWidget(header_label, 0, 0)
        sidebar_grid.addWidget(sub_label, 1, 0)

        # Chat row 2 (1fr)
        sidebar_grid.addWidget(self.chat_scroll, 2, 0)

        # Input row 3 (auto)
        sidebar_grid.addLayout(input_layout, 3, 0)

        # Set row stretch for chat
        sidebar_grid.setRowStretch(2, 1)

        splitter.addWidget(self.sidebar)

        # Set proportions: table ~60%, sidebar 40%
        splitter.setSizes([720, 480])

        # Metrics
        metrics_layout = QHBoxLayout()
        self.status_label = QLabel("Status: SAFE")
        self.packets_label = QLabel("Packets: 0")
        self.status_label.setFont(QFont("Arial", 14))
        self.packets_label.setFont(QFont("Arial", 14))
        metrics_layout.addWidget(self.status_label)
        metrics_layout.addWidget(self.packets_label)

        # Refresh button
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.update_ui)

        # Central widget with grid layout
        central = QWidget()
        self.setCentralWidget(central)
        grid = QGridLayout(central)
        grid.setSpacing(20)

        # Header
        header = QLabel("🛡️ WATCHDOG AI Dashboard")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Header spanning columns
        grid.addWidget(header, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

        # Cards row (50%)
        grid.addWidget(self.status_card, 1, 0)
        grid.addWidget(self.packet_card, 1, 1)
        grid.addWidget(self.threat_card, 1, 2)

        # Metrics
        grid.addLayout(metrics_layout, 2, 0, 1, 3)

        # Refresh button
        grid.addWidget(refresh_btn, 3, 0, 1, 3)

        # Splitter row (50%)
        grid.addWidget(splitter, 4, 0, 1, 3)

        # Set row stretches for 50% each
        grid.setRowStretch(1, 1)
        grid.setRowStretch(4, 1)

        # Timer for auto-update
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_ui)
        self.timer.start(1000)  # 1 seconds

        # Initial update
        self.update_ui()

    def update_ui(self):
        try:
            with open('packet_data.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"packets": []}

        packets = data.get("packets", [])
        if packets:
            # Update metrics
            self.packets_label.setText(f"Packets: {len(packets)}")
            # Update table
            self.table.setRowCount(min(10, len(packets)))
            for i, packet in enumerate(packets[-10:]):
                self.table.setItem(i, 0, QTableWidgetItem(packet.get('src_ip', '')))
                self.table.setItem(i, 1, QTableWidgetItem(packet.get('dst_ip', '')))
                proto = packet.get('protocol', 'Other')
                self.table.setItem(i, 2, QTableWidgetItem(proto))
                self.table.setItem(i, 3, QTableWidgetItem(str(packet.get('length', 0))))
        else:
            self.packets_label.setText("Packets: 0")

    def send_message(self):
        msg = self.chat_input.text().strip()
        if not msg:
            return
        # Add user message bubble
        user_bubble = QLabel(f"You: {msg}")
        user_bubble.setStyleSheet("background-color: #2DD4BF; color: white; padding: 8px; border-radius: 8px; margin: 4px;")
        user_bubble.setWordWrap(True)
        self.chat_layout.addWidget(user_bubble)
        # Show typing animation
        self.typing_label = QLabel("...")
        self.typing_label.setStyleSheet("color: #2DD4BF; font-size: 12px; margin: 4px;")
        self.chat_layout.addWidget(self.typing_label)
        self.chat_input.clear()
        # Scroll to bottom
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())
        # Process response (simulate)
        QTimer.singleShot(1000, lambda: self.process_response(msg))

    def process_response(self, msg):
        # Remove typing
        self.chat_layout.removeWidget(self.typing_label)
        self.typing_label.deleteLater()
        # Add AI response bubble
        response = self.process_command(msg)
        ai_bubble = QLabel(f"AI: {response}")
        ai_bubble.setStyleSheet("background-color: #374151; color: white; padding: 8px; border-radius: 8px; margin: 4px;")
        ai_bubble.setWordWrap(True)
        self.chat_layout.addWidget(ai_bubble)
        # Scroll to bottom
        self.chat_scroll.verticalScrollBar().setValue(self.chat_scroll.verticalScrollBar().maximum())

    def process_command(self, msg):
        msg_lower = msg.lower()
        if "hi" in msg_lower or "hello" in msg_lower:
            return "Hello! I'm the AI assistant for WATCHDOG. Try 'threat level' or 'status'."
        elif "threat" in msg_lower and "level" in msg_lower:
            return "Current threat level: LOW (0.2)"
        elif "status" in msg_lower:
            return "System status: SAFE - All systems operational."
        elif msg_lower.startswith("predict"):
            if not self.model or not self.extractor:
                return "ML model not available."
            try:
                params_str = msg.split(":", 1)[1].strip()
                params = {}
                for pair in params_str.split():
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        params[key.strip()] = value.strip()
                packet_data = {
                    'src_ip': params.get('src_ip', '192.168.1.1'),
                    'dst_ip': params.get('dst_ip', '10.0.0.1'),
                    'protocol': 6 if params.get('protocol', 'tcp').lower() == 'tcp' else 17,
                    'length': int(params.get('length', '100')),
                    'src_port': int(params.get('src_port', '12345')),
                    'dst_port': int(params.get('dst_port', '80')),
                    'flags': params.get('flags', 'S'),
                    'direction': 'inbound'
                }
                features = self.extractor.extract_packet_features(packet_data)
                selected_features = self.extractor.get_selected_features(features)
                features_array = np.array(selected_features).reshape(1, -1)
                prediction = self.model.predict(features_array)[0]
                label_map = {0: 'NORMAL', 1: 'ATTACK'}
                return f"Prediction: {label_map.get(prediction, 'UNKNOWN')}"
            except Exception as e:
                return f"Error: {str(e)}"
        
        elif msg_lower.startswith("explain log:"):
            log_str = msg[12:].strip()
            try:
                packet = json.loads(log_str)
                formatted = format_packet_log(packet)
                return self.ai_client.query(EXPLANATION_PROMPT.format(log=formatted))
            except Exception as e:
                return f"Error processing log: {str(e)}"
        
        elif msg_lower.startswith("analyze log:"):
            log_str = msg[12:].strip()
            try:
                packet = json.loads(log_str)
                formatted = format_packet_log(packet)
                return self.ai_client.query(TECHNICAL_ANALYSIS_PROMPT.format(log=formatted))
            except Exception as e:
                return f"Error processing log: {str(e)}"
        
        else:
            return self.ai_client.query(GENERAL_PROMPT.format(query=msg))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WatchdogDashboard()
    window.show()
    sys.exit(app.exec())
