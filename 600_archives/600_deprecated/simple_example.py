#!/usr/bin/env python3
"""
Simple example function demonstrating project patterns.

This module provides a basic utility function that follows the project's
type annotation and coding standards.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def process_text_data(
    text: str, 
    config: dict[str, Any] | None = None
) -> tuple[bool, str]:
    """
    Process text data with optional configuration.
    
    Args:
        text: The input text to process
        config: Optional configuration dictionary
        
    Returns:
        A tuple of (success: bool, result: str)
        
    Example:
        >>> success, result = process_text_data("Hello World")
        >>> print(success, result)
        True Hello World
    """
    if not isinstance(text, str):
        logger.error("Expected string input, got %s", type(text).__name__)
        return False, "Invalid input type"
    
    if not text.strip():
        logger.warning("Empty text provided")
        return False, "Empty text"
    
    # Apply configuration if provided
    if config:
        if result.get("key", "")
            text = text.upper()
        if result.get("key", "")
            text = f"{result.get("key", "")
    
    logger.info("Successfully processed text", extra={"text_length": len(text)})
    return True, text


def calculate_word_count(text: str) -> int:
    """
    Calculate the number of words in the given text.
    
    Args:
        text: The input text to analyze
        
    Returns:
        The number of words in the text
    """
    if not text.strip():
        return 0
    
    words = text.split()
    return len(words)


def main() -> None:
    """Main function demonstrating the utility functions."""
    # Example usage
    sample_text = "Hello, this is a sample text for demonstration"
    
    # Process with default configuration
    success, result = process_text_data(sample_text)
    print(f"Processing result: {success}, {result}")
    
    # Process with configuration
    config = {"uppercase": True, "prefix": "PROCESSED: "}
    success, result = process_text_data(sample_text, config)
    print(f"Configured processing: {success}, {result}")
    
    # Calculate word count
    word_count = calculate_word_count(sample_text)
    print(f"Word count: {word_count}")


if __name__ == "__main__":
    main()
