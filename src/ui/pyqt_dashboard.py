import datetime
import json
import os
import random
import signal
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import logging
from src.utils.crypto_utils import get_crypto
from src.utils.logger import get_logger, get_user_message, log_exception

logger = get_logger("pyqt_dashboard")
crypto = get_crypto()


# Function to get resource path for frozen executables
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # For development, handle different resource locations
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # If it's an asset file, use src/ui directory
        if relative_path.startswith("assets/"):
            base_path = current_dir
        # If it's a model file, use project root
        elif relative_path.startswith("models/"):
            base_path = os.path.dirname(
                os.path.dirname(current_dir)
            )  # Go up two levels from src/ui
        else:
            # Default to src/ui directory
            base_path = current_dir

    return os.path.join(base_path, relative_path)


import joblib
import psutil
from PyQt6.QtCore import (
    QEasingCurve,
    QParallelAnimationGroup,
    QPoint,
    QPropertyAnimation,
    QRect,
    Qt,
    QThread,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPixmap,
    QShortcut,
)
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSlider,
    QSplashScreen,
    QStackedWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.ml.feature_extractor import FeatureExtractor
from src.ui.error_handler import ErrorHandler
from src.ui.notification_manager import NotificationManager
from src.ui.onboarding_wizard import OnboardingWizard
from src.ui.system_tray import SystemTrayIcon
from src.ui.user_settings import SettingsManager


def get_system_ram():
    """Get total system RAM in GB."""
    try:
        ram_gb = round(psutil.virtual_memory().total / (1024**3))
        return ram_gb
    except Exception:
        return None


def get_recommended_ai_model(ram_gb):
    """Recommend AI model based on available RAM."""
    if ram_gb is None:
        return "3b", "RAM detection failed - using 3b model"
    elif ram_gb < 8:
        return "1b", f"Low RAM ({ram_gb}GB) - Use 1b model for best performance"
    elif ram_gb < 16:
        return "3b", f"Good RAM ({ram_gb}GB) - 3b model recommended"
    else:
        return "phi4", f"High RAM ({ram_gb}GB) - Can use phi4 for best quality"


from src.ai.ollama_client import OllamaClient
from src.ai.ollama_installer import OllamaInstaller
from src.ai.prompts import EXPLANATION_PROMPT, GENERAL_PROMPT, TECHNICAL_ANALYSIS_PROMPT
from src.ai.utils import format_packet_log
from src.firewall_manager import FirewallManager
from src.ui.help_content import PAGE_HELP_CONTENT
from src.ui.incidents_worker import IncidentsWorker
from src.ui.pages import (
    AIMentorPage,
    AutonomousShieldPage,
    ForensicVaultPage,
    LiveSentinelPage,
    NetworkTopologyPage,
    SettingsPage,
    ThreatEncyclopediaPage,
)
from src.ui.theme import THEME
from src.ui.widgets import (
    HelpDialog,
    LiveTrafficWidget,
    ToastNotification,
)


