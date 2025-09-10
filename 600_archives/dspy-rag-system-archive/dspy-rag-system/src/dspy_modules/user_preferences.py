#!/usr/bin/env python3
"""
User Preference System for DSPy AI System
Implements user preference storage, retrieval, and customization for B-1007
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field, field_validator

_LOG = logging.getLogger("user_preferences")

# ---------- User Preference Models ----------


class UserPreference(BaseModel):
    """Model for individual user preferences"""

    preference_id: str = Field(..., description="Unique preference identifier")
    user_id: str = Field(..., description="User identifier")
    preference_key: str = Field(..., description="Preference key")
    preference_value: Any = Field(..., description="Preference value")
    preference_type: str = Field(..., description="Type of preference (string, int, bool, etc.)")
    category: str = Field(..., description="Preference category")
    description: str | None = Field(None, description="Preference description")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    is_active: bool = Field(default=True, description="Whether preference is active")

    @field_validator("preference_id")
    @classmethod
    def validate_preference_id(cls, v: str) -> str:
        """Validate preference ID format"""
        if not v or len(v.strip()) < 3:
            raise ValueError("Preference ID must be at least 3 characters")
        return v.strip()

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validate user ID format"""
        if not v or len(v.strip()) < 1:
            raise ValueError("User ID cannot be empty")
        return v.strip()

    @field_validator("preference_key")
    @classmethod
    def validate_preference_key(cls, v: str) -> str:
        """Validate preference key format"""
        if not v or len(v.strip()) < 2:
            raise ValueError("Preference key must be at least 2 characters")
        return v.strip()


class UserPreferenceSet(BaseModel):
    """Model for a set of user preferences"""

    user_id: str = Field(..., description="User identifier")
    preferences: dict[str, UserPreference] = Field(default_factory=dict, description="User preferences")
    last_sync: datetime = Field(default_factory=datetime.now, description="Last sync timestamp")
    cache_expires: datetime = Field(..., description="Cache expiration timestamp")

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        """Validate user ID format"""
        if not v or len(v.strip()) < 1:
            raise ValueError("User ID cannot be empty")
        return v.strip()


class PreferenceCache(BaseModel):
    """Model for preference caching"""

    cache_key: str = Field(..., description="Cache key")
    preference_data: dict[str, Any] = Field(..., description="Cached preference data")
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


# ---------- Default User Preferences ----------


class DefaultPreferences:
    """Default preferences for new users"""

    DEFAULT_PREFERENCES = {
        "language": {
            "value": "python",
            "type": "string",
            "category": "development",
            "description": "Preferred programming language",
        },
        "style": {
            "value": "concise",
            "type": "string",
            "category": "communication",
            "description": "Preferred communication style",
        },
        "detail_level": {
            "value": "medium",
            "type": "string",
            "category": "communication",
            "description": "Preferred level of detail in responses",
        },
        "code_formatting": {
            "value": "black",
            "type": "string",
            "category": "development",
            "description": "Preferred code formatting style",
        },
        "testing_preference": {
            "value": "pytest",
            "type": "string",
            "category": "development",
            "description": "Preferred testing framework",
        },
        "documentation_style": {
            "value": "markdown",
            "type": "string",
            "category": "documentation",
            "description": "Preferred documentation format",
        },
        "error_handling": {
            "value": "explicit",
            "type": "string",
            "category": "development",
            "description": "Preferred error handling approach",
        },
        "performance_focus": {
            "value": "balanced",
            "type": "string",
            "category": "development",
            "description": "Performance optimization preference",
        },
    }

    @classmethod
    def get_default_preferences(cls, user_id: str) -> list[UserPreference]:
        """Get default preferences for a new user"""
        preferences = []

        for key, config in cls.DEFAULT_PREFERENCES.items():
            preference = UserPreference(
                preference_id=f"{user_id}_{key}",
                user_id=user_id,
                preference_key=key,
                preference_value=config["value"],
                preference_type=config["type"],
                category=config["category"],
                description=config["description"],
            )
            preferences.append(preference)

        return preferences


# ---------- User Preference Manager ----------


