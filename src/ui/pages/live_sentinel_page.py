"""Live Sentinel (Dashboard) page implementation."""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QSizePolicy, QPushButton
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap

from src.ui.theme import THEME
from src.ui.widgets import SystemHealthGauge, LiveTrafficWidget, RiskAnalysisGauge, ForensicAssistantPanel


class LiveSentinelPage:
    """Main dashboard page with metrics, traffic table, and AI panel."""
    
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.table = None
        self.forensic_panel = None
        
    def create(self):
        """Create and return the live sentinel page widget."""
        # Main content widget with dark background
        main_content = QWidget()
        main_content.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        main_layout = QVBoxLayout(main_content)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # ===== HEADER BAR =====
        header_widget = QWidget()
        header_widget.setFixedHeight(60)
        header_widget.setStyleSheet(f"""
            background-color: {THEME['bg_header']};
            border-bottom: 1px solid {THEME['border']};
        """)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 0, 20, 0)
        header_layout.setSpacing(15)
        
        # Dog/Wolf logo icon
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            scaled_logo = logo_pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        else:
            logo_label.setText("🐺")
            logo_label.setStyleSheet("font-size: 32px;")
        logo_label.setFixedSize(48, 48)
        header_layout.addWidget(logo_label)
        
        # Title
        title_label = QLabel("WatchDog AI")
        title_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {THEME['primary']};")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        main_layout.addWidget(header_widget)
        
        # ===== TOP ROW: Three Metric Cards =====
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(20)
        
        # System Health Card
        health_card = self._create_metric_card("System Health", SystemHealthGauge())
        cards_layout.addWidget(health_card)
        
        # Live Traffic Card
        traffic_card = self._create_metric_card("Live Traffic", LiveTrafficWidget())
        cards_layout.addWidget(traffic_card)
        
        # Risk Analysis Card
        self.right_gauge = RiskAnalysisGauge()
        risk_card = self._create_metric_card("Risk Analysis", self.right_gauge)
        cards_layout.addWidget(risk_card)
        
        main_layout.addLayout(cards_layout)
        
        # ===== BOTTOM ROW: Table and AI Panel =====
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
        # Left side: Traffic Table
        table_container = self._create_traffic_table_section()
        bottom_layout.addWidget(table_container, stretch=2)
        
        # Right side: Forensic Assistant Panel
        self.forensic_panel = ForensicAssistantPanel(dashboard=self.dashboard)
        bottom_layout.addWidget(self.forensic_panel, stretch=1)
        
        main_layout.addLayout(bottom_layout, stretch=1)
        
        return main_content
        
    def _create_metric_card(self, title, widget):
        """Create a styled metric card with title."""
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 12px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 20)
        layout.setSpacing(10)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(f"""
            color: {THEME['text_primary']};
            font-family: {THEME['font_mono']};
            font-size: 14px;
            font-weight: bold;
        """)
        layout.addWidget(title_label)
        
        # Widget (gauge or chart)
        widget.setMinimumHeight(180)
        layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return card
        
    def _create_traffic_table_section(self):
        """Create traffic table with teal header and Refresh button."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Table with teal header
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Source IP", "Destination IP", "Protocol", "Length", "Confidence\nScore", "Action"
        ])
        
        # Make table stretch to fill container
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Stretch all columns to fill width
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)
        
        # Make rows fill vertical space and stretch
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(40)
        
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # Teal header styling with improved sizing
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
                font-size: 12px;
                gridline-color: {THEME['border']};
            }}
            QTableWidget::item {{
                padding: 10px;
                border-bottom: 1px solid {THEME['border']};
            }}
            QTableWidget::item:selected {{
                background-color: {THEME['primary']};
                color: {THEME['bg_dark']};
            }}
            QHeaderView::section {{
                background-color: {THEME['primary']};
                color: white;
                font-family: {THEME['font_mono']};
                font-size: 12px;
                font-weight: bold;
                padding: 12px;
                border: none;
            }}
            QHeaderView::section:first {{
                border-top-left-radius: 8px;
            }}
            QHeaderView::section:last {{
                border-top-right-radius: 8px;
            }}
        """)
        
        layout.addWidget(self.table, stretch=1)
        
        # Refresh button (centered)
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setFixedSize(100, 35)
        refresh_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                color: {THEME['bg_dark']};
                border: none;
                border-radius: 8px;
                font-family: {THEME['font_mono']};
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {THEME['secondary']};
            }}
        """)
        refresh_btn.clicked.connect(self.dashboard.update_ui)
        btn_layout.addWidget(refresh_btn)
        
        layout.addWidget(btn_container)
        
        return container
