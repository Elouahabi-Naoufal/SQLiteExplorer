"""Database connection management"""

import sqlite3
import os
from typing import Optional, Dict, Any
from utils.logger import Logger

class DatabaseConnection:
    """Manages SQLite database connections and transactions"""
    
    def __init__(self):
        self.connection: Optional[sqlite3.Connection] = None
        self.database_path: Optional[str] = None
        self.logger = Logger()
        
    def connect(self, db_path: str, password: Optional[str] = None) -> bool:
        """Connect to SQLite database"""
        try:
            if self.connection:
                self.disconnect()
            
            # First try without password
            if not password:
                try:
                    self.connection = sqlite3.connect(db_path)
                    self.connection.row_factory = sqlite3.Row
                    self.connection.execute("PRAGMA foreign_keys = ON")
                    self.connection.execute("SELECT name FROM sqlite_master LIMIT 1")
                    self.database_path = db_path
                    self.logger.log(f"Connected to database: {db_path}")
                    return True
                except Exception as e:
                    self.logger.log(f"Standard connection failed: {str(e)}", "WARNING")
                    if self.connection:
                        self.connection.close()
                        self.connection = None
            
            # Try with password or if standard failed
            if password or self.connection is None:
                try:
                    import pysqlcipher3.dbapi2 as sqlcipher
                    self.connection = sqlcipher.connect(db_path)
                    if password:
                        self.connection.execute(f"PRAGMA key = '{password}'")
                    self.connection.row_factory = sqlite3.Row
                    self.connection.execute("PRAGMA foreign_keys = ON")
                    self.connection.execute("SELECT name FROM sqlite_master LIMIT 1")
                    self.database_path = db_path
                    self.logger.log(f"Connected to encrypted database: {db_path}")
                    return True
                except ImportError:
                    self.logger.log("SQLCipher not available", "ERROR")
                    return False
                except Exception as e:
                    self.logger.log(f"Encrypted connection failed: {str(e)}", "ERROR")
                    if self.connection:
                        self.connection.close()
                        self.connection = None
                    return False
            
            return False
            
        except Exception as e:
            self.logger.log(f"Connection failed: {str(e)}", "ERROR")
            if self.connection:
                try:
                    self.connection.close()
                except:
                    pass
                self.connection = None
            return False
    
    def disconnect(self) -> None:
        """Safely disconnect from database"""
        if self.connection:
            try:
                self.connection.close()
                self.logger.log(f"Disconnected from: {self.database_path}")
            except Exception as e:
                self.logger.log(f"Disconnect error: {str(e)}", "ERROR")
            finally:
                self.connection = None
                self.database_path = None
    
    def test_connection(self) -> bool:
        """Test if connection is active"""
        if not self.connection:
            return False
        try:
            self.connection.execute("SELECT 1")
            return True
        except:
            return False
    
    def begin_transaction(self) -> bool:
        """Begin database transaction"""
        try:
            if self.connection:
                self.connection.execute("BEGIN")
                self.logger.log("Transaction started")
                return True
        except Exception as e:
            self.logger.log(f"Begin transaction failed: {str(e)}", "ERROR")
        return False
    
    def commit_transaction(self) -> bool:
        """Commit current transaction"""
        try:
            if self.connection:
                self.connection.commit()
                self.logger.log("Transaction committed")
                return True
        except Exception as e:
            self.logger.log(f"Commit failed: {str(e)}", "ERROR")
        return False
    
    def rollback_transaction(self) -> bool:
        """Rollback current transaction"""
        try:
            if self.connection:
                self.connection.rollback()
                self.logger.log("Transaction rolled back")
                return True
        except Exception as e:
            self.logger.log(f"Rollback failed: {str(e)}", "ERROR")
        return False
    
    def get_connection(self) -> Optional[sqlite3.Connection]:
        """Get current connection"""
        return self.connection
    
    def is_connected(self) -> bool:
        """Check if connected to database"""
        return self.connection is not None and self.test_connection()