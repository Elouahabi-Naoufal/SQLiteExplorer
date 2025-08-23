# SQLite Manager - Professional Database Management Tool

A full-featured desktop application for managing SQLite databases with complete CRUD operations, schema management, and advanced features.

## Features

### Database Operations (25+ Functions)
1. **Connection Management**
   - Connect to SQLite or SQLCipher databases
   - Disconnect safely with transaction handling
   - Test connection status
   - Auto-reconnect functionality

2. **Transaction Control**
   - Begin/commit/rollback transactions
   - Automatic transaction management
   - Transaction logging

3. **Schema Management**
   - Read all tables, views, indexes, triggers
   - Create, rename, and drop tables
   - Add, rename, or drop columns
   - Create, delete, and modify indexes
   - Create, delete, and modify triggers
   - View table relationships and foreign keys

4. **Data Operations**
   - Insert records (single and batch)
   - Update records (single and batch)
   - Delete records (single, multiple, batch)
   - Search and filter records
   - Sort table data
   - Pagination for large datasets

5. **Query Execution**
   - Execute arbitrary SQL commands (DDL, DML, SELECT)
   - SQL syntax validation
   - Query execution plans
   - Query history tracking

6. **Import/Export**
   - Export table data to CSV or JSON
   - Import CSV or JSON into tables
   - Column mapping for imports
   - Data validation during import

7. **Advanced Features**
   - Backup and restore databases
   - Undo/redo operations logging
   - Multi-tab interface
   - Dark/Light theme support
   - Session management
   - Recent databases tracking

### GUI Features
- **Split View Layout**: Schema tree on left, data tables on right
- **Multi-tab Support**: Open multiple tables simultaneously
- **Dynamic Forms**: Auto-generated forms based on table schema
- **Context Menus**: Right-click operations for tables and records
- **Keyboard Shortcuts**: Quick access to common operations
- **Confirmation Dialogs**: Safety prompts for destructive actions
- **Error Handling**: Comprehensive error messages with SQLite codes

## Installation

### Requirements
```bash
pip install -r requirements.txt
```

### Dependencies
- PyQt6 >= 6.4.0
- pycryptodome >= 3.17.0 (for SQLCipher support)

## Usage

### Running the Application
```bash
python main.py
```

### Basic Operations

1. **Connect to Database**
   - File → Connect to Database
   - Browse for existing .db file or create new
   - Optional: Enable SQLCipher encryption

2. **View Tables**
   - Schema tree shows all tables, views, indexes
   - Double-click table to open in new tab
   - View column information and constraints

3. **Manage Data**
   - Add Record: Click "Add Record" button
   - Edit Record: Double-click row or use "Edit Record"
   - Delete Record: Select row and click "Delete Record"
   - Search: Use search box to filter records

4. **Execute SQL**
   - Edit → Execute SQL (Ctrl+E)
   - Write custom queries
   - View results in table format
   - Access query history

5. **Import/Export**
   - Export: Click "Export" button in table view
   - Import: Use SQL executor or custom import dialogs
   - Supports CSV and JSON formats

## Project Structure

```
dbgui/
├── main.py                 # Application entry point
├── db/                     # Database logic
│   ├── connection.py       # Connection management
│   ├── schema.py          # Schema operations
│   ├── operations.py      # CRUD operations
│   └── queries.py         # Query execution
├── ui/                     # GUI components
│   ├── main_window.py     # Main application window
│   ├── table_view.py      # Table data display
│   ├── forms.py           # Dynamic form generation
│   └── dialogs/           # Dialog windows
│       ├── connection_dialog.py
│       ├── sql_executor.py
│       ├── record_editor.py
│       └── table_editor.py
├── utils/                  # Utilities
│   ├── logger.py          # Logging system
│   ├── backup.py          # Backup/restore
│   ├── export.py          # Import/export
│   ├── session.py         # Session management
│   └── theme.py           # Theme management
├── resources/              # Resources
│   └── styles.qss         # Stylesheets
├── requirements.txt        # Dependencies
└── README.md              # Documentation
```

## Architecture

### Database Layer (`db/`)
- **connection.py**: Manages SQLite connections, transactions
- **schema.py**: Handles table/view/index/trigger operations
- **operations.py**: CRUD operations with validation
- **queries.py**: SQL execution with history tracking

### UI Layer (`ui/`)
- **main_window.py**: Main application window with split view
- **table_view.py**: Data display with pagination and filtering
- **forms.py**: Dynamic form generation based on schema
- **dialogs/**: Specialized dialogs for various operations

### Utilities (`utils/`)
- **logger.py**: Comprehensive logging system
- **backup.py**: Database backup and restore
- **export.py**: CSV/JSON import/export
- **session.py**: Application state persistence
- **theme.py**: Theme management system

## Key Features Implementation

### 1. Dynamic Schema Handling
- Automatically detects table structure
- Generates appropriate input widgets for each data type
- Validates data against schema constraints
- Handles primary keys, foreign keys, and unique constraints

### 2. Transaction Safety
- All operations wrapped in transactions
- Automatic rollback on errors
- Manual transaction control available
- Connection state monitoring

### 3. Data Validation
- Type checking against column definitions
- Required field validation
- Constraint enforcement
- Import data validation

### 4. Performance Optimization
- Pagination for large datasets
- Lazy loading of table data
- Efficient query execution
- Memory management for large results

### 5. User Experience
- Intuitive split-view interface
- Keyboard shortcuts for power users
- Context-sensitive menus
- Comprehensive error messages
- Session persistence

## Advanced Usage

### Custom SQL Queries
```sql
-- Complex joins
SELECT t1.*, t2.name 
FROM table1 t1 
JOIN table2 t2 ON t1.id = t2.table1_id;

-- Data analysis
SELECT category, COUNT(*), AVG(price) 
FROM products 
GROUP BY category 
ORDER BY COUNT(*) DESC;
```

### Batch Operations
- Use SQL executor for batch inserts
- Import CSV files with column mapping
- Batch update operations via SQL

### Database Maintenance
- Regular backups via File → Backup Database
- VACUUM operations via SQL executor
- Index optimization and analysis

## Troubleshooting

### Common Issues
1. **Connection Failed**: Check file permissions and path
2. **Import Errors**: Verify CSV format and column mapping
3. **Performance Issues**: Use pagination and indexes
4. **Theme Issues**: Reset to default theme in preferences

### Logging
- All operations logged to `sqlite_manager.log`
- Error details available in log file
- Debug mode available for development

## Contributing

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Comprehensive docstrings
- Modular design principles

### Testing
- Test with various SQLite database sizes
- Verify import/export functionality
- Check theme switching
- Validate error handling

## License

This project is open source and available under the MIT License.

## Support

For issues and feature requests, please check the documentation or create an issue in the project repository.