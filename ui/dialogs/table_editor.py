"""Table editor dialog for creating/modifying table schemas"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QComboBox, QCheckBox, QPushButton,
                            QTableWidget, QTableWidgetItem, QDialogButtonBox,
                            QLabel, QMessageBox, QHeaderView, QGroupBox)
from PyQt6.QtCore import Qt
from typing import List, Dict, Any, Optional

from db.schema import SchemaManager

class TableEditorDialog(QDialog):
    """Dialog for creating/editing table schemas"""
    
    def __init__(self, schema_manager: SchemaManager, parent=None, table_name: Optional[str] = None):
        super().__init__(parent)
        self.schema_manager = schema_manager
        self.table_name = table_name
        self.is_edit_mode = table_name is not None
        
        self.setWindowTitle(f"{'Edit' if self.is_edit_mode else 'Create'} Table")
        self.setModal(True)
        self.resize(700, 500)
        
        self.columns_data = []
        
        self.init_ui()
        if self.is_edit_mode:
            self.load_existing_table()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # Table name
        name_group = QGroupBox("Table Information")
        name_layout = QFormLayout(name_group)
        
        self.table_name_edit = QLineEdit()
        if self.is_edit_mode:
            self.table_name_edit.setText(self.table_name)
            self.table_name_edit.setEnabled(False)  # Can't rename in this simple version
        name_layout.addRow("Table Name:", self.table_name_edit)
        
        layout.addWidget(name_group)
        
        # Columns section
        columns_group = QGroupBox("Columns")
        columns_layout = QVBoxLayout(columns_group)
        
        # Column buttons
        button_layout = QHBoxLayout()
        
        add_column_btn = QPushButton("Add Column")
        add_column_btn.clicked.connect(self.add_column)
        button_layout.addWidget(add_column_btn)
        
        remove_column_btn = QPushButton("Remove Column")
        remove_column_btn.clicked.connect(self.remove_column)
        button_layout.addWidget(remove_column_btn)
        
        button_layout.addStretch()
        columns_layout.addLayout(button_layout)
        
        # Columns table
        self.columns_table = QTableWidget()
        self.columns_table.setColumnCount(6)
        self.columns_table.setHorizontalHeaderLabels([
            "Name", "Type", "Primary Key", "Not Null", "Unique", "Default"
        ])
        
        # Set column widths
        header = self.columns_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # PK
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Not Null
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Unique
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Default
        
        columns_layout.addWidget(self.columns_table)
        layout.addWidget(columns_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept_table)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Add initial column if creating new table
        if not self.is_edit_mode:
            self.add_column()
    
    def add_column(self):
        """Add new column row"""
        row = self.columns_table.rowCount()
        self.columns_table.insertRow(row)
        
        # Column name
        name_edit = QLineEdit()
        name_edit.setPlaceholderText("column_name")
        self.columns_table.setCellWidget(row, 0, name_edit)
        
        # Column type
        type_combo = QComboBox()
        type_combo.addItems([
            "INTEGER", "TEXT", "REAL", "BLOB", "NUMERIC",
            "VARCHAR(255)", "CHAR(50)", "BOOLEAN", "DATE", "TIME", "DATETIME"
        ])
        type_combo.setEditable(True)
        self.columns_table.setCellWidget(row, 1, type_combo)
        
        # Primary key checkbox
        pk_check = QCheckBox()
        pk_check.stateChanged.connect(lambda state, r=row: self.on_pk_changed(r, state))
        self.columns_table.setCellWidget(row, 2, pk_check)
        
        # Not null checkbox
        nn_check = QCheckBox()
        self.columns_table.setCellWidget(row, 3, nn_check)
        
        # Unique checkbox
        unique_check = QCheckBox()
        self.columns_table.setCellWidget(row, 4, unique_check)
        
        # Default value
        default_edit = QLineEdit()
        default_edit.setPlaceholderText("default value")
        self.columns_table.setCellWidget(row, 5, default_edit)
    
    def remove_column(self):
        """Remove selected column row"""
        current_row = self.columns_table.currentRow()
        if current_row >= 0:
            self.columns_table.removeRow(current_row)
    
    def on_pk_changed(self, row: int, state: int):
        """Handle primary key checkbox change"""
        if state == Qt.CheckState.Checked.value:
            # Set not null when primary key is checked
            nn_check = self.columns_table.cellWidget(row, 3)
            if nn_check:
                nn_check.setChecked(True)
                nn_check.setEnabled(False)
        else:
            # Enable not null when primary key is unchecked
            nn_check = self.columns_table.cellWidget(row, 3)
            if nn_check:
                nn_check.setEnabled(True)
    
    def load_existing_table(self):
        """Load existing table schema"""
        if not self.table_name:
            return
        
        schema = self.schema_manager.get_table_schema(self.table_name)
        
        for column in schema:
            self.add_column()
            row = self.columns_table.rowCount() - 1
            
            # Set column data
            name_edit = self.columns_table.cellWidget(row, 0)
            name_edit.setText(column['name'])
            
            type_combo = self.columns_table.cellWidget(row, 1)
            type_combo.setCurrentText(column['type'])
            
            pk_check = self.columns_table.cellWidget(row, 2)
            pk_check.setChecked(bool(column['pk']))
            
            nn_check = self.columns_table.cellWidget(row, 3)
            nn_check.setChecked(bool(column['notnull']))
            
            default_edit = self.columns_table.cellWidget(row, 5)
            if column['dflt_value']:
                default_edit.setText(str(column['dflt_value']))
    
    def get_columns_data(self) -> List[Dict[str, Any]]:
        """Get column definitions from table"""
        columns = []
        
        for row in range(self.columns_table.rowCount()):
            name_edit = self.columns_table.cellWidget(row, 0)
            type_combo = self.columns_table.cellWidget(row, 1)
            pk_check = self.columns_table.cellWidget(row, 2)
            nn_check = self.columns_table.cellWidget(row, 3)
            unique_check = self.columns_table.cellWidget(row, 4)
            default_edit = self.columns_table.cellWidget(row, 5)
            
            if not name_edit or not name_edit.text().strip():
                continue
            
            column = {
                'name': name_edit.text().strip(),
                'type': type_combo.currentText(),
                'primary_key': pk_check.isChecked(),
                'not_null': nn_check.isChecked(),
                'unique': unique_check.isChecked(),
                'default': default_edit.text().strip() if default_edit.text().strip() else None
            }
            
            columns.append(column)
        
        return columns
    
    def validate_table(self) -> tuple[bool, str]:
        """Validate table definition"""
        table_name = self.table_name_edit.text().strip()
        if not table_name:
            return False, "Table name is required"
        
        columns = self.get_columns_data()
        if not columns:
            return False, "At least one column is required"
        
        # Check for duplicate column names
        column_names = [col['name'].lower() for col in columns]
        if len(column_names) != len(set(column_names)):
            return False, "Duplicate column names are not allowed"
        
        # Check for valid column names
        for column in columns:
            if not column['name'].replace('_', '').isalnum():
                return False, f"Invalid column name: {column['name']}"
        
        # Check primary key constraints
        pk_columns = [col for col in columns if col['primary_key']]
        if len(pk_columns) > 1:
            return False, "Multiple primary key columns are not supported in this version"
        
        return True, "Valid"
    
    def accept_table(self):
        """Accept and create/modify table"""
        is_valid, message = self.validate_table()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", message)
            return
        
        table_name = self.table_name_edit.text().strip()
        columns = self.get_columns_data()
        
        try:
            if self.is_edit_mode:
                # For editing, we would need more complex logic to handle schema changes
                # This is a simplified version that doesn't support editing
                QMessageBox.information(self, "Info", 
                    "Table editing is not fully implemented in this version.\n"
                    "Please use SQL commands for complex schema modifications.")
                return
            else:
                # Create new table
                success = self.schema_manager.create_table(table_name, columns)
                
                if success:
                    QMessageBox.information(self, "Success", f"Table '{table_name}' created successfully!")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", f"Failed to create table '{table_name}'")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")