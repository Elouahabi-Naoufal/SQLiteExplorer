"""Table view widget for displaying and editing table data"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                            QTableWidgetItem, QPushButton, QLineEdit, QLabel,
                            QComboBox, QSpinBox, QMessageBox, QHeaderView,
                            QMenu, QInputDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QContextMenuEvent
from typing import List, Dict, Any, Optional

from db.operations import DatabaseOperations
from db.queries import QueryExecutor
from db.schema import SchemaManager
from .dialogs.record_editor import RecordEditorDialog
from utils.export import ExportManager

class TableView(QWidget):
    """Widget for viewing and editing table data"""
    
    record_changed = pyqtSignal()
    
    def __init__(self, table_name: str, db_operations: DatabaseOperations, 
                 query_executor: QueryExecutor, schema_manager: SchemaManager):
        super().__init__()
        self.table_name = table_name
        self.db_operations = db_operations
        self.query_executor = query_executor
        self.schema_manager = schema_manager
        self.export_manager = ExportManager()
        
        self.current_page = 0
        self.page_size = 100
        self.total_records = 0
        self.current_filter = ""
        self.current_sort = ""
        
        self.table_schema = []
        self.records = []
        
        self.init_ui()
        self.load_schema()
        self.load_data()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        # Search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search...")
        self.search_input.returnPressed.connect(self.search_records)
        toolbar_layout.addWidget(QLabel("Search:"))
        toolbar_layout.addWidget(self.search_input)
        
        # Filter
        self.filter_column = QComboBox()
        self.filter_value = QLineEdit()
        self.filter_value.returnPressed.connect(self.apply_filter)
        toolbar_layout.addWidget(QLabel("Filter:"))
        toolbar_layout.addWidget(self.filter_column)
        toolbar_layout.addWidget(self.filter_value)
        
        # Buttons
        self.add_btn = QPushButton("Add Record")
        self.add_btn.clicked.connect(self.add_record)
        toolbar_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("Edit Record")
        self.edit_btn.clicked.connect(self.edit_record)
        toolbar_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("Delete Record")
        self.delete_btn.clicked.connect(self.delete_record)
        toolbar_layout.addWidget(self.delete_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_data)
        toolbar_layout.addWidget(self.refresh_btn)
        
        self.export_btn = QPushButton("Export")
        self.export_btn.clicked.connect(self.export_data)
        toolbar_layout.addWidget(self.export_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.table_widget.cellDoubleClicked.connect(self.edit_record)
        layout.addWidget(self.table_widget)
        
        # Pagination
        pagination_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.previous_page)
        pagination_layout.addWidget(self.prev_btn)
        
        self.page_label = QLabel("Page 1 of 1")
        pagination_layout.addWidget(self.page_label)
        
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(self.next_btn)
        
        self.page_size_spin = QSpinBox()
        self.page_size_spin.setRange(10, 1000)
        self.page_size_spin.setValue(self.page_size)
        self.page_size_spin.valueChanged.connect(self.change_page_size)
        pagination_layout.addWidget(QLabel("Page Size:"))
        pagination_layout.addWidget(self.page_size_spin)
        
        self.record_count_label = QLabel("0 records")
        pagination_layout.addWidget(self.record_count_label)
        
        pagination_layout.addStretch()
        layout.addLayout(pagination_layout)
    
    def load_schema(self):
        """Load table schema"""
        self.table_schema = self.schema_manager.get_table_schema(self.table_name)
        
        # Setup filter column combo
        self.filter_column.clear()
        self.filter_column.addItem("All Columns")
        for column in self.table_schema:
            self.filter_column.addItem(column['name'])
    
    def load_data(self):
        """Load table data with pagination"""
        offset = self.current_page * self.page_size
        
        # Build where clause for filtering
        where_clause = None
        where_params = None
        
        if self.current_filter:
            if self.filter_column.currentText() == "All Columns":
                # Search all text columns
                text_columns = [col['name'] for col in self.table_schema 
                              if 'TEXT' in col['type'].upper() or 'VARCHAR' in col['type'].upper()]
                if text_columns:
                    conditions = [f"{col} LIKE ?" for col in text_columns]
                    where_clause = " OR ".join(conditions)
                    where_params = [f"%{self.current_filter}%" for _ in text_columns]
            else:
                # Filter specific column
                column_name = self.filter_column.currentText()
                where_clause = f"{column_name} LIKE ?"
                where_params = [f"%{self.current_filter}%"]
        
        # Load records
        self.records = self.db_operations.get_records(
            self.table_name, 
            limit=self.page_size, 
            offset=offset,
            where_clause=where_clause,
            where_params=where_params,
            order_by=self.current_sort
        )
        
        # Get total count
        self.total_records = self.db_operations.count_records(
            self.table_name, where_clause, where_params
        )
        
        self.update_table_display()
        self.update_pagination_info()
    
    def update_table_display(self):
        """Update table widget with current data"""
        if not self.records:
            self.table_widget.setRowCount(0)
            self.table_widget.setColumnCount(0)
            return
        
        # Set up table
        self.table_widget.setRowCount(len(self.records))
        self.table_widget.setColumnCount(len(self.table_schema))
        
        # Set headers
        headers = [col['name'] for col in self.table_schema]
        self.table_widget.setHorizontalHeaderLabels(headers)
        
        # Populate data
        for row_idx, record in enumerate(self.records):
            for col_idx, column in enumerate(self.table_schema):
                value = record.get(column['name'], '')
                if value is None:
                    value = ''
                
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Read-only
                self.table_widget.setItem(row_idx, col_idx, item)
        
        # Auto-resize columns
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    
    def update_pagination_info(self):
        """Update pagination controls"""
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
        current_page_display = self.current_page + 1
        
        self.page_label.setText(f"Page {current_page_display} of {total_pages}")
        self.record_count_label.setText(f"{self.total_records} records")
        
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)
    
    def search_records(self):
        """Search records"""
        self.current_filter = self.search_input.text()
        self.current_page = 0
        self.load_data()
    
    def apply_filter(self):
        """Apply column filter"""
        self.current_filter = self.filter_value.text()
        self.current_page = 0
        self.load_data()
    
    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.load_data()
    
    def next_page(self):
        """Go to next page"""
        total_pages = (self.total_records + self.page_size - 1) // self.page_size
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.load_data()
    
    def change_page_size(self, new_size: int):
        """Change page size"""
        self.page_size = new_size
        self.current_page = 0
        self.load_data()
    
    def add_record(self):
        """Add new record"""
        dialog = RecordEditorDialog(self.table_name, self.table_schema, 
                                  self.db_operations, self)
        if dialog.exec():
            self.refresh_data()
    
    def edit_record(self):
        """Edit selected record"""
        current_row = self.table_widget.currentRow()
        if current_row < 0 or current_row >= len(self.records):
            QMessageBox.warning(self, "Warning", "Please select a record to edit")
            return
        
        record = self.records[current_row]
        dialog = RecordEditorDialog(self.table_name, self.table_schema, 
                                  self.db_operations, self, record)
        if dialog.exec():
            self.refresh_data()
    
    def delete_record(self):
        """Delete selected record"""
        current_row = self.table_widget.currentRow()
        if current_row < 0 or current_row >= len(self.records):
            QMessageBox.warning(self, "Warning", "Please select a record to delete")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", 
                                   "Are you sure you want to delete this record?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            record = self.records[current_row]
            
            # Build where clause using primary key or all columns
            pk_columns = [col['name'] for col in self.table_schema if col['pk']]
            if pk_columns:
                conditions = [f"{col} = ?" for col in pk_columns]
                where_clause = " AND ".join(conditions)
                where_params = [record[col] for col in pk_columns]
            else:
                # Use all columns if no primary key
                conditions = [f"{col['name']} = ?" for col in self.table_schema]
                where_clause = " AND ".join(conditions)
                where_params = [record[col['name']] for col in self.table_schema]
            
            if self.db_operations.delete_record(self.table_name, where_clause, where_params):
                self.refresh_data()
                QMessageBox.information(self, "Success", "Record deleted successfully")
            else:
                QMessageBox.critical(self, "Error", "Failed to delete record")
    
    def refresh_data(self):
        """Refresh table data"""
        self.load_data()
    
    def export_data(self):
        """Export table data"""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, file_type = QFileDialog.getSaveFileName(
            self, "Export Data", f"{self.table_name}.csv",
            "CSV Files (*.csv);;JSON Files (*.json)"
        )
        
        if file_path:
            # Get all data for export (not just current page)
            all_records = self.db_operations.get_records(self.table_name)
            
            if file_type.startswith("CSV"):
                success = self.export_manager.export_to_csv(all_records, file_path)
            else:
                success = self.export_manager.export_to_json(all_records, file_path)
            
            if success:
                QMessageBox.information(self, "Success", f"Data exported to {file_path}")
            else:
                QMessageBox.critical(self, "Error", "Failed to export data")
    
    def show_context_menu(self, position):
        """Show context menu"""
        if self.table_widget.itemAt(position) is None:
            return
        
        menu = QMenu(self)
        
        edit_action = QAction("Edit Record", self)
        edit_action.triggered.connect(self.edit_record)
        menu.addAction(edit_action)
        
        delete_action = QAction("Delete Record", self)
        delete_action.triggered.connect(self.delete_record)
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        copy_action = QAction("Copy Cell", self)
        copy_action.triggered.connect(self.copy_cell)
        menu.addAction(copy_action)
        
        menu.exec(self.table_widget.mapToGlobal(position))
    
    def copy_cell(self):
        """Copy selected cell to clipboard"""
        current_item = self.table_widget.currentItem()
        if current_item:
            from PyQt6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(current_item.text())
    
    def sort_by_column(self, column_index: int):
        """Sort table by column"""
        if column_index < 0 or column_index >= len(self.table_schema):
            return
        
        column_name = self.table_schema[column_index]['name']
        
        # Toggle sort order
        if self.current_sort == f"{column_name} ASC":
            self.current_sort = f"{column_name} DESC"
        else:
            self.current_sort = f"{column_name} ASC"
        
        self.current_page = 0
        self.load_data()