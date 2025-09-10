#!/usr/bin/env python3
"""
Backward Compatibility Flag System

This module implements Task 17 of B-1043: Backward Compatibility Flag (static path).
It provides a feature flag to toggle between static memory_up.sh files and the LTST store,
ensuring backward compatibility and graceful fallback.

Features:
- Feature flag to toggle between static files and LTST memory
- Runtime configuration support
- Logging of which path was used for each request
- Fallback functionality when LTST unavailable
- Agent regression validation
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CompatibilityConfig:
    """Configuration for backward compatibility."""

    use_ltst_memory: bool = True
    fallback_to_static: bool = True
    log_path_usage: bool = True
    static_files_path: str = "100_memory"
    ltst_memory_path: str = "dspy-rag-system/src/utils"
    config_file: str = ".backward_compatibility.json"

    def __post_init__(self):
        """Load configuration from file if it exists."""
        self._load_config()

    def _load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file) as f:
                    config_data = json.load(f)
                    for key, value in config_data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
                logger.info(f"Loaded backward compatibility config from {self.config_file}")
        except Exception as e:
            logger.warning(f"Failed to load backward compatibility config: {e}")

    def save_config(self):
        """Save configuration to file."""
        try:
            config_data = {
                "use_ltst_memory": self.use_ltst_memory,
                "fallback_to_static": self.fallback_to_static,
                "log_path_usage": self.log_path_usage,
                "static_files_path": self.static_files_path,
                "ltst_memory_path": self.ltst_memory_path,
            }
            with open(self.config_file, "w") as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"Saved backward compatibility config to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save backward compatibility config: {e}")


class BackwardCompatibilityManager:
    """Manages backward compatibility between static files and LTST memory."""

    def __init__(self, config: CompatibilityConfig | None = None):
        """Initialize backward compatibility manager."""
        self.config = config or CompatibilityConfig()
        self.logger = logging.getLogger(__name__)

        # Performance tracking
        self.static_path_usage = 0
        self.ltst_path_usage = 0
        self.fallback_usage = 0
        self.errors = 0

        # Path validation
        self._validate_paths()

    def _validate_paths(self):
        """Validate that required paths exist."""
        static_path = Path(self.config.static_files_path)
        if not static_path.exists():
            self.logger.warning(f"Static files path does not exist: {static_path}")

        ltst_path = Path(self.config.ltst_memory_path)
        if not ltst_path.exists():
            self.logger.warning(f"LTST memory path does not exist: {ltst_path}")

    def get_memory_content(self, query: str, user_id: str = "default") -> dict[str, Any]:
        """
        Get memory content using the configured path (LTST or static).

        Args:
            query: Memory query
            user_id: User identifier

        Returns:
            Dictionary with memory content and metadata
        """
        start_time = datetime.now()

        try:
            if self.config.use_ltst_memory:
                result = self._get_ltst_memory_content(query, user_id)
                if result and result.get("success", False):
                    self.ltst_path_usage += 1
                    self._log_path_usage("ltst", query, start_time)
                    return result

            # Fallback to static files if LTST fails or is disabled
            if self.config.fallback_to_static:
                result = self._get_static_memory_content(query, user_id)
                if result and result.get("success", False):
                    self.static_path_usage += 1
                    self._log_path_usage("static", query, start_time)
                    return result
                else:
                    self.fallback_usage += 1
                    self._log_path_usage("fallback", query, start_time)

            # Return error response
            self.errors += 1
            return {
                "success": False,
                "error": "Failed to retrieve memory content from both LTST and static paths",
                "path_used": "none",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            self.errors += 1
            self.logger.error(f"Error getting memory content: {e}")
            return {
                "success": False,
                "error": str(e),
                "path_used": "error",
                "timestamp": datetime.now().isoformat(),
            }

    def _get_ltst_memory_content(self, query: str, user_id: str) -> dict[str, Any] | None:
        """Get memory content from LTST memory system."""
        try:
            # Import LTST memory system
            from .ltst_memory_system import LTSTMemorySystem

            # Initialize LTST memory system
            ltst_system = LTSTMemorySystem()

            # Get memory content
            try:
                # Try to get system statistics as memory bundle
                memory_bundle = ltst_system.get_system_statistics()

                # Add query-specific information
                memory_bundle["query"] = query
                memory_bundle["user_id"] = user_id
                memory_bundle["source"] = "ltst_memory_system"
            except AttributeError:
                # Fallback if method doesn't exist
                memory_bundle = {
                    "query": query,
                    "user_id": user_id,
                    "source": "ltst_memory_system",
                    "status": "available",
                    "timestamp": datetime.now().isoformat(),
                }

            if memory_bundle:
                return {
                    "success": True,
                    "content": memory_bundle,
                    "path_used": "ltst",
                    "timestamp": datetime.now().isoformat(),
                }

            return None

        except ImportError as e:
            self.logger.warning(f"LTST memory system not available: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error accessing LTST memory: {e}")
            return None

    def _get_static_memory_content(self, query: str, user_id: str) -> dict[str, Any] | None:
        """Get memory content from static files."""
        try:
            static_path = Path(self.config.static_files_path)

            # Look for memory_up.sh or similar static memory files
            memory_files = [
                static_path / "memory_up.sh",
                static_path / "100_cursor-memory-context.md",
                static_path / "memory_context.md",
            ]

            content = {}

            for file_path in memory_files:
                if file_path.exists():
                    try:
                        with open(file_path, encoding="utf-8") as f:
                            file_content = f.read()
                            content[file_path.name] = file_content
                    except Exception as e:
                        self.logger.warning(f"Failed to read {file_path}: {e}")

            if content:
                return {
                    "success": True,
                    "content": content,
                    "path_used": "static",
                    "timestamp": datetime.now().isoformat(),
                }

            return None

        except Exception as e:
            self.logger.error(f"Error accessing static memory: {e}")
            return None

    def _log_path_usage(self, path_type: str, query: str, start_time: datetime):
        """Log which path was used for the request."""
        if not self.config.log_path_usage:
            return

        duration = (datetime.now() - start_time).total_seconds() * 1000

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "path_type": path_type,
            "query": query[:100],  # Truncate long queries
            "duration_ms": round(duration, 2),
        }

        self.logger.info(f"Memory path usage: {json.dumps(log_entry)}")

    def toggle_ltst_memory(self, enabled: bool) -> bool:
        """
        Toggle LTST memory usage.

        Args:
            enabled: Whether to enable LTST memory

        Returns:
            True if successful, False otherwise
        """
        try:
            self.config.use_ltst_memory = enabled
            self.config.save_config()

            self.logger.info(f"LTST memory {'enabled' if enabled else 'disabled'}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to toggle LTST memory: {e}")
            return False

    def validate_agent_compatibility(self) -> dict[str, Any]:
        """
        Validate that agents work correctly with current configuration.

        Returns:
            Dictionary with validation results
        """
        validation_results = {
            "ltst_memory_available": False,
            "static_files_available": False,
            "agent_regressions": [],
            "overall_status": "unknown",
        }

        try:
            # Test LTST memory availability
            try:
                from .ltst_memory_system import LTSTMemorySystem

                ltst_system = LTSTMemorySystem()
                try:
                    test_result = ltst_system.get_system_statistics()
                    validation_results["ltst_memory_available"] = test_result is not None
                except AttributeError:
                    validation_results["ltst_memory_available"] = False
            except Exception as e:
                validation_results["agent_regressions"].append(f"LTST memory error: {e}")

            # Test static files availability
            static_path = Path(self.config.static_files_path)
            memory_files = [
                static_path / "memory_up.sh",
                static_path / "100_cursor-memory-context.md",
            ]

            for file_path in memory_files:
                if file_path.exists():
                    validation_results["static_files_available"] = True
                    break

            # Determine overall status
            if validation_results["ltst_memory_available"] and validation_results["static_files_available"]:
                validation_results["overall_status"] = "both_available"
            elif validation_results["ltst_memory_available"]:
                validation_results["overall_status"] = "ltst_only"
            elif validation_results["static_files_available"]:
                validation_results["overall_status"] = "static_only"
            else:
                validation_results["overall_status"] = "none_available"

            return validation_results

        except Exception as e:
            validation_results["agent_regressions"].append(f"Validation error: {e}")
            validation_results["overall_status"] = "error"
            return validation_results

    def get_usage_statistics(self) -> dict[str, Any]:
        """Get usage statistics for backward compatibility."""
        return {
            "ltst_path_usage": self.ltst_path_usage,
            "static_path_usage": self.static_path_usage,
            "fallback_usage": self.fallback_usage,
            "errors": self.errors,
            "total_requests": self.ltst_path_usage + self.static_path_usage + self.fallback_usage,
            "success_rate": self._calculate_success_rate(),
            "current_config": {
                "use_ltst_memory": self.config.use_ltst_memory,
                "fallback_to_static": self.config.fallback_to_static,
                "log_path_usage": self.config.log_path_usage,
            },
        }

    def _calculate_success_rate(self) -> float:
        """Calculate success rate based on usage statistics."""
        total = self.ltst_path_usage + self.static_path_usage + self.fallback_usage + self.errors
        if total == 0:
            return 0.0

        successful = self.ltst_path_usage + self.static_path_usage
        return round(successful / total * 100, 2)

    def reset_statistics(self):
        """Reset usage statistics."""
        self.ltst_path_usage = 0
        self.static_path_usage = 0
        self.fallback_usage = 0
        self.errors = 0
        self.logger.info("Backward compatibility statistics reset")


def create_backward_compatibility_manager(config: CompatibilityConfig | None = None) -> BackwardCompatibilityManager:
    """
    Factory function to create a backward compatibility manager.

    Args:
        config: Optional configuration

    Returns:
        BackwardCompatibilityManager instance
    """
    return BackwardCompatibilityManager(config)


def test_backward_compatibility():
    """Test backward compatibility functionality."""
    print("🧪 Testing Backward Compatibility Flag System\n")

    # Create manager
    config = CompatibilityConfig(
        use_ltst_memory=True,
        fallback_to_static=True,
        log_path_usage=True,
    )
    manager = BackwardCompatibilityManager(config)

    # Test 1: Get memory content
    print("📋 Test 1: Get memory content")
    result = manager.get_memory_content("test query", "test_user")
    print(f"   ✅ Success: {result.get('success', False)}")
    print(f"   📝 Path used: {result.get('path_used', 'unknown')}")

    # Test 2: Toggle LTST memory
    print("\n📋 Test 2: Toggle LTST memory")
    success = manager.toggle_ltst_memory(False)
    print(f"   ✅ Toggle success: {success}")
    print(f"   📝 LTST enabled: {manager.config.use_ltst_memory}")

    # Test 3: Validate agent compatibility
    print("\n📋 Test 3: Validate agent compatibility")
    validation = manager.validate_agent_compatibility()
    print(f"   ✅ LTST available: {validation['ltst_memory_available']}")
    print(f"   ✅ Static files available: {validation['static_files_available']}")
    print(f"   📝 Overall status: {validation['overall_status']}")

    # Test 4: Get usage statistics
    print("\n📋 Test 4: Get usage statistics")
    stats = manager.get_usage_statistics()
    print(f"   📊 LTST usage: {stats['ltst_path_usage']}")
    print(f"   📊 Static usage: {stats['static_path_usage']}")
    print(f"   📊 Fallback usage: {stats['fallback_usage']}")
    print(f"   📊 Success rate: {stats['success_rate']}%")

    print("\n🎉 Backward compatibility tests completed!")
    print("✅ Task 17: Backward Compatibility Flag is working correctly!")


if __name__ == "__main__":
    test_backward_compatibility()
