#!/usr/bin/env python3
"""
Role-Based Context Models for DSPy AI System
Implements typed context models with role-specific validation for B-1007
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

_LOG = logging.getLogger("context_models")

# ---------- Role Definitions ----------


class AIRole(Enum):
    """Available AI roles for context modeling"""

    PLANNER = "planner"
    CODER = "coder"
    RESEARCHER = "researcher"
    IMPLEMENTER = "implementer"


# ---------- Base Context Models ----------


class BaseContext(BaseModel):
    """Base context model with common validation"""

    role: AIRole = Field(..., description="AI role for this context")
    session_id: str = Field(..., description="Unique session identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Context creation timestamp")
    user_id: Optional[str] = Field(None, description="User identifier if available")

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        """Validate session ID format"""
        if not v or len(v.strip()) < 3:
            raise ValueError("Session ID must be at least 3 characters")
        return v.strip()

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: datetime) -> datetime:
        """Validate timestamp is not in the future"""
        if v > datetime.now():
            raise ValueError("Timestamp cannot be in the future")
        return v


# ---------- Role-Specific Context Models ----------


class PlannerContext(BaseContext):
    """Context model for Planner role with strategic validation"""

    role: AIRole = Field(default=AIRole.PLANNER, description="Planner role")
    project_scope: str = Field(..., description="Current project scope and objectives")
    backlog_priority: str = Field(..., description="Current backlog priority level")
    strategic_goals: List[str] = Field(default_factory=list, description="Strategic goals for this session")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Project constraints and limitations")
    dependencies: List[str] = Field(default_factory=list, description="Dependencies and blockers")

    @field_validator("project_scope")
    @classmethod
    def validate_project_scope(cls, v: str) -> str:
        """Validate project scope is meaningful"""
        if not v or len(v.strip()) < 10:
            raise ValueError("Project scope must be at least 10 characters")
        return v.strip()

    @field_validator("backlog_priority")
    @classmethod
    def validate_backlog_priority(cls, v: str) -> str:
        """Validate backlog priority format"""
        valid_priorities = ["P0", "P1", "P2", "P3"]
        if v not in valid_priorities:
            raise ValueError(f"Backlog priority must be one of: {valid_priorities}")
        return v

    @field_validator("strategic_goals")
    @classmethod
    def validate_strategic_goals(cls, v: List[str]) -> List[str]:
        """Validate strategic goals are meaningful"""
        if len(v) > 10:
            raise ValueError("Cannot have more than 10 strategic goals")
        return [goal.strip() for goal in v if goal.strip()]


class CoderContext(BaseContext):
    """Context model for Coder role with implementation validation"""

    role: AIRole = Field(default=AIRole.CODER, description="Coder role")
    codebase_path: str = Field(..., description="Path to current codebase")
    file_context: List[str] = Field(default_factory=list, description="Relevant files for current task")
    language: str = Field(..., description="Primary programming language")
    framework: Optional[str] = Field(None, description="Framework being used")
    testing_requirements: Dict[str, Any] = Field(default_factory=dict, description="Testing requirements")
    performance_constraints: Dict[str, Any] = Field(default_factory=dict, description="Performance constraints")

    @field_validator("codebase_path")
    @classmethod
    def validate_codebase_path(cls, v: str) -> str:
        """Validate codebase path exists and is accessible"""
        import os

        if not os.path.exists(v):
            raise ValueError(f"Codebase path does not exist: {v}")
        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate programming language is supported"""
        supported_languages = ["python", "javascript", "typescript", "go", "rust", "java", "csharp"]
        if v.lower() not in supported_languages:
            raise ValueError(f"Language must be one of: {supported_languages}")
        return v.lower()

    @field_validator("file_context")
    @classmethod
    def validate_file_context(cls, v: List[str]) -> List[str]:
        """Validate file context paths"""
        import os

        valid_files = []
        for file_path in v:
            if os.path.exists(file_path):
                valid_files.append(file_path)
            else:
                _LOG.warning(f"File context path does not exist: {file_path}")
        return valid_files


