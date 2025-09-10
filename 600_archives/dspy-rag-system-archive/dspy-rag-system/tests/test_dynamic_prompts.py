#!/usr/bin/env python3
"""
Tests for Dynamic System Prompts
Validates dynamic prompt generation and caching for B-1007
"""

from datetime import datetime, timedelta

import pytest

from src.dspy_modules.context_models import AIRole, PlannerContext
from src.dspy_modules.dynamic_prompts import (
    DynamicPromptDecorator,
    DynamicPromptManager,
    PromptCache,
    PromptContext,
    PromptPerformanceMetrics,
    PromptSanitizer,
    PromptTemplate,
    create_default_prompt_templates,
)


class TestPromptTemplate:
    """Test prompt template model"""

    def test_prompt_template_creation(self):
        """Test prompt template creation"""
        template = PromptTemplate(
            template_id="test_template",
            template_name="Test Template",
            base_prompt="You are an AI assistant for user {user_id} in session {session_id}.",
            placeholders=["user_id", "session_id"],
        )

        assert template.template_id == "test_template"
        assert template.template_name == "Test Template"
        assert "user_id" in template.base_prompt
        assert "session_id" in template.base_prompt
        assert template.placeholders == ["user_id", "session_id"]
        assert template.context_aware is True
        assert template.user_preference_aware is True

    def test_base_prompt_validation(self):
        """Test base prompt validation"""
        # Valid prompt
        template = PromptTemplate(
            template_id="test",
            template_name="Test",
            base_prompt="This is a valid prompt with sufficient length for testing purposes.",
        )
        assert len(template.base_prompt) >= 10

        # Invalid prompt (too short)
        with pytest.raises(ValueError, match="Base prompt must be at least 10 characters"):
            PromptTemplate(template_id="test", template_name="Test", base_prompt="Short")

    def test_template_id_validation(self):
        """Test template ID validation"""
        # Valid ID
        template = PromptTemplate(
            template_id="valid_id", template_name="Test", base_prompt="Valid prompt with sufficient length"
        )
        assert template.template_id == "valid_id"

        # Invalid ID (too short)
        with pytest.raises(ValueError, match="Template ID must be at least 3 characters"):
            PromptTemplate(template_id="ab", template_name="Test", base_prompt="Valid prompt with sufficient length")


class TestPromptContext:
    """Test prompt context model"""

    def test_prompt_context_creation(self):
        """Test prompt context creation"""
        context = PromptContext(
            user_id="test_user",
            session_id="test_session",
            user_preferences={"language": "python", "style": "concise"},
            dynamic_variables={"task": "coding"},
            role_context=None,
        )

        assert context.user_id == "test_user"
        assert context.session_id == "test_session"
        assert context.user_preferences["language"] == "python"
        assert context.dynamic_variables["task"] == "coding"
        assert context.role_context is None

    def test_session_id_validation(self):
        """Test session ID validation"""
        # Valid session ID
        context = PromptContext(session_id="valid_session_id", user_id=None, role_context=None)
        assert context.session_id == "valid_session_id"

        # Invalid session ID (too short)
        with pytest.raises(ValueError, match="Session ID must be at least 3 characters"):
            PromptContext(session_id="ab", user_id=None, role_context=None)

    def test_prompt_context_with_role_context(self):
        """Test prompt context with role context"""
        role_context = PlannerContext(
            session_id="role_session", project_scope="Test project scope", backlog_priority="P1", user_id=None
        )

        context = PromptContext(session_id="test_session", role_context=role_context, user_id=None)

        assert context.role_context == role_context
        assert context.role_context is not None
        assert context.role_context.role == AIRole.PLANNER


