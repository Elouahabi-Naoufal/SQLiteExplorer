"""Dynamic form generation based on table schema"""

from PyQt6.QtWidgets import (QWidget, QFormLayout, QLineEdit, QTextEdit, 
                            QSpinBox, QDoubleSpinBox, QCheckBox, QComboBox,
                            QDateEdit, QTimeEdit, QLabel, QVBoxLayout)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal
from typing import Dict, Any, List, Optional

class DynamicForm(QWidget):
    """Dynamically generated form based on table schema"""
    
    data_changed = pyqtSignal()
    
    def __init__(self, table_schema: List[Dict[str, Any]], parent=None):
        super().__init__(parent)
        self.table_schema = table_schema
        self.field_widgets = {}
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize form UI"""
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        for column in self.table_schema:
            field_widget = self.create_field_widget(column)
            self.field_widgets[column['name']] = field_widget
            
            # Create label with indicators
            label_text = column['name']
            if column['pk']:
                label_text += " (PK)"
            if column['notnull'] and not column['pk']:
                label_text += " *"
            
            label = QLabel(label_text)
            form_layout.addRow(label, field_widget)
        
        layout.addLayout(form_layout)
    
    def create_field_widget(self, column: Dict[str, Any]):
        """Create appropriate widget for column type"""
        col_type = column['type'].upper()
        
        if 'INT' in col_type:
            widget = QSpinBox()
            widget.setRange(-2147483648, 2147483647)
            widget.valueChanged.connect(self.data_changed.emit)
            return widget
            
        elif 'REAL' in col_type or 'FLOAT' in col_type or 'DOUBLE' in col_type:
            widget = QDoubleSpinBox()
            widget.setRange(-999999999.99, 999999999.99)
            widget.setDecimals(6)
            widget.valueChanged.connect(self.data_changed.emit)
            return widget
            
        elif 'BOOL' in col_type:
            widget = QCheckBox()
            widget.stateChanged.connect(self.data_changed.emit)
            return widget
            
        elif 'DATE' in col_type:
            widget = QDateEdit()
            widget.setDate(QDate.currentDate())
            widget.setCalendarPopup(True)
            widget.dateChanged.connect(self.data_changed.emit)
            return widget
            
        elif 'TIME' in col_type:
            widget = QTimeEdit()
            widget.setTime(QTime.currentTime())
            widget.timeChanged.connect(self.data_changed.emit)
            return widget
            
        elif 'TEXT' in col_type and ('LONG' in col_type or 'MEMO' in col_type):
            widget = QTextEdit()
            widget.setMaximumHeight(100)
            widget.textChanged.connect(self.data_changed.emit)
            return widget
            
        else:
            # Default to line edit
            widget = QLineEdit()
            if column['notnull'] and not column['pk']:
                widget.setPlaceholderText("Required field")
            widget.textChanged.connect(self.data_changed.emit)
            return widget
    
    def set_data(self, data: Dict[str, Any]):
        """Set form data"""
        for column in self.table_schema:
            col_name = column['name']
            if col_name not in data:
                continue
            
            value = data[col_name]
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
                        date_parts = str(value).split('-')
                        if len(date_parts) == 3:
                            widget.setDate(QDate(int(date_parts[0]), int(date_parts[1]), int(date_parts[2])))
                    except:
                        pass
            elif isinstance(widget, QTimeEdit):
                if value:
                    try:
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
    
    def get_data(self) -> Dict[str, Any]:
        """Get form data"""
        data = {}
        
        for column in self.table_schema:
            col_name = column['name']
            widget = self.field_widgets[col_name]
            
            if isinstance(widget, QSpinBox):
                data[col_name] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                data[col_name] = widget.value()
            elif isinstance(widget, QCheckBox):
                data[col_name] = 1 if widget.isChecked() else 0
            elif isinstance(widget, QDateEdit):
                date = widget.date()
                data[col_name] = date.toString("yyyy-MM-dd")
            elif isinstance(widget, QTimeEdit):
                time = widget.time()
                data[col_name] = time.toString("HH:mm:ss")
            elif isinstance(widget, QTextEdit):
                text = widget.toPlainText().strip()
                data[col_name] = text if text else None
            elif isinstance(widget, QLineEdit):
                text = widget.text().strip()
                data[col_name] = text if text else None
        
        return data
    
    def clear_form(self):
        """Clear all form fields"""
        for column in self.table_schema:
            col_name = column['name']
            widget = self.field_widgets[col_name]
            
            if isinstance(widget, QSpinBox):
                widget.setValue(0)
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(0.0)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(False)
            elif isinstance(widget, QDateEdit):
                widget.setDate(QDate.currentDate())
            elif isinstance(widget, QTimeEdit):
                widget.setTime(QTime.currentTime())
            elif isinstance(widget, QTextEdit):
                widget.clear()
            elif isinstance(widget, QLineEdit):
                widget.clear()
    
    def validate_form(self) -> tuple[bool, str]:
        """Validate form data"""
        data = self.get_data()
        errors = []
        
        for column in self.table_schema:
            col_name = column['name']
            value = data.get(col_name)
            
            # Check required fields
            if column['notnull'] and not column['pk'] and (value is None or value == ""):
                errors.append(f"Field '{col_name}' is required")
            
            # Basic type validation
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
        
        if errors:
            return False, "\n".join(errors)
        
        return True, "Valid"
    
    def set_read_only(self, read_only: bool):
        """Set form to read-only mode"""
        for widget in self.field_widgets.values():
            if hasattr(widget, 'setReadOnly'):
                widget.setReadOnly(read_only)
            elif hasattr(widget, 'setEnabled'):
                widget.setEnabled(not read_only)