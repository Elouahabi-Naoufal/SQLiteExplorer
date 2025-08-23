"""Bulk import dialog for CSV/JSON data"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
                            QComboBox, QCheckBox, QMessageBox, QProgressBar,
                            QTextEdit, QTabWidget, QWidget, QSpinBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from typing import List, Dict, Any
import csv
import json

from db.operations import DatabaseOperations
from utils.export import ExportManager

class BulkImportDialog(QDialog):
    """Dialog for bulk importing data from CSV/JSON files"""
    
    def __init__(self, table_name: str, table_schema: List[Dict[str, Any]], 
                 db_operations: DatabaseOperations, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.table_schema = table_schema
        self.db_operations = db_operations
        self.export_manager = ExportManager()
        
        self.file_path = ""
        self.preview_data = []
        self.column_mapping = {}
        
        self.setWindowTitle(f"Bulk Import - {table_name}")
        self.setGeometry(200, 200, 800, 600)
        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)
        
        browse_btn = QPushButton("Browse File")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        
        layout.addLayout(file_layout)
        
        # Options
        options_layout = QHBoxLayout()
        
        self.has_header = QCheckBox("First row contains headers")
        self.has_header.setChecked(True)
        options_layout.addWidget(self.has_header)
        
        options_layout.addWidget(QLabel("Skip rows:"))
        self.skip_rows = QSpinBox()
        self.skip_rows.setRange(0, 100)
        options_layout.addWidget(self.skip_rows)
        
        self.clear_table = QCheckBox("Clear table before import")
        options_layout.addWidget(self.clear_table)
        
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Preview and mapping
        tabs = QTabWidget()
        
        # Preview tab
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        
        preview_btn = QPushButton("Preview Data")
        preview_btn.clicked.connect(self.preview_data_file)
        preview_layout.addWidget(preview_btn)
        
        self.preview_table = QTableWidget()
        preview_layout.addWidget(self.preview_table)
        
        tabs.addTab(preview_widget, "Preview")
        
        # Mapping tab
        mapping_widget = QWidget()
        mapping_layout = QVBoxLayout(mapping_widget)
        
        mapping_layout.addWidget(QLabel("Map file columns to database columns:"))
        
        self.mapping_table = QTableWidget()
        self.mapping_table.setColumnCount(2)
        self.mapping_table.setHorizontalHeaderLabels(["File Column", "Database Column"])
        mapping_layout.addWidget(self.mapping_table)
        
        tabs.addTab(mapping_widget, "Column Mapping")
        
        layout.addWidget(tabs)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        import_btn = QPushButton("Import Data")
        import_btn.clicked.connect(self.import_data)
        button_layout.addWidget(import_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def browse_file(self):
        """Browse for import file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Import File", "",
            "CSV Files (*.csv);;JSON Files (*.json);;All Files (*)"
        )
        
        if file_path:
            self.file_path = file_path
            self.file_label.setText(file_path.split('/')[-1])
    
    def preview_data_file(self):
        """Preview data from selected file"""
        if not self.file_path:
            QMessageBox.warning(self, "Warning", "Please select a file first")
            return
        
        try:
            if self.file_path.lower().endswith('.csv'):
                self.preview_data = self.export_manager.import_from_csv(self.file_path)
            elif self.file_path.lower().endswith('.json'):
                self.preview_data = self.export_manager.import_from_json(self.file_path)
            else:
                QMessageBox.warning(self, "Warning", "Unsupported file format")
                return
            
            if not self.preview_data:
                QMessageBox.warning(self, "Warning", "No data found in file")
                return
            
            # Show preview
            self.show_preview()
            self.setup_column_mapping()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read file: {str(e)}")
    
    def show_preview(self):
        """Show data preview in table"""
        if not self.preview_data:
            return
        
        # Show first 10 rows
        preview_rows = self.preview_data[:10]
        
        if preview_rows:
            columns = list(preview_rows[0].keys())
            
            self.preview_table.setRowCount(len(preview_rows))
            self.preview_table.setColumnCount(len(columns))
            self.preview_table.setHorizontalHeaderLabels(columns)
            
            for row_idx, record in enumerate(preview_rows):
                for col_idx, column in enumerate(columns):
                    value = record.get(column, '')
                    item = QTableWidgetItem(str(value))
                    self.preview_table.setItem(row_idx, col_idx, item)
    
    def setup_column_mapping(self):
        """Setup column mapping interface"""
        if not self.preview_data:
            return
        
        file_columns = list(self.preview_data[0].keys())
        db_columns = [col['name'] for col in self.table_schema]
        
        self.mapping_table.setRowCount(len(file_columns))
        
        for row_idx, file_col in enumerate(file_columns):
            # File column (read-only)
            file_item = QTableWidgetItem(file_col)
            file_item.setFlags(file_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.mapping_table.setItem(row_idx, 0, file_item)
            
            # Database column (combo box)
            combo = QComboBox()
            combo.addItem("-- Skip Column --")
            combo.addItems(db_columns)
            
            # Auto-match by name
            if file_col in db_columns:
                combo.setCurrentText(file_col)
            
            self.mapping_table.setCellWidget(row_idx, 1, combo)
    
    def get_column_mapping(self) -> Dict[str, str]:
        """Get column mapping from UI"""
        mapping = {}
        
        for row in range(self.mapping_table.rowCount()):
            file_col = self.mapping_table.item(row, 0).text()
            combo = self.mapping_table.cellWidget(row, 1)
            db_col = combo.currentText()
            
            if db_col != "-- Skip Column --":
                mapping[file_col] = db_col
        
        return mapping
    
    def import_data(self):
        """Import data into database"""
        if not self.preview_data:
            QMessageBox.warning(self, "Warning", "Please preview data first")
            return
        
        mapping = self.get_column_mapping()
        if not mapping:
            QMessageBox.warning(self, "Warning", "Please map at least one column")
            return
        
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(self.preview_data))
            
            # Clear table if requested
            if self.clear_table.isChecked():
                self.db_operations.db.get_connection().execute(f"DELETE FROM {self.table_name}")
            
            # Prepare data for import
            import_data = []
            for record in self.preview_data:
                mapped_record = {}
                for file_col, db_col in mapping.items():
                    if file_col in record:
                        mapped_record[db_col] = record[file_col]
                
                if mapped_record:
                    import_data.append(mapped_record)
            
            # Batch insert
            success = self.db_operations.batch_insert(self.table_name, import_data)
            
            self.progress_bar.setVisible(False)
            
            if success:
                QMessageBox.information(self, "Success", 
                                      f"Successfully imported {len(import_data)} records")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Failed to import data")
                
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Error", f"Import failed: {str(e)}")