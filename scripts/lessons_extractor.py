#!/usr/bin/env python3
"""
Lessons Extractor - Post-run analysis to extract lessons from evaluation artifacts
"""

import json
import os
import sys
from typing import Any

from lessons_model import Lesson, append_lesson, new_lesson


def load_run_metrics(run_json_path: str) -> dict[str, Any]:
    """Load metrics from a run JSON file"""
    with open(run_json_path) as f:
        return json.load(f)


def load_progress_jsonl(progress_jsonl_path: str) -> list[dict[str, Any]]:
    """Load per-case results from progress JSONL"""
    cases = []
    if not os.path.exists(progress_jsonl_path):
        return cases

    with open(progress_jsonl_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                try:
                    cases.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return cases


def analyze_failure_modes(run_metrics: dict[str, Any], cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Analyze failure modes from run metrics and case results"""
    failure_modes = []

    if not run_metrics or "overall_metrics" not in run_metrics:
        return failure_modes

    metrics = run_metrics["overall_metrics"]
    precision = metrics.get("precision", 0)
    recall = metrics.get("recall", 0)
    f1 = metrics.get("f1_score", metrics.get("f1", 0))  # Handle both f1_score and f1

    # Rule 1: High precision / Low recall
    if precision >= 0.78 and recall <= 0.20:
        failure_modes.append(
            {
                "pattern": "high_precision_low_recall",
                "severity": "high" if recall <= 0.15 else "medium",
                "evidence": {"precision": precision, "recall": recall, "f1": f1, "gap": precision - recall},
            }
        )

    # Rule 2: Low precision / Good recall
    elif precision <= 0.60 and recall >= 0.40:
        failure_modes.append(
            {
                "pattern": "low_precision_good_recall",
                "severity": "high" if precision <= 0.50 else "medium",
                "evidence": {"precision": precision, "recall": recall, "f1": f1, "gap": recall - precision},
            }
        )

    # Rule 3: Balanced but low F1
    elif f1 <= 0.30 and abs(precision - recall) <= 0.15:
        failure_modes.append(
            {
                "pattern": "balanced_low_f1",
                "severity": "high" if f1 <= 0.25 else "medium",
                "evidence": {"precision": precision, "recall": recall, "f1": f1},
            }
        )

    # Analyze case-level patterns
    if cases:
        case_analysis = analyze_case_patterns(cases)
        failure_modes.extend(case_analysis)

    return failure_modes


def analyze_case_patterns(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Analyze patterns in individual case results"""
    patterns = []

    # Count different failure types with safe defaults
    no_answer_found = sum(1 for case in cases if case.get("answer_found", True) == False)
    low_evidence_score = sum(1 for case in cases if case.get("evidence_score", 1.0) < 0.3)
    high_retrieval_count = sum(1 for case in cases if case.get("retrieval_count", 0) > 20)

    total_cases = len(cases)

    # Pattern: Many cases with no answer found
    if no_answer_found / total_cases > 0.4:
        patterns.append(
            {
                "pattern": "high_no_answer_rate",
                "severity": "high",
                "evidence": {"no_answer_rate": no_answer_found / total_cases, "total_cases": total_cases},
            }
        )

    # Pattern: Low evidence scores
    if low_evidence_score / total_cases > 0.3:
        patterns.append(
            {
                "pattern": "low_evidence_scores",
                "severity": "medium",
                "evidence": {"low_evidence_rate": low_evidence_score / total_cases, "total_cases": total_cases},
            }
        )

    return patterns


def generate_lessons(failure_modes: list[dict[str, Any]], run_metrics: dict[str, Any]) -> list[Lesson]:
    """Generate lessons from failure mode analysis"""
    lessons = []

    if not run_metrics:
        return lessons

    run_config = run_metrics.get("run_config", {})
    scope = {
        "level": "profile",
        "profile": run_config.get("PROFILE_NAME", "unknown"),
        "dataset": run_config.get("DATASET", "ragchecker_v2"),
    }

    context = {
        "model_signature": run_config.get("MODEL_SIGNATURE", "unknown"),
        "data_signature": run_metrics.get("data_signature", "unknown"),
        "objective": run_config.get("OBJECTIVE", "f1"),
        "run_id": run_metrics.get("run_id", "unknown"),
        "artifacts": [
            run_metrics.get("run_json_path", ""),
            run_metrics.get("progress_jsonl_path", ""),
        ],
    }

    for failure_mode in failure_modes:
        pattern = failure_mode["pattern"]
        evidence = failure_mode["evidence"]
        severity = failure_mode["severity"]

        if pattern == "high_precision_low_recall":
            recommendation = {
                "type": "param_adjustment",
                "changes": [
                    {"key": "RETRIEVAL_TOP_K", "op": "add", "value": 2},
                    {"key": "RERANK_TOP_K", "op": "add", "value": 5},
                    {"key": "BM25_ANCHOR_BOOST", "op": "mul", "value": 0.9},
                ],
                "predicted_effect": {"recall": "+0.03~+0.06", "precision": "-0.01~0", "latency": "+10~15%"},
                "rationale": "Increase retrieval candidates; rely on reranking for precision; slightly relax lexical anchor boost",
            }
            confidence = 0.7 if severity == "high" else 0.5

        elif pattern == "low_precision_good_recall":
            recommendation = {
                "type": "param_adjustment",
                "changes": [
                    {"key": "RETRIEVAL_TOP_K", "op": "add", "value": -1},
                    {"key": "RERANK_TOP_K", "op": "add", "value": 3},
                    {"key": "CE_WEIGHT", "op": "mul", "value": 1.1},
                ],
                "predicted_effect": {"precision": "+0.02~+0.04", "recall": "-0.01~-0.02", "latency": "+5~8%"},
                "rationale": "Reduce retrieval noise; increase reranking precision; boost cross-encoder weight",
            }
            confidence = 0.6 if severity == "high" else 0.4

        elif pattern == "balanced_low_f1":
            recommendation = {
                "type": "param_adjustment",
                "changes": [
                    {"key": "RAGCHECKER_EVIDENCE_KEEP_PERCENTILE", "op": "add", "value": -5},
                    {"key": "RAGCHECKER_WEIGHT_JACCARD", "op": "mul", "value": 1.05},
                ],
                "predicted_effect": {"f1": "+0.02~+0.04", "precision": "+0.01~+0.02", "recall": "+0.01~+0.02"},
                "rationale": "Lower evidence threshold; boost Jaccard similarity weight for better matching",
            }
            confidence = 0.5

        elif pattern == "high_no_answer_rate":
            recommendation = {
                "type": "param_adjustment",
                "changes": [
                    {"key": "RETRIEVAL_TOP_K", "op": "add", "value": 3},
                    {"key": "RAGCHECKER_EVIDENCE_KEEP_PERCENTILE", "op": "add", "value": -10},
                ],
                "predicted_effect": {"recall": "+0.05~+0.08", "precision": "-0.02~-0.03"},
                "rationale": "Increase retrieval breadth and lower evidence threshold to catch more answers",
            }
            confidence = 0.6

        else:
            continue  # Skip unknown patterns

        finding = {"pattern": pattern, "evidence": evidence, "severity": severity}

        lesson = new_lesson(
            scope=scope,
            context=context,
            finding=finding,
            recommendation=recommendation,
            confidence=confidence,
            notes=f"Auto-generated from {pattern} analysis",
        )

        lessons.append(lesson)

    return lessons


def main(run_json_path: str, progress_jsonl_path: str = None, out_jsonl: str = "metrics/lessons/lessons.jsonl") -> None:
    """Main extraction function"""
    print(f"🧠 Extracting lessons from {run_json_path}")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(out_jsonl), exist_ok=True)

    # Load run data
    run_metrics = load_run_metrics(run_json_path)
    # Attach artifact paths for downstream context
    try:
        run_metrics["run_json_path"] = run_json_path
        if progress_jsonl_path:
            run_metrics["progress_jsonl_path"] = progress_jsonl_path
    except Exception:
        pass
    cases = []
    if progress_jsonl_path and os.path.exists(progress_jsonl_path):
        cases = load_progress_jsonl(progress_jsonl_path)

    # Analyze failure modes
    failure_modes = analyze_failure_modes(run_metrics, cases)
    print(f"📊 Found {len(failure_modes)} failure modes")

    # Generate lessons
    lessons = generate_lessons(failure_modes, run_metrics)
    print(f"💡 Generated {len(lessons)} lessons")

    # Write lessons
    for lesson in lessons:
        append_lesson(out_jsonl, lesson)
        print(f"✅ Saved lesson: {lesson.id} ({lesson.finding['pattern']})")

    # TODO: Also write to episodic store via existing utility
    print(f"📝 Lessons written to {out_jsonl}")

    # --- CRKG (Cross-Run Knowledge Graph) lightweight update ---
    try:
        os.makedirs("metrics/graphs", exist_ok=True)
        crkg_path = os.path.join("metrics", "graphs", "crkg.json")
        pattern_cards_path = os.path.join("metrics", "graphs", "pattern_cards.json")

        # Load existing graph
        crkg = {}
        if os.path.exists(crkg_path):
            try:
                with open(crkg_path, encoding="utf-8") as f:
                    crkg = json.load(f)
            except Exception:
                crkg = {}

        nodes = crkg.get("nodes", [])
        edges = crkg.get("edges", [])

        def _add_node(ntype: str, nid: str, **attrs):
            node_id = f"{ntype}:{nid}"
            if not any(n.get("id") == node_id for n in nodes):
                node = {"id": node_id, "type": ntype}
                node.update(attrs)
                nodes.append(node)
            return node_id

        def _add_edge(src: str, dst: str, etype: str, **attrs):
            edge = {"source": src, "target": dst, "type": etype}
            edge.update(attrs)
            edges.append(edge)

        # Run node and observed metrics
        run_id = run_metrics.get("run_id") or os.path.basename(run_json_path)
        run_node = _add_node("run", str(run_id))
        overall = run_metrics.get("overall_metrics", {})
        for m_key in ("precision", "recall", "f1_score", "f1", "latency_ms"):
            if m_key in overall:
                metric_name = "f1" if m_key in ("f1_score",) else m_key
                mnode = _add_node("metric", metric_name)
                _add_edge(run_node, mnode, "observed", value=overall.get(m_key))

        # Lessons: link param changes and predicted effects
        for l in lessons:
            lnode = _add_node("lesson", l.id, pattern=l.finding.get("pattern"), confidence=l.confidence)
            # Link lesson to params changed
            for ch in l.recommendation.get("changes", []):
                p = ch.get("key")
                if not p:
                    continue
                pnode = _add_node("param", p)
                _add_edge(lnode, pnode, "changes", op=ch.get("op"), value=ch.get("value"))

            # Link predicted metric effects
            predicted = l.recommendation.get("predicted_effect", {}) or {}
            for metric, effect in predicted.items():
                mnode = _add_node("metric", metric)
                # Try to parse range for direction
                sign = None
                try:
                    s = str(effect).strip().rstrip("%")
                    lo, hi = (None, None)
                    if "~" in s:
                        lo_s, hi_s = s.split("~", 1)
                        lo, hi = float(lo_s), float(hi_s)
                    else:
                        v = float(s)
                        lo, hi = v, v
                    if lo is not None and hi is not None:
                        if hi > 0 and lo >= 0:
                            sign = "+"
                        elif hi < 0 and lo <= 0:
                            sign = "-"
                        else:
                            sign = "±"
                except Exception:
                    pass
                _add_edge(lnode, mnode, "predicts", effect=str(effect), direction=sign)

            # Supersedes/conflicts metadata
            for sup in l.supersedes:
                _add_edge(lnode, f"lesson:{sup}", "supersedes")
            for con in getattr(l, "conflicts_with", []) or []:
                _add_edge(lnode, f"lesson:{con}", "conflicts")

        # Persist CRKG
        with open(crkg_path, "w", encoding="utf-8") as f:
            json.dump({"nodes": nodes, "edges": edges}, f, indent=2)
        print(f"🧩 CRKG updated: {crkg_path}")

        # Simple pattern cards: summarize recent lessons' changes → predicted effects
        cards: list[dict[str, Any]] = []
        for l in lessons:
            changes = (
                ", ".join(f"{c.get('key')} {c.get('op')} {c.get('value')}" for c in l.recommendation.get("changes", []))
                or "(no param changes)"
            )
            effects = l.recommendation.get("predicted_effect", {}) or {}
            scope = (
                l.scope.level
                if hasattr(l.scope, "level")
                else (l.scope.get("level") if isinstance(l.scope, dict) else "")
            )
            summary = (
                f"Pattern {l.finding.get('pattern','?')} → {changes}; predicted: {effects}; "
                f"scope={scope}; conf={l.confidence:.2f}"
            )
            cards.append({"lesson_id": l.id, "summary": summary})

        # Merge with existing cards (keep last 100)
        existing_cards = []
        if os.path.exists(pattern_cards_path):
            try:
                with open(pattern_cards_path, encoding="utf-8") as f:
                    obj = json.load(f)
                    if isinstance(obj, dict) and "cards" in obj:
                        existing_cards = obj["cards"]
                    elif isinstance(obj, list):
                        existing_cards = obj
            except Exception:
                existing_cards = []

        merged = (existing_cards + cards)[-100:]
        with open(pattern_cards_path, "w", encoding="utf-8") as f:
            json.dump({"cards": merged}, f, indent=2)
        print(f"🃏 Pattern cards updated: {pattern_cards_path}")
    except Exception as e:
        print(f"⚠️ CRKG update skipped: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python lessons_extractor.py <run_json_path> [progress_jsonl_path] [out_jsonl]")
        sys.exit(1)

    run_json = sys.argv[1]
    progress_jsonl = sys.argv[2] if len(sys.argv) > 2 else None
    out_jsonl = sys.argv[3] if len(sys.argv) > 3 else "metrics/lessons/lessons.jsonl"

    main(run_json, progress_jsonl, out_jsonl)
