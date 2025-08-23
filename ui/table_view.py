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
        
        # Buttons with emojis
        self.add_btn = QPushButton("➕")
        self.add_btn.setToolTip("Add Record")
        self.add_btn.clicked.connect(self.add_record)
        toolbar_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("✏️")
        self.edit_btn.setToolTip("Edit Record")
        self.edit_btn.clicked.connect(self.edit_full_record)
        toolbar_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️")
        self.delete_btn.setToolTip("Delete Record")
        self.delete_btn.clicked.connect(self.delete_record)
        toolbar_layout.addWidget(self.delete_btn)
        
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setToolTip("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_data)
        toolbar_layout.addWidget(self.refresh_btn)
        
        self.export_btn = QPushButton("📤")
        self.export_btn.setToolTip("Export")
        self.export_btn.clicked.connect(self.export_data)
        toolbar_layout.addWidget(self.export_btn)
        
        self.visualize_btn = QPushButton("📊")
        self.visualize_btn.setToolTip("Visualize")
        self.visualize_btn.clicked.connect(self.visualize_data)
        toolbar_layout.addWidget(self.visualize_btn)
        
        self.bulk_import_btn = QPushButton("📥")
        self.bulk_import_btn.setToolTip("Bulk Import")
        self.bulk_import_btn.clicked.connect(self.bulk_import)
        toolbar_layout.addWidget(self.bulk_import_btn)
        
        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)
        
        # Style buttons for smooth hover effect
        button_style = """
            QPushButton {
                border: none;
                padding: 8px;
                font-size: 16px;
                border-radius: 4px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 120, 215, 0.1);
                border: 1px solid rgba(0, 120, 215, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(0, 120, 215, 0.2);
            }
        """
        
        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.refresh_btn, 
                   self.export_btn, self.visualize_btn, self.bulk_import_btn]:
            btn.setStyleSheet(button_style)
        
        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_widget.customContextMenuRequested.connect(self.show_context_menu)
        self.table_widget.itemClicked.connect(self.on_cell_clicked)
        self.table_widget.itemChanged.connect(self.on_cell_changed)
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
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)  # Editable
                self.table_widget.setItem(row_idx, col_idx, item)
        
        # Set column resize mode to interactive
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    
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
        total_pages = max(1, (self.total_records + self.page_size - 1) // self.page_size)
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
        from .dialogs.record_editor import RecordEditorDialog
        dialog = RecordEditorDialog(self.table_name, self.table_schema, self.db_operations, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh_data()
            self.record_changed.emit()
    
    def delete_record(self):
        """Delete selected record"""
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a record to delete")
            return
        
        reply = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this record?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            record = self.records[current_row]
            pk_columns = [col['name'] for col in self.table_schema if col.get('pk')]
            
            if pk_columns:
                where_parts = [f"{col} = ?" for col in pk_columns]
                where_clause = " AND ".join(where_parts)
                where_params = [record[col] for col in pk_columns]
            else:
                where_parts = [f"{col} = ?" for col in record.keys()]
                where_clause = " AND ".join(where_parts)
                where_params = list(record.values())
            
            if self.db_operations.delete_record(self.table_name, where_clause, where_params):
                self.refresh_data()
                self.record_changed.emit()
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
            if file_type.startswith("CSV"):
                success = self.export_manager.export_to_csv(self.records, file_path)
            else:
                success = self.export_manager.export_to_json(self.records, file_path)
            
            if success:
                QMessageBox.information(self, "Success", "Data exported successfully")
            else:
                QMessageBox.critical(self, "Error", "Failed to export data")
    
    def visualize_data(self):
        """Open data visualization dialog"""
        if not self.records:
            QMessageBox.warning(self, "Warning", "No data available for visualization")
            return
        
        try:
            from .data_visualizer import DataVisualizerWidget
            from PyQt6.QtWidgets import QDialog, QVBoxLayout
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Data Visualization - {self.table_name}")
            dialog.setGeometry(200, 200, 1000, 700)
            
            layout = QVBoxLayout(dialog)
            visualizer = DataVisualizerWidget(self.records, self.table_name)
            layout.addWidget(visualizer)
            
            dialog.exec()
            
        except ImportError:
            QMessageBox.critical(self, "Error", "Visualization requires matplotlib and pandas.\nInstall with: pip install matplotlib pandas")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open visualization: {str(e)}")
    
    def on_cell_clicked(self, item):
        """Handle cell click for inline editing"""
        self.table_widget.editItem(item)
    
    def on_cell_changed(self, item):
        """Handle cell value change and save to database"""
        row = item.row()
        col = item.column()
        
        if row >= len(self.records) or col >= len(self.table_schema):
            return
        
        record = self.records[row]
        column_name = self.table_schema[col]['name']
        new_value = item.text()
        
        # Build where clause using primary key or all columns
        pk_columns = [c['name'] for c in self.table_schema if c.get('pk')]
        
        if pk_columns:
            where_parts = [f"{col} = ?" for col in pk_columns]
            where_clause = " AND ".join(where_parts)
            where_params = [record[col] for col in pk_columns]
        else:
            where_parts = [f"{c['name']} = ?" for c in self.table_schema]
            where_clause = " AND ".join(where_parts)
            where_params = [record[c['name']] for c in self.table_schema]
        
        # Update database
        update_data = {column_name: new_value}
        
        if self.db_operations.update_record(self.table_name, update_data, where_clause, where_params):
            # Update local record
            self.records[row][column_name] = new_value
            self.record_changed.emit()
        else:
            # Revert change if update failed
            item.setText(str(record[column_name]))
            QMessageBox.critical(self, "Error", "Failed to update record")
    
    def edit_full_record(self):
        """Edit full record in dialog"""
        current_row = self.table_widget.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Warning", "Please select a record to edit")
            return
        
        record = self.records[current_row]
        from .dialogs.record_editor import RecordEditorDialog
        dialog = RecordEditorDialog(self.table_name, self.table_schema, self.db_operations, self, record)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh_data()
            self.record_changed.emit()
    
    def show_context_menu(self, position):
        """Show context menu"""
        menu = QMenu(self)
        
        add_action = menu.addAction("Add Record")
        add_action.triggered.connect(self.add_record)
        
        if self.table_widget.itemAt(position):
            edit_record_action = menu.addAction("Edit Full Record")
            edit_record_action.triggered.connect(self.edit_full_record)
            
            delete_action = menu.addAction("Delete Record")
            delete_action.triggered.connect(self.delete_record)
        
        menu.addSeparator()
        
        refresh_action = menu.addAction("Refresh")
        refresh_action.triggered.connect(self.refresh_data)
        
        export_action = menu.addAction("Export Data")
        export_action.triggered.connect(self.export_data)
        
        visualize_action = menu.addAction("Visualize Data")
        visualize_action.triggered.connect(self.visualize_data)
        
        bulk_import_action = menu.addAction("Bulk Import")
        bulk_import_action.triggered.connect(self.bulk_import)
        
        menu.exec(self.table_widget.mapToGlobal(position))
    
    def bulk_import(self):
        """Open bulk import dialog"""
        try:
            from .dialogs.bulk_import_dialog import BulkImportDialog
            dialog = BulkImportDialog(self.table_name, self.table_schema, self.db_operations, self)
            if dialog.exec() == dialog.DialogCode.Accepted:
                self.refresh_data()
                self.record_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open bulk import: {str(e)}")