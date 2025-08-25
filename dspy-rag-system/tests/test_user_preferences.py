#!/usr/bin/env python3
"""
Tests for User Preference System
Validates user preference storage, retrieval, and customization for B-1007
"""

from datetime import datetime, timedelta

import pytest

from src.dspy_modules.user_preferences import (
    DefaultPreferences,
    PreferenceCache,
    PreferencePerformanceMetrics,
    ResponseCustomizer,
    UserPreference,
    UserPreferenceManager,
    UserPreferenceSet,
)


class TestUserPreference:
    """Test user preference model"""

    def test_user_preference_creation(self):
        """Test user preference creation"""
        preference = UserPreference(
            preference_id="test_user_language",
            user_id="test_user",
            preference_key="language",
            preference_value="python",
            preference_type="string",
            category="development",
            description="Preferred programming language",
        )

        assert preference.preference_id == "test_user_language"
        assert preference.user_id == "test_user"
        assert preference.preference_key == "language"
        assert preference.preference_value == "python"
        assert preference.preference_type == "string"
        assert preference.category == "development"
        assert preference.description == "Preferred programming language"
        assert preference.is_active is True

    def test_preference_id_validation(self):
        """Test preference ID validation"""
        # Valid ID
        preference = UserPreference(
            preference_id="valid_id",
            user_id="test_user",
            preference_key="test",
            preference_value="value",
            preference_type="string",
            category="test",
            description=None,
        )
        assert preference.preference_id == "valid_id"

        # Invalid ID (too short)
        with pytest.raises(ValueError, match="Preference ID must be at least 3 characters"):
            UserPreference(
                preference_id="ab",
                user_id="test_user",
                preference_key="test",
                preference_value="value",
                preference_type="string",
                category="test",
                description=None,
            )

    def test_user_id_validation(self):
        """Test user ID validation"""
        # Valid user ID
        preference = UserPreference(
            preference_id="test_id",
            user_id="valid_user",
            preference_key="test",
            preference_value="value",
            preference_type="string",
            category="test",
            description=None,
        )
        assert preference.user_id == "valid_user"

        # Invalid user ID (empty)
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            UserPreference(
                preference_id="test_id",
                user_id="",
                preference_key="test",
                preference_value="value",
                preference_type="string",
                category="test",
                description=None,
            )

    def test_preference_key_validation(self):
        """Test preference key validation"""
        # Valid key
        preference = UserPreference(
            preference_id="test_id",
            user_id="test_user",
            preference_key="valid_key",
            preference_value="value",
            preference_type="string",
            category="test",
            description=None,
        )
        assert preference.preference_key == "valid_key"

        # Invalid key (too short)
        with pytest.raises(ValueError, match="Preference key must be at least 2 characters"):
            UserPreference(
                preference_id="test_id",
                user_id="test_user",
                preference_key="a",
                preference_value="value",
                preference_type="string",
                category="test",
                description=None,
            )


class TestUserPreferenceSet:
    """Test user preference set model"""

    def test_preference_set_creation(self):
        """Test preference set creation"""
        expires_at = datetime.now() + timedelta(hours=1)
        preference_set = UserPreferenceSet(user_id="test_user", cache_expires=expires_at)

        assert preference_set.user_id == "test_user"
        assert preference_set.preferences == {}
        assert preference_set.cache_expires == expires_at

    def test_user_id_validation(self):
        """Test user ID validation"""
        expires_at = datetime.now() + timedelta(hours=1)

        # Valid user ID
        preference_set = UserPreferenceSet(user_id="valid_user", cache_expires=expires_at)
        assert preference_set.user_id == "valid_user"

        # Invalid user ID (empty)
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            UserPreferenceSet(user_id="", cache_expires=expires_at)


