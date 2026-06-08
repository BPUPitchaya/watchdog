"""
Onboarding Wizard for first-time users
Guides users through initial setup and configuration
"""

from PyQt6.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QCheckBox, QLineEdit, 
                             QComboBox, QSpinBox, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
import os
import json


class WelcomePage(QWizardPage):
    """Welcome page for onboarding wizard"""
    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to WATCHDOG")
        self.setSubTitle("Your Network Security Assistant")
        
        layout = QVBoxLayout()
        
        # Welcome message
        welcome_label = QLabel(
            "<h2>Welcome to WATCHDOG</h2>"
            "<p>Your personal security assistant that watches over your network.</p>"
            "<p>This quick setup will help you get started in just a few clicks.</p>"
            "<p><b>Your Privacy:</b> Everything stays on your computer. Nothing is sent to the cloud.</p>"
        )
        welcome_label.setWordWrap(True)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)
        
        layout.addStretch()
        self.setLayout(layout)


class NetworkSetupPage(QWizardPage):
    """Network monitoring setup page"""
    def __init__(self):
        super().__init__()
        self.setTitle("Network Monitoring")
        self.setSubTitle("How should WATCHDOG watch your network?")
        
        layout = QVBoxLayout()
        
        # Auto-start monitoring checkbox
        self.auto_start = QCheckBox("Start watching my network automatically")
        self.auto_start.setChecked(True)
        layout.addWidget(self.auto_start)
        
        # Packet capture limit
        layout.addWidget(QLabel("How much data to keep (leave at 0 for best results):"))
        self.packet_limit = QSpinBox()
        self.packet_limit.setRange(0, 10000)
        self.packet_limit.setValue(0)
        self.packet_limit.setSpecialValueText("Recommended")
        layout.addWidget(self.packet_limit)
        
        # Alert threshold
        layout.addWidget(QLabel("Alert sensitivity (lower = more sensitive):"))
        self.alert_threshold = QSpinBox()
        self.alert_threshold.setRange(1, 100)
        self.alert_threshold.setValue(10)
        layout.addWidget(self.alert_threshold)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def get_settings(self):
        return {
            'auto_start': self.auto_start.isChecked(),
            'packet_limit': self.packet_limit.value(),
            'alert_threshold': self.alert_threshold.value()
        }


class PrivacySettingsPage(QWizardPage):
    """Privacy and data settings page"""
    def __init__(self):
        super().__init__()
        self.setTitle("Privacy Settings")
        self.setSubTitle("Keep your data private and secure")
        
        layout = QVBoxLayout()
        
        # Data retention
        layout.addWidget(QLabel("How long to keep data (days):"))
        self.retention_days = QSpinBox()
        self.retention_days.setRange(1, 365)
        self.retention_days.setValue(30)
        layout.addWidget(self.retention_days)
        
        # Anonymize data
        self.anonymize = QCheckBox("Hide IP addresses for extra privacy")
        self.anonymize.setChecked(True)
        layout.addWidget(self.anonymize)
        
        # Delete on exit
        self.delete_on_exit = QCheckBox("Delete all data when I close the app")
        self.delete_on_exit.setChecked(False)
        layout.addWidget(self.delete_on_exit)
        
        # Privacy notice
        privacy_notice = QLabel(
            "<p><b>Your Privacy:</b> All your data stays on your computer. "
            "Nothing is sent anywhere. You're in control.</p>"
        )
        privacy_notice.setWordWrap(True)
        privacy_notice.setStyleSheet("color: #6BCF7F;")
        layout.addWidget(privacy_notice)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def get_settings(self):
        return {
            'retention_days': self.retention_days.value(),
            'anonymize': self.anonymize.isChecked(),
            'delete_on_exit': self.delete_on_exit.isChecked()
        }


