import sys
import os
import json
import datetime
import math
import random
import signal
import threading

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, 
    QScrollArea, QSplitter, QHeaderView, QTextEdit, QProgressBar,
    QStackedWidget, QDialog, QSizePolicy, QListWidget, QListWidgetItem, QMessageBox, QSlider, QFrame, QComboBox, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize, QRect, QRectF, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup, QPointF, QByteArray
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPainterPath, QLinearGradient, QRadialGradient, QPixmap, QIcon
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

# Theme constants for consistent styling across the dashboard - Updated for hi-fi dark teal design
THEME = {
    'primary': '#00B4D8',      # Cyan/teal accent
    'secondary': '#0077B6',     # Darker teal
    'success': '#00B4D8',       # Cyan for health
    'warning': '#FF9F43',      # Orange warning
    'danger': '#FF6B6B',       # Red for risk
    'bg_dark': '#0A1628',      # Deep dark blue background
    'bg_card': '#0D1F35',      # Slightly lighter card background
    'bg_header': '#071220',    # Header background
    'text_primary': '#FFFFFF',
    'text_secondary': '#94A3B8',
    'border': '#1E3A5F',       # Teal border
    'border_highlight': '#00B4D8',
    'font_mono': "'Courier New', monospace",
    'gauge_bg': '#1A3A4A',     # Gauge background ring
    'gauge_active': '#00B4D8', # Gauge active color
    'risk_low': '#00B4D8',     # Low risk cyan
    'risk_high': '#FF6B6B'     # High risk red
}

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
        font = QFont("Arial", 48)
        painter.setFont(font)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "S")

        # Text: horizontal centered 'SYSTEM SAFE'
        painter.setPen(QPen(Qt.GlobalColor.white))
        font = QFont("Arial", 14)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 2)
        painter.setFont(font)
        painter.drawText(QRectF(rect.left(), center.y() + 30, rect.width(), 30), Qt.AlignmentFlag.AlignCenter, "SYSTEM SAFE")

class SystemHealthGauge(QWidget):
    """Circular gauge showing system health percentage"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.health_value = 92
        self.setMinimumSize(180, 180)
        
    def set_health(self, value):
        self.health_value = max(0, min(100, value))
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - 20
        
        # Background ring
        painter.setPen(QPen(QColor(THEME['gauge_bg']), 12))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, radius, radius)
        
        # Active arc (health percentage)
        angle = int(self.health_value * 3.6 * 16)  # Convert to 1/16 degrees
        pen = QPen(QColor(THEME['gauge_active']), 12)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(int(center.x() - radius), int(center.y() - radius), 
                       int(radius * 2), int(radius * 2), 90 * 16, -angle)
        
        # Center text
        painter.setPen(QPen(QColor(THEME['gauge_active'])))
        painter.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        text = f"{self.health_value}%"
        text_rect = QRect(center.x() - 50, center.y() - 20, 100, 40)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

class RiskAnalysisGauge(QWidget):
    """Circular gauge showing risk percentage"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.risk_value = 5
        self.setMinimumSize(180, 180)
        
    def set_risk(self, value):
        self.risk_value = max(0, min(100, value))
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) // 2 - 20
        
        # Background ring
        painter.setPen(QPen(QColor(THEME['gauge_bg']), 12))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, radius, radius)
        
        # Active arc (risk percentage)
        angle = int(self.risk_value * 3.6 * 16)
        # Use green for low risk, red for high
        color = THEME['risk_low'] if self.risk_value < 50 else THEME['risk_high']
        pen = QPen(QColor(color), 12)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawArc(int(center.x() - radius), int(center.y() - radius), 
                       int(radius * 2), int(radius * 2), 90 * 16, -angle)
        
        # Center text
        painter.setPen(QPen(QColor(color)))
        painter.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        text = f"{self.risk_value}%"
        text_rect = QRect(center.x() - 50, center.y() - 20, 100, 40)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, text)

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

