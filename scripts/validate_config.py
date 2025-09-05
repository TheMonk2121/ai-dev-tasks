#!/usr/bin/env python3
"""
JSON Schema validation script for system configuration.
Run this in CI to ensure config/system.json is valid.
"""

from __future__ import annotations

import json
import os
import pathlib
import sys
from typing import Any, Dict, List, Optional, TypedDict

from pydantic import BaseModel
from sqlalchemy import create_engine, text

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
        with open(config_path, "r") as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        print(f"❌ JSON syntax error: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ Config file not found: {config_path}")
        return False


def validate_schema(config: Dict[str, Any]) -> bool:
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


def validate_agent_model_consistency(config: Dict[str, Any]) -> bool:
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
    import sys

    sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "dspy-rag-system"))

    # Import locally to avoid heavy imports on unrelated runs
    from ragchecker_pydantic_models import RAGCheckerInput, RAGCheckerMetrics, RAGCheckerResult

    from src.dspy_modules.constitution_validation import ConstitutionCompliance, ProgramOutput

    # Import DSPy module models
    from src.dspy_modules.context_models import (
        BaseContext,
        CoderContext,
        ImplementerContext,
        PlannerContext,
        ResearcherContext,
    )
    from src.dspy_modules.error_taxonomy import PydanticError, ValidationError

    out_dir = pathlib.Path("dspy-rag-system/config/database/schemas")
    out_dir.mkdir(parents=True, exist_ok=True)

    models: List[type[BaseModel]] = [
        # RAGChecker models
        RAGCheckerInput,
        RAGCheckerMetrics,
        RAGCheckerResult,
        # DSPy context models
        BaseContext,
        PlannerContext,
        CoderContext,
        ResearcherContext,
        ImplementerContext,
        # Constitution validation models
        ConstitutionCompliance,
        ProgramOutput,
        # Error taxonomy models
        PydanticError,
        ValidationError,
    ]

    combined: Dict[str, Any] = {
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
class ColumnInfo(TypedDict):
    table: str
    column: str
    data_type: str
    is_nullable: bool
    is_pk: bool
    is_fk: bool
    references: Optional[str]


class IndexInfo(TypedDict):
    table: str
    index: str
    columns: List[str]
    unique: bool


class TableInfo(TypedDict):
    name: str
    columns: List[ColumnInfo]
    indexes: List[IndexInfo]


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
    Snapshot the live DB schema (tables, columns, indexes) to version-controlled JSON.
    """
    out_dir = pathlib.Path("dspy-rag-system/config/database/schemas")
    out_dir.mkdir(parents=True, exist_ok=True)
    engine = create_engine(_dsn_from_env())

    tables: List[str] = []
    with engine.connect() as conn:
        # Convert Sequence[Any] to List[str] as recommended in Pyright troubleshooting
        tables_result = (
            conn.execute(
                text(
                    """select table_name
                    from information_schema.tables
                    where table_schema=:s and table_type='BASE TABLE'
                    order by table_name"""
                ),
                {"s": schema},
            )
            .scalars()
            .all()
        )
        tables = [str(table) for table in tables_result]

        result: List[TableInfo] = []
        for t in tables:
            cols = conn.execute(
                text(
                    """
              select c.column_name, c.data_type, c.is_nullable,
                     exists(select 1 from information_schema.table_constraints tc
                            join information_schema.key_column_usage k
                              on tc.constraint_name=k.constraint_name
                             and tc.table_schema=k.table_schema
                           where tc.table_name=c.table_name and tc.table_schema=c.table_schema
                             and tc.constraint_type='PRIMARY KEY' and k.column_name=c.column_name) as is_pk,
                     exists(select 1 from information_schema.key_column_usage k
                            join information_schema.referential_constraints rc
                              on k.constraint_name=rc.constraint_name
                             and k.constraint_schema=rc.constraint_schema
                           where k.table_name=c.table_name
                             and k.table_schema=c.table_schema
                             and k.column_name=c.column_name) as is_fk,
                     (select concat(kcu2.table_name, '.', kcu2.column_name)
                        from information_schema.referential_constraints r
                        join information_schema.key_column_usage kcu
                          on r.constraint_name=kcu.constraint_name
                         and r.constraint_schema=kcu.constraint_schema
                        join information_schema.key_column_usage kcu2
                          on r.unique_constraint_name=kcu2.constraint_name
                         and r.unique_constraint_schema=kcu2.constraint_schema
                       where kcu.table_name=c.table_name
                         and kcu.table_schema=c.table_schema
                         and kcu.column_name=c.column_name
                       limit 1) as references
              from information_schema.columns c
              where c.table_schema=:s and c.table_name=:t
              order by c.ordinal_position
            """
                ),
                {"s": schema, "t": t},
            ).all()

            columns: List[ColumnInfo] = [
                {
                    "table": t,
                    "column": r[0],
                    "data_type": str(r[1]),
                    "is_nullable": str(r[2]).upper() == "YES",
                    "is_pk": bool(r[3]),
                    "is_fk": bool(r[4]),
                    "references": (str(r[5]) if r[5] else None),
                }
                for r in cols
            ]

            idx_rows = conn.execute(
                text(
                    """
              select i.relname as index_name,
                     ix.indisunique as is_unique,
                     array(
                       select a.attname
                       from unnest(ix.indkey) k
                       join pg_attribute a on a.attrelid=ix.indrelid and a.attnum=k
                       order by array_position(ix.indkey, k)
                     ) as cols
              from pg_class t
              join pg_index ix on t.oid=ix.indrelid
              join pg_class i  on i.oid=ix.indexrelid
              join pg_namespace n on n.oid=t.relnamespace
              where n.nspname=:s and t.relname=:t and not ix.indisprimary
              order by i.relname
            """
                ),
                {"s": schema, "t": t},
            ).all()

            indexes: List[IndexInfo] = [
                {
                    "table": t,
                    "index": r[0],
                    "unique": bool(r[1]),
                    "columns": [str(c) for c in (r[2] if r[2] is not None else [])],
                }
                for r in idx_rows
            ]

            result.append({"name": t, "columns": columns, "indexes": indexes})

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
    with open(config_path, "r") as f:
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
