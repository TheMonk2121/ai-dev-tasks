#!/usr/bin/env python3
"""
Evaluation Schema Audit Script

Audits all evaluation system schemas to identify inconsistencies and standardization opportunities.
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Set

sys.path.append(".")


@dataclass
class SchemaInfo:
    """Information about a schema definition"""

    file_path: str
    schema_name: str
    schema_type: str  # "dataclass", "pydantic", "typeddict"
    fields: dict[str, str]  # field_name -> field_type
    is_evaluation: bool = False


def audit_schemas() -> list[SchemaInfo]:
    """Audit all schemas in the evaluation system"""
    schemas = []

    # 1. Gold Case Schemas
    schemas.append(
        SchemaInfo(
            file_path="src/utils/gold_loader.py",
            schema_name="GoldCase",
            schema_type="dataclass",
            fields={
                "id": "str",
                "mode": "str",
                "query": "str",
                "tags": "List[str]",
                "category": "Optional[str]",
                "gt_answer": "Optional[str]",
                "expected_files": "Optional[List[str]]",
                "globs": "Optional[List[str]]",
                "expected_decisions": "Optional[List[str]]",
                "notes": "Optional[str]",
            },
            is_evaluation=True,
        )
    )

    # 2. Legacy Case Schema
    schemas.append(
        SchemaInfo(
            file_path="evals/load_cases.py",
            schema_name="Case",
            schema_type="dataclass",
            fields={"id": "str", "query": "str", "tag": "str", "qvec": "list"},  # Note: singular, not plural
            is_evaluation=True,
        )
    )

    # 3. RAGChecker Result Schema
    schemas.append(
        SchemaInfo(
            file_path="scripts/ragchecker_evaluation.py",
            schema_name="RAGCheckerResult",
            schema_type="pydantic",
            fields={
                "test_case_name": "str",
                "query": "str",
                "custom_score": "float",
                "ragchecker_scores": "Dict[str, float]",
                "ragchecker_overall": "float",
                "comparison": "Dict[str, Any]",
                "recommendation": "str",
            },
            is_evaluation=True,
        )
    )

    # 4. DSPy RAG Contracts
    schemas.append(
        SchemaInfo(
            file_path="dspy-rag-system/src/eval/contracts.py",
            schema_name="QuerySample",
            schema_type="typeddict",
            fields={
                "id": "str",
                "question": "str",
                "gold_doc_ids": "Optional[List[str]]",
                "gold_pages": "Optional[List[str]]",
                "claim": "Optional[str]",
                "expected_answer": "Optional[str]",
            },
            is_evaluation=True,
        )
    )

    # 5. Official RAGChecker EvalItem
    schemas.append(
        SchemaInfo(
            file_path="300_experiments/300_testing-scripts/ragchecker_official_evaluation.py",
            schema_name="EvalItem",
            schema_type="typeddict",
            fields={"response": "str", "gt_answer": "str", "query": "str", "query_id": "Optional[str]"},
            is_evaluation=True,
        )
    )

    return schemas


def analyze_schema_inconsistencies(schemas: list[SchemaInfo]) -> dict[str, Any]:
    """Analyze schema inconsistencies"""
    analysis = {
        "field_naming_inconsistencies": [],
        "type_inconsistencies": [],
        "missing_fields": [],
        "redundant_schemas": [],
        "standardization_opportunities": [],
    }

    # Group schemas by purpose
    gold_schemas = [s for s in schemas if "gold" in s.schema_name.lower() or "case" in s.schema_name.lower()]
    result_schemas = [s for s in schemas if "result" in s.schema_name.lower()]

    # Check field naming inconsistencies
    id_fields = set()
    query_fields = set()
    answer_fields = set()

    for schema in schemas:
        if "id" in schema.fields:
            id_fields.add("id")
        if "query" in schema.fields:
            query_fields.add("query")
        if "question" in schema.fields:
            query_fields.add("question")
        if "gt_answer" in schema.fields:
            answer_fields.add("gt_answer")
        if "expected_answer" in schema.fields:
            answer_fields.add("expected_answer")
        if "response" in schema.fields:
            answer_fields.add("response")

    if len(id_fields) > 1:
        analysis["field_naming_inconsistencies"].append(f"ID fields: {id_fields}")
    if len(query_fields) > 1:
        analysis["field_naming_inconsistencies"].append(f"Query fields: {query_fields}")
    if len(answer_fields) > 1:
        analysis["field_naming_inconsistencies"].append(f"Answer fields: {answer_fields}")

    # Check for redundant schemas
    if len(gold_schemas) > 1:
        analysis["redundant_schemas"].append(f"Multiple gold/case schemas: {[s.schema_name for s in gold_schemas]}")

    # Standardization opportunities
    analysis["standardization_opportunities"] = [
        "Standardize on 'id' field (not 'case_id' or 'query_id')",
        "Standardize on 'query' field (not 'question')",
        "Standardize on 'gt_answer' field (not 'expected_answer' or 'response')",
        "Standardize on 'tags' field (not 'tag')",
        "Consolidate GoldCase and Case schemas",
        "Use consistent typing (Pydantic vs dataclass vs TypedDict)",
    ]

    return analysis


def main():
    """Main audit function"""
    print("🔍 Evaluation Schema Audit")
    print("=" * 50)

    schemas = audit_schemas()
    analysis = analyze_schema_inconsistencies(schemas)

    print(f"\n📊 Found {len(schemas)} evaluation schemas:")
    for schema in schemas:
        print(f"  - {schema.schema_name} ({schema.schema_type}) in {schema.file_path}")
        print(f"    Fields: {list(schema.fields.keys())}")

    print("\n⚠️  Schema Inconsistencies:")
    for category, issues in analysis.items():
        if issues:
            print(f"\n{category.replace('_', ' ').title()}:")
            for issue in issues:
                print(f"  - {issue}")

    print("\n🎯 Standardization Recommendations:")
    print("1. Create a unified GoldCase schema with consistent field names")
    print("2. Standardize on Pydantic BaseModel for validation")
    print("3. Use consistent field naming across all schemas")
    print("4. Consolidate redundant schemas")
    print("5. Add proper validation and type hints")

    return schemas, analysis


if __name__ == "__main__":
    schemas, analysis = main()
