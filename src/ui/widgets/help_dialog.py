"""Help dialog widget with screenshot and interactive hotspots."""
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QGraphicsEllipseItem, QGraphicsTextItem,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QRectF, QPointF, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPen, QBrush, QFont
from src.ui.theme import THEME


class HelpHotspot:
    """Defines a clickable help hotspot with explanation."""
    def __init__(self, x, y, title, description, percentage_based=True):
        self.x = x
        self.y = y
        self.title = title
        self.description = description
        self.percentage_based = percentage_based


class HelpDialog(QDialog):
    """Help overlay with screenshot and interactive hotspots."""
    
    def __init__(self, parent, page_name, hotspots):
        super().__init__(parent)
        self.setWindowTitle(f"Help: {page_name}")
        self.setModal(True)
        # Make dialog larger - almost fullscreen
        screen = parent.screen()
        if screen:
            screen_geo = screen.availableGeometry()
            self.resize(int(screen_geo.width() * 0.9), int(screen_geo.height() * 0.9))
        else:
            self.resize(1400, 900)
        
        self.hotspots = hotspots
        self.current_hotspot = None
        
        # Capture screenshot of parent
        self.screenshot = parent.grab()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {THEME['bg_dark']};
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Left: Screenshot with hotspots
        left_widget = self._create_screenshot_widget()
        layout.addWidget(left_widget, stretch=2)
        
        # Right: Explanation panel
        right_panel = self._create_explanation_panel()
        layout.addWidget(right_panel, stretch=1)
    
    def _create_screenshot_widget(self):
        """Create widget showing screenshot with interactive hotspots."""
        container = QWidget()
        container.setStyleSheet(f"""
            background-color: {THEME['bg_card']};
            border: none;
            border-radius: 10px;
        """)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("Page Screenshot - Click the circles to learn")
        title.setStyleSheet(f"""
            color: {THEME['primary']};
            font-size: 16px;
            font-weight: bold;
            padding: 5px;
        """)
        layout.addWidget(title)
        
        # Graphics view for screenshot and hotspots
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("border: none; background: transparent;")
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Scale screenshot to fill available space (larger)
        self.scaled_pixmap = self.screenshot.scaled(
            1000, 750, 
            Qt.AspectRatioMode.KeepAspectRatio, 
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Add screenshot (slightly dimmed)
        self.pixmap_item = QGraphicsPixmapItem(self.scaled_pixmap)
        self.pixmap_item.setOpacity(0.6)
        self.scene.addItem(self.pixmap_item)
        
        # Scale factor for hotspot positions
        self.scale_x = self.scaled_pixmap.width() / self.screenshot.width()
        self.scale_y = self.scaled_pixmap.height() / self.screenshot.height()
        
        # Add hotspots
        self.hotspot_items = []
        for spot in self.hotspots:
            self._add_hotspot(spot)
        
        layout.addWidget(self.view)
        
        return container
    
    def _add_hotspot(self, spot):
        """Add clickable hotspot circle to screenshot."""
        # Calculate position based on whether it's percentage-based or absolute
        if spot.percentage_based:
            # Percentage-based: convert to actual coordinates
            scaled_x = (spot.x / 100) * self.scaled_pixmap.width()
            scaled_y = (spot.y / 100) * self.scaled_pixmap.height()
        else:
            # Absolute: scale with screenshot
            scaled_x = spot.x * self.scale_x
            scaled_y = spot.y * self.scale_y
        
        # Create circle
        circle = QGraphicsEllipseItem(
            scaled_x - 20, scaled_y - 20, 40, 40
        )
        circle.setBrush(QBrush(QColor(THEME['primary'])))
        circle.setPen(QPen(QColor("white"), 3))
        circle.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Add glow effect
        circle.setAcceptHoverEvents(True)
        
        self.scene.addItem(circle)
        
        
        # Store items for hover effects
        self.hotspot_items.append((circle, spot))
        
        # Click handler
        circle.mousePressEvent = lambda e, s=spot: self._show_explanation(s)
    
    def _create_explanation_panel(self):
        """Create side panel showing explanations."""
        panel = QFrame()
        panel.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME['bg_card']};
                border: none;
                border-radius: 10px;
            }}
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("Beginner's Guide")
        header.setStyleSheet(f"""
            color: {THEME['primary']};
            font-size: 22px;
            font-weight: bold;
        """)
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel("Click the numbered circles on the screenshot to learn about each section.")
        instructions.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 12px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        layout.addSpacing(10)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet(f"background-color: {THEME['border']};")
        divider.setFixedHeight(2)
        layout.addWidget(divider)
        
        layout.addSpacing(10)
        
        # Explanation content area
        content_widget = QWidget()
        content_widget.setStyleSheet(f"""
            background-color: {THEME['bg_dark']};
            border: none;
            border-radius: 8px;
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(10)
        
        # Title
        self.explanation_title = QLabel("Select a Section")
        self.explanation_title.setStyleSheet(f"""
            color: {THEME['text_primary']};
            font-size: 18px;
            font-weight: bold;
        """)
        self.explanation_title.setWordWrap(True)
        content_layout.addWidget(self.explanation_title)
        
        # Description
        self.explanation_text = QLabel(
            "Click any highlighted circle on the screenshot to see what that section does. "
            "Each section has a simple explanation to help you understand the dashboard."
        )
        self.explanation_text.setStyleSheet(f"""
            color: {THEME['text_secondary']};
            font-size: 13px;
            line-height: 1.5;
        """)
        self.explanation_text.setWordWrap(True)
        content_layout.addWidget(self.explanation_text)
        
        layout.addWidget(content_widget)
        
        layout.addStretch()
        
        # Tips section
        tips_widget = QWidget()
        tips_widget.setStyleSheet(f"""
            background-color: {THEME['bg_header']};
            border: none;
            border-radius: 5px;
        """)
        tips_layout = QVBoxLayout(tips_widget)
        tips_layout.setContentsMargins(12, 12, 12, 12)
        
        tips_label = QLabel("Pro Tips")
        tips_label.setStyleSheet(f"color: {THEME['warning']}; font-weight: bold; font-size: 13px;")
        tips_layout.addWidget(tips_label)
        
        tips_content = QLabel(
            "• Hover over charts for detailed info\n"
            "• Right-click tables for more options\n"
            "• Use AI Assistant to analyze threats"
        )
        tips_content.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 11px;")
        tips_layout.addWidget(tips_content)
        
        layout.addWidget(tips_widget)
        
        layout.addSpacing(15)
        
        # Close button
        close_btn = QPushButton("✓ Got it!")
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {THEME['primary']};
                border: none;
                border-radius: 8px;
                color: white;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {THEME['secondary']};
                border: none;
            }}
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        return panel
    
    def _show_explanation(self, hotspot):
        """Update side panel with hotspot explanation."""
        self.current_hotspot = hotspot
        self.explanation_title.setText(hotspot.title)
        self.explanation_text.setText(hotspot.description)
        
        # Highlight selected hotspot - change colors only (no scaling to avoid misalignment)
        for circle, spot_item in self.hotspot_items:
            if spot_item == hotspot:
                # Selected: Green fill, thick white border
                circle.setBrush(QBrush(QColor(THEME['success'])))
                circle.setPen(QPen(QColor("white"), 5))
            else:
                # Not selected: Primary fill, thin white border
                circle.setBrush(QBrush(QColor(THEME['primary'])))
                circle.setPen(QPen(QColor("white"), 3))
