"""Database CRUD operations"""

import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from .connection import DatabaseConnection
from utils.logger import Logger

class DatabaseOperations:
    """Handles CRUD operations and data manipulation"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self.logger = Logger()
    
    def insert_record(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Insert single record"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False
            
            columns = list(data.keys())
            placeholders = ['?' for _ in columns]
            values = list(data.values())
            
            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            conn.execute(sql, values)
            conn.commit()
            
            self.logger.log(f"Inserted record into {table_name}")
            return True
            
        except Exception as e:
            self.logger.log(f"Insert failed: {str(e)}", "ERROR")
            return False
    
    def batch_insert(self, table_name: str, records: List[Dict[str, Any]]) -> bool:
        """Insert multiple records"""
        try:
            conn = self.db.get_connection()
            if not conn or not records:
                return False
            
            columns = list(records[0].keys())
            placeholders = ['?' for _ in columns]
            
            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
            
            data = [[record[col] for col in columns] for record in records]
            conn.executemany(sql, data)
            conn.commit()
            
            self.logger.log(f"Batch inserted {len(records)} records into {table_name}")
            return True
            
        except Exception as e:
            self.logger.log(f"Batch insert failed: {str(e)}", "ERROR")
            return False
    
    def update_record(self, table_name: str, data: Dict[str, Any], where_clause: str, where_params: List[Any] = None) -> bool:
        """Update single record"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False
            
            set_clauses = [f"{col} = ?" for col in data.keys()]
            values = list(data.values())
            
            sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {where_clause}"
            
            if where_params:
                values.extend(where_params)
            
            conn.execute(sql, values)
            conn.commit()
            
            self.logger.log(f"Updated record in {table_name}")
            return True
            
        except Exception as e:
            self.logger.log(f"Update failed: {str(e)}", "ERROR")
            return False
    
    def batch_update(self, table_name: str, updates: List[Tuple[Dict[str, Any], str, List[Any]]]) -> bool:
        """Update multiple records"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False
            
            for data, where_clause, where_params in updates:
                set_clauses = [f"{col} = ?" for col in data.keys()]
                values = list(data.values())
                
                sql = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE {where_clause}"
                
                if where_params:
                    values.extend(where_params)
                
                conn.execute(sql, values)
            
            conn.commit()
            self.logger.log(f"Batch updated {len(updates)} records in {table_name}")
            return True
            
        except Exception as e:
            self.logger.log(f"Batch update failed: {str(e)}", "ERROR")
            return False
    
    def delete_record(self, table_name: str, where_clause: str, where_params: List[Any] = None) -> bool:
        """Delete record(s)"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False
            
            sql = f"DELETE FROM {table_name} WHERE {where_clause}"
            
            if where_params:
                conn.execute(sql, where_params)
            else:
                conn.execute(sql)
            
            conn.commit()
            
            self.logger.log(f"Deleted record(s) from {table_name}")
            return True
            
        except Exception as e:
            self.logger.log(f"Delete failed: {str(e)}", "ERROR")
            return False
    
    def batch_delete(self, table_name: str, conditions: List[Tuple[str, List[Any]]]) -> bool:
        """Delete multiple records with different conditions"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False
            
            for where_clause, where_params in conditions:
                sql = f"DELETE FROM {table_name} WHERE {where_clause}"
                
                if where_params:
                    conn.execute(sql, where_params)
                else:
                    conn.execute(sql)
            
            conn.commit()
            self.logger.log(f"Batch deleted records from {table_name}")
            return True
            
        except Exception as e:
            self.logger.log(f"Batch delete failed: {str(e)}", "ERROR")
            return False
    
    def get_records(self, table_name: str, limit: Optional[int] = None, offset: Optional[int] = None, 
                   where_clause: Optional[str] = None, where_params: Optional[List[Any]] = None,
                   order_by: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get records from table with optional filtering and pagination"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return []
            
            sql = f"SELECT * FROM {table_name}"
            params = []
            
            if where_clause:
                sql += f" WHERE {where_clause}"
                if where_params:
                    params.extend(where_params)
            
            if order_by:
                sql += f" ORDER BY {order_by}"
            
            if limit:
                sql += f" LIMIT {limit}"
                if offset:
                    sql += f" OFFSET {offset}"
            
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            
            # Convert to list of dictionaries
            records = []
            for row in rows:
                if hasattr(row, 'keys'):
                    records.append(dict(row))
                else:
                    # Handle tuple results from SQLCipher
                    record = {column_names[i]: row[i] for i in range(len(column_names))}
                    records.append(record)
            
            return records
            
        except Exception as e:
            self.logger.log(f"Get records failed: {str(e)}", "ERROR")
            return []
    
    def count_records(self, table_name: str, where_clause: Optional[str] = None, 
                     where_params: Optional[List[Any]] = None) -> int:
        """Count records in table"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return 0
            
            sql = f"SELECT COUNT(*) FROM {table_name}"
            params = []
            
            if where_clause:
                sql += f" WHERE {where_clause}"
                if where_params:
                    params.extend(where_params)
            
            cursor = conn.execute(sql, params)
            result = cursor.fetchone()
            
            if hasattr(result, 'keys'):
                return result[0] if result else 0
            else:
                # Handle tuple results from SQLCipher
                return result[0] if result else 0
            
        except Exception as e:
            self.logger.log(f"Count records failed: {str(e)}", "ERROR")
            return 0
    
    def search_records(self, table_name: str, search_term: str, columns: List[str]) -> List[Dict[str, Any]]:
        """Search records across specified columns"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return []
            
            conditions = [f"{col} LIKE ?" for col in columns]
            where_clause = " OR ".join(conditions)
            params = [f"%{search_term}%" for _ in columns]
            
            sql = f"SELECT * FROM {table_name} WHERE {where_clause}"
            cursor = conn.execute(sql, params)
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            self.logger.log(f"Search failed: {str(e)}", "ERROR")
            return []
    
    def validate_constraints(self, table_name: str, data: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate data against table constraints"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False, "No database connection"
            
            # Get table schema
            cursor = conn.execute(f"PRAGMA table_info({table_name})")
            columns = {row['name']: row for row in cursor.fetchall()}
            
            # Check required fields
            for col_name, col_info in columns.items():
                if col_info['notnull'] and col_name not in data:
                    return False, f"Required field '{col_name}' is missing"
            
            # Check data types (basic validation)
            for field, value in data.items():
                if field in columns:
                    col_type = columns[field]['type'].upper()
                    if value is not None:
                        if 'INT' in col_type and not isinstance(value, int):
                            try:
                                int(value)
                            except ValueError:
                                return False, f"Field '{field}' must be an integer"
                        elif 'REAL' in col_type or 'FLOAT' in col_type:
                            try:
                                float(value)
                            except ValueError:
                                return False, f"Field '{field}' must be a number"
            
            return True, "Validation passed"
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"