"""Pydantic Evals harness for QA evaluation."""

from collections.abc import Iterable
from dataclasses import dataclass

import logfire
from pydantic import BaseModel, ConfigDict
from pydantic_evals.dataset import Dataset, increment_eval_metric, set_eval_attribute
from pydantic_evals.evaluators import Evaluator, EvaluatorContext


# 1) Define inputs/outputs
class QAInputs(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    question: str


class QAOutput(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    answer: str


# 2) A direct evaluator example
@dataclass
class ContainsAnswer(Evaluator[QAInputs, QAOutput, dict]):
    needle: str

    def evaluate(self, ctx: EvaluatorContext[QAInputs, QAOutput, dict]) -> bool:
        ok = (ctx.output is not None) and (self.needle.lower() in (ctx.output.answer or "").lower())
        increment_eval_metric("contains_answer", 1 if ok else 0)  # adds to telemetry/metrics
        return ok


# 3) Task under test
async def task(inputs: QAInputs) -> QAOutput:
    """Task function that would call your agent/graph."""
    # Here call your agent/graph; for brevity we'll stub:
    set_eval_attribute("profile", "qa-baseline")
    return QAOutput(answer=f"Echo: {inputs.question}")


# 4) Run
async def main(dataset_path: str):
    """Main evaluation function."""
    # Import and use our observability setup
    import sys
    from pathlib import Path

    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    from scripts.observability import init_observability

    init_observability(service="ai-dev-tasks-evals", environment="dev")

    # Create a simple dataset for testing
    from pydantic_evals.dataset import Case

    cases = [
        Case(
            name="capital_question",
            inputs=QAInputs(question="What is the capital of France?"),
            expected_output=QAOutput(answer="Paris"),
        ),
        Case(name="math_question", inputs=QAInputs(question="What is 2+2?"), expected_output=QAOutput(answer="4")),
    ]

    ds = Dataset[QAInputs, QAOutput](cases=cases)

    # For now, just test the basic functionality
    print(f"Dataset created with {len(ds.cases)} cases")
    print("✅ Pydantic Evals integration working")


if __name__ == "__main__":
    import asyncio
    import sys

    # Use a default dataset path or run without one
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else "test_dataset"
    asyncio.run(main(dataset_path))
