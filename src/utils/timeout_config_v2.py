#!/usr/bin/env python3
"""
Modern timeout configuration using pydantic-settings.

This is a migration example showing how to replace the old timeout_config.py
with the new pydantic-settings approach.
"""

import logging
from typing import Any

from src.config import get_settings

logger = logging.getLogger(__name__)


def get_timeout_config() -> dict[str, Any]:
    """
    Get timeout configuration from the centralized settings.

    This function provides a compatibility layer for existing code
    that expects the old timeout_config interface.

    Returns:
        Dictionary with timeout configuration values
    """
    settings = get_settings()
    perf = settings.performance
    db = settings.db

    return {
        # Database timeouts (from Database model)
        "db_connect_timeout": db.connect_timeout,
        "db_read_timeout": db.read_timeout,
        "db_write_timeout": db.write_timeout,
        "db_pool_timeout": db.pool_timeout,
        # HTTP request timeouts (from Performance model)
        "http_connect_timeout": perf.http_connect_timeout,
        "http_read_timeout": perf.http_read_timeout,
        "http_total_timeout": perf.http_total_timeout,
        # File processing timeouts (from Performance model)
        "pdf_processing_timeout": perf.pdf_processing_timeout,
        "file_upload_timeout": perf.file_upload_timeout,
        "chunk_processing_timeout": perf.chunk_processing_timeout,
        # LLM API timeouts (from Performance model)
        "llm_request_timeout": perf.llm_request_timeout,
        "llm_stream_timeout": perf.llm_stream_timeout,
        # System timeouts (from Performance model)
        "health_check_timeout": perf.health_check_timeout,
        "metrics_timeout": perf.metrics_timeout,
        "startup_timeout": perf.startup_timeout,
    }


def validate_timeout_config() -> bool:
    """
    Validate timeout configuration values.

    This function provides a compatibility layer for existing code
    that expects the old validation interface.

    Returns:
        True if configuration is valid, False otherwise
    """
    try:
        settings = get_settings()
        # Pydantic validation already ensures values are within bounds
        # This is just for compatibility
        logger.info("Timeout configuration validation passed")
        return True
    except Exception as e:
        logger.error(f"Timeout configuration validation failed: {e}")
        return False


def format_timeout_duration(seconds: int) -> str:
    """Format timeout duration for logging."""
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


# Backward compatibility: provide the old interface
def load_timeout_config():
    """Backward compatibility function."""
    return get_timeout_config()


# Global timeout configuration instance for backward compatibility
TIMEOUT_CONFIG = get_timeout_config()
