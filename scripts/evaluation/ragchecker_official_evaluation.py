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
            _: Any = config_loader.resolve_config(argv)
        except SystemExit as e:
            # Surface clear error for profile misuse
            print(e)
            return 1
    except Exception as e:
        print(f"Warning: Could not load config loader: {e}")
        # Keep going even if loader isn't available in this environment
        pass

    # Profile-dispatch path: if --profile is provided (or EVAL_PROFILE is set), route to profile runner.
    try:
        profile_arg = None
        if "--profile" in argv:
            i = argv.index("--profile")
            profile_arg = argv[i + 1] if i + 1 < len(argv) else None
        if profile_arg is None:
            profile_arg = os.environ.get("EVAL_PROFILE")
        if profile_arg:
            # Ensure repository root on sys.path for absolute imports
            repo_root = Path(__file__).resolve().parents[2]
            if str(repo_root) not in sys.path:
                sys.path.insert(0, str(repo_root))
            from scripts.evaluation.profiles import Profile
            from scripts.evaluation.profiles import gold as _gold
            from scripts.evaluation.profiles import mock as _mock
            from scripts.evaluation.profiles import real as _real

            registry: dict[str, Any] = {
                Profile.GOLD.value: _gold.RUNNER,
                Profile.REAL.value: _real.RUNNER,
                Profile.MOCK.value: _mock.RUNNER,
            }
            runner = registry.get(str(profile_arg).lower())
            if runner is None:
                print(f"Unknown profile: {profile_arg}. Valid: gold, real, mock")
                return 2
            return int(runner.run(argv))
    except Exception as e:
        print(f"Warning: profile dispatch failed, falling back to SSOT path ({e})")

    # When invoked by the SSOT runner, we receive an --outdir argument.
    # In that case, run the official evaluator inline and write results there.
    if "--outdir" in argv:
        outdir = None
        try:
            i: Any = argv.index("--outdir")
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

        # Use the DSPy evaluator (renamed from clean_dspy_evaluator)
        from scripts.evaluation.dspy_evaluator import CleanDSPyEvaluator

        # Use a permissive type to allow attribute access without incomplete stubs
        evaluator: Any = CleanDSPyEvaluator()

        # Run real evaluation with gold cases and DSPy RAG system
        try:
            # Run real evaluation with gold test cases
            results = evaluator.run_evaluation(
                gold_file="evals/data/gold/v1/gold_cases_121.jsonl",
                limit=5,  # Small test
            )
        except Exception as e:
            print(f"⚠️ Real evaluation failed ({e})")
            return 1

        # Write to requested outdir with the name the runner expects
        import json as _json
        import time as _time

        ts: Any = _time.strftime("%Y%m%d_%H%M%S")
        out_path = Path(outdir) / f"ragchecker_clean_evaluation_{ts}.json"
        os.makedirs(outdir, exist_ok=True)  # pylint: disable=unused-variable,no-value-for-parameter
        _ = out_path.write_text(_json.dumps(results, indent=2), encoding="utf-8")
        print(f"[wrapper] Wrote results → {out_path}")
        return 0

    print("❌ Profile dispatch failed and SSOT fallback is no longer available.")
    print("   The evaluation system now uses profile-based dispatch only.")
    print("   Available profiles: gold, real, mock")
    return 3


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
        # Underlying implementation instance, loaded lazily
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
