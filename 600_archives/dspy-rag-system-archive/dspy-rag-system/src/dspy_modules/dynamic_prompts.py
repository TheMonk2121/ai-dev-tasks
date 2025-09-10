#!/usr/bin/env python3
"""
Dynamic System Prompts for DSPy AI System
Implements dynamic prompt decorators with context injection and user preferences for B-1007
"""

import functools
import hashlib
import logging
import time
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .context_models import BaseContext

_LOG = logging.getLogger("dynamic_prompts")

# ---------- Dynamic Prompt Models ----------


class PromptTemplate(BaseModel):
    """Model for dynamic prompt templates"""

    template_id: str = Field(..., description="Unique template identifier")
    template_name: str = Field(..., description="Human-readable template name")
    base_prompt: str = Field(..., description="Base prompt template with placeholders")
    placeholders: list[str] = Field(default_factory=list, description="Available placeholders")
    context_aware: bool = Field(default=True, description="Whether template uses context")
    user_preference_aware: bool = Field(default=True, description="Whether template uses user preferences")
    version: str = Field(default="1.0.0", description="Template version")
    created_at: datetime = Field(default_factory=datetime.now, description="Template creation timestamp")

    @field_validator("base_prompt")
    @classmethod
    def validate_base_prompt(cls, v: str) -> str:
        """Validate base prompt is not empty"""
        if not v or len(v.strip()) < 10:
            raise ValueError("Base prompt must be at least 10 characters")
        return v.strip()

    @field_validator("template_id")
    @classmethod
    def validate_template_id(cls, v: str) -> str:
        """Validate template ID format"""
        if not v or len(v.strip()) < 3:
            raise ValueError("Template ID must be at least 3 characters")
        return v.strip()


