#!/usr/bin/env python3
"""
Input validation utilities for DSPy RAG system.
Implements security hardening for user inputs and file paths.
"""

import logging
import os
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Raised when security validation fails"""

    pass


class ValidationError(Exception):
    """Raised when input validation fails"""

    pass


def sanitize_prompt(prompt: str, model_id: str | None = None) -> str:
    """
    Sanitize user prompt to prevent injection attacks using regex-based validation.

    Args:
        prompt: User input prompt
        model_id: Optional model ID for model-specific validation

    Returns:
        Sanitized prompt string

    Raises:
        SecurityError: If blocked pattern is detected
    """
    # Import the new prompt sanitizer
    from .prompt_sanitizer import sanitize_prompt as new_sanitize_prompt

    try:
        return new_sanitize_prompt(prompt, model_id)
    except ImportError:
        # Fallback to old implementation if new sanitizer not available
        logger.warning("New prompt sanitizer not available, using fallback")
        return _fallback_sanitize_prompt(prompt)


def _fallback_sanitize_prompt(prompt: str) -> str:
    """Fallback sanitization using old block-list approach"""
    blocklist = [
        "<script>",
        "javascript:",
        "eval(",
        "exec(",
        "import ",
        "from ",
        "__import__",
        "globals()",
        "locals()",
        "vars()",
        "dir()",
        "type(",
        "open(",
        "file(",
        "read(",
        "write(",
        "subprocess",
        "os.system",
        "eval(",
    ]

    prompt_lower = prompt.lower()

    for pattern in blocklist:
        if pattern in prompt_lower:
            logger.warning(f"Blocked pattern detected in prompt: {pattern}")
            raise SecurityError(f"Blocked pattern detected: {pattern}")

    # Additional sanitization
    prompt = prompt.strip()

    # Remove null bytes
    prompt = prompt.replace("\x00", "")

    # Limit length
    if len(prompt) > 10000:
        raise ValidationError("Prompt too long (max 10000 characters)")

    return prompt


def validate_file_path(file_path: str, allowed_extensions: list[str] | None = None) -> bool:
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


def validate_secrets(required_secrets: list[str]) -> None:
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
    dangerous_chars = ["<", ">", ":", '"', "/", "\\", "|", "?", "*"]
    sanitized = filename

    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "_")

    # Remove null bytes
    sanitized = sanitized.replace("\x00", "")

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


def validate_url(url: str, allowed_domains: list[str] | None = None) -> bool:
    """
    Validate URL to prevent SSRF attacks.

    Args:
        url: URL to validate
        allowed_domains: List of allowed domains (defaults to localhost)

    Returns:
        True if URL is valid

    Raises:
        SecurityError: If URL is not allowed
    """
    if allowed_domains is None:
        allowed_domains = ["localhost", "127.0.0.1"]

    # Basic URL validation
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )

    if not url_pattern.match(url):
        logger.warning(f"Invalid URL format: {url}")
        raise SecurityError("Invalid URL format")

    # Extract domain
    domain_match = re.search(r"https?://([^:/]+)", url, re.IGNORECASE)
    if not domain_match:
        raise SecurityError("Could not extract domain from URL")

    domain = domain_match.group(1).lower()

    # Check if domain is allowed
    if not any(allowed_domain in domain for allowed_domain in allowed_domains):
        logger.warning(f"Domain not allowed: {domain}")
        raise SecurityError(f"Domain not allowed: {domain}")

    return True


def validate_json_structure(data: dict, required_fields: list[str], optional_fields: list[str] | None = None) -> bool:
    """
    Validate JSON structure to ensure required fields are present.

    Args:
        data: JSON data to validate
        required_fields: List of required field names
        optional_fields: List of optional field names

    Returns:
        True if structure is valid

    Raises:
        ValidationError: If required fields are missing
    """
    if not isinstance(data, dict):
        raise ValidationError("Data must be a dictionary")

    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)

    if missing_fields:
        logger.warning(f"Missing required fields: {missing_fields}")
        raise ValidationError(f"Missing required fields: {missing_fields}")

    return True


def validate_string_length(text: str, min_length: int = 1, max_length: int = 10000) -> bool:
    """
    Validate string length to prevent buffer overflow.

    Args:
        text: Text to validate
        min_length: Minimum allowed length
        max_length: Maximum allowed length

    Returns:
        True if length is acceptable

    Raises:
        ValidationError: If length is outside bounds
    """
    if len(text) < min_length:
        raise ValidationError(f"Text too short: {len(text)} chars (min {min_length})")

    if len(text) > max_length:
        raise ValidationError(f"Text too long: {len(text)} chars (max {max_length})")

    return True


def validate_integer_range(value: int, min_value: int, max_value: int, field_name: str = "value") -> bool:
    """
    Validate integer is within acceptable range.

    Args:
        value: Integer value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        field_name: Name of the field for error messages

    Returns:
        True if value is within range

    Raises:
        ValidationError: If value is outside range
    """
    if not isinstance(value, int):
        raise ValidationError(f"{field_name} must be an integer")

    if value < min_value or value > max_value:
        raise ValidationError(f"{field_name} out of range: {value} (min {min_value}, max {max_value})")

    return True


def validate_list_length(items: list, max_items: int, field_name: str = "list") -> bool:
    """
    Validate list length to prevent memory issues.

    Args:
        items: List to validate
        max_items: Maximum number of items allowed
        field_name: Name of the field for error messages

    Returns:
        True if length is acceptable

    Raises:
        ValidationError: If list is too long
    """
    if not isinstance(items, list):
        raise ValidationError(f"{field_name} must be a list")

    if len(items) > max_items:
        raise ValidationError(f"{field_name} too long: {len(items)} items (max {max_items})")

    return True


def validate_file_content(file_path: str, max_lines: int = 10000) -> bool:
    """
    Validate file content to prevent resource exhaustion.

    Args:
        file_path: Path to file to validate
        max_lines: Maximum number of lines allowed

    Returns:
        True if file content is acceptable

    Raises:
        ValidationError: If file has too many lines
    """
    if not os.path.exists(file_path):
        raise ValidationError(f"File does not exist: {file_path}")

    try:
        with open(file_path, encoding="utf-8") as f:
            line_count = sum(1 for _ in f)

        if line_count > max_lines:
            logger.warning(f"File too many lines: {line_count} > {max_lines}")
            raise ValidationError(f"File too many lines: {line_count} (max {max_lines})")

        return True
    except UnicodeDecodeError:
        raise ValidationError(f"File encoding error: {file_path}")
    except Exception as e:
        raise ValidationError(f"Error reading file: {e}")


def validate_config_structure(config: dict, required_sections: list[str]) -> bool:
    """
    Validate configuration structure.

    Args:
        config: Configuration dictionary to validate
        required_sections: List of required configuration sections

    Returns:
        True if configuration is valid

    Raises:
        ValidationError: If required sections are missing
    """
    if not isinstance(config, dict):
        raise ValidationError("Configuration must be a dictionary")

    missing_sections = []
    for section in required_sections:
        if section not in config:
            missing_sections.append(section)

    if missing_sections:
        logger.warning(f"Missing required configuration sections: {missing_sections}")
        raise ValidationError(f"Missing required configuration sections: {missing_sections}")

    return True
