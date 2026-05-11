"""Autonomous Shield page implementation."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QScrollArea, QFrame, QHeaderView,
    QSlider, QMessageBox, QSizePolicy, QDial
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QGraphicsDropShadowEffect

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
    
    def _add_shadow(self, widget, blur=20, x_offset=0, y_offset=4):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setXOffset(x_offset)
        shadow.setYOffset(y_offset)
        shadow.setColor(Qt.GlobalColor.black)
        widget.setGraphicsEffect(shadow)
        
    def _create_reason_tag(self, reason):
        """Create styled text based on severity."""
        styles = {
            "Suspicious port scanning": '<span style="color: #FF6B6B; font-weight: bold; font-size: 11px;">%s</span>',
            "Multiple failed login attempts": '<span style="color: #FFD93D; font-weight: 600; font-size: 11px;">%s</span>',
            "Known Malicious IP": '<span style="color: #FF4444; font-weight: bold; font-size: 12px;">%s</span>'        }
        style = styles.get(reason, '<span style="color: #6BCF7F; font-size: 11px;">%s</span>')
        return style % reason
    
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
        self._add_shadow(blocked_container)
        blocked_table_layout = QVBoxLayout(blocked_container)
        blocked_table_layout.setContentsMargins(0, 0, 0, 0)
        blocked_table_layout.setSpacing(0)
        
        # IP table widget
        self.blocked_ip_table = QTableWidget()
        self.blocked_ip_table.setColumnCount(4)
        self.blocked_ip_table.setHorizontalHeaderLabels(["Source Ip", "Reason", "Blocked Time", "Status"])
        self.blocked_ip_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: transparent;
                border: none;
                border-radius: 15px;
                color: {THEME['text_primary']};
                font-family: {THEME['font_mono']};
            }}
            QTableWidget::item {{
                padding: 12px;
                border-bottom: 1px solid #1B2A38;
                background-color: #0f2642;
            }}
            QTableWidget::item:selected {{
                background-color: {THEME['primary']};
                color: {THEME['bg_dark']};
            }}
            QHeaderView::section {{
                background-color: #0B1117;
                color: {THEME['primary']};
                border: none;
                padding: 12px;
                font-family: {THEME['font_mono']};
            }}
        """)
        
        # Make table stretch
        header = self.blocked_ip_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setStretchLastSection(True)
        
        self.blocked_ip_table.verticalHeader().setVisible(False)
        self.blocked_ip_table.horizontalHeader().setVisible(True)
        self.blocked_ip_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.blocked_ip_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Start with empty table
        self.blocked_ip_table.setRowCount(0)

            
        for i in range(len([])):
            self.blocked_ip_table.setRowHeight(i, 50)

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
                padding: 15px;

            }}
        """)
        self._add_shadow(confidence_container)

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
            }
            QSlider::handle:horizontal {
                background: white;
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
        self._add_shadow(stats_container)

        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setSpacing(10)
        stats_layout.setContentsMargins(15, 15, 15, 15)
        
        # Statistics table
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(2)
        self.stats_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: transparent;
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
        
        # Statistics data - start with empty values
        stats_data = [
            ("Total Blocked", "0"),
            ("Auto Blocked", "0"), 
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
        """Update statistics table with current values."""
        # This should be called from main dashboard to refresh stats
        total_blocked = self.blocked_ip_table.rowCount()
        
        # Get manual block count from dashboard
        manual_blocked = 0
        if hasattr(self.dashboard, 'manual_block_count'):
            manual_blocked = self.dashboard.manual_block_count
        
        # Calculate auto blocked (total - manual)
        auto_blocked = total_blocked - manual_blocked
        
        # Update stats table with calculated values
        self.stats_table.setItem(0, 1, QTableWidgetItem(str(total_blocked)))  # Total Blocked
        self.stats_table.setItem(1, 1, QTableWidgetItem(str(auto_blocked)))  # Auto Blocked
        self.stats_table.setItem(2, 1, QTableWidgetItem(str(manual_blocked)))  # Manual Blocked
        
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
                
                # Check if this was a manually blocked IP and decrement counter
                if hasattr(self.dashboard, 'manual_block_count'):
                    # Check if IP is in manual_blocked_ips set (most reliable method)
                    is_manual_block = hasattr(self.dashboard, 'manual_blocked_ips') and ip_address in self.dashboard.manual_blocked_ips
                    print(f"Checking IP {ip_address} - Is manual block: {is_manual_block}")
                    print(f"Manual blocked IPs set: {getattr(self.dashboard, 'manual_blocked_ips', 'Not found')}")
                    
                    if is_manual_block:
                        self.dashboard.manual_block_count = max(0, self.dashboard.manual_block_count - 1)
                        # Remove from manual_blocked_ips set
                        self.dashboard.manual_blocked_ips.discard(ip_address)
                        print(f"Decremented manual block count to {self.dashboard.manual_block_count}")
                        print(f"Removed {ip_address} from manual_blocked_ips set")
                
                self._update_blocking_statistics()
                
    def _update_blocking_statistics(self):
        """Update the blocking statistics table."""
        total_blocked = self.blocked_ip_table.rowCount()

        #Get manual block count from dashboard
        manual_blocked = 0
        if hasattr(self.dashboard, 'manual_block_count'):
            manual_blocked = self.dashboard.manual_block_count

        #Calculate auto blocked (total - manual)
        auto_blocked = total_blocked - manual_blocked
        
        print(f"Statistics Update - Total: {total_blocked}, Manual: {manual_blocked}, Auto: {auto_blocked}")
        
        # Update the stats table
        self.stats_table.setItem(0, 1, QTableWidgetItem(str(total_blocked)))
        self.stats_table.setItem(1, 1, QTableWidgetItem(str(auto_blocked)))
        self.stats_table.setItem(2, 1, QTableWidgetItem(str(manual_blocked)))
    
    def _update_shield_statistics(self):
        """Update shield statistics from dashboard data."""
        self._update_blocking_statistics()
    def _sync_blocked_ips(self):
        """Sync blocked IPs from dashboard to local table."""
        import traceback
        print(f"_sync_blocked_ips called from:")
        traceback.print_stack(limit=3)
        if hasattr(self.dashboard, 'blocked_ips'):
            # Completely rebuild table to avoid caching issues
            self.blocked_ip_table.clearContents()
            self.blocked_ip_table.setRowCount(0)
        
            # Re-add all blocked IPs from dashboard
            import datetime
            for i, ip in enumerate(self.dashboard.blocked_ips):
                # Create row with IP and default values
                self.blocked_ip_table.insertRow(i)
            
                # IP Address
                ip_item = QTableWidgetItem(ip)
                ip_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.blocked_ip_table.setItem(i, 0, ip_item)
            
                # Reason - check if this is a manual block
                reason_label = QLabel()
                is_manual = hasattr(self.dashboard, 'manual_blocked_ips') and ip in self.dashboard.manual_blocked_ips
                if is_manual:
                    reason_label.setText(self._create_reason_tag("Blocked from Vault"))
                else:
                    reason_label.setText(self._create_reason_tag("Auto Blocked"))
                reason_label.setStyleSheet("background-color: transparent; border: none;")
                self.blocked_ip_table.setCellWidget(i, 1, reason_label)
            
                # Time
                time_item = QTableWidgetItem(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.blocked_ip_table.setItem(i, 2, time_item)
            
                # Status
                status_item = QTableWidgetItem("Active")
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.blocked_ip_table.setItem(i, 3, status_item)
            
                # Set row height
                self.blocked_ip_table.setRowHeight(i, 50)
        
        # Force complete UI repaint and update
        self.blocked_ip_table.repaint()
        self.blocked_ip_table.viewport().repaint()
        self.blocked_ip_table.update()
        self.blocked_ip_table.viewport().update()
        
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
