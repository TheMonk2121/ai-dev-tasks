#!/usr/bin/env python3
"""
Structured Logging for DSPy RAG System
Provides consistent, structured logging across all components.
"""

import logging
import json
import sys
from datetime import datetime, timezone, UTC
from pathlib import Path
from typing import Dict, Any, Optional
import traceback
import threading

# Sensitive field patterns for redaction
SENSITIVE_PATTERNS = ["password", "token", "secret", "key", "credential", "auth"]

class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging with security and error handling"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with error handling and security"""
        try:
            log_entry: dict[str, Any] = {
                "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            # Add extra fields if present (dynamic, not hardcoded)
            if hasattr(record, '__dict__'):
                for key, value in record.__dict__.items():
                    if key not in log_entry and not key.startswith('_'):
                        # Redact sensitive fields
                        if any(pattern in key.lower() for pattern in SENSITIVE_PATTERNS):
                            log_entry[key] = "***REDACTED***"
                        else:
                            log_entry[key] = value
            
            # Add exception info if present
            if record.exc_info:
                log_entry['exception'] = {
                    'type': record.exc_info[0].__name__,
                    'message': str(record.exc_info[1]),
                    'traceback': traceback.format_exception(*record.exc_info)
                }
            
            return json.dumps(log_entry, default=str, ensure_ascii=False)
            
        except Exception as e:
            # Fallback to plain text if JSON serialization fails
            try:
                return super().format(record)
            except Exception:
                return f"Log formatting failed: {str(e)}"

# Thread-safe logger cache
_logger_cache: dict[str, logging.Logger] = {}
_cache_lock = threading.Lock()

def get_logger(name: str, level: str = "INFO", log_file: str | None = None) -> logging.Logger:
    """
    Thread-safe factory for structured loggers with singleton pattern
    
    Args:
        name: Logger name
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for file logging
        
    Returns:
        Configured logger instance
    """
    with _cache_lock:
        if name in _logger_cache:
            return _logger_cache[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, level.upper()))
        
        # Only configure if not already configured
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(StructuredFormatter())
            logger.addHandler(console_handler)
            
            # File handler (only if log_file is provided)
            if log_file:
                try:
                    from logging.handlers import RotatingFileHandler
                    file_handler = RotatingFileHandler(
                        log_file,
                        maxBytes=50 * 1024 * 1024,  # 50MB
                        backupCount=5
                    )
                    file_handler.setFormatter(StructuredFormatter())
                    logger.addHandler(file_handler)
                except Exception as e:
                    # Log to console if file handler fails
                    logger.warning(f"Failed to create file handler for {log_file}: {e}")
            
            # Prevent propagation to avoid duplicate logs
            logger.propagate = False
        
        _logger_cache[name] = logger
        return logger

def setup_logger(name: str, level: str = "INFO", log_file: str | None = None) -> logging.Logger:
    """
    Legacy function for backward compatibility
    Use get_logger() for new code
    """
    return get_logger(name, level, log_file)

def log_with_context(logger: logging.Logger, message: str, level: str = "INFO", **context):
    """
    Log with additional context fields
    
    Args:
        logger: Logger instance
        message: Log message
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        **context: Additional context fields
    """
    log_method = getattr(logger, level.lower(), logger.info)
    log_method(message, extra=context)

def log_document_processing(logger: logging.Logger, document_id: str, stage: str, 
                          message: str, level: str = "INFO", **context):
    """
    Log document processing events with standard context
    
    Args:
        logger: Logger instance
        document_id: Document identifier
        stage: Processing stage
        message: Log message
        level: Log level
        **context: Additional context
    """
    context.update({
        'document_id': document_id,
        'stage': stage
    })
    log_with_context(logger, message, level=level, **context)

def log_error_with_context(logger: logging.Logger, error: Exception, 
                         message: str = "Error occurred", **context):
    """
    Log errors with full context and traceback
    
    Args:
        logger: Logger instance
        error: Exception to log
        message: Error message
        **context: Additional context
    """
    logger.error(message, exc_info=True, extra=context)

def configure_logging_from_env():
    """Configure logging from environment variables"""
    import os
    
    log_level = os.getenv('LOG_LEVEL', 'INFO')
    log_file = os.getenv('LOG_FILE')
    
    # Set up root logger
    root_logger = get_logger('root', level=log_level, log_file=log_file)
    
    # Configure other common loggers
    get_logger('dspy_rag', level=log_level, log_file=log_file)
    get_logger('document_processor', level=log_level, log_file=log_file)
    get_logger('vector_store', level=log_level, log_file=log_file)
    
    return root_logger 