class TestPreferenceCache:
    """Test preference cache model"""

    def test_preference_cache_creation(self):
        """Test preference cache creation"""
        expires_at = datetime.now() + timedelta(hours=1)
        cache = PreferenceCache(
            cache_key="test_cache_key",
            preference_data={"language": "python", "style": "concise"},
            expires_at=expires_at,
        )

        assert cache.cache_key == "test_cache_key"
        assert cache.preference_data["language"] == "python"
        assert cache.preference_data["style"] == "concise"
        assert cache.expires_at == expires_at
        assert cache.hit_count == 0

    def test_cache_key_validation(self):
        """Test cache key validation"""
        expires_at = datetime.now() + timedelta(hours=1)

        # Valid cache key
        cache = PreferenceCache(cache_key="valid_cache_key", preference_data={}, expires_at=expires_at)
        assert cache.cache_key == "valid_cache_key"

        # Invalid cache key (too short)
        with pytest.raises(ValueError, match="Cache key must be at least 5 characters"):
            PreferenceCache(cache_key="abcd", preference_data={}, expires_at=expires_at)


class TestDefaultPreferences:
    """Test default preferences"""

    def test_get_default_preferences(self):
        """Test getting default preferences for a user"""
        user_id = "test_user"
        preferences = DefaultPreferences.get_default_preferences(user_id)

        assert len(preferences) == 8  # Number of default preferences

        # Check for expected preferences
        preference_keys = [p.preference_key for p in preferences]
        assert "language" in preference_keys
        assert "style" in preference_keys
        assert "detail_level" in preference_keys
        assert "code_formatting" in preference_keys

        # Check preference values
        language_pref = next(p for p in preferences if p.preference_key == "language")
        assert language_pref.preference_value == "python"
        assert language_pref.user_id == user_id
        assert language_pref.category == "development"

        style_pref = next(p for p in preferences if p.preference_key == "style")
        assert style_pref.preference_value == "concise"
        assert style_pref.category == "communication"

    def test_default_preference_structure(self):
        """Test default preference structure"""
        user_id = "test_user"
        preferences = DefaultPreferences.get_default_preferences(user_id)

        for preference in preferences:
            # Check required fields
            assert preference.preference_id.startswith(user_id)
            assert preference.user_id == user_id
            assert preference.preference_key in DefaultPreferences.DEFAULT_PREFERENCES
            assert preference.preference_type == "string"
            assert preference.is_active is True

            # Check that preference value matches default
            default_config = DefaultPreferences.DEFAULT_PREFERENCES[preference.preference_key]
            assert preference.preference_value == default_config["value"]
            assert preference.category == default_config["category"]
            assert preference.description == default_config["description"]