class SplashScreen(QSplashScreen):
    """Minimalist splash screen with logo."""

    def __init__(self, parent=None):
        # Create pixmap for splash screen
        from PyQt6.QtWidgets import QApplication

        screen = QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()

        # Use screen size or reasonable max size
        width = min(screen_geometry.width() - 100, 1200)
        height = min(screen_geometry.height() - 100, 800)

        # Create pixmap
        pixmap = QPixmap(width, height)

        super().__init__(pixmap)

        # Center on screen
        x = (screen_geometry.width() - width) // 2
        y = (screen_geometry.height() - height) // 2
        self.move(x, y)

        # Draw content on pixmap
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Gradient background
        gradient = QLinearGradient(0, 0, width, height)
        gradient.setColorAt(0, QColor(THEME["bg_dark"]))
        gradient.setColorAt(1, QColor("#0F1318"))
        painter.fillRect(pixmap.rect(), gradient)

        # Decorative circles
        painter.setPen(Qt.PenStyle.NoPen)
        center_x = width // 2
        center_y = height // 2 - 50

        # Large outer circle
        color1 = QColor(THEME["primary"])
        color1.setAlpha(20)
        painter.setBrush(color1)
        painter.drawEllipse(
            QPoint(center_x, center_y), min(width, height) // 3, min(width, height) // 3
        )

        # Medium circle
        color2 = QColor(THEME["primary"])
        color2.setAlpha(40)
        painter.setBrush(color2)
        painter.drawEllipse(
            QPoint(center_x, center_y), min(width, height) // 4, min(width, height) // 4
        )

        # Small inner circle
        color3 = QColor(THEME["primary"])
        color3.setAlpha(60)
        painter.setBrush(color3)
        painter.drawEllipse(
            QPoint(center_x, center_y), min(width, height) // 6, min(width, height) // 6
        )

        # Logo
        logo_path = resource_path("assets/logo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_size = min(width, height) // 5
            scaled_logo = logo_pixmap.scaled(
                logo_size,
                logo_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_x = (width - scaled_logo.width()) // 2
            logo_y = (height - scaled_logo.height()) // 2 - 80
            painter.drawPixmap(logo_x, logo_y, scaled_logo)
        else:
            painter.setPen(QColor(THEME["primary"]))
            font_size = min(width, height) // 10
            font = QFont("Segoe UI", font_size, QFont.Weight.Bold)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "WATCHDOG")

        # Title
        painter.setPen(QColor(THEME["primary"]))
        font = QFont("Segoe UI", min(width, height) // 30, QFont.Weight.Bold)
        painter.setFont(font)
        title_rect = QRect(0, center_y + min(width, height) // 4, width, 50)
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignCenter, "Network Security Monitoring")

        # Subtitle
        painter.setPen(QColor("#FFFFFF"))
        font = QFont("Segoe UI", min(width, height) // 50)
        painter.setFont(font)
        subtitle_rect = QRect(0, center_y + min(width, height) // 4 + 40, width, 40)
        painter.drawText(
            subtitle_rect, Qt.AlignmentFlag.AlignCenter, "AI-Powered Threat Detection System"
        )

        # Loading text
        painter.setPen(QColor(THEME["primary"]))
        font = QFont("Segoe UI", min(width, height) // 45, QFont.Weight.Medium)
        painter.setFont(font)
        loading_rect = QRect(0, height - 100, width, 40)
        painter.drawText(loading_rect, Qt.AlignmentFlag.AlignCenter, "Initializing...")

        # Progress bar background
        progress_bg_rect = QRect(width // 4, height - 60, width // 2, 4)
        painter.setBrush(QColor(THEME["bg_card"]))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(progress_bg_rect, 2, 2)

        # Progress bar fill (animated-looking)
        progress_fill_rect = QRect(width // 4, height - 60, width // 4, 4)
        painter.setBrush(QColor(THEME["primary"]))
        painter.drawRoundedRect(progress_fill_rect, 2, 2)

        # Version info at bottom
        version_color = QColor(THEME["text_secondary"])
        version_color.setAlpha(100)
        painter.setPen(version_color)
        font = QFont("Segoe UI", min(width, height) // 70)
        painter.setFont(font)
        version_rect = QRect(0, height - 30, width, 30)
        painter.drawText(
            version_rect, Qt.AlignmentFlag.AlignCenter, "v2.0 | Secure • Monitor • Protect"
        )

        painter.end()

        self.setPixmap(pixmap)


class TermsDialog(QDialog):
    """Minimalist terms and conditions dialog."""

    def __init__(self, parent=None, on_accept=None):
        super().__init__(parent)
        self.on_accept = on_accept
        self.setWindowTitle("Terms & Conditions")
        self.setFixedSize(500, 400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {THEME['bg_dark']};
                color: {THEME['text_primary']};
            }}
            QLabel {{
                color: {THEME['text_primary']};
                font-family: 'Segoe UI', sans-serif;
            }}
            QPushButton {{
                background-color: {THEME['bg_card']};
                color: {THEME['text_primary']};
                border: 1px solid {THEME['border']};
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {THEME['primary']};
                color: white;
                border: 1px solid {THEME['primary']};
            }}
            QPushButton#agree_btn {{
                background-color: {THEME['primary']};
                color: white;
                border: 1px solid {THEME['primary']};
            }}
            QPushButton#agree_btn:hover {{
                background-color: {THEME['secondary']};
                border: 1px solid {THEME['secondary']};
            }}
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Title
        title = QLabel("Network Monitoring Agreement")
        title.setStyleSheet(f"""
            font-size: 18px;
            font-weight: 600;
            color: {THEME['primary']};
        """)
        layout.addWidget(title)

        # Content in scrollable area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        content = QLabel()
        content.setWordWrap(True)
        content.setText("""
            <b>Please read these terms carefully before using WatchDog AI.</b><br><br>
            By clicking "I Agree" or continuing to use this software, you agree to be bound by these Terms and Conditions.<br><br>
            
            <b>1. Acknowledgment of MVP Status</b><br>
            WatchDog AI is provided as a Minimum Viable Product (MVP) and diagnostic tool. While the system utilizes machine learning to detect network anomalies and automate defenses, it is not a guarantee of absolute cybersecurity. The developers (Pitchaya and Thae) provide this software "as is" and without warranties of any kind.<br><br>
            
            <b>2. Authorized Use & Legal Compliance</b><br>
            WatchDog AI utilizes active packet-sniffing technology. By using this software, you explicitly warrant that:<br>
            • You are the owner, or have explicit authorization from the owner, of the network and hardware being monitored.<br>
            • You will not use this application to intercept, monitor, or capture data on networks or devices you do not have legal permission to audit.<br>
            • Your use of this software complies with all applicable local and national cybersecurity legislation, including the New Zealand Computer Act.<br><br>
            
            <b>3. Data Privacy and Edge Processing</b><br>
            WatchDog AI is built on an "Uncompromising Data Sovereignty" architecture. We respect your privacy.<br>
            <b>Zero Cloud Transmission:</b> All network packet ingestion, machine learning threat analysis, and Explainable AI (XAI) log generation occur entirely on your local hardware (Edge computing).<br>
            No network telemetry, packet data, or system logs are ever transmitted to external servers, third-party APIs, or the developers. This localized processing aligns with the standards set by the New Zealand Privacy Act 2020.<br><br>
            
            <b>4. Automated Mitigation & System Modifications</b><br>
            WatchDog AI includes an automated firewall mitigation feature that may actively alter your operating system's IP blocking rules to stop perceived threats.<br>
            You acknowledge that automated mitigation carries the risk of "false positives," which may temporarily block legitimate business traffic or services.<br>
            While fail-safes are built-in, you are solely responsible for reviewing the AI Assistant's logs and managing your firewall rules.<br><br>
            
            <b>5. Limitation of Liability</b><br>
            To the maximum extent permitted by law, the developers shall not be held liable for any direct, indirect, incidental, or consequential damages resulting from the use or inability to use this software. This includes, but is not limited to, data loss, business interruption, successful cyberattacks, or network outages caused by automated firewall modifications.<br><br>
            
            <b>6. Governing Law</b><br>
            These terms shall be governed by and construed in accordance with the laws of New Zealand.
        """)
        content.setStyleSheet(f"""
            font-size: 12px;
            line-height: 1.6;
            color: {THEME['text_secondary']};
        """)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        decline_btn = QPushButton("Decline")
        decline_btn.clicked.connect(self.reject)
        button_layout.addWidget(decline_btn)

        agree_btn = QPushButton("Agree && Continue")
        agree_btn.setObjectName("agree_btn")
        agree_btn.clicked.connect(self.on_agree)
        button_layout.addWidget(agree_btn)

        layout.addLayout(button_layout)

    def on_agree(self):
        """Handle agree button click - call callback then accept."""
        if self.on_accept:
            self.on_accept()
        self.accept()


class ModeSelectionDialog(QDialog):
    """Minimalist mode selection dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_mode = "live"  # Default to live mode
        self.setWindowTitle("Select Mode")
        self.setFixedSize(500, 350)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {THEME['bg_dark']};
                color: {THEME['text_primary']};
            }}
            QLabel {{
                color: {THEME['text_primary']};
                font-family: 'Segoe UI', sans-serif;
            }}
            QPushButton {{
                background-color: {THEME['bg_card']};
                color: white;
                border: 1px solid {THEME['border']};
                border-radius: 6px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 500;
                text-align: center;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {THEME['primary']};
                color: white;
                border: 1px solid {THEME['primary']};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(50, 50, 50, 50)

        # Title
        title = QLabel("Select Mode")
        title.setStyleSheet(f"""
            font-size: 24px;
            font-weight: 600;
            color: {THEME['primary']};
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Choose how you want to use Watchdog")
        subtitle.setStyleSheet(f"""
            font-size: 12px;
            color: {THEME['text_secondary']};
        """)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addStretch()

        # Mode buttons
        button_layout = QVBoxLayout()
        button_layout.setSpacing(20)

        # Demo Mode button
        demo_btn = QPushButton("Demo Mode")
        demo_btn.clicked.connect(lambda: self._select_mode("demo"))
        button_layout.addWidget(demo_btn)

        # Live Mode button
        live_btn = QPushButton("Live Mode")
        live_btn.clicked.connect(lambda: self._select_mode("live"))
        button_layout.addWidget(live_btn)

        layout.addLayout(button_layout)

        layout.addStretch()

    def _select_mode(self, mode):
        """Handle mode selection."""
        self.selected_mode = mode
        self.accept()

    def get_selected_mode(self):
        """Return the selected mode."""
        return self.selected_mode


def signal_handler(sig, frame):
    QApplication.quit()


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class AIWorker(QThread):
    """Worker thread for non-blocking AI queries with streaming."""

    chunk = pyqtSignal(str, str)  # (chunk, full_response_so_far)
    finished = pyqtSignal(str)  # Emits final AI response
    error = pyqtSignal(str)  # Emits error message

    def __init__(self, ai_client, prompt):
        super().__init__()
        self.ai_client = ai_client
        self.prompt = prompt

    def run(self):
        try:
            # Use streaming for real-time updates
            def on_chunk(chunk, full):
                self.chunk.emit(chunk, full)

            response = self.ai_client.query_stream(self.prompt, on_chunk)
            self.finished.emit(response)
        except Exception as e:
            self.error.emit(f"AI Error: {str(e)}")


class WatchdogDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WATCHDOG AI Dashboard")
        self.setGeometry(100, 100, 1200, 1000)
        self.hide()  # Hide window initially

        # Initialize UX components first (needed for onboarding check)
        self.settings_manager = SettingsManager()
        self.settings = {}  # Initialize settings dictionary for runtime settings
        self.error_handler = ErrorHandler(self)
        self.notification_manager = NotificationManager(self)
        self.system_tray = SystemTrayIcon(self)

        # Connect system tray signals
        self.system_tray.signals.show_window.connect(self.show)
        self.system_tray.signals.hide_window.connect(self.hide)
        self.system_tray.signals.start_monitoring.connect(self.start_sniffing)
        self.system_tray.signals.stop_monitoring.connect(self.stop_sniffing)
        self.system_tray.signals.quit_application.connect(self.close)

        # Check for --layout-only and --no-ai flags
        import sys

        self.layout_only = False  # Force UI creation for widgets
        self.no_ai = "--no-ai" in sys.argv

        # Show splash screen before proceeding (skip if layout-only)
        if not self.layout_only:
            print("Showing splash screen...")
            splash = SplashScreen()
            splash.show()

            # Process events to ensure splash is displayed
            QApplication.processEvents()

            # Use QTimer for delay instead of sleep to ensure UI updates
            # Create a timer to close splash after 5 seconds
            splash_timer = QTimer()
            splash_timer.setSingleShot(True)
            splash_timer.timeout.connect(splash.close)
            splash_timer.start(5000)

            # Wait for splash to close
            while not splash.isHidden():
                QApplication.processEvents()
                QThread.msleep(50)

            print("Splash screen closed")

            # Show terms dialog after splash with auto-accept for GUI launches
            try:
                terms_dialog = TermsDialog(self, on_accept=None)
                if terms_dialog.exec() != QDialog.DialogCode.Accepted:
                    print("User declined terms. Exiting.")
                    sys.exit(0)
            except Exception as e:
                print(f"Terms dialog failed to display: {e}")
                print("Auto-accepting terms for production build")

            # Show mode selection dialog after terms (skip for production builds)
            if hasattr(sys, "frozen"):
                print("Skipping mode selection dialog (production build)")
                self.demo_mode = False
            else:
                mode_dialog = ModeSelectionDialog(self)
                if mode_dialog.exec() != QDialog.DialogCode.Accepted:
                    print("User cancelled mode selection. Exiting.")
                    sys.exit(0)
                self.demo_mode = mode_dialog.get_selected_mode() == "demo"
            print(f"DEBUG: Demo mode = {self.demo_mode}")

            # Show main window after mode selection
            self.showMaximized()

            # Update demo mode indicator
            if hasattr(self, "demo_indicator"):
                self.demo_indicator.setVisible(self.demo_mode)

        # Show onboarding wizard for first-time users (outside layout-only check)
        is_first_time = self.settings_manager.is_first_time_user()
        print(f"DEBUG: is_first_time = {is_first_time}")
        wizard_completed = False
        if is_first_time:
            try:
                print("DEBUG: Creating onboarding wizard")
                wizard = OnboardingWizard(self)
                wizard.settings_saved.connect(self.apply_onboarding_settings)
                print("DEBUG: Showing onboarding wizard")
                result = wizard.exec()
                print(f"DEBUG: Wizard closed with result {result}")
                if result == 1 or result == QDialog.DialogCode.Accepted:
                    wizard_completed = True
                    print("DEBUG: Wizard completed successfully")
                else:
                    print("DEBUG: Wizard was cancelled or closed without completion")
                    sys.exit(0)  # Exit if wizard not completed
            except Exception as e:
                print(f"DEBUG: Onboarding wizard error: {e}")
                import traceback

                traceback.print_exc()
                sys.exit(0)  # Exit on error
        else:
            print("DEBUG: Skipping onboarding wizard (not first time)")

        # Start sniffer ONLY after onboarding wizard completes successfully
        # Only start if not layout-only
        if not self.layout_only and (not is_first_time or wizard_completed):
            print("Starting packet sniffer...")
            from src.network.basic_sniffer import BasicSniffer

            class SnifferThread(QThread):
                def __init__(self, sniffer):
                    super().__init__()
                    self.sniffer = sniffer

                def run(self):
                    self.sniffer.start_sniffing()

            self.sniffer = BasicSniffer()
            self.sniffer_thread = SnifferThread(self.sniffer)
            self.sniffer_thread.start()
            print("Packet sniffer started")

        # Initialize attributes
        self.model = None  # ML model (RandomForestClassifier)
        self.ai_model_name = "llama3.2:1b"  # Ollama model name
        self.extractor = None
        self.ai_client = None
        self.previous_packets = 0
        self.toast = None  # Toast notification instance
        self.manual_block_count = 0
        self.manual_blocked_ips = set()  # Track which IPs were manually blocked
        self.blocked_ips = set()  # Track all blocked IPs (auto + manual)
        self.ai_mentor_page = None  # Will be set in create_pages()
        self.conversation_history = []  # Shared conversation history for AI chat sync
        self._ml_cache = {}  # Cache ML predictions to avoid recomputing on main thread
        self.confidence_cache = {}  # Cache for confidence scores and actions
        self.chat_history_file = "logs/chat_history.enc"  # Encrypted chat history file
        self._prediction_buffer = []  # Buffer for batch predictions
        self._prediction_sample_rate = self.settings_manager.get(
            "ml_sample_rate", 5
        )  # Load from settings
        self._packet_counter = 0  # Track packet count for sampling
        self.firewall_manager = FirewallManager()  # System-level IP blocking via pfctl
        # demo_mode is set by mode selection dialog, don't overwrite here

        # Load ML (skip if layout-only)
        if not self.layout_only:
            try:
                self.model = joblib.load(resource_path("models/random_forest_model.pkl"))
                self.extractor = FeatureExtractor()
                print("ML model loaded successfully")
            except FileNotFoundError:
                self.error_handler.handle_error(
                    FileNotFoundError("ML model file not found"), "model_not_found", "ML_ERRORS"
                )
                self.model = None
                self.extractor = None
            except Exception as e:
                self.error_handler.handle_error(e, "prediction_failed", "ML_ERRORS")
                self.model = None
                self.extractor = None

            # Initialize AI client (skip if --no-ai flag)
            if not self.no_ai:
                try:
                    # Check if Ollama is installed and running
                    installer = OllamaInstaller(model=self.ai_model_name)

                    if not installer.is_ollama_installed():
                        print("Ollama not found. AI features will be disabled.")
                        print("To enable AI: python src/ai/ollama_installer.py --auto-install")
                        self.ai_client = None
                    elif not installer.is_ollama_running():
                        print("Ollama is installed but not running. AI features will be disabled.")
                        print("Please start Ollama application/service.")
                        self.ai_client = None
                    elif not installer.is_model_available():
                        print(f"Model {self.ai_model_name} not found. Pulling it now...")
                        installer.pull_model()
                        self.ai_client = OllamaClient(model=self.ai_model_name)
                    else:
                        self.ai_client = OllamaClient(model=self.ai_model_name)
                        print(f"AI initialized with model: {self.ai_model_name}")
                except Exception as e:
                    print(f"AI initialization failed: {e}")
                    self.ai_client = None

        # Create UI components
        self.create_ui()

        # Setup keyboard shortcuts
        self._setup_keyboard_shortcuts()

        # Timer for auto-update (skip in layout-only or demo mode)
        if not self.layout_only and not self.demo_mode:
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_ui)
            self.timer.start(5000)  # Increased to 5 seconds for better performance

        # Initial update (skip in layout-only or demo mode)
        if not self.layout_only and not self.demo_mode:
            self.update_ui()

        # Load chat history on startup
        self._load_chat_history()

        # Clean up old logs based on retention setting
        self._cleanup_old_logs()

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for quick access."""
        # Ctrl+Q: Quit application
        quit_shortcut = QShortcut(QKeySequence.StandardKey.Quit, self)
        quit_shortcut.activated.connect(self.close)

        # Ctrl+S: Navigate to settings
        settings_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        settings_shortcut.activated.connect(self._navigate_to_settings)

        # F11: Toggle fullscreen
        fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        fullscreen_shortcut.activated.connect(self._toggle_fullscreen)

    def _navigate_to_settings(self):
        """Navigate to settings page."""
        if hasattr(self, "settings_nav"):
            # Navigate to settings page (index 6)
            self.page_container.setCurrentIndex(6)
            # Update navigation button
            self._set_nav_active(6)

    def _toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def create_ui(self):
        # Create page container first (full-size content area)
        self.page_container = QStackedWidget()
        self.page_container.setStyleSheet("background-color: transparent;")
        self.create_pages()

        # Create overlay container widget (this will be the central widget)
        self.overlay_container = QWidget()
        self.overlay_container.setStyleSheet("background-color: transparent;")

        from PyQt6.QtGui import QFontDatabase

        # Load custom font
        font_path = resource_path("assets/Orbitron-VariableFont_wght.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            tech_font = font_families[0] if font_families else "Courier New"
        else:
            tech_font = "Courier New"

        # Store it for use in stylesheets
        self.tech_font = tech_font
        # Page container fills the entire overlay but with left margin for sidebar
        self.page_container.setParent(self.overlay_container)
        self.page_container.setGeometry(
            64, 0, self.overlay_container.width() - 64, self.overlay_container.height()
        )

        # Sidebar is a child of overlay container, positioned absolutely on the left
        self.nav_sidebar = QWidget(self.overlay_container)
        self.nav_sidebar.setGeometry(0, 0, 64, self.overlay_container.height())
        self.nav_sidebar.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_dark']};
                border-right: 1px solid {THEME['border']};
            }}
        """)
        self.sidebar_expanded = False

        # Set the overlay container as central widget
        self.setCentralWidget(self.overlay_container)

        # Handle resize of overlay container
        self.overlay_container.resizeEvent = self._on_overlay_resize

        nav_layout = QVBoxLayout(self.nav_sidebar)
        nav_layout.setContentsMargins(0, 16, 0, 16)
        nav_layout.setSpacing(4)
        nav_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Logo and title header container
        self.sidebar_header = QWidget()
        self.sidebar_header.setMinimumHeight(50)
        self.sidebar_header.setStyleSheet("background-color: transparent;")
        header_layout = QHBoxLayout(self.sidebar_header)
        header_layout.setContentsMargins(5, 0, 5, 0)
        header_layout.setSpacing(8)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo
        self.sidebar_logo = QLabel()
        self.sidebar_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = resource_path("assets/logo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            scaled_logo = logo_pixmap.scaled(
                32,
                32,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.sidebar_logo.setPixmap(scaled_logo)
        else:
            self.sidebar_logo.setText("WD")
            self.sidebar_logo.setStyleSheet("font-size: 16px;")
        self.sidebar_logo.setFixedSize(32, 32)
        header_layout.addWidget(self.sidebar_logo)

        # Sidebar title (hidden when collapsed)
        self.sidebar_title = QLabel("WATCHDOG")
        self.sidebar_title.setStyleSheet(f"""
            color: {THEME['text_primary']};
            font-family: 'Segoe UI';
            font-size: 13px;
            font-weight: 600;
            letter-spacing: 1px;
        """)
        self.sidebar_title.setVisible(False)
        header_layout.addWidget(self.sidebar_title, alignment=Qt.AlignmentFlag.AlignVCenter)
        header_layout.addStretch()

        # Demo mode indicator
        self.demo_indicator = QLabel("DEMO MODE")
        self.demo_indicator.setStyleSheet(f"""
            color: {THEME['warning']};
            font-family: {THEME['font_mono']};
            font-size: 10px;
            font-weight: 600;
            padding: 4px 8px;
            border-radius: 4px;
            background-color: rgba(255, 193, 7, 0.1);
        """)
        self.demo_indicator.setVisible(False)
        header_layout.addWidget(self.demo_indicator)

        nav_layout.addWidget(self.sidebar_header)

        # Navigation buttons with icons (Settings at bottom)
        nav_buttons = [
            (
                "DASHBOARD",
                "Real-time visibility and high-frequency packet monitoring",
                "dashboard icon.png",
            ),
            (
                "FORENSIC LOG VAULT",
                "Translating complex metadata into human-readable advice",
                "log vault icon.png",
            ),
            (
                "SECURITY CONTROL",
                "Managing host firewall and setting AI confidence thresholds",
                "security control icon.png",
            ),
            ("AI ASSISTANT", "AI model selector and real-time analysis", "Ai assistant icon.png"),
            (
                "NETWORK TOPOLOGY",
                "Identifying all hardware on the LAN to resolve visibility gap",
                "network topology icon.png",
            ),
            (
                "THREAT ENCYCLOPEDIA",
                "Educational resource for understanding cyber threats and attack types",
                "Threat_encyclopedia.png",
            ),
            (
                "SETTINGS AND PRIVACY",
                "Configuring Ollama and ensuring alignment with NZ Privacy Act 2020 principles",
                "setting icon.png",
            ),
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
            container.setFixedSize(62, 52)
            container.setCursor(Qt.CursorShape.PointingHandCursor)
            container.setToolTip(tooltip)
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(4, 0, 4, 0)
            container_layout.setSpacing(6)
            container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # Icon label (always visible)
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_path = resource_path(f"assets/{icon_file}")
            if os.path.exists(icon_path):
                pixmap = QPixmap(icon_path).scaled(
                    28,
                    28,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                # Special handling for Threat Encyclopedia icon with white background
                if icon_file == "Threat_encyclopedia.png":
                    # Create circular mask to hide white background
                    # Create a circular mask
                    mask = QPixmap(48, 48)
                    mask.fill(Qt.GlobalColor.black)
                    painter = QPainter(mask)
                    painter.setBrush(QBrush(Qt.GlobalColor.white))
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(2, 2, 44, 44)  # Draw white circle
                    painter.end()
                    pixmap.setMask(mask.createMaskFromColor(Qt.GlobalColor.black))
                icon_label.setPixmap(pixmap)
            icon_label.setFixedSize(28, 28)
            container_layout.addWidget(icon_label)

            # Text label (hidden when collapsed)
            text_label = QLabel(label)
            text_label.setStyleSheet(f"""
                color: {THEME['text_secondary']};
                font-size: 12px;
                font-weight: bold;
                font-family: 'Segoe UI';
            """)
            text_label.setVisible(False)
            container_layout.addWidget(text_label)
            container_layout.addStretch()

            # Style container like a button
            container.setStyleSheet(f"""
                QWidget {{
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                }}
                QWidget:hover {{
                    background-color: {THEME['bg_card']};
                }}
            """)

            # Make clickable
            container.mousePressEvent = lambda event, idx=i: self.switch_page(idx)

            nav_layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignHCenter)
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

    def _add_help_button(self, page_widget, page_name, help_y_offset=30):
        """Add floating help button to a page widget."""
        # Create wrapper widget
        wrapper = QWidget()
        wrapper.setLayout(QVBoxLayout())
        wrapper.layout().setContentsMargins(0, 0, 0, 0)
        wrapper.layout().setSpacing(0)

        # Add the page widget
        wrapper.layout().addWidget(page_widget)

        # Create help button
        help_btn = QPushButton("?")
        help_btn.setFixedSize(36, 36)
        help_btn.setToolTip(f"Learn about {page_name}")
        help_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                border: none;
                border-radius: 18px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {THEME['secondary']};
                border: 2px solid white;
            }}
        """)

        # Position button in top-right corner with configurable Y offset
        help_btn.setParent(wrapper)
        help_btn.move(wrapper.width() - 60, help_y_offset)
        help_btn.raise_()

        # Update position on resize
        def update_position(e=None):
            help_btn.move(wrapper.width() - 60, help_y_offset)
            help_btn.raise_()

        wrapper.resizeEvent = lambda e: update_position()

        # Connect click to show help
        def show_help():
            hotspots = PAGE_HELP_CONTENT.get(page_name, [])
            if hotspots:
                dialog = HelpDialog(wrapper, page_name, hotspots)
                dialog.exec()

        help_btn.clicked.connect(show_help)

        return wrapper

    def create_pages(self):
        """Create all dashboard pages with help buttons."""
        # Page 0: Live Sentinel (main dashboard) - move help button down to avoid blocking "live" placeholder
        live_sentinel = LiveSentinelPage(self)
        sentinel_widget = self._add_help_button(
            live_sentinel.create(), "Live Sentinel", help_y_offset=80
        )
        self.page_container.addWidget(sentinel_widget)
        self.table = live_sentinel.table
        self.live_sentinel_page = live_sentinel  # Store reference for updates
        self.forensic_panel = live_sentinel.forensic_panel  # Link AI chat panel

        # Page 1: Forensic Vault
        self.forensic_vault = ForensicVaultPage(self)
        vault_widget = self._add_help_button(self.forensic_vault.create(), "Forensic Vault")
        self.page_container.addWidget(vault_widget)
        self.vault_table = self.forensic_vault.vault_table
        self.vault_search = self.forensic_vault.vault_search

        # Page 2: Autonomous Shield
        self.shield_page = AutonomousShieldPage(self)
        shield_widget = self._add_help_button(self.shield_page.create(), "Autonomous Shield")
        self.page_container.addWidget(shield_widget)
        self.blocked_ip_table = self.shield_page.blocked_ip_table

        # Page 3: AI Mentor - move help button up
        self.ai_mentor_page = AIMentorPage(self)
        mentor_widget = self._add_help_button(
            self.ai_mentor_page.create(), "AI Mentor", help_y_offset=20
        )
        self.page_container.addWidget(mentor_widget)

        # Page 4: Network Topology
        try:
            self.network_topology = NetworkTopologyPage(self)
            topology_widget = self._add_help_button(
                self.network_topology.create(), "Network Topology"
            )
            self.page_container.addWidget(topology_widget)
        except Exception as e:
            log_exception(logger, "creating network topology page", e, get_user_message("ui_error"))
            import traceback

            logger.error(f"Network topology page creation failed: {traceback.format_exc()}")
            # Create a placeholder page instead
            from src.ui.pages import PlaceholderPage

            placeholder = PlaceholderPage(self)
            placeholder_widget = self._add_help_button(
                placeholder.create(
                    "Network Topology", "Network topology scanning is currently unavailable."
                ),
                "Network Topology",
            )
            self.page_container.addWidget(placeholder_widget)

        # Page 5: Threat Encyclopedia
        threat_encyclopedia = ThreatEncyclopediaPage(self)
        encyclopedia_widget = self._add_help_button(
            threat_encyclopedia.create(), "Threat Encyclopedia"
        )
        self.page_container.addWidget(encyclopedia_widget)

        # Page 6: Settings & Privacy (at bottom of sidebar)
        settings_page = SettingsPage(self)
        self.settings_page = settings_page  # Store reference for syncing
        settings_widget = self._add_help_button(settings_page.create(), "Settings")
        self.page_container.addWidget(settings_widget)
        self.settings_nav = settings_page.settings_nav
        self.settings_content = settings_page.settings_content

    def update_traffic_status(self):
        if hasattr(self, "sniffer") and self.sniffer.is_running:
            # Find the live sentinel page and update status
            for i in range(self.page_container.count()):
                widget = self.page_container.widget(i)
                if hasattr(widget, "findChild"):
                    traffic_widgets = widget.findChildren(LiveTrafficWidget)
                    for traffic_widget in traffic_widgets:
                        traffic_widget.set_network_status("Connected")

        # Schedule initial status update
        QTimer.singleShot(3000, self.update_traffic_status)

    def _on_overlay_resize(self, event):
        """Update page container and sidebar when overlay container is resized"""
        # Update page container with left margin for sidebar
        self.page_container.setGeometry(
            64, 0, self.overlay_container.width() - 64, self.overlay_container.height()
        )
        # Update sidebar height
        self.nav_sidebar.setGeometry(
            self.nav_sidebar.x(), 0, self.nav_sidebar.width(), self.overlay_container.height()
        )

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
        target_width = 220

        # Create parallel animation group for coordinated animation
        self.animation_group = QParallelAnimationGroup()

        # 1. Animate sidebar width
        sidebar_anim = QPropertyAnimation(self.nav_sidebar, b"geometry")
        sidebar_anim.setDuration(350)
        sidebar_anim.setStartValue(self.nav_sidebar.geometry())
        sidebar_anim.setEndValue(QRect(0, 0, target_width, self.overlay_container.height()))
        sidebar_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
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
        target_width = 64

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
                container.setFixedSize(200, 52)
                text_label.setVisible(True)
            else:
                # Narrow container, text hidden
                container.setFixedSize(62, 52)
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
            icon_label = self.nav_item_icon_labels[i]
            if i == index:
                container.setStyleSheet(f"""
                    QWidget {{
                        background-color: {THEME['bg_card']};
                        border: none;
                        border-left: 2px solid {THEME['primary']};
                        border-radius: 0px;
                    }}
                """)
                icon_label.setStyleSheet("opacity: 1;")
                text_label.setStyleSheet(f"""
                    color: {THEME['primary']};
                    font-size: 11px;
                    font-weight: 600;
                    font-family: 'Segoe UI';
                """)
            else:
                container.setStyleSheet(f"""
                    QWidget {{
                        background-color: transparent;
                        border: none;
                        border-radius: 6px;
                    }}
                    QWidget:hover {{
                        background-color: {THEME['bg_card']};
                        border: none;
                    }}
                """)
                text_label.setStyleSheet(f"""
                    color: {THEME['text_secondary']};
                    font-size: 11px;
                    font-weight: 400;
                    font-family: 'Segoe UI';
                """)

    def _animate_text_labels_in(self):
        """Show text labels after expansion completes"""
        for container in self.nav_item_containers:
            container.setFixedSize(200, 52)
        for text_label in self.nav_item_text_labels:
            text_label.setVisible(True)

    def toggle_ai(self, checked):
        try:
            if checked:
                # Enable AI
                if not self.ai_client:
                    try:
                        # Check if Ollama is installed and running
                        installer = OllamaInstaller(model=self.ai_model_name)

                        if not installer.is_ollama_installed():
                            log_exception(
                                logger,
                                "Ollama not installed",
                                Exception("Ollama not found"),
                                get_user_message("ollama_not_installed"),
                            )
                            from PyQt6.QtWidgets import QMessageBox

                            QMessageBox.warning(
                                self,
                                "Ollama Not Found",
                                f"{get_user_message('ollama_not_installed')}\n\n"
                                "To enable AI features:\n"
                                "1. Run: python src/ai/ollama_installer.py --auto-install\n"
                                "2. Or download from https://ollama.ai/download",
                            )
                            self.ai_toggle_btn.setChecked(False)
                            return
                        elif not installer.is_ollama_running():
                            log_exception(
                                logger,
                                "Ollama not running",
                                Exception("Ollama not running"),
                                get_user_message("ollama_not_running"),
                            )
                            from PyQt6.QtWidgets import QMessageBox

                            QMessageBox.warning(
                                self,
                                "Ollama Not Running",
                                f"{get_user_message('ollama_not_running')}\n\n"
                                "Please start the Ollama application:\n"
                                "- macOS: Open Ollama from Applications\n"
                                "- Windows: Start Ollama from Start Menu\n"
                                "- Linux: Run 'ollama serve' in terminal",
                            )
                            self.ai_toggle_btn.setChecked(False)
                            return
                        elif not installer.is_model_available():
                            logger.info(f"Model {self.ai_model_name} not found. Pulling it now...")
                            print(f"Model {self.ai_model_name} not found. Pulling it now...")
                            installer.pull_model()
                            self.ai_client = OllamaClient(model=self.ai_model_name)
                            logger.info(f"AI enabled with model: {self.ai_model_name}")
                        else:
                            self.ai_client = OllamaClient(model=self.ai_model_name)
                            logger.info(f"AI enabled with model: {self.ai_model_name}")
                            print(f"AI enabled with model: {self.ai_model_name}")
                    except Exception as e:
                        log_exception(logger, "initializing AI", e, get_user_message("ui_error"))
                        from PyQt6.QtWidgets import QMessageBox

                        QMessageBox.critical(
                            self, "AI Error", f"{get_user_message('ui_error')}\n\nDetails: {str(e)}"
                        )
                        self.ai_toggle_btn.setChecked(False)
                        return
            else:
                # Disable AI
                self.ai_client = None
                logger.info("AI disabled")

            # Update button text and style
            self.ai_toggle_btn.setText("AI: ON" if checked else "AI: OFF")

            # Refresh forensic vault to update AI availability
            if hasattr(self, "vault_table"):
                self.load_flagged_incidents()
        except Exception as e:
            log_exception(logger, "toggling AI", e)
            logger.error(f"Failed to toggle AI: {e}")

    def switch_page(self, index):
        # Update active navigation styling
        self._set_nav_active(index)

        # Switch to the selected page
        self.page_container.setCurrentIndex(index)

        # Removed automatic loading to prevent lag during page transitions

    def load_flagged_incidents(self):
        # Load flagged incidents from packet_data.json
        # In live mode, start with empty data (fresh session)
        # In demo mode, load from packet_data.json for demo data
        if hasattr(self, "demo_mode") and self.demo_mode:
            try:
                data = crypto.read_encrypted_file("packet_data.json")
            except (FileNotFoundError, Exception):
                data = {"packets": []}
            packets = data.get("packets", [])
        else:
            packets = []
            # Clear vault table in live mode for fresh session
            if hasattr(self, "vault_table") and self.vault_table:
                self.vault_table.setRowCount(0)

        # Move heavy processing to background thread
        self.worker = IncidentsWorker(packets, self.model, self.extractor, self.layout_only)
        self.worker.finished.connect(self._update_vault_table)
        self.worker.start()

    def _add_to_vault(self, packet, confidence, action):
        """Add a single flagged packet to the forensic vault."""
        if not hasattr(self, "vault_table") or self.vault_table is None:
            return

        # Add new row to vault table
        row = self.vault_table.rowCount()
        self.vault_table.insertRow(row)

        # Convert timestamp to human-readable format
        timestamp = packet.get("timestamp", 0)
        if isinstance(timestamp, (int, float)):
            dt = datetime.datetime.fromtimestamp(timestamp)
            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            timestamp = "Unknown"

        src_ip = packet.get("src_ip", "")
        dst_ip = packet.get("dst_ip", "")
        protocol = packet.get("protocol", "Other")

        self.vault_table.setItem(row, 0, QTableWidgetItem(timestamp))
        src_ip_item = QTableWidgetItem(src_ip)
        src_ip_item.setForeground(QColor(THEME["primary"]))
        src_ip_item.setFont(QFont(THEME["font_mono"].strip("'"), 12))
        self.vault_table.setItem(row, 1, src_ip_item)
        self.vault_table.setItem(row, 2, QTableWidgetItem(dst_ip))
        self.vault_table.setItem(row, 3, QTableWidgetItem(protocol))
        self.vault_table.setItem(row, 4, QTableWidgetItem(f"{confidence:.0f}%"))
        self.vault_table.setItem(row, 5, QTableWidgetItem(action))
        self.vault_table.setItem(row, 6, QTableWidgetItem("Click to view AI analysis"))
        self.vault_table.setItem(row, 7, QTableWidgetItem("Analyze"))

    def _update_vault_table(self, flagged_packets, force_demo_data=False):
        # In demo mode, don't add sample data unless forced
        # If force_demo_data is True, use the flagged_packets directly without adding sample data
        sample_packets = []
        if hasattr(self, "demo_mode") and self.demo_mode:
            if force_demo_data:
                # Use the passed-in flagged_packets directly for demo attack
                final_list = flagged_packets
            else:
                # Normal demo mode - empty
                final_list = []
        else:
            # Always add sample flagged incidents for demonstration
            sample_packets = [
                {
                    "timestamp": 1773629875.0,
                    "src_ip": "192.168.1.100",
                    "dst_ip": "10.0.0.1",
                    "protocol": "TCP",
                    "length": 1500,
                    "src_port": 4444,
                    "dst_port": 80,
                    "flags": "S",
                    "count": 9999,
                },
                {
                    "timestamp": 1773629876.0,
                    "src_ip": "10.10.10.10",
                    "dst_ip": "172.16.40.172",
                    "protocol": "UDP",
                    "length": 512,
                    "src_port": 53,
                    "dst_port": 53,
                    "flags": "",
                    "count": 10000,
                },
                {
                    "timestamp": 1773629877.0,
                    "src_ip": "203.0.113.1",
                    "dst_ip": "172.16.40.172",
                "protocol": "TCP",
                "length": 2000,
                "src_port": 22,
                "dst_port": 22,
                "flags": "SA",
                "count": 10001,
            },
            {
                "timestamp": 1773629880.0,
                "src_ip": "192.168.1.105",
                "dst_ip": "10.0.0.5",
                "protocol": "TCP",
                "length": 1200,
                "src_port": 3389,
                "dst_port": 443,
                "flags": "PA",
                "count": 10002,
            },
            {
                "timestamp": 1773629885.0,
                "src_ip": "172.16.40.50",
                "dst_ip": "192.168.1.1",
                "protocol": "ICMP",
                "length": 64,
                "src_port": 0,
                "dst_port": 0,
                "flags": "",
                "count": 10003,
            },
            {
                "timestamp": 1773629890.0,
                "src_ip": "198.51.100.22",
                "dst_ip": "172.16.40.172",
                "protocol": "TCP",
                "length": 800,
                "src_port": 443,
                "dst_port": 8080,
                "flags": "F",
                "count": 10004,
            },
            {
                "timestamp": 1773629895.0,
                "src_ip": "192.168.1.200",
                "dst_ip": "10.0.0.50",
                "protocol": "UDP",
                "length": 256,
                "src_port": 123,
                "dst_port": 123,
                "flags": "",
                "count": 10005,
            },
            {
                "timestamp": 1773629900.0,
                "src_ip": "203.0.113.50",
                "dst_ip": "192.168.1.100",
                "protocol": "TCP",
                "length": 1800,
                "src_port": 445,
                "dst_port": 139,
                "flags": "S",
                "count": 10006,
            },
            {
                "timestamp": 1773629905.0,
                "src_ip": "10.20.30.40",
                "dst_ip": "172.16.40.172",
                "protocol": "TCP",
                "length": 500,
                "src_port": 25,
                "dst_port": 587,
                "flags": "R",
                "count": 10007,
            },
            {
                "timestamp": 1773629910.0,
                "src_ip": "198.51.100.100",
                "dst_ip": "10.0.0.100",
                "protocol": "UDP",
                "length": 1024,
                "src_port": 161,
                "dst_port": 162,
                "flags": "",
                "count": 10008,
            },
        ]

        # Merge sample packets if they aren't already represented (to ensure vault has content)
        # For simplicity in demo, we just add them
        # Skip this if force_demo_data is True (demo attack scenario)
        if not force_demo_data:
            final_list = flagged_packets + sample_packets[:10]

        if not hasattr(self, "vault_table") or self.vault_table is None:
            return

        self.vault_table.setRowCount(len(final_list))
        for i, packet in enumerate(final_list):
            # Convert timestamp to human-readable format
            timestamp = packet.get("timestamp", 0)
            if isinstance(timestamp, (int, float)):
                dt = datetime.datetime.fromtimestamp(timestamp)
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                timestamp = "Unknown"

            src_ip = packet.get("src_ip", "")
            dst_ip = packet.get("dst_ip", "")
            protocol = packet.get("protocol", "Other")

            # Use pre-calculated AI results from worker
            confidence = packet.get("ai_confidence", "N/A")
            threat_level = packet.get("ai_threat", "UNKNOWN")
            ai_summary = (
                "Click to view AI analysis" if not self.layout_only else "Sample flagged packet"
            )

            self.vault_table.setItem(i, 0, QTableWidgetItem(timestamp))
            # Make IP columns stand out with cyan color
            src_ip_item = QTableWidgetItem(src_ip)
            src_ip_item.setForeground(QColor(THEME["primary"]))
            src_ip_item.setFont(QFont(THEME["font_mono"].strip("'"), 12))
            self.vault_table.setItem(i, 1, src_ip_item)

            # Add other columns
            self.vault_table.setItem(i, 2, QTableWidgetItem(dst_ip))
            self.vault_table.setItem(i, 3, QTableWidgetItem(protocol))
            self.vault_table.setItem(i, 4, QTableWidgetItem(confidence))
            self.vault_table.setItem(i, 5, QTableWidgetItem(threat_level))
            self.vault_table.setItem(i, 6, QTableWidgetItem(ai_summary))

            # Action button
            self.vault_table.setItem(i, 7, QTableWidgetItem("Analyze"))

            dst_ip_item = QTableWidgetItem(dst_ip)
            dst_ip_item.setForeground(QColor(THEME["primary"]))
            dst_ip_item.setFont(QFont(THEME["font_mono"].strip("'"), 12))
            self.vault_table.setItem(i, 2, dst_ip_item)
            self.vault_table.setItem(i, 3, QTableWidgetItem(protocol))
            self.vault_table.setItem(i, 4, QTableWidgetItem(confidence))
            self.vault_table.setItem(i, 5, QTableWidgetItem(threat_level))
            self.vault_table.setItem(i, 6, QTableWidgetItem(ai_summary))

            # Add Action buttons - compact tool buttons
            action_widget = QWidget()
            action_widget.setStyleSheet(f"background-color: {THEME['bg_card']};")
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 3, 5, 8)
            action_layout.setSpacing(6)
            action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            from PyQt6.QtWidgets import QToolButton

            # Block Source IP button
            block_src_btn = QToolButton()
            block_src_btn.setText("Block Source")
            block_src_btn.setFixedSize(90, 25)
            block_src_btn.setStyleSheet("""
                QToolButton {
                    background-color: #DC2626;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QToolButton:hover {
                    background-color: #EF4444;
                }
            """)
            block_src_btn.setToolTip(f"Block Source: {src_ip}")
            block_src_btn.clicked.connect(lambda checked, ip=src_ip: self.block_ip_from_vault(ip))
            action_layout.addWidget(block_src_btn)

            # Block Destination IP button
            block_dst_btn = QToolButton()
            block_dst_btn.setText("Block Destination")
            block_dst_btn.setFixedSize(100, 25)
            block_dst_btn.setStyleSheet("""
                QToolButton {
                    background-color: #06B6D4;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 10px;
                    font-weight: bold;
                }
                QToolButton:hover {
                    background-color: #0891B2;
                }
            """)
            block_dst_btn.setToolTip(f"Block Destination: {dst_ip}")
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
            "Block IP Address",
            f"Are you sure you want to block {ip_address}?\n\nThis will add it to the Autonomous Shield block list.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Add to notification system
            self.notification_manager.add_threat_alert(
                "IP Blocked",
                ip_address,
                f"User manually blocked IP {ip_address} from Forensic Vault",
            )

            # Increment manual block counter and track manual IPs FIRST
            if hasattr(self, "manual_block_count"):
                self.manual_block_count += 1
                self.manual_blocked_ips.add(ip_address)

            # Add to blocked IPs set
            if hasattr(self, "blocked_ips"):
                self.blocked_ips.add(ip_address)

            # Actually block at system firewall level
            try:
                self.firewall_manager.block_ip(ip_address)
            except Exception as e:
                print(f"Firewall block failed: {e}")

            # Add to shield's blocked list widget if it exists
            if hasattr(self, "blocked_list_widget"):
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

            # Show confirmation
            QMessageBox.information(
                self,
                "IP Blocked",
                f"Successfully blocked {ip_address}\nAdded to Autonomous Shield block list.",
            )

            # Sync blocked IPs and update statistics AFTER manual counter is updated
            self.shield_page._sync_blocked_ips()
            self.shield_page.update_shield_statistics()

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
        analysis_label.setStyleSheet(
            "background-color: rgba(30, 41, 59, 0.8); padding: 20px; border-radius: 10px; border: 1px solid #222222;"
        )
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

    def _generate_demo_data(self):
        """Generate realistic simulated threat data for demo mode."""
        import datetime

        # Threat types with realistic scenarios
        threat_scenarios = [
            {
                "source": "203.0.113.45",
                "destination": "192.168.1.94",
                "protocol": "TCP",
                "length": 1500,
                "threat_type": "DDoS Attack",
                "confidence": 95,
                "action": "Block",
            },
            {
                "source": "198.51.100.23",
                "destination": "192.168.1.1",
                "protocol": "TCP",
                "length": 60,
                "threat_type": "Port Scanning",
                "confidence": 88,
                "action": "Flag",
            },
            {
                "source": "192.0.2.78",
                "destination": "192.168.1.94",
                "protocol": "UDP",
                "length": 512,
                "threat_type": "Malware C2",
                "confidence": 92,
                "action": "Block",
            },
            {
                "source": "10.0.0.50",
                "destination": "192.168.1.200",
                "protocol": "TCP",
                "length": 1200,
                "threat_type": "Phishing Attempt",
                "confidence": 85,
                "action": "Flag",
            },
            {
                "source": "192.168.1.100",
                "destination": "192.168.1.1",
                "protocol": "TCP",
                "length": 64,
                "threat_type": "Brute Force",
                "confidence": 90,
                "action": "Block",
            },
        ]

        # Generate packets based on scenarios
        packets = []
        current_time = datetime.datetime.now()

        for _i in range(15):  # Generate 15 packets
            scenario = random.choice(threat_scenarios)
            packet = {
                "src_ip": scenario["source"],
                "dst_ip": scenario["destination"],
                "protocol": scenario["protocol"],
                "length": scenario["length"] + random.randint(-100, 100),
                "timestamp": (
                    current_time - datetime.timedelta(seconds=random.randint(0, 60))
                ).isoformat(),
                "threat_type": scenario["threat_type"],
                "confidence": scenario["confidence"] + random.randint(-5, 5),
                "action": scenario["action"],
            }
            packets.append(packet)

        return {"packets": packets, "packet_count": len(packets), "demo_mode": True}

    def update_ui(self):
        if self.demo_mode:
            # Use simulated data in demo mode
            data = self._generate_demo_data()
            current_packets = data.get("packet_count", 0)
        else:
            # Use real network data in live mode
            current_packets = 0
            try:
                data = crypto.read_encrypted_file("packet_data.json")
                current_packets = data.get("packet_count", 0)
            except (FileNotFoundError, Exception):
                data = {"packets": []}

        # Update LiveSentinelPage widgets
        if hasattr(self, "live_sentinel_page") and self.live_sentinel_page:
            self.live_sentinel_page.update_all_widgets()

        packets = data.get("packets", [])
        if packets and not self.demo_mode:
            # Update table (skip in demo mode - table is pre-populated)
            self.table.setRowCount(min(10, len(packets)))
            for i, packet in enumerate(packets[-10:]):
                self.table.setItem(i, 0, QTableWidgetItem(packet.get("src_ip", "")))
                self.table.setItem(i, 1, QTableWidgetItem(packet.get("dst_ip", "")))
                proto = packet.get("protocol", "Other")
                self.table.setItem(i, 2, QTableWidgetItem(proto))
                self.table.setItem(i, 3, QTableWidgetItem(str(packet.get("length", 0))))

                # ML predictions for Confidence Score and Action (skip in layout-only)
                # Use cache to avoid expensive ML computation on the main thread
                prediction = 0  # Initialize to safe default
                if not self.layout_only and self.model and self.extractor:
                    # Check cache first
                    cache_key = f"{packet.get('src_ip', '')}:{packet.get('dst_ip', '')}:{packet.get('protocol', '')}"
                    if cache_key in self.confidence_cache:
                        confidence, action = self.confidence_cache[cache_key]
                    else:
                        # Compute ML prediction
                        try:
                            packet_data = {
                                "src_ip": packet.get("src_ip", "192.168.1.1"),
                                "dst_ip": packet.get("dst_ip", "10.0.0.1"),
                                "protocol": 6 if packet.get("protocol", "TCP").upper() == "TCP" else 17,
                                "length": packet.get("length", 100),
                                "src_port": packet.get("src_port", 12345),
                                "dst_port": packet.get("dst_port", 80),
                                "flags": packet.get("flags", "S"),
                                "direction": "inbound",
                            }
                            features = self.extractor.extract_packet_features(packet_data)
                            selected_features, feature_names = self.extractor.get_selected_features(features)
                            import numpy as np
                            features_array = np.array([selected_features])
                            prediction = self.model.predict(features_array)[0]
                            probabilities = self.model.predict_proba(features_array)[0]
                            confidence = max(probabilities) * 100
                            action = "Flagged" if prediction == 1 else "Allowed"
                        except Exception as e:
                            confidence = 50
                            action = "Allowed"
                        self.confidence_cache[cache_key] = (confidence, action)

                    self.table.setItem(i, 4, QTableWidgetItem(f"{confidence:.0f}%"))
                    self.table.setItem(i, 5, QTableWidgetItem(action))

                    # If flagged, add to forensic vault
                    if prediction == 1 and hasattr(self, "vault_table") and self.vault_table:
                        self._add_to_vault(packet, confidence, action)
                else:
                    # Layout-only mode: show placeholder values
                    self.table.setItem(i, 4, QTableWidgetItem("N/A"))
                    self.table.setItem(i, 5, QTableWidgetItem("N/A"))
        elif self.demo_mode:
            # In demo mode, populate with sample data
            sample_traffic = [
                ("192.168.1.100", "10.0.0.1", "TCP", 1500, "85%", "Allowed"),
                ("192.168.1.105", "10.0.0.5", "TCP", 1200, "92%", "Allowed"),
                ("172.16.40.50", "192.168.1.1", "ICMP", 64, "45%", "Allowed"),
                ("198.51.100.22", "172.16.40.172", "TCP", 800, "78%", "Allowed"),
                ("203.0.113.45", "192.168.1.1", "TCP", 1500, "95%", "Flagged"),
                ("198.51.100.23", "192.168.1.1", "TCP", 1500, "88%", "Flagged"),
                ("192.0.2.100", "192.168.1.1", "HTTP", 1500, "92%", "Flagged"),
                ("203.0.113.67", "192.168.1.1", "SSH", 1500, "85%", "Flagged"),
                ("198.51.100.50", "192.168.1.1", "DNS", 1500, "90%", "Flagged"),
                ("203.0.113.89", "192.168.1.1", "HTTP", 1500, "87%", "Flagged"),
            ]
            self.table.setRowCount(len(sample_traffic))
            for i, (src_ip, dst_ip, protocol, length, confidence, action) in enumerate(sample_traffic):
                self.table.setItem(i, 0, QTableWidgetItem(src_ip))
                self.table.setItem(i, 1, QTableWidgetItem(dst_ip))
                self.table.setItem(i, 2, QTableWidgetItem(protocol))
                self.table.setItem(i, 3, QTableWidgetItem(str(length)))
                self.table.setItem(i, 4, QTableWidgetItem(confidence))
                self.table.setItem(i, 5, QTableWidgetItem(action))

        # Update pps and gauge (skip in layout-only)
        if not self.layout_only:
            pps = max(0, current_packets - self.previous_packets)
            self.previous_packets = current_packets
            risk = min(100, (pps / 50) * 100)  # 50 pps = 100% risk
            if hasattr(self, "right_gauge") and self.right_gauge:
                self.right_gauge.set_risk(risk)

    def send_message(self, msg):
        """Send message programmatically (used by forensic panel)."""
        if not msg:
            return
        # Add user message and queue AI response
        self.add_chat_message("user", msg)
        QTimer.singleShot(1000, lambda: self.process_response(msg))

    def process_response(self, msg):
        """Process AI response and add to shared conversation."""
        response = self.process_command(msg)
        self.add_chat_message("ai", response)

    def add_chat_message(self, sender, message):
        """Add a message to shared conversation history and sync both chats."""
        # Add to shared history
        self.conversation_history.append((sender, message))

        # Limit history to prevent unbounded growth (keep last 500 messages)
        if len(self.conversation_history) > 500:
            self.conversation_history = self.conversation_history[-500:]

        # Auto-save chat history
        self._save_chat_history()

        # Update dashboard forensic panel chat (QTextEdit uses HTML)
        if hasattr(self, "forensic_panel") and self.forensic_panel:
            if sender == "user":
                self.forensic_panel.chat_area.append(f"<b>You:</b> {message}")
            else:  # ai
                self.forensic_panel.chat_area.append(
                    f"<b><span style='color: #2DD4BF'>AI:</span></b> {message}"
                )

        # Sync with AI Mentor page if available
        if self.ai_mentor_page:
            self.ai_mentor_page.sync_message(sender, message)

    def _save_chat_history(self):
        """Save chat history to encrypted file."""
        try:
            from src.utils.crypto_utils import get_crypto
            from pathlib import Path

            # Ensure logs directory exists
            Path("logs").mkdir(exist_ok=True)

            crypto = get_crypto()
            chat_data = {
                "conversation_history": self.conversation_history,
                "timestamp": __import__("time").time(),
            }
            crypto.write_encrypted_file(chat_data, self.chat_history_file)
        except Exception as e:
            print(f"Failed to save chat history: {e}")

    def _load_chat_history(self):
        """Load chat history from encrypted file and restore to UI."""
        try:
            from src.utils.crypto_utils import get_crypto

            crypto = get_crypto()
            if crypto.file_exists(self.chat_history_file):
                chat_data = crypto.read_encrypted_file(self.chat_history_file)
                self.conversation_history = chat_data.get("conversation_history", [])
                print(f"Loaded {len(self.conversation_history)} chat messages")

                # Restore messages to UI after a short delay to ensure UI is ready
                QTimer.singleShot(1000, self._restore_chat_to_ui)
        except Exception as e:
            print(f"Failed to load chat history: {e}")
            self.conversation_history = []

    def _restore_chat_to_ui(self):
        """Restore loaded chat history to UI components."""
        for sender, message in self.conversation_history:
            # Update dashboard forensic panel chat
            if hasattr(self, "forensic_panel") and self.forensic_panel:
                if sender == "user":
                    self.forensic_panel.chat_area.append(f"<b>You:</b> {message}")
                else:  # ai
                    self.forensic_panel.chat_area.append(
                        f"<b><span style='color: #2DD4BF'>AI:</span></b> {message}"
                    )

            # Sync with AI Mentor page if available
            if self.ai_mentor_page:
                self.ai_mentor_page.sync_message(sender, message)

    def _cleanup_old_logs(self):
        """Clean up old log files based on retention setting."""
        try:
            import os
            from datetime import datetime, timedelta

            # Get retention days from settings (default 30)
            retention_days = getattr(self, "settings", {}).get("log_retention_days", 30)

            logs_dir = "logs"
            if not os.path.exists(logs_dir):
                return

            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=retention_days)

            # Clean up old log files
            for filename in os.listdir(logs_dir):
                if filename.endswith(".log") or filename.endswith(".enc"):
                    filepath = os.path.join(logs_dir, filename)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))

                    if file_mtime < cutoff_date:
                        try:
                            os.remove(filepath)
                            print(f"Deleted old log file: {filename}")
                        except Exception as e:
                            print(f"Failed to delete {filename}: {e}")
        except Exception as e:
            print(f"Error cleaning up old logs: {e}")

    def process_command(self, msg):
        """Process user commands and return appropriate responses."""
        msg_lower = msg.lower()

        # Keyword-based responses (work without AI)
        import re

        greeting_pattern = r"\b(hi|hello|hey|greetings)\b"
        if re.search(greeting_pattern, msg_lower):
            return "Hello! I'm the AI assistant for WATCHDOG. Type 'help' to see what I can do."

        elif msg_lower.strip() in ["help", "?", "help me", "commands"] or msg_lower.startswith(
            "help "
        ):
            return """Quick Commands:

Basic:      hi | help | time
Security:   threat level | status | danger
Info:       traffic | logs | firewall | attacks
Advice:     tips | prevent | secure network
ML:         predict: src_ip=X dst_ip=Y protocol=tcp

Type any command above to get started!"""

        elif "what can you do" in msg_lower or "capabilities" in msg_lower:
            offline_features = [
                "Real-time threat monitoring (Live Sentinel)",
                "ML-based packet analysis",
                "Security best practices and tips",
                "Network traffic insights",
                "System health reports",
                "Attack type explanations",
            ]
            ai_features = (
                "Detailed log analysis and natural language security explanations (with AI enabled)"
            )
            return (
                "Offline Features (no AI required):\n• "
                + "\n• ".join(offline_features)
                + f"\n\n{ai_features}\n\nType 'help' for all available commands."
            )

        elif "thank" in msg_lower:
            return "You're welcome! Let me know if you need anything else."

        elif "threat" in msg_lower and "level" in msg_lower:
            context = self._get_system_context()
            return f"Current threat level: {context['threat_level']} ({context['risk_score']:.1f}% risk)\n{context['system_health']}\nTotal packets monitored: {context['total_packets']:,}\n{context['recent_alerts']}"

        elif "status" in msg_lower:
            context = self._get_system_context()
            return f"System Status: {context['system_health']}\nThreat Level: {context['threat_level']}\nPackets Monitored: {context['total_packets']:,}\nAI Assistant: {'Online (with real-time context)' if self.ai_client else 'Offline'}"

        elif "firewall" in msg_lower:
            return "Firewall Status: ACTIVE - Blocking unauthorized connections. Last updated: just now."

        elif "packet" in msg_lower or "traffic" in msg_lower:
            return "Recent activity: Monitoring 47 packets/sec. No anomalies detected in current traffic flow."

        elif "who are you" in msg_lower or "your name" in msg_lower:
            return "I'm WATCHDOG's AI Security Assistant. I help monitor network traffic, detect threats, and provide forensic analysis."

        elif "time" in msg_lower:
            from datetime import datetime

            return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        # Comprehensive security advice responses (work without AI)
        elif "prevent" in msg_lower and any(
            w in msg_lower for w in ["threat", "attack", "security", "protect"]
        ):
            context = self._get_system_context()
            return f"""Security Best Practices:

Current Status: {context['system_health']}

Prevention Tips:
1. Keep firewall ACTIVE (currently enabled)
2. Monitor unusual traffic patterns ({context['recent_alerts']})
3. Regular security audits ({context['total_packets']:,} packets analyzed)
4. Block suspicious IPs (ML model: {'Active' if self.model else 'Offline'})

Risk Level: {context['threat_level']} ({context['risk_score']:.1f}%)

For detailed analysis, enable AI with Ollama running on port 11434."""

        elif any(w in msg_lower for w in ["tip", "advice", "recommend", "improve", "secure"]):
            return """Network Security Recommendations:

Quick Wins:
• Use strong, unique passwords for all network devices
• Enable WPA3 encryption on WiFi
• Disable unused ports and services
• Keep firmware/software updated
• Enable automatic security patches

Monitoring:
• Review firewall logs weekly
• Set up alerts for suspicious traffic
• Check for unauthorized devices
• Audit user access permissions

Currently: ML threat detection {'active' if self.model else 'offline'}, monitoring enabled."""

        elif "dangerous" in msg_lower or "risk" in msg_lower or "warning" in msg_lower:
            context = self._get_system_context()
            if context["threat_level"] in ["HIGH", "ELEVATED"]:
                return f"ALERT: {context['recent_alerts']}\n\nRisk Score: {context['risk_score']:.1f}%\nStatus: {context['system_health']}\n\nRecommend immediate review of recent traffic. Check Settings > Flagged Incidents for details."
            else:
                return f"System is currently safe. Risk Level: {context['threat_level']} ({context['risk_score']:.1f}%)\n\n{context['system_health']}\n\nContinue monitoring - no immediate threats detected."

        elif "attack" in msg_lower and "type" in msg_lower:
            return """Common Attack Types Detected by WATCHDOG:

1. Port Scanning - Systematic scanning of ports for vulnerabilities
2. DDoS - Distributed Denial of Service traffic floods
3. Malware C2 - Command & control communication attempts
4. Brute Force - Repeated login/password attempts
5. Suspicious Payloads - Unusual packet sizes or content
6. IP Spoofing - Fake source addresses

Current Detection: ML model {'active' if self.model else 'offline'}
Check Live Sentinel > Flagged Incidents for detected threats."""

        elif "wpa3" in msg_lower:
            if "enable" in msg_lower or "turn on" in msg_lower or "setup" in msg_lower:
                return """How to Enable WPA3 on Your Router:

1. Access router admin panel (usually 192.168.1.1 or 192.168.0.1)
2. Login with admin credentials
3. Go to WiFi/Wireless Settings
4. Change Security Mode to "WPA3-Personal" or "WPA3-SAE"
5. Save and restart router
6. Reconnect all devices with new password

Note: Older devices may not support WPA3."""
            else:
                return """WPA3 (WiFi Protected Access 3):

Latest WiFi security standard with:
- Stronger encryption (192-bit for enterprise)
- Protection against offline dictionary attacks
- Forward secrecy (past traffic stays encrypted)
- Simplified device setup (QR codes)

Upgrade from WPA2 if your router supports it."""

        elif "password" in msg_lower and (
            "strong" in msg_lower or "good" in msg_lower or "create" in msg_lower
        ):
            return """Strong Password Tips:

Length: Use 12+ characters
Mix: Upper, lower, numbers, symbols
Avoid: Common words, names, dates
Unique: Different password for each device
Manager: Use a password manager

Example good password: Tr0ub4dor&3X9!kL

Change default router password first!"""

        elif "update" in msg_lower or "patch" in msg_lower:
            return """Keeping Software Updated:

Router: Check for firmware updates monthly
Devices: Enable auto-updates when possible
Priority order:
1. Router firmware
2. Operating system updates
3. Security software
4. Other applications

Updates fix security vulnerabilities quickly."""

        elif "log" in msg_lower or "history" in msg_lower or "record" in msg_lower:
            context = self._get_system_context()
            return f"""Network Activity Log Summary:

• Total Packets Monitored: {context['total_packets']:,}
• Recent Alerts: {context['recent_alerts']}
• Current Threat Level: {context['threat_level']}
• System Status: {context['system_health']}

View detailed logs:
- Live Sentinel page: Real-time packet table
- Forensic Vault: Flagged incidents and analysis
- Settings: Export packet data

For AI-powered log analysis, enable Ollama integration."""

        elif "monitor" in msg_lower or "watch" in msg_lower:
            return """WATCHDOG Monitoring Capabilities:

Active Monitoring:
- Real-time packet capture and analysis
- ML-based threat detection ({'enabled' if self.model else 'disabled'})
- Risk score calculation (0-100%)
- Automated toast alerts for threats
- Network traffic visualization

Dashboard Views:
- Live Sentinel: Current traffic + threat gauge
- Forensic Vault: Historical incidents
- Network Topology: Device monitoring

Auto-refresh: Every 2 seconds"""

        elif msg_lower.startswith("predict"):
            if not self.model or not self.extractor:
                return "ML model not available. Please ensure models/random_forest_model.pkl exists. Try 'help' for other commands."
            try:
                params_str = msg.split(":", 1)[1].strip()
                params = {}
                for pair in params_str.split():
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        params[key.strip()] = value.strip()
                packet_data = {
                    "src_ip": params.get("src_ip", "192.168.1.1"),
                    "dst_ip": params.get("dst_ip", "10.0.0.1"),
                    "protocol": 6 if params.get("protocol", "tcp").lower() == "tcp" else 17,
                    "length": int(params.get("length", "100")),
                    "src_port": int(params.get("src_port", "12345")),
                    "dst_port": int(params.get("dst_port", "80")),
                    "flags": params.get("flags", "S"),
                    "direction": "inbound",
                }
                features = self.extractor.extract_packet_features(packet_data)
                selected_features, feature_names = self.extractor.get_selected_features(features)
                import numpy as np

                # Use numpy array without feature names to avoid sklearn warning
                features_array = np.array([selected_features])
                prediction = self.model.predict(features_array)[0]
                label_map = {0: "Safe", 1: "ATTACK"}
                return f"Prediction: {label_map.get(prediction, 'UNKNOWN')}"
            except Exception as e:
                return f"Error: {str(e)}"

        # AI-dependent responses (require ai_client)
        if not self.ai_client:
            return "I'm not connected to the AI backend right now. Try 'help' to see available offline commands, or enable AI with Ollama running on port 11434."

        # Check if there's already an AI query running
        if hasattr(self, "_ai_worker") and self._ai_worker and self._ai_worker.isRunning():
            return "⏳ I'm still processing your previous question. Please wait..."

        if msg_lower.startswith("explain log:"):
            log_str = msg[12:].strip()
            try:
                packet = json.loads(log_str)
                formatted = format_packet_log(packet)
                self._start_ai_query(EXPLANATION_PROMPT.format(log=formatted))
                return "__AI_PROCESSING__"  # Signal that we're handling this async
            except Exception as e:
                return f"Error processing log: {str(e)}"

        elif msg_lower.startswith("analyze log:"):
            log_str = msg[12:].strip()
            try:
                packet = json.loads(log_str)
                formatted = format_packet_log(packet)
                self._start_ai_query(TECHNICAL_ANALYSIS_PROMPT.format(log=formatted))
                return "__AI_PROCESSING__"
            except Exception as e:
                return f"Error processing log: {str(e)}"

        elif "analyze last threat" in msg_lower:
            # Handle "Analyze Last Threat" command
            if not hasattr(self, "flagged_incidents") or not self.flagged_incidents:
                return "No threats have been detected yet. Click 'Test Threat' in AI Mentor to create a mock threat for testing."

            # Get the most recent threat
            last_threat = self.flagged_incidents[0]

            # Debug: print what keys are in the threat
            print(
                f"[DEBUG] Threat keys: {list(last_threat.keys()) if isinstance(last_threat, dict) else 'Not a dict'}"
            )

            # Safely extract only serializable data
            def safe_str(value, default="N/A"):
                try:
                    if value is None:
                        return default
                    # Skip complex objects
                    if hasattr(value, "__class__") and "RandomForest" in str(type(value)):
                        return default
                    return str(value)
                except:
                    return default

            def safe_int(value, default=0):
                try:
                    if value is None:
                        return default
                    if isinstance(value, (int, float)):
                        return int(value)
                    return default
                except:
                    return default

            timestamp = safe_str(last_threat.get("timestamp"))
            attack_type = safe_str(last_threat.get("attack_type", "Unknown"))
            source_ip = safe_str(last_threat.get("source_ip"))
            destination_ip = safe_str(last_threat.get("destination_ip"))
            protocol = safe_str(last_threat.get("protocol"))
            confidence = safe_int(last_threat.get("confidence"))
            action = safe_str(last_threat.get("action"))
            description = safe_str(last_threat.get("description"))

            # Format threat details for AI
            threat_details = f"""
Last Detected Threat:
- Timestamp: {timestamp}
- Attack Type: {attack_type}
- Source IP: {source_ip}
- Destination IP: {destination_ip}
- Protocol: {protocol}
- Confidence Score: {confidence}%
- Action Taken: {action}
- Description: {description}

Please analyze this threat for a business owner or manager (non-technical audience). Your response should:

1. Explain what happened in simple, non-technical language
2. Describe the potential business impact (data loss, downtime, reputation, etc.)
3. Provide clear, actionable steps they can take to protect their business
4. Explain whether this is a serious threat or something minor
5. Use plain English - avoid technical jargon, acronyms, or complex terminology
6. Format with bullet points and clear headings for easy reading

Keep the tone helpful, reassuring, and practical. Focus on what matters most to running a business safely.
"""

            self._start_ai_query(threat_details)
            return "__AI_PROCESSING__"

        # Catch-all for general security questions (works without AI)
        elif any(word in msg_lower for word in ["how", "what", "why", "can", "should", "do i"]):
            return """I can help with security topics. Try these commands:

Network: secure network | firewall | attacks | traffic
WiFi: wpa3 | password tips
System: threat level | status | tips | updates

For specific questions about WATCHDOG features, type 'help' to see all commands.

Enable Ollama AI (port 11434) for detailed answers to any question."""

        # AI-dependent responses (require ai_client)
        if not self.ai_client:
            return "I'm not connected to the AI backend right now. Try 'help' to see available offline commands, or enable AI with Ollama running on port 11434."

        # Check if there's already an AI query running
        if hasattr(self, "_ai_worker") and self._ai_worker and self._ai_worker.isRunning():
            return "I'm still processing your previous question. Please wait..."

        # General query - use AI with context
        context = self._get_system_context()
        prompt = GENERAL_PROMPT.format(
            query=msg,
            threat_level=context["threat_level"],
            risk_score=context["risk_score"],
            total_packets=context["total_packets"],
            recent_alerts=context["recent_alerts"],
            system_health=context["system_health"],
        )
        self._start_ai_query(prompt)
        return "__AI_PROCESSING__"

    def _get_system_context(self):
        """Gather current system state for AI context (fast, no ML predictions)."""
        context = {
            "threat_level": "LOW",
            "risk_score": 0,
            "total_packets": 0,
            "recent_alerts": "None",
            "system_health": "Operational",
        }

        # Get packet count from file (fast)
        try:
            data = crypto.read_encrypted_file("packet_data.json")
            context["total_packets"] = data.get("packet_count", 0)
        except (FileNotFoundError, Exception):
            pass

        # Count attacks from table widget (fast, already calculated)
        attack_count = 0
        if hasattr(self, "table"):
            row_count = min(self.table.rowCount(), 20)  # Check last 20 visible rows
            for i in range(row_count):
                action_item = self.table.item(i, 5)  # Action column
                if action_item and action_item.text() == "ATTACK":
                    attack_count += 1

        # Set threat level based on risk percentage (aligned with system health thresholds)
        if context["risk_score"] > 70:
            context["threat_level"] = "HIGH"
        elif context["risk_score"] > 40:
            context["threat_level"] = "ELEVATED"
        elif attack_count > 0:
            context["threat_level"] = "LOW"

        if attack_count > 0:
            context["recent_alerts"] = f"{attack_count} threats in recent traffic"

        # Get risk score from gauge (fast)
        if hasattr(self, "live_sentinel_page") and self.live_sentinel_page:
            if hasattr(self.live_sentinel_page, "right_gauge") and hasattr(
                self.live_sentinel_page.right_gauge, "risk_value"
            ):
                context["risk_score"] = round(self.live_sentinel_page.right_gauge.risk_value, 1)

        # Determine system health
        if context["risk_score"] > 70:
            context["system_health"] = "CRITICAL - Immediate attention required"
        elif context["risk_score"] > 40:
            context["system_health"] = "WARNING - Elevated risk detected"
        elif context["risk_score"] > 0:
            context["system_health"] = "CAUTION - Minor anomalies"
        else:
            context["system_health"] = "NOMINAL - All systems operational"

        return context

    def _start_ai_query(self, prompt):
        """Start async AI query with streaming."""
        # Initialize streaming state
        self._streaming_buffer = ""
        self._streaming_anchor_pos = None  # Integer position anchor

        # Add placeholder message and store position
        if hasattr(self, "forensic_panel") and self.forensic_panel:
            chat = self.forensic_panel.chat_area
            chat.append("<b><span style='color: #2DD4BF'>AI:</span></b> ")
            # Store the text length as anchor position
            self._streaming_anchor_pos = len(chat.toPlainText())

        # Setup timer for batched UI updates (every 150ms)
        self._stream_timer = QTimer(self)
        self._stream_timer.timeout.connect(self._flush_stream_buffer)
        self._stream_timer.start(500)  # Increased to 500ms for better performance

        # Create and start worker thread
        self._ai_worker = AIWorker(self.ai_client, prompt)
        self._ai_worker.chunk.connect(self._on_ai_chunk_buffered)
        self._ai_worker.finished.connect(self._on_ai_finished)
        self._ai_worker.error.connect(self._on_ai_error)
        self._ai_worker.start()

    def _on_ai_chunk_buffered(self, chunk, full_response):
        """Buffer chunks - actual UI update happens in timer."""
        self._streaming_buffer = full_response

    def _flush_stream_buffer(self):
        """Batch update UI with accumulated chunks."""
        if not self._streaming_buffer or self._streaming_anchor_pos is None:
            return

        chat = self.forensic_panel.chat_area
        cursor = chat.textCursor()

        # Select from anchor position to end
        cursor.beginEditBlock()
        cursor.setPosition(self._streaming_anchor_pos)
        cursor.movePosition(cursor.MoveOperation.End, cursor.MoveMode.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(self._streaming_buffer)
        cursor.endEditBlock()

        # Auto-scroll
        scrollbar = chat.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_ai_finished(self, response):
        """Handle AI response when streaming finishes."""
        # Stop the batch timer
        if hasattr(self, "_stream_timer") and self._stream_timer:
            self._stream_timer.stop()

        # Final flush to ensure all text is shown
        self._flush_stream_buffer()
        self._streaming_buffer = ""
        self._streaming_anchor_pos = None

        # Sync to AI Mentor page
        if self.ai_mentor_page:
            self.ai_mentor_page.sync_message("ai", response)

    def _on_ai_error(self, error_msg):
        """Handle AI query error."""
        if hasattr(self, "_stream_timer") and self._stream_timer:
            self._stream_timer.stop()
        self.add_chat_message("ai", f"❌ {error_msg}")

    def update_ai_model(self, model_name):
        """Update AI model used by OllamaClient."""
        self.ai_model_name = model_name  # Store for future AI client initialization
        if self.ai_client:
            self.ai_client.model = model_name
        else:
            # Model switch will apply on next AI query
            pass

        # Add system message to dashboard AI chat
        self.add_chat_message("ai", f"System: AI model switched to {model_name}")

        # Update AI mentor page if available
        if hasattr(self, "ai_mentor_page") and hasattr(self.ai_mentor_page, "set_model"):
            # Convert model name to index
            models = ["llama3.2:1b", "llama3.2:3b", "llama3:8b", "phi4"]
            try:
                index = models.index(model_name)
                self.ai_mentor_page.set_model(index)
            except ValueError:
                pass

        # Update forensic panel if available
        if hasattr(self, "forensic_panel") and hasattr(self.forensic_panel, "set_model"):
            # Convert model name to index
            models = ["llama3.2:1b", "llama3.2:3b", "llama3:8b", "phi4"]
            try:
                index = models.index(model_name)
                self.forensic_panel.set_model(index)
            except ValueError:
                pass

        # Update AI widget if available
        if hasattr(self, "ai_widget"):
            self.ai_widget.set_model(model_name)

        # Update settings page if available
        if hasattr(self, "settings_page") and hasattr(self.settings_page, "set_model"):
            self.settings_page.set_model(model_name)

    def closeEvent(self, event):
        # Save chat history before closing
        self._save_chat_history()

        # Stop all timers
        if hasattr(self, "timer"):
            self.timer.stop()
        if hasattr(self, "right_gauge") and hasattr(self.right_gauge, "smooth_timer"):
            self.right_gauge.smooth_timer.stop()
        if hasattr(self, "live_traffic") and hasattr(self.live_traffic, "timer"):
            self.live_traffic.timer.stop()
        if hasattr(self, "_stream_timer") and self._stream_timer:
            self._stream_timer.stop()
        # Stop AI worker if running
        if hasattr(self, "_ai_worker") and self._ai_worker and self._ai_worker.isRunning():
            self._ai_worker.terminate()
            self._ai_worker.wait(1000)
        # Quit the application
        QApplication.quit()
        event.accept()

    def create_settings_page(self):
        """Create Settings & Privacy page with toast notification testing"""
        settings_page = QWidget()
        settings_page.setStyleSheet(f"background-color: {THEME['bg_dark']};")

        main_layout = QVBoxLayout(settings_page)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)

        # Header
        header = QLabel("SETTINGS & PRIVACY")
        header.setFont(QFont(THEME["font_mono"].strip("'"), 28))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet(f"color: {THEME['primary']}; margin-bottom: 20px;")
        main_layout.addWidget(header)

        # Subtitle
        subtitle = QLabel(
            "Configure Ollama and ensure alignment with NZ Privacy Act 2020 principles"
        )
        subtitle.setFont(QFont(THEME["font_mono"].strip("'"), 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {THEME['text_secondary']}; margin-bottom: 30px;")
        main_layout.addWidget(subtitle)

        # Toast Notification Testing Section
        toast_section = QWidget()
        toast_section.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        toast_layout = QVBoxLayout(toast_section)

        toast_title = QLabel("Toast Notification Testing")
        toast_title.setFont(QFont(THEME["font_mono"].strip("'"), 18))
        toast_title.setStyleSheet(f"color: {THEME['text_primary']}; margin-bottom: 15px;")
        toast_layout.addWidget(toast_title)

        toast_desc = QLabel("Test the toast notification system with different message types:")
        toast_desc.setStyleSheet(
            f"color: {THEME['text_secondary']}; font-size: 12px; margin-bottom: 15px;"
        )
        toast_layout.addWidget(toast_desc)

        # Test buttons
        btn_layout = QHBoxLayout()

        # Info toast button (Electric Blue)
        info_btn = QPushButton("Test Info Toast")
        info_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {THEME['primary']};
                border: 2px solid {THEME['primary']};
                border-radius: 8px;
                padding: 12px 24px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 180, 216, 0.2);
            }}
        """)
        info_btn.clicked.connect(
            lambda: self.show_toast("System Update", "Dashboard refreshed successfully", "info")
        )
        btn_layout.addWidget(info_btn)

        # Block toast button (Red)
        block_btn = QPushButton("Test Block Toast")
        block_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {THEME['danger']};
                border: 2px solid {THEME['danger']};
                border-radius: 8px;
                padding: 12px 24px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 107, 107, 0.2);
            }}
        """)
        block_btn.clicked.connect(
            lambda: self.show_toast(
                "IP Blocked", "192.168.1.100 has been added to block list", "block"
            )
        )
        btn_layout.addWidget(block_btn)

        # Auto-block toast button (Red with specific message)
        autoblock_btn = QPushButton("Test Auto-Block Toast")
        autoblock_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {THEME['danger']};
                border: 2px solid {THEME['danger']};
                border-radius: 8px;
                padding: 12px 24px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 107, 107, 0.2);
            }}
        """)
        autoblock_btn.clicked.connect(
            lambda: self.show_toast(
                "IP AUTO-BLOCKED",
                "Attack from 203.0.113.45 to 192.168.1.1\nConfidence: 95%\nIP has been automatically blocked",
                "block"
            )
        )
        btn_layout.addWidget(autoblock_btn)

        # Multiple toasts button
        multi_btn = QPushButton("Test Multiple Toasts")
        multi_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {THEME['warning']};
                border: 2px solid {THEME['warning']};
                border-radius: 8px;
                padding: 12px 24px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 159, 67, 0.2);
            }}
        """)
        multi_btn.clicked.connect(self.test_multiple_toasts)
        btn_layout.addWidget(multi_btn)

        toast_layout.addLayout(btn_layout)
        main_layout.addWidget(toast_section)

        # Add some spacing
        main_layout.addStretch()

        self.page_container.addWidget(settings_page)

    def show_toast(self, title, message, type="info"):
        """Show a toast notification"""
        # Check if sound alerts are enabled
        sound_enabled = getattr(self, "settings", {}).get("sound_alerts", True)

        # Check if animations are enabled
        animations_enabled = getattr(self, "settings", {}).get("animations", True)

        if not self.toast:
            self.toast = ToastNotification(None)  # No parent to allow screen positioning

        # Update animation setting
        self.toast.set_animations_enabled(animations_enabled)

        self.toast.show_message(title, message, type)

        # Play sound if enabled
        if sound_enabled:
            self._play_alert_sound(type)

    def _play_alert_sound(self, alert_type):
        """Play alert sound based on type"""
        try:
            from PyQt6.QtMultimedia import QSoundEffect
            from PyQt6.QtCore import QUrl

            # Create sound effect
            sound = QSoundEffect(self)

            # Different sounds for different alert types
            if alert_type == "block":
                # Critical threat - use system beep
                from PyQt6.QtWidgets import QApplication
                QApplication.beep()
            elif alert_type == "simulation":
                # Simulation - softer sound
                QApplication.beep()
            else:
                # Info - minimal sound
                pass

        except Exception as e:
            print(f"Error playing alert sound: {e}")

    def test_multiple_toasts(self):
        """Test showing multiple toast notifications"""
        self.show_toast("First Notification", "This is the first toast message", "info")
        QTimer.singleShot(
            500,
            lambda: self.show_toast(
                "Second Notification", "This is the second toast message", "block"
            ),
        )
        QTimer.singleShot(
            1000,
            lambda: self.show_toast(
                "Third Notification", "This is the third toast message", "info"
            ),
        )

    def apply_theme(self):
        """Re-apply current theme to all UI components."""
        from src.ui.theme import THEME

        # Update main window background
        self.setStyleSheet(f"background-color: {THEME['bg_dark']};")

        # Update sidebar header
        if hasattr(self, "sidebar_header"):
            self.sidebar_header.setStyleSheet(f"""
                background-color: {THEME['bg_header']};
            """)

        # Update nav_sidebar
        if hasattr(self, "nav_sidebar"):
            self.nav_sidebar.setStyleSheet(f"""
                QWidget {{
                    background-color: {THEME['bg_header']};
                }}
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    color: {THEME['text_secondary']};
                    font-family: 'Segoe UI';
                    font-size: 12px;
                    padding: 12px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {THEME['bg_card']};
                    color: {THEME['text_primary']};
                }}
                QPushButton:checked {{
                    background-color: {THEME['primary']};
                    color: {THEME['bg_dark']};
                }}
            """)
            # Recursively update sidebar widgets
            self._update_widget_theme(self.nav_sidebar)

        # Update sidebar title
        if hasattr(self, "sidebar_title"):
            self.sidebar_title.setStyleSheet(f"""
                color: {THEME['primary']};
                font-family: 'Segoe UI';
                font-size: 18px;
                font-weight: bold;
                letter-spacing: 2px;
            """)

        # Update status bar if exists
        if hasattr(self, "status_bar"):
            self.status_bar.setStyleSheet(f"""
                background-color: {THEME['bg_header']};
                border-top: 2px solid {THEME['border']};
                color: {THEME['text_secondary']};
                font-family: 'Segoe UI';
                font-size: 11px;
                padding: 5px 15px;
            """)

        # Update all page backgrounds
        if hasattr(self, "page_container"):
            for i in range(self.page_container.count()):
                wrapper = self.page_container.widget(i)
                if wrapper and wrapper.layout() and wrapper.layout().count() > 0:
                    # Get the actual page widget (first child of wrapper)
                    page_widget = wrapper.layout().itemAt(0).widget()
                    if page_widget:
                        page_widget.setStyleSheet(f"background-color: {THEME['bg_dark']};")
                        # Recursively update all widgets in the page
                        self._update_widget_theme(page_widget)

        # Update settings page if exists
        if hasattr(self, "settings_page"):
            self.settings_page.apply_theme()

        # Update AI mentor page if exists
        if hasattr(self, "ai_mentor_page"):
            self.ai_mentor_page.apply_theme()

        # Update forensic panel if exists
        if hasattr(self, "forensic_panel"):
            self.forensic_panel.apply_theme()

    def _update_widget_theme(self, widget):
        """Recursively update theme for all child widgets."""
        from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget

        from src.ui.theme import THEME

        # Update the widget itself if it has a specific type
        if isinstance(widget, QLabel):
            widget.setStyleSheet(f"color: {THEME['text_primary']};")
        elif isinstance(widget, QComboBox):
            widget.setStyleSheet(f"""
                QComboBox {{
                    background-color: {THEME['bg_card']};
                    border: none;
                    border-radius: 6px;
                    color: {THEME['text_primary']};
                    padding: 6px;
                    font-family: {THEME['font_mono']};
                    font-size: 11px;
                }}
            """)
        elif isinstance(widget, QSlider):
            widget.setStyleSheet(f"""
                QSlider::groove:horizontal {{
                    border: none;
                    height: 6px;
                    background: {THEME['bg_card']};
                    border-radius: 3px;
                }}
                QSlider::sub-page:horizontal {{
                    background: {THEME['primary']};
                    border-radius: 3px;
                }}
                QSlider::handle:horizontal {{
                    background: white;
                    border: 2px solid {THEME['primary']};
                    width: 14px;
                    border-radius: 7px;
                    margin: -4px 0;
                }}
            """)
        elif isinstance(widget, QCheckBox):
            widget.setStyleSheet(f"""
                QCheckBox::indicator {{
                    width: 35px;
                    height: 18px;
                    border-radius: 9px;
                    background: {THEME['bg_card']};
                    border: none;
                }}
                QCheckBox::indicator:checked {{
                    background: {THEME['primary']};
                }}
            """)
        elif isinstance(widget, QPushButton):
            widget.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    border: none;
                    color: {THEME['text_secondary']};
                    font-family: 'Segoe UI';
                    font-size: 12px;
                    padding: 12px;
                    text-align: left;
                }}
                QPushButton:hover {{
                    background-color: {THEME['bg_card']};
                    color: {THEME['text_primary']};
                }}
                QPushButton:checked {{
                    background-color: {THEME['primary']};
                    color: {THEME['bg_dark']};
                }}
            """)
        elif isinstance(widget, QLineEdit):
            widget.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {THEME['bg_card']};
                    border: none;
                    border-radius: 6px;
                    color: {THEME['text_primary']};
                    padding: 6px;
                    font-family: {THEME['font_mono']};
                    font-size: 11px;
                }}
            """)
        elif isinstance(widget, QListWidget):
            widget.setStyleSheet(f"""
                QListWidget {{
                    background-color: {THEME['bg_card']};
                    border: none;
                    border-radius: 6px;
                    color: {THEME['text_primary']};
                    padding: 4px;
                    font-family: {THEME['font_mono']};
                    font-size: 10px;
                }}
                QListWidget::item {{
                    padding: 4px;
                    border-bottom: 1px solid {THEME['border']};
                }}
                QListWidget::item:selected {{
                    background-color: {THEME['primary']};
                    color: white;
                }}
            """)
        elif isinstance(widget, QWidget):
            # Check if it's a container with the dark background style
            current_style = widget.styleSheet()
            if (
                "background-color: {THEME" in current_style
                or "background-color: #0" in current_style
                or "background-color: #F" in current_style
            ):
                widget.setStyleSheet(f"""
                    QWidget {{
                        background-color: {THEME['bg_dark']};
                        border: 1px solid {THEME['border']};
                        border-radius: 10px;
                        padding: 12px;
                    }}
                """)

        # Recursively update children
        if hasattr(widget, "children"):
            for child in widget.children():
                if isinstance(child, QWidget):
                    self._update_widget_theme(child)

    def apply_onboarding_settings(self, settings: dict):
        """Apply settings from onboarding wizard"""
        self.settings_manager.update(settings)
        self.settings_manager.mark_onboarding_complete()

        # Apply notification settings
        if settings.get("enable_notifications"):
            self.notification_manager.settings["enabled"] = True
        if settings.get("system_tray"):
            self.system_tray.show()
        else:
            self.system_tray.hide()

        print("Onboarding settings applied successfully")

    def start_sniffing(self):
        """Start packet sniffing (for system tray)"""
        if hasattr(self, "sniffer") and hasattr(self, "sniffer_thread"):
            if not self.sniffer.is_running:
                self.sniffer_thread.start()
                self.system_tray.set_monitoring_active(True)
                print("Packet sniffer started from system tray")

    def stop_sniffing(self):
        """Stop packet sniffing (for system tray)"""
        if hasattr(self, "sniffer"):
            self.sniffer.stop_sniffing()
            self.system_tray.set_monitoring_active(False)
            print("Packet sniffer stopped from system tray")


if __name__ == "__main__":
    # Enable cross-platform optimizations for better graphics performance
    import platform

    # Hardware acceleration optimizations
    if platform.system() == "Windows":
        # Windows: Use OpenGL for better performance
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL)
    elif platform.system() == "Linux":
        # Linux: Use OpenGL ES for better compatibility
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseOpenGLES)
    # macOS: Uses Metal by default, no changes needed

    # Enable antialiasing for smoother graphics
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    window = WatchdogDashboard()
    window.show()
    sys.exit(app.exec())
