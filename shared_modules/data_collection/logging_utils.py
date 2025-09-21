# logging_utils.py - Centralized logging configuration with Unicode support
import os
import sys
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
import codecs

def setup_logging():
    """Setup logging configuration with file and console handlers with Unicode support"""
    # Create Logs directory if it doesn't exist
    logs_dir = "Logs"
    os.makedirs(logs_dir, exist_ok=True)
    
    # Generate log filename with current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    full_log_file = os.path.join(logs_dir, f"trade_bot_{current_date}.log")
    error_log_file = os.path.join(logs_dir, f"trade_bot_errors_{current_date}.log")
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Full log file handler (DEBUG and above)
    full_file_handler = RotatingFileHandler(
        full_log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    full_file_handler.setLevel(logging.DEBUG)
    full_file_handler.setFormatter(formatter)
    logger.addHandler(full_file_handler)
    
    # Error log file handler (WARNING and above)
    error_file_handler = RotatingFileHandler(
        error_log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.WARNING)
    error_file_handler.setFormatter(formatter)
    logger.addHandler(error_file_handler)
    
    # Console handler with Unicode support
    if sys.platform == 'win32':
        # On Windows, try to use UTF-8 encoding
        try:
            # For Windows 10 and later, try to set console to UTF-8
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except:
            # Fallback to replacing problematic characters
            class UnicodeSafeStream:
                def __init__(self, stream):
                    self.stream = stream
                
                def write(self, msg):
                    # Replace emojis and other problematic Unicode characters
                    msg = msg.replace('✅', '[OK]')
                    msg = msg.replace('❌', '[FAIL]')
                    msg = msg.replace('📊', '[DATA]')
                    msg = msg.replace('🔄', '[PROCESS]')
                    msg = msg.replace('⏳', '[WAIT]')
                    msg = msg.replace('📡', '[WS]')
                    msg = msg.replace('💾', '[SAVE]')
                    msg = msg.replace('🔌', '[CONNECT]')
                    msg = msg.replace('📋', '[INFO]')
                    msg = msg.replace('🔍', '[DEBUG]')
                    msg = msg.replace('💓', '[HEARTBEAT]')
                    self.stream.write(msg)
                
                def flush(self):
                    self.stream.flush()
                
                def close(self):
                    self.stream.close()
            
            console_handler = logging.StreamHandler(UnicodeSafeStream(sys.stdout))
        else:
            console_handler = logging.StreamHandler(sys.stdout)
    else:
        # On other platforms, use standard console handler
        console_handler = logging.StreamHandler(sys.stdout)
    
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    logger.info("Logging system initialized")
    return logger