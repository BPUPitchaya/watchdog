"""
System Tray Icon for Background Monitoring
Provides system tray icon with menu for background monitoring control
"""

from PyQt6.QtWidgets import (QSystemTrayIcon, QMenu, QWidget, QVBoxLayout, 
                             QLabel, QPushButton, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QIcon, QAction
from typing import Optional


class TraySignals(QObject):
    """Signals for system tray events"""
    show_window = pyqtSignal()
    hide_window = pyqtSignal()
    start_monitoring = pyqtSignal()
    stop_monitoring = pyqtSignal()
    quit_application = pyqtSignal()
    toggle_notifications = pyqtSignal(bool)


class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon for background monitoring"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = TraySignals()
        self.monitoring_active = False
        self.notifications_enabled = True
        
        self.setup_tray_icon()
        self.setup_context_menu()
    
    def setup_tray_icon(self):
        """Setup the tray icon"""
        # Create a simple icon (in production, use actual icon file)
        self.setIcon(self.create_icon())
        self.setToolTip("WATCHDOG Network Security Monitor")
        
        # Show tray icon
        self.show()
    
    def create_icon(self) -> QIcon:
        """Create tray icon (placeholder - use actual icon in production)"""
        # In production, load from file: QIcon('assets/tray_icon.png')
        # For now, create a simple colored icon
        from PyQt6.QtGui import QPixmap, QPainter, QColor
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        
        # Draw shield-like shape
        color = QColor('#3B82F6') if not self.monitoring_active else QColor('#6BCF7F')
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(4, 4, 24, 24)
        
        # Draw "W" for Watchdog
        painter.setBrush(QColor('#FFFFFF'))
        painter.drawEllipse(12, 12, 8, 8)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def setup_context_menu(self):
        """Setup context menu for tray icon"""
        menu = QMenu()
        
        # Show/Hide window
        self.show_action = QAction("Show Dashboard", self)
        self.show_action.triggered.connect(self.signals.show_window.emit)
        menu.addAction(self.show_action)
        
        self.hide_action = QAction("Hide to Tray", self)
        self.hide_action.triggered.connect(self.signals.hide_window.emit)
        menu.addAction(self.hide_action)
        
        menu.addSeparator()
        
        # Start/Stop monitoring
        self.start_action = QAction("Start Monitoring", self)
        self.start_action.triggered.connect(self.signals.start_monitoring.emit)
        menu.addAction(self.start_action)
        
        self.stop_action = QAction("Stop Monitoring", self)
        self.stop_action.triggered.connect(self.signals.stop_monitoring.emit)
        self.stop_action.setEnabled(False)
        menu.addAction(self.stop_action)
        
        menu.addSeparator()
        
        # Toggle notifications
        self.notifications_action = QAction("Enable Notifications", self)
        self.notifications_action.setCheckable(True)
        self.notifications_action.setChecked(True)
        self.notifications_action.triggered.connect(self.toggle_notifications)
        menu.addAction(self.notifications_action)
        
        menu.addSeparator()
        
        # Quit
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.signals.quit_application.emit)
        menu.addAction(quit_action)
        
        self.setContextMenu(menu)
        self.update_menu_state()
    
    def update_menu_state(self):
        """Update menu state based on monitoring status"""
        self.start_action.setEnabled(not self.monitoring_active)
        self.stop_action.setEnabled(self.monitoring_active)
        
        # Update tooltip
        status = "Active" if self.monitoring_active else "Inactive"
        self.setToolTip(f"WATCHDOG - Monitoring: {status}")
        
        # Update icon
        self.setIcon(self.create_icon())
    
    def set_monitoring_active(self, active: bool):
        """Set monitoring status"""
        self.monitoring_active = active
        self.update_menu_state()
        
        # Show notification
        if self.notifications_enabled:
            self.show_notification(
                "WATCHDOG",
                f"Monitoring {'started' if active else 'stopped'}"
            )
    
    def toggle_notifications(self, enabled: bool):
        """Toggle notifications"""
        self.notifications_enabled = enabled
        self.signals.toggle_notifications.emit(enabled)
    
    def show_notification(self, title: str, message: str):
        """Show system tray notification"""
        if self.supportsMessages():
            self.showMessage(title, message, QSystemTrayIcon.MessageIcon.Information, 3000)
    
    def show_critical_notification(self, title: str, message: str):
        """Show critical notification"""
        if self.supportsMessages():
            self.showMessage(title, message, QSystemTrayIcon.MessageIcon.Critical, 5000)
    
    def show_warning_notification(self, title: str, message: str):
        """Show warning notification"""
        if self.supportsMessages():
            self.showMessage(title, message, QSystemTrayIcon.MessageIcon.Warning, 4000)


class TrayControlPanel(QWidget):
    """Control panel for system tray settings"""
    
    def __init__(self, tray_icon: SystemTrayIcon, parent=None):
        super().__init__(parent)
        self.tray_icon = tray_icon
        self.setup_ui()
    
    def setup_ui(self):
        """Setup control panel UI"""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("System Tray Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(title)
        
        # Enable tray icon
        self.enable_tray = QCheckBox("Enable System Tray Icon")
        self.enable_tray.setChecked(True)
        self.enable_tray.toggled.connect(self.toggle_tray)
        layout.addWidget(self.enable_tray)
        
        # Minimize to tray
        self.minimize_to_tray = QCheckBox("Minimize to System Tray")
        self.minimize_to_tray.setChecked(True)
        layout.addWidget(self.minimize_to_tray)
        
        # Close to tray
        self.close_to_tray = QCheckBox("Close to System Tray")
        self.close_to_tray.setChecked(False)
        layout.addWidget(self.close_to_tray)
        
        # Notifications
        self.enable_notifications = QCheckBox("Enable Tray Notifications")
        self.enable_notifications.setChecked(True)
        self.enable_notifications.toggled.connect(self.toggle_notifications)
        layout.addWidget(self.enable_notifications)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Style
        self.setStyleSheet("""
            QWidget {
                background-color: #0F1318;
                color: #E0E0E0;
            }
            QLabel {
                color: #E0E0E0;
                font-family: 'Segoe UI', sans-serif;
            }
            QCheckBox {
                color: #E0E0E0;
                font-family: 'Segoe UI', sans-serif;
                spacing: 10px;
            }
        """)
    
    def toggle_tray(self, enabled: bool):
        """Toggle tray icon visibility"""
        if enabled:
            self.tray_icon.show()
        else:
            self.tray_icon.hide()
    
    def toggle_notifications(self, enabled: bool):
        """Toggle notifications"""
        self.tray_icon.toggle_notifications(enabled)
