"""
Desktop Notifications for Security Alerts
Provides desktop notification system for security events
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class NotificationType:
    """Notification types"""

    THREAT = "threat"
    ANOMALY = "anomaly"
    SYSTEM = "system"
    INFO = "info"


class NotificationPriority:
    """Notification priority levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Notification:
    """Single notification object"""

    def __init__(
        self,
        title: str,
        message: str,
        notification_type: str = NotificationType.INFO,
        priority: str = NotificationPriority.MEDIUM,
        timestamp: Optional[str] = None,
    ):
        self.title = title
        self.message = message
        self.type = notification_type
        self.priority = priority
        self.timestamp = timestamp or datetime.now().isoformat()
        self.read = False

    def to_dict(self) -> Dict:
        """Convert notification to dictionary"""
        return {
            "title": self.title,
            "message": self.message,
            "type": self.type,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "read": self.read,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Notification":
        """Create notification from dictionary"""
        return cls(
            data["title"], data["message"], data["type"], data["priority"], data["timestamp"]
        )


class NotificationSignals(QObject):
    """Signals for notification events"""

    notification_added = pyqtSignal(Notification)
    notification_read = pyqtSignal(str)
    all_notifications_read = pyqtSignal()
    settings_changed = pyqtSignal(dict)


class NotificationManager(QObject):
    """Manages desktop notifications for security alerts"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.signals = NotificationSignals()
        self.notifications: List[Notification] = []
        self.settings = self.load_settings()
        self.max_notifications = 100
        self.notification_file = "notifications.json"

        self.load_notifications()

    def load_settings(self) -> Dict:
        """Load notification settings"""
        default_settings = {
            "enabled": True,
            "sound_enabled": True,
            "threat_alerts": True,
            "anomaly_alerts": True,
            "system_alerts": False,
            "popup_duration": 5000,
            "max_stored": 100,
            "priority_filter": "all",  # all, medium, high, critical
        }

        try:
            with open("notification_settings.json") as f:
                loaded = json.load(f)
                return {**default_settings, **loaded}
        except:
            return default_settings

    def save_settings(self) -> bool:
        """Save notification settings"""
        try:
            with open("notification_settings.json", "w") as f:
                json.dump(self.settings, f, indent=2)
            self.signals.settings_changed.emit(self.settings)
            return True
        except Exception as e:
            print(f"Error saving notification settings: {e}")
            return False

    def load_notifications(self) -> None:
        """Load saved notifications"""
        try:
            if not self.notifications:
                with open(self.notification_file) as f:
                    data = json.load(f)
                    self.notifications = [Notification.from_dict(n) for n in data]
        except:
            self.notifications = []

    def save_notifications(self) -> bool:
        """Save notifications to file"""
        try:
            # Keep only recent notifications
            recent = self.notifications[-self.settings["max_stored"] :]
            with open(self.notification_file, "w") as f:
                json.dump([n.to_dict() for n in recent], f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving notifications: {e}")
            return False

    def add_notification(
        self,
        title: str,
        message: str,
        notification_type: str = NotificationType.INFO,
        priority: str = NotificationPriority.MEDIUM,
    ) -> None:
        """Add a new notification"""
        if not self.settings["enabled"]:
            return

        # Check if this type is enabled
        if notification_type == NotificationType.THREAT and not self.settings["threat_alerts"]:
            return
        if notification_type == NotificationType.ANOMALY and not self.settings["anomaly_alerts"]:
            return
        if notification_type == NotificationType.SYSTEM and not self.settings["system_alerts"]:
            return

        # Check priority filter
        priority_levels = {
            NotificationPriority.LOW: 0,
            NotificationPriority.MEDIUM: 1,
            NotificationPriority.HIGH: 2,
            NotificationPriority.CRITICAL: 3,
        }
        filter_levels = {"all": 0, "medium": 1, "high": 2, "critical": 3}

        if priority_levels[priority] < filter_levels[self.settings["priority_filter"]]:
            return

        # Create notification
        notification = Notification(title, message, notification_type, priority)
        self.notifications.append(notification)

        # Limit stored notifications
        if len(self.notifications) > self.settings["max_stored"]:
            self.notifications = self.notifications[-self.settings["max_stored"] :]

        # Save and emit signal
        self.save_notifications()
        self.signals.notification_added.emit(notification)

    def mark_as_read(self, timestamp: str) -> None:
        """Mark notification as read"""
        for notification in self.notifications:
            if notification.timestamp == timestamp:
                notification.read = True
                self.signals.notification_read.emit(timestamp)
                self.save_notifications()
                break

    def mark_all_as_read(self) -> None:
        """Mark all notifications as read"""
        for notification in self.notifications:
            notification.read = True
        self.signals.all_notifications_read.emit()
        self.save_notifications()

    def get_unread_count(self) -> int:
        """Get count of unread notifications"""
        return sum(1 for n in self.notifications if not n.read)

    def get_notifications(self, unread_only: bool = False) -> List[Notification]:
        """Get notifications"""
        if unread_only:
            return [n for n in self.notifications if not n.read]
        return self.notifications

    def clear_notifications(self) -> None:
        """Clear all notifications"""
        self.notifications = []
        self.save_notifications()

    def add_threat_alert(self, threat_type: str, source_ip: str, details: str = "") -> None:
        """Add a security threat alert"""
        message = f"Threat detected: {threat_type}\nSource: {source_ip}"
        if details:
            message += f"\nDetails: {details}"

        self.add_notification(
            f"Security Threat: {threat_type}",
            message,
            NotificationType.THREAT,
            NotificationPriority.HIGH,
        )

    def add_anomaly_alert(self, anomaly_type: str, details: str = "") -> None:
        """Add a network anomaly alert"""
        message = f"Network anomaly detected: {anomaly_type}"
        if details:
            message += f"\nDetails: {details}"

        self.add_notification(
            f"Network Anomaly: {anomaly_type}",
            message,
            NotificationType.ANOMALY,
            NotificationPriority.MEDIUM,
        )

    def add_system_alert(self, event: str, details: str = "") -> None:
        """Add a system event alert"""
        message = f"System event: {event}"
        if details:
            message += f"\nDetails: {details}"

        self.add_notification(
            f"System Event: {event}", message, NotificationType.SYSTEM, NotificationPriority.LOW
        )


class NotificationWidget(QWidget):
    """Widget for displaying notifications"""

    def __init__(self, notification_manager: NotificationManager, parent=None):
        super().__init__(parent)
        self.manager = notification_manager
        self.setup_ui()
        self.connect_signals()
        self.refresh_notifications()

    def setup_ui(self):
        """Setup notification widget UI"""
        layout = QVBoxLayout()

        # Header
        header = QHBoxLayout()
        title = QLabel("Security Alerts")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #E0E0E0;")
        header.addWidget(title)

        self.unread_count = QLabel("0 unread")
        self.unread_count.setStyleSheet("color: #6BCF7F;")
        header.addWidget(self.unread_count)

        header.addStretch()

        mark_read_btn = QPushButton("Mark All Read")
        mark_read_btn.clicked.connect(self.mark_all_read)
        header.addWidget(mark_read_btn)

        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all)
        header.addWidget(clear_btn)

        layout.addLayout(header)

        # Notification list
        self.notification_list = QListWidget()
        self.notification_list.setStyleSheet("""
            QListWidget {
                background-color: #1A1F26;
                border: 1px solid #2A3038;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 10px;
                margin: 2px;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #2A3038;
            }
        """)
        layout.addWidget(self.notification_list)

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
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)

    def connect_signals(self):
        """Connect notification manager signals"""
        self.manager.signals.notification_added.connect(self.on_notification_added)
        self.manager.signals.notification_read.connect(self.on_notification_read)
        self.manager.signals.all_notifications_read.connect(self.on_all_read)

    def refresh_notifications(self):
        """Refresh notification list"""
        self.notification_list.clear()
        notifications = self.manager.get_notifications()

        for notification in reversed(notifications):
            item = QListWidgetItem()

            # Style based on priority
            priority_colors = {
                NotificationPriority.LOW: "#6B7280",
                NotificationPriority.MEDIUM: "#F59E0B",
                NotificationPriority.HIGH: "#EF4444",
                NotificationPriority.CRITICAL: "#DC2626",
            }

            color = priority_colors.get(notification.priority, "#6B7280")
            background = "#2A3038" if notification.read else "#1E3A5F"

            text = f"<b>{notification.title}</b><br>"
            text += f"<span style='color: {color};'>[{notification.priority.upper()}]</span> "
            text += f"{notification.message}<br>"
            text += (
                f"<span style='color: #6B7280; font-size: 11px;'>{notification.timestamp}</span>"
            )

            item.setText(text)
            item.setBackground(QColor(background))
            self.notification_list.addItem(item)

        self.unread_count.setText(f"{self.manager.get_unread_count()} unread")

    def on_notification_added(self, notification: Notification):
        """Handle new notification"""
        self.refresh_notifications()

    def on_notification_read(self, timestamp: str):
        """Handle notification read"""
        self.refresh_notifications()

    def on_all_read(self):
        """Handle all notifications read"""
        self.refresh_notifications()

    def mark_all_read(self):
        """Mark all notifications as read"""
        self.manager.mark_all_as_read()

    def clear_all(self):
        """Clear all notifications"""
        self.manager.clear_notifications()
        self.refresh_notifications()


class NotificationSettingsPanel(QWidget):
    """Panel for notification settings"""

    def __init__(self, notification_manager: NotificationManager, parent=None):
        super().__init__(parent)
        self.manager = notification_manager
        self.setup_ui()

    def setup_ui(self):
        """Setup settings panel UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Notification Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #E0E0E0;")
        layout.addWidget(title)

        # Enable notifications
        self.enabled = QCheckBox("Enable Notifications")
        self.enabled.setChecked(self.manager.settings["enabled"])
        self.enabled.toggled.connect(self.update_setting)
        layout.addWidget(self.enabled)

        # Sound
        self.sound = QCheckBox("Play Sound Alerts")
        self.sound.setChecked(self.manager.settings["sound_enabled"])
        self.sound.toggled.connect(self.update_setting)
        layout.addWidget(self.sound)

        # Alert types
        layout.addWidget(QLabel("Alert Types:"))

        self.threats = QCheckBox("Security Threats")
        self.threats.setChecked(self.manager.settings["threat_alerts"])
        self.threats.toggled.connect(self.update_setting)
        layout.addWidget(self.threats)

        self.anomalies = QCheckBox("Network Anomalies")
        self.anomalies.setChecked(self.manager.settings["anomaly_alerts"])
        self.anomalies.toggled.connect(self.update_setting)
        layout.addWidget(self.anomalies)

        self.system = QCheckBox("System Events")
        self.system.setChecked(self.manager.settings["system_alerts"])
        self.system.toggled.connect(self.update_setting)
        layout.addWidget(self.system)

        # Priority filter
        layout.addWidget(QLabel("Minimum Priority:"))
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["All", "Medium", "High", "Critical"])
        self.priority_filter.setCurrentText(self.manager.settings["priority_filter"].capitalize())
        self.priority_filter.currentTextChanged.connect(self.update_priority)
        layout.addWidget(self.priority_filter)

        # Popup duration
        layout.addWidget(QLabel("Popup Duration (ms):"))
        self.duration = QSpinBox()
        self.duration.setRange(1000, 10000)
        self.duration.setValue(self.manager.settings["popup_duration"])
        self.duration.setSingleStep(1000)
        self.duration.valueChanged.connect(self.update_setting)
        layout.addWidget(self.duration)

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
            QComboBox, QSpinBox {
                background-color: #1A1F26;
                color: #E0E0E0;
                border: 1px solid #2A3038;
                border-radius: 6px;
                padding: 8px;
            }
        """)

    def update_setting(self):
        """Update notification settings"""
        self.manager.settings["enabled"] = self.enabled.isChecked()
        self.manager.settings["sound_enabled"] = self.sound.isChecked()
        self.manager.settings["threat_alerts"] = self.threats.isChecked()
        self.manager.settings["anomaly_alerts"] = self.anomalies.isChecked()
        self.manager.settings["system_alerts"] = self.system.isChecked()
        self.manager.settings["popup_duration"] = self.duration.value()
        self.manager.save_settings()

    def update_priority(self, text: str):
        """Update priority filter"""
        self.manager.settings["priority_filter"] = text.lower()
        self.manager.save_settings()
