from __future__ import annotations
import argparse
import copy
import json
import os
import sys
from datetime import datetime
from typing import Any
from lessons_model import Lesson, filter_lessons, load_lessons
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Lessons Loader - Pre-run component to load relevant lessons and generate candidate configs
"""

def env_to_dict(env_path: str) -> dict[str, str]:
    """Load environment variables from .env file"""
    env_dict = {}
    if not os.path.exists(env_path):
        return env_dict

    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                # Handle both "KEY=value" and "export KEY=value" formats
                if line.startswith("export "):
                    key, value = line[7:].split("=", 1)  # Remove "export "
                else:
                    key, value = line.split("=", 1)
                env_dict[key] = value

    return env_dict

def dict_to_env(env_dict: dict[str, str], header: str | None = None) -> str:
    """Convert dictionary to .env file content"""
    lines = []
    if header:
        lines.append(f"# {header}")
        lines.append("")

    for key, value in env_dict.items():
        lines.append(f"{key}={value}")

    return "\n".join(lines)

def apply_changes(base_env: dict[str, str], changes: list[dict[str, Any]]) -> dict[str, str]:
    """Apply parameter changes to environment dictionary"""
    env = copy.deepcopy(base_env)

    for change in changes:
        key = change["key"]
        op = change["op"]
        value = change["value"]

        if key not in env and op != "set":
            continue

        if op == "set":
            # "set" can add new keys or modify existing ones
            env[key] = str(value)
        else:
            # "add" and "mul" require existing numeric values
            try:
                current = float(env[key])
                if op == "add":
                    env[key] = str(current + float(value))
                elif op == "mul":
                    env[key] = str(current * float(value))
            except ValueError:
                # Handle non-numeric values - only allow set
                if op == "set":
                    env[key] = str(value)

    return env

def _parse_effect(effect: Any) -> tuple[float | None, float | None, bool]:
    """Parse a predicted effect value into (min_delta, max_delta, is_percent).

    Supports strings like "+0.03~+0.06", "-0.02", "+10~15%". Returns None if unparsable.
    """
    if effect is None:
        return None, None, False
    is_percent = False
    try:
        # If already numeric, treat as symmetric delta
        if isinstance(effect, int | float):
            val = float(effect)
            return val, val, False

        s = str(effect).strip()
        if s.endswith("%"):
            is_percent = True
            s = s[:-1]
        if "~" in s:
            lo, hi = s.split("~", 2)
            lo = lo.strip().replace("%", "")
            hi = hi.strip().replace("%", "")
            return float(lo), float(hi), is_percent
        # single number
        return float(s), float(s), is_percent
    except Exception:
        return None, None, is_percent

def resolve_conflicts(lessons: list[Lesson]) -> list[Lesson]:
    """Resolve conflicts between lessons using deterministic rules"""

    # Sort by recency, then confidence, then evidence strength
    def sort_key(lesson: Lesson) -> tuple:
        # Parse date for recency
        try:
            date = datetime.fromisoformat(lesson.created_at.replace("Z", "+00:00"))
            recency_score = date.timestamp()
        except:
            recency_score = 0

        # Confidence score
        confidence_score = lesson.confidence

        # Evidence strength (simple heuristic)
        evidence_score = 0
        if "evidence" in lesson.finding:
            evidence = lesson.finding["evidence"]
            if "precision" in evidence and "recall" in evidence:
                # Higher effect size = stronger evidence
                effect_size = abs(evidence.get("precision", 0) - evidence.get("recall", 0))
                evidence_score = effect_size

        return (-recency_score, -confidence_score, -evidence_score)

    sorted_lessons = sorted(lessons, key=sort_key)

    # Simple conflict resolution: take the first (highest priority) lesson for each parameter
    applied_params = set()
    resolved_lessons = []

    for lesson in sorted_lessons:
        if lesson.status not in ("proposed", "applied"):
            continue

        # Check for parameter conflicts
        conflicts = False
        for change in lesson.recommendation.get("changes", []):
            param = change["key"]
            if param in applied_params:
                conflicts = True
                break

        if not conflicts:
            resolved_lessons.append(lesson)
            for change in lesson.recommendation.get("changes", []):
                applied_params.add(change["key"])

    return resolved_lessons

def generate_decision_docket(
    base_env_path: str,
    applied_lessons: list[Lesson],
    candidate_env: dict[str, str],
    base_env: dict[str, str],
    gate_warnings: list[str] | None = None,
    apply_blocked: bool = False,
) -> str:
    """Generate a decision docket markdown file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    docket = f"""# Decision Docket

**Generated**: {timestamp}
**Base Config**: `{os.path.basename(base_env_path)}`
**Applied Lessons**: {len(applied_lessons)}

## Summary

This candidate configuration was generated by applying {len(applied_lessons)} lessons learned from previous evaluation runs.

## Applied Lessons

"""

    for i, lesson in enumerate(applied_lessons, 1):
        docket += f"""### {i}. {lesson.id}

- **Pattern**: {lesson.finding.get('pattern', 'unknown')}
- **Confidence**: {lesson.confidence:.2f}
- **Rationale**: {lesson.recommendation.get('rationale', 'No rationale provided')}
- **Predicted Effects**: {lesson.recommendation.get('predicted_effect', {})}

"""

    # Quality gates summary (if any)
    if gate_warnings:
        docket += """## Quality Gates

"""
        if apply_blocked:
            docket += "⚠️ APPLY BLOCKED: Candidate changes conflict with quality gates.\n\n"
        docket += """### Warnings

"""
        for w in gate_warnings:
            docket += f"- {w}\n"
        docket += "\n"

    docket += """## Parameter Changes

| Parameter | From | To | Change |
|-----------|------|----|---------|
"""

    for key in sorted(candidate_env.keys()):
        if key in base_env and candidate_env[key] != base_env[key]:
            from_val = base_env[key]
            to_val = candidate_env[key]
            try:
                from_num = float(from_val)
                to_num = float(to_val)
                change = f"{to_num - from_num:+.3f}"
            except ValueError:
                change = "modified"

            docket += f"| {key} | {from_val} | {to_val} | {change} |\n"

    docket += """
## Usage

To use this candidate configuration:

```bash
# Advisory mode (recommended first)
python scripts/ragchecker_official_evaluation.py --lessons-mode advisory

# Apply mode (after review)
python scripts/ragchecker_official_evaluation.py --lessons-mode apply
```

## Notes

- This is an automatically generated configuration
- Review the predicted effects before applying
- Monitor performance after application
- Revert if quality gates are violated
"""

    return docket

