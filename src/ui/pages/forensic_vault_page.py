"""Forensic Vault page implementation."""
import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QPushButton, QScrollArea,
    QFrame, QHeaderView, QToolButton, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from src.ui.theme import THEME


class ForensicVaultPage:
    """Forensic Vault page for viewing and analyzing flagged incidents."""
    
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.vault_table = None
        self.vault_search = None
        
    def create(self):
        """Create and return the forensic vault page widget."""
        vault_page = QWidget()
        vault_page.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        
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
        vault_subtitle.setStyleSheet(f"color: {THEME['text_secondary']};")
        main_layout.addWidget(vault_subtitle)

        # Search bar layout (responsive)
        search_layout = QHBoxLayout()
        search_label = QLabel("Search Flagged Incidents:")
        search_label.setStyleSheet(f"color: {THEME['text_primary']}; font-family: {THEME['font_mono']};")
        self.vault_search = QLineEdit()
        self.vault_search.setPlaceholderText("Enter IP address, protocol, or threat type...")
        self.vault_search.setStyleSheet(f"""
            QLineEdit {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
                color: {THEME['text_primary']};
                padding: 8px;
                font-family: {THEME['font_mono']};
            }}
            QLineEdit:focus {{
                border: 1px solid {THEME['primary']};
            }}
        """)
        self.vault_search.textChanged.connect(self._filter_vault_table)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.vault_search, stretch=1)
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
                gridline-color: #1E3A5F;
            }}
            QTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid #1E3A5F;
                background-color: #0F2642;
            }}
            QTableWidget::item:selected {{
                background-color: {THEME['primary']};
                color: {THEME['bg_dark']};
            }}
            QTableCornerButton::section {{
                background-color: #0A1628;
                border: none;
                border-top-left-radius: 13px;
            }}
            QHeaderView::section {{
                background-color: #0A1628;
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
        
        # Make columns stretch to fill width
        header = self.vault_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)
        
        self.vault_table.verticalHeader().setDefaultSectionSize(55)
        self.vault_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.vault_table.itemDoubleClicked.connect(self._show_forensic_analysis)
        
        table_layout.addWidget(self.vault_table, stretch=1)
        scroll_area.setWidget(table_container)
        main_layout.addWidget(scroll_area, stretch=1)

        # Refresh button
        vault_refresh_btn = QPushButton("Load Flagged Incidents")
        vault_refresh_btn.clicked.connect(self.dashboard.load_flagged_incidents)
        vault_refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {THEME['primary']};
                border: 2px solid {THEME['primary']};
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-family: {THEME['font_mono']};
            }}
            QPushButton:hover {{
                background-color: rgba(0, 180, 216, 0.2);
            }}
        """)
        main_layout.addWidget(vault_refresh_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        return vault_page
        
    def _filter_vault_table(self, text):
        """Filter table rows based on search text."""
        for row in range(self.vault_table.rowCount()):
            show_row = False
            for col in range(self.vault_table.columnCount()):
                item = self.vault_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    show_row = True
                    break
            self.vault_table.setRowHidden(row, not show_row)
            
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
