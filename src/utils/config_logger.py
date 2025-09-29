#!/usr/bin/env python3
"""
Comprehensive Configuration Logger with Logfire Integration

Captures and logs all evaluation configuration details including:
- Environment variables
- Database settings
- Model configurations
- Memory system settings
- Profile configurations
- System state

Integrates with Logfire for real-time observability and tracking.
"""

from __future__ import annotations

import json
import os
import sys
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.common.db_dsn import resolve_dsn

# Import Logfire for observability
logfire_available = False
logfire = None
init_observability = None
try:
    from scripts.monitoring.observability import get_logfire, init_observability

    logfire = get_logfire()
    logfire_available = True
except ImportError:
    pass

# Import psycopg (v3) for database operations
psycopg_available = False
psycopg = None
dict_row = None
try:
    import psycopg
    from psycopg.rows import dict_row

    psycopg_available = True
except Exception:
    pass


class ConfigLogger:
    """Comprehensive configuration logging for evaluation runs."""

    def __init__(self, run_id: str | None = None):
        self.run_id: str = run_id or f"config-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.config_data: dict[str, Any] = {}
        self.logfire_span: Any = None

        # Initialize Logfire if available
        if logfire_available and init_observability and logfire:
            try:
                init_observability(service="ai-dev-tasks")
                self.logfire_span = logfire.span("config.capture", run_id=self.run_id)
            except Exception as e:
                print(f"⚠️  Logfire initialization failed: {e}")
                self.logfire_span = None

    def capture_full_config(self) -> dict[str, Any]:
        """Capture complete system configuration."""
        with self.logfire_span if self.logfire_span else nullcontext():
            self.config_data = {
                "run_id": self.run_id,
                "timestamp": datetime.now().isoformat(),
                "environment": self._capture_environment(),
                "database": self._capture_database_config(),
                "evaluation": self._capture_evaluation_config(),
                "memory": self._capture_memory_config(),
                "models": self._capture_model_config(),
                "system": self._capture_system_config(),
                "profiles": self._capture_profile_configs(),
            }

            # Log to Logfire
            if logfire_available and logfire:
                try:
                    logfire.info(
                        "config.captured",
                        run_id=self.run_id,
                        profile=self.config_data["evaluation"]["profile"],
                        driver=self.config_data["evaluation"]["driver"],
                        database_connected=self.config_data["database"]["connection_test"],
                        env_vars_count=len(self.config_data["environment"]),
                        profiles_count=len(self.config_data["profiles"]),
                        config_data=self.config_data,
                    )
                except Exception as e:
                    print(f"⚠️  Logfire logging failed: {e}")

            return self.config_data

    def _capture_environment(self) -> dict[str, Any]:
        """Capture relevant environment variables."""
        env_vars = [
            # Database
            "POSTGRES_DSN",
            "DATABASE_URL",
            "PG_SSLMODE",
            # Evaluation
            "EVAL_PROFILE",
            "EVAL_DRIVER",
            "RAGCHECKER_USE_REAL_RAG",
            "USE_GOLD",
            "GOLD_CASES_PATH",
            "EVAL_CONCURRENCY",
            # Retrieval
            "RETRIEVER_MIN_CHARS",
            "RETRIEVER_MIN_CHARS_SHORT_QUERY",
            "RETRIEVER_TOPK_VEC",
            "RETRIEVER_TOPK_BM25",
            # Models
            "DSPY_MODEL",
            "AWS_REGION",
            "AWS_ACCESS_KEY_ID",
            "AWS_SECRET_ACCESS_KEY",
            "USE_BEDROCK_QUEUE",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            # Memory
            "MEMORY_SYSTEM",
            "LTST_ENABLED",
            "CURSOR_MEMORY_ENABLED",
            # System
            "APP_ENV",
            "MAX_WORKERS",
            "SEED",
            "UV_PROJECT_ENVIRONMENT",
            # Ingestion
            "INGEST_RUN_ID",
            "CHUNK_VARIANT",
            "CHUNK_SIZE_TOKENS",
            "CHUNK_OVERLAP_TOKENS",
            "SOURCE_COMMIT",
        ]

        env_config = {}
        for var in env_vars:
            value = os.getenv(var)
            if value is not None:
                # Redact sensitive values
                if any(sensitive in var.upper() for sensitive in ["KEY", "PASSWORD", "SECRET", "TOKEN"]):
                    env_config[var] = "***REDACTED***"
                else:
                    env_config[var] = value

        return env_config

    def _capture_database_config(self) -> dict[str, Any]:
        """Capture database configuration and connection details."""
        db_config: dict[str, Any] = {
            "dsn_configured": False,
            "connection_test": False,
            "extensions": [],
            "tables": [],
            "error": None,
        }

        if not psycopg_available or not psycopg:
            db_config["error"] = "psycopg (v3) not available"
            return db_config

        try:
            dsn = resolve_dsn(strict=False)
            db_config["dsn_configured"] = True

            # Test connection and get info
            with psycopg.connect(dsn) as conn:
                with conn.cursor(row_factory=dict_row) as cur:  # type: ignore
                    # Test connection
                    cur.execute("SELECT 1")
                    db_config["connection_test"] = True

                    # Get extensions
                    cur.execute(
                        """
                        SELECT extname, extversion 
                        FROM pg_extension 
                        WHERE extname IN ('vector', 'pg_trgm', 'pg_stat_statements')
                        ORDER BY extname
                    """
                    )
                    db_config["extensions"] = [dict(row) for row in cur.fetchall()]

                    # Get relevant tables
                    cur.execute(
                        """
                        SELECT tablename, schemaname 
                        FROM pg_tables 
                        WHERE schemaname = 'public' 
                        AND tablename IN ('documents', 'document_chunks', 'conversation_sessions', 
                                        'conversation_messages', 'eval_event', 'eval_run', 'eval_case_result')
                        ORDER BY tablename
                    """
                    )
                    db_config["tables"] = [dict(row) for row in cur.fetchall()]

        except Exception as e:
            db_config["error"] = str(e)

        return db_config

    def _capture_evaluation_config(self) -> dict[str, Any]:
        """Capture evaluation-specific configuration."""
        return {
            "profile": os.getenv("EVAL_PROFILE", "unknown"),
            "driver": os.getenv("EVAL_DRIVER", "unknown"),
            "use_real_rag": os.getenv("RAGCHECKER_USE_REAL_RAG", "0") == "1",
            "use_gold": os.getenv("USE_GOLD", "0") == "1",
            "gold_cases_path": os.getenv("GOLD_CASES_PATH", ""),
            "concurrency": int(os.getenv("EVAL_CONCURRENCY", "1")),
            "retriever_min_chars": int(os.getenv("RETRIEVER_MIN_CHARS", "140")),
            "retriever_min_chars_short": int(os.getenv("RETRIEVER_MIN_CHARS_SHORT_QUERY", "80")),
        }

    def _capture_memory_config(self) -> dict[str, Any]:
        """Capture memory system configuration."""
        return {
            "ltst_enabled": os.getenv("LTST_ENABLED", "0") == "1",
            "cursor_memory_enabled": os.getenv("CURSOR_MEMORY_ENABLED", "0") == "1",
            "memory_system": os.getenv("MEMORY_SYSTEM", "unknown"),
            "rehydration_enabled": os.getenv("REHYDRATION_ENABLED", "0") == "1",
        }

    def _capture_model_config(self) -> dict[str, Any]:
        """Capture model and provider configuration."""
        return {
            "dspy_model": os.getenv("DSPY_MODEL", ""),
            "aws_region": os.getenv("AWS_REGION", ""),
            "use_bedrock_queue": os.getenv("USE_BEDROCK_QUEUE", "0") == "1",
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
            "aws_configured": bool(os.getenv("AWS_ACCESS_KEY_ID")),
        }

    def _capture_system_config(self) -> dict[str, Any]:
        """Capture system-level configuration."""
        return {
            "app_env": os.getenv("APP_ENV", "unknown"),
            "max_workers": int(os.getenv("MAX_WORKERS", "1")),
            "seed": os.getenv("SEED", ""),
            "uv_environment": os.getenv("UV_PROJECT_ENVIRONMENT", ""),
            "python_version": sys.version,
            "platform": sys.platform,
        }

    def _capture_profile_configs(self) -> dict[str, Any]:
        """Capture profile-specific configurations."""
        profiles = {}
        profile_dir = project_root / "evals" / "configs" / "profiles"

        if profile_dir.exists():
            for env_file in profile_dir.glob("*.env"):
                profile_name = env_file.stem
                try:
                    with open(env_file) as f:
                        content = f.read()
                    profiles[profile_name] = {
                        "file_path": str(env_file),
                        "content": content,
                        "parsed": self._parse_env_content(content),
                    }
                except Exception as e:
                    profiles[profile_name] = {"error": str(e)}

        return profiles

    def _parse_env_content(self, content: str) -> dict[str, str]:
        """Parse environment file content."""
        parsed = {}
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                parsed[key.strip()] = value.strip().strip("\"'")
        return parsed

    def log_to_file(self, output_path: Path) -> None:
        """Log configuration to JSON file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(self.config_data, f, indent=2, default=str)

    def log_to_database(self, dsn: str) -> None:
        """Log configuration to database (if eval tables exist)."""
        if not psycopg_available or not psycopg:
            print("Warning: psycopg (v3) not available, cannot log to database")
            return

        try:
            with psycopg.connect(dsn) as conn:
                with conn.cursor(row_factory=dict_row) as cur:  # type: ignore
                    # Check if eval tables exist
                    cur.execute(
                        """
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.tables 
                            WHERE table_name = 'eval_run'
                        )
                    """
                    )
                    result = cur.fetchone()
                    if not result or not result["exists"]:
                        return  # Skip if eval tables don't exist

                    # Insert config as metadata
                    cur.execute(
                        """
                        INSERT INTO eval_run (run_id, tag, started_at, meta)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (run_id) DO UPDATE SET
                            meta = EXCLUDED.meta,
                            started_at = EXCLUDED.started_at
                    """,
                        (self.run_id, "config_log", datetime.now(), json.dumps(self.config_data, default=str)),
                    )
                    conn.commit()
        except Exception as e:
            print(f"Warning: Could not log config to database: {e}")


def create_config_logger(run_id: str | None = None) -> ConfigLogger:
    """Factory function to create a config logger."""
    return ConfigLogger(run_id)


if __name__ == "__main__":
    # Test the config logger
    logger = create_config_logger("test-config")
    config = logger.capture_full_config()

    # Print summary
    print("🔧 Configuration Summary:")
    print(f"   Run ID: {config['run_id']}")
    print(f"   Profile: {config['evaluation']['profile']}")
    print(f"   Driver: {config['evaluation']['driver']}")
    print(f"   Database: {'✅' if config['database']['connection_test'] else '❌'}")
    print(f"   Extensions: {len(config['database']['extensions'])}")
    print(f"   Environment Variables: {len(config['environment'])}")
    print(f"   Profiles: {len(config['profiles'])}")

    # Save to file
    output_path = project_root / "300_evals" / "metrics" / "logs" / f"config_{logger.run_id}.json"
    logger.log_to_file(output_path)
    print(f"   Saved to: {output_path}")
