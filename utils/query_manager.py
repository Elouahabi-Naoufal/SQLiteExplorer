"""Query history and favorites management"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class QueryManager:
    """Manages SQL query history and favorites"""
    
    def __init__(self, data_dir: str = "."):
        self.data_dir = data_dir
        self.history_file = os.path.join(data_dir, "query_history.json")
        self.favorites_file = os.path.join(data_dir, "query_favorites.json")
        self.max_history = 100
        
    def add_to_history(self, query: str, execution_time: float = 0, result_count: int = 0):
        """Add query to history"""
        history = self.get_history()
        
        entry = {
            'query': query.strip(),
            'timestamp': datetime.now().isoformat(),
            'execution_time': execution_time,
            'result_count': result_count
        }
        
        # Remove duplicate if exists
        history = [h for h in history if h['query'] != query.strip()]
        
        # Add to beginning
        history.insert(0, entry)
        
        # Limit history size
        if len(history) > self.max_history:
            history = history[:self.max_history]
            
        self._save_history(history)
        
    def get_history(self) -> List[Dict[str, Any]]:
        """Get query history"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
        
    def clear_history(self):
        """Clear query history"""
        if os.path.exists(self.history_file):
            os.remove(self.history_file)
            
    def add_favorite(self, name: str, query: str, description: str = ""):
        """Add query to favorites"""
        favorites = self.get_favorites()
        
        favorite = {
            'name': name,
            'query': query.strip(),
            'description': description,
            'created': datetime.now().isoformat()
        }
        
        # Remove existing favorite with same name
        favorites = [f for f in favorites if f['name'] != name]
        favorites.append(favorite)
        
        self._save_favorites(favorites)
        
    def get_favorites(self) -> List[Dict[str, Any]]:
        """Get favorite queries"""
        try:
            if os.path.exists(self.favorites_file):
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
        
    def remove_favorite(self, name: str):
        """Remove favorite query"""
        favorites = self.get_favorites()
        favorites = [f for f in favorites if f['name'] != name]
        self._save_favorites(favorites)
        
    def _save_history(self, history: List[Dict[str, Any]]):
        """Save history to file"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2)
        except Exception:
            pass
            
    def _save_favorites(self, favorites: List[Dict[str, Any]]):
        """Save favorites to file"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(favorites, f, indent=2)
        except Exception:
            pass