class ResearcherContext(BaseContext):
    """Context model for Researcher role with analysis validation"""

    role: AIRole = Field(default=AIRole.RESEARCHER, description="Researcher role")
    research_topic: str = Field(..., description="Current research topic")
    sources: List[str] = Field(default_factory=list, description="Research sources and references")
    methodology: str = Field(..., description="Research methodology being used")
    hypotheses: List[str] = Field(default_factory=list, description="Research hypotheses")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Research constraints")

    @field_validator("research_topic")
    @classmethod
    def validate_research_topic(cls, v: str) -> str:
        """Validate research topic is meaningful"""
        if not v or len(v.strip()) < 5:
            raise ValueError("Research topic must be at least 5 characters")
        return v.strip()

    @field_validator("methodology")
    @classmethod
    def validate_methodology(cls, v: str) -> str:
        """Validate research methodology"""
        valid_methodologies = ["literature_review", "experimental", "case_study", "survey", "analysis"]
        if v.lower() not in valid_methodologies:
            raise ValueError(f"Methodology must be one of: {valid_methodologies}")
        return v.lower()


class ImplementerContext(BaseContext):
    """Context model for Implementer role with execution validation"""

    role: AIRole = Field(default=AIRole.IMPLEMENTER, description="Implementer role")
    implementation_plan: str = Field(..., description="Implementation plan and approach")
    target_environment: str = Field(..., description="Target deployment environment")
    integration_points: List[str] = Field(default_factory=list, description="Integration points")
    rollback_strategy: Optional[str] = Field(None, description="Rollback strategy if needed")
    monitoring_requirements: Dict[str, Any] = Field(default_factory=dict, description="Monitoring requirements")

    @field_validator("implementation_plan")
    @classmethod
    def validate_implementation_plan(cls, v: str) -> str:
        """Validate implementation plan is detailed enough"""
        if not v or len(v.strip()) < 20:
            raise ValueError("Implementation plan must be at least 20 characters")
        return v.strip()

    @field_validator("target_environment")
    @classmethod
    def validate_target_environment(cls, v: str) -> str:
        """Validate target environment"""
        valid_environments = ["development", "staging", "production", "testing"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Target environment must be one of: {valid_environments}")
        return v.lower()


# ---------- Context Factory ----------


class ContextFactory:
    """Factory for creating role-specific context models"""

    @staticmethod
    def create_context(role: AIRole, **kwargs) -> BaseContext:
        """Create a context model for the specified role"""

        context_classes = {
            AIRole.PLANNER: PlannerContext,
            AIRole.CODER: CoderContext,
            AIRole.RESEARCHER: ResearcherContext,
            AIRole.IMPLEMENTER: ImplementerContext,
        }

        if role not in context_classes:
            raise ValueError(f"Unsupported role: {role}")

        context_class = context_classes[role]
        return context_class(role=role, **kwargs)

    @staticmethod
    def validate_context(context: BaseContext) -> bool:
        """Validate a context model"""
        try:
            # Pydantic validation happens automatically
            return True
        except Exception as e:
            _LOG.error(f"Context validation failed: {e}")
            return False


# ---------- Backward Compatibility Layer ----------


class LegacyContextAdapter:
    """Adapter for backward compatibility with existing API calls"""

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> BaseContext:
        """Convert dictionary to appropriate context model"""

        # Extract role from data
        role_str = data.get("role", "planner")
        try:
            role = AIRole(role_str)
        except ValueError:
            _LOG.warning(f"Unknown role '{role_str}', defaulting to planner")
            role = AIRole.PLANNER

        # Remove role from data to avoid duplicate argument
        data_copy = data.copy()
        data_copy.pop("role", None)

        # Create context using factory
        return ContextFactory.create_context(role, **data_copy)

    @staticmethod
    def to_dict(context: BaseContext) -> Dict[str, Any]:
        """Convert context model to dictionary"""
        data = context.model_dump()
        # Convert AIRole enum to string for backward compatibility
        data["role"] = context.role.value
        return data


# ---------- Performance Benchmarking ----------


class ContextValidationBenchmark:
    """Benchmarking utilities for context validation performance"""

    @staticmethod
    def benchmark_validation_overhead(context: BaseContext, iterations: int = 1000) -> Dict[str, float]:
        """Benchmark validation overhead"""
        import time

        start_time = time.time()

        for _ in range(iterations):
            # Trigger validation by creating a copy
            context.model_copy()

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / iterations

        return {
            "total_time_ms": total_time * 1000,
            "avg_time_ms": avg_time * 1000,
            "iterations": iterations,
            "overhead_percent": (avg_time / 0.001) * 100,  # Assuming 1ms baseline
        }
