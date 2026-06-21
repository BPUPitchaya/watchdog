"""
Onboarding Wizard for first-time users
Guides users through initial setup and configuration
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox, QFrame, QHBoxLayout, QLabel, QPushButton, QSpinBox, QVBoxLayout, QWizard, QWizardPage
)


def _make_stepper(label_text, tooltip, min_val, max_val, default_val, unit=""):
    """Create a custom +/- stepper widget that is beginner-friendly."""
    container = QFrame()
    container.setStyleSheet("background: transparent;")
    row = QHBoxLayout(container)
    row.setContentsMargins(0, 8, 0, 8)
    row.setSpacing(12)

    lbl = QLabel(label_text)
    lbl.setWordWrap(True)
    lbl.setStyleSheet("color: #E0E0E0; font-size: 13px;")
    lbl.setToolTip(tooltip)
    row.addWidget(lbl, stretch=1)

    minus_btn = QPushButton("  −  ")
    minus_btn.setFixedSize(42, 36)
    minus_btn.setStyleSheet("""
        QPushButton {
            background-color: #2A3038;
            color: #FFFFFF;
            font-size: 20px;
            font-weight: bold;
            border: 2px solid #00B4D8;
            border-radius: 8px;
        }
        QPushButton:hover { background-color: #3A4048; }
        QPushButton:pressed { background-color: #00B4D8; }
    """)

    value_label = QLabel(f"{default_val}{' ' + unit if unit else ''}")
    value_label.setFixedWidth(100)
    value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    value_label.setStyleSheet("""
        color: #00B4D8;
        font-size: 15px;
        font-weight: bold;
        background-color: #1A1F26;
        border: 1px solid #2A3038;
        border-radius: 6px;
        padding: 6px 4px;
    """)

    plus_btn = QPushButton("  +  ")
    plus_btn.setFixedSize(42, 36)
    plus_btn.setStyleSheet("""
        QPushButton {
            background-color: #2A3038;
            color: #FFFFFF;
            font-size: 20px;
            font-weight: bold;
            border: 2px solid #00B4D8;
            border-radius: 8px;
        }
        QPushButton:hover { background-color: #3A4048; }
        QPushButton:pressed { background-color: #00B4D8; }
    """)

    _state = [default_val]

    def update_value():
        value_label.setText(f"{_state[0]}{' ' + unit if unit else ''}")
        minus_btn.setEnabled(_state[0] > min_val)
        plus_btn.setEnabled(_state[0] < max_val)

    def decrement():
        if _state[0] > min_val:
            _state[0] -= 1
            update_value()

    def increment():
        if _state[0] < max_val:
            _state[0] += 1
            update_value()

    minus_btn.clicked.connect(decrement)
    plus_btn.clicked.connect(increment)
    update_value()

    row.addWidget(minus_btn)
    row.addWidget(value_label)
    row.addWidget(plus_btn)

    container._state = _state
    container.get_value = lambda: _state[0]
    return container


def _make_help_label(text):
    lbl = QLabel(f"  {text}")
    lbl.setWordWrap(True)
    lbl.setStyleSheet(
        "color: #6BCF7F; font-size: 11px; padding: 2px 4px;"
    )
    return lbl


class WelcomePage(QWizardPage):
    """Welcome page for onboarding wizard"""

    def __init__(self):
        super().__init__()
        self.setTitle("Welcome to WATCHDOG")
        self.setSubTitle("Your Network Security Assistant")

        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Welcome message
        welcome_label = QLabel(
            "<h2 style='color:#00B4D8;'>Welcome to WATCHDOG</h2>"
            "<p style='font-size:14px;'>WATCHDOG keeps an eye on your home or office network "
            "and warns you if anything suspicious happens.</p>"
            "<p style='font-size:14px;'>This quick setup takes about <b>1 minute</b>.</p>"
        )
        welcome_label.setWordWrap(True)
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(welcome_label)

        layout.addSpacing(10)

        for title, desc in [
            ("Monitors your network", "Watches all traffic coming in and out."),
            ("Detects threats", "Alerts you when something suspicious is found."),
            ("Keeps your data private", "Everything stays on your computer. Nothing is uploaded."),
        ]:
            row = QHBoxLayout()
            tick_lbl = QLabel("\u2713")
            tick_lbl.setFixedWidth(28)
            tick_lbl.setStyleSheet("color: #00B4D8; font-size: 18px; font-weight: bold;")
            title_lbl = QLabel(f"<b>{title}</b><br><span style='color:#8899AA;font-size:12px;'>{desc}</span>")
            title_lbl.setWordWrap(True)
            row.addWidget(tick_lbl)
            row.addWidget(title_lbl)
            layout.addLayout(row)

        layout.addStretch()
        self.setLayout(layout)


class NetworkSetupPage(QWizardPage):
    """Network monitoring setup page"""

    def __init__(self):
        super().__init__()
        self.setTitle("Step 1 — Network Monitoring")
        self.setSubTitle("Choose how WATCHDOG watches your network")

        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Auto-start monitoring checkbox
        self.auto_start = QCheckBox("Automatically start monitoring when I open the app")
        self.auto_start.setChecked(True)
        self.auto_start.setToolTip("Tick this so WATCHDOG starts protecting you as soon as you open it. Recommended for most users.")
        layout.addWidget(self.auto_start)
        layout.addWidget(_make_help_label("Recommended: Leave this ON so you're always protected."))

        layout.addSpacing(8)

        # Alert threshold stepper
        self.alert_threshold_widget = _make_stepper(
            "Alert sensitivity  (how quickly you get warned)",
            "Lower = warns you more often. Higher = only warns for serious threats.",
            1, 20, 10
        )
        layout.addWidget(self.alert_threshold_widget)
        layout.addWidget(_make_help_label(
            "10 is a good default. Lower this if you want to be warned about more things. "
            "Raise it if you're getting too many alerts."
        ))

        layout.addStretch()
        self.setLayout(layout)

    def get_settings(self):
        return {
            "auto_start": self.auto_start.isChecked(),
            "packet_limit": 0,
            "alert_threshold": self.alert_threshold_widget.get_value(),
        }


class PrivacySettingsPage(QWizardPage):
    """Privacy and data settings page"""

    def __init__(self):
        super().__init__()
        self.setTitle("Step 2 — Privacy & Data")
        self.setSubTitle("Control how your data is stored")

        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Data retention stepper
        self.retention_widget = _make_stepper(
            "Keep history for how many days?",
            "After this many days, old data is automatically deleted to save space.",
            1, 365, 30, "days"
        )
        layout.addWidget(self.retention_widget)
        layout.addWidget(_make_help_label(
            "30 days is recommended. More days = more disk space used. Fewer days = less history."
        ))

        layout.addSpacing(8)

        # Anonymize data
        self.anonymize = QCheckBox("Hide device IP addresses in logs (extra privacy)")
        self.anonymize.setChecked(True)
        self.anonymize.setToolTip("Hides real IP addresses in the display so they can't be seen at a glance. Good for privacy.")
        layout.addWidget(self.anonymize)
        layout.addWidget(_make_help_label("Recommended: Leave this ON unless you need to investigate a specific device."))

        layout.addSpacing(4)

        # Delete on exit
        self.delete_on_exit = QCheckBox("Delete all data when I close the app")
        self.delete_on_exit.setChecked(False)
        self.delete_on_exit.setToolTip("Wipes all data every time you close the app. Maximum privacy but you lose all history.")
        layout.addWidget(self.delete_on_exit)
        layout.addWidget(_make_help_label("Leave this OFF to keep your history between sessions."))

        # Privacy badge
        badge = QLabel("Your data never leaves this device. Nothing is uploaded or shared.")
        badge.setWordWrap(True)
        badge.setStyleSheet(
            "color: #6BCF7F; font-size: 12px; background: #0F2010; "
            "border: 1px solid #2A5020; border-radius: 6px; padding: 8px;"
        )
        layout.addWidget(badge)

        layout.addStretch()
        self.setLayout(layout)

    def get_settings(self):
        return {
            "retention_days": self.retention_widget.get_value(),
            "anonymize": self.anonymize.isChecked(),
            "delete_on_exit": self.delete_on_exit.isChecked(),
        }


class NotificationSettingsPage(QWizardPage):
    """Notification settings page"""

    def __init__(self):
        super().__init__()
        self.setTitle("Step 3 — Notifications")
        self.setSubTitle("Choose how you want to be warned")

        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Enable notifications
        self.enable_notifications = QCheckBox("Show me pop-up alerts for security events")
        self.enable_notifications.setChecked(True)
        self.enable_notifications.setToolTip("Shows a notification on your screen when a threat or suspicious event is detected.")
        layout.addWidget(self.enable_notifications)

        # Sound alerts
        self.sound_alerts = QCheckBox("Play a sound when an alert fires")
        self.sound_alerts.setChecked(True)
        self.sound_alerts.setToolTip("Makes a sound so you notice the alert even if you're not looking at the screen.")
        layout.addWidget(self.sound_alerts)

        # System tray icon
        self.system_tray = QCheckBox("Show WATCHDOG icon in the menu bar")
        self.system_tray.setChecked(True)
        self.system_tray.setToolTip("A small icon appears in the top menu bar so you can check status at a glance. Recommended.")
        layout.addWidget(self.system_tray)
        layout.addWidget(_make_help_label("Recommended: Keep all three ON for the best protection."))

        layout.addSpacing(6)
        layout.addWidget(QLabel("What types of events should alert me?"))

        self.alert_threats = QCheckBox("Security threats  (e.g. attacks, malware traffic)")
        self.alert_threats.setChecked(True)
        self.alert_threats.setToolTip("Alert when real threats are detected. Always recommended.")
        layout.addWidget(self.alert_threats)

        self.alert_anomalies = QCheckBox("Unusual activity  (e.g. unexpected devices, spikes)")
        self.alert_anomalies.setChecked(True)
        self.alert_anomalies.setToolTip("Alert on anything unusual. May occasionally give false positives.")
        layout.addWidget(self.alert_anomalies)

        self.alert_system = QCheckBox("System info messages  (app status, updates)")
        self.alert_system.setChecked(False)
        self.alert_system.setToolTip("Informational messages about the app itself. Can be noisy - leave OFF if unsure.")
        layout.addWidget(self.alert_system)

        layout.addStretch()
        self.setLayout(layout)

    def get_settings(self):
        return {
            "enable_notifications": self.enable_notifications.isChecked(),
            "sound_alerts": self.sound_alerts.isChecked(),
            "system_tray": self.system_tray.isChecked(),
            "alert_threats": self.alert_threats.isChecked(),
            "alert_anomalies": self.alert_anomalies.isChecked(),
            "alert_system": self.alert_system.isChecked(),
        }


class CompletionPage(QWizardPage):
    """Completion page"""

    def __init__(self):
        super().__init__()
        self.setTitle("All Done!")
        self.setSubTitle("You're ready to go")

        layout = QVBoxLayout()

        completion_label = QLabel(
            "<h2 style='color:#00B4D8;'>You're All Set!</h2>"
            "<p style='font-size:14px;'>WATCHDOG is ready to protect your network.</p>"
            "<p style='font-size:13px;'>"
            "\u2713 &nbsp;Watching your network in real-time<br>"
            "\u2713 &nbsp;Detecting threats automatically<br>"
            "\u2713 &nbsp;Alerting you to suspicious activity<br>"
            "\u2713 &nbsp;Keeping everything private on your device"
            "</p>"
            "<p style='color:#6BCF7F; font-size:13px;'>"
            "<b>Your data never leaves your computer. Ever.</b></p>"
            "<p style='font-size:13px;'>Click <b>Finish</b> to start protecting your network.</p>"
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
        self.setWizardStyle(QWizard.WizardStyle.ClassicStyle)
        self.setMinimumSize(700, 500)
        self.setOption(QWizard.WizardOption.HaveCustomButton1, False)
        self.setOption(QWizard.WizardOption.NoBackButtonOnStartPage, True)
        self.setOption(QWizard.WizardOption.NoBackButtonOnLastPage, True)

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
            * {
                color: #E0E0E0;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            }
            QWizard {
                background-color: #0F1318;
            }
            QWizardPage {
                background-color: #0F1318;
            }
            QWizard QLabel {
                color: #E0E0E0;
                background-color: transparent;
            }
            QWizard QLineEdit {
                color: #E0E0E0;
                background-color: #1A1F26;
                border: 1px solid #2A3038;
                border-radius: 6px;
                padding: 8px;
            }
            QWizard QPushButton {
                background-color: #00B4D8;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                min-width: 100px;
            }
            QWizard QPushButton:hover {
                background-color: #0096B4;
            }
            QWizard QPushButton:disabled {
                background-color: #2A3038;
                color: #5A6070;
            }
            QLabel {
                color: #E0E0E0;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            }
            QLabel h2 {
                color: #00B4D8;
                font-size: 24px;
                font-weight: 600;
            }
            QLabel h3 {
                color: #FFFFFF;
                font-size: 18px;
                font-weight: 500;
            }
            QCheckBox {
                color: #E0E0E0;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
                spacing: 10px;
                padding: 8px 0;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #2A3038;
                border-radius: 4px;
                background-color: #1A1F26;
            }
            QCheckBox::indicator:checked {
                background-color: #00B4D8;
                border-color: #00B4D8;
            }
            QSpinBox, QComboBox {
                background-color: #1A1F26;
                color: #E0E0E0;
                border: 1px solid #2A3038;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
                min-height: 20px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #00B4D8;
                border: none;
                width: 35px;
                border-radius: 4px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #0096B4;
            }
            QSpinBox::up-button::sub-control {
                subcontrol-origin: border;
                subcontrol-position: center;
                width: 15px;
                height: 15px;
            }
            QSpinBox::down-button::sub-control {
                subcontrol-origin: border;
                subcontrol-position: center;
                width: 15px;
                height: 15px;
            }
            QSpinBox::up-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 8px solid transparent;
                border-right: 8px solid transparent;
                border-bottom: 12px solid #FFFFFF;
            }
            QSpinBox::down-arrow {
                image: none;
                width: 0;
                height: 0;
                border-left: 8px solid transparent;
                border-right: 8px solid transparent;
                border-top: 12px solid #FFFFFF;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #1A1F26;
                color: #E0E0E0;
                border: 1px solid #2A3038;
                selection-background-color: #00B4D8;
            }
        """)

    def get_all_settings(self):
        """Collect all settings from wizard pages"""
        settings = {}
        settings.update(self.network_page.get_settings())
        settings.update(self.privacy_page.get_settings())
        settings.update(self.notification_page.get_settings())
        settings["onboarding_completed"] = True
        return settings

    def accept(self):
        """Handle wizard completion"""
        settings = self.get_all_settings()
        self.settings_saved.emit(settings)
        super().accept()
