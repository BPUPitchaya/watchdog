import sys
import os
import json
import datetime
import math
import random
import signal

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, 
    QScrollArea, QSplitter, QHeaderView, QTextEdit, QProgressBar,
    QStackedWidget, QDialog, QSizePolicy, QListWidget, QMessageBox, QSlider, QFrame
)
from PyQt6.QtCore import QTimer, Qt, QRectF, QByteArray
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPainterPath, QLinearGradient
from PyQt6.QtSvgWidgets import QSvgWidget

import joblib
import pandas as pd
import numpy as np

from src.ml.feature_extractor import FeatureExtractor

from src.ai.ollama_client import OllamaClient
from src.ai.prompts import GENERAL_PROMPT, EXPLANATION_PROMPT, TECHNICAL_ANALYSIS_PROMPT
from src.ai.utils import format_packet_log

def signal_handler(sig, frame):
    QApplication.quit()

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

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
        self.timer.start(500)  # 0.5s

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
        painter.setPen(QPen(Qt.GlobalColor.white))
        # -15s at left
        painter.drawText(int(chart_rect.left() - 10), int(chart_rect.bottom() + 15), "-15s")
        # -7.5s at center
        painter.drawText(int(chart_rect.center().x() - 15), int(chart_rect.bottom() + 15), "-7.5s")
        # NOW at right
        painter.drawText(int(chart_rect.right() - 25), int(chart_rect.bottom() + 15), "NOW")

        # Draw the path with Bézier
        max_pps = max(self.data) if self.data else 0
        stroke_color = "#FF4B2B" if max_pps > 0.8 * self.y_axis_max else "#F59E0B" if max_pps > 0.5 * self.y_axis_max else "#00F2FE"
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

class CircularGaugeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.score = 100
        self.smoothed_score = 100
        self.target_score = 100
        self.svg_widget = QSvgWidget()
        layout = QVBoxLayout(self)
        layout.addWidget(self.svg_widget)
        self.smooth_timer = QTimer(self)
        self.smooth_timer.timeout.connect(self.update_smooth)
        self.smooth_timer.start(50)  # 50ms for smooth animation
        self.update_svg()

    def update_smooth(self):
        if abs(self.smoothed_score - self.target_score) > 0.1:
            self.smoothed_score += (self.target_score - self.smoothed_score) * 0.05
            self.update_svg()

    def update_svg(self):
        circumference = 2 * 3.14159 * 80  # radius 80
        dash_length = (self.smoothed_score / 100) * circumference
        color = self.get_color()
        svg = f'''
<svg width="200" height="200" viewBox="0 0 200 200">
<circle cx="100" cy="100" r="80" fill="none" stroke="#333333" stroke-width="10" stroke-opacity="0.3" />
<circle cx="100" cy="100" r="80" fill="none" stroke="{color}" stroke-width="10" stroke-dasharray="{dash_length},{circumference}" />
<text x="100" y="110" text-anchor="middle" font-family="Monospace" font-size="18" fill="{color}">{self.smoothed_score:.0f}% Risk</text>
</svg>
'''
        self.svg_widget.load(QByteArray(svg.encode()))

    def get_color(self):
        if self.smoothed_score > 80:
            return "#FF4B2B"  # red
        elif self.smoothed_score > 50:
            return "#F59E0B"  # amber
        else:
            return "#00F2FE"  # teal

    def set_score(self, score):
        self.target_score = score

class WatchdogDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WATCHDOG AI Dashboard")
        self.setGeometry(100, 100, 1200, 1000)

        # Check for --layout-only and --no-ai flags
        import sys
        self.layout_only = '--layout-only' in sys.argv
        self.no_ai = '--no-ai' in sys.argv

        self.ai_client = None

        self.previous_packets = 0

        self.status_card = QWidget()
        self.status_card.setStyleSheet("background-color: #1e293b; border-radius: 12px;")
        status_layout = QVBoxLayout(self.status_card)
        status_layout.setContentsMargins(24, 24, 24, 24)
        status_title = QLabel("SYSTEM STATUS")
        status_title.setStyleSheet("color: gray; font-family: Monospace; font-size: 10px; text-transform: uppercase;")
        status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(status_title)
        self.left_gauge = StatusCore()
        status_layout.addWidget(self.left_gauge)

        self.live_traffic = LiveTrafficWidget()
        self.live_traffic_card = QWidget()
        self.live_traffic_card.setStyleSheet("background-color: #1e293b; border-radius: 12px;")
        live_layout = QVBoxLayout(self.live_traffic_card)
        live_layout.setContentsMargins(24, 24, 24, 24)
        live_title = QLabel("LIVE TRAFFIC")
        live_title.setStyleSheet("color: gray; font-family: Monospace; font-size: 10px; text-transform: uppercase;")
        live_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        live_layout.addWidget(live_title)
        live_layout.addWidget(self.live_traffic)

        self.right_gauge = CircularGaugeWidget()
        self.threat_card = QWidget()
        self.threat_card.setStyleSheet("background-color: #1e293b; border-radius: 12px;")
        threat_layout = QVBoxLayout(self.threat_card)
        threat_layout.setContentsMargins(24, 24, 24, 24)
        threat_title = QLabel("RISK ANALYSIS")
        threat_title.setStyleSheet("color: gray; font-family: Monospace; font-size: 10px; text-transform: uppercase;")
        threat_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        threat_layout.addWidget(threat_title)
        threat_layout.addWidget(self.right_gauge)

        # Splitter for table and chat
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Src IP", "Dst IP", "Protocol", "Length", "Confidence Score", "Action"])
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

        # Navigation Sidebar (left)
        self.nav_sidebar = QWidget()
        self.nav_sidebar.setFixedWidth(80)
        self.nav_sidebar.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-right: 1px solid #222222;
            }
        """)
        nav_layout = QVBoxLayout(self.nav_sidebar)
        nav_layout.setContentsMargins(0, 20, 0, 20)
        nav_layout.setSpacing(20)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Navigation buttons
        nav_buttons = [
            ("LIVE SENTINEL", "Real-time visibility and high-frequency packet monitoring"),
            ("FORENSIC VAULT", "Translating complex metadata into human-readable advice"),
            ("AUTONOMOUS SHIELD", "Managing the host firewall and setting AI confidence thresholds"),
            ("AI MENTOR", "A dedicated chat interface for Llama 4 Scout to provide education-active security guidance"),
            ("NETWORK TOPOLOGY", "Identifying all hardware on the LAN to resolve the visibility gap"),
            ("SETTINGS & PRIVACY", "Configuring Ollama and ensuring alignment with NZ Privacy Act 2020 principles")
        ]

        self.nav_button_group = []
        for icon, tooltip in nav_buttons:
            btn = QPushButton(icon)
            btn.setFixedSize(80, 60)
            btn.setToolTip(tooltip)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: rgba(255, 255, 255, 0.3);
                    font-size: 10px;
                    font-weight: bold;
                    border-radius: 8px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #2a2a2a;
                    color: rgba(255, 255, 255, 0.6);
                }
                QPushButton:checked {
                    background-color: transparent;
                    color: #00D1FF;
                    border-left: 3px solid #00D1FF;
                }
            """)
            btn.setCheckable(True)
            nav_layout.addWidget(btn)
            self.nav_button_group.append(btn)

        # Set first button as active
        if self.nav_button_group:
            self.nav_button_group[0].setChecked(True)

        # Main content area
        main_content = QWidget()
        main_grid = QGridLayout(main_content)
        main_grid.setSpacing(20)

        # Header
        header = QLabel("WATCHDOG AI Dashboard")
        header.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: white;")

        # Header spanning columns
        main_grid.addWidget(header, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

        # Cards row (50%)
        main_grid.addWidget(self.status_card, 1, 0)
        main_grid.addWidget(self.live_traffic_card, 1, 1)
        main_grid.addWidget(self.threat_card, 1, 2)

        # Refresh button
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.update_ui)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #00D4FF;
                color: #121212;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00B8CC;
            }
        """)
        main_grid.addWidget(refresh_btn, 2, 0, 1, 3)

        # Splitter row (50%)
        main_grid.addWidget(splitter, 3, 0, 1, 3)

        # Set row stretches for 50% each, but bottom thicker
        main_grid.setRowStretch(1, 1)

class WatchdogDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WATCHDOG AI Dashboard")
        self.setGeometry(100, 100, 1200, 1000)

        # Check for --layout-only and --no-ai flags
        import sys
        self.layout_only = '--layout-only' in sys.argv
        self.no_ai = '--no-ai' in sys.argv

        # Initialize attributes
        self.model = None
        self.extractor = None
        self.ai_client = None
        self.previous_packets = 0

        # Load ML (skip if layout-only)
        if not self.layout_only:
            try:
                self.model = joblib.load('models/random_forest_model.pkl')
                self.extractor = FeatureExtractor()
            except Exception as e:
                print(f"Failed to load ML model: {e}")
                self.model = None
                self.extractor = None

            # Initialize AI client (skip if --no-ai flag)
            if not self.no_ai:
                try:
                    self.ai_client = OllamaClient()
                except Exception as e:
                    print(f"Failed to initialize AI: {e}")
                    self.ai_client = None

        # Create UI components
        self.create_ui()

        # Timer for auto-update (skip in layout-only)
        if not self.layout_only:
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_ui)
            self.timer.start(1000)  # 1 seconds

        # Initial update (skip in layout-only)
        if not self.layout_only:
            self.update_ui()

    def create_ui(self):
        # Create page container
        self.page_container = QStackedWidget()
        self.create_pages()

        # Navigation Sidebar (left)
        self.nav_sidebar = QWidget()
        self.nav_sidebar.setFixedWidth(80)
        self.nav_sidebar.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-right: 1px solid #222222;
            }
        """)

        nav_layout = QVBoxLayout(self.nav_sidebar)
        nav_layout.setContentsMargins(0, 20, 0, 20)
        nav_layout.setSpacing(20)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Navigation buttons
        nav_buttons = [
            ("LIVE SENTINEL", "Real-time visibility and high-frequency packet monitoring"),
            ("FORENSIC VAULT", "Translating complex metadata into human-readable advice"),
            ("AUTONOMOUS SHIELD", "Managing the host firewall and setting AI confidence thresholds"),
            ("AI MENTOR", "A dedicated chat interface for Llama 4 Scout to provide education-active security guidance"),
            ("NETWORK TOPOLOGY", "Identifying all hardware on the LAN to resolve the visibility gap"),
            ("SETTINGS & PRIVACY", "Configuring Ollama and ensuring alignment with NZ Privacy Act 2020 principles")
        ]

        self.nav_button_group = []
        for i, (icon, tooltip) in enumerate(nav_buttons):
            btn = QPushButton(icon)
            btn.setFixedSize(80, 60)
            btn.setToolTip(tooltip)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    color: rgba(255, 255, 255, 0.3);
                    font-size: 10px;
                    font-weight: bold;
                    border-radius: 8px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #2a2a2a;
                    color: rgba(255, 255, 255, 0.6);
                }
                QPushButton:checked {
                    background-color: transparent;
                    color: #00D1FF;
                    border-left: 3px solid #00D1FF;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self.switch_page(idx))
            nav_layout.addWidget(btn)
            self.nav_button_group.append(btn)

        # Set first button as active
        if self.nav_button_group:
            self.nav_button_group[0].setChecked(True)

        # Main layout with sidebar and page container
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.nav_sidebar)
        main_layout.addWidget(self.page_container)

        # Central widget
        central = QWidget()
        central.setLayout(main_layout)
        self.setCentralWidget(central)

    def create_pages(self):
        # Page 0: Live Sentinel (Dashboard)
        self.create_live_sentinel_page()

        # Page 1: Forensic Vault
        self.create_forensic_vault_page()

        # Page 2: Autonomous Shield (placeholder)
        self.create_autonomous_shield_page()

        # Page 3: AI Mentor (placeholder)
        self.create_ai_mentor_page()

        # Page 4: Network Topology (placeholder)
        self.create_placeholder_page("NETWORK TOPOLOGY", "Identifying all hardware on the LAN to resolve the visibility gap")

        # Page 5: Settings & Privacy (placeholder)
        self.create_placeholder_page("SETTINGS & PRIVACY", "Configuring Ollama and ensuring alignment with NZ Privacy Act 2020 principles")

    def create_live_sentinel_page(self):
        # Main content area
        main_content = QWidget()
        main_grid = QGridLayout(main_content)
        main_grid.setSpacing(30)  # Increased spacing for breathing room

        # Header
        header = QLabel("WATCHDOG AI Dashboard")
        header.setFont(QFont("JetBrains Mono", 24, QFont.Weight.Bold))  # Modern monospace font
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: white;")

        # AI Toggle Button
        self.ai_toggle_btn = QPushButton("AI: ON" if not self.no_ai else "AI: OFF")
        self.ai_toggle_btn.setCheckable(True)
        self.ai_toggle_btn.setChecked(not self.no_ai)
        self.ai_toggle_btn.clicked.connect(self.toggle_ai)
        self.ai_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #00D4FF;
                color: #121212;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-family: 'JetBrains Mono';
            }
            QPushButton:hover {
                background-color: #00B8CC;
            }
            QPushButton:checked {
                background-color: #00D4FF;
                color: #121212;
            }
            QPushButton:!checked {
                background-color: #666666;
                color: #CCCCCC;
            }
        """)

        # Header layout with title and toggle
        header_layout = QHBoxLayout()
        header_layout.addWidget(header, 1)  # Title takes available space
        header_layout.addWidget(self.ai_toggle_btn, 0)  # Button stays compact
        header_widget = QWidget()
        header_widget.setLayout(header_layout)

        # Header spanning columns
        main_grid.addWidget(header_widget, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

        # Cards with refined styling
        self.status_card = QWidget()
        self.status_card.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 41, 59, 0.8);
                border: 1px solid #222222;
                border-radius: 15px;
            }
        """)
        status_layout = QVBoxLayout(self.status_card)
        status_layout.setContentsMargins(40, 40, 40, 40)  # Increased padding
        status_title = QLabel("SYSTEM STATUS")
        status_title.setStyleSheet("color: gray; font-family: 'JetBrains Mono'; font-size: 10px; text-transform: uppercase; text-align: center;")
        status_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_layout.addWidget(status_title)
        self.left_gauge = StatusCore()
        status_layout.addWidget(self.left_gauge)

        self.live_traffic_card = QWidget()
        self.live_traffic_card.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 41, 59, 0.8);
                border: 1px solid #222222;
                border-radius: 15px;
            }
        """)
        live_layout = QVBoxLayout(self.live_traffic_card)
        live_layout.setContentsMargins(40, 40, 40, 40)
        live_title = QLabel("LIVE TRAFFIC")
        live_title.setStyleSheet("color: gray; font-family: 'JetBrains Mono'; font-size: 10px; text-transform: uppercase; text-align: center;")
        live_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        live_layout.addWidget(live_title)
        self.live_traffic = LiveTrafficWidget()
        live_layout.addWidget(self.live_traffic)

        self.threat_card = QWidget()
        self.threat_card.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 41, 59, 0.8);
                border: 1px solid #222222;
                border-radius: 15px;
            }
        """)
        threat_layout = QVBoxLayout(self.threat_card)
        threat_layout.setContentsMargins(40, 40, 40, 40)
        threat_title = QLabel("RISK ANALYSIS")
        threat_title.setStyleSheet("color: gray; font-family: 'JetBrains Mono'; font-size: 10px; text-transform: uppercase; text-align: center;")
        threat_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        threat_layout.addWidget(threat_title)
        self.right_gauge = CircularGaugeWidget()
        threat_layout.addWidget(self.right_gauge)

        # Cards row
        main_grid.addWidget(self.status_card, 1, 0)
        main_grid.addWidget(self.live_traffic_card, 1, 1)
        main_grid.addWidget(self.threat_card, 1, 2)

        # Ghost button styling
        refresh_btn = QPushButton("Refresh Data")
        refresh_btn.clicked.connect(self.update_ui)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #00D4FF;
                border: 2px solid #00D4FF;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(0, 212, 255, 0.1);
            }
        """)
        main_grid.addWidget(refresh_btn, 2, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

        # Splitter for table and chat
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Src IP", "Dst IP", "Protocol", "Length", "Confidence Score", "Action"])
        self.table.setContentsMargins(0, 24, 0, 24)
        self.table.verticalHeader().setDefaultSectionSize(50)
        splitter.addWidget(self.table)

        # Right: AI Intelligence Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(400)
        self.sidebar.setStyleSheet("background-color: rgba(15, 23, 42, 0.9); border-left: 1px solid rgba(255, 255, 255, 0.05);")

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

        # Input Field - sleek underline
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 2px solid #888888;
                background-color: transparent;
                color: white;
                padding: 8px;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #00D4FF;
            }
        """)
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

        # Splitter row
        main_grid.addWidget(splitter, 3, 0, 1, 3)

        # Set row stretches
        main_grid.setRowStretch(1, 1)
        main_grid.setRowStretch(3, 2)

        self.page_container.addWidget(main_content)

    def create_forensic_vault_page(self):
        # Forensic Vault page widget
        vault_page = QWidget()
        vault_layout = QVBoxLayout(vault_page)
        vault_layout.setContentsMargins(40, 40, 40, 40)
        vault_layout.setSpacing(20)

        # Header
        vault_header = QLabel("FORENSIC VAULT")
        vault_header.setFont(QFont("JetBrains Mono", 28, QFont.Weight.Bold))
        vault_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vault_header.setStyleSheet("color: white; margin-bottom: 20px;")
        vault_layout.addWidget(vault_header)

        # Subtitle
        vault_subtitle = QLabel("Translating complex metadata into human-readable advice")
        vault_subtitle.setFont(QFont("JetBrains Mono", 14))
        vault_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vault_subtitle.setStyleSheet("color: #888888; margin-bottom: 30px;")
        vault_layout.addWidget(vault_subtitle)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search Flagged Incidents:")
        search_label.setStyleSheet("color: white; font-family: 'JetBrains Mono';")
        self.vault_search = QLineEdit()
        self.vault_search.setPlaceholderText("Enter IP address, protocol, or threat type...")
        self.vault_search.setStyleSheet("""
            QLineEdit {
                background-color: rgba(30, 41, 59, 0.8);
                border: 1px solid #222222;
                border-radius: 8px;
                color: white;
                padding: 8px;
                font-family: 'JetBrains Mono';
            }
        """)
        self.vault_search.textChanged.connect(self.filter_vault_table)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.vault_search)
        vault_layout.addLayout(search_layout)

        # Flagged incidents table
        self.vault_table = QTableWidget()
        self.vault_table.setColumnCount(8)
        self.vault_table.setHorizontalHeaderLabels([
            "Timestamp", "Source IP", "Destination IP", "Protocol", 
            "Confidence", "Threat Level", "AI Summary", "Action"
        ])
        self.vault_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(30, 41, 59, 0.8);
                border: 1px solid #222222;
                border-radius: 15px;
                color: white;
                font-family: 'JetBrains Mono';
            }
            QHeaderView::section {
                background-color: #1a1a1a;
                color: white;
                border: none;
                padding: 8px;
                font-weight: bold;
            }
        """)
        # Set column widths - remove fixed widths to allow stretching
        # self.vault_table.setColumnWidth(0, 170)  # Timestamp
        # self.vault_table.setColumnWidth(1, 120)  # Source IP
        # self.vault_table.setColumnWidth(2, 120)  # Destination IP
        # self.vault_table.setColumnWidth(3, 80)   # Protocol
        # self.vault_table.setColumnWidth(4, 100)  # Confidence
        # self.vault_table.setColumnWidth(5, 100)  # Threat Level
        # self.vault_table.setColumnWidth(6, 180)  # AI Summary
        
        # Enable stretching to fill entire page width
        self.vault_table.horizontalHeader().setStretchLastSection(True)
        self.vault_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Timestamp - auto-resize
        self.vault_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Source IP - auto-resize
        self.vault_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Dest IP - auto-resize
        self.vault_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Protocol - auto-resize
        self.vault_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Confidence - auto-resize
        self.vault_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Threat Level - auto-resize
        self.vault_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # AI Summary - auto-resize
        # Last column (Action) will stretch to fill remaining space
        self.vault_table.verticalHeader().setDefaultSectionSize(50)
        self.vault_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.vault_table.itemDoubleClicked.connect(self.show_forensic_analysis)
        vault_layout.addWidget(self.vault_table)

        # Refresh button
        vault_refresh_btn = QPushButton("Load Flagged Incidents")
        vault_refresh_btn.clicked.connect(self.load_flagged_incidents)
        vault_refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #00D4FF;
                border: 2px solid #00D4FF;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-family: 'JetBrains Mono';
            }
            QPushButton:hover {
                background-color: rgba(0, 212, 255, 0.1);
            }
        """)
        vault_layout.addWidget(vault_refresh_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.page_container.addWidget(vault_page)

    def create_placeholder_page(self, title, description):
        # Placeholder page for future implementation
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        page_title = QLabel(title)
        page_title.setFont(QFont("JetBrains Mono", 28, QFont.Weight.Bold))
        page_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page_title.setStyleSheet("color: white;")
        layout.addWidget(page_title)

        page_desc = QLabel(description)
        page_desc.setFont(QFont("JetBrains Mono", 14))
        page_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page_desc.setStyleSheet("color: #888888;")
        layout.addWidget(page_desc)

        coming_soon = QLabel("Coming Soon...")
        coming_soon.setFont(QFont("JetBrains Mono", 16))
        coming_soon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        coming_soon.setStyleSheet("color: #00D4FF; margin-top: 50px;")
        layout.addWidget(coming_soon)

        self.page_container.addWidget(page)

    def toggle_ai(self, checked):
        if checked:
            # Enable AI
            if not self.ai_client:
                try:
                    self.ai_client = OllamaClient()
                    print("AI features enabled")
                except Exception as e:
                    print(f"Failed to initialize AI: {e}")
                    self.ai_toggle_btn.setChecked(False)
                    return
        else:
            # Disable AI
            self.ai_client = None
            print("AI features disabled")
        
        # Update button text and style
        self.ai_toggle_btn.setText("AI: ON" if checked else "AI: OFF")
        
        # Refresh forensic vault to update AI availability
        if hasattr(self, 'vault_table'):
            self.load_flagged_incidents()

    def switch_page(self, index):
        # Update button states
        for i, btn in enumerate(self.nav_button_group):
            btn.setChecked(i == index)
        
        # Switch to the selected page
        self.page_container.setCurrentIndex(index)
        
        # Load page-specific data
        if index == 1:  # Forensic Vault
            self.load_flagged_incidents()

    def load_flagged_incidents(self):
        # Load flagged incidents from packet_data.json
        try:
            with open('packet_data.json', 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"packets": []}

        packets = data.get("packets", [])
        flagged_packets = []
        
        # Filter for packets with ATTACK classification or low confidence
        for packet in packets:
            if not self.layout_only and self.model and self.extractor:
                packet_data = {
                    'src_ip': packet.get('src_ip', '192.168.1.1'),
                    'dst_ip': packet.get('dst_ip', '10.0.0.1'),
                    'protocol': 6 if packet.get('protocol', 'TCP').upper() == 'TCP' else 17,
                    'length': packet.get('length', 100),
                    'src_port': packet.get('src_port', 12345),
                    'dst_port': packet.get('dst_port', 80),
                    'flags': packet.get('flags', 'S'),
                    'direction': 'inbound'
                }
                features = self.extractor.extract_packet_features(packet_data)
                selected_features = self.extractor.get_selected_features(features)
                features_array = np.array(selected_features).reshape(1, -1)
                prediction = self.model.predict(features_array)[0]
                probabilities = self.model.predict_proba(features_array)[0]
                confidence = max(probabilities) * 100
                
                # Flag if ATTACK prediction OR low confidence (< 60%)
                if prediction == 1 or confidence < 60.0:
                    flagged_packets.append(packet)
        
        # Always add sample flagged incidents for demonstration
        sample_packets = [
            {
                'timestamp': 1773629875.0,
                'src_ip': '192.168.1.100',
                'dst_ip': '10.0.0.1',
                'protocol': 'TCP',
                'length': 1500,
                'src_port': 4444,
                'dst_port': 80,
                'flags': 'S',
                'count': 9999
            },
            {
                'timestamp': 1773629876.0,
                'src_ip': '10.10.10.10',
                'dst_ip': '172.16.40.172',
                'protocol': 'UDP',
                'length': 512,
                'src_port': 53,
                'dst_port': 53,
                'flags': '',
                'count': 10000
            },
            {
                'timestamp': 1773629877.0,
                'src_ip': '203.0.113.1',
                'dst_ip': '172.16.40.172',
                'protocol': 'TCP',
                'length': 2000,
                'src_port': 22,
                'dst_port': 22,
                'flags': 'SA',
                'count': 10001
            }
        ]
        
        # Add samples to ensure vault has content
        for sample in sample_packets:
            if len(flagged_packets) < 3:
                flagged_packets.append(sample)

        self.vault_table.setRowCount(len(flagged_packets))
        for i, packet in enumerate(flagged_packets):
            # Convert timestamp to human-readable format
            timestamp = packet.get('timestamp', 0)
            if isinstance(timestamp, (int, float)):
                dt = datetime.datetime.fromtimestamp(timestamp)
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                timestamp = "Unknown"
            
            src_ip = packet.get('src_ip', '')
            dst_ip = packet.get('dst_ip', '')
            protocol = packet.get('protocol', 'Other')
            
            # Always calculate confidence for all packets
            confidence = "N/A"
            threat_level = "UNKNOWN"
            if not self.layout_only and self.model and self.extractor:
                packet_data = {
                    'src_ip': src_ip or '192.168.1.1',
                    'dst_ip': dst_ip or '10.0.0.1',
                    'protocol': 6 if protocol.upper() == 'TCP' else 17,
                    'length': packet.get('length', 100),
                    'src_port': packet.get('src_port', 12345),
                    'dst_port': packet.get('dst_port', 80),
                    'flags': packet.get('flags', 'S'),
                    'direction': 'inbound'
                }
                features = self.extractor.extract_packet_features(packet_data)
                selected_features = self.extractor.get_selected_features(features)
                features_array = np.array(selected_features).reshape(1, -1)
                prediction = self.model.predict(features_array)[0]
                probabilities = self.model.predict_proba(features_array)[0]
                confidence = f"{max(probabilities) * 100:.1f}%"
                threat_level = "ATTACK" if prediction == 1 else "NORMAL"
            
            ai_summary = "Click to view AI analysis" if not self.layout_only else "Sample flagged packet"

            self.vault_table.setItem(i, 0, QTableWidgetItem(timestamp))
            self.vault_table.setItem(i, 1, QTableWidgetItem(src_ip))
            self.vault_table.setItem(i, 2, QTableWidgetItem(dst_ip))
            self.vault_table.setItem(i, 3, QTableWidgetItem(protocol))
            self.vault_table.setItem(i, 4, QTableWidgetItem(confidence))
            self.vault_table.setItem(i, 5, QTableWidgetItem(threat_level))
            self.vault_table.setItem(i, 6, QTableWidgetItem(ai_summary))
            
            # Add Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(5)
            
            # Block Source IP button
            block_src_btn = QPushButton("Block Src")
            block_src_btn.setFixedSize(70, 25)
            block_src_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF6B6B;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #FF5252;
                }
            """)
            block_src_btn.clicked.connect(lambda checked, ip=src_ip: self.block_ip_from_vault(ip))
            action_layout.addWidget(block_src_btn)
            
            # Block Destination IP button
            block_dst_btn = QPushButton("Block Dst")
            block_dst_btn.setFixedSize(70, 25)
            block_dst_btn.setStyleSheet("""
                QPushButton {
                    background-color: #00D4FF;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00B8CC;
                }
            """)
            block_dst_btn.clicked.connect(lambda checked, ip=dst_ip: self.block_ip_from_vault(ip))
            action_layout.addWidget(block_dst_btn)
            
            self.vault_table.setCellWidget(i, 7, action_widget)

    def filter_vault_table(self, text):
        # Filter table rows based on search text
        for row in range(self.vault_table.rowCount()):
            show_row = False
            for col in range(self.vault_table.columnCount()):
                item = self.vault_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    show_row = True
                    break
            self.vault_table.setRowHidden(row, not show_row)

    def block_ip_from_vault(self, ip_address):
        """Block an IP address from the vault and add it to the shield"""
        if not ip_address or ip_address in ["", "Unknown"]:
            return
            
        reply = QMessageBox.question(
            self, 
            'Block IP Address', 
            f'Are you sure you want to block {ip_address}?\n\nThis will add it to the Autonomous Shield block list.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Add to blocked IPs set
            if hasattr(self, 'blocked_ips'):
                self.blocked_ips.add(ip_address)
            
            # Increment manual block counter
            if hasattr(self, 'manual_block_count'):
                self.manual_block_count += 1
            
            # Add to shield's blocked list widget if it exists
            if hasattr(self, 'blocked_list_widget'):
                # Check if already in list
                items = []
                for i in range(self.blocked_list_widget.count()):
                    item_text = self.blocked_list_widget.item(i).text()
                    existing_ip = item_text.split(" - ")[0]
                    items.append(existing_ip)
                
                if ip_address not in items:
                    # Add with description from vault
                    description = "Blocked from Forensic Vault"
                    self.blocked_list_widget.addItem(f"{ip_address} - {description}")
            
            # Update statistics
            self.update_shield_statistics()
            
            # Show confirmation
            QMessageBox.information(self, "IP Blocked", 
                f"Successfully blocked {ip_address}\nAdded to Autonomous Shield block list.")
            
            print(f"Blocked IP from vault: {ip_address}")

    def show_forensic_analysis(self, item):
        # Show forensic analysis dialog for clicked item
        row = item.row()
        
        # Get packet data from table
        src_ip = self.vault_table.item(row, 1).text() if self.vault_table.item(row, 1) else ""
        dst_ip = self.vault_table.item(row, 2).text() if self.vault_table.item(row, 2) else ""
        protocol = self.vault_table.item(row, 3).text() if self.vault_table.item(row, 3) else ""
        
        # Create forensic analysis dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Forensic Analysis")
        dialog.setModal(True)
        dialog.setStyleSheet("background-color: #121212; color: white;")
        
        layout = QVBoxLayout(dialog)
        
        title = QLabel(f"Forensic Analysis: {src_ip} → {dst_ip}")
        title.setFont(QFont("JetBrains Mono", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #00D4FF; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Analysis content
        if not self.layout_only and self.ai_client:
            packet_info = f"Source IP: {src_ip}\nDestination IP: {dst_ip}\nProtocol: {protocol}"
            analysis_text = self.process_command(f"analyze packet: {packet_info}")
        else:
            analysis_text = f"This packet from {src_ip} to {dst_ip} using {protocol} was flagged as potentially malicious.\n\nIn a full implementation, Llama 4 Scout would provide detailed forensic analysis explaining why this packet was considered a threat, including:\n\n• Protocol analysis\n• Traffic pattern recognition\n• Known threat signature matching\n• Behavioral anomaly detection"
        
        analysis_label = QLabel(analysis_text)
        analysis_label.setWordWrap(True)
        analysis_label.setStyleSheet("background-color: rgba(30, 41, 59, 0.8); padding: 20px; border-radius: 10px; border: 1px solid #222222;")
        layout.addWidget(analysis_label)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #00D4FF;
                color: #121212;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        dialog.resize(600, 400)
        dialog.exec()

    def update_ui(self):
        current_packets = 0
        try:
            with open('packet_data.json', 'r') as f:
                data = json.load(f)
            current_packets = data.get('packet_count', 0)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"packets": []}

        packets = data.get("packets", [])
        if packets:
            # Update table
            self.table.setRowCount(min(10, len(packets)))
            for i, packet in enumerate(packets[-10:]):
                self.table.setItem(i, 0, QTableWidgetItem(packet.get('src_ip', '')))
                self.table.setItem(i, 1, QTableWidgetItem(packet.get('dst_ip', '')))
                proto = packet.get('protocol', 'Other')
                self.table.setItem(i, 2, QTableWidgetItem(proto))
                self.table.setItem(i, 3, QTableWidgetItem(str(packet.get('length', 0))))
                
                # ML predictions for Confidence Score and Action (skip in layout-only)
                if not self.layout_only and self.model and self.extractor:
                    packet_data = {
                        'src_ip': packet.get('src_ip', '192.168.1.1'),
                        'dst_ip': packet.get('dst_ip', '10.0.0.1'),
                        'protocol': 6 if packet.get('protocol', 'TCP').upper() == 'TCP' else 17,
                        'length': packet.get('length', 100),
                        'src_port': packet.get('src_port', 12345),
                        'dst_port': packet.get('dst_port', 80),
                        'flags': packet.get('flags', 'S'),
                        'direction': 'inbound'
                    }
                    features = self.extractor.extract_packet_features(packet_data)
                    selected_features = self.extractor.get_selected_features(features)
                    features_array = np.array(selected_features).reshape(1, -1)
                    prediction = self.model.predict(features_array)[0]
                    probabilities = self.model.predict_proba(features_array)[0]
                    confidence = max(probabilities) * 100
                    action = "NORMAL" if prediction == 0 else "ATTACK"
                    self.table.setItem(i, 4, QTableWidgetItem(f"{confidence:.1f}%"))
                    self.table.setItem(i, 5, QTableWidgetItem(action))
                else:
                    self.table.setItem(i, 4, QTableWidgetItem("N/A"))
                    self.table.setItem(i, 5, QTableWidgetItem("UNKNOWN"))

        # Update pps and gauge (skip in layout-only)
        if not self.layout_only:
            pps = max(0, current_packets - self.previous_packets)
            self.previous_packets = current_packets
            risk = min(100, (pps / 50) * 100)  # 50 pps = 100% risk
            self.right_gauge.set_score(risk)

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
        if self.layout_only or not self.ai_client:
            return f"Layout-only mode: Would process '{msg}' with AI analysis."
        
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

    def process_command(self, msg):
        if self.layout_only or not self.ai_client:
            return f"Layout-only mode: Would process '{msg}' with AI analysis."
        
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

    def create_autonomous_shield_page(self):
        """Create Autonomous Shield page with firewall management"""
        shield_page = QWidget()
        
        # Main layout
        main_layout = QVBoxLayout(shield_page)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Header
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet("""
            QWidget {
                background: linear-gradient(135deg, #1a1a1a, #2d3748);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px 15px 0 0;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(40, 20, 40, 20)
        
        title_section = QVBoxLayout()
        title_section.setSpacing(5)
        
        shield_title = QLabel("AUTONOMOUS SHIELD")
        shield_title.setFont(QFont("JetBrains Mono", 24, QFont.Weight.Bold))
        shield_title.setStyleSheet("color: #FF6B6B; margin: 0;")
        title_section.addWidget(shield_title)
        
        shield_subtitle = QLabel("Firewall Management & AI Confidence Control")
        shield_subtitle.setFont(QFont("JetBrains Mono", 12))
        shield_subtitle.setStyleSheet("color: #888888; margin: 0;")
        title_section.addWidget(shield_subtitle)
        
        header_layout.addLayout(title_section)
        header_layout.addStretch()
        
        main_layout.addWidget(header_widget)
        
        # Content area with two sections
        content_area = QWidget()
        content_layout = QHBoxLayout(content_area)
        content_layout.setSpacing(30)
        
        # Left section - Blocked IPs
        left_section = QWidget()
        left_section.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout = QVBoxLayout(left_section)
        left_layout.setSpacing(20)
        
        # Blocked IPs header
        blocked_header = QLabel("BLOCKED IP ADDRESSES")
        blocked_header.setFont(QFont("JetBrains Mono", 16, QFont.Weight.Bold))
        blocked_header.setStyleSheet("color: #FF6B6B; margin-bottom: 10px;")
        left_layout.addWidget(blocked_header)
        
        # Blocked IPs list
        self.blocked_list_widget = QListWidget()
        self.blocked_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #121212;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px;
                font-family: 'JetBrains Mono';
                font-size: 14px;
                color: white;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 5px;
                margin: 2px 0;
            }
            QListWidget::item:selected {
                background-color: rgba(255, 107, 107, 0.2);
            }
            QListWidget::item:hover {
                background-color: rgba(255, 107, 107, 0.1);
            }
        """)
        
        # Add some sample blocked IPs
        sample_blocked_ips = [
            "192.168.1.100 - Suspicious port scanning",
            "10.0.0.50 - Multiple failed login attempts", 
            "203.0.113.1 - Known malicious IP",
            "198.51.100.0 - Brute force attack detected"
        ]
        
        for ip_info in sample_blocked_ips:
            self.blocked_list_widget.addItem(ip_info)
        
        left_layout.addWidget(self.blocked_list_widget)
        
        # Unblock button
        unblock_btn = QPushButton("UNBLOCK SELECTED")
        unblock_btn.setFixedHeight(40)
        unblock_btn.setFont(QFont("JetBrains Mono", 12, QFont.Weight.Bold))
        unblock_btn.setStyleSheet("""
            QPushButton {
                background: linear-gradient(135deg, #FF6B6B, #FF5252);
                border: 2px solid #FF6B6B;
                border-radius: 10px;
                color: white;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #FF5252, #FF3838);
                border: 2px solid #FF5252;
            }
            QPushButton:pressed {
                background: linear-gradient(135deg, #FF3838, #E91E63);
                border: 2px solid #FF3838;
            }
        """)
        unblock_btn.clicked.connect(self.unblock_selected_ip)
        left_layout.addWidget(unblock_btn)
        
        # Right section - Confidence Threshold
        right_section = QWidget()
        right_section.setFixedWidth(400)
        right_layout = QVBoxLayout(right_section)
        right_layout.setSpacing(20)
        
        # Confidence threshold header
        confidence_header = QLabel("AI CONFIDENCE THRESHOLD")
        confidence_header.setFont(QFont("JetBrains Mono", 16, QFont.Weight.Bold))
        confidence_header.setStyleSheet("color: #00D4FF; margin-bottom: 10px;")
        right_layout.addWidget(confidence_header)
        
        # Confidence slider
        confidence_container = QWidget()
        confidence_container.setStyleSheet("""
            QWidget {
                background-color: #121212;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        confidence_layout = QVBoxLayout(confidence_container)
        confidence_layout.setSpacing(15)
        
        # Current threshold display
        self.confidence_label = QLabel("Current Threshold: 75%")
        self.confidence_label.setFont(QFont("JetBrains Mono", 14))
        self.confidence_label.setStyleSheet("color: #00D4FF; margin: 0;")
        self.confidence_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        confidence_layout.addWidget(self.confidence_label)
        
        # Confidence slider
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(75)
        self.confidence_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #1a1a1a;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #FF6B6B, stop:0.5 #FFD93D, stop:1 #6BCF7F);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #00D4FF;
                border: 2px solid #1a1a1a;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
        """)
        self.confidence_slider.valueChanged.connect(self.update_confidence_threshold)
        confidence_layout.addWidget(self.confidence_slider)
        
        # Threshold labels
        labels_layout = QHBoxLayout()
        labels_layout.setSpacing(0)
        
        relaxed_label = QLabel("Relaxed")
        relaxed_label.setFont(QFont("JetBrains Mono", 10))
        relaxed_label.setStyleSheet("color: #FF6B6B;")
        
        balanced_label = QLabel("Balanced")
        balanced_label.setFont(QFont("JetBrains Mono", 10))
        balanced_label.setStyleSheet("color: #FFD93D;")
        balanced_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        aggressive_label = QLabel("Aggressive")
        aggressive_label.setFont(QFont("JetBrains Mono", 10))
        aggressive_label.setStyleSheet("color: #6BCF7F;")
        aggressive_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        labels_layout.addWidget(relaxed_label)
        labels_layout.addStretch()
        labels_layout.addWidget(balanced_label)
        labels_layout.addStretch()
        labels_layout.addWidget(aggressive_label)
        confidence_layout.addLayout(labels_layout)
        
        # Mode description
        mode_desc = QLabel("Lower values = More blocks (Aggressive)\nHigher values = Fewer false positives (Relaxed)")
        mode_desc.setFont(QFont("JetBrains Mono", 10))
        mode_desc.setStyleSheet("color: #888888; margin: 10px 0;")
        mode_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mode_desc.setWordWrap(True)
        confidence_layout.addWidget(mode_desc)
        
        right_layout.addWidget(confidence_container)
        
        # Statistics
        stats_container = QWidget()
        stats_container.setStyleSheet("""
            QWidget {
                background-color: #121212;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setSpacing(10)
        
        stats_title = QLabel("BLOCKING STATISTICS")
        stats_title.setFont(QFont("JetBrains Mono", 12, QFont.Weight.Bold))
        stats_title.setStyleSheet("color: #FFD93D; margin: 0;")
        stats_layout.addWidget(stats_title)
        
        self.total_blocked_label = QLabel(f"Total Blocked: {len(sample_blocked_ips)}")
        self.total_blocked_label.setFont(QFont("JetBrains Mono", 11))
        self.total_blocked_label.setStyleSheet("color: white; margin: 5px 0;")
        stats_layout.addWidget(self.total_blocked_label)
        
        self.auto_blocked_label = QLabel(f"Auto-Blocked: {len(sample_blocked_ips)}")
        self.auto_blocked_label.setFont(QFont("JetBrains Mono", 11))
        self.auto_blocked_label.setStyleSheet("color: #6BCF7F; margin: 5px 0;")
        stats_layout.addWidget(self.auto_blocked_label)
        
        self.manual_blocked_label = QLabel("Manual: 0")
        self.manual_blocked_label.setFont(QFont("JetBrains Mono", 11))
        self.manual_blocked_label.setStyleSheet("color: #00D4FF; margin: 5px 0;")
        stats_layout.addWidget(self.manual_blocked_label)
        
        # Initialize manual block counter
        self.manual_block_count = 0
        
        right_layout.addWidget(stats_container)
        right_layout.addStretch()
        
        # Add sections to content
        content_layout.addWidget(left_section)
        content_layout.addWidget(right_section)
        
        main_layout.addWidget(content_area)
        shield_page.setLayout(main_layout)
        self.page_container.addWidget(shield_page)
        
        # Initialize blocked IPs list
        self.blocked_ips = set()

    def update_shield_statistics(self):
        """Update the shield statistics display"""
        if hasattr(self, 'total_blocked_label') and hasattr(self, 'blocked_list_widget'):
            total_count = self.blocked_list_widget.count()
            auto_count = 4  # Initial sample blocked IPs
            manual_count = self.manual_block_count if hasattr(self, 'manual_block_count') else 0
            
            self.total_blocked_label.setText(f"Total Blocked: {total_count}")
            self.auto_blocked_label.setText(f"Auto-Blocked: {auto_count}")
            self.manual_blocked_label.setText(f"Manual: {manual_count}")

    def unblock_selected_ip(self):
        """Unblock the selected IP from the list"""
        selected_items = self.blocked_list_widget.selectedItems()
        if selected_items:
            item = selected_items[0]
            ip_address = item.text().split(" - ")[0]  # Extract IP from "IP - description"
            
            reply = QMessageBox.question(
                self, 
                'Unblock IP', 
                f'Are you sure you want to unblock {ip_address}?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.blocked_list_widget.takeItem(self.blocked_list_widget.row(item))
                if ip_address in self.blocked_ips:
                    self.blocked_ips.remove(ip_address)
                
                # Update manual block count if it was a manual block
                if hasattr(self, 'manual_block_count'):
                    item_text = item.text()
                    if "Blocked from Forensic Vault" in item_text or "Manual" in item_text:
                        self.manual_block_count = max(0, self.manual_block_count - 1)
                
                # Update statistics
                self.update_shield_statistics()
                
                print(f"Unblocked IP: {ip_address}")

    def update_confidence_threshold(self, value):
        """Update the confidence threshold display"""
        self.confidence_label.setText(f"Current Threshold: {value}%")
        
        # Update label color based on threshold
        if value < 33:
            color = "#6BCF7F"  # Green for aggressive
        elif value < 66:
            color = "#FFD93D"  # Yellow for balanced
        else:
            color = "#FF6B6B"  # Red for relaxed
        
        self.confidence_label.setStyleSheet(f"color: {color}; margin: 0;")

    def create_ai_mentor_page(self):
        """Create AI Mentor page as a Forensic Analysis Hub"""
        # AI Mentor page widget
        mentor_page = QWidget()
        
        # Main Horizontal Layout: 70% chat, 30% diagnostics
        main_layout = QHBoxLayout(mentor_page)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # LEFT SIDE - Chat Area (70%)
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setSpacing(10)

        # Status Bar Header
        status_bar = QFrame()
        status_bar.setFixedHeight(40)
        status_bar.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 30, 0.9);
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 8px;
                color: #00D4FF;
            }
        """)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(15, 5, 15, 5)
        
        # Sentinel Pulse Icon
        pulse_icon = QLabel("●")
        pulse_icon.setStyleSheet("""
            QLabel {
                color: #00D4FF;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        status_layout.addWidget(pulse_icon)
        
        # Status Text
        status_text = QLabel("SYSTEM STATUS: MONITORING | AGENT: LLAMA 4 SCOUT")
        status_text.setStyleSheet("""
            QLabel {
                color: #00D4FF;
                font-family: 'JetBrains Mono';
                font-size: 12px;
                font-weight: bold;
            }
        """)
        status_layout.addWidget(status_text)
        status_layout.addStretch()
        
        chat_layout.addWidget(status_bar)

        # Chat Scroll Area
        self.mentor_chat_area = QScrollArea()
        self.mentor_chat_area.setWidgetResizable(True)
        self.mentor_chat_area.setFrameShape(QFrame.Shape.NoFrame)
        self.mentor_chat_area.setStyleSheet("""
            QScrollArea {
                background: rgba(18, 18, 18, 0.8);
                border: 1px solid rgba(0, 212, 255, 0.2);
                border-radius: 12px;
            }
        """)
        self.mentor_chat_area.setContentsMargins(100, 10, 100, 10)

        # Chat Container
        self.mentor_chat_widget = QWidget()
        self.mentor_chat_layout = QVBoxLayout(self.mentor_chat_widget)
        self.mentor_chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.mentor_chat_layout.setContentsMargins(20, 20, 20, 20)
        self.mentor_chat_layout.setSpacing(10)
        self.mentor_chat_area.setWidget(self.mentor_chat_widget)

        chat_layout.addWidget(self.mentor_chat_area, stretch=1)

        # Quick Action Ghost Buttons
        quick_actions = QFrame()
        quick_actions.setFixedHeight(50)
        quick_actions.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
            }
        """)
        actions_layout = QHBoxLayout(quick_actions)
        actions_layout.setContentsMargins(100, 10, 100, 10)
        actions_layout.setSpacing(15)
        
        # Ghost Button 1
        btn1 = QPushButton("Analyze Last 5 Minutes")
        btn1.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-family: 'JetBrains Mono';
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)
        btn1.clicked.connect(lambda: self.quick_question("Analyze the last 5 minutes of network activity"))
        actions_layout.addWidget(btn1)
        
        # Ghost Button 2
        btn2 = QPushButton("Scan Local Devices")
        btn2.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-family: 'JetBrains Mono';
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)
        btn2.clicked.connect(lambda: self.quick_question("Scan all local devices for security vulnerabilities"))
        actions_layout.addWidget(btn2)
        
        # Ghost Button 3
        btn3 = QPushButton("Explain Risk Level")
        btn3.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                font-family: 'JetBrains Mono';
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)
        btn3.clicked.connect(lambda: self.quick_question("Explain the current network risk level"))
        actions_layout.addWidget(btn3)
        
        actions_layout.addStretch()
        chat_layout.addWidget(quick_actions)

        # Input Section
        input_container = QFrame()
        input_container.setFixedHeight(50)  # Reduced height
        input_container.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 30, 0.8);
                border: 1px solid rgba(0, 212, 255, 0.3);
                border-radius: 8px;
            }
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(100, 5, 100, 5)  # Reduced margins to bring it up
        
        self.mentor_input = QLineEdit()
        self.mentor_input.setPlaceholderText("Ask me anything about network security...")
        self.mentor_input.setStyleSheet("""
            QLineEdit {
                background: rgba(30, 30, 30, 0.6);
                color: white;
                border: 1px solid rgba(0, 212, 255, 0.4);
                padding: 8px;  # Reduced padding
                border-radius: 6px;
                font-family: 'JetBrains Mono';
            }
            QLineEdit:focus {
                border: 1px solid #00D4FF;
                background: rgba(30, 30, 30, 0.8);
            }
        """)

        self.mentor_send_btn = QPushButton("SEND")
        self.mentor_send_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 212, 255, 0.2);
                border: 1px solid #00D4FF;
                color: #00D4FF;
                font-weight: bold;
                padding: 8px 16px;  # Reduced padding
                border-radius: 6px;
                font-family: 'JetBrains Mono';
            }
            QPushButton:hover {
                background: rgba(0, 212, 255, 0.3);
            }
        """)

        input_layout.addWidget(self.mentor_input)
        input_layout.addWidget(self.mentor_send_btn)
        chat_layout.addWidget(input_container)

        # Add chat container to main layout (70%)
        main_layout.addWidget(chat_container, stretch=7)

        # RIGHT SIDE - Live Diagnostics (30%)
        diagnostics_container = QFrame()
        diagnostics_container.setFixedWidth(400)
        diagnostics_container.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 30, 0.8);
                border: 1px solid rgba(0, 212, 255, 0.2);
                border-radius: 12px;
            }
        """)
        diagnostics_layout = QVBoxLayout(diagnostics_container)
        diagnostics_layout.setContentsMargins(20, 20, 20, 20)
        diagnostics_layout.setSpacing(15)

        # Diagnostics Header
        diag_header = QLabel("LIVE DIAGNOSTICS")
        diag_header.setStyleSheet("""
            QLabel {
                color: #00D4FF;
                font-family: 'JetBrains Mono';
                font-size: 14px;
                font-weight: bold;
                border-bottom: 1px solid rgba(0, 212, 255, 0.3);
                padding-bottom: 10px;
            }
        """)
        diagnostics_layout.addWidget(diag_header)

        # Threat Level Meter
        threat_frame = QFrame()
        threat_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 107, 107, 0.3);
                border-radius: 8px;
                padding: 10px;
            }
        """)
        threat_layout = QVBoxLayout(threat_frame)
        
        threat_title = QLabel("THREAT LEVEL")
        threat_title.setStyleSheet("""
            QLabel {
                color: #FF6B6B;
                font-family: 'JetBrains Mono';
                font-size: 12px;
                font-weight: bold;
            }
        """)
        threat_layout.addWidget(threat_title)
        
        self.threat_level_label = QLabel("LOW")
        self.threat_level_label.setStyleSheet("""
            QLabel {
                color: #6BCF7F;
                font-family: 'JetBrains Mono';
                font-size: 24px;
                font-weight: bold;
            }
        """)
        threat_layout.addWidget(self.threat_level_label)
        
        diagnostics_layout.addWidget(threat_frame)

        # Network Activity
        activity_frame = QFrame()
        activity_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
            }
        """)
        activity_layout = QVBoxLayout(activity_frame)
        
        activity_title = QLabel("NETWORK ACTIVITY")
        activity_title.setStyleSheet("""
            QLabel {
                color: white;
                font-family: 'JetBrains Mono';
                font-size: 12px;
                font-weight: bold;
            }
        """)
        activity_layout.addWidget(activity_title)
        
        self.activity_text = QLabel("Monitoring...\nNo suspicious activity detected")
        self.activity_text.setStyleSheet("""
            QLabel {
                color: #888888;
                font-family: 'JetBrains Mono';
                font-size: 10px;
            }
        """)
        self.activity_text.setWordWrap(True)
        activity_layout.addWidget(self.activity_text)
        
        diagnostics_layout.addWidget(activity_frame)

        # Recent Alerts
        alerts_frame = QFrame()
        alerts_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
            }
        """)
        alerts_layout = QVBoxLayout(alerts_frame)
        
        alerts_title = QLabel("RECENT ALERTS")
        alerts_title.setStyleSheet("""
            QLabel {
                color: white;
                font-family: 'JetBrains Mono';
                font-size: 12px;
                font-weight: bold;
            }
        """)
        alerts_layout.addWidget(alerts_title)
        
        self.alerts_text = QLabel("No alerts in last hour")
        self.alerts_text.setStyleSheet("""
            QLabel {
                color: #888888;
                font-family: 'JetBrains Mono';
                font-size: 10px;
            }
        """)
        self.alerts_text.setWordWrap(True)
        alerts_layout.addWidget(self.alerts_text)
        
        diagnostics_layout.addWidget(alerts_frame)
        
        diagnostics_layout.addStretch()

        # Add diagnostics container to main layout (30%)
        main_layout.addWidget(diagnostics_container, stretch=3)
        
        # Store references
        self.chat_container = self.mentor_chat_widget
        self.chat_layout = self.mentor_chat_layout
        self.scroll_area = self.mentor_chat_area
        self.chat_input = self.mentor_input
        self.send_button = self.mentor_send_btn
        
        # Connect signals
        self.mentor_input.returnPressed.connect(self.send_mentor_message)
        self.mentor_send_btn.clicked.connect(self.send_mentor_message)
        
        # Add welcome message with XAI Insight Card styling
        welcome_card = self.create_insight_card("SYSTEM READY", 
            "AI Forensic Hub initialized. I'm monitoring network activity and ready to analyze security events. Ask me about threats, vulnerabilities, or network behavior.")
        self.mentor_chat_layout.addWidget(welcome_card)
        
        mentor_page.setLayout(main_layout)
        self.page_container.addWidget(mentor_page)

    def send_mentor_message(self):
        """Send message to AI Mentor"""
        message = self.mentor_input.text().strip()
        if not message:
            return
        
        # Check if chat layout exists before adding messages
        if not hasattr(self, 'mentor_chat_layout'):
            return
        
        # Add user message
        self.add_mentor_message("You", message)
        self.mentor_input.clear()
        
        # Show typing indicator
        self.show_mentor_typing()
        
        # Process response (simulate for now)
        QTimer.singleShot(1500, lambda: self.process_mentor_response(message))

    def create_insight_card(self, header, content):
        """Create an XAI Insight Card with glassmorphism styling"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 30, 0.8);
                border: 1px solid rgba(0, 212, 255, 0.4);
                border-radius: 12px;
                margin: 5px 0;
            }
        """)
        card.setMaximumWidth(600)
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 12, 15, 12)
        card_layout.setSpacing(8)
        
        # Header
        header_label = QLabel(f"[{header}]")
        header_label.setStyleSheet("""
            QLabel {
                color: #00D4FF;
                font-family: 'JetBrains Mono';
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
            }
        """)
        card_layout.addWidget(header_label)
        
        # Content
        content_label = QLabel(content)
        content_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: 'JetBrains Mono';
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        content_label.setWordWrap(True)
        card_layout.addWidget(content_label)
        
        return card

    def add_mentor_message(self, sender, message):
        """Add a message to the chat display with glassmorphism styling"""
        # Create message widget
        message_widget = QWidget()
        message_layout = QHBoxLayout(message_widget)
        message_layout.setContentsMargins(0, 0, 0, 0)
        
        if sender == "You":
            # User message - simple bubble
            message_label = QLabel(message)
            message_label.setWordWrap(True)
            message_label.setFont(QFont("JetBrains Mono", 11))
            message_label.setMaximumWidth(600)
            message_label.setStyleSheet("""
                QLabel {
                    background: rgba(0, 123, 255, 0.8);
                    color: white;
                    padding: 10px 15px;
                    border-radius: 12px;
                    border: 1px solid rgba(0, 123, 255, 0.4);
                }
            """)
            message_layout.addStretch()
            message_layout.addWidget(message_label)
            message_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        else:
            # AI message - create insight card
            insight_card = self.create_insight_card("ANALYSIS COMPLETE", message)
            message_layout.addWidget(insight_card)
            message_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
            
        self.mentor_chat_layout.addWidget(message_widget)
        QTimer.singleShot(100, lambda: self.mentor_chat_area.verticalScrollBar().setValue(
            self.mentor_chat_area.verticalScrollBar().maximum()
        ))  # Auto-scroll

    def quick_question(self, question):
        """Handle quick question button clicks"""
        self.mentor_input.setText(question)
        self.send_mentor_message()

    def show_mentor_typing(self):
        """Show typing indicator"""
        typing_label = QLabel("AI Mentor is typing...")
        typing_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-style: italic;
                font-family: Arial;
                font-size: 12px;
                padding: 5px;
            }
        """)
        self.mentor_chat_layout.addWidget(typing_label)
        
        # Auto-scroll to typing indicator
        QTimer.singleShot(100, lambda: self.mentor_chat_area.verticalScrollBar().setValue(
            self.mentor_chat_area.verticalScrollBar().maximum()
        ))
        
        # Store reference to remove later
        self.typing_indicator = typing_label

    def process_mentor_response(self, user_message):
        """Process and display AI response"""
        # Remove typing indicator
        if hasattr(self, 'typing_indicator') and self.typing_indicator is not None:
            try:
                self.mentor_chat_layout.removeWidget(self.typing_indicator)
                self.typing_indicator.deleteLater()
                self.typing_indicator = None
            except:
                pass  # Widget already deleted
        
        # Generate response (hardcoded for now)
        response = self.generate_ai_response(user_message)
        
        # Add AI response
        self.add_mentor_message("AI Mentor", response)

    def generate_ai_response(self, message):
        """Generate AI response based on user message"""
        message_lower = message.lower()
        
        if "router" in message_lower and "harden" in message_lower:
            return """To harden your router:
            