class NotificationSettingsPage(QWizardPage):
    """Notification settings page"""
    def __init__(self):
        super().__init__()
        self.setTitle("Notifications")
        self.setSubTitle("Stay informed about security")
        
        layout = QVBoxLayout()
        
        # Enable notifications
        self.enable_notifications = QCheckBox("Show me security alerts")
        self.enable_notifications.setChecked(True)
        layout.addWidget(self.enable_notifications)
        
        # Sound alerts
        self.sound_alerts = QCheckBox("Play a sound for alerts")
        self.sound_alerts.setChecked(True)
        layout.addWidget(self.sound_alerts)
        
        # System tray icon
        self.system_tray = QCheckBox("Show icon in menu bar (recommended)")
        self.system_tray.setChecked(True)
        layout.addWidget(self.system_tray)
        
        # Alert types
        layout.addWidget(QLabel("What to alert me about:"))
        self.alert_threats = QCheckBox("Security threats")
        self.alert_threats.setChecked(True)
        layout.addWidget(self.alert_threats)
        
        self.alert_anomalies = QCheckBox("Unusual network activity")
        self.alert_anomalies.setChecked(True)
        layout.addWidget(self.alert_anomalies)
        
        self.alert_system = QCheckBox("System messages")
        self.alert_system.setChecked(False)
        layout.addWidget(self.alert_system)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def get_settings(self):
        return {
            'enable_notifications': self.enable_notifications.isChecked(),
            'sound_alerts': self.sound_alerts.isChecked(),
            'system_tray': self.system_tray.isChecked(),
            'alert_threats': self.alert_threats.isChecked(),
            'alert_anomalies': self.alert_anomalies.isChecked(),
            'alert_system': self.alert_system.isChecked()
        }


class CompletionPage(QWizardPage):
    """Completion page"""
    def __init__(self):
        super().__init__()
        self.setTitle("All Done!")
        self.setSubTitle("You're ready to go")
        
        layout = QVBoxLayout()
        
        completion_label = QLabel(
            "<h2>You're All Set!</h2>"
            "<p>WATCHDOG is now ready to protect your network.</p>"
            "<p><b>What it does:</b></p>"
            "<ul>"
            "<li>Watches your network in real-time</li>"
            "<li>Detects threats automatically</li>"
            "<li>Sends you security alerts</li>"
            "<li>Keeps everything private on your computer</li>"
            "</ul>"
            "<p><b>Your Privacy:</b> Your data never leaves your computer. Ever.</p>"
            "<p>Click 'Finish' to start protecting your network.</p>"
        )
        completion_label.setWordWrap(True)
        completion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(completion_label)
        
        layout.addStretch()
        self.setLayout(layout)


class OnboardingWizard(QWizard):
    """Main onboarding wizard"""
    settings_saved = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("WATCHDOG Setup Wizard")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(600, 500)
        
        # Add pages
        self.addPage(WelcomePage())
        self.network_page = NetworkSetupPage()
        self.addPage(self.network_page)
        self.privacy_page = PrivacySettingsPage()
        self.addPage(self.privacy_page)
        self.notification_page = NotificationSettingsPage()
        self.addPage(self.notification_page)
        self.addPage(CompletionPage())
        
        # Style
        self.setStyleSheet("""
            QWizard {
                background-color: #0F1318;
                color: #E0E0E0;
            }
            QWizardPage {
                background-color: #0F1318;
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
            QSpinBox, QComboBox {
                background-color: #1A1F26;
                color: #E0E0E0;
                border: 1px solid #2A3038;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Segoe UI', sans-serif;
            }
            QPushButton {
                background-color: #3B82F6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
        """)
    
    def get_all_settings(self):
        """Collect all settings from wizard pages"""
        settings = {}
        settings.update(self.network_page.get_settings())
        settings.update(self.privacy_page.get_settings())
        settings.update(self.notification_page.get_settings())
        settings['onboarding_completed'] = True
        return settings
    
    def accept(self):
        """Handle wizard completion"""
        settings = self.get_all_settings()
        self.settings_saved.emit(settings)
        super().accept()