class TestUserPreferenceManager:
    """Test user preference manager"""

    def test_manager_creation(self):
        """Test manager creation"""
        manager = UserPreferenceManager(cache_ttl=300)
        assert manager.cache_ttl == 300
        assert len(manager._cache) == 0
        assert len(manager._preference_sets) == 0

    def test_get_user_preferences_new_user(self):
        """Test getting preferences for a new user"""
        manager = UserPreferenceManager()
        user_id = "new_user"

        preferences = manager.get_user_preferences(user_id)

        # Should return default preferences
        assert "language" in preferences
        assert "style" in preferences
        assert "detail_level" in preferences
        assert preferences["language"] == "python"
        assert preferences["style"] == "concise"

    def test_set_user_preference(self):
        """Test setting a user preference"""
        manager = UserPreferenceManager()
        user_id = "test_user"

        preference = manager.set_user_preference(
            user_id=user_id,
            preference_key="custom_setting",
            preference_value="custom_value",
            category="custom",
            description="Custom preference for testing",
        )

        assert preference.user_id == user_id
        assert preference.preference_key == "custom_setting"
        assert preference.preference_value == "custom_value"
        assert preference.category == "custom"
        assert preference.description == "Custom preference for testing"

        # Verify preference is saved
        saved_preferences = manager.get_user_preferences(user_id)
        assert "custom_setting" in saved_preferences
        assert saved_preferences["custom_setting"] == "custom_value"

    def test_get_user_preference(self):
        """Test getting a specific user preference"""
        manager = UserPreferenceManager()
        user_id = "test_user"

        # Set a preference
        manager.set_user_preference(user_id, "test_key", "test_value")

        # Get the preference
        value = manager.get_user_preference(user_id, "test_key")
        assert value == "test_value"

        # Get non-existent preference with default
        default_value = manager.get_user_preference(user_id, "nonexistent", "default")
        assert default_value == "default"

    def test_delete_user_preference(self):
        """Test deleting a user preference"""
        manager = UserPreferenceManager()
        user_id = "test_user"

        # Set a preference
        manager.set_user_preference(user_id, "to_delete", "value")

        # Verify it exists
        preferences = manager.get_user_preferences(user_id)
        assert "to_delete" in preferences

        # Delete the preference
        success = manager.delete_user_preference(user_id, "to_delete")
        assert success is True

        # Verify it's gone
        preferences = manager.get_user_preferences(user_id)
        assert "to_delete" not in preferences

    def test_get_preferences_by_category(self):
        """Test getting preferences by category"""
        manager = UserPreferenceManager()
        user_id = "test_user"

        # Set preferences in different categories
        manager.set_user_preference(user_id, "dev_pref", "value1", "development")
        manager.set_user_preference(user_id, "comm_pref", "value2", "communication")

        # Get development preferences
        dev_prefs = manager.get_preferences_by_category(user_id, "development")
        assert "dev_pref" in dev_prefs
        assert "comm_pref" not in dev_prefs

        # Get communication preferences
        comm_prefs = manager.get_preferences_by_category(user_id, "communication")
        assert "comm_pref" in comm_prefs
        assert "dev_pref" not in comm_prefs

    def test_update_preferences_batch(self):
        """Test updating multiple preferences at once"""
        manager = UserPreferenceManager()
        user_id = "test_user"

        batch_preferences = {"batch_key1": "value1", "batch_key2": "value2", "batch_key3": "value3"}

        updated_preferences = manager.update_preferences_batch(user_id, batch_preferences)

        assert len(updated_preferences) == 3

        # Verify all preferences were set
        preferences = manager.get_user_preferences(user_id)
        for key, value in batch_preferences.items():
            assert key in preferences
            assert preferences[key] == value

    def test_cache_functionality(self):
        """Test preference caching"""
        manager = UserPreferenceManager(cache_ttl=300)
        user_id = "test_user"

        # First call - should cache
        preferences1 = manager.get_user_preferences(user_id)
        assert len(manager._cache) == 1

        # Second call - should use cache
        preferences2 = manager.get_user_preferences(user_id)
        assert preferences1 == preferences2

        # Check cache hit
        cache_key = f"preferences_{user_id}"
        cache_entry = manager._cache[cache_key]
        assert cache_entry.hit_count > 0

    def test_cache_invalidation(self):
        """Test cache invalidation"""
        manager = UserPreferenceManager()
        user_id = "test_user"

        # Get preferences (creates cache)
        manager.get_user_preferences(user_id)
        assert len(manager._cache) == 1

        # Set a preference (should invalidate cache)
        manager.set_user_preference(user_id, "new_pref", "value")
        assert len(manager._cache) == 0

        # Get preferences again (should recreate cache)
        manager.get_user_preferences(user_id)
        assert len(manager._cache) == 1