class TestPromptCache:
    """Test prompt cache model"""

    def test_prompt_cache_creation(self):
        """Test prompt cache creation"""
        expires_at = datetime.now() + timedelta(hours=1)
        cache = PromptCache(
            cache_key="test_cache_key",
            prompt_content="Cached prompt content",
            context_hash="abc123",
            expires_at=expires_at,
        )

        assert cache.cache_key == "test_cache_key"
        assert cache.prompt_content == "Cached prompt content"
        assert cache.context_hash == "abc123"
        assert cache.expires_at == expires_at
        assert cache.hit_count == 0

    def test_cache_key_validation(self):
        """Test cache key validation"""
        expires_at = datetime.now() + timedelta(hours=1)

        # Valid cache key
        cache = PromptCache(
            cache_key="valid_cache_key", prompt_content="Content", context_hash="hash", expires_at=expires_at
        )
        assert cache.cache_key == "valid_cache_key"

        # Invalid cache key (too short)
        with pytest.raises(ValueError, match="Cache key must be at least 5 characters"):
            PromptCache(cache_key="abcd", prompt_content="Content", context_hash="hash", expires_at=expires_at)


class TestDynamicPromptDecorator:
    """Test dynamic prompt decorator"""

    def test_decorator_creation(self):
        """Test decorator creation"""
        template = PromptTemplate(
            template_id="test", template_name="Test", base_prompt="Hello {user_id}, welcome to session {session_id}."
        )

        decorator = DynamicPromptDecorator(template, cache_ttl=300)
        assert decorator.template == template
        assert decorator.cache_ttl == 300
        assert len(decorator._cache) == 0

    def test_decorator_function_wrapping(self):
        """Test decorator function wrapping"""
        template = PromptTemplate(
            template_id="test", template_name="Test", base_prompt="Hello {user_id}, welcome to session {session_id}."
        )

        decorator = DynamicPromptDecorator(template)

        @decorator
        def test_function(context, prompt=None):
            return f"Function called with prompt: {prompt}"

        # Test with context
        context = PromptContext(user_id="test_user", session_id="test_session", role_context=None)

        result = test_function(context)
        assert "Function called with prompt:" in result
        assert "test_user" in result
        assert "test_session" in result

    def test_cache_functionality(self):
        """Test cache functionality"""
        template = PromptTemplate(template_id="test", template_name="Test", base_prompt="Hello {user_id}.")

        decorator = DynamicPromptDecorator(template, cache_ttl=300)
        context = PromptContext(user_id="test_user", session_id="test_session", role_context=None)

        # First call - should cache
        prompt1 = decorator._generate_prompt(context)
        assert len(decorator._cache) == 1

        # Second call - should use cache
        prompt2 = decorator._generate_prompt(context)
        assert prompt1 == prompt2

        # Check cache hit
        cache_key = decorator._generate_cache_key(context)
        cache_entry = decorator._cache[cache_key]
        assert cache_entry.hit_count > 0

    def test_context_variable_injection(self):
        """Test context variable injection"""
        template = PromptTemplate(
            template_id="test",
            template_name="Test",
            base_prompt="User: {user_id}, Session: {session_id}, Time: {timestamp}",
        )

        decorator = DynamicPromptDecorator(template)
        context = PromptContext(user_id="test_user", session_id="test_session", role_context=None)

        prompt = decorator._generate_prompt(context)

        assert "test_user" in prompt
        assert "test_session" in prompt
        assert "Time:" in prompt

    def test_user_preference_injection(self):
        """Test user preference injection"""
        template = PromptTemplate(
            template_id="test",
            template_name="Test",
            base_prompt="Language: {language}, Style: {style}, Detail: {detail_level}",
        )

        decorator = DynamicPromptDecorator(template)
        context = PromptContext(
            user_id="test_user",
            session_id="test_session",
            user_preferences={"language": "python", "style": "concise", "detail_level": "high"},
            role_context=None,
        )

        prompt = decorator._generate_prompt(context)

        assert "python" in prompt
        assert "concise" in prompt
        assert "high" in prompt

    def test_role_context_injection(self):
        """Test role context injection"""
        template = PromptTemplate(
            template_id="test", template_name="Test", base_prompt="Role: {role}, Project: {project_scope}"
        )

        decorator = DynamicPromptDecorator(template)
        role_context = PlannerContext(
            session_id="test_session", project_scope="Test project", backlog_priority="P1", user_id=None
        )

        context = PromptContext(user_id="test_user", session_id="test_session", role_context=role_context)

        prompt = decorator._generate_prompt(context)

        assert "planner" in prompt
        assert "Test project" in prompt

    def test_dynamic_variable_injection(self):
        """Test dynamic variable injection"""
        template = PromptTemplate(
            template_id="test", template_name="Test", base_prompt="Task: {task}, Priority: {priority}"
        )

        decorator = DynamicPromptDecorator(template)
        context = PromptContext(
            user_id="test_user",
            session_id="test_session",
            dynamic_variables={"task": "coding", "priority": "high"},
            role_context=None,
        )

        prompt = decorator._generate_prompt(context)

        assert "coding" in prompt
        assert "high" in prompt


