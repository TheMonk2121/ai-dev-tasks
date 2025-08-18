#!/usr/bin/env python3.12.123.11
"""
Global timeout configuration for the DSPy RAG system.

This module provides centralized timeout configuration for:
- Database connection pool timeouts
- HTTP request timeouts
- PDF processing timeouts
- File upload timeouts
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TimeoutConfig:
    """Global timeout configuration"""
    
    # Database timeouts
    db_connect_timeout: int = 10
    db_read_timeout: int = 30
    db_write_timeout: int = 60
    db_pool_timeout: int = 20
    
    # HTTP request timeouts
    http_connect_timeout: int = 10
    http_read_timeout: int = 30
    http_total_timeout: int = 120
    
    # File processing timeouts
    pdf_processing_timeout: int = 300
    file_upload_timeout: int = 600
    chunk_processing_timeout: int = 120
    
    # LLM API timeouts
    llm_request_timeout: int = 120
    llm_stream_timeout: int = 300
    
    # System timeouts
    health_check_timeout: int = 10
    metrics_timeout: int = 5
    startup_timeout: int = 60

def load_timeout_config() -> TimeoutConfig:
    """Load timeout configuration from environment variables and system.json"""
    
    # Default configuration
    config = TimeoutConfig()
    
    # Load from environment variables
    config.db_connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", config.db_connect_timeout))
    config.db_read_timeout = int(os.getenv("DB_READ_TIMEOUT", config.db_read_timeout))
    config.db_write_timeout = int(os.getenv("DB_WRITE_TIMEOUT", config.db_write_timeout))
    config.db_pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", config.db_pool_timeout))
    
    config.http_connect_timeout = int(os.getenv("HTTP_CONNECT_TIMEOUT", config.http_connect_timeout))
    config.http_read_timeout = int(os.getenv("HTTP_READ_TIMEOUT", config.http_read_timeout))
    config.http_total_timeout = int(os.getenv("HTTP_TOTAL_TIMEOUT", config.http_total_timeout))
    
    config.pdf_processing_timeout = int(os.getenv("PDF_PROCESSING_TIMEOUT", config.pdf_processing_timeout))
    config.file_upload_timeout = int(os.getenv("FILE_UPLOAD_TIMEOUT", config.file_upload_timeout))
    config.chunk_processing_timeout = int(os.getenv("CHUNK_PROCESSING_TIMEOUT", config.chunk_processing_timeout))
    
    config.llm_request_timeout = int(os.getenv("LLM_REQUEST_TIMEOUT", config.llm_request_timeout))
    config.llm_stream_timeout = int(os.getenv("LLM_STREAM_TIMEOUT", config.llm_stream_timeout))
    
    config.health_check_timeout = int(os.getenv("HEALTH_CHECK_TIMEOUT", config.health_check_timeout))
    config.metrics_timeout = int(os.getenv("METRICS_TIMEOUT", config.metrics_timeout))
    config.startup_timeout = int(os.getenv("STARTUP_TIMEOUT", config.startup_timeout))
    
    # Try to load from system.json if available
    try:
        import json
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'system.json')
        if os.path.exists(config_path):
            with open(config_path) as f:
                system_config = json.load(f)
                
            # Override with system.json timeouts if present
            if 'timeouts' in system_config:
                timeouts = system_config['timeouts']
                config.db_connect_timeout = timeouts.get('db_connect_timeout', config.db_connect_timeout)
                config.db_read_timeout = timeouts.get('db_read_timeout', config.db_read_timeout)
                config.db_write_timeout = timeouts.get('db_write_timeout', config.db_write_timeout)
                config.db_pool_timeout = timeouts.get('db_pool_timeout', config.db_pool_timeout)
                
                config.http_connect_timeout = timeouts.get('http_connect_timeout', config.http_connect_timeout)
                config.http_read_timeout = timeouts.get('http_read_timeout', config.http_read_timeout)
                config.http_total_timeout = timeouts.get('http_total_timeout', config.http_total_timeout)
                
                config.pdf_processing_timeout = timeouts.get('pdf_processing_timeout', config.pdf_processing_timeout)
                config.file_upload_timeout = timeouts.get('file_upload_timeout', config.file_upload_timeout)
                config.chunk_processing_timeout = timeouts.get('chunk_processing_timeout', config.chunk_processing_timeout)
                
                config.llm_request_timeout = timeouts.get('llm_request_timeout', config.llm_request_timeout)
                config.llm_stream_timeout = timeouts.get('llm_stream_timeout', config.llm_stream_timeout)
                
                config.health_check_timeout = timeouts.get('health_check_timeout', config.health_check_timeout)
                config.metrics_timeout = timeouts.get('metrics_timeout', config.metrics_timeout)
                config.startup_timeout = timeouts.get('startup_timeout', config.startup_timeout)
                
    except Exception as e:
        logger.warning(f"Could not load timeout config from system.json: {e}")
    
    logger.info(f"Loaded timeout configuration: {config}")
    return config

# Global timeout configuration instance
TIMEOUT_CONFIG = load_timeout_config()

def get_timeout_config() -> TimeoutConfig:
    """Get the global timeout configuration"""
    return TIMEOUT_CONFIG

def validate_timeout_config(config: TimeoutConfig) -> bool:
    """Validate timeout configuration values"""
    
    errors = []
    
    # Validate database timeouts
    if config.db_connect_timeout < 1:
        errors.append("DB_CONNECT_TIMEOUT must be >= 1")
    if config.db_read_timeout < 5:
        errors.append("DB_READ_TIMEOUT must be >= 5")
    if config.db_write_timeout < 10:
        errors.append("DB_WRITE_TIMEOUT must be >= 10")
    if config.db_pool_timeout < 5:
        errors.append("DB_POOL_TIMEOUT must be >= 5")
    
    # Validate HTTP timeouts
    if config.http_connect_timeout < 1:
        errors.append("HTTP_CONNECT_TIMEOUT must be >= 1")
    if config.http_read_timeout < 5:
        errors.append("HTTP_READ_TIMEOUT must be >= 5")
    if config.http_total_timeout < config.http_connect_timeout + config.http_read_timeout:
        errors.append("HTTP_TOTAL_TIMEOUT must be >= CONNECT_TIMEOUT + READ_TIMEOUT")
    
    # Validate file processing timeouts
    if config.pdf_processing_timeout < 60:
        errors.append("PDF_PROCESSING_TIMEOUT must be >= 60")
    if config.file_upload_timeout < 120:
        errors.append("FILE_UPLOAD_TIMEOUT must be >= 120")
    if config.chunk_processing_timeout < 30:
        errors.append("CHUNK_PROCESSING_TIMEOUT must be >= 30")
    
    # Validate LLM timeouts
    if config.llm_request_timeout < 30:
        errors.append("LLM_REQUEST_TIMEOUT must be >= 30")
    if config.llm_stream_timeout < config.llm_request_timeout:
        errors.append("LLM_STREAM_TIMEOUT must be >= LLM_REQUEST_TIMEOUT")
    
    # Validate system timeouts
    if config.health_check_timeout < 1:
        errors.append("HEALTH_CHECK_TIMEOUT must be >= 1")
    if config.metrics_timeout < 1:
        errors.append("METRICS_TIMEOUT must be >= 1")
    if config.startup_timeout < 30:
        errors.append("STARTUP_TIMEOUT must be >= 30")
    
    if errors:
        logger.error(f"Timeout configuration validation failed: {errors}")
        return False
    
    logger.info("Timeout configuration validation passed")
    return True

def format_timeout_duration(seconds: int) -> str:
    """Format timeout duration for logging"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m{remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h{remaining_minutes}m" 