def main(
    base_env_path: str,
    lessons_jsonl: str,
    mode: str = "advisory",
    scope_filters: dict[str, Any] | None = None,
    out_dir: str = "metrics/derived_configs",
    window_size: int = 5,
) -> dict[str, Any]:
    """Main loader function"""
    print(f"🧠 Loading lessons for {os.path.basename(base_env_path)}", file=sys.stderr)

    # Ensure output directory exists
    os.makedirs(out_dir, exist_ok=True)

    # Load base environment
    base_env = env_to_dict(base_env_path)
    if not base_env:
        raise ValueError(f"Could not load base environment from {base_env_path}")

    # Load and filter lessons
    all_lessons = load_lessons(lessons_jsonl)
    if scope_filters is None:
        scope_filters = {"level": "profile", "profile": "auto"}

    relevant_lessons = filter_lessons(all_lessons, scope_filters)
    print(f"📚 Found {len(relevant_lessons)} relevant lessons", file=sys.stderr)

    # Apply windowing (limit to most recent N lessons)
    if window_size > 0:
        # Sort by created_at and take the most recent
        sorted_lessons = sorted(relevant_lessons, key=lambda x: x.created_at, reverse=True)
        relevant_lessons = sorted_lessons[:window_size]
        print(f"🪟 Applied window of {window_size} lessons", file=sys.stderr)

    # Resolve conflicts
    resolved_lessons = resolve_conflicts(relevant_lessons)
    print(f"✅ Resolved to {len(resolved_lessons)} lessons after conflict resolution", file=sys.stderr)

    # Apply lessons to generate candidate
    candidate_env = dict(base_env)
    applied_lessons = []

    for lesson in resolved_lessons[:5]:  # Limit to top 5 lessons
        changes = lesson.recommendation.get("changes", [])
        candidate_env = apply_changes(candidate_env, changes)
        applied_lessons.append(lesson)

    # Check quality gates before applying (if in apply mode)
    _gate_violations: list[str] = []
    _apply_blocked = False
    if mode == "apply":
        quality_gates_path = "config/ragchecker_quality_gates.json"
        if os.path.exists(quality_gates_path):
            try:
                with open(quality_gates_path) as f:
                    quality_gates = json.load(f)

                # Conservative safety: block apply if predicted effects clearly move against gates
                violations: list[str] = []
                for lesson in applied_lessons:
                    predicted_effects = lesson.recommendation.get("predicted_effect", {})
                    for metric, effect in predicted_effects.items():
                        if metric not in quality_gates:
                            continue
                        gate = quality_gates[metric]
                        lo, hi, is_percent = _parse_effect(effect)
                        if lo is None or hi is None:
                            # Unable to parse; skip strict enforcement
                            continue
                        # Metrics with a minimum gate (e.g., precision/recall/f1/faithfulness):
                        # if worst-case predicts decrease (hi <= 0), block apply
                        if "min" in gate and hi <= 0:
                            violations.append(f"{metric}: predicted {effect} may reduce below minimum; block apply")
                        # Metrics with a maximum gate (e.g., latency): if any increase is predicted, block
                        if "max" in gate and hi > 0:
                            # If percent, be conservative and block on any positive increase
                            violations.append(
                                f"{metric}: predicted increase {effect} conflicts with max gate {gate['max']}"
                            )

                if violations:
                    _gate_violations = violations
                    _apply_blocked = True
                    print("❌ Quality gate violations detected:", file=sys.stderr)
                    for violation in violations:
                        print(f"  • {violation}", file=sys.stderr)
                    print("❌ Apply will be blocked; details added to decision docket", file=sys.stderr)

            except Exception as e:
                print(f"⚠️ Warning: Could not check quality gates: {e}", file=sys.stderr)

    # Generate output files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.splitext(os.path.basename(base_env_path))[0]

    candidate_path = os.path.join(out_dir, f"{timestamp}_{base_name}_candidate.env")
    docket_path = os.path.join(out_dir, f"{timestamp}_{base_name}_decision_docket.md")

    # Write candidate environment
    header = f"Derived from {os.path.basename(base_env_path)} @ {timestamp}"
    if applied_lessons:
        lesson_ids = [lesson.id for lesson in applied_lessons]
        header += f"\n# LESSONS_APPLIED={','.join(lesson_ids)}"
    candidate_content = dict_to_env(candidate_env, header)
    with open(candidate_path, "w") as f:
        f.write(candidate_content)

    # Write decision docket
    docket_content = generate_decision_docket(
        base_env_path,
        applied_lessons,
        candidate_env,
        base_env,
        gate_warnings=locals().get("_gate_violations", []),
        apply_blocked=locals().get("_apply_blocked", False),
    )
    with open(docket_path, "w") as f:
        f.write(docket_content)

    # Prepare result
    result = {
        "candidate_env": candidate_path,
        "decision_docket": docket_path,
        "applied_lessons": [lesson.id for lesson in applied_lessons],
        "mode": mode,
        "base_config": base_env_path,
        "apply_blocked": _apply_blocked,
        "gate_warnings": _gate_violations,
    }

    # Print logs to stderr, JSON result to stdout
    print(f"✅ Generated candidate config: {candidate_path}", file=sys.stderr)
    print(f"📋 Generated decision docket: {docket_path}", file=sys.stderr)
    print(f"🎯 Applied {len(applied_lessons)} lessons", file=sys.stderr)

    # If apply is blocked by gates, we still return JSON (runner will skip applying)
    if mode == "apply" and _apply_blocked:
        print(
            "❌ Apply blocked by quality gates (runner will keep base env); see decision docket",
            file=sys.stderr,
        )

    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load lessons and generate candidate configuration")
    parser.add_argument("base_env", help="Base environment file path")
    parser.add_argument("lessons_jsonl", help="Lessons JSONL file path")
    parser.add_argument(
        "--mode", choices=["advisory", "apply"], default="advisory", help="Mode: advisory (default) or apply"
    )
    parser.add_argument("--scope-level", default="profile", help="Scope level filter")
    parser.add_argument("--scope-profile", default="auto", help="Scope profile filter")
    parser.add_argument("--scope-dataset", default="auto", help="Scope dataset filter")
    parser.add_argument("--out-dir", default="metrics/derived_configs", help="Output directory for generated files")
    parser.add_argument("--window", type=int, default=5, help="Number of recent lessons to consider")

    args = parser.parse_args()

    scope_filters = {"level": args.scope_level}
    if args.scope_level == "profile":
        scope_filters["profile"] = args.scope_profile
    elif args.scope_level == "dataset":
        scope_filters["dataset"] = args.scope_dataset
    # global level doesn't need additional filters

    try:
        result = main(args.base_env, args.lessons_jsonl, args.mode, scope_filters, args.out_dir, args.window)
        # Print JSON to stdout, logs already went to stderr
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
