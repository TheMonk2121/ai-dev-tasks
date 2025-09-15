from __future__ import annotations
#!/usr/bin/env python3
import json
import os
import pathlib
import sys
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy import create_engine, text
from ragchecker_pydantic_models import (
    RAGCheckerInput,
    RAGCheckerMetrics,
    RAGCheckerResult,
)
"""
JSON Schema validation script for system configuration.
Run this in CI to ensure config/system.json is valid.
"""

# JSON Schema for v0.3.1 system configuration
SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["version", "agents", "models", "memory", "error_policy", "fast_path", "security", "monitoring"],
    "properties": {
        "version": {"type": "string"},
        "agents": {"type": "object"},
        "models": {"type": "object"},
        "memory": {"type": "object"},
        "error_policy": {"type": "object"},
        "fast_path": {"type": "object"},
        "security": {"type": "object"},
        "monitoring": {"type": "object"},
    },
}

def validate_json_syntax(config_path: str) -> bool:
    """Validate JSON syntax"""
    try:
        with open(config_path) as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        print(f"❌ JSON syntax error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_path}")
        return False

def validate_schema(config: dict[str, Any]) -> bool:
    """Validate against our schema"""
    # Check required fields
    required_fields = ["version", "agents", "models", "memory", "error_policy", "fast_path", "security", "monitoring"]
    for field in required_fields:
        if field not in config:
            print(f"❌ Missing required field: {field}")
            return False

    # Check version
    if config["version"] != "0.3.1":
        print(f"❌ Invalid version: {config['version']}, expected 0.3.1")
        return False

    # Check agents structure
    if not isinstance(config["agents"], dict):
        print("❌ Agents must be an object")
        return False

    # Check models structure
    if not isinstance(config["models"], dict):
        print("❌ Models must be an object")
        return False

    # Check memory structure
    if not isinstance(config["memory"], dict):
        print("❌ Memory must be an object")
        return False

    # Check error_policy structure
    if not isinstance(config["error_policy"], dict):
        print("❌ Error policy must be an object")
        return False

    # Check fast_path structure
    if not isinstance(config["fast_path"], dict):
        print("❌ Fast path must be an object")
        return False

    # Check security structure
    if not isinstance(config["security"], dict):
        print("❌ Security must be an object")
        return False

    # Check monitoring structure
    if not isinstance(config["monitoring"], dict):
        print("❌ Monitoring must be an object")
        return False

    return True

def validate_agent_model_consistency(config: dict[str, Any]) -> bool:
    """Validate that all agents reference valid models"""
    models = config.get("models", {})
    agents = config.get("agents", {})

    for agent_name, agent_config in agents.items():
        model_id = agent_config.get("model_id")
        if not model_id:
            print(f"❌ Agent {agent_name} missing model_id")
            return False

        if model_id not in models:
            print(f"❌ Agent {agent_name} references unknown model: {model_id}")
            return False

    return True

# ---- Pydantic dump: reuse your existing models ----
def dump_pydantic_schemas() -> None:
    """
    Export JSON Schemas for core RAG models to version-controlled location.
    Uses your existing Pydantic model modules (no new infra).
    """
    # Add dspy-rag-system to path for imports

    # sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "dspy-rag-system"))  # REMOVED: DSPy venv consolidated into main project
    # Import DSPy module models lazily and tolerate absence
    dspy_context_models: list[type[BaseModel]] = []
    try:
        from src.dspy_modules.context_models import (
            BaseContext,
            CoderContext,
            ImplementerContext,
            PlannerContext,
            ResearcherContext,
        )

        dspy_context_models = [BaseContext, PlannerContext, CoderContext, ResearcherContext, ImplementerContext]
    except Exception:
        dspy_context_models = []

    constitution_models: list[type[BaseModel]] = []
    try:
        from src.dspy_modules.constitution_validation import ConstitutionCompliance, ProgramOutput

        constitution_models = [ConstitutionCompliance, ProgramOutput]
    except Exception:
        constitution_models = []

    error_models: list[type[BaseModel]] = []
    try:
        from src.dspy_modules.error_taxonomy import PydanticError, ValidationError

        error_models = [PydanticError, ValidationError]
    except Exception:
        error_models = []

    out_dir = pathlib.Path("dspy-rag-system/config/database/schemas")
    out_dir.mkdir(parents=True, exist_ok=True)

    models: list[type[BaseModel]] = [
        RAGCheckerInput,
        RAGCheckerMetrics,
        RAGCheckerResult,
        *dspy_context_models,
        *constitution_models,
        *error_models,
    ]

    combined: dict[str, Any] = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "PydanticComponents",
        "components": {},
    }

    for m in models:
        schema = m.model_json_schema()  # pydantic v2
        (out_dir / f"model_{m.__name__}.schema.json").write_text(json.dumps(schema, indent=2))
        combined["components"][m.__name__] = schema

    (out_dir / "pydantic_components.json").write_text(json.dumps(combined, indent=2))
    print("✅ Wrote Pydantic schemas → dspy-rag-system/config/database/schemas/")

