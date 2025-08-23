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
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                
                QTreeWidget {
                    background-color: #3c3c3c;
                    border: 1px solid #555555;
                    color: #ffffff;
                    selection-background-color: #4a90e2;
                }
                
                QTableWidget {
                    background-color: #3c3c3c;
                    alternate-background-color: #454545;
                    gridline-color: #555555;
                    color: #ffffff;
                    selection-background-color: #4a90e2;
                }
                
                QHeaderView::section {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 4px;
                }
                
                QTabWidget::pane {
                    border: 1px solid #555555;
                    background-color: #3c3c3c;
                }
                
                QTabBar::tab {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    padding: 8px 16px;
                    margin-right: 2px;
                    border: 1px solid #555555;
                }
                
                QTabBar::tab:selected {
                    background-color: #3c3c3c;
                    border-bottom: 2px solid #4a90e2;
                }
                
                QPushButton {
                    background-color: #4a4a4a;
                    border: 1px solid #666666;
                    color: #ffffff;
                    padding: 6px 12px;
                    border-radius: 4px;
                }
                
                QPushButton:hover {
                    background-color: #5a5a5a;
                }
                
                QPushButton:pressed {
                    background-color: #3a3a3a;
                }
                
                QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                    background-color: #4a4a4a;
                    border: 1px solid #666666;
                    color: #ffffff;
                    padding: 4px;
                    border-radius: 2px;
                }
                
                QLineEdit:focus, QTextEdit:focus {
                    border: 2px solid #4a90e2;
                }
                
                QComboBox::drop-down {
                    border: none;
                    background-color: #4a4a4a;
                }
                
                QComboBox::down-arrow {
                    border: none;
                    background-color: #666666;
                }
                
                QMenuBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border-bottom: 1px solid #555555;
                }
                
                QMenuBar::item:selected {
                    background-color: #4a4a4a;
                }
                
                QMenu {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                
                QMenu::item:selected {
                    background-color: #4a90e2;
                }
                
                QStatusBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border-top: 1px solid #555555;
                }
                
                QToolBar {
                    background-color: #2b2b2b;
                    border-bottom: 1px solid #555555;
                    spacing: 4px;
                }
                
                QSplitter::handle {
                    background-color: #555555;
                }
                
                QSplitter::handle:horizontal {
                    width: 2px;
                }
                
                QSplitter::handle:vertical {
                    height: 2px;
                }
                
                QDialog {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                
                QLabel {
                    color: #ffffff;
                }
                
                QCheckBox {
                    color: #ffffff;
                }
                
                QCheckBox::indicator:checked {
                    background-color: #4a90e2;
                    border: 1px solid #4a90e2;
                }
                
                QCheckBox::indicator:unchecked {
                    background-color: #4a4a4a;
                    border: 1px solid #666666;
                }
                
                QScrollBar:vertical {
                    background-color: #3c3c3c;
                    width: 12px;
                    border: none;
                }
                
                QScrollBar::handle:vertical {
                    background-color: #666666;
                    border-radius: 6px;
                    min-height: 20px;
                }
                
                QScrollBar::handle:vertical:hover {
                    background-color: #777777;
                }
                
                QScrollBar:horizontal {
                    background-color: #3c3c3c;
                    height: 12px;
                    border: none;
                }
                
                QScrollBar::handle:horizontal {
                    background-color: #666666;
                    border-radius: 6px;
                    min-width: 20px;
                }
                
                QScrollBar::handle:horizontal:hover {
                    background-color: #777777;
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