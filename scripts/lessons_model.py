#!/usr/bin/env python3
"""
Lessons Model - Data structures and utilities for the Closed-Loop Lessons Engine (CLLE)
"""

import json
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone, UTC
from typing import Any, Dict, List, Optional


@dataclass
class ParamChange:
    """Represents a parameter change operation"""

    key: str  # e.g., "RETRIEVAL_TOP_K"
    op: str  # "add"|"mul"|"set"
    value: float  # numeric or string; keep float for simplicity


@dataclass
class Lesson:
    """A lesson learned from an evaluation run"""

    id: str
    created_at: str
    scope: dict[str, Any]
    context: dict[str, Any]
    finding: dict[str, Any]
    recommendation: dict[str, Any]
    confidence: float
    status: str = "proposed"
    conflicts_with: list[str] = None
    supersedes: list[str] = None
    notes: str | None = None

    def __post_init__(self):
        if self.conflicts_with is None:
            self.conflicts_with = []
        if self.supersedes is None:
            self.supersedes = []


def new_lesson(
    scope: dict[str, Any],
    context: dict[str, Any],
    finding: dict[str, Any],
    recommendation: dict[str, Any],
    confidence: float = 0.5,
    notes: str | None = None,
) -> Lesson:
    """Create a new lesson with auto-generated ID and timestamp"""
    return Lesson(
        id=f"LL-{datetime.now(UTC).strftime('%Y-%m-%d')}-{uuid.uuid4().hex[:4]}",
        created_at=datetime.now(UTC).isoformat(),
        scope=scope,
        context=context,
        finding=finding,
        recommendation=recommendation,
        confidence=confidence,
        notes=notes,
    )


def append_lesson(path: str, lesson: Lesson) -> None:
    """Append a lesson to the JSONL file"""
    with open(path, "a") as f:
        f.write(json.dumps(asdict(lesson)) + "\n")


def load_lessons(path: str) -> list[Lesson]:
    """Load all lessons from a JSONL file"""
    lessons = []
    if not path or not os.path.exists(path):
        return lessons

    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                try:
                    data = json.loads(line)
                    lessons.append(Lesson(**data))
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"Warning: Skipping invalid lesson line: {e}")

    return lessons


def filter_lessons(lessons: list[Lesson], scope_filters: dict[str, Any]) -> list[Lesson]:
    """Filter lessons by scope criteria"""
    filtered = []
    for lesson in lessons:
        if lesson.status not in ("proposed", "applied"):
            continue

        # Simple scope matching - extend as needed
        lesson_scope = lesson.scope

        # Check level filter
        if "level" in scope_filters and scope_filters["level"] != "auto":
            if lesson_scope.get("level") != scope_filters["level"]:
                continue

        # Check profile filter (allow "auto" to match any profile)
        if "profile" in scope_filters and scope_filters["profile"] != "auto":
            if lesson_scope.get("profile") != scope_filters["profile"]:
                continue

        # Check dataset filter
        if "dataset" in scope_filters and scope_filters["dataset"] != "auto":
            if lesson_scope.get("dataset") != scope_filters["dataset"]:
                continue

        filtered.append(lesson)

    return filtered


if __name__ == "__main__":
    # Test the model
    import os

    # Create a test lesson
    scope = {"level": "profile", "profile": "precision_elevated"}
    context = {"model_signature": "bedrock:claude-3-haiku", "objective": "precision", "run_id": "test_run_001"}
    finding = {"pattern": "high_precision_low_recall", "evidence": {"precision": 0.85, "recall": 0.15, "f1": 0.25}}
    recommendation = {
        "type": "param_adjustment",
        "changes": [{"key": "RETRIEVAL_TOP_K", "op": "add", "value": 2}],
        "predicted_effect": {"recall": "+0.03~+0.06"},
        "rationale": "Increase retrieval to improve recall",
    }

    lesson = new_lesson(scope, context, finding, recommendation, confidence=0.7)
    print(f"Created lesson: {lesson.id}")
    print(json.dumps(asdict(lesson), indent=2))
