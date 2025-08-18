#!/usr/bin/env python3.12
"""
Module Description

This module provides brief description of functionality.

Author: Your Name
Version: 1.0
Last Updated: Date
"""

# Standard library imports (always first)
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

# Third-party imports
# import requests
# import psycopg2

# Local imports
# from utils.logger import setup_logger
# from utils.config_manager import ConfigManager


@dataclass
class ExampleData:
    """Example data structure."""

    name: str
    value: int
    metadata: dict[str, Any] | None = None


class ExampleClass:
    """Example class demonstrating proper structure."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the example class."""
        self.config = config or self._get_default_config()
        self.data: list[ExampleData] = []

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration."""
        return {
            "setting1": "default_value",
            "setting2": 42,
        }

    def process_data(self, input_data: list[str]) -> list[ExampleData]:
        """Process input data and return structured results."""
        results = []

        for item in input_data:
            # Example of proper f-string usage
            processed_item = ExampleData(
                name=f"processed_{item}",
                value=len(item),
                metadata={"processed_at": datetime.now().isoformat()},
            )
            results.append(processed_item)

        return results

    def validate_input(self, data: Any) -> bool:
        """Validate input data."""
        if not isinstance(data, (str, list)):  # noqa: UP038
            return False

        # Example of proper string usage (not f-string when no placeholders)
        if isinstance(data, str):
            return len(data) > 0

        return True


def main():
    """Main function for standalone execution."""
    example = ExampleClass()

    # Example usage
    test_data = ["item1", "item2", "item3"]
    results = example.process_data(test_data)

    # Proper f-string usage with placeholders
    print(f"Processed {len(results)} items")

    for result in results:
        print(f"Item: {result.name}, Value: {result.value}")


if __name__ == "__main__":
    main()
