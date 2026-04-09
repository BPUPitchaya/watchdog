"""Autonomous Shield page implementation."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QScrollArea, QFrame, QHeaderView,
    QSlider, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.ui.theme import THEME


class AutonomousShieldPage:
    """Autonomous Shield page for firewall management and AI confidence control."""
    
    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.blocked_ip_table = None
        self.confidence_slider = None
        self.confidence_label = None
        self.relaxed_btn = None
        self.balanced_btn = None
        self.aggressive_btn = None
        
    def create(self):
        """Create and return the autonomous shield page widget."""
        shield_page = QWidget()
        shield_page.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        
        main_layout = QVBoxLayout(shield_page)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Page title at top left (gray)
        page_title = QLabel("Security Control")
        page_title.setFont(QFont(THEME['font_mono'].strip("'"), 18))
        page_title.setStyleSheet(f"color: {THEME['text_secondary']};")
        main_layout.addWidget(page_title)
        
        # Header - Autonomous Shield (cyan)
        shield_header = QLabel("Autonomous Shield (Security Control)")
        shield_header.setFont(QFont(THEME['font_mono'].strip("'"), 24))
        shield_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shield_header.setStyleSheet(f"color: {THEME['primary']};")
        main_layout.addWidget(shield_header)
        
        # Subtitle
        shield_subtitle = QLabel("Firewall Management and AI Confidence Control")
        shield_subtitle.setFont(QFont(THEME['font_mono'].strip("'"), 12))
        shield_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        shield_subtitle.setStyleSheet(f"color: {THEME['text_primary']};")
        main_layout.addWidget(shield_subtitle)
        
        # Split layout for left/right sections - RESPONSIVE
        split_layout = QHBoxLayout()
        split_layout.setSpacing(20)
        
        # LEFT SECTION - Blocked IP Addresses (expands)
        left_section = QWidget()
        left_layout = QVBoxLayout(left_section)
        left_layout.setSpacing(10)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        blocked_title = QLabel("Blocked IP Addresses")
        blocked_title.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        blocked_title.setStyleSheet(f"color: {THEME['danger']};")
        left_layout.addWidget(blocked_title)
        
        # Scroll area for blocked IPs table
        blocked_scroll = QScrollArea()
        blocked_scroll.setWidgetResizable(True)
        blocked_scroll.setFrameShape(QFrame.Shape.NoFrame)
        blocked_scroll.setStyleSheet("background-color: transparent; border: none;")
        
        # Blocked IPs container
        blocked_container = QWidget()
        blocked_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
            }}
        """)
        blocked_table_layout = QVBoxLayout(blocked_container)
        blocked_table_layout.setContentsMargins(0, 0, 0, 0)
        blocked_table_layout.setSpacing(0)
        
        # IP table widget
        self.blocked_ip_table = QTableWidget()
        self.blocked_ip_table.setColumnCount(2)
        self.blocked_ip_table.setHorizontalHeaderLabels(["IP Address", "Description"])
        self.blocked_ip_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: transparent;
                border: none;
                font-family: {THEME['font_mono']};
                font-size: 13px;
                color: {THEME['text_primary']};
            }}
            QTableWidget::item {{
                padding: 12px 15px;
                border-bottom: 1px solid {THEME['border']};
            }}
            QTableWidget::item:selected {{
                background-color: {THEME['danger']};
                color: white;
            }}
        """)
        
        # Make table stretch
        header = self.blocked_ip_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)
        
        self.blocked_ip_table.verticalHeader().setVisible(False)
        self.blocked_ip_table.horizontalHeader().setVisible(False)
        self.blocked_ip_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.blocked_ip_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Sample data
        sample_blocked_data = [
            ("192.168.100.1", "Suspicious port scanning"),
            ("10.0.0.50", "Multiple failed login attempts"),
            ("203.0.113.1", "Known Malicious IP")
        ]
        self.blocked_ip_table.setRowCount(len(sample_blocked_data))
        for i, (ip, desc) in enumerate(sample_blocked_data):
            self.blocked_ip_table.setItem(i, 0, QTableWidgetItem(ip))
            self.blocked_ip_table.setItem(i, 1, QTableWidgetItem(desc))
        
        blocked_table_layout.addWidget(self.blocked_ip_table, stretch=1)
        blocked_scroll.setWidget(blocked_container)
        left_layout.addWidget(blocked_scroll, stretch=1)
        
        # Unblock button
        unblock_btn = QPushButton("Unblock Selected")
        unblock_btn.setFixedHeight(40)
        unblock_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {THEME['danger']};
                border: 2px solid {THEME['danger']};
                border-radius: 8px;
                font-family: {THEME['font_mono']};
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: rgba(255, 107, 107, 0.2);
            }}
        """)
        unblock_btn.clicked.connect(self._unblock_selected_ip)
        left_layout.addWidget(unblock_btn)
        
        # RIGHT SECTION - Controls (fixed width)
        right_section = QWidget()
        right_section.setMinimumWidth(300)
        right_section.setMaximumWidth(400)
        right_layout = QVBoxLayout(right_section)
        right_layout.setSpacing(15)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # AI Confidence Threshold
        confidence_title = QLabel("AI Confidence Threshold")
        confidence_title.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        confidence_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        confidence_title.setStyleSheet(f"color: {THEME['primary']};")
        right_layout.addWidget(confidence_title)
        
        # Confidence container
        confidence_container = QWidget()
        confidence_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        confidence_layout = QVBoxLayout(confidence_container)
        confidence_layout.setSpacing(10)
        
        # Current threshold label
        threshold_label_layout = QHBoxLayout()
        threshold_label_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        threshold_text = QLabel("Current Threshold :")
        threshold_text.setStyleSheet(f"color: {THEME['text_primary']}; font-family: {THEME['font_mono']};")
        self.confidence_label = QLabel("75%")
        self.confidence_label.setStyleSheet(f"color: {THEME['text_primary']}; font-family: {THEME['font_mono']}; font-weight: bold;")
        threshold_label_layout.addWidget(threshold_text)
        threshold_label_layout.addWidget(self.confidence_label)
        confidence_layout.addLayout(threshold_label_layout)
        
        # Colored slider
        self.confidence_slider = QSlider(Qt.Orientation.Horizontal)
        self.confidence_slider.setRange(0, 100)
        self.confidence_slider.setValue(75)
        self.confidence_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #FF6B6B, stop:0.5 #FFD93D, stop:1 #6BCF7F);
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: white;
                border: 2px solid #00D4FF;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -4px 0;
            }
        """)
        self.confidence_slider.valueChanged.connect(self._update_confidence_threshold)
        confidence_layout.addWidget(self.confidence_slider)
        
        # Mode buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.relaxed_btn = QPushButton("Relaxed")
        self.relaxed_btn.setCheckable(True)
        self.balanced_btn = QPushButton("Balanced")
        self.balanced_btn.setCheckable(True)
        self.aggressive_btn = QPushButton("Aggressive")
        self.aggressive_btn.setCheckable(True)
        
        for btn, color in [(self.relaxed_btn, "#FF6B6B"), (self.balanced_btn, "#FFD93D"), (self.aggressive_btn, "#6BCF7F")]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {color};
                    border: 1px solid {color};
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-family: {THEME['font_mono']};
                    font-size: 11px;
                }}
                QPushButton:checked {{
                    background-color: {color};
                    color: {THEME['bg_dark']};
                }}
            """)
        
        self.relaxed_btn.setChecked(True)
        buttons_layout.addWidget(self.relaxed_btn)
        buttons_layout.addWidget(self.balanced_btn)
        buttons_layout.addWidget(self.aggressive_btn)
        confidence_layout.addLayout(buttons_layout)
        
        # Connect button clicks
        self.relaxed_btn.clicked.connect(lambda: self.confidence_slider.setValue(25))
        self.balanced_btn.clicked.connect(lambda: self.confidence_slider.setValue(50))
        self.aggressive_btn.clicked.connect(lambda: self.confidence_slider.setValue(75))
        
        right_layout.addWidget(confidence_container)
        
        # Blocking Statistics Table
        stats_title = QLabel("Blocking Statistics")
        stats_title.setFont(QFont(THEME['font_mono'].strip("'"), 16))
        stats_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_title.setStyleSheet(f"color: {THEME['warning']};")
        right_layout.addWidget(stats_title)
        
        # Stats container
        stats_container = QWidget()
        stats_container.setMinimumHeight(250)
        stats_container.setStyleSheet(f"""
            QWidget {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 10px;
                padding: 15px;
            }}
        """)
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setSpacing(10)
        stats_layout.setContentsMargins(15, 15, 15, 15)
        
        # Statistics table
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: transparent;
                border: none;
                font-family: {THEME['font_mono']};
                font-size: 13px;
                color: {THEME['text_primary']};
            }}
            QTableWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {THEME['border']};
            }}
        """)
        
        # Make columns stretch
        stats_header = self.stats_table.horizontalHeader()
        stats_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        stats_header.setStretchLastSection(True)
        
        self.stats_table.verticalHeader().setVisible(False)
        self.stats_table.horizontalHeader().setVisible(False)
        self.stats_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.stats_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        
        # Statistics data - matching hi-fi
        stats_data = [
            ("Total Blocked", "4"),
            ("Auto Blocked", "4"),
            ("Manual Blocked", "0"),
        ]
        self.stats_table.setRowCount(len(stats_data))
        for i, (metric, count) in enumerate(stats_data):
            metric_item = QTableWidgetItem(metric)
            count_item = QTableWidgetItem(count)
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.stats_table.setItem(i, 0, metric_item)
            self.stats_table.setItem(i, 1, count_item)
        
        # Set row heights - fill the container completely
        for i in range(len(stats_data)):
            self.stats_table.setRowHeight(i, 60)
        
        # Disable scrollbars completely
        self.stats_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.stats_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Make table expand to fill container
        self.stats_table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        stats_layout.addWidget(self.stats_table, stretch=1)
        right_layout.addWidget(stats_container)
        right_layout.addStretch()
        
        # Add sections to split layout with stretch factors
        split_layout.addWidget(left_section, stretch=2)
        split_layout.addWidget(right_section, stretch=1)
        
        main_layout.addLayout(split_layout, stretch=1)
        
        # Initialize blocked IPs set
        self.dashboard.blocked_ips = set()
        self.dashboard.manual_block_count = 0
        
        return shield_page
        
    def update_shield_statistics(self):
        """Update the statistics table with current values."""
        # This can be called from the main dashboard to refresh stats
        stats_data = [
            ("Total Blocked", str(len(self.dashboard.blocked_ips))),
            ("Auto Blocked", str(len(self.dashboard.blocked_ips) - self.dashboard.manual_block_count)),
            ("Manual Blocked", str(self.dashboard.manual_block_count)),
        ]
        self.stats_table.setRowCount(len(stats_data))
        for i, (metric, count) in enumerate(stats_data):
            metric_item = QTableWidgetItem(metric)
            count_item = QTableWidgetItem(count)
            count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.stats_table.setItem(i, 0, metric_item)
            self.stats_table.setItem(i, 1, count_item)
        
    def _unblock_selected_ip(self):
        """Unblock the selected IP from the table."""
        selected_row = self.blocked_ip_table.currentRow()
        if selected_row >= 0:
            ip_item = self.blocked_ip_table.item(selected_row, 0)
            ip_address = ip_item.text() if ip_item else ""
            
            reply = QMessageBox.question(
                self.dashboard, 
                'Unblock IP', 
                f'Are you sure you want to unblock {ip_address}?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.blocked_ip_table.removeRow(selected_row)
                if ip_address in self.dashboard.blocked_ips:
                    self.dashboard.blocked_ips.remove(ip_address)
                print(f"Unblocked IP: {ip_address}")
                
    def _update_confidence_threshold(self, value):
        """Update the confidence threshold display and color."""
        self.confidence_label.setText(f"{value}%")
        
        # Update label color based on threshold value
        if value < 33:
            color = "#FF6B6B"  # Red for relaxed (low value)
        elif value < 66:
            color = "#FFD93D"  # Yellow for balanced
        else:
            color = "#6BCF7F"  # Green for aggressive (high value)
        
        self.confidence_label.setStyleSheet(f"color: {color}; font-family: {THEME['font_mono']}; font-weight: bold;")
        
        # Update button states - slider left (low) = Relaxed (green), right (high) = Aggressive (red)
        self.relaxed_btn.setChecked(value < 33)
        self.balanced_btn.setChecked(33 <= value < 66)
        self.aggressive_btn.setChecked(value >= 66)
