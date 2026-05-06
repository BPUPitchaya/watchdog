import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QByteArray, QRect
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QRadialGradient
from PyQt6.QtSvgWidgets import QSvgWidget

from src.ui.theme import THEME


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
        # self.smooth_timer.start(100)  # Disabled for performance
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
