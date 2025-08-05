#!/usr/bin/env python3
"""
Retry wrapper utility for DSPy RAG system.
Implements configurable retry logic with exponential backoff.
"""

import time
import functools
import logging
from typing import Callable, Any, Dict, Optional
from requests.exceptions import Timeout, RequestException
import psycopg2

logger = logging.getLogger(__name__)

class RetryableError(Exception):
    """Base class for errors that should trigger retries"""
    pass

class FatalError(Exception):
    """Base class for errors that should not trigger retries"""
    pass

class TimeoutError(RetryableError):
    """Request timeout error"""
    pass

class DataStoreError(FatalError):
    """Database connection or operation error"""
    pass

def load_error_policy() -> Dict[str, Any]:
    """Load error policy from system configuration"""
    # TODO: Load from config/system.json
    return {
        "max_retries": 3,
        "backoff_factor": 2.0,
        "timeout_seconds": 30,
        "fatal_errors": ["DataStoreError", "AuthenticationError"]
    }

def retry(
    max_retries: Optional[int] = None,
    backoff_factor: Optional[float] = None,
    timeout_seconds: Optional[int] = None,
    fatal_errors: Optional[list] = None
):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
        timeout_seconds: Timeout for each attempt
        fatal_errors: List of error types that should not trigger retries
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Load default policy if not specified
            policy = load_error_policy()
            max_retries_actual = max_retries or policy["max_retries"]
            backoff_factor_actual = backoff_factor or policy["backoff_factor"]
            timeout_actual = timeout_seconds or policy["timeout_seconds"]
            fatal_errors_actual = fatal_errors or policy["fatal_errors"]
            
            last_exception = None
            
            for attempt in range(max_retries_actual + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    # Check if this is a fatal error
                    if any(fatal_error in str(type(e)) for fatal_error in fatal_errors_actual):
                        logger.error(f"Fatal error encountered: {e}")
                        raise e
                    
                    # Check if we should retry
                    if attempt < max_retries_actual:
                        wait_time = backoff_factor_actual ** attempt
                        logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries_actual} retry attempts failed. Last error: {e}")
                        raise last_exception
            
            return None  # Should never reach here
        
        return wrapper
    return decorator

# Convenience functions for common retry scenarios
def retry_http(func: Callable) -> Callable:
    """Retry decorator for HTTP requests"""
    return retry(
        max_retries=3,
        backoff_factor=2.0,
        timeout_seconds=30,
        fatal_errors=["AuthenticationError", "DataStoreError"]
    )(func)

def retry_database(func: Callable) -> Callable:
    """Retry decorator for database operations"""
    return retry(
        max_retries=3,
        backoff_factor=1.5,
        timeout_seconds=60,
        fatal_errors=["DataStoreError", "ConfigurationError"]
    )(func)

def retry_llm(func: Callable) -> Callable:
    """Retry decorator for LLM API calls"""
    return retry(
        max_retries=2,
        backoff_factor=2.0,
        timeout_seconds=120,
        fatal_errors=["AuthenticationError", "ResourceBusyError"]
    )(func) 