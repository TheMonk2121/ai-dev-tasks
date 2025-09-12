from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field
import os
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Pydantic Models for Backlog Workflow Validation

Lightweight validation schemas for handoff context bundles, idea capture,
PRDs, and task lists to ensure reliable data flow across workflow stages.
"""





class ContextBundle(BaseModel):
    """Handoff context bundle for clean chat pickup."""

    backlog_id: str = Field(..., pattern=r"^B-\d{4}$", description="Backlog ID (e.g., B-1071)")
    title: str = Field(..., min_length=1, description="Brief title")
    what: str = Field(..., min_length=1, description="What this item is about")
    where: str = Field(..., description="Current status/phase")
    priority: str = Field(..., description="Priority level")
    next: str = Field(..., description="Next action to take")
    context: dict[str, Any] = Field(default_factory=dict, description="Additional context data")

    class Config:
        extra = "allow"  # Allow additional fields for future extensibility


class BacklogIdea(BaseModel):
    """Validated idea for backlog capture."""

    thought: str = Field(..., min_length=1, max_length=500, description="Raw idea text")
    problem: str | None = Field(None, description="What problem does this solve")
    value: str | None = Field(None, description="Why this matters")
    next_action: str | None = Field(None, description="Suggested next step")
    anchor_after: str = Field(default="B-1071", description="Insert after this backlog ID")


class PRDSummary(BaseModel):
    """Basic PRD validation structure."""

    backlog_id: str = Field(..., pattern=r"^B-\d{4}$")
    title: str = Field(..., min_length=1)
    problem: str = Field(..., min_length=1, description="What's broken")
    solution: str = Field(..., min_length=1, description="What we're building")
    acceptance_criteria: list[str] = Field(..., min_length=1)
    risks: list[str] = Field(default_factory=list)
    estimated_points: int | None = Field(None, ge=1, le=20)


class Task(BaseModel):
    """Individual task validation."""

    id: str = Field(..., description="Task ID")
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    priority: str = Field(..., description="Critical/High/Medium/Low")
    estimated_hours: int | None = Field(None, ge=1, le=40)
    dependencies: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(..., min_length=1)


class TaskList(BaseModel):
    """Task list validation structure."""

    backlog_id: str = Field(..., pattern=r"^B-\d{4}$")
    title: str = Field(..., min_length=1)
    total_tasks: int = Field(..., ge=1)
    tasks: list[Task] = Field(..., min_length=1)
    estimated_total_hours: int | None = Field(None, ge=1)

    def validate_task_count(self) -> bool:
        """Ensure total_tasks matches actual task count."""
        return self.total_tasks == len(self.tasks)
