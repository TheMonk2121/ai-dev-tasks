from __future__ import annotations

"""Shared helpers for production evaluation passes.

This module centralises the configuration and execution logic for production
RAGChecker evaluations so both CLI scripts and notebooks can reuse the same
behaviour. All functions are designed with type hints and minimal side effects
so they can be consumed in environments that need dry runs or custom logging.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Callable, Mapping, MutableMapping, Sequence

DEFAULT_CASES_FILE = "evals/legacy/test_cases.json"
DEFAULT_RESULTS_DIR = Path("metrics/production_evaluations")


@dataclass(slots=True)
class EvaluationPassConfig:
    """Configuration for an individual evaluation pass."""

    name: str
    description: str
    env: Mapping[str, str]
    cases_file: str = DEFAULT_CASES_FILE
    extra_args: Sequence[str] = field(default_factory=tuple)


@dataclass(slots=True)
class EvaluationPassResult:
    """Result metadata for an executed evaluation pass."""

    config: EvaluationPassConfig
    output_file: Path
    return_code: int | None
    stdout: str | None
    stderr: str | None
    duration_seconds: float | None
    error: str | None
    payload: dict[str, object] | None
    executed: bool

    @property
    def succeeded(self) -> bool:
        return self.executed and self.return_code == 0 and self.error is None


@dataclass(slots=True)
class ProductionEvaluationSummary:
    """Aggregate summary for a set of evaluation passes."""

    results: Sequence[EvaluationPassResult]
    successful_passes: int
    failed_passes: int
    skipped_passes: int
    total_passes: int
    overall_status: str


def default_production_passes() -> tuple[EvaluationPassConfig, ...]:
    """Return the canonical set of production evaluation passes."""

    return (
        EvaluationPassConfig(
            name="Retrieval-Only Baseline",
            description="Confirms retrieval, rerank, and chunk config (450/10%/J=0.8/prefix-A)",
            env={
                "FEW_SHOT_K": "0",
                "EVAL_COT": "0",
                "TEMPERATURE": "0",
                "EVAL_DISABLE_CACHE": "1",
                "DSPY_TELEPROMPT_CACHE": "false",
            },
        ),
        EvaluationPassConfig(
            name="Deterministic Few-Shot",
            description="Records prompt_audit.few_shot_ids, prompt_hash, cot_enabled=false",
            env={
                "FEW_SHOT_K": "5",
                "FEW_SHOT_SELECTOR": "knn",
                "FEW_SHOT_SEED": "42",
                "EVAL_COT": "0",
                "EVAL_DISABLE_CACHE": "1",
                "DSPY_TELEPROMPT_CACHE": "false",
            },
        ),
    )


def run_evaluation_pass(
    pass_config: EvaluationPassConfig,
    *,
    project_root: Path,
    results_dir: Path | None = None,
    execute: bool = True,
    capture_output: bool = True,
    logger: Callable[[str], None] | None = None,
    base_env: Mapping[str, str] | None = None,
) -> EvaluationPassResult:
    """Execute a single evaluation pass.

    Parameters
    ----------
    pass_config:
        The configuration describing the pass to run.
    project_root:
        Repository root used as working directory for subprocess execution.
    results_dir:
        Directory where per-pass JSON results should be written. Defaults to
        ``metrics/production_evaluations`` relative to ``project_root``.
    execute:
        When ``False`` the function performs a dry run and returns metadata
        without spawning the subprocess.
    capture_output:
        Controls whether stdout/stderr are captured. When ``False`` the child
        process inherits the current stdout/stderr streams.
    logger:
        Optional callable used for progress logging. Receives plain text lines.
    base_env:
        Base environment variables to clone before applying pass overrides.

    Returns
    -------
    EvaluationPassResult
        Metadata describing the execution outcome (or dry-run details).
    """

    if logger is None:
        def _noop(_: str) -> None:
            return

        logger = _noop

    resolved_results_dir = results_dir or DEFAULT_RESULTS_DIR
    resolved_results_dir.mkdir(parents=True, exist_ok=True)

    safe_pass_name = pass_config.name.lower().replace(" ", "_")
    output_file = resolved_results_dir / f"pass_{safe_pass_name}.json"
    artifacts_dir = resolved_results_dir / f"pass_{safe_pass_name}_artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    logger("\n🔄 Running %s" % pass_config.name)
    logger("=" * 60)
    logger(pass_config.description)

    env: MutableMapping[str, str] = dict(base_env or {})
    env.update({key: str(value) for key, value in pass_config.env.items()})

    for key, value in pass_config.env.items():
        logger(f"   {key}={value}")

    if not execute:
        logger("   (dry-run) skipping execution")
        return EvaluationPassResult(
            config=pass_config,
            output_file=output_file,
            return_code=None,
            stdout=None,
            stderr=None,
            duration_seconds=None,
            error=None,
            payload={"dry_run": True, "config": dict(pass_config.env)},
            executed=False,
        )

    args = [
        sys.executable,
        "scripts/ragchecker_official_evaluation.py",
        "--cases",
        pass_config.cases_file,
        "--outdir",
        str(artifacts_dir),
        "--use-bedrock",
        "--bypass-cli",
        *pass_config.extra_args,
    ]

    start_time = time.time()
    try:
        result = subprocess.run(
            args,
            cwd=project_root,
            check=False,
            capture_output=capture_output,
            text=True,
            env=env,
        )
        duration = time.time() - start_time

        stdout = result.stdout if capture_output else None
        stderr = result.stderr if capture_output else None

        if capture_output:
            logger(f"Return code: {result.returncode}")

        payload: dict[str, object] = {
            "pass_name": pass_config.name,
            "config": dict(pass_config.env),
            "eval_time_seconds": duration,
            "return_code": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        return EvaluationPassResult(
            config=pass_config,
            output_file=output_file,
            return_code=result.returncode,
            stdout=stdout,
            stderr=stderr,
            duration_seconds=duration,
            error=None,
            payload=payload,
            executed=True,
        )
    except Exception as exc:  # pragma: no cover - subprocess failures
        duration = time.time() - start_time
        logger(f"❌ {pass_config.name} failed: {exc}")
        payload = {
            "pass_name": pass_config.name,
            "config": dict(pass_config.env),
            "error": str(exc),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

        return EvaluationPassResult(
            config=pass_config,
            output_file=output_file,
            return_code=None,
            stdout=None,
            stderr=None,
            duration_seconds=duration,
            error=str(exc),
            payload=payload,
            executed=True,
        )


def analyse_pass_results(results: Sequence[EvaluationPassResult]) -> ProductionEvaluationSummary:
    """Compute aggregate summary data for evaluation pass results."""

    successful = sum(1 for result in results if result.succeeded)
    failed = sum(1 for result in results if result.executed and not result.succeeded)
    skipped = sum(1 for result in results if not result.executed)

    if failed == 0 and successful > 0 and skipped == 0:
        overall = "success"
    elif failed == 0 and successful == 0 and skipped > 0:
        overall = "dry-run"
    elif failed == 0 and skipped > 0:
        overall = "partial"
    elif successful == 0:
        overall = "failed"
    else:
        overall = "partial"

    return ProductionEvaluationSummary(
        results=results,
        successful_passes=successful,
        failed_passes=failed,
        skipped_passes=skipped,
        total_passes=len(results),
        overall_status=overall,
    )


def run_production_evaluation(
    passes: Sequence[EvaluationPassConfig] | None = None,
    *,
    project_root: Path,
    results_dir: Path | None = None,
    execute: bool = True,
    capture_output: bool = True,
    logger: Callable[[str], None] | None = None,
    base_env: Mapping[str, str] | None = None,
) -> ProductionEvaluationSummary:
    """Run all configured production evaluation passes and return a summary."""

    passes_to_run = list(passes or default_production_passes())
    results: list[EvaluationPassResult] = []

    for pass_config in passes_to_run:
        result = run_evaluation_pass(
            pass_config,
            project_root=project_root,
            results_dir=results_dir,
            execute=execute,
            capture_output=capture_output,
            logger=logger,
            base_env=base_env,
        )
        results.append(result)

    return analyse_pass_results(results)


DEFAULT_PRODUCTION_PASSES = default_production_passes()

__all__ = [
    "DEFAULT_CASES_FILE",
    "DEFAULT_PRODUCTION_PASSES",
    "DEFAULT_RESULTS_DIR",
    "EvaluationPassConfig",
    "EvaluationPassResult",
    "ProductionEvaluationSummary",
    "analyse_pass_results",
    "default_production_passes",
    "run_evaluation_pass",
    "run_production_evaluation",
]
