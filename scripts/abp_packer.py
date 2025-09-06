#!/usr/bin/env python3
"""
Agent Briefing Pack (ABP) Packer

Generates a concise pre-run briefing that combines:
- Constraints & targets (from Baseline Manifest if available; falls back to quality gates)
- Recent lessons (top-N by recency and confidence)
- Pattern cards from cross-run knowledge graph (if present)
- Decision docket reference (if provided)

Emits: metrics/briefings/<timestamp>_<profile>_ABP.md

Token budgeting is approximated via character budgeting (tokens ~= chars/4).
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# --- Data helpers ---


def _safe_load_json(path: str) -> Optional[Dict[str, Any]]:
    try:
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        return None
    return None


def _parse_lessons_jsonl(path: str) -> List[Dict[str, Any]]:
    lessons: List[Dict[str, Any]] = []
    if not path or not os.path.exists(path):
        return lessons
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                obj = json.loads(line)
                lessons.append(obj)
            except Exception:
                continue
    return lessons


def _parse_effect_value(effect: Any) -> Tuple[Optional[float], Optional[float]]:
    # Returns (min_delta, max_delta) if parsable, else (None, None)
    if effect is None:
        return None, None
    try:
        if isinstance(effect, (int, float)):
            v = float(effect)
            return v, v
        s = str(effect).strip().rstrip("%")
        if "~" in s:
            lo, hi = s.split("~", 1)
            return float(lo), float(hi)
        return float(s), float(s)
    except Exception:
        return None, None


def _lesson_score(lesson: Dict[str, Any]) -> float:
    # score = 0.5*recency + 0.3*confidence + 0.2*effect_size
    # Recency: use created_at timestamp if present
    recency = 0.0
    try:
        ts = lesson.get("created_at")
        if ts:
            # Normalize to seconds
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            recency = dt.timestamp()
    except Exception:
        recency = 0.0

    confidence = float(lesson.get("confidence", 0.0) or 0.0)

    # Effect size: sum absolute predicted deltas for key metrics if available
    effect_size = 0.0
    predicted = ((lesson.get("recommendation") or {}).get("predicted_effect")) or {}
    for m in ("f1", "precision", "recall"):
        lo, hi = _parse_effect_value(predicted.get(m))
        if lo is not None and hi is not None:
            effect_size += abs(lo) + abs(hi)

    # weights chosen to prioritize freshness then confidence
    return 0.5 * recency + 0.3 * confidence + 0.2 * effect_size


# --- ABP assembly ---


@dataclass
class ABPInputs:
    profile: str
    manifest: Optional[Dict[str, Any]]
    gates: Optional[Dict[str, Any]]
    lessons: List[Dict[str, Any]]
    pattern_cards: Optional[List[Dict[str, Any]]]
    decision_docket: Optional[str]
    token_budget: int


def _format_constraints(manifest: Optional[Dict[str, Any]], gates: Optional[Dict[str, Any]]) -> str:
    lines: List[str] = ["## Constraints & Targets"]
    if manifest:
        targets = manifest.get("targets", {})
        ema = manifest.get("ema", {})
        lines.append("- Targets: " + ", ".join(f"{k}={v}" for k, v in targets.items()))
        if ema:
            lines.append("- EMA: " + ", ".join(f"{k}={v}" for k, v in ema.items()))
    if gates:
        # Flatten min/max gates
        gparts: List[str] = []
        for k, v in gates.items():
            if isinstance(v, dict):
                if "min" in v:
                    gparts.append(f"{k}_min={v['min']}")
                if "max" in v:
                    gparts.append(f"{k}_max={v['max']}")
        if gparts:
            lines.append("- Gates: " + ", ".join(gparts))
    return "\n".join(lines) + "\n\n"


def _format_lessons(lessons: List[Dict[str, Any]], max_items: int = 8) -> str:
    if not lessons:
        return ""
    lines: List[str] = ["## Recent Lessons"]
    # Sort by score desc
    ranked = sorted(lessons, key=_lesson_score, reverse=True)[:max_items]
    for l in ranked:
        lid = l.get("id", "unknown")
        pat = ((l.get("finding") or {}).get("pattern")) or "unknown"
        conf = l.get("confidence", 0.0)
        pred = ((l.get("recommendation") or {}).get("predicted_effect")) or {}
        rationale = ((l.get("recommendation") or {}).get("rationale")) or ""
        lines.append(f"- {lid} | pattern={pat} | conf={conf:.2f} | effects={pred} | {rationale}")
    return "\n".join(lines) + "\n\n"


def _format_patterns(cards: Optional[List[Dict[str, Any]]], max_items: int = 6) -> str:
    if not cards:
        return ""
    lines: List[str] = ["## Pattern Cards"]
    for card in cards[:max_items]:
        summary = card.get("summary") or card.get("text") or json.dumps(card, ensure_ascii=False)[:240]
        lines.append(f"- {summary}")
    return "\n".join(lines) + "\n\n"


def build_abp(inputs: ABPInputs) -> str:
    header = [
        f"# Agent Briefing Pack — {inputs.profile}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]
    body = []
    body.append(_format_constraints(inputs.manifest, inputs.gates))
    body.append(_format_lessons(inputs.lessons))
    body.append(_format_patterns(inputs.pattern_cards))
    if inputs.decision_docket:
        body.append("## Decision Docket\n")
        body.append(f"- Path: `{inputs.decision_docket}`\n\n")

    text = "\n".join(header + body)

    # Approx token budget → char budget (~4 chars per token)
    max_chars = inputs.token_budget * 4
    if len(text) > max_chars:
        # Trim from the end; prioritize constraints and top lessons
        text = text[:max_chars] + "\n\n… (truncated to fit token budget)\n"
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Agent Briefing Pack (ABP)")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--lessons-jsonl", default="metrics/lessons/lessons.jsonl")
    parser.add_argument("--baseline-manifest", default=None)
    parser.add_argument("--gates", default="config/ragchecker_quality_gates.json")
    parser.add_argument("--pattern-cards", default="metrics/graphs/pattern_cards.json")
    parser.add_argument("--decision-docket", default=None)
    parser.add_argument("--token-budget", type=int, default=2500)
    parser.add_argument("--out-dir", default="metrics/briefings")

    args = parser.parse_args()

    # Resolve manifest default if not passed
    manifest_path = (
        args.baseline_manifest
        if args.baseline_manifest is not None
        else os.path.join("config", "baselines", f"{args.profile}.json")
    )

    manifest = _safe_load_json(manifest_path)
    gates = _safe_load_json(args.gates)
    lessons = _parse_lessons_jsonl(args.lessons_jsonl)

    pattern_cards = None
    cards_obj = _safe_load_json(args.pattern_cards)
    if isinstance(cards_obj, list):
        pattern_cards = cards_obj
    elif isinstance(cards_obj, dict) and "cards" in cards_obj:
        pattern_cards = cards_obj["cards"]

    os.makedirs(args.out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{ts}_{args.profile}_ABP.md"
    out_path = os.path.join(args.out_dir, fname)

    abp = build_abp(
        ABPInputs(
            profile=args.profile,
            manifest=manifest,
            gates=gates,
            lessons=lessons,
            pattern_cards=pattern_cards,
            decision_docket=args.decision_docket,
            token_budget=args.token_budget,
        )
    )

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(abp)

    # Print path to stdout for caller
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