# ---- DB schema snapshot via SQLAlchemy ----
class ColumnInfo(BaseModel):
    """Database column information with Pydantic validation."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    table: str = Field(..., min_length=1, description="Table name")
    column: str = Field(..., min_length=1, description="Column name")
    data_type: str = Field(..., min_length=1, description="Column data type")
    is_nullable: bool = Field(..., description="Whether column allows NULL values")
    is_pk: bool = Field(..., description="Whether column is primary key")
    is_fk: bool = Field(..., description="Whether column is foreign key")
    references: str | None = Field(None, description="Referenced table if foreign key")

    @field_validator("table", "column", "data_type")
    @classmethod
    def validate_string_fields(cls, v):
        """Validate string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("String field cannot be empty")
        return v.strip()

class IndexInfo(BaseModel):
    """Database index information with Pydantic validation."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    table: str = Field(..., min_length=1, description="Table name")
    index: str = Field(..., min_length=1, description="Index name")
    columns: list[str] = Field(..., description="List of column names in index")
    unique: bool = Field(..., description="Whether index is unique")

    @field_validator("table", "index")
    @classmethod
    def validate_string_fields(cls, v):
        """Validate string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("String field cannot be empty")
        return v.strip()

    @field_validator("columns")
    @classmethod
    def validate_columns(cls, v):
        """Validate columns list is not empty."""
        if not v:
            raise ValueError("Columns list cannot be empty")
        for col in v:
            if not col or not col.strip():
                raise ValueError("Column name cannot be empty")
        return v

class TableInfo(BaseModel):
    """Database table information with Pydantic validation."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    name: str = Field(..., min_length=1, description="Table name")
    columns: list[ColumnInfo] = Field(..., description="List of column information")
    indexes: list[IndexInfo] = Field(default_factory=list, description="List of index information")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Validate table name is not empty."""
        if not v or not v.strip():
            raise ValueError("Table name cannot be empty")
        return v.strip()

def _dsn_from_env() -> str:
    # Respect your existing env usage
    driver = os.getenv("DB_DRIVER", "postgresql+psycopg2")
    host = os.getenv("PGHOST", "localhost")
    port = os.getenv("PGPORT", "5432")
    user = os.getenv("PGUSER", "danieljacobs")
    pwd = os.getenv("PGPASSWORD", "postgres")
    db = os.getenv("PGDATABASE", "ai_agency")
    return f"{driver}://{user}:{pwd}@{host}:{port}/{db}"

def dump_db_schema_json(schema: str = "public") -> None:
    """
    Snapshot the live DB schema (tables, columns) to version-controlled JSON.
    Keeps the query simple to avoid cross-database quirks.
    """
    out_dir = pathlib.Path("dspy-rag-system/config/database/schemas")
    out_dir.mkdir(parents=True, exist_ok=True)
    engine = create_engine(_dsn_from_env())

    result: list[TableInfo] = []
    with engine.connect() as conn:
        tables = (
            conn.execute(
                text(
                    """
                    select table_name
                    from information_schema.tables
                    where table_schema=:s and table_type='BASE TABLE'
                    order by table_name
                    """
                ),
                {"s": schema},
            )
            .scalars()
            .all()
        )
        for t in tables:
            cols = conn.execute(
                text(
                    """
                    select column_name, data_type, is_nullable
                    from information_schema.columns
                    where table_schema=:s and table_name=:t
                    order by ordinal_position
                    """
                ),
                {"s": schema, "t": t},
            ).all()
            columns: list[ColumnInfo] = [
                {
                    "table": str(t),
                    "column": str(r[0]),
                    "data_type": str(r[1]),
                    "is_nullable": str(r[2]).upper() == "YES",
                    "is_pk": False,
                    "is_fk": False,
                    "references": None,
                }
                for r in cols
            ]
            result.append({"name": str(t), "columns": columns, "indexes": []})

    (out_dir / "db_schema.snapshot.json").write_text(json.dumps(result, indent=2))
    print("✅ Wrote DB schema → dspy-rag-system/config/database/schemas/db_schema.snapshot.json")

def main():
    """Main validation function"""
    config_path = "config/system.json"

    print("🔍 Validating system configuration...")

    # Validate JSON syntax
    if not validate_json_syntax(config_path):
        sys.exit(1)

    # Load config
    with open(config_path) as f:
        config = json.load(f)

    # Validate schema
    if not validate_schema(config):
        sys.exit(1)

    # Validate agent-model consistency
    if not validate_agent_model_consistency(config):
        sys.exit(1)

    print("✅ Configuration validation passed!")

    # Generate schema snapshots if requested
    if "--dump-schemas" in sys.argv:
        print("📋 Generating schema snapshots...")
        try:
            dump_pydantic_schemas()
            dump_db_schema_json()
            print("✅ Schema snapshots generated successfully!")
        except Exception as e:
            print(f"❌ Schema snapshot generation failed: {e}")
            sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
