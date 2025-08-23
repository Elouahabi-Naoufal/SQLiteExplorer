"""SQL query executor dialog"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QSplitter, QLabel, QTabWidget, QWidget,
                            QMessageBox, QHeaderView, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

from db.queries import QueryExecutor
from utils.query_manager import QueryManager

class SQLExecutorDialog(QDialog):
    """Dialog for executing SQL queries"""
    
    def __init__(self, query_executor: QueryExecutor, parent=None):
        super().__init__(parent)
        self.query_executor = query_executor
        self.query_manager = QueryManager()
        
        self.setWindowTitle("SQL Query Executor")
        self.setModal(False)
        self.resize(800, 600)
        
        self.init_ui()
        self.load_query_history()
    
    def init_ui(self):
        """Initialize user interface"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        execute_btn = QPushButton("Execute (F5)")
        execute_btn.clicked.connect(self.execute_query)
        execute_btn.setShortcut("F5")
        toolbar_layout.addWidget(execute_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_query)
        toolbar_layout.addWidget(clear_btn)
        
        explain_btn = QPushButton("Explain")
        explain_btn.clicked.connect(self.explain_query)
        toolbar_layout.addWidget(explain_btn)
        
        history_btn = QPushButton("Query Manager")
        history_btn.clicked.connect(self.open_query_manager)
        toolbar_layout.addWidget(history_btn)
        
        toolbar_layout.addStretch()
        
        # Query history dropdown
        self.history_combo = QComboBox()
        self.history_combo.setMinimumWidth(200)
        self.history_combo.currentTextChanged.connect(self.load_from_history)
        toolbar_layout.addWidget(QLabel("History:"))
        toolbar_layout.addWidget(self.history_combo)
        
        layout.addLayout(toolbar_layout)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)
        
        # Query editor
        self.query_editor = QTextEdit()
        self.query_editor.setPlaceholderText("Enter SQL query here...")
        
        # Set monospace font
        font = QFont("Courier New", 10)
        font.setFixedPitch(True)
        self.query_editor.setFont(font)
        
        splitter.addWidget(self.query_editor)
        
        # Results area
        self.results_tabs = QTabWidget()
        splitter.addWidget(self.results_tabs)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setAlternatingRowColors(True)
        self.results_tabs.addTab(self.results_table, "Results")
        
        # Messages area
        self.messages_text = QTextEdit()
        self.messages_text.setReadOnly(True)
        self.messages_text.setMaximumHeight(100)
        self.results_tabs.addTab(self.messages_text, "Messages")
        
        # Set splitter proportions
        splitter.setSizes([300, 300])
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.row_count_label = QLabel("0 rows")
        status_layout.addWidget(self.row_count_label)
        
        layout.addLayout(status_layout)
    
    def execute_query(self):
        """Execute the SQL query"""
        query = self.query_editor.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a SQL query")
            return
        
        self.status_label.setText("Executing query...")
        self.messages_text.clear()
        
        try:
            success, result, message = self.query_executor.execute_query(query)
            
            if success:
                if result and 'results' in result:
                    # SELECT query results
                    self.display_results(result['results'], result['columns'])
                    self.messages_text.append(f"Query executed successfully. {len(result['results'])} rows returned.")
                    self.row_count_label.setText(f"{len(result['results'])} rows")
                elif result and 'rows_affected' in result:
                    # DML query results
                    self.clear_results()
                    self.messages_text.append(f"Query executed successfully. {result['rows_affected']} rows affected.")
                    self.row_count_label.setText(f"{result['rows_affected']} rows affected")
                else:
                    # DDL or other queries
                    self.clear_results()
                    self.messages_text.append("Query executed successfully.")
                    self.row_count_label.setText("Query completed")
                
                self.status_label.setText("Query completed")
                self.results_tabs.setCurrentIndex(0)  # Show results tab
                
                # Add to query history
                result_count = len(result['results']) if result and 'results' in result else result.get('rows_affected', 0) if result else 0
                self.query_manager.add_to_history(query, 0, result_count)
            else:
                self.clear_results()
                self.messages_text.append(f"Query failed: {message}")
                self.status_label.setText("Query failed")
                self.results_tabs.setCurrentIndex(1)  # Show messages tab
                
        except Exception as e:
            self.clear_results()
            self.messages_text.append(f"Error: {str(e)}")
            self.status_label.setText("Error")
            self.results_tabs.setCurrentIndex(1)
        
        # Refresh history
        self.load_query_history()
    
    def display_results(self, results, columns):
        """Display query results in table"""
        if not results:
            self.clear_results()
            return
        
        self.results_table.setRowCount(len(results))
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        
        for row_idx, record in enumerate(results):
            for col_idx, column in enumerate(columns):
                value = record.get(column, '')
                if value is None:
                    value = ''
                
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.results_table.setItem(row_idx, col_idx, item)
        
        # Auto-resize columns
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    
    def clear_results(self):
        """Clear results table"""
        self.results_table.setRowCount(0)
        self.results_table.setColumnCount(0)
        self.row_count_label.setText("0 rows")
    
    def clear_query(self):
        """Clear query editor"""
        self.query_editor.clear()
        self.clear_results()
        self.messages_text.clear()
        self.status_label.setText("Ready")
    
    def explain_query(self):
        """Show query execution plan"""
        query = self.query_editor.toPlainText().strip()
        if not query:
            QMessageBox.warning(self, "Warning", "Please enter a SQL query")
            return
        
        try:
            plan = self.query_executor.get_query_plan(query)
            if plan:
                self.display_results(plan, list(plan[0].keys()) if plan else [])
                self.messages_text.append("Query execution plan displayed.")
                self.results_tabs.setCurrentIndex(0)
            else:
                self.messages_text.append("No execution plan available.")
                self.results_tabs.setCurrentIndex(1)
                
        except Exception as e:
            self.messages_text.append(f"Error getting execution plan: {str(e)}")
            self.results_tabs.setCurrentIndex(1)
    
    def load_query_history(self):
        """Load query history into dropdown"""
        self.history_combo.clear()
        self.history_combo.addItem("Select from history...")
        
        history = self.query_executor.get_query_history()
        for entry in reversed(history[-20:]):  # Show last 20 queries
            query_preview = entry['query'][:50].replace('\n', ' ')
            if len(entry['query']) > 50:
                query_preview += "..."
            
            display_text = f"{entry['timestamp']} - {query_preview}"
            self.history_combo.addItem(display_text, entry['query'])
    
    def load_from_history(self, text):
        """Load query from history"""
        if text and text != "Select from history...":
            index = self.history_combo.currentIndex()
            if index > 0:
                query = self.history_combo.itemData(index)
                if query:
                    self.query_editor.setPlainText(query)
    
    def open_query_manager(self):
        """Open query manager dialog"""
        from .query_manager_dialog import QueryManagerDialog
        
        dialog = QueryManagerDialog(self.query_manager, self)
        dialog.query_selected.connect(self.load_query_from_manager)
        dialog.exec()
    
    def load_query_from_manager(self, query: str):
        """Load query from manager"""
        self.query_editor.setPlainText(query)
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_F5:
            self.execute_query()
        else:
            super().keyPressEvent(event)