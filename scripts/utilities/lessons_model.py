from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime, timezone
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

#!/usr/bin/env python3
"""
Lessons Model - Data structures and utilities for the Closed-Loop Lessons Engine (CLLE)
"""


class ParamChange(BaseModel):
    """Represents a parameter change operation with Pydantic validation."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    key: str = Field(..., min_length=1, description="Parameter key (e.g., 'RETRIEVAL_TOP_K')")
    op: str = Field(..., pattern="^(add|mul|set)$", description="Operation type: add, mul, or set")
    value: float = Field(..., description="Numeric value for the operation")

    @field_validator("key")
    @classmethod
    def validate_key(cls, v):
        """Validate parameter key format."""
        if not v or not v.strip():
            raise ValueError("Parameter key cannot be empty")
        return v.strip().upper()


class Lesson(BaseModel):
    """A lesson learned from an evaluation run with Pydantic validation."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    id: str = Field(..., min_length=1, description="Unique lesson identifier")
    created_at: str = Field(..., description="ISO timestamp when lesson was created")
    scope: dict[str, Any] = Field(..., description="Scope of the lesson (level, profile, dataset)")
    context: dict[str, Any] = Field(..., description="Context information for the lesson")
    finding: dict[str, Any] = Field(..., description="What was discovered")
    recommendation: dict[str, Any] = Field(..., description="Recommended actions")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the lesson")
    status: str = Field(
        default="proposed", pattern="^(proposed|applied|rejected|superseded)$", description="Lesson status"
    )
    conflicts_with: list[str] = Field(default_factory=list, description="IDs of conflicting lessons")
    supersedes: list[str] = Field(default_factory=list, description="IDs of superseded lessons")
    notes: str | None = Field(None, description="Additional notes")

    @field_validator("created_at")
    @classmethod
    def validate_created_at(cls, v):
        """Validate ISO timestamp format."""
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return v
        except ValueError:
            raise ValueError("created_at must be a valid ISO timestamp")

    @field_validator("scope", "context", "finding", "recommendation")
    @classmethod
    def validate_dict_fields(cls, v):
        """Validate that dict fields are not empty."""
        if not isinstance(v, dict):
            raise ValueError("Field must be a dictionary")
        if not v:
            raise ValueError("Dictionary cannot be empty")
        return v


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
        f.write(json.dumps(lesson.model_dump()) + "\n")


def load_lessons(path: str) -> list[Lesson]:
    """Load all lessons from a JSONL file"""
    lessons: list[Lesson] = []
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
    print(json.dumps(lesson.model_dump(), indent=2))
