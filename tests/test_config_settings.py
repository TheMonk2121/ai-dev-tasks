from __future__ import annotations
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest
import yaml
from pydantic import ValidationError
from src.config.models import RAG, Database, Eval, Observability
from src.config.settings import Settings, get_settings, reload_settings, reset_settings
import sys
"""Tests for the centralized configuration system."""

class TestSettings:
    """Test the Settings class and configuration loading."""

    def setup_method(self):
        """Reset settings before each test."""
        reset_settings()

    def teardown_method(self):
        """Reset settings after each test."""
        reset_settings()

    def test_default_settings(self):
        """Test that default settings are loaded correctly."""
        # Clear environment variables that might affect the test
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()

            # Test core settings
            assert settings.env == "dev"
            assert isinstance(settings.root_dir, Path)

            # Test domain settings have defaults
            assert isinstance(settings.db, Database)
            assert isinstance(settings.rag, RAG)
            assert isinstance(settings.eval, Eval)
            assert isinstance(settings.obs, Observability)

    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        with patch.dict(
            os.environ,
            {
                "APP_ENV": "test",
                "APP_DB__POOL_SIZE": "16",
                "APP_RAG__TOPK": "50",
            },
        ):
            settings = Settings()

            assert settings.env == "test"
            assert settings.db.pool_size == 16
            assert settings.rag.topk == 50

    def test_nested_environment_variables(self):
        """Test nested environment variable access."""
        with patch.dict(
            os.environ,
            {
                "APP_DB__POOL_SIZE": "32",
                "APP_RAG__CHUNK_SIZE": "600",
                "APP_EVAL__PRECISION_THRESHOLD": "0.25",
            },
        ):
            settings = Settings()

            assert settings.db.pool_size == 32
            assert settings.rag.chunk_size == 600
            assert settings.eval.precision_threshold == 0.25

    def test_yaml_configuration_loading(self):
        """Test YAML configuration file loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "configs"
            config_dir.mkdir()

            # Create base.yaml
            base_config = {
                "env": "test",
                "db": {"pool_size": 4},
                "rag": {"topk": 10},
            }
            with open(config_dir / "base.yaml", "w") as f:
                yaml.dump(base_config, f)

            # Create test.yaml
            test_config = {
                "rag": {"topk": 20},
                "eval": {"use_bedrock": False},
            }
            with open(config_dir / "test.yaml", "w") as f:
                yaml.dump(test_config, f)

            with patch.dict(os.environ, {"APP_ENV": "test"}, clear=True):
                # Mock the Path constructor to return our test directory
                original_path = Path

                def mock_path_constructor(path_str):
                    if path_str == "configs/base.yaml":
                        return config_dir / "base.yaml"
                    elif path_str == "configs/test.yaml":
                        return config_dir / "test.yaml"
                    else:
                        return original_path(path_str)

                with patch("src.config.settings.Path", side_effect=mock_path_constructor):
                    settings = Settings()

                    # Should inherit from base.yaml
                    assert settings.db.pool_size == 4
                    # Should override from test.yaml
                    assert settings.rag.topk == 20
                    assert settings.eval.use_bedrock is False

    def test_validation_errors(self):
        """Test that validation errors are raised for invalid values."""
        with patch.dict(
            os.environ,
            {
                "APP_DB__POOL_SIZE": "0",  # Invalid: must be >= 1
                "APP_RAG__TOPK": "150",  # Invalid: must be <= 100
            },
        ):
            with pytest.raises(ValidationError):
                Settings()

    def test_secret_fields_not_logged(self):
        """Test that secret fields are excluded from safe dumps."""
        settings = Settings()
        safe_dump = settings.model_dump_safe()

        # Security secrets should be excluded
        assert "openai_api_key" not in safe_dump.get("security", {})
        assert "aws_access_key_id" not in safe_dump.get("security", {})
        assert "aws_secret_access_key" not in safe_dump.get("security", {})

        # Observability secrets should be excluded
        assert "logfire_token" not in safe_dump.get("obs", {})

    def test_get_settings_singleton(self):
        """Test that get_settings returns the same instance."""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_reset_settings(self):
        """Test that reset_settings clears the singleton."""
        settings1 = get_settings()
        reset_settings()
        settings2 = get_settings()

        assert settings1 is not settings2

    def test_reload_settings(self):
        """Test that reload_settings creates a new instance."""
        settings1 = get_settings()
        settings2 = reload_settings()

        assert settings1 is not settings2
        assert get_settings() is settings2

class TestConfigurationPrecedence:
    """Test configuration precedence order."""

    def setup_method(self):
        """Reset settings before each test."""
        reset_settings()

    def teardown_method(self):
        """Reset settings after each test."""
        reset_settings()

    def test_precedence_order(self):
        """Test that configuration sources are applied in correct order."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir) / "configs"
            config_dir.mkdir()

            # Base YAML
            base_config = {"rag": {"topk": 10}}
            with open(config_dir / "base.yaml", "w") as f:
                yaml.dump(base_config, f)

            # Environment YAML
            env_config = {"rag": {"topk": 20}}
            with open(config_dir / "test.yaml", "w") as f:
                yaml.dump(env_config, f)

            with patch.dict(
                os.environ,
                {
                    "APP_ENV": "test",
                    "APP_RAG__TOPK": "30",  # Should override YAML
                },
            ):
                # Mock the Path constructor to return our test directory
                original_path = Path

                def mock_path_constructor(path_str):
                    if path_str == "configs/base.yaml":
                        return config_dir / "base.yaml"
                    elif path_str == "configs/test.yaml":
                        return config_dir / "test.yaml"
                    else:
                        return original_path(path_str)

                with patch("src.config.settings.Path", side_effect=mock_path_constructor):
                    settings = Settings()

                    # Environment variable should win
                    assert settings.rag.topk == 30

class TestModelValidation:
    """Test individual model validation."""

    def test_database_validation(self):
        """Test Database model validation."""
        # Valid database config - use default dsn
        db = Database()
        assert db.pool_size == 8
        assert db.timeout_ms == 5000

        # Invalid pool size
        with pytest.raises(ValidationError):
            Database(pool_size=0)

        # Invalid timeout
        with pytest.raises(ValidationError):
            Database(timeout_ms=50)

    def test_rag_validation(self):
        """Test RAG model validation."""
        # Valid RAG config
        rag = RAG()
        assert rag.topk == 25
        assert rag.chunk_size == 450
        assert rag.overlap_ratio == 0.10

        # Invalid topk
        with pytest.raises(ValidationError):
            RAG(topk=150)

        # Invalid chunk size
        with pytest.raises(ValidationError):
            RAG(chunk_size=50)

        # Invalid overlap ratio
        with pytest.raises(ValidationError):
            RAG(overlap_ratio=0.8)

    def test_eval_validation(self):
        """Test Eval model validation."""
        # Valid eval config
        eval_config = Eval()
        assert eval_config.driver == "dspy_rag"
        assert eval_config.precision_threshold == 0.20

        # Invalid driver
        with pytest.raises(ValidationError):
            Eval(driver="invalid_driver")  # type: ignore[assignment]

        # Invalid threshold
        with pytest.raises(ValidationError):
            Eval(precision_threshold=1.5)

@pytest.fixture(autouse=True)
def reset_settings_fixture():
    """Reset settings before and after each test."""
    reset_settings()
    yield
    reset_settings()
