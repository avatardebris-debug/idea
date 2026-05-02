"""Logging configuration for the Fiverr Job Automation Tool."""

import logging
import os
import sys
from typing import Optional
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config


def setup_logger(
    name: Optional[str] = None,
    log_file: Optional[str] = None,
    log_level: Optional[str] = None,
    log_format: Optional[str] = None
) -> logging.Logger:
    """Set up logging with file and console handlers.
    
    Args:
        name: Logger name. If None, uses the root logger.
        log_file: Path to log file. If None, uses default from config.
        log_level: Logging level. If None, uses default from config.
        log_format: Log format string. If None, uses default format.
        
    Returns:
        Configured logger instance.
    """
    # Get configuration values
    log_file = log_file or Config.LOG_FILE
    log_level = log_level or Config.LOG_LEVEL
    log_format = log_format or Config.LOG_FORMAT
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # File handler
    try:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (IOError, OSError) as e:
        print(f"Warning: Could not create log file {log_file}: {e}")
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and above on console
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.
    
    Args:
        name: Name of the logger (typically __name__).
        
    Returns:
        Configured logger instance.
    """
    return setup_logger(name=name)
