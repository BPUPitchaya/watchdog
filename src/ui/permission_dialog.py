"""
Permission Request Dialog
GUI dialog to request administrator privileges for network monitoring
"""

import os
import platform

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)


class PermissionRequestDialog(QDialog):
    """Dialog to request administrator permissions"""

    permission_granted = pyqtSignal()
    permission_denied = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("WATCHDOG - Permission Required")
        self.setMinimumSize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        """Setup the permission request dialog UI"""
        layout = QVBoxLayout()

        # Title
        title = QLabel("Administrator Permission Required")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #E0E0E0;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Explanation
        explanation = QLabel(
            "WATCHDOG requires administrator privileges to monitor network traffic. "
            "This is necessary for:"
        )
        explanation.setWordWrap(True)
        explanation.setStyleSheet("color: #E0E0E0; margin: 10px 0;")
        layout.addWidget(explanation)

        # Reasons
        reasons = QLabel(
            "• Capturing network packets\n"
            "• Analyzing network traffic\n"
            "• Detecting security threats\n"
            "• Managing firewall rules"
        )
        reasons.setStyleSheet("color: #6BCF7F; margin-left: 20px;")
        layout.addWidget(reasons)

        # Privacy note
        privacy_note = QLabel(
            "<b>Privacy Guarantee:</b> All data is processed locally on your device. "
            "No data is transmitted to external servers."
        )
        privacy_note.setWordWrap(True)
        privacy_note.setStyleSheet(
            "color: #6BCF7F; margin: 20px 0; padding: 10px; "
            "background-color: rgba(107, 207, 127, 0.1); border-radius: 6px;"
        )
        layout.addWidget(privacy_note)

        # Platform-specific instructions
        self.platform_instructions = QLabel()
        self.platform_instructions.setWordWrap(True)
        self.platform_instructions.setStyleSheet("color: #E0E0E0; margin: 10px 0;")
        self.update_platform_instructions()
        layout.addWidget(self.platform_instructions)

        # Checkbox to remember choice
        self.remember_choice = QCheckBox("Don't ask again for this session")
        self.remember_choice.setStyleSheet("color: #E0E0E0;")
        layout.addWidget(self.remember_choice)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        grant_btn = QPushButton("Grant Permission")
        grant_btn.setStyleSheet("""
            background-color: #6BCF7F;
            color: #0F1318;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: 500;
        """)
        grant_btn.clicked.connect(self.grant_permission)
        button_layout.addWidget(grant_btn)

        deny_btn = QPushButton("Run with Limited Features")
        deny_btn.setStyleSheet("""
            background-color: #EF4444;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: 500;
        """)
        deny_btn.clicked.connect(self.deny_permission)
        button_layout.addWidget(deny_btn)

        layout.addLayout(button_layout)

        # Style
        self.setStyleSheet("""
            QDialog {
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

        self.setLayout(layout)

    def update_platform_instructions(self):
        """Update instructions based on platform"""
        system = platform.system()

        if system == "Darwin":  # macOS
            instructions = (
                "<b>macOS Instructions:</b><br>"
                "1. Click 'Grant Permission'<br>"
                "2. Enter your administrator password when prompted<br>"
                "3. The application will restart with elevated privileges"
            )
        elif system == "Windows":
            instructions = (
                "<b>Windows Instructions:</b><br>"
                "1. Close this application<br>"
                "2. Right-click the application icon<br>"
                "3. Select 'Run as Administrator'<br>"
                "4. Click 'Yes' to the User Account Control prompt"
            )
        elif system == "Linux":
            instructions = (
                "<b>Linux Instructions:</b><br>"
                "1. Close this application<br>"
                "2. Run the application with sudo:<br>"
                "   <code>sudo python3 src/ui/pyqt_dashboard.py</code>"
            )
        else:
            instructions = "Please run this application with administrator privileges."

        self.platform_instructions.setText(instructions)

    def grant_permission(self):
        """Handle permission grant"""
        system = platform.system()

        if system == "Darwin":  # macOS
            # On macOS, we need to restart with sudo
            QMessageBox.information(
                self,
                "Restart Required",
                "The application will now restart with administrator privileges.\n"
                "Please enter your password when prompted.",
                QMessageBox.StandardButton.Ok,
            )
            self.permission_granted.emit()
            self.accept()

        elif system == "Windows":
            # On Windows, user needs to manually restart as admin
            QMessageBox.information(
                self,
                "Manual Restart Required",
                "Please close this application and run it as Administrator.\n"
                "Right-click the application and select 'Run as Administrator'.",
                QMessageBox.StandardButton.Ok,
            )
            self.permission_denied.emit()
            self.accept()

        elif system == "Linux":
            # On Linux, user needs to use sudo
            QMessageBox.information(
                self,
                "Manual Restart Required",
                "Please close this application and run it with sudo:\n"
                "sudo python3 src/ui/pyqt_dashboard.py",
                QMessageBox.StandardButton.Ok,
            )
            self.permission_denied.emit()
            self.accept()

    def deny_permission(self):
        """Handle permission denial"""
        reply = QMessageBox.question(
            self,
            "Limited Features",
            "Without administrator privileges, network monitoring will be limited.\n"
            "Some features may not work correctly.\n\n"
            "Continue with limited features?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.permission_denied.emit()
            self.accept()
        else:
            # Return to permission request
            pass


class PermissionChecker:
    """Check if application has required permissions"""

    @staticmethod
    def has_admin_privileges():
        """Check if running with administrator privileges"""
        try:
            if platform.system() == "Windows":
                import ctypes

                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                # Unix-like systems
                return os.geteuid() == 0
        except Exception:
            return False

    @staticmethod
    def request_permission(parent=None):
        """Show permission request dialog"""
        dialog = PermissionRequestDialog(parent)
        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted
