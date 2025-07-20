# modules/utils/logging_setup.py
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_enhanced_logging():
    """Setup enhanced logging dengan file rotation dan Unicode support"""
    # Tentukan direktori log
    if getattr(sys, 'frozen', False):
        base_dir = Path(sys.executable).parent
    else:
        base_dir = Path(__file__).parent.parent.parent
    
    log_dir = base_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Format log
    log_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.INFO)
    
    # Set encoding untuk console
    if hasattr(console_handler.stream, 'reconfigure'):
        try:
            console_handler.stream.reconfigure(encoding='utf-8')
        except:
            pass
    
    # File handlers
    try:
        file_handler = RotatingFileHandler(
            log_dir / "bot.log", 
            maxBytes=10*1024*1024,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(logging.DEBUG)
        
        error_handler = RotatingFileHandler(
            log_dir / "bot_errors.log", 
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setFormatter(log_formatter)
        error_handler.setLevel(logging.ERROR)
        
        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(error_handler)
        
    except ImportError:
        # Fallback
        file_handler = logging.FileHandler(log_dir / "bot.log", encoding='utf-8')
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(logging.DEBUG)
        
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
    
    return root_logger