class TestPromptSanitizer:
    """Test prompt sanitizer"""

    def test_sanitize_prompt_basic(self):
        """Test basic prompt sanitization"""
        prompt = "Hello <script>alert('xss')</script> world"
        sanitized = PromptSanitizer.sanitize_prompt(prompt)

        assert "<script>" not in sanitized
        # The script tag is completely removed, so no angle brackets remain
        assert "alert" not in sanitized
        assert "Hello" in sanitized
        assert "world" in sanitized

    def test_sanitize_prompt_length_limit(self):
        """Test prompt length limiting"""
        long_prompt = "A" * 15000
        sanitized = PromptSanitizer.sanitize_prompt(long_prompt)

        assert len(sanitized) <= 10000
        assert sanitized.endswith("...")

    def test_validate_prompt_safety(self):
        """Test prompt safety validation"""
        # Safe prompt
        safe_prompt = "Hello world, how are you today?"
        assert PromptSanitizer.validate_prompt_safety(safe_prompt) is True

        # Unsafe prompt
        unsafe_prompt = "Here is my password: secret123"
        assert PromptSanitizer.validate_prompt_safety(unsafe_prompt) is False

        # Another unsafe prompt
        unsafe_prompt2 = "Admin credentials: root:password"
        assert PromptSanitizer.validate_prompt_safety(unsafe_prompt2) is False


class TestPromptPerformanceMetrics:
    """Test prompt performance metrics"""

    def test_metrics_creation(self):
        """Test metrics creation"""
        metrics = PromptPerformanceMetrics(
            total_generations=100,
            cache_hits=80,
            cache_misses=20,
            avg_generation_time=0.05,
            generation_times=[0.04, 0.05, 0.06],
        )

        assert metrics.total_generations == 100
        assert metrics.cache_hits == 80
        assert metrics.cache_misses == 20
        assert metrics.avg_generation_time == 0.05
        assert len(metrics.generation_times) == 3

    def test_cache_hit_rate_calculation(self):
        """Test cache hit rate calculation"""
        # With hits and misses
        metrics = PromptPerformanceMetrics(cache_hits=80, cache_misses=20)
        assert metrics.cache_hit_rate == 0.8

        # With no requests
        metrics = PromptPerformanceMetrics()
        assert metrics.cache_hit_rate == 0.0

    def test_avg_generation_time_ms(self):
        """Test average generation time in milliseconds"""
        metrics = PromptPerformanceMetrics(avg_generation_time=0.05)
        assert metrics.avg_generation_time_ms == 50.0


