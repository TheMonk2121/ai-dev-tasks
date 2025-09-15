#!/usr/bin/env python3
"""
Compatibility wrapper that supports the new profile system and forwards
into the SSOT runner (evals_300.tools.run). It also preserves --help behavior
expected by tests and wrapper scripts.

Also exposes a minimal OfficialRAGCheckerEvaluator shim so other modules
can import a consistent symbol without depending on experiment paths.
"""

import os
import sys
from pathlib import Path
from typing import Any

# Setup observability if available
try:
    from scripts.monitoring.observability import get_logfire, init_observability

    logfire = get_logfire()
    try:
        _ = init_observability(service="ai-dev-tasks")
    except Exception:
        pass
except Exception:
    logfire = None


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if "--help" in argv or "-h" in argv:
        print("Usage: scripts/ragchecker_official_evaluation.py [--profile gold|mock] [args]")
        print("")
        print("Profiles:")
        print("  gold  - Real RAG + gold cases")
        print("  mock  - Infra-only, synthetic")
        return 0

    # Resolve profile and print banner if possible
    try:
        lib_path = Path("scripts/lib").resolve()
        if str(lib_path) not in sys.path:
            sys.path.insert(0, str(lib_path))
        import config_loader

        try:
            _ = config_loader.resolve_config(argv)
        except SystemExit as e:
            # Surface clear error for profile misuse
            print(e)
            return 1
    except Exception as e:
        print(f"Warning: Could not load config loader: {e}")
        # Keep going even if loader isn't available in this environment
        pass

    # When invoked by the SSOT runner, we receive an --outdir argument.
    # In that case, run the official evaluator inline and write results there.
    if "--outdir" in argv:
        outdir = None
        try:
            i = argv.index("--outdir")
            outdir = argv[i + 1] if i + 1 < len(argv) else None
        except Exception:
            outdir = None
        if not outdir:
            print("--outdir is required when invoking this wrapper from the runner")
            return 2

        # Ensure repository root on sys.path for 'scripts' absolute imports in impl
        repo_root = Path(__file__).resolve().parents[2]
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))

        # Use the clean DSPy evaluator
        from scripts.evaluation.clean_dspy_evaluator import CleanDSPyEvaluator

        evaluator = CleanDSPyEvaluator()

        # Run real evaluation with gold cases and DSPy RAG system
        try:
            # Run real evaluation with gold test cases
            results = evaluator.run_evaluation(
                gold_file="300_evals/data/gold/v1/gold_cases.jsonl", limit=5  # Small test
            )
        except Exception as e:
            print(f"⚠️ Real evaluation failed ({e})")
            return 1

        # Write to requested outdir with the name the runner expects
        import json as _json
        import time as _time

        ts = _time.strftime("%Y%m%d_%H%M%S")
        out_path = Path(outdir) / f"ragchecker_clean_evaluation_{ts}.json"
        os.makedirs(outdir, exist_ok=True)  # pylint: disable=unused-variable,no-value-for-parameter
        _ = out_path.write_text(_json.dumps(results, indent=2), encoding="utf-8")
        print(f"[wrapper] Wrote results → {out_path}")
        return 0

    print("[DEPRECATION] Use evals_300.tools.run; forwarding…")

    # Forward into SSOT runner programmatically (avoid CLI parsing conflicts) for standalone calls
    try:
        # Ensure repository root is on sys.path so 'evals_300' is importable
        repo_root = Path(__file__).resolve().parents[2]
        if str(repo_root) not in sys.path:
            sys.path.insert(0, str(repo_root))
        from .tools.run import run as ssot_run
    except Exception as e:
        print(f"Failed to import SSOT runner: {e}")
        return 3

    suite = os.environ.get("EVAL_SUITE", "300_core")
    pass_id = os.environ.get("EVAL_PASS", "reranker_ablation_suite")

    try:
        conc_env = os.environ.get("EVAL_CONCURRENCY")
        concurrency = int(conc_env) if conc_env else None
    except ValueError:
        concurrency = None

    _ = ssot_run(suite=suite, pass_id=pass_id, out=None, seed=None, concurrency=concurrency)
    return 0


# --- Minimal shims for compatibility ---
# Expose RAGCheckerInput for tests; prefer experiment definition, else fallback dataclass
try:
    _impl_path = Path("300_experiments/300_testing-scripts/ragchecker_official_evaluation.py").resolve()
    _impl_mod = (
        __import__("importlib.machinery", fromlist=["SourceFileLoader"])
        .SourceFileLoader("ragchecker_official_eval_impl", str(_impl_path))
        .load_module()
    )
    RAGCheckerInput = getattr(_impl_mod, "RAGCheckerInput")
except Exception:
    from dataclasses import dataclass

    @dataclass
    class RAGCheckerInput:  # type: ignore[no-redef]
        query_id: str
        query: str
        gt_answer: str
        response: str
        retrieved_context: list[str]


class OfficialRAGCheckerEvaluator:
    """Proxy to experiment implementation with broader interface forwarding used by tests."""

    def __init__(self) -> None:
        # Lazy-load implementation to avoid importing heavy deps during import-only tests
        self._impl: Any | None = None
        # Provide direct attribute expected by tests without loading impl
        self.metrics_dir: Path = Path("metrics/baseline_evaluations")

    def _ensure_impl(self) -> None:
        if self._impl is not None:
            return
        try:
            impl_path = Path("300_experiments/300_testing-scripts/ragchecker_official_evaluation.py").resolve()
            if not impl_path.exists():
                impl_path = Path("600_archives/600_deprecated/_ragchecker_eval_impl.py").resolve()
            module = (
                __import__("importlib.machinery", fromlist=["SourceFileLoader"])
                .SourceFileLoader("ragchecker_official_eval_impl", str(impl_path))
                .load_module()
            )
            self._impl = getattr(module, "OfficialRAGCheckerEvaluator")()
        except Exception as e:
            raise RuntimeError(f"Failed to load OfficialRAGCheckerEvaluator implementation: {e}")

    # Forward full interface used by tests; gracefully degrade if missing
    def create_official_test_cases(self) -> Any:  # noqa: D401
        self._ensure_impl()
        return self._impl.create_official_test_cases()  # type: ignore[union-attr]

    def create_fallback_evaluation(self, data: Any) -> Any:  # noqa: D401
        self._ensure_impl()
        return self._impl.create_fallback_evaluation(data)  # type: ignore[union-attr]

    def get_memory_system_response(self, *args: Any, **kwargs: Any) -> Any:
        self._ensure_impl()
        return self._impl.get_memory_system_response(*args, **kwargs)  # type: ignore[union-attr]

    def prepare_official_input_data(self, *args: Any, **kwargs: Any) -> Any:
        self._ensure_impl()
        return self._impl.prepare_official_input_data(*args, **kwargs)  # type: ignore[union-attr]

    def save_official_input_data(self, *args: Any, **kwargs: Any) -> Any:
        self._ensure_impl()
        return self._impl.save_official_input_data(*args, **kwargs)  # type: ignore[union-attr]

    def run_official_ragchecker_cli(self, *args: Any, **kwargs: Any) -> Any:
        self._ensure_impl()
        return self._impl.run_official_ragchecker_cli(*args, **kwargs)  # type: ignore[union-attr]

    def run_official_evaluation(self, *args: Any, **kwargs: Any) -> Any:
        self._ensure_impl()
        return self._impl.run_official_evaluation(*args, **kwargs)  # type: ignore[union-attr]


if __name__ == "__main__":
    sys.exit(main())
