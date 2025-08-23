"""Session management utilities"""

import json
import os
from typing import Dict, Any, List, Optional
from .logger import Logger

class SessionManager:
    """Manages application session data"""
    
    def __init__(self, session_file: str = "session.json"):
        self.session_file = session_file
        self.logger = Logger()
    
    def save_session(self, session_data: Dict[str, Any]) -> bool:
        """Save session data to file"""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, default=str)
            
            self.logger.log("Session saved")
            return True
            
        except Exception as e:
            self.logger.log(f"Failed to save session: {str(e)}", "ERROR")
            return False
    
    def load_session(self) -> Dict[str, Any]:
        """Load session data from file"""
        try:
            if not os.path.exists(self.session_file):
                return {}
            
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            self.logger.log("Session loaded")
            return session_data
            
        except Exception as e:
            self.logger.log(f"Failed to load session: {str(e)}", "ERROR")
            return {}
    
    def add_recent_database(self, database_path: str, max_recent: int = 10) -> bool:
        """Add database to recent list"""
        try:
            session_data = self.load_session()
            recent_databases = session_data.get('recent_databases', [])
            
            # Remove if already exists
            if database_path in recent_databases:
                recent_databases.remove(database_path)
            
            # Add to beginning
            recent_databases.insert(0, database_path)
            
            # Limit to max_recent
            recent_databases = recent_databases[:max_recent]
            
            session_data['recent_databases'] = recent_databases
            return self.save_session(session_data)
            
        except Exception as e:
            self.logger.log(f"Failed to add recent database: {str(e)}", "ERROR")
            return False
    
    def get_recent_databases(self) -> List[str]:
        """Get list of recent databases"""
        session_data = self.load_session()
        recent = session_data.get('recent_databases', [])
        
        # Filter out non-existent files
        existing_recent = [db for db in recent if os.path.exists(db)]
        
        # Update session if list changed
        if len(existing_recent) != len(recent):
            session_data['recent_databases'] = existing_recent
            self.save_session(session_data)
        
        return existing_recent
    
    def save_window_state(self, geometry: List[int], maximized: bool = False) -> bool:
        """Save window state"""
        try:
            session_data = self.load_session()
            session_data['window_state'] = {
                'geometry': geometry,
                'maximized': maximized
            }
            return self.save_session(session_data)
            
        except Exception as e:
            self.logger.log(f"Failed to save window state: {str(e)}", "ERROR")
            return False
    
    def get_window_state(self) -> Optional[Dict[str, Any]]:
        """Get saved window state"""
        session_data = self.load_session()
        return session_data.get('window_state')
    
    def save_table_settings(self, table_name: str, settings: Dict[str, Any]) -> bool:
        """Save table-specific settings"""
        try:
            session_data = self.load_session()
            table_settings = session_data.get('table_settings', {})
            table_settings[table_name] = settings
            session_data['table_settings'] = table_settings
            return self.save_session(session_data)
            
        except Exception as e:
            self.logger.log(f"Failed to save table settings: {str(e)}", "ERROR")
            return False
    
    def get_table_settings(self, table_name: str) -> Dict[str, Any]:
        """Get table-specific settings"""
        session_data = self.load_session()
        table_settings = session_data.get('table_settings', {})
        return table_settings.get(table_name, {})
    
    def save_query_history(self, queries: List[Dict[str, Any]], max_history: int = 100) -> bool:
        """Save query history"""
        try:
            session_data = self.load_session()
            # Keep only the most recent queries
            session_data['query_history'] = queries[-max_history:]
            return self.save_session(session_data)
            
        except Exception as e:
            self.logger.log(f"Failed to save query history: {str(e)}", "ERROR")
            return False
    
    def get_query_history(self) -> List[Dict[str, Any]]:
        """Get query history"""
        session_data = self.load_session()
        return session_data.get('query_history', [])
    
    def save_preferences(self, preferences: Dict[str, Any]) -> bool:
        """Save user preferences"""
        try:
            session_data = self.load_session()
            session_data['preferences'] = preferences
            return self.save_session(session_data)
            
        except Exception as e:
            self.logger.log(f"Failed to save preferences: {str(e)}", "ERROR")
            return False
    
    def get_preferences(self) -> Dict[str, Any]:
        """Get user preferences"""
        session_data = self.load_session()
        return session_data.get('preferences', {
            'theme': 'light',
            'auto_backup': True,
            'backup_interval': 30,  # minutes
            'max_recent_files': 10,
            'default_page_size': 100,
            'confirm_deletes': True
        })
    
    def clear_session(self) -> bool:
        """Clear all session data"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
            self.logger.log("Session cleared")
            return True
            
        except Exception as e:
            self.logger.log(f"Failed to clear session: {str(e)}", "ERROR")
            return False