class TestDynamicPromptManager:
    """Test dynamic prompt manager"""

    def test_manager_creation(self):
        """Test manager creation"""
        manager = DynamicPromptManager()
        assert len(manager.templates) == 0
        assert manager.sanitizer is not None
        assert manager.metrics is not None

    def test_register_template(self):
        """Test template registration"""
        manager = DynamicPromptManager()
        template = PromptTemplate(template_id="test", template_name="Test", base_prompt="Hello {user_id}.")

        manager.register_template(template)
        assert "test" in manager.templates
        assert manager.templates["test"] == template

    def test_generate_prompt(self):
        """Test prompt generation"""
        manager = DynamicPromptManager()
        template = PromptTemplate(
            template_id="test", template_name="Test", base_prompt="Hello {user_id}, welcome to {session_id}."
        )

        manager.register_template(template)
        context = PromptContext(user_id="test_user", session_id="test_session", role_context=None)

        prompt = manager.generate_prompt("test", context)

        assert "test_user" in prompt
        assert "test_session" in prompt

    def test_generate_prompt_template_not_found(self):
        """Test prompt generation with non-existent template"""
        manager = DynamicPromptManager()
        context = PromptContext(user_id="test_user", session_id="test_session", role_context=None)

        with pytest.raises(ValueError, match="Template not found"):
            manager.generate_prompt("nonexistent", context)

    def test_generate_prompt_with_sanitization(self):
        """Test prompt generation with sanitization"""
        manager = DynamicPromptManager()
        template = PromptTemplate(
            template_id="test", template_name="Test", base_prompt="Hello {user_id} <script>alert('xss')</script>."
        )

        manager.register_template(template)
        context = PromptContext(user_id="test_user", session_id="test_session", role_context=None)

        prompt = manager.generate_prompt("test", context)

        assert "<script>" not in prompt
        assert "alert" not in prompt
        assert "test_user" in prompt

    def test_get_metrics(self):
        """Test metrics retrieval"""
        manager = DynamicPromptManager()
        template = PromptTemplate(template_id="test", template_name="Test", base_prompt="Hello {user_id}.")

        manager.register_template(template)
        context = PromptContext(user_id="test_user", session_id="test_session", role_context=None)

        # Generate some prompts to update metrics
        manager.generate_prompt("test", context)
        manager.generate_prompt("test", context)

        metrics = manager.get_metrics()
        assert metrics.total_generations > 0


class TestDefaultPromptTemplates:
    """Test default prompt templates"""

    def test_create_default_prompt_templates(self):
        """Test creation of default prompt templates"""
        templates = create_default_prompt_templates()

        assert len(templates) == 3

        # Check for expected templates
        template_ids = [t.template_id for t in templates]
        assert "planner_general" in template_ids
        assert "coder_implementation" in template_ids
        assert "researcher_analysis" in template_ids

    def test_planner_template_content(self):
        """Test planner template content"""
        templates = create_default_prompt_templates()
        planner_template = next(t for t in templates if t.template_id == "planner_general")

        assert "planner" in planner_template.base_prompt.lower()
        assert "{user_id}" in planner_template.base_prompt
        assert "{project_scope}" in planner_template.base_prompt
        assert planner_template.context_aware is True
        assert planner_template.user_preference_aware is True

    def test_coder_template_content(self):
        """Test coder template content"""
        templates = create_default_prompt_templates()
        coder_template = next(t for t in templates if t.template_id == "coder_implementation")

        assert "coder" in coder_template.base_prompt.lower()
        assert "{language}" in coder_template.base_prompt
        assert "{codebase_path}" in coder_template.base_prompt
        assert coder_template.context_aware is True
        assert coder_template.user_preference_aware is True

    def test_researcher_template_content(self):
        """Test researcher template content"""
        templates = create_default_prompt_templates()
        researcher_template = next(t for t in templates if t.template_id == "researcher_analysis")

        assert "researcher" in researcher_template.base_prompt.lower()
        assert "{research_topic}" in researcher_template.base_prompt
        assert "{methodology}" in researcher_template.base_prompt
        assert researcher_template.context_aware is True
        assert researcher_template.user_preference_aware is True


if __name__ == "__main__":
    pytest.main([__file__])
