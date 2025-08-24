# ANCHOR_KEY: prompt-sanitizer
# ANCHOR_PRIORITY: 25
# ROLE_PINS: ["implementer", "coder"]
"""
Prompt Sanitization Utility

Provides regex-based prompt sanitization with configurable block-list and optional whitelist.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Raised when a security violation is detected"""

    pass


def load_security_config() -> Dict[str, Any]:
    """Load security configuration from system.json"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "system.json")
        with open(config_path, "r") as f:
            config = json.load(f)

        security_config = config.get("security", {})

        return {
            "prompt_blocklist": security_config.get("prompt_blocklist", ["{{", "}}", "<script>"]),
            "prompt_whitelist": security_config.get("prompt_whitelist", []),
            "file_validation": security_config.get(
                "file_validation", {"max_size_mb": 50, "allowed_ext": ["txt", "md", "pdf", "csv"]}
            ),
        }
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logger.warning(f"Could not load security config: {e}. Using defaults.")
        return {
            "prompt_blocklist": ["{{", "}}", "<script>"],
            "prompt_whitelist": [],
            "file_validation": {"max_size_mb": 50, "allowed_ext": ["txt", "md", "pdf", "csv"]},
        }


def sanitize_prompt(prompt: str, model_id: Optional[str] = None) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        prompt: The input prompt to sanitize
        model_id: Optional model ID for model-specific sanitization

    Returns:
        Sanitized prompt string

    Raises:
        SecurityError: If blocked patterns are detected
    """
    if not prompt or not isinstance(prompt, str):
        return prompt

    config = load_security_config()
    blocklist = config["prompt_blocklist"]
    whitelist = config["prompt_whitelist"]

    # Convert to lowercase for case-insensitive matching
    prompt_lower = prompt.lower()

    # If whitelist is provided, only allow whitelisted patterns
    if whitelist:
        # Check if any non-whitelisted patterns are present
        for pattern in blocklist:
            if pattern.lower() in prompt_lower:
                # Check if this pattern is in the whitelist
                if pattern not in whitelist:
                    raise SecurityError(f"Blocked pattern detected: {pattern}")
        return prompt.strip()

    # Otherwise, use block-list approach
    for pattern in blocklist:
        if pattern.lower() in prompt_lower:
            raise SecurityError(f"Blocked pattern detected: {pattern}")

    return prompt.strip()


def validate_file_path(file_path: str) -> bool:
    """
    Validate file path to prevent path traversal attacks.

    Args:
        file_path: The file path to validate

    Returns:
        True if path is valid, False otherwise
    """
    if not file_path or not isinstance(file_path, str):
        return False

    # Check for path traversal attempts
    dangerous_patterns = [
        "../",
        "..\\",
        "..%2f",
        "..%5c",  # Directory traversal
        "file://",
        "ftp://",
        "http://",
        "https://",  # URL schemes
        "data:",
        "javascript:",  # Dangerous protocols
    ]

    file_path_lower = file_path.lower()
    for pattern in dangerous_patterns:
        if pattern in file_path_lower:
            logger.warning(f"Potentially dangerous file path detected: {file_path}")
            return False

    # Check for absolute paths (optional security measure)
    if os.path.isabs(file_path):
        logger.warning(f"Absolute path detected: {file_path}")
        return False

    return True


def validate_file_size(file_size_bytes: int) -> bool:
    """
    Validate file size against configured limits.

    Args:
        file_size_bytes: File size in bytes

    Returns:
        True if file size is acceptable, False otherwise
    """
    config = load_security_config()
    max_size_mb = config["file_validation"]["max_size_mb"]

    # Check environment variable override
    env_max_size = os.getenv("SECURITY_MAX_FILE_MB")
    if env_max_size:
        try:
            max_size_mb = int(env_max_size)
        except ValueError:
            logger.warning(f"Invalid SECURITY_MAX_FILE_MB value: {env_max_size}")

    max_size_bytes = max_size_mb * 1024 * 1024

    if file_size_bytes > max_size_bytes:
        logger.warning(f"File size {file_size_bytes} bytes exceeds limit {max_size_bytes} bytes")
        return False

    return True


def validate_file_extension(filename: str) -> bool:
    """
    Validate file extension against allowed extensions.

    Args:
        filename: The filename to validate

    Returns:
        True if extension is allowed, False otherwise
    """
    if not filename:
        return False

    config = load_security_config()
    allowed_extensions = config["file_validation"]["allowed_ext"]

    # Extract file extension
    _, ext = os.path.splitext(filename)
    if ext:
        ext = ext.lower().lstrip(".")
        return ext in allowed_extensions

    return False


def sanitize_and_validate_input(
    prompt: str, file_path: Optional[str] = None, file_size_bytes: Optional[int] = None, model_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Comprehensive input sanitization and validation.

    Args:
        prompt: The prompt to sanitize
        file_path: Optional file path to validate
        file_size_bytes: Optional file size to validate
        model_id: Optional model ID for model-specific validation

    Returns:
        Dictionary with validation results

    Raises:
        SecurityError: If any security violations are detected
    """
    results = {
        "prompt_sanitized": None,
        "file_path_valid": None,
        "file_size_valid": None,
        "file_extension_valid": None,
        "overall_valid": True,
    }

    try:
        # Sanitize prompt
        results["prompt_sanitized"] = sanitize_prompt(prompt, model_id)
    except SecurityError as e:
        results["overall_valid"] = False
        logger.error(f"Prompt sanitization failed: {e}")
        raise

    # Validate file path if provided
    if file_path:
        results["file_path_valid"] = validate_file_path(file_path)
        if not results["file_path_valid"]:
            results["overall_valid"] = False

    # Validate file size if provided
    if file_size_bytes is not None:
        results["file_size_valid"] = validate_file_size(file_size_bytes)
        if not results["file_size_valid"]:
            results["overall_valid"] = False

    # Validate file extension if file path provided
    if file_path:
        results["file_extension_valid"] = validate_file_extension(file_path)
        if not results["file_extension_valid"]:
            results["overall_valid"] = False

    return results
