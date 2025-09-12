from __future__ import annotations
import os
from pathlib import Path
from typing import Any
import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from .models import (
import sys
from typing import Any, Dict, List, Optional, Union
"""Centralized settings management with YAML defaults and environment overrides."""



    RAG,
    Database,
    Development,
    Eval,
    Memory,
    Observability,
    Performance,
    Security,
)


class YamlSource(PydanticBaseSettingsSource):
    """Custom settings source for YAML configuration files."""

    def __init__(self, settings_cls, path: Path):
        super().__init__(settings_cls)
        self.path = path

    def __call__(self) -> dict[str, Any]:
        """Load configuration from YAML file."""
        if not self.path.exists():
            return {}

        try:
            data = yaml.safe_load(self.path.read_text()) or {}
            return data
        except Exception as e:
            # Log warning but don't fail - let other sources provide defaults
            print(f"Warning: Could not load YAML config from {self.path}: {e}")
            return {}

    def get_field_value(self, field_info, field_name: str) -> tuple[Any, str, bool]:
        """Get field value from YAML source."""
        data = self()
        if not data:
            return None, field_name, False

        # For nested models, we need to return the entire nested dict
        # pydantic-settings will handle the nested model creation
        if field_name in data:
            return data[field_name], field_name, True

        return None, field_name, False


class Settings(BaseSettings):
    """Centralized application settings with typed validation."""

    # ---- Core Configuration ----
    env: str = Field(default="dev", description="Environment: dev, test, or prod")
    root_dir: Path = Field(default_factory=Path.cwd, description="Project root directory")

    # ---- Feature Flags / Execution Guards ----
    use_pydantic_agent: bool = Field(
        default=False,
        description="Toggle Pydantic AI agent boundary fronting DSPy pipeline",
    )
    use_memory_graph: bool = Field(
        default=False,
        description="Toggle Pydantic Graph for memory consolidation (off hot path)",
    )
    strict_provenance: bool = Field(
        default=True,
        description="Reject rows lacking ingest_run_id/chunk_variant at boundaries",
    )
    limit_concurrency: int = Field(ge=1, le=64, default=3, description="Global concurrency cap while stabilizing")

    # ---- Domain-Specific Configuration ----
    db: Database = Field(default_factory=lambda: Database(), description="Database configuration")
    rag: RAG = Field(default_factory=lambda: RAG(), description="RAG system configuration")
    eval: Eval = Field(default_factory=lambda: Eval(), description="Evaluation configuration")
    obs: Observability = Field(default_factory=lambda: Observability(), description="Observability configuration")
    security: Security = Field(default_factory=lambda: Security(), description="Security configuration")
    performance: Performance = Field(default_factory=lambda: Performance(), description="Performance configuration")
    memory: Memory = Field(default_factory=lambda: Memory(), description="Memory system configuration")
    dev: Development = Field(default_factory=lambda: Development(), description="Development configuration")

    # ---- Pydantic Settings Configuration ----
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
        secrets_dir=os.getenv("SECRETS_DIR", None),
        case_sensitive=False,
        validate_assignment=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ):
        """Customize settings sources with clear precedence order."""
        # Determine environment-specific YAML file
        env = os.getenv("APP_ENV", "dev")
        base_path = Path("configs/base.yaml")
        env_path = Path(f"configs/{env}.yaml")

        return (
            init_settings,  # 1. Explicit kwargs (highest priority)
            env_settings,  # 2. Environment variables (APP_*)
            dotenv_settings,  # 3. .env file
            YamlSource(settings_cls, env_path),  # 4. Environment-specific YAML
            YamlSource(settings_cls, base_path),  # 5. Base YAML defaults
            file_secret_settings,  # 6. Secret files (lowest priority)
        )

    def model_dump_safe(self) -> dict[str, Any]:
        """Dump settings excluding sensitive information."""
        return self.model_dump(
            exclude={
                "security": {"openai_api_key", "aws_access_key_id", "aws_secret_access_key"},
                "obs": {"logfire_token"},
            }
        )


# Lazy singleton to avoid import cycles
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get the global settings instance (lazy singleton)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """Reset the global settings instance (useful for testing)."""
    global _settings
    _settings = None


def reload_settings() -> Settings:
    """Reload settings from all sources."""
    global _settings
    _settings = None
    return get_settings()
