"""Record editor dialog for adding/editing table records"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox,
                            QCheckBox, QComboBox, QDateEdit, QTimeEdit,
                            QDialogButtonBox, QLabel, QMessageBox, QScrollArea,
                            QWidget, QPushButton)
from PyQt6.QtCore import Qt, QDate, QTime
from typing import Dict, Any, List, Optional

from db.operations import DatabaseOperations

class RecordEditorDialog(QDialog):
    """Dialog for adding/editing table records"""
    
    def __init__(self, table_name: str, table_schema: List[Dict[str, Any]], 
                 db_operations: DatabaseOperations, parent=None, 
                 existing_record: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.table_name = table_name
        self.table_schema = table_schema
        self.db_operations = db_operations
        self.existing_record = existing_record
        self.is_edit_mode = existing_record is not None
        
        self.field_widgets = {}
        
        self.setWindowTitle(f"{'Edit' if self.is_edit_mode else 'Add'} Record - {table_name}")
        self.setModal(True)
        self.resize(500, 600)
        
        self.init_ui()
        if self.is_edit_mode:
            self.populate_fields()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # Scroll area for form fields
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Form layout
        form_layout = QFormLayout()
        
        for column in self.table_schema:
            field_widget = self.create_field_widget(column)
            self.field_widgets[column['name']] = field_widget
            
            label_text = column['name']
            if column['pk']:
                label_text += " (PK)"
            if column['notnull'] and not column['pk']:
                label_text += " *"
            
            form_layout.addRow(QLabel(label_text), field_widget)
        
        scroll_layout.addLayout(form_layout)
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Validation button
        validate_btn = QPushButton("Validate Data")
        validate_btn.clicked.connect(self.validate_data)
        layout.addWidget(validate_btn)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept_record)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def create_field_widget(self, column: Dict[str, Any]):
        """Create appropriate widget for column type"""
        col_type = column['type'].upper()
        col_name = column['name']
        
        if 'INT' in col_type:
            widget = QSpinBox()
            widget.setRange(-2147483648, 2147483647)
            if column.get('default'):
                try:
                    widget.setValue(int(column['default']))
                except:
                    pass
            return widget
            
        elif 'REAL' in col_type or 'FLOAT' in col_type or 'DOUBLE' in col_type:
            widget = QDoubleSpinBox()
            widget.setRange(-999999999.99, 999999999.99)
            widget.setDecimals(6)
            if column.get('default'):
                try:
                    widget.setValue(float(column['default']))
                except:
                    pass
            return widget
            
        elif 'BOOL' in col_type:
            widget = QCheckBox()
            if column.get('default'):
                widget.setChecked(column['default'].lower() in ['1', 'true', 'yes'])
            return widget
            
        elif 'DATE' in col_type:
            widget = QDateEdit()
            widget.setDate(QDate.currentDate())
            widget.setCalendarPopup(True)
            return widget
            
        elif 'TIME' in col_type:
            widget = QTimeEdit()
            widget.setTime(QTime.currentTime())
            return widget
            
        elif 'TEXT' in col_type and ('LONG' in col_type or 'MEMO' in col_type):
            widget = QTextEdit()
            widget.setMaximumHeight(100)
            if column.get('default'):
                widget.setPlainText(str(column['default']))
            return widget
            
        else:
            # Default to line edit for VARCHAR, CHAR, TEXT, etc.
            widget = QLineEdit()
            if column.get('default'):
                widget.setText(str(column['default']))
            
            # Set placeholder for required fields
            if column['notnull'] and not column['pk']:
                widget.setPlaceholderText("Required field")
            
            return widget
    
    def populate_fields(self):
        """Populate fields with existing record data"""
        if not self.existing_record:
            return
        
        for column in self.table_schema:
            col_name = column['name']
            if col_name not in self.existing_record:
                continue
            
            value = self.existing_record[col_name]
            widget = self.field_widgets[col_name]
            
            if isinstance(widget, QSpinBox):
                widget.setValue(int(value) if value is not None else 0)
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(float(value) if value is not None else 0.0)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(bool(value) if value is not None else False)
            elif isinstance(widget, QDateEdit):
                if value:
                    try:
                        # Assume ISO date format
                        date_parts = str(value).split('-')
                        if len(date_parts) == 3:
                            widget.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
                    except:
                        pass
            elif isinstance(widget, QTimeEdit):
                if value:
                    try:
                        # Assume HH:MM:SS format
                        time_parts = str(value).split(':')
                        if len(time_parts) >= 2:
                            hour = int(time_parts[0])
                            minute = int(time_parts[1])
                            second = int(time_parts[2]) if len(time_parts) > 2 else 0
                            widget.setTime(QTime(hour, minute, second))
                    except:
                        pass
            elif isinstance(widget, QTextEdit):
                widget.setPlainText(str(value) if value is not None else "")
            elif isinstance(widget, QLineEdit):
                widget.setText(str(value) if value is not None else "")
    
    def get_field_values(self) -> Dict[str, Any]:
        """Get values from all field widgets"""
        values = {}
        
        for column in self.table_schema:
            col_name = column['name']
            widget = self.field_widgets[col_name]
            
            if isinstance(widget, QSpinBox):
                values[col_name] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                values[col_name] = widget.value()
            elif isinstance(widget, QCheckBox):
                values[col_name] = 1 if widget.isChecked() else 0
            elif isinstance(widget, QDateEdit):
                date = widget.date()
                values[col_name] = date.toString("yyyy-MM-dd")
            elif isinstance(widget, QTimeEdit):
                time = widget.time()
                values[col_name] = time.toString("HH:mm:ss")
            elif isinstance(widget, QTextEdit):
                text = widget.toPlainText().strip()
                values[col_name] = text if text else None
            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                values[col_name] = text if text else None
        
        return values
    
    def validate_data(self):
        """Validate form data"""
        values = self.get_field_values()
        
        # Basic validation
        errors = []
        
        for column in self.table_schema:
            col_name = column['name']
            value = values.get(col_name)
            
            # Check required fields
            if column['notnull'] and not column['pk'] and (value is None or value == ""):
                errors.append(f"Field '{col_name}' is required")
            
            # Check data types
            if value is not None and value != "":
                col_type = column['type'].upper()
                
                if 'INT' in col_type:
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        errors.append(f"Field '{col_name}' must be an integer")
                
                elif 'REAL' in col_type or 'FLOAT' in col_type:
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        errors.append(f"Field '{col_name}' must be a number")
        
        # Use database validation
        is_valid, db_message = self.db_operations.validate_constraints(self.table_name, values)
        if not is_valid:
            errors.append(db_message)
        
        if errors:
            QMessageBox.warning(self, "Validation Errors", "\n".join(errors))
            return False
        else:
            QMessageBox.information(self, "Validation", "All data is valid!")
            return True
    
    def accept_record(self):
        """Accept and save record"""
        values = self.get_field_values()
        
        # Validate data first
        is_valid, message = self.db_operations.validate_constraints(self.table_name, values)
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", message)
            return
        
        # Remove None values for insert, but keep them for update
        if not self.is_edit_mode:
            values = {k: v for k, v in values.items() if v is not None}
        
        try:
            if self.is_edit_mode:
                # Update existing record
                pk_columns = [col['name'] for col in self.table_schema if col['pk']]
                if pk_columns:
                    # Use primary key for WHERE clause
                    conditions = [f"{col} = ?" for col in pk_columns]
                    where_clause = " AND ".join(conditions)
                    where_params = [self.existing_record[col] for col in pk_columns]
                    
                    # Remove primary key columns from update data
                    update_data = {k: v for k, v in values.items() if k not in pk_columns}
                    
                    success = self.db_operations.update_record(
                        self.table_name, update_data, where_clause, where_params
                    )
                else:
                    # No primary key, use all original values for WHERE clause
                    conditions = [f"{col['name']} = ?" for col in self.table_schema]
                    where_clause = " AND ".join(conditions)
                    where_params = [self.existing_record[col['name']] for col in self.table_schema]
                    
                    success = self.db_operations.update_record(
                        self.table_name, values, where_clause, where_params
                    )
                
                if success:
                    QMessageBox.information(self, "Success", "Record updated successfully!")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", "Failed to update record")
            else:
                # Insert new record
                success = self.db_operations.insert_record(self.table_name, values)
                
                if success:
                    QMessageBox.information(self, "Success", "Record added successfully!")
                    self.accept()
                else:
                    QMessageBox.critical(self, "Error", "Failed to add record")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database error: {str(e)}")