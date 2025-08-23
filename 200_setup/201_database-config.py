#!/usr/bin/env python3
"""
Database Configuration Manager
==============================
Single source of truth for all database configuration across the AI development ecosystem.
Eliminates multiple inconsistent connection strings across the codebase.

This file follows the "One Source Per Scope" principle for configuration management.
"""

import os


class DatabaseConfigManager:
    """Centralized database configuration management for the AI development ecosystem"""

    def __init__(self):
        self._database_url: str = ""
        self._load_config()

    def _load_config(self):
        """Load database configuration from environment variables with sensible defaults"""
        # Database configuration - single source of truth
        self._database_url = (
            os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
            or "postgresql://danieljacobs@localhost:5432/ai_agency"
        )

        # Ensure DATABASE_URL is also set for compatibility
        if not os.getenv("DATABASE_URL"):
            os.environ["DATABASE_URL"] = self._database_url

    @property
    def database_url(self) -> str:
        """Get the standardized database connection string"""
        return self._database_url

    @property
    def postgres_dsn(self) -> str:
        """Alias for database_url for compatibility"""
        return self._database_url

    def get_database_config(self) -> dict:
        """Get database configuration as a dictionary"""
        return {"url": self._database_url, "dsn": self._database_url, "connection_string": self._database_url}

    def validate_database_config(self) -> bool:
        """Validate that database configuration is properly set"""
        if not self._database_url:
            return False

        # Basic validation - should start with postgresql://
        if not self._database_url.startswith("postgresql://"):
            return False

        return True

# Global configuration instance
_database_config_manager = DatabaseConfigManager()

def get_database_config() -> DatabaseConfigManager:
    """Get the global database configuration manager"""
    return _database_config_manager

def get_database_url() -> str:
    """Get the standardized database connection string"""
    return _database_config_manager.database_url

def get_postgres_dsn() -> str:
    """Get the PostgreSQL DSN for compatibility"""
    return _database_config_manager.postgres_dsn

def validate_database_config() -> bool:
    """Validate all database configuration settings"""
    return _database_config_manager.validate_database_config()
