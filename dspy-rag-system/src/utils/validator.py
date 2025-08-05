#!/usr/bin/env python3
"""
Input validation utilities for DSPy RAG system.
Implements security hardening for user inputs and file paths.
"""

import re
import os
import logging
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Raised when security validation fails"""
    pass

class ValidationError(Exception):
    """Raised when input validation fails"""
    pass

def sanitize_prompt(prompt: str, blocklist: Optional[List[str]] = None) -> str:
    """
    Sanitize user prompt to prevent injection attacks.
    
    Args:
        prompt: User input prompt
        blocklist: List of blocked patterns (defaults to common injection patterns)
    
    Returns:
        Sanitized prompt string
    
    Raises:
        SecurityError: If blocked pattern is detected
    """
    if blocklist is None:
        blocklist = [
            "<script>", "javascript:", "eval(", "exec(",
            "import ", "from ", "__import__", "globals()",
            "locals()", "vars()", "dir()", "type(",
            "open(", "file(", "read(", "write(",
            "subprocess", "os.system", "eval("
        ]
    
    prompt_lower = prompt.lower()
    
    for pattern in blocklist:
        if pattern in prompt_lower:
            logger.warning(f"Blocked pattern detected in prompt: {pattern}")
            raise SecurityError(f"Blocked pattern detected: {pattern}")
    
    # Additional sanitization
    prompt = prompt.strip()
    
    # Remove null bytes
    prompt = prompt.replace('\x00', '')
    
    # Limit length
    if len(prompt) > 10000:
        raise ValidationError("Prompt too long (max 10000 characters)")
    
    return prompt

def validate_file_path(file_path: str, allowed_extensions: Optional[List[str]] = None) -> bool:
    """
    Validate file path to prevent path traversal attacks.
    
    Args:
        file_path: File path to validate
        allowed_extensions: List of allowed file extensions
    
    Returns:
        True if path is valid
    
    Raises:
        SecurityError: If path traversal or invalid extension detected
    """
    if allowed_extensions is None:
        allowed_extensions = [".txt", ".md", ".pdf", ".csv"]
    
    # Convert to Path object for better handling
    path = Path(file_path)
    
    # Check for path traversal attempts
    if ".." in str(path):
        logger.warning(f"Path traversal attempt detected: {file_path}")
        raise SecurityError("Path traversal not allowed")
    
    # Check for absolute paths (if not allowed)
    if path.is_absolute():
        logger.warning(f"Absolute path not allowed: {file_path}")
        raise SecurityError("Absolute paths not allowed")
    
    # Check file extension
    if path.suffix.lower() not in allowed_extensions:
        logger.warning(f"Invalid file extension: {path.suffix}")
        raise SecurityError(f"Invalid file extension: {path.suffix}")
    
    # Check for suspicious characters
    suspicious_chars = ["<", ">", "|", "&", ";", "`", "$", "(", ")", "{", "}"]
    if any(char in str(path) for char in suspicious_chars):
        logger.warning(f"Suspicious characters in path: {file_path}")
        raise SecurityError("Suspicious characters in file path")
    
    return True

def validate_file_size(file_path: str, max_size_mb: int = 50) -> bool:
    """
    Validate file size to prevent memory issues.
    
    Args:
        file_path: Path to file to check
        max_size_mb: Maximum file size in MB
    
    Returns:
        True if file size is acceptable
    
    Raises:
        ValidationError: If file is too large
    """
    if not os.path.exists(file_path):
        raise ValidationError(f"File does not exist: {file_path}")
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    
    if file_size_mb > max_size_mb:
        logger.warning(f"File too large: {file_size_mb:.2f}MB > {max_size_mb}MB")
        raise ValidationError(f"File too large: {file_size_mb:.2f}MB (max {max_size_mb}MB)")
    
    return True

def validate_secrets(required_secrets: List[str]) -> None:
    """
    Validate that all required secrets are present.
    
    Args:
        required_secrets: List of required secret environment variables
    
    Raises:
        ValidationError: If any required secret is missing
    """
    missing_secrets = []
    
    for secret in required_secrets:
        if not os.getenv(secret):
            missing_secrets.append(secret)
    
    if missing_secrets:
        logger.error(f"Missing required secrets: {missing_secrets}")
        raise ValidationError(f"Missing required secrets: {missing_secrets}")

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent security issues.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    # Remove or replace dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    sanitized = filename
    
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')
    
    # Limit length
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    
    return sanitized

def validate_query_complexity(query: str, max_tokens: int = 1000) -> bool:
    """
    Validate query complexity to prevent resource exhaustion.
    
    Args:
        query: User query to validate
        max_tokens: Maximum number of tokens allowed
    
    Returns:
        True if query complexity is acceptable
    
    Raises:
        ValidationError: If query is too complex
    """
    # Simple token estimation (rough count)
    estimated_tokens = len(query.split()) * 1.3  # Rough approximation
    
    if estimated_tokens > max_tokens:
        logger.warning(f"Query too complex: ~{estimated_tokens:.0f} tokens > {max_tokens}")
        raise ValidationError(f"Query too complex: ~{estimated_tokens:.0f} tokens (max {max_tokens})")
    
    return True 