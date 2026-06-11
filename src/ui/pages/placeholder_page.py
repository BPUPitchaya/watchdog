"""Placeholder page for features not yet implemented."""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.ui.theme import THEME


class PlaceholderPage:
    """Placeholder page for future implementation with universal dark teal theme."""

    def __init__(self, dashboard):
        self.dashboard = dashboard

    def create(self, title, description):
        """Create and return the placeholder page widget."""
        page = QWidget()
        page.setStyleSheet(f"background-color: {THEME['bg_dark']};")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)

        page_title = QLabel(title)
        page_title.setFont(QFont(THEME["font_mono"].strip("'"), 28))
        page_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page_title.setStyleSheet(f"color: {THEME['primary']};")
        layout.addWidget(page_title)

        page_desc = QLabel(description)
        page_desc.setFont(QFont(THEME["font_mono"].strip("'"), 14))
        page_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        page_desc.setStyleSheet(f"color: {THEME['text_secondary']};")
        layout.addWidget(page_desc)

        coming_soon = QLabel("Coming Soon...")
        coming_soon.setFont(QFont(THEME["font_mono"].strip("'"), 16))
        coming_soon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        coming_soon.setStyleSheet(f"color: {THEME['primary']}; margin-top: 50px;")
        layout.addWidget(coming_soon)

        return page
