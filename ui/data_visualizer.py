"""Data visualization widget for charts and graphs"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QComboBox, QLabel, QMessageBox, QSplitter)
from PyQt6.QtCore import Qt
try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import pandas as pd
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    FigureCanvas = None
    Figure = None
    pd = None
from typing import List, Dict, Any

class DataVisualizerWidget(QWidget):
    """Widget for creating data visualizations"""
    
    def __init__(self, data: List[Dict[str, Any]], table_name: str):
        super().__init__()
        
        if not MATPLOTLIB_AVAILABLE:
            self.show_error()
            return
            
        self.data = data
        self.table_name = table_name
        self.df = pd.DataFrame(data) if data else pd.DataFrame()
        
        self.init_ui()
    
    def show_error(self):
        """Show error message when matplotlib is not available"""
        layout = QVBoxLayout(self)
        error_label = QLabel("Visualization requires matplotlib and pandas.\nInstall with: pip install matplotlib pandas")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(error_label)
        
    def init_ui(self):
        """Initialize user interface"""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        layout = QVBoxLayout(self)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Chart Type:"))
        self.chart_type = QComboBox()
        self.chart_type.addItems(["Bar Chart", "Line Chart", "Pie Chart", "Histogram", "Scatter Plot"])
        controls_layout.addWidget(self.chart_type)
        
        controls_layout.addWidget(QLabel("X Column:"))
        self.x_column = QComboBox()
        controls_layout.addWidget(self.x_column)
        
        controls_layout.addWidget(QLabel("Y Column:"))
        self.y_column = QComboBox()
        controls_layout.addWidget(self.y_column)
        
        self.generate_btn = QPushButton("Generate Chart")
        self.generate_btn.clicked.connect(self.generate_chart)
        controls_layout.addWidget(self.generate_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Chart canvas
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.populate_columns()
        
    def populate_columns(self):
        """Populate column dropdowns"""
        if not MATPLOTLIB_AVAILABLE or self.df.empty:
            return
            
        columns = list(self.df.columns)
        # Convert columns to numeric where possible
        for col in columns:
            self.df[col] = pd.to_numeric(self.df[col], errors='ignore')
        
        numeric_columns = list(self.df.select_dtypes(include=['number']).columns)
        
        self.x_column.clear()
        self.y_column.clear()
        
        self.x_column.addItems(columns)
        self.y_column.addItems(numeric_columns if numeric_columns else columns)
        
    def generate_chart(self):
        """Generate selected chart type"""
        if self.df.empty:
            QMessageBox.warning(self, "Warning", "No data available for visualization")
            return
            
        chart_type = self.chart_type.currentText()
        x_col = self.x_column.currentText()
        y_col = self.y_column.currentText()
        
        if not x_col or not y_col:
            QMessageBox.warning(self, "Warning", "Please select both X and Y columns")
            return
            
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        try:
            if chart_type == "Bar Chart":
                if pd.api.types.is_numeric_dtype(self.df[y_col]):
                    self.df.groupby(x_col)[y_col].sum().plot(kind='bar', ax=ax)
                else:
                    self.df[x_col].value_counts().plot(kind='bar', ax=ax)
                ax.set_title(f"{y_col} by {x_col}")
                
            elif chart_type == "Line Chart":
                if pd.api.types.is_numeric_dtype(self.df[y_col]):
                    self.df.plot(x=x_col, y=y_col, kind='line', ax=ax, marker='o')
                    ax.set_title(f"{y_col} over {x_col}")
                else:
                    QMessageBox.warning(self, "Warning", "Line chart requires numeric Y column")
                    return
                
            elif chart_type == "Pie Chart":
                if pd.api.types.is_numeric_dtype(self.df[y_col]):
                    data_grouped = self.df.groupby(x_col)[y_col].sum()
                else:
                    data_grouped = self.df[x_col].value_counts()
                ax.pie(data_grouped.values, labels=data_grouped.index, autopct='%1.1f%%')
                ax.set_title(f"{y_col} distribution by {x_col}")
                
            elif chart_type == "Histogram":
                if pd.api.types.is_numeric_dtype(self.df[y_col]):
                    self.df[y_col].hist(bins=20, ax=ax)
                    ax.set_title(f"Distribution of {y_col}")
                    ax.set_xlabel(y_col)
                else:
                    QMessageBox.warning(self, "Warning", "Histogram requires numeric column")
                    return
                
            elif chart_type == "Scatter Plot":
                if pd.api.types.is_numeric_dtype(self.df[x_col]) and pd.api.types.is_numeric_dtype(self.df[y_col]):
                    self.df.plot.scatter(x=x_col, y=y_col, ax=ax)
                    ax.set_title(f"{y_col} vs {x_col}")
                else:
                    QMessageBox.warning(self, "Warning", "Scatter plot requires numeric columns")
                    return
            
            ax.tick_params(axis='x', rotation=45)
            self.figure.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate chart: {str(e)}")