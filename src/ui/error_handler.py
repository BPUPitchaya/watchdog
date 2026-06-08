"""
Error Handler with User-Friendly Messages
Provides user-friendly error messages and dialogs
"""

from PyQt6.QtWidgets import (QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QTextEdit, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import traceback
import sys
from typing import Optional, Dict, Any


class ErrorMessages:
    """User-friendly error messages"""
    
    NETWORK_ERRORS = {
        'permission_denied': {
            'title': 'Permission Required',
            'message': 'Network monitoring requires administrator privileges.',
            'solution': 'Please run the application with administrator/sudo privileges.',
            'icon': QMessageBox.Icon.Warning
        },
        'interface_not_found': {
            'title': 'Network Interface Not Found',
            'message': 'Could not find a suitable network interface for monitoring.',
            'solution': 'Please check your network connections and try again.',
            'icon': QMessageBox.Icon.Warning
        },
        'capture_failed': {
            'title': 'Packet Capture Failed',
            'message': 'Failed to start network packet capture.',
            'solution': 'Check if another application is using the network interface.',
            'icon': QMessageBox.Icon.Critical
        }
    }
    
    ML_ERRORS = {
        'model_not_found': {
            'title': 'ML Model Not Found',
            'message': 'The machine learning model file could not be loaded.',
            'solution': 'Please ensure the model file exists in the models directory.',
            'icon': QMessageBox.Icon.Warning
        },
        'prediction_failed': {
            'title': 'Prediction Failed',
            'message': 'Failed to analyze network traffic with ML model.',
            'solution': 'The model may need to be retrained or the data format may be incorrect.',
            'icon': QMessageBox.Icon.Warning
        },
        'feature_extraction_failed': {
            'title': 'Feature Extraction Failed',
            'message': 'Could not extract features from network packet.',
            'solution': 'Packet format may be incompatible. Traffic monitoring will continue without ML analysis.',
            'icon': QMessageBox.Icon.Warning
        }
    }
    
    AI_ERRORS = {
        'ai_not_available': {
            'title': 'AI Assistant Unavailable',
            'message': 'The AI assistant (Ollama) could not be connected.',
            'solution': 'AI features will be disabled. You can still use manual threat analysis. Install Ollama to enable AI features.',
            'icon': QMessageBox.Icon.Information
        },
        'ai_connection_failed': {
            'title': 'AI Connection Failed',
            'message': 'Failed to connect to AI assistant server.',
            'solution': 'Ensure Ollama is running with: ollama serve. AI features will be temporarily disabled.',
            'icon': QMessageBox.Icon.Warning
        },
        'ai_response_timeout': {
            'title': 'AI Response Timeout',
            'message': 'AI assistant took too long to respond.',
            'solution': 'The request was cancelled. Try again or use manual analysis.',
            'icon': QMessageBox.Icon.Warning
        },
        'ai_model_not_found': {
            'title': 'AI Model Not Found',
            'message': 'The requested AI model is not available in Ollama.',
            'solution': 'Install the model with: ollama pull <model-name>',
            'icon': QMessageBox.Icon.Warning
        }
    }
    
    FILE_ERRORS = {
        'file_not_found': {
            'title': 'File Not Found',
            'message': 'A required file could not be found.',
            'solution': 'Please check if the file exists and you have read permissions.',
            'icon': QMessageBox.Icon.Warning
        },
        'permission_denied': {
            'title': 'File Access Denied',
            'message': 'Permission denied when accessing file.',
            'solution': 'Please check file permissions and try again.',
            'icon': QMessageBox.Icon.Warning
        },
        'write_failed': {
            'title': 'File Write Failed',
            'message': 'Failed to write data to file.',
            'solution': 'Check disk space and file permissions.',
            'icon': QMessageBox.Icon.Critical
        }
    }
    
    SYSTEM_ERRORS = {
        'memory_error': {
            'title': 'Memory Error',
            'message': 'The application ran out of memory.',
            'solution': 'Close other applications and try again.',
            'icon': QMessageBox.Icon.Critical
        },
        'dependency_missing': {
            'title': 'Missing Dependency',
            'message': 'A required library or dependency is missing.',
            'solution': 'Please install all required dependencies using pip install -r requirements.txt',
            'icon': QMessageBox.Icon.Critical
        }
    }
    
    @classmethod
    def get_message(cls, error_type: str, category: str = 'NETWORK_ERRORS') -> Optional[Dict[str, Any]]:
        """Get error message by type and category"""
        category_dict = getattr(cls, category, {})
        return category_dict.get(error_type)


class ErrorDialog(QDialog):
    """Custom error dialog with detailed information"""
    
    def __init__(self, title: str, message: str, solution: str, 
                 details: str = '', parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(500, 300)
        
        layout = QVBoxLayout()
        
        # Main message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("font-size: 14px; color: #E0E0E0;")
        layout.addWidget(message_label)
        
        # Solution
        solution_label = QLabel(f"<b>Solution:</b> {solution}")
        solution_label.setWordWrap(True)
        solution_label.setStyleSheet("color: #6BCF7F; margin-top: 10px;")
        layout.addWidget(solution_label)
        
        # Details section (collapsible)
        if details:
            self.show_details = QCheckBox("Show technical details")
            self.show_details.setStyleSheet("margin-top: 20px;")
            layout.addWidget(self.show_details)
            
            self.details_text = QTextEdit()
            self.details_text.setPlainText(details)
            self.details_text.setMaximumHeight(150)
            self.details_text.setReadOnly(True)
            self.details_text.setStyleSheet("""
                background-color: #1A1F26;
                color: #E0E0E0;
                border: 1px solid #2A3038;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 11px;
            """)
            self.details_text.hide()
            layout.addWidget(self.details_text)
            
            self.show_details.toggled.connect(self.details_text.setVisible)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            background-color: #3B82F6;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 13px;
            font-weight: 500;
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
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
            }
        """)
        
        self.setLayout(layout)


class ErrorHandler:
    """Main error handler for the application"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.show_technical_details = False
    
    def handle_error(self, error: Exception, error_type: str = 'unknown', 
                    category: str = 'NETWORK_ERRORS', show_dialog: bool = True) -> None:
        """Handle an error with user-friendly message"""
        # Get error message
        error_info = ErrorMessages.get_message(error_type, category)
        
        if error_info:
            title = error_info['title']
            message = error_info['message']
            solution = error_info['solution']
            icon = error_info['icon']
        else:
            title = 'Error'
            message = f'An unexpected error occurred: {str(error)}'
            solution = 'Please try again or contact support if the problem persists.'
            icon = QMessageBox.Icon.Warning
        
        # Get technical details
        details = traceback.format_exc() if self.show_technical_details else ''
        
        if show_dialog:
            self.show_error_dialog(title, message, solution, details)
        else:
            print(f"ERROR: {title} - {message}")
            print(f"Solution: {solution}")
            if details:
                print(f"Details: {details}")
    
    def show_error_dialog(self, title: str, message: str, solution: str, 
                         details: str = '') -> None:
        """Show error dialog to user"""
        dialog = ErrorDialog(title, message, solution, details, self.parent)
        dialog.exec()
    
    def show_critical_error(self, error: Exception, message: str = '') -> None:
        """Show critical error dialog and exit"""
        error_dialog = QMessageBox.critical(
            self.parent,
            'Critical Error',
            f'{message}\n\nThe application will now exit.',
            QMessageBox.StandardButton.Ok
        )
        sys.exit(1)
    
    def show_warning(self, title: str, message: str) -> None:
        """Show warning dialog"""
        QMessageBox.warning(
            self.parent,
            title,
            message,
            QMessageBox.StandardButton.Ok
        )
    
    def show_info(self, title: str, message: str) -> None:
        """Show info dialog"""
        QMessageBox.information(
            self.parent,
            title,
            message,
            QMessageBox.StandardButton.Ok
        )
    
    def set_technical_details(self, show: bool) -> None:
        """Enable/disable technical details in error messages"""
        self.show_technical_details = show


def safe_execute(func, error_handler: ErrorHandler, *args, **kwargs):
    """Decorator/function wrapper for safe execution with error handling"""
    try:
        return func(*args, **kwargs)
    except PermissionError as e:
        error_handler.handle_error(e, 'permission_denied', 'NETWORK_ERRORS')
    except FileNotFoundError as e:
        error_handler.handle_error(e, 'file_not_found', 'FILE_ERRORS')
    except MemoryError as e:
        error_handler.handle_error(e, 'memory_error', 'SYSTEM_ERRORS')
    except Exception as e:
        error_handler.handle_error(e, 'unknown', 'NETWORK_ERRORS')
    return None
