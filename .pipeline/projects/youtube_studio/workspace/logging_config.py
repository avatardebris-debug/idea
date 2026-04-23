"""Logging system for YouTube Studio.

This module provides a centralized logging infrastructure with support
for multiple output formats, log levels, and file rotation.
"""

import logging
import sys
from typing import Optional, Dict, Any
from logging.handlers import RotatingFileHandler
from pathlib import Path


class YouTubeStudioLogger:
    """Centralized logger for YouTube Studio.
    
    This class provides a consistent logging interface with support for:
    - Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Console and file output
    - JSON formatting for structured logging
    - Rotating file handlers
    """
    
    _instance: Optional['YouTubeStudioLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls) -> 'YouTubeStudioLogger':
        """Singleton pattern to ensure single logger instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._logger = logging.getLogger('youtube_studio')
            cls._logger.setLevel(logging.DEBUG)
        return cls._instance
    
    def setup(
        self,
        log_level: str = 'INFO',
        log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        log_file: Optional[str] = None,
        max_bytes: int = 10_485_760,  # 10MB
        backup_count: int = 5,
        json_format: bool = False
    ) -> None:
        """Configure the logger.
        
        Args:
            log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_format: Log format string
            log_file: Path to log file (None for console only)
            max_bytes: Maximum size for log file rotation
            backup_count: Number of backup files to keep
            json_format: Use JSON format for structured logging
        """
        if self._logger is None:
            self._logger = logging.getLogger('youtube_studio')
        
        # Clear existing handlers
        self._logger.handlers.clear()
        
        # Set log level
        level = getattr(logging, log_level.upper(), logging.INFO)
        self._logger.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        if json_format:
            console_handler.setFormatter(JsonFormatter())
        else:
            console_handler.setFormatter(logging.Formatter(log_format))
        
        self._logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count
            )
            file_handler.setLevel(level)
            
            if json_format:
                file_handler.setFormatter(JsonFormatter())
            else:
                file_handler.setFormatter(logging.Formatter(log_format))
            
            self._logger.addHandler(file_handler)
    
    def get_logger(self) -> logging.Logger:
        """Get the logger instance."""
        if self._logger is None:
            self._logger = logging.getLogger('youtube_studio')
        return self._logger
    
    def debug(self, msg: str, **kwargs) -> None:
        """Log a debug message."""
        self._log('debug', msg, **kwargs)
    
    def info(self, msg: str, **kwargs) -> None:
        """Log an info message."""
        self._log('info', msg, **kwargs)
    
    def warning(self, msg: str, **kwargs) -> None:
        """Log a warning message."""
        self._log('warning', msg, **kwargs)
    
    def error(self, msg: str, **kwargs) -> None:
        """Log an error message."""
        self._log('error', msg, **kwargs)
    
    def critical(self, msg: str, **kwargs) -> None:
        """Log a critical message."""
        self._log('critical', msg, **kwargs)
    
    def _log(self, level: str, msg: str, **kwargs) -> None:
        """Log a message with additional context."""
        logger = self.get_logger()
        log_method = getattr(logger, level)
        
        if kwargs:
            context = ', '.join(f'{k}={v}' for k, v in kwargs.items())
            log_method(f'{msg} [{context}]')
        else:
            log_method(msg)


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        import json
        return json.dumps(log_data)


# Global logger instance
logger = YouTubeStudioLogger()


def get_logger() -> logging.Logger:
    """Get the global logger instance."""
    return logger.get_logger()


def setup_logger(
    log_level: str = 'INFO',
    log_format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    log_file: Optional[str] = None,
    max_bytes: int = 10_485_760,
    backup_count: int = 5,
    json_format: bool = False
) -> None:
    """Setup the logger with specified configuration.
    
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format string
        log_file: Path to log file (None for console only)
        max_bytes: Maximum size for log file rotation
        backup_count: Number of backup files to keep
        json_format: Use JSON format for structured logging
    """
    logger.setup(
        log_level=log_level,
        log_format=log_format,
        log_file=log_file,
        max_bytes=max_bytes,
        backup_count=backup_count,
        json_format=json_format
    )


if __name__ == '__main__':
    # Test logging
    setup_logger(log_level='DEBUG', log_file='test.log')
    
    log = get_logger()
    
    log.debug('This is a debug message')
    log.info('This is an info message')
    log.warning('This is a warning message')
    log.error('This is an error message')
    log.critical('This is a critical message')
    
    # Test with context
    log.info('Processing video', title='Python Tutorial', duration=300)
    
    print('Logging test completed successfully')
