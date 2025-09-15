#!/usr/bin/env python3
# ANCHOR_KEY: database-config
# ANCHOR_PRIORITY: 35
# ROLE_PINS: ["implementer", "coder"]
"""
Database Configuration Manager
==============================
DEPRECATED: Use src/common/db_dsn.resolve_dsn() instead.

This file is maintained for backward compatibility only.
All new code should use the centralized DSN resolution system.

Migration Guide:
- Replace: get_database_url()
- With: common.db_dsn.resolve_dsn()
- Replace: get_postgres_dsn()
- With: common.db_dsn.resolve_dsn()
"""

import warnings
from typing import Any

# Import the current standard
try:
    from src.common.db_dsn import resolve_dsn
except ImportError:
    # Fallback for when src is not in path
    resolve_dsn = None


def get_database_url() -> str:
    """
    DEPRECATED: Use common.db_dsn.resolve_dsn() instead.

    Get the standardized database connection string using the current DSN resolution system.
    """
    warnings.warn(
        "get_database_url() is deprecated. Use common.db_dsn.resolve_dsn() instead.", DeprecationWarning, stacklevel=2
    )

    if resolve_dsn:
        return resolve_dsn()

    # Fallback for backward compatibility
    import os

    return os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")


def get_postgres_dsn() -> str:
    """
    DEPRECATED: Use common.db_dsn.resolve_dsn() instead.

    Get the PostgreSQL DSN for compatibility.
    """
    warnings.warn(
        "get_postgres_dsn() is deprecated. Use common.db_dsn.resolve_dsn() instead.", DeprecationWarning, stacklevel=2
    )

    return get_database_url()


def get_database_config() -> dict[str, Any]:
    """
    DEPRECATED: Use common.db_dsn.resolve_dsn() instead.

    Get database configuration as a dictionary.
    """
    warnings.warn(
        "get_database_config() is deprecated. Use common.db_dsn.resolve_dsn() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    dsn = get_database_url()
    return {"url": dsn, "dsn": dsn, "connection_string": dsn}


def validate_database_config() -> bool:
    """
    DEPRECATED: Use common.db_dsn.resolve_dsn() instead.

    Validate that database configuration is properly set.
    """
    warnings.warn(
        "validate_database_config() is deprecated. Use common.db_dsn.resolve_dsn() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    try:
        dsn = get_database_url()
        return bool(dsn and dsn.startswith("postgresql://"))
    except Exception:
        return False


# Legacy class for backward compatibility
class DatabaseConfigManager:
    """
    DEPRECATED: Use common.db_dsn.resolve_dsn() instead.

    Centralized database configuration management for the AI development ecosystem.
    """

    def __init__(self):
        warnings.warn(
            "DatabaseConfigManager is deprecated. Use common.db_dsn.resolve_dsn() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._database_url = get_database_url()

    @property
    def database_url(self) -> str:
        """Get the standardized database connection string"""
        return self._database_url

    @property
    def postgres_dsn(self) -> str:
        """Alias for database_url for compatibility"""
        return self._database_url

    def get_database_config(self) -> dict[str, Any]:
        """Get database configuration as a dictionary"""
        return get_database_config()

    def validate_database_config(self) -> bool:
        """Validate that database configuration is properly set"""
        return validate_database_config()


# Global configuration instance (deprecated)
_database_config_manager = DatabaseConfigManager()


def get_database_config() -> DatabaseConfigManager:
    """
    DEPRECATED: Use common.db_dsn.resolve_dsn() instead.

    Get the global database configuration manager.
    """
    warnings.warn(
        "get_database_config() is deprecated. Use common.db_dsn.resolve_dsn() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return _database_config_manager
