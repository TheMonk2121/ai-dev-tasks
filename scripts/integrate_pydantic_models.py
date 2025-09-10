"""Integration example showing how to wire in new Pydantic models to existing evaluation runners."""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.schemas.eval import CaseResult, ContextChunk, EvaluationRun, RetrievalCandidate
from src.settings import load_eval_settings


def create_evaluation_run_from_legacy_data(
    legacy_results: list[dict[str, Any]], profile: str = "default"
) -> EvaluationRun:
    """Convert legacy evaluation results to new Pydantic models.

    This function demonstrates how to migrate existing evaluation data
    to the new strict Pydantic models.
    """
    cases = []

    for result in legacy_results:
        # Convert legacy result to new CaseResult
        case = CaseResult(
            case_id=result.get("id", "unknown"),
            mode=result.get("mode", "rag"),
            query=result.get("query", ""),
            predicted_answer=result.get("predicted_answer"),
            precision=result.get("metrics", {}).get("precision"),
            recall=result.get("metrics", {}).get("recall"),
            f1=result.get("metrics", {}).get("f1"),
            faithfulness=result.get("metrics", {}).get("faithfulness"),
            answer_latency_ms=result.get("timings", {}).get("answer_latency_ms"),
        )

        # Convert retrieval candidates if present
        if "retrieval_snapshot" in result:
            for candidate in result["retrieval_snapshot"]:
                retrieval_candidate = RetrievalCandidate(
                    doc_id=candidate.get("doc_id", "unknown"),
                    score=candidate.get("score", 0.0),
                    title=candidate.get("title"),
                    url=candidate.get("url"),
                    chunk=candidate.get("chunk", ""),
                )
                case.retrieval_snapshot.append(retrieval_candidate)

        # Convert context chunks if present
        if "retrieved_context" in result:
            for chunk in result["retrieved_context"]:
                context_chunk = ContextChunk(
                    source_id=chunk.get("source_id", "unknown"),
                    text=chunk.get("text", ""),
                    start=chunk.get("start"),
                    end=chunk.get("end"),
                )
                case.retrieved_context.append(context_chunk)

        cases.append(case)

    # Create evaluation run
    settings = load_eval_settings()
    run = EvaluationRun(
        profile=profile,
        pass_id=f"pydantic_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        reranker={
            "enable": True,
            "model": settings.RERANKER_MODEL,
            "input_topk": settings.RERANKER_TOPK,
            "keep": settings.RERANKER_KEEP,
            "device": settings.RERANKER_DEVICE,
            "cache": bool(settings.RERANKER_CACHE),
        },
        started_at=datetime.now(),
        cases=cases,
    )

    return run


def export_evaluation_run(run: EvaluationRun, output_path: Path) -> None:
    """Export evaluation run using Pydantic serialization.

    This replaces json.dumps() calls with proper Pydantic serialization.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Use Pydantic's model_dump_json for proper serialization
    output_path.write_text(run.model_dump_json(indent=2, exclude_none=True, exclude={"n_cases"}), encoding="utf-8")


def load_evaluation_run(input_path: Path) -> EvaluationRun:
    """Load evaluation run using Pydantic validation.

    This replaces manual JSON parsing with proper Pydantic validation.
    """
    return EvaluationRun.model_validate_json(input_path.read_text())


def validate_retrieval_candidates(candidates_data: list[dict[str, Any]]) -> list[RetrievalCandidate]:
    """Validate retrieval candidates using TypeAdapter.

    This demonstrates how to use TypeAdapter for list validation
    to catch shape drift at boundaries.
    """
    from pydantic import TypeAdapter

    ta = TypeAdapter(list[RetrievalCandidate])
    return ta.validate_python(candidates_data)


# Example usage for existing evaluation runners
def example_integration():
    """Example showing how to integrate with existing evaluation runners."""

    # 1. Load legacy data (replace existing json.loads calls)
    legacy_data = [
        {
            "id": "test_case_1",
            "mode": "rag",
            "query": "What is the capital of France?",
            "predicted_answer": "Paris",
            "metrics": {"precision": 0.8, "recall": 0.7, "f1": 0.75},
            "timings": {"answer_latency_ms": 1500},
            "retrieval_snapshot": [{"doc_id": "doc1", "score": 0.9, "chunk": "Paris is the capital..."}],
        }
    ]

    # 2. Convert to new Pydantic models
    evaluation_run = create_evaluation_run_from_legacy_data(legacy_data, "test_profile")

    # 3. Export using Pydantic serialization
    output_path = Path("metrics/test_evaluation_run.json")
    export_evaluation_run(evaluation_run, output_path)

    # 4. Load back and validate
    loaded_run = load_evaluation_run(output_path)
    assert loaded_run.n_cases == 1
    assert loaded_run.cases[0].case_id == "test_case_1"

    print("✅ Successfully integrated Pydantic models")
    print(f"   Exported: {output_path}")
    print(f"   Cases: {loaded_run.n_cases}")


if __name__ == "__main__":
    example_integration()
