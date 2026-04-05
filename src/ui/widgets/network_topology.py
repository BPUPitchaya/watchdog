import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPointF, QRect
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush, QRadialGradient, QLinearGradient

from src.ui.theme import THEME


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
