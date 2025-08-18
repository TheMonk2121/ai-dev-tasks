#!/usr/bin/env python3.12.123.11
"""
Retry wrapper utility for DSPy RAG system.
Implements configurable retry logic with exponential backoff.
"""

import time
import functools
import logging
import json
import os
from typing import Any, Optional
from collections.abc import Callable
from requests.exceptions import Timeout, RequestException
import psycopg2

# Import error pattern recognition
try:
    from .error_pattern_recognition import analyze_error_pattern, suggest_recovery_strategy
    from .hotfix_templates import generate_hotfix_template
    from .model_specific_handling import handle_model_error
    ERROR_PATTERN_ANALYSIS_AVAILABLE = True
except ImportError:
    ERROR_PATTERN_ANALYSIS_AVAILABLE = False

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

class AuthenticationError(FatalError):
    """Authentication or authorization error"""
    pass

class ResourceBusyError(FatalError):
    """Resource is busy or unavailable"""
    pass

class ConfigurationError(FatalError):
    """Configuration or setup error"""
    pass

def load_error_policy() -> dict[str, Any]:
    """Load error policy from system configuration"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'config', 'system.json')
        with open(config_path) as f:
            config = json.load(f)
        
        error_policy = config.get("error_policy", {})
        
        # Set defaults if not present
        return {
            "max_retries": error_policy.get("max_retries", 3),
            "backoff_factor": error_policy.get("backoff_factor", 2.0),
            "timeout_seconds": error_policy.get("timeout_seconds", 30),
            "llm_timeout_seconds": error_policy.get("llm_timeout_seconds", 90),
            "fatal_errors": error_policy.get("fatal_errors", ["ResourceBusyError", "AuthenticationError"])
        }
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Could not load error policy from config: {e}. Using defaults.")
        return {
            "max_retries": 3,
            "backoff_factor": 2.0,
            "timeout_seconds": 30,
            "llm_timeout_seconds": 90,
            "fatal_errors": ["ResourceBusyError", "AuthenticationError"]
        }

def get_llm_timeout(model_id: str = None) -> int:
    """Get LLM-specific timeout based on model type"""
    policy = load_error_policy()
    
    # Check environment variable override
    env_timeout = os.getenv('LLM_TIMEOUT_SEC')
    if env_timeout:
        try:
            return int(env_timeout)
        except ValueError:
            logger.warning(f"Invalid LLM_TIMEOUT_SEC value: {env_timeout}")
    
    # Use model-specific timeout for large models
    if model_id and model_id.startswith('mixtral'):
        return policy.get("llm_timeout_seconds", 90)
    
    # Default timeout for other models
    return policy.get("timeout_seconds", 30)

def is_fatal_error(exception: Exception, fatal_errors: list[str]) -> bool:
    """Check if an exception is a fatal error that should not trigger retries"""
    exception_type = type(exception).__name__
    exception_str = str(type(exception))
    
    # Check exact type name match
    if exception_type in fatal_errors:
        return True
    
    # Check if any fatal error string is in the exception type string
    for fatal_error in fatal_errors:
        if fatal_error in exception_str:
            return True
    
    # Check for specific exception types
    fatal_exception_types = [
        AuthenticationError,
        DataStoreError,
        ResourceBusyError,
        ConfigurationError
    ]
    
    return any(isinstance(exception, fatal_type) for fatal_type in fatal_exception_types)

def retry(
    max_retries: int | None = None,
    backoff_factor: float | None = None,
    timeout_seconds: int | None = None,
    fatal_errors: list[str] | None = None,
    jitter: bool = True
):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        backoff_factor: Exponential backoff multiplier
        timeout_seconds: Timeout for each attempt
        fatal_errors: List of error types that should not trigger retries
        jitter: Add random jitter to prevent thundering herd
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
                    
                    # Analyze error pattern if available
                    if ERROR_PATTERN_ANALYSIS_AVAILABLE:
                        try:
                            # Extract context from function and arguments
                            context = {
                                'function_name': func.__name__,
                                'attempt': attempt + 1,
                                'model_id': kwargs.get('model_id') or kwargs.get('model')
                            }
                            
                            analysis = analyze_error_pattern(str(e), type(e).__name__, context)
                            
                            if analysis.matched_patterns:
                                logger.info(f"Error pattern analysis: {len(analysis.matched_patterns)} patterns matched, "
                                           f"severity: {analysis.severity_score:.2f}")
                                
                                # Log recovery suggestions
                                recovery_strategies = suggest_recovery_strategy(analysis)
                                if recovery_strategies:
                                    logger.info(f"Recovery suggestions: {', '.join(recovery_strategies[:3])}")
                                
                                # Apply model-specific handling if available
                                if analysis.model_specific_handling:
                                    logger.info(f"Applying model-specific handling: {analysis.model_specific_handling}")
                                
                                # Generate HotFix template if available
                                try:
                                    hotfix_template = generate_hotfix_template(analysis, context)
                                    if hotfix_template:
                                        logger.info(f"Generated HotFix template: {hotfix_template.name}")
                                        logger.info(f"Template category: {hotfix_template.category}")
                                        logger.info(f"Estimated time: {hotfix_template.estimated_time}")
                                except Exception as hotfix_error:
                                    logger.warning(f"HotFix template generation failed: {hotfix_error}")
                                
                                # Apply model-specific handling if model_id is available
                                try:
                                    model_id = context.get('model_id') if context else None
                                    if model_id:
                                        model_response = handle_model_error(str(e), model_id, context)
                                        logger.info(f"Model-specific recovery: {model_response.recovery_action}")
                                        if model_response.fallback_model:
                                            logger.info(f"Suggested fallback: {model_response.fallback_model}")
                                        logger.info(f"Recovery confidence: {model_response.confidence:.2f}")
                                        logger.info(f"Estimated time: {model_response.estimated_time}")
                                except Exception as model_error:
                                    logger.warning(f"Model-specific handling failed: {model_error}")
                                    
                        except Exception as analysis_error:
                            logger.warning(f"Error pattern analysis failed: {analysis_error}")
                    
                    # Check if this is a fatal error
                    if is_fatal_error(e, fatal_errors_actual):
                        logger.error(f"Fatal error encountered: {type(e).__name__}: {e}")
                        raise e
                    
                    # Check if we should retry
                    if attempt < max_retries_actual:
                        wait_time = backoff_factor_actual ** attempt
                        
                        # Add jitter to prevent thundering herd
                        if jitter:
                            import random
                            jitter_amount = random.uniform(0, 0.1 * wait_time)
                            wait_time += jitter_amount
                        
                        logger.warning(f"Attempt {attempt + 1} failed: {type(e).__name__}: {e}. Retrying in {wait_time:.2f}s...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {max_retries_actual} retry attempts failed. Last error: {type(e).__name__}: {e}")
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
    """Retry decorator for LLM API calls with model-specific timeouts"""
    def decorator_with_model_timeout(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract model_id from kwargs or first argument
            model_id = kwargs.get('model_id') or kwargs.get('model')
            if not model_id and args:
                # Check if first arg is a string that might be model_id
                if isinstance(args[0], str) and ('mistral' in args[0].lower() or 'mixtral' in args[0].lower() or 'yi-coder' in args[0].lower()):
                    model_id = args[0]
            
            # Get model-specific timeout
            timeout = get_llm_timeout(model_id)
            
            # Use the retry decorator with model-specific timeout
            return retry(
                max_retries=2,
                backoff_factor=2.0,
                timeout_seconds=timeout,
                fatal_errors=["AuthenticationError", "ResourceBusyError"]
            )(func)(*args, **kwargs)
        
        return wrapper
    return decorator_with_model_timeout(func)

def retry_with_timeout(timeout_seconds: int = 30):
    """Retry decorator with specific timeout"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Function timed out after {timeout_seconds} seconds")
            
            # Set up timeout
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout_seconds)
            
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel timeout
                return result
            except TimeoutError:
                signal.alarm(0)
                raise
            finally:
                signal.signal(signal.SIGALRM, old_handler)
        
        return wrapper
    return decorator

# Utility functions for error handling
def handle_retryable_errors(func: Callable, *args, **kwargs) -> Any:
    """Execute function with retry logic for retryable errors"""
    try:
        return func(*args, **kwargs)
    except (Timeout, RequestException, psycopg2.OperationalError) as e:
        logger.warning(f"Retryable error encountered: {e}")
        raise RetryableError(f"Retryable error: {e}") from e
    except Exception as e:
        logger.error(f"Non-retryable error encountered: {e}")
        raise

def get_retry_stats() -> dict[str, Any]:
    """Get retry statistics for monitoring"""
    # This would be implemented with a metrics collector
    return {
        "total_retries": 0,
        "successful_retries": 0,
        "failed_retries": 0,
        "fatal_errors": 0
    } 