class TestResponseCustomizer:
    """Test response customizer"""

    def test_customizer_creation(self):
        """Test customizer creation"""
        manager = UserPreferenceManager()
        customizer = ResponseCustomizer(manager)
        assert customizer.preference_manager == manager

    def test_customize_text_response_concise_style(self):
        """Test text response customization with concise style"""
        manager = UserPreferenceManager()
        customizer = ResponseCustomizer(manager)
        user_id = "test_user"

        # Set concise style preference
        manager.set_user_preference(user_id, "style", "concise")

        # Long response
        long_response = "This is sentence one. This is sentence two. This is sentence three. This is sentence four. This is sentence five."
        customized = customizer.customize_response(user_id, long_response, "text")

        # Should be truncated to first 3 sentences
        assert customized.count(".") <= 3

    def test_customize_text_response_detailed_style(self):
        """Test text response customization with detailed style"""
        manager = UserPreferenceManager()
        customizer = ResponseCustomizer(manager)
        user_id = "test_user"

        # Set detailed style preference
        manager.set_user_preference(user_id, "style", "detailed")

        # Short response
        short_response = "This is a short response."
        customized = customizer.customize_response(user_id, short_response, "text")

        # Should add detail prompt
        assert "For more detailed information" in customized

    def test_customize_text_response_detail_level(self):
        """Test text response customization with detail level preference"""
        manager = UserPreferenceManager()
        customizer = ResponseCustomizer(manager)
        user_id = "test_user"

        # Set high detail level
        manager.set_user_preference(user_id, "detail_level", "high")

        # Medium length response
        response = "This is a medium length response that should trigger the high detail level customization."
        customized = customizer.customize_response(user_id, response, "text")

        # Should add detail prompt
        assert "Would you like me to provide more detailed information" in customized

    def test_customize_code_response_black_formatting(self):
        """Test code response customization with Black formatting"""
        manager = UserPreferenceManager()
        customizer = ResponseCustomizer(manager)
        user_id = "test_user"

        # Set Black formatting preference
        manager.set_user_preference(user_id, "code_formatting", "black")

        code_response = "def hello():\n    print('Hello, world!')"
        customized = customizer.customize_response(user_id, code_response, "code")

        # Should add Black formatting comment
        assert "Code formatted with Black" in customized

    def test_customize_code_response_pep8_formatting(self):
        """Test code response customization with PEP 8 formatting"""
        manager = UserPreferenceManager()
        customizer = ResponseCustomizer(manager)
        user_id = "test_user"

        # Set PEP 8 formatting preference
        manager.set_user_preference(user_id, "code_formatting", "pep8")

        code_response = "def hello():\n    print('Hello, world!')"
        customized = customizer.customize_response(user_id, code_response, "code")

        # Should add PEP 8 comment
        assert "Code follows PEP 8 style guide" in customized

    def test_customize_code_response_explicit_error_handling(self):
        """Test code response customization with explicit error handling"""
        manager = UserPreferenceManager()
        customizer = ResponseCustomizer(manager)
        user_id = "test_user"

        # Set explicit error handling preference
        manager.set_user_preference(user_id, "error_handling", "explicit")

        code_response = "def hello():\n    print('Hello, world!')"
        customized = customizer.customize_response(user_id, code_response, "code")

        # Should add error handling
        assert "try:" in customized
        assert "except Exception as e:" in customized

    def test_customize_documentation_response_markdown(self):
        """Test documentation response customization with markdown"""
        manager = UserPreferenceManager()
        customizer = ResponseCustomizer(manager)
        user_id = "test_user"

        # Set markdown documentation style
        manager.set_user_preference(user_id, "documentation_style", "markdown")

        doc_response = "This is documentation content."
        customized = customizer.customize_response(user_id, doc_response, "documentation")

        # Should add markdown header
        assert "# Documentation" in customized

    def test_customize_documentation_response_rst(self):
        """Test documentation response customization with RST"""
        manager = UserPreferenceManager()
        customizer = ResponseCustomizer(manager)
        user_id = "test_user"

        # Set RST documentation style
        manager.set_user_preference(user_id, "documentation_style", "rst")

        doc_response = "This is documentation content."
        customized = customizer.customize_response(user_id, doc_response, "documentation")

        # Should add RST header
        assert "Documentation\n============" in customized

    def test_customize_response_unknown_type(self):
        """Test response customization with unknown type"""
        manager = UserPreferenceManager()
        customizer = ResponseCustomizer(manager)
        user_id = "test_user"

        response = "This is a test response."
        customized = customizer.customize_response(user_id, response, "unknown_type")

        # Should return unchanged response
        assert customized == response


class TestPreferencePerformanceMetrics:
    """Test preference performance metrics"""

    def test_metrics_creation(self):
        """Test metrics creation"""
        metrics = PreferencePerformanceMetrics(
            total_requests=100, cache_hits=80, cache_misses=20, avg_lookup_time=0.05, lookup_times=[0.04, 0.05, 0.06]
        )

        assert metrics.total_requests == 100
        assert metrics.cache_hits == 80
        assert metrics.cache_misses == 20
        assert metrics.avg_lookup_time == 0.05
        assert len(metrics.lookup_times) == 3

    def test_cache_hit_rate_calculation(self):
        """Test cache hit rate calculation"""
        # With hits and misses
        metrics = PreferencePerformanceMetrics(cache_hits=80, cache_misses=20)
        assert metrics.cache_hit_rate == 0.8

        # With no requests
        metrics = PreferencePerformanceMetrics()
        assert metrics.cache_hit_rate == 0.0

    def test_avg_lookup_time_ms(self):
        """Test average lookup time in milliseconds"""
        metrics = PreferencePerformanceMetrics(avg_lookup_time=0.05)
        assert metrics.avg_lookup_time_ms == 50.0


if __name__ == "__main__":
    pytest.main([__file__])
