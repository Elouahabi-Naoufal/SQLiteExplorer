"""Logging utilities"""

import os
import logging
from datetime import datetime
from typing import Optional

class Logger:
    """Application logger"""
    
    def __init__(self, log_file: Optional[str] = None):
        if log_file:
            self.log_file = log_file
        else:
            # Use user's home directory for logs when in AppImage
            home_dir = os.path.expanduser("~")
            self.log_file = os.path.join(home_dir, "sqlite_manager.log")
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with specified level"""
        if level.upper() == "DEBUG":
            self.logger.debug(message)
        elif level.upper() == "INFO":
            self.logger.info(message)
        elif level.upper() == "WARNING":
            self.logger.warning(message)
        elif level.upper() == "ERROR":
            self.logger.error(message)
        elif level.upper() == "CRITICAL":
            self.logger.critical(message)
    
    def get_timestamp(self) -> str:
        """Get current timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def clear_log(self):
        """Clear log file"""
        try:
            if os.path.exists(self.log_file):
                os.remove(self.log_file)
            self.setup_logging()
        except Exception as e:
            self.logger.error(f"Failed to clear log: {str(e)}")
    
    def get_log_contents(self) -> str:
        """Get log file contents"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    return f.read()
            return ""
        except Exception as e:
            return f"Error reading log: {str(e)}"