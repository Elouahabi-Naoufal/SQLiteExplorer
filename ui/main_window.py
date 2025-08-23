"""Main application window"""

import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QSplitter, QTreeWidget, QTreeWidgetItem, QTabWidget,
                            QMenuBar, QMenu, QStatusBar, QMessageBox, QFileDialog,
                            QToolBar, QLabel, QPushButton, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QKeySequence

from db.connection import DatabaseConnection
from db.schema import SchemaManager
from db.operations import DatabaseOperations
from db.queries import QueryExecutor
from .table_view import TableView
from .dialogs.connection_dialog import ConnectionDialog
from .dialogs.sql_executor import SQLExecutorDialog
from .dialogs.table_editor import TableEditorDialog
from utils.backup import BackupManager
from utils.session import SessionManager
from utils.theme import ThemeManager
from utils.query_manager import QueryManager

class MainWindow(QMainWindow):
    """Main application window with split view layout"""
    
    database_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.db_connection = DatabaseConnection()
        self.schema_manager = SchemaManager(self.db_connection)
        self.db_operations = DatabaseOperations(self.db_connection)
        self.query_executor = QueryExecutor(self.db_connection)
        self.backup_manager = BackupManager()
        self.session_manager = SessionManager()
        self.theme_manager = ThemeManager()
        self.query_manager = QueryManager()
        
        self.current_table = None
        self.open_tabs = {}
        
        self.init_ui()
        self.create_menus()
        self.create_toolbar()
        self.create_status_bar()
        self.load_session()
        
        # Detect and apply system theme
        self.detect_and_apply_theme()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("SQLite Manager")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left panel - Schema tree
        self.schema_tree = QTreeWidget()
        self.schema_tree.setHeaderLabel("Database Schema")
        self.schema_tree.itemClicked.connect(self.on_schema_item_clicked)
        self.schema_tree.setMaximumWidth(300)
        splitter.addWidget(self.schema_tree)
        
        # Right panel - Tab widget for tables/queries
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        splitter.addWidget(self.tab_widget)
        
        # Set splitter proportions
        splitter.setSizes([300, 900])
    
    def create_menus(self):
        """Create application menus"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        connect_action = QAction("&Connect to Database...", self)
        connect_action.setShortcut(QKeySequence.StandardKey.Open)
        connect_action.triggered.connect(self.connect_database)
        file_menu.addAction(connect_action)
        
        disconnect_action = QAction("&Disconnect", self)
        disconnect_action.triggered.connect(self.disconnect_database)
        file_menu.addAction(disconnect_action)
        
        file_menu.addSeparator()
        
        backup_action = QAction("&Backup Database...", self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        restore_action = QAction("&Restore Database...", self)
        restore_action.triggered.connect(self.restore_database)
        file_menu.addAction(restore_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        sql_action = QAction("&Execute SQL...", self)
        sql_action.setShortcut(QKeySequence("Ctrl+E"))
        sql_action.triggered.connect(self.open_sql_executor)
        edit_menu.addAction(sql_action)
        
        query_manager_action = QAction("&Query Manager...", self)
        query_manager_action.setShortcut(QKeySequence("Ctrl+H"))
        query_manager_action.triggered.connect(self.open_query_manager)
        edit_menu.addAction(query_manager_action)
        
        # Table menu
        table_menu = menubar.addMenu("&Table")
        
        create_table_action = QAction("&Create Table...", self)
        create_table_action.triggered.connect(self.create_table)
        table_menu.addAction(create_table_action)
        
        edit_table_action = QAction("&Edit Table...", self)
        edit_table_action.triggered.connect(self.edit_table)
        table_menu.addAction(edit_table_action)
        
        drop_table_action = QAction("&Drop Table...", self)
        drop_table_action.triggered.connect(self.drop_table)
        table_menu.addAction(drop_table_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut(QKeySequence.StandardKey.Refresh)
        refresh_action.triggered.connect(self.refresh_schema)
        view_menu.addAction(refresh_action)
        
        theme_menu = view_menu.addMenu("&Theme")
        
        light_theme_action = QAction("&Light", self)
        light_theme_action.triggered.connect(lambda: self.change_theme("light"))
        theme_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction("&Dark", self)
        dark_theme_action.triggered.connect(lambda: self.change_theme("dark"))
        theme_menu.addAction(dark_theme_action)
    
    def create_toolbar(self):
        """Create application toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        connect_btn = QPushButton("Connect")
        connect_btn.clicked.connect(self.connect_database)
        toolbar.addWidget(connect_btn)
        
        disconnect_btn = QPushButton("Disconnect")
        disconnect_btn.clicked.connect(self.disconnect_database)
        toolbar.addWidget(disconnect_btn)
        
        toolbar.addSeparator()
        
        sql_btn = QPushButton("Execute SQL")
        sql_btn.clicked.connect(self.open_sql_executor)
        toolbar.addWidget(sql_btn)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_schema)
        toolbar.addWidget(refresh_btn)
    
    def create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.connection_label = QLabel("Not connected")
        self.status_bar.addPermanentWidget(self.connection_label)
    
    def connect_database(self):
        """Open connection dialog"""
        dialog = ConnectionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            db_path, password = dialog.get_connection_info()
            if self.db_connection.connect(db_path, password):
                self.connection_label.setText(f"Connected: {os.path.basename(db_path)}")
                self.refresh_schema()
                self.session_manager.add_recent_database(db_path)
            else:
                QMessageBox.critical(self, "Connection Error", "Failed to connect to database")
    
    def disconnect_database(self):
        """Disconnect from database"""
        self.db_connection.disconnect()
        self.connection_label.setText("Not connected")
        self.schema_tree.clear()
        self.close_all_tabs()
    
    def refresh_schema(self):
        """Refresh schema tree"""
        if not self.db_connection.is_connected():
            return
        
        self.schema_tree.clear()
        
        try:
            # Add tables
            tables_item = QTreeWidgetItem(self.schema_tree, ["Tables"])
            tables_item.setExpanded(True)
            
            tables = self.schema_manager.get_tables()
            print(f"DEBUG: Found {len(tables)} tables")
            
            for table in tables:
                table_item = QTreeWidgetItem(tables_item, [table['name']])
                table_item.setData(0, Qt.ItemDataRole.UserRole, {'type': 'table', 'name': table['name']})
                print(f"DEBUG: Added table {table['name']}")
                
        except Exception as e:
            print(f"DEBUG: Schema refresh failed: {e}")
            QMessageBox.critical(self, "Error", f"Failed to refresh schema: {str(e)}")
    
    def on_schema_item_clicked(self, item, column):
        """Handle schema tree item double click"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data['type'] == 'table':
            self.open_table_tab(data['name'])
    
    def open_table_tab(self, table_name: str):
        """Open table in new tab"""
        if table_name in self.open_tabs:
            # Switch to existing tab
            self.tab_widget.setCurrentWidget(self.open_tabs[table_name])
            return
        
        # Create new table view
        table_view = TableView(table_name, self.db_operations, self.query_executor, self.schema_manager)
        self.tab_widget.addTab(table_view, table_name)
        self.tab_widget.setCurrentWidget(table_view)
        
        self.open_tabs[table_name] = table_view
        self.current_table = table_name
    
    def close_tab(self, index: int):
        """Close tab at index"""
        widget = self.tab_widget.widget(index)
        if widget:
            # Find and remove from open_tabs
            for table_name, tab_widget in list(self.open_tabs.items()):
                if tab_widget == widget:
                    del self.open_tabs[table_name]
                    break
            
            self.tab_widget.removeTab(index)
            widget.deleteLater()
    
    def close_all_tabs(self):
        """Close all open tabs"""
        self.tab_widget.clear()
        self.open_tabs.clear()
        self.current_table = None
    
    def open_sql_executor(self):
        """Open SQL executor dialog"""
        if not self.db_connection.is_connected():
            QMessageBox.warning(self, "Warning", "Please connect to a database first")
            return
        
        dialog = SQLExecutorDialog(self.query_executor, self)
        dialog.exec()
    
    def create_table(self):
        """Open create table dialog"""
        if not self.db_connection.is_connected():
            QMessageBox.warning(self, "Warning", "Please connect to a database first")
            return
        
        dialog = TableEditorDialog(self.schema_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_schema()
    
    def edit_table(self):
        """Edit current table"""
        if not self.current_table:
            QMessageBox.warning(self, "Warning", "Please select a table first")
            return
        
        dialog = TableEditorDialog(self.schema_manager, self, self.current_table)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_schema()
    
    def drop_table(self):
        """Drop current table"""
        if not self.current_table:
            QMessageBox.warning(self, "Warning", "Please select a table first")
            return
        
        reply = QMessageBox.question(self, "Confirm Drop", 
                                   f"Are you sure you want to drop table '{self.current_table}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.schema_manager.drop_table(self.current_table):
                self.refresh_schema()
                if self.current_table in self.open_tabs:
                    tab_widget = self.open_tabs[self.current_table]
                    index = self.tab_widget.indexOf(tab_widget)
                    self.close_tab(index)
                QMessageBox.information(self, "Success", f"Table '{self.current_table}' dropped successfully")
            else:
                QMessageBox.critical(self, "Error", f"Failed to drop table '{self.current_table}'")
    
    def backup_database(self):
        """Backup current database"""
        if not self.db_connection.is_connected():
            QMessageBox.warning(self, "Warning", "Please connect to a database first")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Backup Database", "", "SQLite Files (*.db *.sqlite)")
        if file_path:
            if self.backup_manager.backup_database(self.db_connection.database_path, file_path):
                QMessageBox.information(self, "Success", "Database backed up successfully")
            else:
                QMessageBox.critical(self, "Error", "Failed to backup database")
    
    def restore_database(self):
        """Restore database from backup"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Restore Database", "", "SQLite Files (*.db *.sqlite)")
        if file_path:
            if self.backup_manager.restore_database(file_path, self.db_connection.database_path):
                QMessageBox.information(self, "Success", "Database restored successfully")
                self.refresh_schema()
            else:
                QMessageBox.critical(self, "Error", "Failed to restore database")
    
    def change_theme(self, theme_name: str):
        """Change application theme"""
        self.theme_manager.apply_theme(self, theme_name)
    
    def detect_and_apply_theme(self):
        """Detect system theme and apply appropriate theme"""
        from PyQt6.QtGui import QPalette
        from PyQt6.QtWidgets import QApplication
        
        # Check if system is in dark mode
        palette = QApplication.palette()
        window_color = palette.color(QPalette.ColorRole.Window)
        
        # If window background is dark, use dark theme
        if window_color.lightness() < 128:
            self.theme_manager.apply_theme(self, "dark")
        else:
            self.theme_manager.apply_theme(self, "light")
    
    def load_session(self):
        """Load previous session"""
        session_data = self.session_manager.load_session()
        if session_data.get('last_database'):
            # Auto-connect to last database if it exists
            db_path = session_data['last_database']
            if os.path.exists(db_path):
                if self.db_connection.connect(db_path):
                    self.connection_label.setText(f"Connected: {os.path.basename(db_path)}")
                    self.refresh_schema()
    
    def save_session(self):
        """Save current session"""
        session_data = {
            'last_database': self.db_connection.database_path,
            'open_tables': list(self.open_tabs.keys()),
            'window_geometry': [self.x(), self.y(), self.width(), self.height()]
        }
        self.session_manager.save_session(session_data)
    
    def open_query_manager(self):
        """Open query manager dialog"""
        from .dialogs.query_manager_dialog import QueryManagerDialog
        
        dialog = QueryManagerDialog(self.query_manager, self)
        dialog.exec()
    
    def closeEvent(self, event):
        """Handle application close"""
        self.save_session()
        self.db_connection.disconnect()
        event.accept()