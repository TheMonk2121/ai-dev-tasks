from __future__ import annotations

"""Shared helpers for production evaluation passes.

This module centralises the configuration and execution logic for production
RAGChecker evaluations so both CLI scripts and notebooks can reuse the same
behaviour. All functions are designed with type hints and minimal side effects
so they can be consumed in environments that need dry runs or custom logging.
"""

import hashlib
import json
import os
import subprocess
import sys
import time
from collections.abc import Callable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path


def _append_manifest(entry: Mapping[str, object], *paths: Path | None) -> None:
    for path in paths:
        if path is None:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")


def _resolve_git_sha() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        return "unknown"


def _dataset_hash(path: Path) -> str:
    try:
        digest = hashlib.md5()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except Exception:
        return "unknown"

DEFAULT_CASES_FILE = "evals/legacy/test_cases.json"
DEFAULT_RESULTS_DIR = Path("metrics/production_evaluations")


def _collect_pass_provenance(
    *,
    run_id: str | None,
    pass_config: EvaluationPassConfig,
    env: Mapping[str, str],
    output_file: Path,
    artifacts_dir: Path,
    duration: float | None,
    return_code: int | None,
    project_root: Path,
    error: str | None,
) -> dict[str, object]:
    provider = env.get("EVAL_PROVIDER") or os.getenv("EVAL_PROVIDER")
    model = env.get("DSPY_MODEL") or os.getenv("DSPY_MODEL")
    reranker_model = env.get("RERANKER_MODEL") or os.getenv("RERANKER_MODEL")
    seed = (
        env.get("SEED")
        or env.get("EVAL_SEED")
        or env.get("FEW_SHOT_SEED")
        or os.getenv("SEED")
        or os.getenv("EVAL_SEED")
        or os.getenv("FEW_SHOT_SEED")
    )
    profile = env.get("EVAL_PROFILE") or os.getenv("EVAL_PROFILE")

    dataset_path = Path(pass_config.cases_file)
    if not dataset_path.is_absolute():
        dataset_path = (project_root / dataset_path).resolve()
    dataset_hash = _dataset_hash(dataset_path) if dataset_path.exists() else "unknown"

    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "run_id": run_id or "unknown",
        "git_sha": _resolve_git_sha(),
        "pass_name": pass_config.name,
        "profile": profile,
        "provider": provider,
        "model": model,
        "reranker_model": reranker_model,
        "seed": seed,
        "cases_file": str(dataset_path),
        "dataset_hash": dataset_hash,
        "env_overrides": dict(pass_config.env),
        "output_file": str(output_file),
        "artifacts_dir": str(artifacts_dir),
        "duration_seconds": duration,
        "return_code": return_code,
        "error": error,
    }


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
    run_id: str
    run_dir: Path
    manifest_path: Path


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
    run_id: str | None = None,
    run_manifest_path: Path | None = None,
    global_manifest_path: Path | None = None,
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
    logger(f"\n🔄 Running {pass_config.name}")
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

        provenance = _collect_pass_provenance(
            run_id=run_id,
            pass_config=pass_config,
            env=env,
            output_file=output_file,
            artifacts_dir=artifacts_dir,
            duration=duration,
            return_code=result.returncode,
            project_root=project_root,
            error=None,
        )

        payload: dict[str, object] = {
            "pass_name": pass_config.name,
            "config": dict(pass_config.env),
            "eval_time_seconds": duration,
            "return_code": result.returncode,
            "stdout": stdout,
            "stderr": stderr,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "provenance": provenance,
        }

        output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        _append_manifest(provenance, run_manifest_path, global_manifest_path)

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
        provenance = _collect_pass_provenance(
            run_id=run_id,
            pass_config=pass_config,
            env=env,
            output_file=output_file,
            artifacts_dir=artifacts_dir,
            duration=duration,
            return_code=None,
            project_root=project_root,
            error=str(exc),
        )

        payload = {
            "pass_name": pass_config.name,
            "config": dict(pass_config.env),
            "error": str(exc),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "provenance": provenance,
        }
        output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        _append_manifest(provenance, run_manifest_path, global_manifest_path)

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


def analyse_pass_results(
    results: Sequence[EvaluationPassResult],
    *,
    run_id: str,
    run_dir: Path,
    manifest_path: Path,
) -> ProductionEvaluationSummary:
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
        run_id=run_id,
        run_dir=run_dir,
        manifest_path=manifest_path,
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
    run_id: str | None = None,
    global_manifest_path: Path | None = None,
) -> ProductionEvaluationSummary:
    """Run all configured production evaluation passes and return a summary."""

    passes_to_run = list(passes or default_production_passes())
    root_results_dir = Path(results_dir) if results_dir else DEFAULT_RESULTS_DIR
    root_results_dir.mkdir(parents=True, exist_ok=True)

    resolved_run_id = run_id or time.strftime("%Y%m%d_%H%M%S")
    run_dir = root_results_dir / resolved_run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    run_manifest_path = run_dir / "run_manifest.jsonl"
    manifest_path = global_manifest_path or (root_results_dir / "manifest.jsonl")

    results: list[EvaluationPassResult] = []

    for pass_config in passes_to_run:
        result = run_evaluation_pass(
            pass_config,
            project_root=project_root,
            results_dir=run_dir,
            execute=execute,
            capture_output=capture_output,
            logger=logger,
            base_env=base_env,
            run_id=resolved_run_id,
            run_manifest_path=run_manifest_path,
            global_manifest_path=manifest_path,
        )
        results.append(result)

    return analyse_pass_results(
        results,
        run_id=resolved_run_id,
        run_dir=run_dir,
        manifest_path=manifest_path,
    )


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