class ForensicAssistantPanel(QWidget):
    """AI chat panel for forensic analysis"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header
        header = QLabel("Forensic Assistant AI")
        header.setStyleSheet(f"""
            background-color: {THEME['primary']};
            color: white;
            padding: 12px;
            font-family: {THEME['font_mono']};
            font-size: 14px;
            font-weight: bold;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        """)
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Chat area
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-top: none;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                padding: 10px;
            }}
        """)
        layout.addWidget(self.chat_area)
        
        # Input area
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(8)
        input_widget.setStyleSheet(f"""
            background-color: {THEME['bg_card']};
            border: 1px solid {THEME['border']};
            border-top: none;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
        """)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type here to ask AI...")
        self.input_field.setStyleSheet(f"""
            QLineEdit {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 6px;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                padding: 8px 12px;
            }}
        """)
        input_layout.addWidget(self.input_field)
        
        send_btn = QPushButton("▶")
        send_btn.setFixedSize(30, 30)
        send_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 10px;
            }}
            QPushButton:hover {{
                background-color: {THEME['secondary']};
            }}
        """)
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        
        # Connect Enter key to send message
        self.input_field.returnPressed.connect(self.send_message)
        
        layout.addWidget(input_widget)
        
    def send_message(self):
        text = self.input_field.text().strip()
        if text:
            self.chat_area.append(f"<b>You:</b> {text}")
            self.chat_area.append(f"<b><span style='color: {THEME['primary']}'>AI:</span></b> I'm analyzing the packet data...")
            self.input_field.clear()

class NetworkTopologyWidget(QWidget):
    """Cisco-style network topology visualization with radial layout"""
    device_clicked = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 350)
        self.devices = []
        self.device_positions = {}
        self.hovered_device = None
        self.selected_device = None
        self.animation_offset = 0
        
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self._update_animation)
        self.anim_timer.start(50)
        
    def set_devices(self, devices):
        self.devices = devices
        self.device_positions = {}
        self.hovered_device = None
        self.selected_device = None
        self.update()
        
    def _update_animation(self):
        self.animation_offset = (self.animation_offset + 2) % 20
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(THEME['bg_dark']))
        
        rect = self.rect().adjusted(20, 20, -20, -20)
        center_x = rect.center().x()
        center_y = rect.center().y()
        center = QPointF(center_x, center_y)
        
        gateway_radius = 35
        orbit_radius = min(rect.width(), rect.height()) / 2 - 70
        
        self._draw_connections(painter, center, orbit_radius, gateway_radius)
        self._draw_gateway(painter, center, gateway_radius)
        
        if not self.devices:
            painter.setPen(QPen(QColor(THEME['text_secondary'])))
            painter.setFont(QFont(THEME['font_mono'].strip("'"), 14))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "🌐 No devices discovered\nRun a network scan to see topology")
            return
            
        angle_step = 2 * math.pi / len(self.devices)
        for i, device in enumerate(self.devices):
            angle = i * angle_step - math.pi / 2
            x = center_x + orbit_radius * math.cos(angle)
            y = center_y + orbit_radius * math.sin(angle)
            device_center = QPointF(x, y)
            
            self.device_positions[device['ip']] = {
                'center': device_center,
                'radius': 25,
                'device': device
            }
            
            self._draw_device_node(painter, device_center, 25, device, i)
            
        self._draw_legend(painter)
        
    def _draw_connections(self, painter, center, orbit_radius, gateway_radius):
        if not self.devices:
            return
            
        angle_step = 2 * math.pi / len(self.devices)
        
        for i, device in enumerate(self.devices):
            angle = i * angle_step - math.pi / 2
            x = center.x() + orbit_radius * math.cos(angle)
            y = center.y() + orbit_radius * math.sin(angle)
            
            gradient = QLinearGradient(center.x(), center.y(), x, y)
            gradient.setColorAt(0, QColor(THEME['primary']))
            gradient.setColorAt(1, QColor(THEME['success']))
            
            pen = QPen(QBrush(gradient), 2)
            painter.setPen(pen)
            painter.drawLine(int(center.x()), int(center.y()), int(x), int(y))
            
            packet_count = 3
            for j in range(packet_count):
                t = ((self.animation_offset + j * 7) % 20) / 20.0
                packet_x = center.x() + t * (x - center.x())
                packet_y = center.y() + t * (y - center.y())
                
                dist_to_gateway = math.sqrt((packet_x - center.x())**2 + (packet_y - center.y())**2)
                dist_to_device = math.sqrt((packet_x - x)**2 + (packet_y - y)**2)
                
                if dist_to_gateway > gateway_radius and dist_to_device > 20:
                    painter.setBrush(QBrush(QColor(THEME['primary'])))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(QPointF(packet_x, packet_y), 3, 3)
                    
    def _draw_gateway(self, painter, center, radius):
        glow_color = QColor(THEME['primary'])
        glow_color.setAlpha(80)
        painter.setBrush(QBrush(glow_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center, radius + 5, radius + 5)
        
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, QColor(THEME['bg_card']))
        gradient.setColorAt(1, QColor(THEME['bg_dark']))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(THEME['primary']), 2))
        painter.drawEllipse(center, radius, radius)
        
        icon_size = int(radius // 2)
        icon_rect = QRect(int(center.x() - icon_size//2), int(center.y() - icon_size//2), icon_size, icon_size)
        painter.drawRect(icon_rect)
        painter.drawLine(icon_rect.center().x(), icon_rect.top(), icon_rect.center().x() - 5, icon_rect.top() - 8)
        painter.drawLine(icon_rect.center().x(), icon_rect.top(), icon_rect.center().x() + 5, icon_rect.top() - 8)
        
        painter.setPen(QPen(QColor(THEME['text_primary'])))
        painter.setFont(QFont(THEME['font_mono'].strip("'"), 10))
        label_rect = QRect(int(center.x() - radius), int(center.y() + radius + 5), radius * 2, 20)
        painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, "GATEWAY")
        
    def _draw_device_node(self, painter, center, radius, device, index):
        device_type = device.get('type', 'unknown')
        is_hovered = self.hovered_device == device['ip']
        is_selected = self.selected_device == device['ip']
        
        colors = {
            'pc': THEME['primary'],
            'mobile': THEME['warning'],
            'iot': '#FF9F43',
            'vm': THEME['success'],
            'pi': '#E74C3C',
            'unknown': THEME['danger']
        }
        color = colors.get(device_type, THEME['text_secondary'])
        
        if is_selected or is_hovered:
            ring_color = QColor(THEME['primary'])
            ring_color.setAlpha(100 if is_hovered else 150)
            painter.setBrush(QBrush(ring_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(center, radius + 8, radius + 8)
        
        gradient = QRadialGradient(center, radius)
        gradient.setColorAt(0, QColor(THEME['bg_card']))
        gradient.setColorAt(1, QColor(THEME['bg_dark']))
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor(color), 2))
        painter.drawEllipse(center, radius, radius)
        
        icons = {
            'pc': '🖥️',
            'mobile': '📱',
            'iot': '📡',
            'vm': '💻',
            'pi': '🥧',
            'unknown': '❓'
        }
        icon = icons.get(device_type, '❓')
        
        painter.setPen(QPen(QColor(THEME['text_primary'])))
        painter.setFont(QFont("Segoe UI Emoji", 16))
        icon_rect = QRect(int(center.x() - 15), int(center.y() - 20), 30, 30)
        painter.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, icon)
        
        painter.setFont(QFont(THEME['font_mono'].strip("'"), 10))
        ip_rect = QRect(int(center.x() - radius - 20), int(center.y() + radius + 2), radius * 2 + 40, 16)
        painter.setPen(QPen(QColor(THEME['text_secondary'])))
        painter.drawText(ip_rect, Qt.AlignmentFlag.AlignCenter, device['ip'])
        
        hostname = device.get('hostname', '')[:10]
        if hostname and hostname != 'Unknown':
            host_rect = QRect(int(center.x() - radius - 20), int(center.y() + radius + 18), radius * 2 + 40, 14)
            painter.setPen(QPen(QColor(color)))
            painter.setFont(QFont(THEME['font_mono'].strip("'"), 10))
            painter.drawText(host_rect, Qt.AlignmentFlag.AlignCenter, hostname)
            
    def _draw_legend(self, painter):
        legend_x = 10
        legend_y = self.height() - 100
        
        painter.setFont(QFont(THEME['font_mono'].strip("'"), 10))
        painter.setPen(QPen(QColor(THEME['text_primary'])))
        painter.drawText(legend_x, legend_y, "Device Types:")
        
        types = [
            ('pc', '💻 PC/Server', THEME['primary']),
            ('mobile', '📱 Mobile', THEME['warning']),
            ('iot', '📡 IoT', '#FF9F43'),
            ('unknown', '❓ Unknown', THEME['danger'])
        ]
        
        for i, (type_id, label, color) in enumerate(types):
            y_pos = legend_y + 18 + i * 16
            painter.setPen(QPen(QColor(color)))
            painter.setFont(QFont(THEME['font_mono'].strip("'"), 10))
            painter.drawText(legend_x + 10, y_pos, label)
            
    def mouseMoveEvent(self, event):
        pos = event.pos()
        old_hover = self.hovered_device
        
        self.hovered_device = None
        for ip, data in self.device_positions.items():
            center = data['center']
            radius = data['radius']
            distance = math.sqrt((pos.x() - center.x())**2 + (pos.y() - center.y())**2)
            
            if distance <= radius:
                self.hovered_device = ip
                self.setCursor(Qt.CursorShape.PointingHandCursor)
                break
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            
        if old_hover != self.hovered_device:
            self.update()
            
    def mousePressEvent(self, event):
        if self.hovered_device:
            self.selected_device = self.hovered_device
            device_data = self.device_positions[self.hovered_device]
            self.device_clicked.emit(device_data['device'])
            self.update()

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
        header_label.setFont(QFont("Arial", 16))
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

        # Navigation Sidebar (left) - using universal dark teal theme
        self.nav_sidebar = QWidget()
        self.nav_sidebar.setFixedWidth(80)
        self.nav_sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_header']};
                border-right: 1px solid {THEME['border']};
            }}
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
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    color: {THEME['text_secondary']};
                    font-size: 10px;
                    
                    border-radius: 8px;
                    text-align: center;
                }}
                QPushButton:hover {{
                    background-color: {THEME['bg_card']};
                    color: {THEME['text_primary']};
                }}
                QPushButton:checked {{
                    background-color: transparent;
                    color: {THEME['primary']};
                    border-left: 3px solid {THEME['primary']};
                }}
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
        header.setFont(QFont("Arial", 20))
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
        # Create page container first (full-size content area)
        self.page_container = QStackedWidget()
        self.page_container.setStyleSheet("background-color: transparent;")
        self.create_pages()
        
        # Create overlay container widget (this will be the central widget)
        self.overlay_container = QWidget()
        self.overlay_container.setStyleSheet("background-color: transparent;")
        
        # Use absolute positioning within the overlay container
        # Page container fills the entire overlay but with left margin for sidebar
        self.page_container.setParent(self.overlay_container)
        self.page_container.setGeometry(70, 0, self.overlay_container.width() - 70, self.overlay_container.height())
        
        # Sidebar is a child of overlay container, positioned absolutely on the left
        self.nav_sidebar = QWidget(self.overlay_container)
        self.nav_sidebar.setGeometry(0, 0, 70, self.overlay_container.height())
        self.nav_sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_header']};
            }}
        """)
        self.sidebar_expanded = False
        
        # Set the overlay container as central widget
        self.setCentralWidget(self.overlay_container)
        
        # Handle resize of overlay container
        self.overlay_container.resizeEvent = self._on_overlay_resize

        nav_layout = QVBoxLayout(self.nav_sidebar)
        nav_layout.setContentsMargins(0, 20, 0, 20)
        nav_layout.setSpacing(20)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Logo and title header container
        self.sidebar_header = QWidget()
        self.sidebar_header.setMinimumHeight(50)
        self.sidebar_header.setStyleSheet("background-color: transparent;")
        header_layout = QHBoxLayout(self.sidebar_header)
        header_layout.setContentsMargins(5, 5, 5, 5)
        header_layout.setSpacing(8)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Logo
        self.sidebar_logo = QLabel()
        self.sidebar_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            scaled_logo = logo_pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.sidebar_logo.setPixmap(scaled_logo)
        else:
            self.sidebar_logo.setText("🐺")
            self.sidebar_logo.setStyleSheet("font-size: 20px;")
        self.sidebar_logo.setFixedSize(32, 32)
        header_layout.addWidget(self.sidebar_logo)
        
        # Sidebar title (hidden when collapsed)
        self.sidebar_title = QLabel("WATCHDOG")
        self.sidebar_title.setStyleSheet(f"""
            color: {THEME['primary']};
            font-family: {THEME['font_mono']};
            font-size: 16px;
            font-weight: bold;
        """)
        self.sidebar_title.setVisible(False)
        header_layout.addWidget(self.sidebar_title, alignment=Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch()
        
        nav_layout.addWidget(self.sidebar_header)

        # Navigation buttons with icons
        nav_buttons = [
            ("DASHBOARD", "Real-time visibility and high-frequency packet monitoring", "dashboard icon.png"),
            ("FORENSIC LOG VAULT", "Translating complex metadata into human-readable advice", "log vault icon.png"),
            ("SECURITY CONTROL", "Managing the host firewall and setting AI confidence thresholds", "security control icon.png"),
            ("FORENSIC AI ASSISTANT", "A dedicated chat interface for Llama 4 Scout to provide education-active security guidance", "Ai assistant icon.png"),
            ("NETWORK TOPOLOGY", "Identifying all hardware on the LAN to resolve the visibility gap", "network topology icon.png"),
            ("SETTINGS AND PRIVACY", "Configuring Ollama and ensuring alignment with NZ Privacy Act 2020 principles", "setting icon.png")
        ]

        self.nav_button_group = []
        self.nav_button_labels = []  # Store text labels for show/hide
        self.nav_button_icons = []  # Store icon paths
        self.nav_item_containers = []  # Store container widgets
        self.nav_item_icon_labels = []  # Store icon labels
        self.nav_item_text_labels = []  # Store text labels
        
        for i, (label, tooltip, icon_file) in enumerate(nav_buttons):
            # Create container widget for icon + text
            container = QWidget()
            container.setFixedSize(70, 60)
            container.setCursor(Qt.CursorShape.PointingHandCursor)
            container.setToolTip(tooltip)
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(5, 0, 5, 0)
            container_layout.setSpacing(5)
            container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Icon label (always visible)
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_path = os.path.join(os.path.dirname(__file__), "assets", icon_file)
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            icon_label.setFixedSize(48, 48)
            container_layout.addWidget(icon_label)
            
            # Text label (hidden when collapsed)
            text_label = QLabel(label)
            text_label.setStyleSheet(f"""
                color: {THEME['text_secondary']};
                font-size: 12px;
                font-weight: bold;
                font-family: {THEME['font_mono']};
            """)
            text_label.setVisible(False)
            container_layout.addWidget(text_label)
            container_layout.addStretch()
            
            # Style container like a button
            container.setStyleSheet(f"""
                QWidget {{
                    background-color: transparent;
                    border: none;
                    border-radius: 8px;
                }}
                QWidget:hover {{
                    background-color: {THEME['bg_card']};
                }}
            """)
            
            # Make clickable
            container.mousePressEvent = lambda event, idx=i: self.switch_page(idx)
            
            nav_layout.addWidget(container)
            self.nav_button_group.append(container)
            self.nav_item_containers.append(container)
            self.nav_item_icon_labels.append(icon_label)
            self.nav_item_text_labels.append(text_label)
            
            # Store the full text and icon for later
            self.nav_button_labels.append(label)
            self.nav_button_icons.append(icon_path)

        # Set first button as active
        if self.nav_button_group:
            self._set_nav_active(0)

        # Set the overlay container as central widget
        self.setCentralWidget(self.overlay_container)

        # Enable hover events for sidebar (must be after sidebar is created)
        self.nav_sidebar.setMouseTracking(True)
        self.nav_sidebar.enterEvent = self._on_sidebar_enter
        self.nav_sidebar.leaveEvent = self._on_sidebar_leave
        
        # Timer for delayed collapse
        self.sidebar_collapse_timer = QTimer()
        self.sidebar_collapse_timer.setSingleShot(True)
        self.sidebar_collapse_timer.timeout.connect(self._contract_sidebar)

    def _on_overlay_resize(self, event):
        """Update page container and sidebar when overlay container is resized"""
        # Update page container with left margin for sidebar
        self.page_container.setGeometry(70, 0, self.overlay_container.width() - 70, self.overlay_container.height())
        # Update sidebar height
        self.nav_sidebar.setGeometry(
            self.nav_sidebar.x(), 
            0, 
            self.nav_sidebar.width(), 
            self.overlay_container.height()
        )

    def create_pages(self):
        # Page 0: Live Sentinel (Dashboard)
        self.create_live_sentinel_page()

        # Page 1: Forensic Vault
        self.create_forensic_vault_page()

        # Page 2: Autonomous Shield (placeholder)
        self.create_autonomous_shield_page()

        # Page 3: AI Mentor (placeholder)
        self.create_ai_mentor_page()

        # Page 4: Network Topology
        self.create_network_topology_page()

        # Page 5: Settings & Privacy (full implementation)
        self.create_settings_page()

    def _on_sidebar_enter(self, event):
        """Expand sidebar when mouse enters"""
        self.sidebar_collapse_timer.stop()  # Cancel any pending collapse
        if not self.sidebar_expanded:
            self._expand_sidebar()

    def _on_sidebar_leave(self, event):
        """Start timer to collapse sidebar when mouse leaves"""
        if self.sidebar_expanded:
            self.sidebar_collapse_timer.start(300)  # 300ms delay before collapsing

    def _expand_sidebar(self):
        """Expand sidebar with coordinated animation - logo moves left, titles slide in"""
        self.sidebar_expanded = True
        target_width = 280
        
        # Create parallel animation group for coordinated animation
        self.animation_group = QParallelAnimationGroup()
        
        # 1. Animate sidebar width
        sidebar_anim = QPropertyAnimation(self.nav_sidebar, b"geometry")
        sidebar_anim.setDuration(350)
        sidebar_anim.setStartValue(self.nav_sidebar.geometry())
        sidebar_anim.setEndValue(QRect(0, 0, target_width, self.overlay_container.height()))
        sidebar_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation_group.addAnimation(sidebar_anim)
        
        # 2. Show title label
        self.sidebar_title.setVisible(True)
        
        # Connect to update button text and animate text labels when animation finishes
        self.animation_group.finished.connect(self._update_sidebar_buttons)
        self.animation_group.finished.connect(self._adjust_logo_alignment)
        
        # Start animation
        self.animation_group.start()

    def _contract_sidebar(self):
        """Contract sidebar with coordinated animation"""
        self.sidebar_expanded = False
        target_width = 70
        
        # Update buttons first (remove text, show icons)
        self._update_sidebar_buttons()
        
        # Hide title
        self.sidebar_title.setVisible(False)
        
        # Create parallel animation group
        self.animation_group = QParallelAnimationGroup()
        
        # Animate sidebar width
        sidebar_anim = QPropertyAnimation(self.nav_sidebar, b"geometry")
        sidebar_anim.setDuration(350)
        sidebar_anim.setStartValue(self.nav_sidebar.geometry())
        sidebar_anim.setEndValue(QRect(0, 0, target_width, self.overlay_container.height()))
        sidebar_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation_group.addAnimation(sidebar_anim)
        
        # Connect to adjust logo alignment when done
        self.animation_group.finished.connect(self._adjust_logo_alignment)
        
        # Start animation
        self.animation_group.start()

    def toggle_sidebar(self):
        """Toggle sidebar with coordinated animation"""
        if self.sidebar_expanded:
            self._contract_sidebar()
        else:
            self._expand_sidebar()
    
    def _update_sidebar_buttons(self):
        """Update button containers based on sidebar state"""
        for i, container in enumerate(self.nav_item_containers):
            text_label = self.nav_item_text_labels[i]
            if self.sidebar_expanded:
                # Wider container, text visible
                container.setFixedSize(260, 60)
                text_label.setVisible(True)
            else:
                # Narrow container, text hidden
                container.setFixedSize(70, 60)
                text_label.setVisible(False)
    
    def _adjust_logo_alignment(self):
        """Adjust logo alignment based on sidebar state"""
        header_layout = self.sidebar_header.layout()
        if self.sidebar_expanded:
            header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        else:
            header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def _set_nav_active(self, index):
        """Set active navigation item styling"""
        for i, container in enumerate(self.nav_item_containers):
            text_label = self.nav_item_text_labels[i]
            if i == index:
                container.setStyleSheet(f"""
                    QWidget {{
                        background-color: {THEME['bg_card']};
                        border-radius: 8px;
                    }}
                """)
                text_label.setStyleSheet(f"""
                    color: {THEME['primary']};
                    font-size: 12px;
                    font-weight: bold;
                    font-family: {THEME['font_mono']};
                """)
            else:
                container.setStyleSheet(f"""
                    QWidget {{
                        background-color: transparent;
                        border: none;
                        border-radius: 8px;
                    }}
                    QWidget:hover {{
                        background-color: {THEME['bg_card']};
                    }}
                """)
                text_label.setStyleSheet(f"""
                    color: {THEME['text_secondary']};
                    font-size: 12px;
                    font-weight: bold;
                    font-family: {THEME['font_mono']};
                """)
    
    def _animate_text_labels_in(self):
        """Show text labels after expansion completes"""
        for container in self.nav_item_containers:
            container.setFixedSize(260, 60)
        for text_label in self.nav_item_text_labels:
            text_label.setVisible(True)

    def create_live_sentinel_page(self):
        """Create the main dashboard page matching hi-fi mockup design"""
        # Main content widget with dark background
        main_content = QWidget()
        main_content.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        main_layout = QVBoxLayout(main_content)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # ===== HEADER BAR =====
        header_widget = QWidget()
        header_widget.setFixedHeight(60)
        header_widget.setStyleSheet(f"""
            background-color: {THEME['bg_header']};
            border-bottom: 1px solid {THEME['border']};
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(15)
        
        # Dog/Wolf logo icon
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            scaled_logo = logo_pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        else:
            logo_label.setText("🐺")
            logo_label.setStyleSheet("font-size: 32px;")
        logo_label.setFixedSize(48, 48)
        header_layout.addWidget(logo_label)
        
        # Title
        title_label = QLabel("WatchDog AI")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {THEME['primary']};")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        main_layout.addWidget(header_widget)
        
        # ===== TOP ROW: Three Metric Cards =====
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        # System Health Card
        health_card = self._create_metric_card("System Health", SystemHealthGauge())
        cards_layout.addWidget(health_card)
        
        # Live Traffic Card
        traffic_card = self._create_metric_card("Live Traffic", LiveTrafficWidget())
        cards_layout.addWidget(traffic_card)
        
        # Risk Analysis Card
        risk_card = self._create_metric_card("Risk Analysis", RiskAnalysisGauge())
        cards_layout.addWidget(risk_card)
        
        main_layout.addLayout(cards_layout)
        
        # ===== BOTTOM ROW: Table and AI Panel =====
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
        # Left side: Traffic Table
        table_container = self._create_traffic_table_section()
        bottom_layout.addWidget(table_container, stretch=2)
        
        # Right side: Forensic Assistant Panel
        self.forensic_panel = ForensicAssistantPanel()
        bottom_layout.addWidget(self.forensic_panel, stretch=1)
        
        main_layout.addLayout(bottom_layout, stretch=1)
        
        self.page_container.addWidget(main_content)
        
    def _create_metric_card(self, title, widget):
        """Create a styled metric card with title"""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 20)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            color: {THEME['text_primary']};
            font-family: {THEME['font_mono']};
            font-size: 14px;
            font-weight: bold;
        """)
        layout.addWidget(title_label)
        
        # Widget (gauge or chart)
        widget.setMinimumHeight(180)
        layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return card
        
    def _create_traffic_table_section(self):
        """Create traffic table with teal header and Refresh button"""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Table with teal header
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Source IP", "Destination IP", "Protocol", "Length", "Confidence\nScore", "Action"
        ])
        
        # Make table stretch to fill container
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Stretch all columns to fill width
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)
        
        # Make rows fill vertical space and stretch
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(40)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Teal header styling with improved sizing
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                gridline-color: {THEME['border']};
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {THEME['border']};
            }}
            QTableWidget::item:selected {{
                background-color: {THEME['primary']};
                color: {THEME['bg_dark']};
            }}
            QHeaderView::section {{
                background-color: {THEME['primary']};
                color: white;
                font-family: {THEME['font_mono']};
                font-size: 12px;
                font-weight: bold;
                padding: 12px;
                border: none;
            }}
            QHeaderView::section:first {{
                border-top-left-radius: 8px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 8px;
            }}
        """)
        
        layout.addWidget(self.table, stretch=1)
        
        # Refresh button (centered)
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedSize(100, 35)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                font-family: {THEME['font_mono']};
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {THEME['secondary']};
            }}
        """)
        refresh_btn.clicked.connect(self.update_ui)
        btn_layout.addWidget(refresh_btn)
        
        layout.addWidget(btn_container)
        
        return container

    def create_forensic_vault_page(self):
        """Create Forensic Vault page with dark teal theme"""
        vault_page = QWidget()
        vault_page.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        vault_layout = QVBoxLayout(vault_page)
        vault_layout.setContentsMargins(40, 40, 40, 40)
        vault_layout.setSpacing(20)

        # Header
        vault_header = QLabel("FORENSIC VAULT")
        vault_header.setFont(QFont(THEME['font_mono'].strip("'"), 28))
        vault_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vault_header.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 20px;")
        vault_layout.addWidget(vault_header)

        # Subtitle
        vault_subtitle = QLabel("Translating complex metadata into human-readable advice")
        vault_subtitle.setFont(QFont(THEME['font_mono'].strip("'"), 14))
        vault_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vault_subtitle.setStyleSheet(f"color: {THEME['text_secondary']}; margin-bottom: 30px;")
        vault_layout.addWidget(vault_subtitle)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search Flagged Incidents:")
        search_label.setStyleSheet(f"color: {THEME['text_primary']}; font-family: {THEME['font_mono']};")
        self.vault_search = QLineEdit()
        self.vault_search.setPlaceholderText("Enter IP address, protocol, or threat type...")
        self.vault_search.setStyleSheet(f"""
            QLineEdit {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
                color: {THEME['text_primary']};
                padding: 8px;
                font-family: {THEME['font_mono']};
            }}
            QLineEdit:focus {{
                border: 1px solid {THEME['primary']};
            }}
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
        self.vault_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 15px;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                gridline-color: {THEME['border']};
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {THEME['border']};
            }}
            QTableWidget::item:selected {{
                background-color: {THEME['primary']};
                color: {THEME['bg_dark']};
            }}
            QHeaderView::section {{
                background-color: {THEME['primary']};
                color: {THEME['bg_dark']};
                border: none;
                padding: 12px;
                font-weight: bold;
                font-family: {THEME['font_mono']};
            }}
            QHeaderView::section:first {{
                border-top-left-radius: 15px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 15px;
            }}
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
        self.vault_table.verticalHeader().setDefaultSectionSize(55)
        self.vault_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.vault_table.itemDoubleClicked.connect(self.show_forensic_analysis)
        vault_layout.addWidget(self.vault_table)

        # Refresh button
        vault_refresh_btn = QPushButton("Load Flagged Incidents")
        vault_refresh_btn.clicked.connect(self.load_flagged_incidents)
        vault_refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {THEME['primary']};
                border: 2px solid {THEME['primary']};
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-family: {THEME['font_mono']};
            }}
            QPushButton:hover {{
                background-color: rgba(0, 180, 216, 0.2);
            }}
        """)
        vault_layout.addWidget(vault_refresh_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.page_container.addWidget(vault_page)

    def create_placeholder_page(self, title, description):
        # Placeholder page for future implementation with universal dark teal theme
        page = QWidget()
        page.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        page_title = QLabel(title)
        page_title.setFont(QFont(THEME['font_mono'].strip("'"), 28))
        page_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page_title.setStyleSheet(f"color: {THEME['primary']};")
        layout.addWidget(page_title)

        page_desc = QLabel(description)
        page_desc.setFont(QFont(THEME['font_mono'].strip("'"), 14))
        page_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page_desc.setStyleSheet(f"color: {THEME['text_secondary']};")
        layout.addWidget(page_desc)

        coming_soon = QLabel("Coming Soon...")
        coming_soon.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        coming_soon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        coming_soon.setStyleSheet(f"color: {THEME['primary']}; margin-top: 50px;")
        layout.addWidget(coming_soon)

        self.page_container.addWidget(page)

    def create_settings_page(self):
        """Create Settings & Privacy page with QListWidget navigation and QStackedWidget content"""
        settings_page = QWidget()
        settings_page.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        
        # Main horizontal layout
        main_layout = QHBoxLayout(settings_page)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # LEFT: Navigation List
        nav_widget = QWidget()
        nav_widget.setFixedWidth(200)
        nav_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_header']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
            }}
        """)
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(10, 20, 10, 20)
        nav_layout.setSpacing(10)
        
        # Settings title
        settings_title = QLabel("SETTINGS")
        settings_title.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        settings_title.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 20px;")
        settings_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(settings_title)
        
        # Navigation list
        self.settings_nav = QListWidget()
        self.settings_nav.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 13px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 12px 15px;
                border-radius: 8px;
                margin: 2px 0;
            }}
            QListWidget::item:selected {{
                background-color: {THEME['primary']};
                color: {THEME['bg_dark']};
            }}
            QListWidget::item:hover {{
                background-color: {THEME['bg_card']};
            }}
        """)
        self.settings_nav.addItem("Network")
        self.settings_nav.addItem("AI Brain")
        self.settings_nav.addItem("Security")
        self.settings_nav.addItem("Privacy")
        nav_layout.addWidget(self.settings_nav)
        nav_layout.addStretch()
        
        main_layout.addWidget(nav_widget)
        
        # RIGHT: Content Stack
        self.settings_content = QStackedWidget()
        self.settings_content.setStyleSheet(f"""
            QStackedWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
            }}
        """)
        
        # === NETWORK TAB ===
        network_tab = QWidget()
        network_layout = QVBoxLayout(network_tab)
        network_layout.setContentsMargins(30, 30, 30, 30)
        network_layout.setSpacing(20)
        
        network_header = QLabel("Network Settings")
        network_header.setFont(QFont(THEME['font_mono'].strip("'"), 20))
        network_header.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 20px;")
        network_layout.addWidget(network_header)
        
        # Active Interface dropdown
        interface_container = QWidget()
        interface_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        interface_layout = QVBoxLayout(interface_container)
        
        interface_label = QLabel("Active Interface")
        interface_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        interface_label.setStyleSheet(f"color: {THEME['text_primary']};")
        interface_layout.addWidget(interface_label)
        
        self.interface_combo = QComboBox()
        self.interface_combo.addItems(["eth0", "wlan0", "lo", "en0", "Wi-Fi", "Ethernet"])
        self.interface_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 8px;
                font-family: {THEME['font_mono']};
                min-width: 200px;
            }}
            QComboBox::drop-down {{
                border: none;
                padding-right: 10px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {THEME['primary']};
            }}
            QComboBox QAbstractItemView {{
                background-color: {THEME['bg_card']};
                color: {THEME['text_primary']};
                selection-background-color: {THEME['primary']};
                selection-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
            }}
        """)
        interface_layout.addWidget(self.interface_combo)
        
        network_layout.addWidget(interface_container)
        
        # Network range input
        range_container = QWidget()
        range_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        range_layout = QVBoxLayout(range_container)
        
        range_label = QLabel("Network Range")
        range_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        range_label.setStyleSheet(f"color: {THEME['text_primary']};")
        range_layout.addWidget(range_label)
        
        self.settings_range_input = QLineEdit("172.16.40.0/24")
        self.settings_range_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 8px;
                font-family: {THEME['font_mono']};
            }}
            QLineEdit:focus {{
                border: 1px solid {THEME['primary']};
            }}
        """)
        range_layout.addWidget(self.settings_range_input)
        
        network_layout.addWidget(range_container)
        network_layout.addStretch()
        
        self.settings_content.addWidget(network_tab)
        
        # === AI BRAIN TAB ===
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)
        ai_layout.setContentsMargins(30, 30, 30, 30)
        ai_layout.setSpacing(20)
        
        ai_header = QLabel("AI Brain Settings")
        ai_header.setFont(QFont(THEME['font_mono'].strip("'"), 20))
        ai_header.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 20px;")
        ai_layout.addWidget(ai_header)
        
        # Explanation Detail slider
        explanation_container = QWidget()
        explanation_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        explanation_layout = QVBoxLayout(explanation_container)
        
        explanation_label = QLabel("Explanation Detail")
        explanation_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        explanation_label.setStyleSheet(f"color: {THEME['text_primary']};")
        explanation_layout.addWidget(explanation_label)
        
        self.explanation_slider = QSlider(Qt.Orientation.Horizontal)
        self.explanation_slider.setRange(1, 5)
        self.explanation_slider.setValue(3)
        self.explanation_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {THEME['border']};
                height: 8px;
                background: {THEME['bg_card']};
                border-radius: 4px;
            }}
            QSlider::sub-page:horizontal {{
                background: #00D1FF;
                border: 1px solid #00D1FF;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: #00D1FF;
                border: 2px solid {THEME['bg_dark']};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
        """)
        
        # Slider labels
        slider_labels = QHBoxLayout()
        for label in ["Minimal", "Brief", "Standard", "Detailed", "Verbose"]:
            lbl = QLabel(label)
            lbl.setFont(QFont(THEME['font_mono'].strip("'"), 9))
            lbl.setStyleSheet(f"color: {THEME['text_secondary']};")
            slider_labels.addWidget(lbl)
        ai_layout.addWidget(explanation_container)
        
        # Local Model toggle
        local_model_container = QWidget()
        local_model_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        local_model_layout = QHBoxLayout(local_model_container)
        
        local_model_label = QLabel("Use Local Model")
        local_model_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        local_model_label.setStyleSheet(f"color: {THEME['text_primary']};")
        local_model_layout.addWidget(local_model_label)
        local_model_layout.addStretch()
        
        self.local_model_toggle = QCheckBox()
        self.local_model_toggle.setChecked(True)
        self.local_model_toggle.setStyleSheet(f"""
            QCheckBox {{
                spacing: 5px;
            }}
            QCheckBox::indicator {{
                width: 40px;
                height: 20px;
                border-radius: 10px;
                background: {THEME['bg_card']};
                border: 2px solid {THEME['border']};
            }}
            QCheckBox::indicator:checked {{
                background: #00D1FF;
                border: 2px solid #00D1FF;
            }}
            QCheckBox::indicator::handle {{
                background: white;
                border-radius: 8px;
                width: 16px;
                height: 16px;
                margin: 2px;
            }}
        """)
        local_model_layout.addWidget(self.local_model_toggle)
        
        ai_layout.addWidget(local_model_container)
        ai_layout.addStretch()
        
        self.settings_content.addWidget(ai_tab)
        
        # === SECURITY TAB ===
        security_tab = QWidget()
        security_layout = QVBoxLayout(security_tab)
        security_layout.setContentsMargins(30, 30, 30, 30)
        security_layout.setSpacing(20)
        
        security_header = QLabel("Security Settings")
        security_header.setFont(QFont(THEME['font_mono'].strip("'"), 20))
        security_header.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 20px;")
        security_layout.addWidget(security_header)
        
        # Sensitivity slider
        sensitivity_container = QWidget()
        sensitivity_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        sensitivity_layout = QVBoxLayout(sensitivity_container)
        
        sensitivity_label = QLabel("Detection Sensitivity")
        sensitivity_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        sensitivity_label.setStyleSheet(f"color: {THEME['text_primary']};")
        sensitivity_layout.addWidget(sensitivity_label)
        
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setRange(0, 100)
        self.sensitivity_slider.setValue(75)
        self.sensitivity_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {THEME['border']};
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {THEME['success']}, stop:0.5 {THEME['warning']}, stop:1 {THEME['danger']});
                border-radius: 4px;
            }}
            QSlider::sub-page:horizontal {{
                background: #00D1FF;
                border: 1px solid #00D1FF;
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: #00D1FF;
                border: 2px solid {THEME['bg_dark']};
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }}
        """)
        sensitivity_layout.addWidget(self.sensitivity_slider)
        
        # Sensitivity labels
        sens_labels = QHBoxLayout()
        relaxed_lbl = QLabel("Relaxed")
        relaxed_lbl.setStyleSheet(f"color: {THEME['success']}; font-family: {THEME['font_mono']};")
        balanced_lbl = QLabel("Balanced")
        balanced_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        balanced_lbl.setStyleSheet(f"color: {THEME['warning']}; font-family: {THEME['font_mono']};")
        aggressive_lbl = QLabel("Aggressive")
        aggressive_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        aggressive_lbl.setStyleSheet(f"color: {THEME['danger']}; font-family: {THEME['font_mono']};")
        sens_labels.addWidget(relaxed_lbl)
        sens_labels.addWidget(balanced_lbl)
        sens_labels.addWidget(aggressive_lbl)
        sensitivity_layout.addLayout(sens_labels)
        
        security_layout.addWidget(sensitivity_container)
        
        # Auto-block toggle
        autoblock_container = QWidget()
        autoblock_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        autoblock_layout = QHBoxLayout(autoblock_container)
        
        autoblock_label = QLabel("Auto-Block Threats")
        autoblock_label.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        autoblock_label.setStyleSheet(f"color: {THEME['text_primary']};")
        autoblock_layout.addWidget(autoblock_label)
        autoblock_layout.addStretch()
        
        self.autoblock_toggle = QCheckBox()
        self.autoblock_toggle.setChecked(True)
        self.autoblock_toggle.setStyleSheet(f"""
            QCheckBox {{
                spacing: 5px;
            }}
            QCheckBox::indicator {{
                width: 40px;
                height: 20px;
                border-radius: 10px;
                background: {THEME['bg_card']};
                border: 2px solid {THEME['border']};
            }}
            QCheckBox::indicator:checked {{
                background: #00D1FF;
                border: 2px solid #00D1FF;
            }}
        """)
        autoblock_layout.addWidget(self.autoblock_toggle)
        
        security_layout.addWidget(autoblock_container)
        security_layout.addStretch()
        
        self.settings_content.addWidget(security_tab)
        
        # === PRIVACY TAB ===
        privacy_tab = QWidget()
        privacy_layout = QVBoxLayout(privacy_tab)
        privacy_layout.setContentsMargins(30, 30, 30, 30)
        privacy_layout.setSpacing(20)
        
        privacy_header = QLabel("Privacy Settings")
        privacy_header.setFont(QFont(THEME['font_mono'].strip("'"), 20))
        privacy_header.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 20px;")
        privacy_layout.addWidget(privacy_header)
        
        privacy_info = QLabel("NZ Privacy Act 2020 Compliance\n\nYour data is processed locally.\nNo data is sent to external servers.")
        privacy_info.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        privacy_info.setStyleSheet(f"color: {THEME['text_secondary']};")
        privacy_info.setWordWrap(True)
        privacy_layout.addWidget(privacy_info)
        privacy_layout.addStretch()
        
        self.settings_content.addWidget(privacy_tab)
        
        # Connect navigation to content
        self.settings_nav.currentRowChanged.connect(self.settings_content.setCurrentIndex)
        
        main_layout.addWidget(self.settings_content, stretch=1)
        
        self.page_container.addWidget(settings_page)

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
        # Update active navigation styling
        self._set_nav_active(index)
        
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
            action_widget.setStyleSheet("background-color: transparent;")
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 2, 2, 2)
            action_layout.setSpacing(8)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Block Source IP button
            block_src_btn = QPushButton("Block Source")
            block_src_btn.setFixedSize(95, 32)
            block_src_btn.setStyleSheet("""
                QPushButton {
                    background-color: #B91C1C;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #DC2626;
                }
            """)
            block_src_btn.clicked.connect(lambda checked, ip=src_ip: self.block_ip_from_vault(ip))
            action_layout.addWidget(block_src_btn)
            
            # Block Destination IP button
            block_dst_btn = QPushButton("Block Destination")
            block_dst_btn.setFixedSize(105, 32)
            block_dst_btn.setStyleSheet("""
                QPushButton {
                    background-color: #06B6D4;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 11px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #0891B2;
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
        title.setFont(QFont("Courier New", 16))
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
        """Create Autonomous Shield page with firewall management - using universal dark teal theme"""
        shield_page = QWidget()
        shield_page.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        
        # Main layout
        main_layout = QVBoxLayout(shield_page)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Header
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_header']};
                border-bottom: 1px solid {THEME['border']};
                border-radius: 12px;
            }}
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(40, 20, 40, 20)
        
        title_section = QVBoxLayout()
        title_section.setSpacing(5)
        
        shield_title = QLabel("AUTONOMOUS SHIELD")
        shield_title.setFont(QFont(THEME['font_mono'].strip("'"), 24))
        shield_title.setStyleSheet(f"color: {THEME['danger']}; margin: 0;")
        title_section.addWidget(shield_title)
        
        shield_subtitle = QLabel("Firewall Management & AI Confidence Control")
        shield_subtitle.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        shield_subtitle.setStyleSheet(f"color: {THEME['text_secondary']}; margin: 0;")
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
        blocked_header.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        blocked_header.setStyleSheet(f"color: {THEME['danger']}; margin-bottom: 10px;")
        left_layout.addWidget(blocked_header)
        
        # Blocked IPs list with dark teal theme
        self.blocked_list_widget = QListWidget()
        self.blocked_list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 10px;
                font-family: {THEME['font_mono']};
                font-size: 14px;
                color: {THEME['text_primary']};
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {THEME['border']};
                border-radius: 5px;
                margin: 2px 0;
            }}
            QListWidget::item:selected {{
                background-color: {THEME['danger']};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: rgba(255, 107, 107, 0.2);
            }}
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
        unblock_btn.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        unblock_btn.setStyleSheet(f"""
            QPushButton {{
                background: linear-gradient(135deg, {THEME['danger']}, #FF5252);
                border: 2px solid {THEME['danger']};
                border-radius: 10px;
                color: white;
                font-weight: bold;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background: linear-gradient(135deg, #FF5252, #FF3838);
                border: 2px solid #FF5252;
            }}
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
        confidence_header.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        confidence_header.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 10px;")
        right_layout.addWidget(confidence_header)
        
        # Confidence slider container
        confidence_container = QWidget()
        confidence_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        confidence_layout = QVBoxLayout(confidence_container)
        confidence_layout.setSpacing(15)
        
        # Current threshold display
        self.confidence_label = QLabel("Current Threshold: 75%")
        self.confidence_label.setFont(QFont(THEME['font_mono'].strip("'"), 14))
        self.confidence_label.setStyleSheet(f"color: {THEME['primary']}; margin: 0;")
        self.confidence_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        confidence_layout.addWidget(self.confidence_label)
        
        # Confidence slider with theme colors
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(75)
        self.confidence_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {THEME['border']};
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 {THEME['danger']}, stop:0.5 {THEME['warning']}, stop:1 {THEME['success']});
                border-radius: 4px;
            }}
            QSlider::handle:horizontal {{
                background: {THEME['primary']};
                border: 2px solid {THEME['border']};
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }}
        """)
        self.confidence_slider.valueChanged.connect(self.update_confidence_threshold)
        confidence_layout.addWidget(self.confidence_slider)
        
        # Threshold labels
        labels_layout = QHBoxLayout()
        labels_layout.setSpacing(0)
        
        relaxed_label = QLabel("Relaxed")
        relaxed_label.setFont(QFont(THEME['font_mono'].strip("'"), 10))
        relaxed_label.setStyleSheet(f"color: {THEME['danger']};")
        
        balanced_label = QLabel("Balanced")
        balanced_label.setFont(QFont(THEME['font_mono'].strip("'"), 10))
        balanced_label.setStyleSheet(f"color: {THEME['warning']};")
        balanced_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        aggressive_label = QLabel("Aggressive")
        aggressive_label.setFont(QFont(THEME['font_mono'].strip("'"), 10))
        aggressive_label.setStyleSheet(f"color: {THEME['success']};")
        aggressive_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        labels_layout.addWidget(relaxed_label)
        labels_layout.addStretch()
        labels_layout.addWidget(balanced_label)
        labels_layout.addStretch()
        labels_layout.addWidget(aggressive_label)
        confidence_layout.addLayout(labels_layout)
        
        # Mode description
        mode_desc = QLabel("Lower values = More blocks (Aggressive)\nHigher values = Fewer false positives (Relaxed)")
        mode_desc.setFont(QFont(THEME['font_mono'].strip("'"), 10))
        mode_desc.setStyleSheet(f"color: {THEME['text_secondary']}; margin: 10px 0;")
        mode_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mode_desc.setWordWrap(True)
        confidence_layout.addWidget(mode_desc)
        
        right_layout.addWidget(confidence_container)
        
        # Statistics
        stats_container = QWidget()
        stats_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setSpacing(10)
        
        stats_title = QLabel("BLOCKING STATISTICS")
        stats_title.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        stats_title.setStyleSheet(f"color: {THEME['warning']}; margin: 0;")
        stats_layout.addWidget(stats_title)
        
        self.total_blocked_label = QLabel(f"Total Blocked: 4")
        self.total_blocked_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        self.total_blocked_label.setStyleSheet(f"color: {THEME['text_primary']}; margin: 5px 0;")
        stats_layout.addWidget(self.total_blocked_label)
        
        self.auto_blocked_label = QLabel(f"Auto-Blocked: 4")
        self.auto_blocked_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        self.auto_blocked_label.setStyleSheet(f"color: {THEME['success']}; margin: 5px 0;")
        stats_layout.addWidget(self.auto_blocked_label)
        
        self.manual_blocked_label = QLabel("Manual: 0")
        self.manual_blocked_label.setFont(QFont(THEME['font_mono'].strip("'"), 11))
        self.manual_blocked_label.setStyleSheet(f"color: {THEME['primary']}; margin: 5px 0;")
        stats_layout.addWidget(self.manual_blocked_label)
        
        # Initialize manual block counter
        self.manual_block_count = 0
        
        right_layout.addWidget(stats_container)
        
        content_layout.addWidget(left_section, stretch=2)
        content_layout.addWidget(right_section, stretch=1)
        
        main_layout.addWidget(content_area, stretch=1)
        
        self.page_container.addWidget(shield_page)
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
        """Create AI Mentor page as a Forensic Analysis Hub with dark teal theme"""
        # AI Mentor page widget
        mentor_page = QWidget()
        mentor_page.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        
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
        status_bar.setStyleSheet(f"""
            QFrame {{
                background: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
                color: {THEME['primary']};
            }}
        """)
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(15, 5, 15, 5)
        
        # Sentinel Pulse Icon
        pulse_icon = QLabel("●")
        pulse_icon.setStyleSheet(f"""
            QLabel {{
                color: {THEME['primary']};
                font-size: 16px;
                
            }}
        """)
        status_layout.addWidget(pulse_icon)
        
        # Status Text
        status_text = QLabel("SYSTEM STATUS: MONITORING | AGENT: LLAMA 4 SCOUT")
        status_text.setStyleSheet(f"""
            QLabel {{
                color: {THEME['primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                
            }}
        """)
        status_layout.addWidget(status_text)
        status_layout.addStretch()
        
        chat_layout.addWidget(status_bar)

        # Chat Scroll Area
        self.mentor_chat_area = QScrollArea()
        self.mentor_chat_area.setWidgetResizable(True)
        self.mentor_chat_area.setFrameShape(QFrame.Shape.NoFrame)
        self.mentor_chat_area.setStyleSheet(f"""
            QScrollArea {{
                background: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
            }}
        """)
        self.mentor_chat_area.setContentsMargins(20, 10, 20, 10)

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
        btn1.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {THEME['border']};
                color: {THEME['text_primary']};
                padding: 8px 16px;
                border-radius: 6px;
                font-family: {THEME['font_mono']};
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: rgba(0, 180, 216, 0.1);
                border: 1px solid {THEME['primary']};
            }}
        """)
        btn1.clicked.connect(lambda: self.quick_question("Analyze the last 5 minutes of network activity"))
        actions_layout.addWidget(btn1)
        
        # Ghost Button 2
        btn2 = QPushButton("Scan Local Devices")
        btn2.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {THEME['border']};
                color: {THEME['text_primary']};
                padding: 8px 16px;
                border-radius: 6px;
                font-family: {THEME['font_mono']};
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: rgba(0, 180, 216, 0.1);
                border: 1px solid {THEME['primary']};
            }}
        """)
        btn2.clicked.connect(lambda: self.quick_question("Scan all local devices for security vulnerabilities"))
        actions_layout.addWidget(btn2)
        
        # Ghost Button 3
        btn3 = QPushButton("Explain Risk Level")
        btn3.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid {THEME['border']};
                color: {THEME['text_primary']};
                padding: 8px 16px;
                border-radius: 6px;
                font-family: {THEME['font_mono']};
                font-size: 11px;
            }}
            QPushButton:hover {{
                background: rgba(0, 180, 216, 0.1);
                border: 1px solid {THEME['primary']};
            }}
        """)
        btn3.clicked.connect(lambda: self.quick_question("Explain the current network risk level"))
        actions_layout.addWidget(btn3)
        
        actions_layout.addStretch()
        chat_layout.addWidget(quick_actions)

        # Input Section
        input_container = QFrame()
        input_container.setFixedHeight(50)
        input_container.setStyleSheet(f"""
            QFrame {{
                background: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
            }}
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(100, 5, 100, 5)
        
        self.mentor_input = QLineEdit()
        self.mentor_input.setPlaceholderText("Ask me anything about network security...")
        self.mentor_input.setStyleSheet(f"""
            QLineEdit {{
                background: {THEME['bg_dark']};
                color: {THEME['text_primary']};
                border: 1px solid {THEME['border']};
                padding: 8px;
                border-radius: 6px;
                font-family: {THEME['font_mono']};
            }}
            QLineEdit:focus {{
                border: 2px solid {THEME['primary']};
            }}
        """)

        self.mentor_send_btn = QPushButton("SEND")
        self.mentor_send_btn.setStyleSheet(f"""
            QPushButton {{
                background: rgba(0, 180, 216, 0.2);
                border: 1px solid {THEME['primary']};
                color: {THEME['primary']};
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: rgba(0, 180, 216, 0.3);
            }}
        """)

        input_layout.addWidget(self.mentor_input)
        input_layout.addWidget(self.mentor_send_btn)
        chat_layout.addWidget(input_container)

        # Add chat container to main layout (70%)
        main_layout.addWidget(chat_container, stretch=7)

        # RIGHT SIDE - Live Diagnostics (30%)
        diagnostics_container = QFrame()
        diagnostics_container.setFixedWidth(400)
        diagnostics_container.setStyleSheet(f"""
            QFrame {{
                background: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
            }}
        """)
        diagnostics_layout = QVBoxLayout(diagnostics_container)
        diagnostics_layout.setContentsMargins(20, 20, 20, 20)
        diagnostics_layout.setSpacing(15)

        # Diagnostics Header
        diag_header = QLabel("LIVE DIAGNOSTICS")
        diag_header.setStyleSheet(f"""
            QLabel {{
                color: {THEME['primary']};
                font-family: {THEME['font_mono']};
                font-size: 14px;
                font-weight: bold;
                border-bottom: 1px solid {THEME['border']};
                padding-bottom: 10px;
            }}
        """)
        diagnostics_layout.addWidget(diag_header)

        # Threat Level Meter
        threat_frame = QFrame()
        threat_frame.setStyleSheet(f"""
            QFrame {{
                background: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        threat_layout = QVBoxLayout(threat_frame)
        
        threat_title = QLabel("THREAT LEVEL")
        threat_title.setStyleSheet(f"""
            QLabel {{
                color: {THEME['danger']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        threat_layout.addWidget(threat_title)
        
        self.threat_level_label = QLabel("LOW")
        self.threat_level_label.setStyleSheet(f"""
            QLabel {{
                color: {THEME['success']};
                font-family: {THEME['font_mono']};
                font-size: 24px;
                font-weight: bold;
            }}
        """)
        threat_layout.addWidget(self.threat_level_label)
        
        diagnostics_layout.addWidget(threat_frame)

        # Network Activity
        activity_frame = QFrame()
        activity_frame.setStyleSheet(f"""
            QFrame {{
                background: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        activity_layout = QVBoxLayout(activity_frame)
        
        activity_title = QLabel("NETWORK ACTIVITY")
        activity_title.setStyleSheet(f"""
            QLabel {{
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        activity_layout.addWidget(activity_title)
        
        self.activity_text = QLabel("Monitoring...\nNo suspicious activity detected")
        self.activity_text.setStyleSheet(f"""
            QLabel {{
                color: {THEME['text_secondary']};
                font-family: {THEME['font_mono']};
                font-size: 10px;
            }}
        """)
        self.activity_text.setWordWrap(True)
        activity_layout.addWidget(self.activity_text)
        
        diagnostics_layout.addWidget(activity_frame)

        # Recent Alerts
        alerts_frame = QFrame()
        alerts_frame.setStyleSheet(f"""
            QFrame {{
                background: {THEME['bg_dark']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        alerts_layout = QVBoxLayout(alerts_frame)
        
        alerts_title = QLabel("RECENT ALERTS")
        alerts_title.setStyleSheet(f"""
            QLabel {{
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        alerts_layout.addWidget(alerts_title)
        
        self.alerts_text = QLabel("No alerts in last hour")
        self.alerts_text.setStyleSheet(f"""
            QLabel {{
                color: {THEME['text_secondary']};
                font-family: {THEME['font_mono']};
                font-size: 10px;
            }}
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
        
        # Process instant response
        QTimer.singleShot(1000, lambda: self.display_instant_response(message))

    def create_insight_card(self, header, content):
        """Create an XAI Insight Card with glassmorphism styling"""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(30, 30, 30, 0.8);
                border: none;
                border-radius: 12px;
                margin: 8px 0;
                padding: 0;
            }
        """)
        # card.setMaximumWidth(600)  # Removed constraint to fill chat box
        
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(8, 8, 8, 8)
        card_layout.setSpacing(8)
        
        # Header
        header_label = QLabel(f"[{header}]")
        header_label.setStyleSheet("""
            QLabel {
                color: #00D4FF;
                font-size: 11px;
                
                text-transform: uppercase;
            }
        """)
        card_layout.addWidget(header_label)
        
        # Content
        content_label = QLabel(content)
        content_label.setStyleSheet("""
            QLabel {
                color: #E0E0E0;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        content_label.setWordWrap(True)
        content_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
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
            message_label.setFont(QFont("Courier New", 11))
            message_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            # message_label.setMaximumWidth(600)  # Removed constraint to fill chat box
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

    def create_network_topology_page(self):
        """Create Network Topology Discovery page with device scanning - using universal dark teal theme"""
        topology_page = QWidget()
        topology_page.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        topology_layout = QVBoxLayout(topology_page)
        topology_layout.setContentsMargins(20, 20, 20, 20)
        topology_layout.setSpacing(20)
        
        # Header Section
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        header_layout.setSpacing(10)
        
        topology_title = QLabel("NETWORK TOPOLOGY DISCOVERY")
        topology_title.setFont(QFont(THEME['font_mono'].strip("'"), 28))
        topology_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        topology_title.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 10px;")
        header_layout.addWidget(topology_title)
        
        topology_subtitle = QLabel("Scan your LAN to discover all connected devices and identify potential shadow IT")
        topology_subtitle.setFont(QFont(THEME['font_mono'].strip("'"), 14))
        topology_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        topology_subtitle.setStyleSheet(f"color: {THEME['text_secondary']}; margin-bottom: 20px;")
        header_layout.addWidget(topology_subtitle)
        
        # Scan Controls
        scan_controls = QHBoxLayout()
        scan_controls.setSpacing(15)
        
        self.scan_btn = QPushButton("🔍 SCAN NETWORK")
        self.scan_btn.setFont(QFont(THEME['font_mono'].strip("'"), 14))
        self.scan_btn.setStyleSheet(f"""
            QPushButton {{
                background: {THEME['primary']};
                border: none;
                border-radius: 10px;
                color: {THEME['bg_dark']};
                padding: 15px 30px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {THEME['secondary']};
            }}
            QPushButton:disabled {{
                background: #666666;
                color: #999999;
            }}
        """)
        print("[DEBUG] Connecting scan button...")
        self.scan_btn.clicked.connect(self.scan_network_devices)
        print("[DEBUG] Adding scan button to layout...")
        scan_controls.addWidget(self.scan_btn)
        print("[DEBUG] Scan button added!")
        
        # Network Range Input
        range_layout = QHBoxLayout()
        range_label = QLabel("Network Range:")
        range_label.setStyleSheet(f"color: {THEME['text_primary']}; font-family: {THEME['font_mono']}; font-size: 12px;")
        self.network_range_input = QLineEdit("172.16.40.0/24")
        self.network_range_input.setStyleSheet(f"""
            QLineEdit {{
                background: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 6px;
                color: {THEME['text_primary']};
                padding: 8px;
                font-family: {THEME['font_mono']};
                min-width: 150px;
            }}
            QLineEdit:focus {{
                border: 1px solid {THEME['primary']};
            }}
        """)
        range_layout.addWidget(range_label)
        range_layout.addWidget(self.network_range_input)
        range_layout.addStretch()
        scan_controls.addLayout(range_layout)
        
        # Status Label
        self.scan_status = QLabel("Ready to scan")
        self.scan_status.setStyleSheet(f"color: {THEME['success']}; font-family: {THEME['font_mono']}; font-size: 12px;")
        scan_controls.addWidget(self.scan_status)
        
        scan_controls.addStretch()
        header_layout.addLayout(scan_controls)
        
        # Stats Bar
        stats_widget = QWidget()
        stats_widget.setStyleSheet(f"""
            QWidget {{
                background: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 10px;
            }}
        """)
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setSpacing(40)
        
        self.total_devices_label = QLabel("Total Devices: 0")
        self.total_devices_label.setStyleSheet(f"color: {THEME['text_primary']}; font-family: {THEME['font_mono']}; font-size: 14px; ")
        stats_layout.addWidget(self.total_devices_label)
        
        self.pc_count_label = QLabel("💻 PCs: 0")
        self.pc_count_label.setStyleSheet(f"color: {THEME['primary']}; font-family: {THEME['font_mono']}; font-size: 14px;")
        stats_layout.addWidget(self.pc_count_label)
        
        self.iot_count_label = QLabel("📱 Mobile/IoT: 0")
        self.iot_count_label.setStyleSheet(f"color: {THEME['warning']}; font-family: {THEME['font_mono']}; font-size: 14px;")
        stats_layout.addWidget(self.iot_count_label)
        
        self.unknown_count_label = QLabel("❓ Unknown: 0")
        self.unknown_count_label.setStyleSheet(f"color: {THEME['danger']}; font-family: {THEME['font_mono']}; font-size: 14px;")
        stats_layout.addWidget(self.unknown_count_label)
        
        stats_layout.addStretch()
        header_layout.addWidget(stats_widget)
        
        topology_layout.addWidget(header_widget)
        
        # Main Content Area - Split View
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Device List
        device_list_widget = QWidget()
        device_list_layout = QVBoxLayout(device_list_widget)
        device_list_layout.setContentsMargins(0, 0, 0, 0)
        
        device_list_header = QLabel("DISCOVERED DEVICES")
        device_list_header.setStyleSheet(f"color: {THEME['primary']}; font-family: {THEME['font_mono']}; font-size: 16px;  margin-bottom: 10px;")
        device_list_layout.addWidget(device_list_header)
        
        self.device_list = QListWidget()
        self.device_list.setStyleSheet(f"""
            QListWidget {{
                background: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 10px;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
            }}
            QListWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {THEME['border']};
                border-radius: 5px;
                margin: 2px 0;
            }}
            QListWidget::item:selected {{
                background: {THEME['primary']};
                color: {THEME['bg_dark']};
            }}
            QListWidget::item:hover {{
                background: rgba(0, 180, 216, 0.2);
            }}
        """)
        self.device_list.itemClicked.connect(self.show_device_details)
        device_list_layout.addWidget(self.device_list)
        
        content_splitter.addWidget(device_list_widget)
        
        # Right: Device Details & Visualization
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Network Visualization (Cisco-style radial topology)
        viz_header = QLabel("NETWORK VISUALIZATION")
        viz_header.setStyleSheet(f"color: {THEME['primary']}; font-family: {THEME['font_mono']}; font-size: 16px;  margin-bottom: 10px;")
        right_layout.addWidget(viz_header)
        
        self.network_viz = NetworkTopologyWidget()
        self.network_viz.device_clicked.connect(self._on_topology_device_clicked)
        right_layout.addWidget(self.network_viz)
        
        # Device Details Panel
        details_header = QLabel("DEVICE DETAILS")
        details_header.setStyleSheet(f"color: {THEME['primary']}; font-family: {THEME['font_mono']}; font-size: 16px;  margin-top: 20px; margin-bottom: 10px;")
        right_layout.addWidget(details_header)
        
        self.device_details = QTextEdit()
        self.device_details.setReadOnly(True)
        self.device_details.setStyleSheet(f"""
            QTextEdit {{
                background: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                line-height: 1.6;
            }}
        """)
        self.device_details.setPlaceholderText("Select a device from the list to view detailed information...")
        self.device_details.setMaximumHeight(200)
        right_layout.addWidget(self.device_details)
        
        content_splitter.addWidget(right_panel)
        content_splitter.setSizes([400, 600])
        
        topology_layout.addWidget(content_splitter, stretch=1)
        
        self.page_container.addWidget(topology_page)
        
        # Initialize discovered devices storage
        self.discovered_devices = {}
    
    def scan_network_devices(self):
        """Scan network for connected devices using ARP requests"""
        print("[DEBUG] Scan button clicked!")
        self.scan_btn.setEnabled(False)
        self.scan_status.setText("🔍 Scanning network...")
        self.scan_status.setStyleSheet("color: #FFD93D; font-family: 'Courier New', monospace; font-size: 12px;")
        self.device_list.clear()
        
        # Clear topology visualization
        self.network_viz.set_devices([])
        
        print("[DEBUG] Starting background thread...")
        # Run scan in background thread
        threading.Thread(target=self._perform_network_scan, daemon=True).start()
    
    def _perform_network_scan(self):
        """Perform actual network scanning"""
        try:
            import scapy.all as scapy
            from scapy.layers.l2 import ARP, Ether
            
            network_range = self.network_range_input.text().strip()
            print(f"[DEBUG] Starting scan of {network_range}")
            
            # Check if running as root (required for scapy) - Unix only
            import os
            is_windows = os.name == 'nt'
            is_root = hasattr(os, 'geteuid') and os.geteuid() == 0
            
            # Show demo devices on Windows, non-root Unix, or in layout-only mode
            if (is_windows or not is_root) or self.layout_only:
                print("[DEBUG] Demo/Limited mode - showing demo devices")
                # Show demo devices for testing without root
                demo_devices = [
                    {'ip': '192.168.1.1', 'mac': '00:11:22:33:44:55', 'hostname': 'Router-Gateway', 'vendor': 'Netgear', 'type': 'pc'},
                    {'ip': '192.168.1.5', 'mac': 'A4:B1:C1:22:33:44', 'hostname': 'iPhone-BPU', 'vendor': 'Apple', 'type': 'mobile'},
                    {'ip': '192.168.1.10', 'mac': '64:16:66:77:88:99', 'hostname': 'Alexa-Echo', 'vendor': 'Amazon', 'type': 'iot'},
                    {'ip': '192.168.1.15', 'mac': '08:00:27:AB:CD:EF', 'hostname': 'Ubuntu-VM', 'vendor': 'VirtualBox', 'type': 'vm'},
                    {'ip': '192.168.1.20', 'mac': 'B8:27:EB:12:34:56', 'hostname': 'Raspberry-Pi', 'vendor': 'Raspberry Pi', 'type': 'pi'},
                    {'ip': '192.168.1.100', 'mac': 'AA:BB:CC:DD:EE:FF', 'hostname': 'Unknown-Device', 'vendor': 'Unknown Vendor', 'type': 'unknown'},
                ]
                print("[DEBUG] Demo mode - updating UI directly")
                # Store devices and schedule UI update from main thread
                self._pending_devices = demo_devices
                QTimer.singleShot(0, self._apply_demo_devices)
                return
            
            # Create ARP request packet
            print(f"[DEBUG] Creating ARP packet for {network_range}")
            arp = ARP(pdst=network_range)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp
            print(f"[DEBUG] Packet created: {packet.summary()}")
            
            print(f"[DEBUG] Sending ARP requests...")
            # Send packet and capture responses
            try:
                result = scapy.srp(packet, timeout=3, verbose=0)[0]
                print(f"[DEBUG] Received {len(result)} responses")
            except Exception as scan_err:
                print(f"[DEBUG] Scapy srp error: {scan_err}")
                result = []
            
            if len(result) == 0:
                print("[DEBUG] No devices found - network may be empty or firewall blocking ARP")
            
            devices = []
            for sent, received in result:
                print(f"[DEBUG] Found device: {received.psrc} - {received.hwsrc}")
                device_info = {
                    'ip': received.psrc,
                    'mac': received.hwsrc,
                    'hostname': self._get_hostname(received.psrc),
                    'vendor': self._get_vendor(received.hwsrc),
                    'type': self._categorize_device(received.hwsrc, received.psrc)
                }
                devices.append(device_info)
            
            print(f"[DEBUG] Total devices found: {len(devices)}")
            # Update UI from main thread
            self._pending_devices = devices
            QTimer.singleShot(0, self._apply_real_devices)
            
        except Exception as e:
            import traceback
            print(f"[DEBUG] Scan error: {str(e)}")
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")
            QTimer.singleShot(0, lambda: self._scan_error(str(e)))
    
    def _get_hostname(self, ip):
        """Try to get hostname from IP"""
        try:
            import socket
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except:
            return "Unknown"
    
    def _get_vendor(self, mac):
        """Get vendor from MAC address (simplified)"""
        mac_prefix = mac[:8].upper()
        vendors = {
            "00:50:56": "VMware",
            "08:00:27": "VirtualBox",
            "B8:27:EB": "Raspberry Pi",
            "DC:A6:32": "Raspberry Pi",
            "B8:27:EB": "Raspberry Pi",
            "00:17:88": "Philips Hue",
            "18:B4:30": "Nest Labs",
            "64:16:66": "Amazon",
            "A4:77:33": "Amazon",
            "AC:63:BE": "Amazon",
            "00:04:20": "Google",
            "60:03:08": "Google",
            "D4:F5:47": "Google",
            "00:26:BB": "Apple",
            "60:33:4B": "Apple",
            "AC:DE:48": "Apple",
            "D0:23:DB": "Apple",
            "A4:B1:C1": "Apple",
            "AC:BC:32": "Apple",
            "68:D7:9A": "Samsung",
            "24:4B:03": "Samsung",
            "C0:97:27": "Samsung",
        }
        return vendors.get(mac_prefix, "Unknown Vendor")
    
    def _categorize_device(self, mac, ip):
        """Categorize device type based on MAC and hostname"""
        mac_upper = mac.upper()
        hostname_upper = self._get_hostname(ip).upper()
        
        # Mobile devices
        mobile_keywords = ["PHONE", "MOBILE", "IPHONE", "ANDROID", "IPAD", "TABLET"]
        if any(kw in hostname_upper for kw in mobile_keywords):
            return "mobile"
        
        # Check MAC prefixes for common mobile vendors
        mobile_prefixes = ["00:26:BB", "60:33:4B", "AC:DE:48", "D0:23:DB", "A4:B1:C1", "AC:BC:32", "68:D7:9A", "24:4B:03", "C0:97:27"]
        if any(mac_upper.startswith(prefix) for prefix in mobile_prefixes):
            return "mobile"
        
        # IoT devices
        iot_keywords = ["SMART", "HUE", "NEST", "RING", "ALEXA", "ECHO", "CAMERA", "IOT"]
        if any(kw in hostname_upper for kw in iot_keywords):
            return "iot"
        
        # Check MAC prefixes for common IoT vendors
        iot_prefixes = ["00:17:88", "18:B4:30", "64:16:66", "A4:77:33", "AC:63:BE"]
        if any(mac_upper.startswith(prefix) for prefix in iot_prefixes):
            return "iot"
        
        # VMs
        vm_prefixes = ["00:50:56", "08:00:27"]
        if any(mac_upper.startswith(prefix) for prefix in vm_prefixes):
            return "vm"
        
        # Raspberry Pi
        pi_prefixes = ["B8:27:EB", "DC:A6:32"]
        if any(mac_upper.startswith(prefix) for prefix in pi_prefixes):
            return "pi"
        
        return "unknown"
    
    def _apply_demo_devices(self):
        """Apply demo devices to UI from main thread"""
        print("[DEBUG] _apply_demo_devices called")
        if hasattr(self, '_pending_devices'):
            self._update_device_list(self._pending_devices)
            self.scan_status.setText("⚠️ Demo mode (run with sudo for real scan)")
            self.scan_status.setStyleSheet("color: #FFD93D; font-family: 'Courier New', monospace; font-size: 12px;")
            self.scan_btn.setEnabled(True)
            print("[DEBUG] Demo devices applied to UI")
    
    def _apply_real_devices(self):
        """Apply real scan devices to UI from main thread"""
        print("[DEBUG] _apply_real_devices called")
        if hasattr(self, '_pending_devices'):
            self._update_device_list(self._pending_devices)
            print("[DEBUG] Real devices applied to UI")
    
    def _update_device_list(self, devices):
        """Update the device list UI"""
        print(f"[DEBUG] _update_device_list called with {len(devices)} devices")
        self.discovered_devices = {}
        
        # Count devices by type
        counts = {'total': 0, 'pc': 0, 'mobile': 0, 'iot': 0, 'vm': 0, 'pi': 0, 'unknown': 0}
        
        for device in devices:
            counts['total'] += 1
            device_type = device['type']
            counts[device_type] = counts.get(device_type, 0) + 1
            
            # Create list item
            icon = self._get_device_icon(device_type)
            item_text = f"{icon} {device['ip']} - {device['hostname']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, device)
            self.device_list.addItem(item)
            self.discovered_devices[device['ip']] = device
        
        # Update stats
        self.total_devices_label.setText(f"Total Devices: {counts['total']}")
        self.pc_count_label.setText(f"💻 PCs/Servers: {counts.get('vm', 0) + counts.get('pi', 0)}")
        self.iot_count_label.setText(f"📱 Mobile/IoT: {counts.get('mobile', 0) + counts.get('iot', 0)}")
        self.unknown_count_label.setText(f"❓ Unknown: {counts['unknown']}")
        
        # Update visualization
        self._update_network_viz(devices)
        
        self.scan_btn.setEnabled(True)
        self.scan_status.setText(f"✅ Scan complete - {counts['total']} devices found")
        self.scan_status.setStyleSheet("color: #6BCF7F; font-family: 'Courier New', monospace; font-size: 12px;")
    
    def _get_device_icon(self, device_type):
        """Get icon for device type"""
        icons = {
            'pc': '💻',
            'mobile': '📱',
            'iot': '📡',
            'vm': '🖥️',
            'pi': '🥧',
            'unknown': '❓'
        }
        return icons.get(device_type, '❓')
    
    def _update_network_viz(self, devices):
        """Update network visualization using Cisco-style topology widget"""
        self.network_viz.set_devices(devices)
    
    def _on_topology_device_clicked(self, device):
        """Handle device click from topology visualization"""
        # Update device details panel with selected device
        self.device_details.setHtml(self._format_device_details(device))
    
    def show_device_details(self, item):
        """Show detailed information for selected device"""
        device = item.data(Qt.ItemDataRole.UserRole)
        if not device:
            return
        
        details_text = f"""
<b>Device Information</b>
━━━━━━━━━━━━━━━━━━━━━━━

<b>IP Address:</b>     {device['ip']}
<b>MAC Address:</b>   {device['mac']}
<b>Hostname:</b>      {device['hostname']}
<b>Vendor:</b>         {device['vendor']}
<b>Device Type:</b>    {device['type'].upper()}

<b>Security Analysis</b>
━━━━━━━━━━━━━━━━━━━━━━━

• Device is actively responding to ARP requests
• MAC address is {'well-known' if device['vendor'] != 'Unknown Vendor' else 'unknown - potential shadow IT'}
• Classification: {self._get_device_risk_assessment(device)}

<b>Recommendations</b>
━━━━━━━━━━━━━━━━━━━━━━━

{self._get_device_recommendations(device)}
        """
        
        self.device_details.setHtml(details_text)
    
    def _get_device_risk_assessment(self, device):
        """Get security risk assessment for device"""
        if device['vendor'] == "Unknown Vendor":
            return "⚠️ MEDIUM RISK - Unknown device vendor"
        if device['type'] == 'iot':
            return "⚠️ LOW-MEDIUM RISK - IoT device, ensure firmware is updated"
        if device['type'] == 'mobile':
            return "✅ LOW RISK - Personal mobile device"
        return "✅ LOW RISK - Known device type"
    
    def _get_device_recommendations(self, device):
        """Get security recommendations for device"""
        if device['vendor'] == "Unknown Vendor":
            return "• Investigate this device - unknown vendor could indicate rogue device\n• Consider blocking MAC if not authorized\n• Check network access logs for this IP"
        if device['type'] == 'iot':
            return "• Verify IoT device is on isolated network segment\n• Check for latest security updates\n• Review device permissions and network access"
        if device['type'] == 'mobile':
            return "• Ensure device is using WPA3 WiFi\n• Verify mobile device management (MDM) policies\n• Check for unauthorized network access"
        return "• Verify device is authorized on network\n• Ensure proper network segmentation\n• Monitor traffic patterns from this device"
    
    def _format_device_details(self, device):
        """Format device details as HTML"""
        return f"""
<b>Device Information</b>
━━━━━━━━━━━━━━━━━━━━━━━

<b>IP Address:</b>     {device['ip']}
<b>MAC Address:</b>   {device['mac']}
<b>Hostname:</b>      {device['hostname']}
<b>Vendor:</b>         {device['vendor']}
<b>Device Type:</b>    {device['type'].upper()}

<b>Security Analysis</b>
━━━━━━━━━━━━━━━━━━━━━━━

• Device is actively responding to ARP requests
• MAC address is {'well-known' if device['vendor'] != 'Unknown Vendor' else 'unknown - potential shadow IT'}
• Classification: {self._get_device_risk_assessment(device)}

<b>Recommendations</b>
━━━━━━━━━━━━━━━━━━━━━━━

{self._get_device_recommendations(device)}
        """
    
    def _scan_error(self, error_msg):
        """Handle scan errors"""
        self.scan_btn.setEnabled(True)
        self.scan_status.setText(f"❌ Scan failed: {error_msg}")
        self.scan_status.setStyleSheet("color: #FF6B6B; font-family: 'Courier New', monospace; font-size: 12px;")
        
        # Show error in device list
        error_item = QListWidgetItem(f"⚠️ Error: {error_msg}")
        error_item.setForeground(Qt.GlobalColor.red)
        self.device_list.addItem(error_item)

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

    def display_instant_response(self, message):
        """Display instant AI response"""
        # Remove typing indicator
        if hasattr(self, 'typing_indicator') and self.typing_indicator is not None:
            try:
                self.mentor_chat_layout.removeWidget(self.typing_indicator)
                self.typing_indicator.deleteLater()
                self.typing_indicator = None
            except:
                pass
        
        # Generate and display response
        response = self.generate_instant_response(message)
        self.add_mentor_message("AI Mentor", response)

    def generate_instant_response(self, message):
        """Generate instant AI response based on keywords"""
        msg_lower = message.lower()
        
        # Greeting responses
        if msg_lower in ["hi", "hello", "hey", "greetings", "good morning", "good afternoon"]:
            return random.choice([
                "Hello! I'm your AI cybersecurity mentor. How can I help you today?",
                "Hi there! Ready to assist with your security questions. What's on your mind?",
                "Greetings! I'm here to help with network security and cyber defense topics.",
                "Hello! Ask me anything about cybersecurity, and I'll provide expert guidance."
            ])
        
        # Network segmentation
        elif "network" in msg_lower and ("segment" in msg_lower or "segmentation" in msg_lower):
            return """Network segmentation is a critical security architecture that divides your network into smaller, isolated segments or zones.

**Key Benefits:**
- **Containment**: Limits lateral movement for attackers
- **Access Control**: Enforces least privilege principles  
- **Performance**: Reduces broadcast traffic
- **Compliance**: Helps meet regulatory requirements

**Implementation Strategy:**
1. **VLAN Segmentation**: Separate by department/function
2. **Firewall Zones**: Create DMZ, internal, trusted zones
3. **Micro-segmentation**: Zero-trust approach for critical assets
4. **Network Access Control**: 802.1X authentication for all segments

**Best Practices:**
- Document all segmentation rules
- Monitor inter-segment traffic
- Regular security audits
- Implement proper routing between segments

Would you like specific guidance on implementing segmentation for your network?"""

        # DDoS attacks
        elif "ddos" in msg_lower or "distributed denial" in msg_lower:
            return """DDoS (Distributed Denial of Service) attacks overwhelm your systems with traffic from multiple sources.

**Attack Types:**
- **Volumetric**: Saturates bandwidth (UDP floods, ICMP floods)
- **Protocol**: Exploits protocol weaknesses (SYN floods, ACK floods)
- **Application**: Targets application layer (HTTP floods, slowloris)

**Defense Strategy:**
1. **Detection**: Monitor traffic patterns, baseline behavior
2. **Mitigation**: Rate limiting, connection tracking, blackholing
3. **Scrubbing**: Clean traffic before it reaches your network
4. **CDN**: Distribute traffic across multiple endpoints

**Prevention Measures:**
- Deploy WAF with DDoS protection
- Configure network devices for rate limiting
- Have incident response plan ready
- Consider cloud-based DDoS protection services

Need help setting up DDoS protection for your infrastructure?"""

        # Port scanning
        elif "port scan" in msg_lower or "port scanning" in msg_lower:
            return """Port scanning is a reconnaissance technique used to discover open ports and services on your network.

**Common Scan Types:**
- **TCP Connect Scan**: Full three-way handshake
- **SYN Scan**: Half-open scanning (stealthy)
- **UDP Scan**: Checks for open UDP ports
- **Xmas Scan**: Uses FIN, PSH, URG flags

**Detection Methods:**
1. **IDS/IPS**: Signature-based detection
2. **Log Analysis**: Monitor connection patterns
3. **Network Monitoring**: Unusual port access attempts
4. **Honeypots**: Decoy systems to catch scanners

**Prevention Strategies:**
- Close unnecessary ports and services
- Implement firewall rules
- Use port knocking techniques
- Deploy intrusion detection systems
- Regular vulnerability assessments

**Response Protocol:**
1. Identify scanning source
2. Block malicious IPs
3. Document the incident
4. Strengthen defenses

Would you like help configuring your firewall to prevent port scanning?"""

        # Firewall hardening
        elif "firewall" in msg_lower and ("harden" in msg_lower or "hardening" in msg_lower or "secure" in msg_lower):
            return """Firewall hardening is essential for robust network security. Here's a comprehensive approach:

**Basic Configuration:**
- **Default Deny**: Block all traffic by default, allow only necessary
- **Rule Cleanup**: Remove unused rules and services
- **Logging**: Enable comprehensive logging for all rules
- **Regular Updates**: Keep firewall firmware/software current

**Advanced Hardening:**
1. **Application Layer Filtering**: Deep packet inspection
2. **Geo-blocking**: Block traffic from high-risk regions
3. **Rate Limiting**: Prevent brute force and DDoS
4. **Intrusion Prevention**: Integrated IPS capabilities

**Best Practices:**
- **Rule Documentation**: Maintain clear rule documentation
- **Regular Audits**: Review and update rules quarterly
- **Backup Configuration**: Save working configurations
- **Test Changes**: Validate in lab environment first

**Monitoring:**
- Real-time traffic analysis
- Alert on rule violations
- Performance metrics
- Security event correlation

Need specific firewall configuration guidance for your environment?"""

        # Default response
        else:
            return random.choice([
                "That's an interesting cybersecurity question. Let me provide some guidance on this topic. Could you be more specific about what aspect you'd like to explore?",
                "I can help with that security topic. To give you the most relevant advice, could you provide more details about your specific situation or concerns?",
                "Great question about cybersecurity! I'd be happy to help. What particular aspect of this topic interests you most - prevention, detection, or response?",
                "I can assist with that security area. For the most accurate guidance, tell me more about your current setup or what you're trying to achieve."
            ])

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