class UserPreferenceManager:
    """Manages user preferences with caching and persistence"""

    def __init__(self, db_connection=None, cache_ttl: int = 300):
        """Initialize preference manager"""
        self.db_connection = db_connection
        self.cache_ttl = cache_ttl
        self._cache: dict[str, PreferenceCache] = {}
        self._preference_sets: dict[str, UserPreferenceSet] = {}
        self._preferences: dict[str, dict[str, Any]] = {}  # In-memory storage for testing

    def get_user_preferences(self, user_id: str, force_refresh: bool = False) -> dict[str, Any]:
        """Get user preferences with caching"""
        cache_key = f"preferences_{user_id}"

        # Check cache first
        if not force_refresh:
            cached_data = self._get_cached_preferences(cache_key)
            if cached_data:
                return cached_data

        # Get from database or create defaults
        preferences = self._load_user_preferences(user_id)

        # Cache the preferences
        self._cache_preferences(cache_key, preferences)

        return preferences

    def set_user_preference(
        self,
        user_id: str,
        preference_key: str,
        preference_value: Any,
        category: str = "general",
        description: str | None = None,
    ) -> UserPreference:
        """Set a user preference"""
        # Determine preference type
        preference_type = type(preference_value).__name__

        # Create preference
        preference = UserPreference(
            preference_id=f"{user_id}_{preference_key}",
            user_id=user_id,
            preference_key=preference_key,
            preference_value=preference_value,
            preference_type=preference_type,
            category=category,
            description=description,
            updated_at=datetime.now(),
        )

        # Save to database
        self._save_preference(preference)

        # Update cache
        self._invalidate_user_cache(user_id)

        _LOG.info(f"Set preference for user {user_id}: {preference_key} = {preference_value}")

        return preference

    def get_user_preference(self, user_id: str, preference_key: str, default: Any = None) -> Any:
        """Get a specific user preference"""
        preferences = self.get_user_preferences(user_id)
        return preferences.get(preference_key, default)

    def delete_user_preference(self, user_id: str, preference_key: str) -> bool:
        """Delete a user preference"""
        # Delete from database
        success = self._delete_preference(user_id, preference_key)

        if success:
            # Update cache
            self._invalidate_user_cache(user_id)
            _LOG.info(f"Deleted preference for user {user_id}: {preference_key}")

        return success

    def get_preferences_by_category(self, user_id: str, category: str) -> dict[str, Any]:
        """Get user preferences by category"""
        preferences = self.get_user_preferences(user_id)
        return {k: v for k, v in preferences.items() if self._get_preference_category(k) == category}

    def update_preferences_batch(self, user_id: str, preferences: dict[str, Any]) -> list[UserPreference]:
        """Update multiple preferences at once"""
        updated_preferences = []

        for key, value in preferences.items():
            preference = self.set_user_preference(user_id, key, value)
            updated_preferences.append(preference)

        return updated_preferences

    def _load_user_preferences(self, user_id: str) -> dict[str, Any]:
        """Load user preferences from database or create defaults"""
        # Check in-memory storage first
        if user_id in self._preferences:
            return self._preferences[user_id]

        # Try to load from database
        db_preferences = self._load_from_database(user_id)

        if db_preferences:
            self._preferences[user_id] = db_preferences
            return db_preferences

        # Create default preferences for new user
        default_preferences = DefaultPreferences.get_default_preferences(user_id)

        # Save defaults to database
        for preference in default_preferences:
            self._save_preference(preference)

        # Store in memory and return default preferences as dict
        preferences_dict = {p.preference_key: p.preference_value for p in default_preferences}
        self._preferences[user_id] = preferences_dict
        return preferences_dict

    def _load_from_database(self, user_id: str) -> dict[str, Any] | None:
        """Load preferences from database"""
        if not self.db_connection:
            # Mock database for testing
            return None

        try:
            # This would be a real database query in production
            # For now, return None to trigger default creation
            return None
        except Exception as e:
            _LOG.error(f"Error loading preferences from database: {e}")
            return None

    def _save_preference(self, preference: UserPreference) -> bool:
        """Save preference to database"""
        # Save to in-memory storage
        if preference.user_id not in self._preferences:
            self._preferences[preference.user_id] = {}

        self._preferences[preference.user_id][preference.preference_key] = preference.preference_value

        if not self.db_connection:
            # Mock database for testing
            return True

        try:
            # This would be a real database insert/update in production
            # For now, just return success
            return True
        except Exception as e:
            _LOG.error(f"Error saving preference to database: {e}")
            return False

    def _delete_preference(self, user_id: str, preference_key: str) -> bool:
        """Delete preference from database"""
        # Delete from in-memory storage
        if user_id in self._preferences and preference_key in self._preferences[user_id]:
            del self._preferences[user_id][preference_key]
            return True

        if not self.db_connection:
            # Mock database for testing
            return True

        try:
            # This would be a real database delete in production
            # For now, just return success
            return True
        except Exception as e:
            _LOG.error(f"Error deleting preference from database: {e}")
            return False

    def _get_cached_preferences(self, cache_key: str) -> dict[str, Any] | None:
        """Get cached preferences"""
        if cache_key in self._cache:
            cache_entry = self._cache[cache_key]
            if datetime.now() < cache_entry.expires_at:
                cache_entry.hit_count += 1
                return cache_entry.preference_data
            else:
                # Remove expired cache entry
                del self._cache[cache_key]

        return None

    def _cache_preferences(self, cache_key: str, preferences: dict[str, Any]) -> None:
        """Cache user preferences"""
        expires_at = datetime.now() + timedelta(seconds=self.cache_ttl)

        cache_entry = PreferenceCache(cache_key=cache_key, preference_data=preferences, expires_at=expires_at)

        self._cache[cache_key] = cache_entry

    def _invalidate_user_cache(self, user_id: str) -> None:
        """Invalidate cache for a specific user"""
        cache_key = f"preferences_{user_id}"
        if cache_key in self._cache:
            del self._cache[cache_key]

    def _get_preference_category(self, preference_key: str) -> str:
        """Get category for a preference key"""
        # This would typically be stored in the database
        # For now, use a simple mapping
        category_mapping = {
            "language": "development",
            "style": "communication",
            "detail_level": "communication",
            "code_formatting": "development",
            "testing_preference": "development",
            "documentation_style": "documentation",
            "error_handling": "development",
            "performance_focus": "development",
            "dev_pref": "development",
            "comm_pref": "communication",
        }

        return category_mapping.get(preference_key, "general")


