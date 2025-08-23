"""Theme management utilities"""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from typing import Dict, Any
from .logger import Logger

class ThemeManager:
    """Manages application themes"""
    
    def __init__(self):
        self.logger = Logger()
        self.themes = {
            'light': self.get_light_theme(),
            'dark': self.get_dark_theme()
        }
        self.current_theme = 'light'
    
    def get_light_theme(self) -> Dict[str, str]:
        """Get light theme stylesheet"""
        return {
            'stylesheet': """
                QMainWindow {
                    background-color: #f0f0f0;
                    color: #333333;
                }
                
                QTreeWidget {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    selection-background-color: #3daee9;
                }
                
                QTableWidget {
                    background-color: #ffffff;
                    alternate-background-color: #f5f5f5;
                    gridline-color: #e0e0e0;
                    selection-background-color: #3daee9;
                }
                
                QTabWidget::pane {
                    border: 1px solid #cccccc;
                    background-color: #ffffff;
                }
                
                QTabBar::tab {
                    background-color: #e0e0e0;
                    padding: 8px 16px;
                    margin-right: 2px;
                }
                
                QTabBar::tab:selected {
                    background-color: #ffffff;
                    border-bottom: 2px solid #3daee9;
                }
                
                QPushButton {
                    background-color: #e0e0e0;
                    border: 1px solid #cccccc;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
                
                QPushButton:pressed {
                    background-color: #c0c0c0;
                }
                
                QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                    padding: 4px;
                    border-radius: 2px;
                }
                
                QLineEdit:focus, QTextEdit:focus {
                    border: 2px solid #3daee9;
                }
                
                QMenuBar {
                    background-color: #f0f0f0;
                    border-bottom: 1px solid #cccccc;
                }
                
                QMenuBar::item:selected {
                    background-color: #e0e0e0;
                }
                
                QMenu {
                    background-color: #ffffff;
                    border: 1px solid #cccccc;
                }
                
                QMenu::item:selected {
                    background-color: #3daee9;
                    color: white;
                }
                
                QStatusBar {
                    background-color: #f0f0f0;
                    border-top: 1px solid #cccccc;
                }
                
                QToolBar {
                    background-color: #f0f0f0;
                    border-bottom: 1px solid #cccccc;
                    spacing: 4px;
                }
                
                QSplitter::handle {
                    background-color: #cccccc;
                }
                
                QSplitter::handle:horizontal {
                    width: 2px;
                }
                
                QSplitter::handle:vertical {
                    height: 2px;
                }
            """,
            'name': 'Light Theme'
        }
    
    def get_dark_theme(self) -> Dict[str, str]:
        """Get dark theme stylesheet"""
        return {
            'stylesheet': """
                * {
                    background-color: #2d2d30;
                    color: #cccccc;
                    border: none;
                }
                
                QMainWindow {
                    background-color: #2d2d30;
                    color: #cccccc;
                }
                
                QWidget {
                    background-color: #2d2d30;
                    color: #cccccc;
                }
                
                QTreeWidget {
                    background-color: #383838;
                    border: 1px solid #555555;
                    color: #cccccc;
                    selection-background-color: #007acc;
                    selection-color: #ffffff;
                    outline: none;
                }
                
                QTreeWidget::item {
                    padding: 4px;
                    border: none;
                }
                
                QTreeWidget::item:hover {
                    background-color: #404040;
                }
                
                QTreeWidget::item:selected {
                    background-color: #007acc;
                    color: #ffffff;
                }
                
                QTableWidget {
                    background-color: #383838;
                    alternate-background-color: #404040;
                    gridline-color: #555555;
                    color: #cccccc;
                    selection-background-color: #007acc;
                    selection-color: #ffffff;
                }
                
                QHeaderView::section {
                    background-color: #2d2d30;
                    color: #cccccc;
                    border: 1px solid #555555;
                    padding: 6px;
                    font-weight: bold;
                }
                
                QTabWidget::pane {
                    border: 1px solid #555555;
                    background-color: #383838;
                }
                
                QTabBar::tab {
                    background-color: #2d2d30;
                    color: #cccccc;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border: 1px solid #555555;
                    border-bottom: none;
                }
                
                QTabBar::tab:selected {
                    background-color: #383838;
                    border-bottom: 2px solid #007acc;
                }
                
                QTabBar::tab:hover {
                    background-color: #404040;
                }
                
                QPushButton {
                    background-color: #0e639c;
                    border: 1px solid #007acc;
                    color: #ffffff;
                    padding: 8px 16px;
                    border-radius: 2px;
                    font-weight: bold;
                }
                
                QPushButton:hover {
                    background-color: #1177bb;
                }
                
                QPushButton:pressed {
                    background-color: #005a9e;
                }
                
                QPushButton:disabled {
                    background-color: #555555;
                    color: #888888;
                    border: 1px solid #666666;
                }
                
                QLineEdit, QTextEdit {
                    background-color: #1e1e1e;
                    border: 1px solid #555555;
                    color: #cccccc;
                    padding: 6px;
                    border-radius: 2px;
                }
                
                QLineEdit:focus, QTextEdit:focus {
                    border: 2px solid #007acc;
                    background-color: #252526;
                }
                
                QSpinBox, QDoubleSpinBox {
                    background-color: #1e1e1e;
                    border: 1px solid #555555;
                    color: #cccccc;
                    padding: 4px;
                }
                
                QComboBox {
                    background-color: #1e1e1e;
                    border: 1px solid #555555;
                    color: #cccccc;
                    padding: 4px;
                    min-width: 100px;
                }
                
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 20px;
                    border-left: 1px solid #555555;
                    background-color: #383838;
                }
                
                QComboBox::down-arrow {
                    image: none;
                    border: 2px solid #cccccc;
                    width: 6px;
                    height: 6px;
                    border-top: none;
                    border-left: none;
                    margin-top: -2px;
                }
                
                QComboBox QAbstractItemView {
                    background-color: #383838;
                    border: 1px solid #555555;
                    selection-background-color: #007acc;
                }
                
                QMenuBar {
                    background-color: #2d2d30;
                    color: #cccccc;
                    border-bottom: 1px solid #555555;
                }
                
                QMenuBar::item {
                    padding: 6px 12px;
                    background-color: transparent;
                }
                
                QMenuBar::item:selected {
                    background-color: #404040;
                }
                
                QMenu {
                    background-color: #383838;
                    color: #cccccc;
                    border: 1px solid #555555;
                }
                
                QMenu::item {
                    padding: 6px 20px;
                }
                
                QMenu::item:selected {
                    background-color: #007acc;
                    color: #ffffff;
                }
                
                QStatusBar {
                    background-color: #007acc;
                    color: #ffffff;
                    border: none;
                }
                
                QToolBar {
                    background-color: #2d2d30;
                    border: none;
                    spacing: 4px;
                    padding: 4px;
                }
                
                QSplitter::handle {
                    background-color: #555555;
                }
                
                QSplitter::handle:horizontal {
                    width: 3px;
                }
                
                QSplitter::handle:vertical {
                    height: 3px;
                }
                
                QDialog {
                    background-color: #2d2d30;
                    color: #cccccc;
                }
                
                QGroupBox {
                    color: #cccccc;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                
                QLabel {
                    color: #cccccc;
                    background-color: transparent;
                }
                
                QCheckBox {
                    color: #cccccc;
                    spacing: 8px;
                }
                
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                
                QCheckBox::indicator:unchecked {
                    background-color: #1e1e1e;
                    border: 1px solid #555555;
                }
                
                QCheckBox::indicator:checked {
                    background-color: #007acc;
                    border: 1px solid #007acc;
                }
                
                QScrollBar:vertical {
                    background-color: #2d2d30;
                    width: 16px;
                    border: none;
                }
                
                QScrollBar::handle:vertical {
                    background-color: #555555;
                    border-radius: 8px;
                    min-height: 20px;
                    margin: 2px;
                }
                
                QScrollBar::handle:vertical:hover {
                    background-color: #666666;
                }
                
                QScrollBar:horizontal {
                    background-color: #2d2d30;
                    height: 16px;
                    border: none;
                }
                
                QScrollBar::handle:horizontal {
                    background-color: #555555;
                    border-radius: 8px;
                    min-width: 20px;
                    margin: 2px;
                }
                
                QScrollBar::handle:horizontal:hover {
                    background-color: #666666;
                }
                
                QScrollBar::add-line, QScrollBar::sub-line {
                    background: none;
                }
                
                QListWidget {
                    background-color: #383838;
                    border: 1px solid #555555;
                    color: #cccccc;
                }
                
                QListWidget::item {
                    padding: 4px;
                    border-bottom: 1px solid #555555;
                }
                
                QListWidget::item:selected {
                    background-color: #007acc;
                    color: #ffffff;
                }
                
                QListWidget::item:hover {
                    background-color: #404040;
                }
            """,
            'name': 'Dark Theme'
        }
    
    def apply_theme(self, app_or_widget, theme_name: str) -> bool:
        """Apply theme to application or widget"""
        try:
            if theme_name not in self.themes:
                self.logger.log(f"Unknown theme: {theme_name}", "ERROR")
                return False
            
            theme = self.themes[theme_name]
            
            if hasattr(app_or_widget, 'setStyleSheet'):
                app_or_widget.setStyleSheet(theme['stylesheet'])
            
            self.current_theme = theme_name
            self.logger.log(f"Applied theme: {theme['name']}")
            return True
            
        except Exception as e:
            self.logger.log(f"Failed to apply theme: {str(e)}", "ERROR")
            return False
    
    def get_current_theme(self) -> str:
        """Get current theme name"""
        return self.current_theme
    
    def get_available_themes(self) -> Dict[str, str]:
        """Get list of available themes"""
        return {name: theme['name'] for name, theme in self.themes.items()}
    
    def add_custom_theme(self, name: str, stylesheet: str, display_name: str) -> bool:
        """Add custom theme"""
        try:
            self.themes[name] = {
                'stylesheet': stylesheet,
                'name': display_name
            }
            self.logger.log(f"Added custom theme: {display_name}")
            return True
            
        except Exception as e:
            self.logger.log(f"Failed to add custom theme: {str(e)}", "ERROR")
            return False