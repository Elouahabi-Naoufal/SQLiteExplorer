"""Database connection dialog"""

import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QFileDialog, QCheckBox,
                            QDialogButtonBox, QGroupBox, QListWidget)
from PyQt6.QtCore import Qt

class ConnectionDialog(QDialog):
    """Dialog for database connection settings"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Connect to Database")
        self.setModal(True)
        self.resize(500, 400)
        
        self.db_path = ""
        self.password = ""
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # Database file selection
        file_group = QGroupBox("Database File")
        file_layout = QVBoxLayout(file_group)
        
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select SQLite database file...")
        path_layout.addWidget(self.path_edit)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_database)
        path_layout.addWidget(browse_btn)
        
        file_layout.addLayout(path_layout)
        
        # Create new database option
        create_layout = QHBoxLayout()
        create_btn = QPushButton("Create New Database...")
        create_btn.clicked.connect(self.create_database)
        create_layout.addWidget(create_btn)
        create_layout.addStretch()
        
        file_layout.addLayout(create_layout)
        layout.addWidget(file_group)
        
        # Encryption settings
        encryption_group = QGroupBox("Encryption (Optional)")
        encryption_layout = QVBoxLayout(encryption_group)
        
        self.use_encryption = QCheckBox("Use SQLCipher encryption")
        encryption_layout.addWidget(self.use_encryption)
        
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setEnabled(False)
        password_layout.addWidget(self.password_edit)
        
        encryption_layout.addLayout(password_layout)
        layout.addWidget(encryption_group)
        
        # Connect encryption checkbox to password field
        self.use_encryption.toggled.connect(self.password_edit.setEnabled)
        
        # Recent databases
        recent_group = QGroupBox("Recent Databases")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_list = QListWidget()
        self.recent_list.itemDoubleClicked.connect(self.select_recent_database)
        recent_layout.addWidget(self.recent_list)
        
        layout.addWidget(recent_group)
        
        # Load recent databases
        self.load_recent_databases()
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept_connection)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def browse_database(self):
        """Browse for database file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Database File", "", 
            "SQLite Files (*.db *.sqlite *.sqlite3);;All Files (*)"
        )
        if file_path:
            self.path_edit.setText(file_path)
    
    def create_database(self):
        """Create new database file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Create New Database", "", 
            "SQLite Files (*.db *.sqlite *.sqlite3)"
        )
        if file_path:
            # Create empty database file
            try:
                import sqlite3
                conn = sqlite3.connect(file_path)
                conn.close()
                self.path_edit.setText(file_path)
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", f"Failed to create database: {str(e)}")
    
    def load_recent_databases(self):
        """Load recent database list"""
        # This would typically load from settings/session manager
        # For now, just show placeholder
        self.recent_list.addItem("No recent databases")
    
    def select_recent_database(self, item):
        """Select database from recent list"""
        if item.text() != "No recent databases":
            self.path_edit.setText(item.text())
    
    def accept_connection(self):
        """Accept connection with validation"""
        self.db_path = self.path_edit.text().strip()
        
        if not self.db_path:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please select a database file")
            return
        
        if not os.path.exists(self.db_path):
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, "File Not Found", 
                f"Database file does not exist:\n{self.db_path}\n\nCreate new database?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    import sqlite3
                    conn = sqlite3.connect(self.db_path)
                    conn.close()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to create database: {str(e)}")
                    return
            else:
                return
        
        if self.use_encryption.isChecked():
            self.password = self.password_edit.text()
            if not self.password:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Warning", "Please enter a password for encryption")
                return
        else:
            self.password = None
        
        self.accept()
    
    def get_connection_info(self):
        """Get connection information"""
        return self.db_path, self.password