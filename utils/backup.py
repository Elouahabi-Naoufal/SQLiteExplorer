"""Database backup and restore utilities"""

import os
import shutil
import sqlite3
from datetime import datetime
from typing import Optional
from .logger import Logger

class BackupManager:
    """Manages database backup and restore operations"""
    
    def __init__(self):
        self.logger = Logger()
    
    def backup_database(self, source_path: str, backup_path: str) -> bool:
        """Backup database to specified path"""
        try:
            if not os.path.exists(source_path):
                self.logger.log(f"Source database not found: {source_path}", "ERROR")
                return False
            
            # Create backup directory if it doesn't exist
            backup_dir = os.path.dirname(backup_path)
            if backup_dir and not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Copy database file
            shutil.copy2(source_path, backup_path)
            
            self.logger.log(f"Database backed up: {source_path} -> {backup_path}")
            return True
            
        except Exception as e:
            self.logger.log(f"Backup failed: {str(e)}", "ERROR")
            return False
    
    def restore_database(self, backup_path: str, target_path: str) -> bool:
        """Restore database from backup"""
        try:
            if not os.path.exists(backup_path):
                self.logger.log(f"Backup file not found: {backup_path}", "ERROR")
                return False
            
            # Verify backup is a valid SQLite database
            if not self.verify_database(backup_path):
                self.logger.log(f"Invalid SQLite database: {backup_path}", "ERROR")
                return False
            
            # Create target directory if it doesn't exist
            target_dir = os.path.dirname(target_path)
            if target_dir and not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            # Copy backup to target
            shutil.copy2(backup_path, target_path)
            
            self.logger.log(f"Database restored: {backup_path} -> {target_path}")
            return True
            
        except Exception as e:
            self.logger.log(f"Restore failed: {str(e)}", "ERROR")
            return False
    
    def create_automatic_backup(self, database_path: str, backup_dir: str = "backups") -> Optional[str]:
        """Create automatic backup with timestamp"""
        try:
            if not os.path.exists(database_path):
                return None
            
            # Create backup directory
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Generate backup filename with timestamp
            db_name = os.path.splitext(os.path.basename(database_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{db_name}_backup_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            if self.backup_database(database_path, backup_path):
                return backup_path
            
            return None
            
        except Exception as e:
            self.logger.log(f"Automatic backup failed: {str(e)}", "ERROR")
            return None
    
    def verify_database(self, database_path: str) -> bool:
        """Verify database file integrity"""
        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            cursor.fetchall()
            conn.close()
            return True
            
        except Exception as e:
            self.logger.log(f"Database verification failed: {str(e)}", "ERROR")
            return False
    
    def get_backup_info(self, backup_path: str) -> dict:
        """Get information about backup file"""
        try:
            if not os.path.exists(backup_path):
                return {}
            
            stat = os.stat(backup_path)
            
            # Get database info
            conn = sqlite3.connect(backup_path)
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return {
                'file_size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'table_count': len(tables),
                'tables': tables
            }
            
        except Exception as e:
            self.logger.log(f"Failed to get backup info: {str(e)}", "ERROR")
            return {}
    
    def cleanup_old_backups(self, backup_dir: str, keep_count: int = 10) -> int:
        """Clean up old backup files, keeping only the most recent ones"""
        try:
            if not os.path.exists(backup_dir):
                return 0
            
            # Get all backup files
            backup_files = []
            for filename in os.listdir(backup_dir):
                if filename.endswith('.db') and 'backup' in filename:
                    filepath = os.path.join(backup_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    backup_files.append((filepath, mtime))
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Remove old backups
            removed_count = 0
            for filepath, _ in backup_files[keep_count:]:
                try:
                    os.remove(filepath)
                    removed_count += 1
                    self.logger.log(f"Removed old backup: {filepath}")
                except Exception as e:
                    self.logger.log(f"Failed to remove backup {filepath}: {str(e)}", "ERROR")
            
            return removed_count
            
        except Exception as e:
            self.logger.log(f"Backup cleanup failed: {str(e)}", "ERROR")
            return 0