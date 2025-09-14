from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from src.schemas.eval import CaseResult, ContextChunk, EvaluationRun, RerankerConfig, RetrievalCandidate

"""Export JSON schemas for Pydantic models."""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import QAAnswer directly to avoid agent initialization


class QAAnswer(BaseModel):
    """Structured answer output for QA tasks."""

    model_config = ConfigDict(strict=True, extra="forbid")
    answer: str = Field(min_length=1)
    confidence: float | None = None


def export_schemas():
    """Export JSON schemas for all Pydantic models."""
    schemas_dir = Path("schemas")
    schemas_dir.mkdir(exist_ok=True)

    # Export schemas for evaluation models
    (schemas_dir / "evaluation_run.schema.json").write_text(json.dumps(EvaluationRun.model_json_schema(), indent=2))

    (schemas_dir / "case_result.schema.json").write_text(json.dumps(CaseResult.model_json_schema(), indent=2))

    (schemas_dir / "retrieval_candidate.schema.json").write_text(
        json.dumps(RetrievalCandidate.model_json_schema(), indent=2)
    )

    (schemas_dir / "context_chunk.schema.json").write_text(json.dumps(ContextChunk.model_json_schema(), indent=2))

    (schemas_dir / "reranker_config.schema.json").write_text(json.dumps(RerankerConfig.model_json_schema(), indent=2))

    # Export schemas for agent models
    (schemas_dir / "qa_answer.schema.json").write_text(json.dumps(QAAnswer.model_json_schema(), indent=2))

    print("✅ Exported JSON schemas to schemas/ directory")
    print("   - evaluation_run.schema.json")
    print("   - case_result.schema.json")
    print("   - retrieval_candidate.schema.json")
    print("   - context_chunk.schema.json")
    print("   - reranker_config.schema.json")
    print("   - qa_answer.schema.json")


if __name__ == "__main__":
    export_schemas()