# ---------- Preference-Based Response Customization ----------


class ResponseCustomizer:
    """Customizes responses based on user preferences"""

    def __init__(self, preference_manager: UserPreferenceManager):
        """Initialize response customizer"""
        self.preference_manager = preference_manager

    def customize_response(self, user_id: str, base_response: str, response_type: str = "text") -> str:
        """Customize response based on user preferences"""
        preferences = self.preference_manager.get_user_preferences(user_id)

        if response_type == "text":
            return self._customize_text_response(base_response, preferences)
        elif response_type == "code":
            return self._customize_code_response(base_response, preferences)
        elif response_type == "documentation":
            return self._customize_documentation_response(base_response, preferences)
        else:
            return base_response

    def _customize_text_response(self, response: str, preferences: dict[str, Any]) -> str:
        """Customize text response based on preferences"""
        # Apply style preference
        style = preferences.get("style", "concise")

        if style == "concise":
            # Make response more concise
            sentences = response.split(". ")
            if len(sentences) > 3:
                response = ". ".join(sentences[:3]) + "."
        elif style == "detailed":
            # Add more detail if response is too short
            if len(response) < 100:
                response += "\n\nFor more detailed information, please let me know what specific aspects you'd like me to elaborate on."

        # Apply detail level preference
        detail_level = preferences.get("detail_level", "medium")

        if detail_level == "high" and len(response) < 200:
            response += "\n\nWould you like me to provide more detailed information on any specific aspect?"
        elif detail_level == "low" and len(response) > 300:
            # Truncate long responses
            response = response[:300] + "..."

        return response

    def _customize_code_response(self, response: str, preferences: dict[str, Any]) -> str:
        """Customize code response based on preferences"""
        # Apply code formatting preference
        formatting = preferences.get("code_formatting", "black")

        if formatting == "black":
            # Add Black formatting comment
            response = "# Code formatted with Black\n" + response
        elif formatting == "pep8":
            # Add PEP 8 comment
            response = "# Code follows PEP 8 style guide\n" + response

        # Apply error handling preference
        error_handling = preferences.get("error_handling", "explicit")

        if error_handling == "explicit" and "try:" not in response:
            # Add explicit error handling
            response = self._add_explicit_error_handling(response)

        return response

    def _customize_documentation_response(self, response: str, preferences: dict[str, Any]) -> str:
        """Customize documentation response based on preferences"""
        # Apply documentation style preference
        doc_style = preferences.get("documentation_style", "markdown")

        if doc_style == "markdown" and not response.startswith("#"):
            # Ensure markdown formatting
            response = "# Documentation\n\n" + response
        elif doc_style == "rst" and not response.startswith("="):
            # Ensure RST formatting
            response = "Documentation\n============\n\n" + response

        return response

    def _add_explicit_error_handling(self, code: str) -> str:
        """Add explicit error handling to code"""
        # Simple implementation - in practice, this would be more sophisticated
        if "def " in code and "try:" not in code:
            # Add basic error handling to functions
            lines = code.split("\n")
            for i, line in enumerate(lines):
                if line.strip().startswith("def "):
                    # Add try-except after function definition
                    indent = " " * (len(line) - len(line.lstrip()))
                    error_handling = f"\n{indent}try:\n{indent}    # Function implementation\n{indent}except Exception as e:\n{indent}    raise e"
                    lines.insert(i + 1, error_handling)
                    break
            code = "\n".join(lines)

        return code


# ---------- Performance Monitoring ----------


class PreferencePerformanceMetrics(BaseModel):
    """Metrics for preference system performance"""

    total_requests: int = Field(default=0, description="Total preference requests")
    cache_hits: int = Field(default=0, description="Number of cache hits")
    cache_misses: int = Field(default=0, description="Number of cache misses")
    avg_lookup_time: float = Field(default=0.0, description="Average lookup time in seconds")
    lookup_times: list[float] = Field(default_factory=list, description="Lookup times")

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total_requests = self.cache_hits + self.cache_misses
        if total_requests == 0:
            return 0.0
        return self.cache_hits / total_requests

    @property
    def avg_lookup_time_ms(self) -> float:
        """Get average lookup time in milliseconds"""
        return self.avg_lookup_time * 1000