class PromptContext(BaseModel):
    """Model for prompt context injection"""

    user_id: str | None = Field(None, description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    role_context: BaseContext | None = Field(None, description="Role-specific context")
    user_preferences: dict[str, Any] = Field(default_factory=dict, description="User preferences")
    dynamic_variables: dict[str, Any] = Field(default_factory=dict, description="Dynamic variables")
    timestamp: datetime = Field(default_factory=datetime.now, description="Context timestamp")

    @field_validator("session_id")
    @classmethod
    def validate_session_id(cls, v: str) -> str:
        """Validate session ID"""
        if not v or len(v.strip()) < 3:
            raise ValueError("Session ID must be at least 3 characters")
        return v.strip()


class PromptCache(BaseModel):
    """Model for prompt caching"""

    cache_key: str = Field(..., description="Cache key for the prompt")
    prompt_content: str = Field(..., description="Generated prompt content")
    context_hash: str = Field(..., description="Hash of context used")
    created_at: datetime = Field(default_factory=datetime.now, description="Cache creation timestamp")
    expires_at: datetime = Field(..., description="Cache expiration timestamp")
    hit_count: int = Field(default=0, description="Number of cache hits")

    @field_validator("cache_key")
    @classmethod
    def validate_cache_key(cls, v: str) -> str:
        """Validate cache key"""
        if not v or len(v.strip()) < 5:
            raise ValueError("Cache key must be at least 5 characters")
        return v.strip()


# ---------- Dynamic Prompt Decorators ----------


class DynamicPromptDecorator:
    """Decorator for dynamic prompt generation with context injection"""

    def __init__(self, template: PromptTemplate, cache_ttl: int = 300):
        """Initialize decorator with template and cache TTL"""
        self.template = template
        self.cache_ttl = cache_ttl
        self._cache: dict[str, PromptCache] = {}

    def __call__(self, func: Callable) -> Callable:
        """Apply decorator to function"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract context from function arguments
            context = self._extract_context(args, kwargs)

            # Generate dynamic prompt
            prompt = self._generate_prompt(context)

            # Inject prompt into function call
            return func(*args, prompt=prompt, **kwargs)

        return wrapper

    def _extract_context(self, args: tuple, kwargs: dict[str, Any]) -> PromptContext:
        """Extract context from function arguments"""
        # Look for context in kwargs first
        context = kwargs.get("context")
        if context and isinstance(context, PromptContext):
            return context

        # Look for context in args
        for arg in args:
            if isinstance(arg, PromptContext):
                return arg

        # Create default context
        return PromptContext(
            user_id="anonymous",
            session_id=f"default-{int(time.time())}",
            role_context=None,
            user_preferences={},
            dynamic_variables={},
        )

    def _generate_prompt(self, context: PromptContext) -> str:
        """Generate dynamic prompt from template and context"""
        # Check cache first
        cache_key = self._generate_cache_key(context)
        cached_prompt = self._get_cached_prompt(cache_key)
        if cached_prompt:
            return cached_prompt

        # Generate new prompt
        prompt_content = self.template.base_prompt

        # Inject context variables
        prompt_content = self._inject_context_variables(prompt_content, context)

        # Inject user preferences
        if self.template.user_preference_aware:
            prompt_content = self._inject_user_preferences(prompt_content, context)

        # Inject role-specific context
        if self.template.context_aware and context.role_context:
            prompt_content = self._inject_role_context(prompt_content, context.role_context)

        # Inject dynamic variables
        prompt_content = self._inject_dynamic_variables(prompt_content, context)

        # Cache the generated prompt
        self._cache_prompt(cache_key, prompt_content, context)

        return prompt_content

    def _generate_cache_key(self, context: PromptContext) -> str:
        """Generate cache key for context"""
        # Create hash of context for cache key
        context_data = {
            "template_id": self.template.template_id,
            "user_id": context.user_id,
            "session_id": context.session_id,
            "user_preferences": context.user_preferences,
            "dynamic_variables": context.dynamic_variables,
            "role_context": context.role_context.model_dump() if context.role_context else None,
        }

        context_str = str(sorted(context_data.items()))
        return hashlib.md5(context_str.encode()).hexdigest()

    def _get_cached_prompt(self, cache_key: str) -> str | None:
        """Get cached prompt if available and not expired"""
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if datetime.now() < cache_entry.expires_at:
                cache_entry.hit_count += 1
                return cache_entry.prompt_content
            else:
                # Remove expired cache entry
                del self._cache[cache_key]

        return None

    def _cache_prompt(self, cache_key: str, prompt_content: str, context: PromptContext) -> None:
        """Cache generated prompt"""
        context_hash = hashlib.md5(str(context.model_dump()).encode()).hexdigest()
        expires_at = datetime.now() + timedelta(seconds=self.cache_ttl)

        cache_entry = PromptCache(
            cache_key=cache_key, prompt_content=prompt_content, context_hash=context_hash, expires_at=expires_at
        )

        self._cache[cache_key] = cache_entry

    def _inject_context_variables(self, prompt: str, context: PromptContext) -> str:
        """Inject context variables into prompt"""
        # Basic context variable injection
        variables = {
            "user_id": context.user_id or "anonymous",
            "session_id": context.session_id,
            "timestamp": context.timestamp.isoformat(),
        }

        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value))

        return prompt

    def _inject_user_preferences(self, prompt: str, context: PromptContext) -> str:
        """Inject user preferences into prompt"""
        if not context.user_preferences:
            return prompt

        # Inject common user preferences
        preferences = context.user_preferences

        # Language preference
        if "language" in preferences:
            prompt = prompt.replace("{language}", preferences["language"])

        # Style preference
        if "style" in preferences:
            prompt = prompt.replace("{style}", preferences["style"])

        # Detail level preference
        if "detail_level" in preferences:
            prompt = prompt.replace("{detail_level}", preferences["detail_level"])

        return prompt

    def _inject_role_context(self, prompt: str, role_context: BaseContext) -> str:
        """Inject role-specific context into prompt"""
        # Inject role information
        prompt = prompt.replace("{role}", role_context.role.value)

        # Inject role-specific variables based on role type
        if hasattr(role_context, "project_scope"):
            prompt = prompt.replace("{project_scope}", getattr(role_context, "project_scope", ""))

        if hasattr(role_context, "language"):
            prompt = prompt.replace("{language}", getattr(role_context, "language", ""))

        if hasattr(role_context, "research_topic"):
            prompt = prompt.replace("{research_topic}", getattr(role_context, "research_topic", ""))

        return prompt

    def _inject_dynamic_variables(self, prompt: str, context: PromptContext) -> str:
        """Inject dynamic variables into prompt"""
        for key, value in context.dynamic_variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value))

        return prompt


# ---------- Prompt Security and Sanitization ----------


class PromptSanitizer:
    """Sanitizes prompts for security and safety"""

    @staticmethod
    def sanitize_prompt(prompt: str) -> str:
        """Sanitize prompt content for security"""
        # Remove potentially dangerous patterns
        dangerous_patterns = [
            r"<script.*?</script>",
            r"javascript:",
            r"data:text/html",
            r"vbscript:",
            r"on\w+\s*=",
        ]

        import re

        for pattern in dangerous_patterns:
            prompt = re.sub(pattern, "", prompt, flags=re.IGNORECASE)

        # Escape HTML entities
        prompt = prompt.replace("<", "&lt;").replace(">", "&gt;")

        # Limit prompt length
        max_length = 10000
        if len(prompt) > max_length:
            prompt = prompt[: max_length - 3] + "..."

        return prompt

    @staticmethod
    def validate_prompt_safety(prompt: str) -> bool:
        """Validate prompt for safety concerns"""
        # Check for potentially unsafe content
        unsafe_patterns = [
            "password",
            "secret",
            "key",
            "token",
            "admin",
            "root",
            "sudo",
        ]

        prompt_lower = prompt.lower()
        for pattern in unsafe_patterns:
            if pattern in prompt_lower:
                return False

        return True


# ---------- Prompt Performance Monitoring ----------


class PromptPerformanceMetrics(BaseModel):
    """Metrics for prompt generation performance"""

    total_generations: int = Field(default=0, description="Total prompt generations")
    cache_hits: int = Field(default=0, description="Number of cache hits")
    cache_misses: int = Field(default=0, description="Number of cache misses")
    avg_generation_time: float = Field(default=0.0, description="Average generation time in seconds")
    generation_times: list[float] = Field(default_factory=list, description="Generation times")

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total_requests = self.cache_hits + self.cache_misses
        if total_requests == 0:
            return 0.0
        return self.cache_hits / total_requests

    @property
    def avg_generation_time_ms(self) -> float:
        """Get average generation time in milliseconds"""
        return self.avg_generation_time * 1000


# ---------- Dynamic Prompt Manager ----------


class DynamicPromptManager:
    """Manages dynamic prompt generation and caching"""

    def __init__(self):
        """Initialize prompt manager"""
        self.templates: dict[str, PromptTemplate] = {}
        self.sanitizer = PromptSanitizer()
        self.metrics = PromptPerformanceMetrics()

    def register_template(self, template: PromptTemplate) -> None:
        """Register a prompt template"""
        self.templates[template.template_id] = template
        _LOG.info(f"Registered prompt template: {template.template_name}")

    def generate_prompt(self, template_id: str, context: PromptContext, cache_ttl: int = 300) -> str:
        """Generate dynamic prompt from template"""
        start_time = time.time()

        # Get template
        if template_id not in self.templates:
            raise ValueError(f"Template not found: {template_id}")

        template = self.templates[template_id]

        # Create decorator for this generation
        decorator = DynamicPromptDecorator(template, cache_ttl)

        # Generate prompt using decorator logic
        prompt = decorator._generate_prompt(context)

        # Sanitize prompt
        prompt = self.sanitizer.sanitize_prompt(prompt)

        # Validate safety
        if not self.sanitizer.validate_prompt_safety(prompt):
            _LOG.warning(f"Potentially unsafe prompt detected for template: {template_id}")

        # Update metrics
        generation_time = time.time() - start_time
        self._update_metrics(generation_time, decorator._cache)

        return prompt

    def _update_metrics(self, generation_time: float, cache: dict[str, PromptCache]) -> None:
        """Update performance metrics"""
        self.metrics.total_generations += 1
        self.metrics.generation_times.append(generation_time)

        # Calculate average generation time
        self.metrics.avg_generation_time = sum(self.metrics.generation_times) / len(self.metrics.generation_times)

        # Update cache metrics
        cache_hits = sum(1 for entry in cache.values() if entry.hit_count > 0)
        self.metrics.cache_hits = cache_hits
        self.metrics.cache_misses = self.metrics.total_generations - cache_hits

    def get_metrics(self) -> PromptPerformanceMetrics:
        """Get current performance metrics"""
        return self.metrics


# ---------- Default Prompt Templates ----------


def create_default_prompt_templates() -> list[PromptTemplate]:
    """Create default prompt templates"""
    templates = [
        PromptTemplate(
            template_id="planner_general",
            template_name="General Planner Prompt",
            base_prompt="""You are an AI planner with the following context:
- User ID: {user_id}
- Session: {session_id}
- Project Scope: {project_scope}
- Language: {language}
- Style: {style}

Please provide strategic planning assistance for the current project.""",
            placeholders=["user_id", "session_id", "project_scope", "language", "style"],
            context_aware=True,
            user_preference_aware=True,
        ),
        PromptTemplate(
            template_id="coder_implementation",
            template_name="Coder Implementation Prompt",
            base_prompt="""You are an AI coder with the following context:
- User ID: {user_id}
- Session: {session_id}
- Language: {language}
- Codebase Path: {codebase_path}
- Detail Level: {detail_level}

Please provide implementation assistance for the current task.""",
            placeholders=["user_id", "session_id", "language", "codebase_path", "detail_level"],
            context_aware=True,
            user_preference_aware=True,
        ),
        PromptTemplate(
            template_id="researcher_analysis",
            template_name="Researcher Analysis Prompt",
            base_prompt="""You are an AI researcher with the following context:
- User ID: {user_id}
- Session: {session_id}
- Research Topic: {research_topic}
- Methodology: {methodology}
- Style: {style}

Please provide research analysis for the current topic.""",
            placeholders=["user_id", "session_id", "research_topic", "methodology", "style"],
            context_aware=True,
            user_preference_aware=True,
        ),
    ]

    return templates
