#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from src.schemas.eval import CaseResult, EvaluationRun


def main() -> None:
    out_dir = Path("schemas")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "case_result.schema.json").write_text(CaseResult.model_json_schema_json(indent=2))
    (out_dir / "evaluation_run.schema.json").write_text(EvaluationRun.model_json_schema_json(indent=2))
    print(f"✅ Wrote schemas to {out_dir}")


if __name__ == "__main__":
    main()
