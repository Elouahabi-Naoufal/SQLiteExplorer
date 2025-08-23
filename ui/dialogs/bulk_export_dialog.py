"""Bulk export dialog for database data"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFileDialog, QCheckBox, QMessageBox,
                            QComboBox, QSpinBox, QLineEdit, QTextEdit,
                            QProgressBar, QListWidget, QListWidgetItem)
from PyQt6.QtCore import Qt
from typing import List, Dict, Any

from db.operations import DatabaseOperations
from db.schema import SchemaManager
from utils.export import ExportManager

class BulkExportDialog(QDialog):
    """Dialog for bulk exporting database data"""
    
    def __init__(self, db_operations: DatabaseOperations, schema_manager: SchemaManager, parent=None):
        super().__init__(parent)
        self.db_operations = db_operations
        self.schema_manager = schema_manager
        self.export_manager = ExportManager()
        
        self.setWindowTitle("Bulk Export Database")
        self.setGeometry(200, 200, 600, 500)
        self.init_ui()
        self.load_tables()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # Table selection
        layout.addWidget(QLabel("Select tables to export:"))
        
        table_layout = QHBoxLayout()
        
        self.table_list = QListWidget()
        table_layout.addWidget(self.table_list)
        
        # Table selection buttons
        button_layout = QVBoxLayout()
        
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all_tables)
        button_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton("Select None")
        select_none_btn.clicked.connect(self.select_no_tables)
        button_layout.addWidget(select_none_btn)
        
        button_layout.addStretch()
        table_layout.addLayout(button_layout)
        
        layout.addLayout(table_layout)
        
        # Export options
        options_layout = QVBoxLayout()
        
        # Format selection
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Export format:"))
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "JSON"])
        format_layout.addWidget(self.format_combo)
        
        format_layout.addStretch()
        options_layout.addLayout(format_layout)
        
        # Export options
        self.include_headers = QCheckBox("Include column headers (CSV only)")
        self.include_headers.setChecked(True)
        options_layout.addWidget(self.include_headers)
        
        self.pretty_json = QCheckBox("Pretty format JSON")
        self.pretty_json.setChecked(True)
        options_layout.addWidget(self.pretty_json)
        
        # Row limit
        limit_layout = QHBoxLayout()
        self.limit_rows = QCheckBox("Limit rows per table:")
        limit_layout.addWidget(self.limit_rows)
        
        self.row_limit = QSpinBox()
        self.row_limit.setRange(1, 1000000)
        self.row_limit.setValue(10000)
        self.row_limit.setEnabled(False)
        self.limit_rows.toggled.connect(self.row_limit.setEnabled)
        limit_layout.addWidget(self.row_limit)
        
        limit_layout.addStretch()
        options_layout.addLayout(limit_layout)
        
        # Output directory
        output_layout = QHBoxLayout()
        output_layout.addWidget(QLabel("Output directory:"))
        
        self.output_path = QLineEdit()
        output_layout.addWidget(self.output_path)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(browse_btn)
        
        options_layout.addLayout(output_layout)
        
        layout.addLayout(options_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status text
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setVisible(False)
        layout.addWidget(self.status_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton("Export Data")
        export_btn.clicked.connect(self.export_data)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def load_tables(self):
        """Load available tables"""
        try:
            tables = self.schema_manager.get_tables()
            
            for table in tables:
                item = QListWidgetItem(table['name'])
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                item.setCheckState(Qt.CheckState.Checked)
                self.table_list.addItem(item)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tables: {str(e)}")
    
    def select_all_tables(self):
        """Select all tables"""
        for i in range(self.table_list.count()):
            item = self.table_list.item(i)
            item.setCheckState(Qt.CheckState.Checked)
    
    def select_no_tables(self):
        """Deselect all tables"""
        for i in range(self.table_list.count()):
            item = self.table_list.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)
    
    def browse_output_dir(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.output_path.setText(directory)
    
    def get_selected_tables(self) -> List[str]:
        """Get list of selected tables"""
        selected = []
        for i in range(self.table_list.count()):
            item = self.table_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected.append(item.text())
        return selected
    
    def export_data(self):
        """Export selected tables"""
        selected_tables = self.get_selected_tables()
        if not selected_tables:
            QMessageBox.warning(self, "Warning", "Please select at least one table")
            return
        
        output_dir = self.output_path.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "Warning", "Please select output directory")
            return
        
        try:
            self.progress_bar.setVisible(True)
            self.status_text.setVisible(True)
            self.progress_bar.setMaximum(len(selected_tables))
            
            export_format = self.format_combo.currentText().lower()
            exported_files = []
            
            for i, table_name in enumerate(selected_tables):
                self.status_text.append(f"Exporting {table_name}...")
                
                # Get table data
                limit = self.row_limit.value() if self.limit_rows.isChecked() else None
                records = self.db_operations.get_records(table_name, limit=limit)
                
                if records:
                    # Generate filename
                    filename = f"{table_name}.{export_format}"
                    file_path = f"{output_dir}/{filename}"
                    
                    # Export data
                    if export_format == "csv":
                        success = self.export_manager.export_to_csv(records, file_path)
                    else:  # json
                        success = self.export_manager.export_to_json(
                            records, file_path, pretty=self.pretty_json.isChecked()
                        )
                    
                    if success:
                        exported_files.append(filename)
                        self.status_text.append(f"✓ {table_name} exported ({len(records)} records)")
                    else:
                        self.status_text.append(f"✗ Failed to export {table_name}")
                else:
                    self.status_text.append(f"⚠ {table_name} is empty")
                
                self.progress_bar.setValue(i + 1)
            
            self.progress_bar.setVisible(False)
            
            if exported_files:
                QMessageBox.information(self, "Export Complete", 
                                      f"Successfully exported {len(exported_files)} tables to {output_dir}")
            else:
                QMessageBox.warning(self, "Export Failed", "No tables were exported")
                
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Error", f"Export failed: {str(e)}")