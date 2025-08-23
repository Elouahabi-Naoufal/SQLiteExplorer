"""Query history and favorites management dialog"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                            QListWidget, QListWidgetItem, QPushButton, QTextEdit,
                            QLabel, QLineEdit, QMessageBox, QInputDialog,
                            QSplitter, QWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
from utils.query_manager import QueryManager

class QueryManagerDialog(QDialog):
    """Dialog for managing query history and favorites"""
    
    query_selected = pyqtSignal(str)
    
    def __init__(self, query_manager: QueryManager, parent=None):
        super().__init__(parent)
        self.query_manager = query_manager
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Query Manager")
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout(self)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # History tab
        self.create_history_tab()
        
        # Favorites tab
        self.create_favorites_tab()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.use_query_btn = QPushButton("Use Query")
        self.use_query_btn.clicked.connect(self.use_selected_query)
        button_layout.addWidget(self.use_query_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
    def create_history_tab(self):
        """Create history tab"""
        history_widget = QWidget()
        layout = QVBoxLayout(history_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear History")
        clear_btn.clicked.connect(self.clear_history)
        controls_layout.addWidget(clear_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Splitter for list and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.itemSelectionChanged.connect(self.on_history_selection_changed)
        splitter.addWidget(self.history_list)
        
        # Query preview
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        preview_layout.addWidget(QLabel("Query Preview:"))
        self.history_preview = QTextEdit()
        self.history_preview.setReadOnly(True)
        preview_layout.addWidget(self.history_preview)
        
        preview_layout.addWidget(QLabel("Details:"))
        self.history_details = QLabel()
        self.history_details.setWordWrap(True)
        preview_layout.addWidget(self.history_details)
        
        splitter.addWidget(preview_widget)
        splitter.setSizes([400, 400])
        
        self.tab_widget.addTab(history_widget, "History")
        
    def create_favorites_tab(self):
        """Create favorites tab"""
        favorites_widget = QWidget()
        layout = QVBoxLayout(favorites_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        add_favorite_btn = QPushButton("Add to Favorites")
        add_favorite_btn.clicked.connect(self.add_favorite)
        controls_layout.addWidget(add_favorite_btn)
        
        remove_favorite_btn = QPushButton("Remove Favorite")
        remove_favorite_btn.clicked.connect(self.remove_favorite)
        controls_layout.addWidget(remove_favorite_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Splitter for list and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Favorites list
        self.favorites_list = QListWidget()
        self.favorites_list.itemSelectionChanged.connect(self.on_favorites_selection_changed)
        splitter.addWidget(self.favorites_list)
        
        # Query preview
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        preview_layout.addWidget(QLabel("Query Preview:"))
        self.favorites_preview = QTextEdit()
        self.favorites_preview.setReadOnly(True)
        preview_layout.addWidget(self.favorites_preview)
        
        preview_layout.addWidget(QLabel("Description:"))
        self.favorites_description = QLabel()
        self.favorites_description.setWordWrap(True)
        preview_layout.addWidget(self.favorites_description)
        
        splitter.addWidget(preview_widget)
        splitter.setSizes([400, 400])
        
        self.tab_widget.addTab(favorites_widget, "Favorites")
        
    def load_data(self):
        """Load history and favorites data"""
        self.load_history()
        self.load_favorites()
        
    def load_history(self):
        """Load query history"""
        self.history_list.clear()
        history = self.query_manager.get_history()
        
        for entry in history:
            timestamp = datetime.fromisoformat(entry['timestamp'])
            display_text = f"{timestamp.strftime('%Y-%m-%d %H:%M')} - {entry['query'][:50]}..."
            
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.history_list.addItem(item)
            
    def load_favorites(self):
        """Load favorite queries"""
        self.favorites_list.clear()
        favorites = self.query_manager.get_favorites()
        
        for favorite in favorites:
            item = QListWidgetItem(favorite['name'])
            item.setData(Qt.ItemDataRole.UserRole, favorite)
            self.favorites_list.addItem(item)
            
    def on_history_selection_changed(self):
        """Handle history selection change"""
        current_item = self.history_list.currentItem()
        if current_item:
            entry = current_item.data(Qt.ItemDataRole.UserRole)
            self.history_preview.setPlainText(entry['query'])
            
            timestamp = datetime.fromisoformat(entry['timestamp'])
            details = f"Executed: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            details += f"Execution Time: {entry['execution_time']:.3f}s\n"
            details += f"Result Count: {entry['result_count']} rows"
            
            self.history_details.setText(details)
        else:
            self.history_preview.clear()
            self.history_details.clear()
            
    def on_favorites_selection_changed(self):
        """Handle favorites selection change"""
        current_item = self.favorites_list.currentItem()
        if current_item:
            favorite = current_item.data(Qt.ItemDataRole.UserRole)
            self.favorites_preview.setPlainText(favorite['query'])
            self.favorites_description.setText(favorite.get('description', ''))
        else:
            self.favorites_preview.clear()
            self.favorites_description.clear()
            
    def use_selected_query(self):
        """Use selected query"""
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:  # History tab
            current_item = self.history_list.currentItem()
            if current_item:
                entry = current_item.data(Qt.ItemDataRole.UserRole)
                self.query_selected.emit(entry['query'])
                self.close()
        else:  # Favorites tab
            current_item = self.favorites_list.currentItem()
            if current_item:
                favorite = current_item.data(Qt.ItemDataRole.UserRole)
                self.query_selected.emit(favorite['query'])
                self.close()
                
    def clear_history(self):
        """Clear query history"""
        reply = QMessageBox.question(self, "Confirm", "Clear all query history?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.query_manager.clear_history()
            self.load_history()
            
    def add_favorite(self):
        """Add current query to favorites"""
        current_tab = self.tab_widget.currentIndex()
        query = ""
        
        if current_tab == 0:  # From history
            current_item = self.history_list.currentItem()
            if current_item:
                entry = current_item.data(Qt.ItemDataRole.UserRole)
                query = entry['query']
        
        if not query:
            QMessageBox.warning(self, "Warning", "Please select a query from history first")
            return
            
        name, ok = QInputDialog.getText(self, "Add Favorite", "Enter name for this query:")
        if ok and name:
            description, _ = QInputDialog.getText(self, "Add Favorite", "Enter description (optional):")
            self.query_manager.add_favorite(name, query, description)
            self.load_favorites()
            
    def remove_favorite(self):
        """Remove selected favorite"""
        current_item = self.favorites_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a favorite to remove")
            return
            
        favorite = current_item.data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(self, "Confirm", f"Remove favorite '{favorite['name']}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.query_manager.remove_favorite(favorite['name'])
            self.load_favorites()