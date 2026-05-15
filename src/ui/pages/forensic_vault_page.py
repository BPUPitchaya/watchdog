"""Forensic Vault page implementation."""
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QPushButton, QScrollArea,
    QFrame, QHeaderView, QToolButton, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, QTimer

from src.ui.theme import THEME


class ForensicVaultPage:
    """Forensic Vault page for viewing and analyzing flagged incidents."""
    
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.vault_table = None
        self.vault_search = None
        self.auto_update_timer = None
        self.auto_update_enabled = False
        self.last_update_time = None
        
    def create(self):
        """Create and return the forensic vault page widget."""
        vault_page = QWidget()
        vault_page.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        
        # Start auto-refresh timer (e.g., every 5 seconds)
        self.auto_update_timer = QTimer(vault_page)
        self.auto_update_timer.timeout.connect(self.dashboard.load_flagged_incidents)
        self.auto_update_timer.start(5000)
        self.auto_update_enabled = True
        
        # Main layout that fills the entire page
        main_layout = QVBoxLayout(vault_page)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        vault_header = QLabel("FORENSIC VAULT")
        vault_header.setFont(QFont(THEME['font_mono'].strip("'"), 28))
        vault_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vault_header.setStyleSheet(f"color: {THEME['primary']};")
        main_layout.addWidget(vault_header)

        # Subtitle
        vault_subtitle = QLabel("Translating complex metadata into human-readable advice")
        vault_subtitle.setFont(QFont(THEME['font_mono'].strip("'"), 14))
        vault_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vault_subtitle.setStyleSheet(f"color: {THEME['text_secondary']}; font-family: {THEME['font_mono']};")
        main_layout.addWidget(vault_subtitle)

        # Search bar layout (responsive)
        search_layout = QHBoxLayout()
        # === NEW SEARCH BAR ===
        search_label = QLabel("Search Flagged Incidents:")
        search_label.setStyleSheet(f"color: {THEME['text_primary']}; font-family: {THEME['font_mono']};")
        
        # Search input with button
        self.vault_search = QLineEdit()
        self.vault_search.setPlaceholderText("Enter IP, protocol, or threat type...")
        self.vault_search.setStyleSheet(f"""
            QLineEdit {{
                background-color: {THEME['bg_card']};
                border: 2px solid {THEME['border']};
                border-radius: 8px;
                color: {THEME['text_primary']};
                min-height: 40px;
                padding: 8px 12px;
                font-family: {THEME['font_mono']};
            }}
            QLineEdit:focus {{
                border: 2px solid {THEME['primary']};
            }}
        """)
        
        # Search button
        search_btn = QPushButton("Search")
        search_btn.setMinimumHeight(40)
        search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                color: white;
                border: 2px solid {THEME['primary']};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-family: {THEME['font_mono']};
                font-size: 13px;
            }}
            
            QPushButton:hover {{
                background-color: {THEME['secondary']};
                border: 2px solid {THEME['secondary']};
            }}
            QPushButton:pressed {{
                background-color: {THEME['primary']};
                border: 2px solid white;
            }}
        """)
        
        # Connect search triggers
        search_btn.clicked.connect(self._do_search)
        self.vault_search.returnPressed.connect(self._do_search)
        
        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.setMinimumHeight(40)
        clear_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {THEME['text_secondary']};
                border: 2px solid {THEME['border']};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-family: {THEME['font_mono']};
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {THEME['bg_card']};
                border: 2px solid {THEME['text_secondary']};
                color: {THEME['text_primary']};
            }}
            QPushButton:pressed {{
                background-color: {THEME['bg_card']};
                border: 2px solid white;
            }}
        """)
        clear_btn.clicked.connect(self._clear_search)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.vault_search, stretch=1)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(clear_btn)
        main_layout.addLayout(search_layout)

        # Scroll area for the table (responsive)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        # Table container widget
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)
        
        # Flagged incidents table
        self.vault_table = QTableWidget()
        self.vault_table.setColumnCount(8)
        self.vault_table.setHorizontalHeaderLabels([
            "Timestamp", "Source IP", "Destination IP", "Protocol", 
            "Confidence", "Threat Level", "AI Summary", "Action"
        ])
        self.vault_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: #0A1628;
                border: none;
                border-radius: 15px;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
            }}
            QTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid #1B2A38;
                background-color: #0F2642;
            }}
            QTableWidget::item:selected {{
                background-color: {THEME['primary']};
                color: {THEME['bg_dark']};
            }}
            QTableCornerButton::section {{
                background-color: #0B1117;
                border: none;
                border-top-left-radius: 13px;
            }}
            QHeaderView::section {{
                background-color: #0B1117;
                color: {THEME['primary']};
                border: none;
                padding: 12px;
                font-family: {THEME['font_mono']};
            }}
            QHeaderView::section:first {{
                border-top-left-radius: 13px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 13px;
            }}
        """)
        
        header = self.vault_table.horizontalHeader()
        
        # Set specific resize modes per column
        # Only Timestamp stretches to fill remaining space
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)    # Timestamp - fills space
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)      # Source IP
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)      # Destination IP  
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)      # Protocol
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)      # Confidence
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)      # Threat Level
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)      # AI Summary
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)      # Action
        
        # Set exact column widths per specification
        self.vault_table.setColumnWidth(1, 140)   # Source IP
        self.vault_table.setColumnWidth(2, 140)   # Destination IP  
        self.vault_table.setColumnWidth(3, 80)    # Protocol
        self.vault_table.setColumnWidth(4, 90)    # Confidence
        self.vault_table.setColumnWidth(5, 110)   # Threat Level
        self.vault_table.setColumnWidth(6, 200)   # AI Summary
        self.vault_table.setColumnWidth(7, 240)   # Action

        self.vault_table.verticalHeader().setDefaultSectionSize(55)
        self.vault_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.vault_table.itemDoubleClicked.connect(self._show_forensic_analysis)
        
        table_layout.addWidget(self.vault_table, stretch=1)
        scroll_area.setWidget(table_container)
        main_layout.addWidget(scroll_area, stretch=1)

        # Refresh button
        vault_refresh_btn = QPushButton("Load Flagged Incidents")
        vault_refresh_btn.clicked.connect(self.dashboard.load_flagged_incidents)
        vault_refresh_btn.setMinimumHeight(40)
        vault_refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                color: white;
                border: 2px solid {THEME['primary']};
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-family: {THEME['font_mono']};
                font-size: 13px;
            }}
            
            QPushButton:hover {{
                background-color: {THEME['secondary']};
                border: 2px solid {THEME['secondary']};
            }}
            QPushButton:pressed {{
                background-color: {THEME['primary']};
                border: 2px solid white;
            }}
        """)
        main_layout.addWidget(vault_refresh_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return vault_page
        
    def _do_search(self):
        """Search and filter table rows."""
        search_text = self.vault_search.text().lower().strip()
        
        if not search_text:
            self._clear_search()
            return
        
        # Hide rows that don't match
        for row in range(self.vault_table.rowCount()):
            match_found = False
            for col in range(7):  # Search first 7 columns
                item = self.vault_table.item(row, col)
                if item and search_text in item.text().lower():
                    match_found = True
                    break
            self.vault_table.setRowHidden(row, not match_found)
    
    def _clear_search(self):
        """Clear search and show all rows."""
        self.vault_search.clear()
        for row in range(self.vault_table.rowCount()):
            self.vault_table.setRowHidden(row, False)
            
    def _show_forensic_analysis(self, item):
        """Show forensic analysis dialog for clicked item."""
        row = item.row()
        
        # Get packet data from table
        src_ip = self.vault_table.item(row, 1).text() if self.vault_table.item(row, 1) else ""
        dst_ip = self.vault_table.item(row, 2).text() if self.vault_table.item(row, 2) else ""
        protocol = self.vault_table.item(row, 3).text() if self.vault_table.item(row, 3) else ""
        
        # Create forensic analysis dialog
        dialog = QDialog(self.dashboard)
        dialog.setWindowTitle("Forensic Analysis")
        dialog.setModal(True)
        dialog.setStyleSheet("background-color: #121212; color: white;")
        
        layout = QVBoxLayout(dialog)
        
        title = QLabel(f"Forensic Analysis: {src_ip} → {dst_ip}")
        title.setFont(QFont("Courier New", 16))
        title.setStyleSheet("color: #00D4FF; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Analysis content
        if not self.dashboard.layout_only and self.dashboard.ai_client:
            packet_info = f"Source IP: {src_ip}\nDestination IP: {dst_ip}\nProtocol: {protocol}"
            analysis_text = self.dashboard.process_command(f"analyze packet: {packet_info}")
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
