"""SQL query execution and management"""

import sqlite3
from typing import List, Dict, Any, Optional, Tuple
from .connection import DatabaseConnection
from utils.logger import Logger

class QueryExecutor:
    """Executes SQL queries and manages query history"""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self.logger = Logger()
        self.query_history = []
    
    def execute_select(self, query: str, params: Optional[List[Any]] = None) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Execute SELECT query and return results with column names"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return [], []
            
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            
            columns = [description[0] for description in cursor.description] if cursor.description else []
            results = [dict(row) for row in cursor.fetchall()]
            
            self.logger.log(f"SELECT query executed: {len(results)} rows returned")
            self._add_to_history(query, params)
            
            return results, columns
            
        except Exception as e:
            self.logger.log(f"SELECT query failed: {str(e)}", "ERROR")
            return [], []
    
    def execute_dml(self, query: str, params: Optional[List[Any]] = None) -> Tuple[bool, int, str]:
        """Execute INSERT, UPDATE, DELETE query"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False, 0, "No database connection"
            
            if params:
                cursor = conn.execute(query, params)
            else:
                cursor = conn.execute(query)
            
            conn.commit()
            rows_affected = cursor.rowcount
            
            self.logger.log(f"DML query executed: {rows_affected} rows affected")
            self._add_to_history(query, params)
            
            return True, rows_affected, "Success"
            
        except Exception as e:
            error_msg = str(e)
            self.logger.log(f"DML query failed: {error_msg}", "ERROR")
            return False, 0, error_msg
    
    def execute_ddl(self, query: str) -> Tuple[bool, str]:
        """Execute DDL query (CREATE, ALTER, DROP)"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False, "No database connection"
            
            conn.execute(query)
            conn.commit()
            
            self.logger.log(f"DDL query executed successfully")
            self._add_to_history(query)
            
            return True, "Success"
            
        except Exception as e:
            error_msg = str(e)
            self.logger.log(f"DDL query failed: {error_msg}", "ERROR")
            return False, error_msg
    
    def execute_script(self, script: str) -> Tuple[bool, str]:
        """Execute multiple SQL statements"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False, "No database connection"
            
            conn.executescript(script)
            conn.commit()
            
            self.logger.log(f"SQL script executed successfully")
            self._add_to_history(script)
            
            return True, "Success"
            
        except Exception as e:
            error_msg = str(e)
            self.logger.log(f"SQL script failed: {error_msg}", "ERROR")
            return False, error_msg
    
    def execute_query(self, query: str, params: Optional[List[Any]] = None) -> Tuple[bool, Any, str]:
        """Execute any SQL query and return appropriate results"""
        query_type = query.strip().upper().split()[0]
        
        if query_type == 'SELECT':
            results, columns = self.execute_select(query, params)
            return True, {'results': results, 'columns': columns}, "Success"
        elif query_type in ['INSERT', 'UPDATE', 'DELETE']:
            success, rows_affected, message = self.execute_dml(query, params)
            return success, {'rows_affected': rows_affected}, message
        elif query_type in ['CREATE', 'ALTER', 'DROP']:
            success, message = self.execute_ddl(query)
            return success, None, message
        else:
            # Try as general query
            try:
                conn = self.db.get_connection()
                if not conn:
                    return False, None, "No database connection"
                
                if params:
                    cursor = conn.execute(query, params)
                else:
                    cursor = conn.execute(query)
                
                conn.commit()
                
                # Try to get results if it's a query that returns data
                try:
                    if cursor.description:
                        columns = [desc[0] for desc in cursor.description]
                        results = [dict(row) for row in cursor.fetchall()]
                        return True, {'results': results, 'columns': columns}, "Success"
                    else:
                        return True, {'rows_affected': cursor.rowcount}, "Success"
                except:
                    return True, None, "Success"
                    
            except Exception as e:
                error_msg = str(e)
                self.logger.log(f"Query execution failed: {error_msg}", "ERROR")
                return False, None, error_msg
    
    def get_query_plan(self, query: str) -> List[Dict[str, Any]]:
        """Get query execution plan"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return []
            
            explain_query = f"EXPLAIN QUERY PLAN {query}"
            cursor = conn.execute(explain_query)
            
            return [dict(row) for row in cursor.fetchall()]
            
        except Exception as e:
            self.logger.log(f"Query plan failed: {str(e)}", "ERROR")
            return []
    
    def validate_query(self, query: str) -> Tuple[bool, str]:
        """Validate SQL query syntax"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return False, "No database connection"
            
            # Try to prepare the query
            conn.execute(f"EXPLAIN {query}")
            return True, "Query is valid"
            
        except Exception as e:
            return False, str(e)
    
    def get_table_data_preview(self, table_name: str, limit: int = 100) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Get preview of table data"""
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.execute_select(query)
    
    def _add_to_history(self, query: str, params: Optional[List[Any]] = None):
        """Add query to history"""
        self.query_history.append({
            'query': query,
            'params': params,
            'timestamp': self.logger.get_timestamp()
        })
        
        # Keep only last 100 queries
        if len(self.query_history) > 100:
            self.query_history = self.query_history[-100:]
    
    def get_query_history(self) -> List[Dict[str, Any]]:
        """Get query execution history"""
        return self.query_history.copy()
    
    def clear_history(self):
        """Clear query history"""
        self.query_history.clear()
        self.logger.log("Query history cleared")