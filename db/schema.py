"""Database schema operations"""

import sqlite3
from typing import List, Dict, Any, Optional
from .connection import DatabaseConnection
from utils.logger import Logger

class SchemaManager:
    """Manages database schema operations"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self.logger = Logger()
    
    def get_tables(self) -> List[Dict[str, Any]]:
        """Get all tables in database"""
        try:
            conn = self.db.get_connection()
            if not conn:
                self.logger.log("No database connection", "ERROR")
                return []
            
            # Try simple query first
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
            rows = cursor.fetchall()
            
            tables = []
            for row in rows:
                # Handle both tuple and Row objects
                if hasattr(row, 'keys'):
                    table_name = row['name']
                else:
                    table_name = row[0]
                tables.append({
                    'name': table_name,
                    'type': 'table',
                    'sql': None
                })
            
            self.logger.log(f"Found {len(tables)} tables: {[t['name'] for t in tables]}")
            return tables
            
        except Exception as e:
            self.logger.log(f"Get tables failed: {str(e)}", "ERROR")
            return []
    
    def get_views(self) -> List[Dict[str, Any]]:
        """Get all views in database"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return []
            
            cursor = conn.execute("""
                SELECT name, sql FROM sqlite_master 
                WHERE type='view' ORDER BY name
            """)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.log(f"Get views failed: {str(e)}", "ERROR")
            return []
    
    def get_indexes(self, table_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get indexes for table or all indexes"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return []
            
            query = "SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index'"
            if table_name:
                query += f" AND tbl_name='{table_name}'"
            query += " ORDER BY name"
            
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.log(f"Get indexes failed: {str(e)}", "ERROR")
            return []
    
    def get_triggers(self, table_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get triggers for table or all triggers"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return []
            
            query = "SELECT name, tbl_name, sql FROM sqlite_master WHERE type='trigger'"
            if table_name:
                query += f" AND tbl_name='{table_name}'"
            query += " ORDER BY name"
            
            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.log(f"Get triggers failed: {str(e)}", "ERROR")
            return []
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get column information for table"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return []
            
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            rows = cursor.fetchall()
            
            columns = []
            for row in rows:
                if hasattr(row, 'keys'):
                    columns.append(dict(row))
                else:
                    # Handle tuple results from SQLCipher
                    columns.append({
                        'cid': row[0],
                        'name': row[1],
                        'type': row[2],
                        'notnull': row[3],
                        'dflt_value': row[4],
                        'pk': row[5]
                    })
            
            return columns
        except Exception as e:
            self.logger.log(f"Get table schema failed: {str(e)}", "ERROR")
            return []
    
    def create_table(self, table_name: str, columns: List[Dict[str, str]]) -> bool:
        """Create new table"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False
            
            col_defs = []
            for col in columns:
                col_def = f"{col['name']} {col['type']}"
                if col.get('primary_key'):
                    col_def += " PRIMARY KEY"
                if col.get('not_null'):
                    col_def += " NOT NULL"
                if col.get('unique'):
                    col_def += " UNIQUE"
                if col.get('default'):
                    col_def += f" DEFAULT {col['default']}"
                col_defs.append(col_def)
            
            sql = f"CREATE TABLE {table_name} ({', '.join(col_defs)})"
            conn.execute(sql)
            conn.commit()
            
            self.logger.log(f"Created table: {table_name}")
            return True
            
        except Exception as e:
            self.logger.log(f"Create table failed: {str(e)}", "ERROR")
            return False
    
    def drop_table(self, table_name: str) -> bool:
        """Drop table"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False
            
            conn.execute(f"DROP TABLE IF EXISTS {table_name}")
            conn.commit()
            
            self.logger.log(f"Dropped table: {table_name}")
            return True
            
        except Exception as e:
            self.logger.log(f"Drop table failed: {str(e)}", "ERROR")
            return False
    
    def rename_table(self, old_name: str, new_name: str) -> bool:
        """Rename table"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False
            
            conn.execute(f"ALTER TABLE {old_name} RENAME TO {new_name}")
            conn.commit()
            
            self.logger.log(f"Renamed table: {old_name} -> {new_name}")
            return True
            
        except Exception as e:
            self.logger.log(f"Rename table failed: {str(e)}", "ERROR")
            return False
    
    def add_column(self, table_name: str, column_name: str, column_type: str, default_value: Optional[str] = None) -> bool:
        """Add column to table"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False
            
            sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
            if default_value:
                sql += f" DEFAULT {default_value}"
            
            conn.execute(sql)
            conn.commit()
            
            self.logger.log(f"Added column {column_name} to {table_name}")
            return True
            
        except Exception as e:
            self.logger.log(f"Add column failed: {str(e)}", "ERROR")
            return False
    
    def create_index(self, index_name: str, table_name: str, columns: List[str], unique: bool = False) -> bool:
        """Create index"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False
            
            unique_str = "UNIQUE " if unique else ""
            cols_str = ", ".join(columns)
            sql = f"CREATE {unique_str}INDEX {index_name} ON {table_name} ({cols_str})"
            
            conn.execute(sql)
            conn.commit()
            
            self.logger.log(f"Created index: {index_name}")
            return True
            
        except Exception as e:
            self.logger.log(f"Create index failed: {str(e)}", "ERROR")
            return False
    
    def drop_index(self, index_name: str) -> bool:
        """Drop index"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False
            
            conn.execute(f"DROP INDEX IF EXISTS {index_name}")
            conn.commit()
            
            self.logger.log(f"Dropped index: {index_name}")
            return True
            
        except Exception as e:
            self.logger.log(f"Drop index failed: {str(e)}", "ERROR")
            return False
    
    def get_foreign_keys(self, table_name: str) -> List[Dict[str, Any]]:
        """Get foreign key constraints for table"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return []
            
            cursor = conn.execute(f"PRAGMA foreign_key_list({table_name})")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            self.logger.log(f"Get foreign keys failed: {str(e)}", "ERROR")
            return []