1. Change default admin password
2. Update firmware regularly  
3. Disable WPS (Wi-Fi Protected Setup)
4. Use WPA3 encryption
5. Disable remote management
6. Enable firewall features
7. Change default SSID name
8. Set up guest network separately
9. Enable MAC address filtering
10. Regular security audits"""
        
        elif "syn flood" in message_lower:
            return """A SYN flood attack is a type of DoS attack that exploits the TCP handshake process:

How it works:
1. Attacker sends multiple SYN packets to target
2. Target responds with SYN-ACK packets
3. Attacker never sends ACK packets
4. Target's connection table fills up
5. Legitimate connections are blocked

Mitigation:
- SYN cookies
- Rate limiting
- Firewall rules
- Load balancers
- Intrusion detection systems"""
        
        elif "port scanning" in message_lower:
            return """Port scanning is the process of checking open ports on a network:

Types:
- TCP Connect Scan: Full three-way handshake
- SYN Scan: Half-open scanning
- UDP Scan: Checks UDP ports
- Xmas Scan: Uses FIN, PSH, URG flags

Detection:
- Monitor connection logs
- Use intrusion detection systems
- Check for unusual port access patterns

Prevention:
- Close unused ports
- Use firewalls
- Implement port knocking
- Regular security audits"""
        
        elif "firewall" in message_lower and "rules" in message_lower:
            return """Best practices for firewall rules:

1. Default deny policy
2. Principle of least privilege
3. Rule ordering matters
4. Document all rules
5. Regular rule reviews
6. Separate internal/external rules
7. Use specific IP ranges
8. Log and monitor rules
9. Backup configurations
10. Test changes in staging"""
        
        else:
            return """That's a great cybersecurity question! Based on what you've asked, I recommend:

1. Assess your current security posture
2. Identify specific vulnerabilities
3. Implement defense-in-depth strategy
4. Regular security monitoring
5. Employee training and awareness
6. Incident response planning

Would you like me to elaborate on any of these areas or do you have a more specific question?"""

    def quick_question(self, question):
        """Handle quick suggestion clicks"""
        self.mentor_input.setText(question)
        self.send_mentor_message()

    def closeEvent(self, event):
        # Stop all timers
        if hasattr(self, 'timer'):
            self.timer.stop()
        if hasattr(self, 'right_gauge') and hasattr(self.right_gauge, 'smooth_timer'):
            self.right_gauge.smooth_timer.stop()
        if hasattr(self, 'live_traffic') and hasattr(self.live_traffic, 'timer'):
            self.live_traffic.timer.stop()
        # Quit the application
        QApplication.quit()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WatchdogDashboard()
    window.show()
    sys.exit(app.exec())
