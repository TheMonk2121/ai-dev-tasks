#!/usr/bin/env python3
"""
Tests for secrets management functionality.
"""

import os
from importlib import import_module
from unittest.mock import MagicMock, patch

import pytest

# Dynamic import to satisfy static analyzers and work in pytest/runtime
try:
    sm = import_module("utils.secrets_manager")
except ModuleNotFoundError:
    sm = import_module("utils.secrets_manager")

SecretConfig = sm.SecretConfig
SecretsManager = sm.SecretsManager
setup_secrets_interactive = sm.setup_secrets_interactive
validate_startup_secrets = sm.validate_startup_secrets


class TestSecretConfig:
    """Test SecretConfig dataclass"""

    @pytest.mark.tier2
    @pytest.mark.unit
    def test_basic_config(self):
        """Test basic SecretConfig creation"""
        config = SecretConfig(name="TEST_SECRET", required=True, description="Test secret")

        assert config.name == "TEST_SECRET"
        assert config.required is True
        assert config.description == "Test secret"
        assert config.sensitive is True

    def test_optional_config(self):
        """Test optional SecretConfig creation"""
        config = SecretConfig(name="OPTIONAL_SECRET", required=False, default="default_value", sensitive=False)

        assert config.name == "OPTIONAL_SECRET"
        assert config.required is False
        assert config.default == "default_value"
        assert config.sensitive is False


class TestSecretsManager:
    """Test SecretsManager functionality"""

    def setup_method(self):
        """Setup for each test"""
        self.manager = SecretsManager("test-app")
        self.test_secret = "TEST_SECRET"
        self.test_value = "test_value_123"

    def teardown_method(self):
        """Cleanup after each test"""
        # Clean up any test secrets
        self.manager.delete_secret(self.test_secret)

    @pytest.mark.tier2
    @pytest.mark.unit
    def test_init(self):
        """Test SecretsManager initialization"""
        assert self.manager.app_name == "test-app"
        assert isinstance(self.manager.secrets_cache, dict)
        assert isinstance(self.manager.validation_cache, dict)

    @patch("utils.secrets_manager.KEYRING_AVAILABLE", False)
    def test_init_without_keyring(self):
        """Test initialization without keyring"""
        manager = SecretsManager()
        assert manager.keyring_available is False

    def test_set_get_secret_environment(self):
        """Test setting and getting secrets from environment"""
        # Set secret
        assert self.manager.set_secret(self.test_secret, self.test_value, use_keyring=False)

        # Get secret
        retrieved = self.manager.get_secret(self.test_secret, use_keyring=False)
        assert retrieved == self.test_value

    def test_get_nonexistent_secret(self):
        """Test getting a secret that doesn't exist"""
        result = self.manager.get_secret("NONEXISTENT_SECRET")
        assert result is None

    def test_delete_secret(self):
        """Test deleting a secret"""
        # Set secret first
        self.manager.set_secret(self.test_secret, self.test_value, use_keyring=False)

        # Verify it exists
        assert self.manager.get_secret(self.test_secret) == self.test_value

        # Delete it
        assert self.manager.delete_secret(self.test_secret, use_keyring=False)

        # Verify it's gone
        assert self.manager.get_secret(self.test_secret) is None

    def test_generate_secure_secret(self):
        """Test secure secret generation"""
        secret = self.manager.generate_secure_secret(32)
        assert len(secret) == 32
        assert isinstance(secret, str)

    def test_hash_secret(self):
        """Test secret hashing"""
        original_secret = "my_secret_password"
        hash_string = self.manager.hash_secret(original_secret)

        # Should contain salt and hash
        assert ":" in hash_string
        parts = hash_string.split(":")
        assert len(parts) == 2

        # Should verify correctly
        assert self.manager.verify_secret_hash(original_secret, hash_string)
        assert not self.manager.verify_secret_hash("wrong_password", hash_string)

    def test_validate_secret_success(self):
        """Test successful secret validation"""
        config = SecretConfig(name=self.test_secret, required=True, min_length=5, max_length=20)

        # Set a valid secret
        self.manager.set_secret(self.test_secret, "valid_secret", use_keyring=False)

        # Should validate successfully
        assert self.manager.validate_secret(self.test_secret, config)

    def test_validate_secret_missing_required(self):
        """Test validation of missing required secret"""
        config = SecretConfig(name=self.test_secret, required=True)

        # Should fail validation
        assert not self.manager.validate_secret(self.test_secret, config)

    def test_validate_secret_optional_with_default(self):
        """Test validation of optional secret with default"""
        config = SecretConfig(name=self.test_secret, required=False, default="default_value")

        # Should pass validation (uses default)
        assert self.manager.validate_secret(self.test_secret, config)

    def test_validate_secret_too_short(self):
        """Test validation of secret that's too short"""
        config = SecretConfig(name=self.test_secret, required=True, min_length=10)

        # Set a short secret
        self.manager.set_secret(self.test_secret, "short", use_keyring=False)

        # Should fail validation
        assert not self.manager.validate_secret(self.test_secret, config)

    def test_validate_secret_too_long(self):
        """Test validation of secret that's too long"""
        config = SecretConfig(name=self.test_secret, required=True, max_length=5)

        # Set a long secret
        self.manager.set_secret(self.test_secret, "very_long_secret", use_keyring=False)

        # Should fail validation
        assert not self.manager.validate_secret(self.test_secret, config)

    def test_validate_secret_regex(self):
        """Test validation with regex pattern"""
        config = SecretConfig(name=self.test_secret, required=True, validation_regex=r"^https?://.*")

        # Set a valid URL
        self.manager.set_secret(self.test_secret, "http://localhost:8080", use_keyring=False)
        assert self.manager.validate_secret(self.test_secret, config)

        # Set an invalid URL
        self.manager.set_secret(self.test_secret, "not_a_url", use_keyring=False)
        assert not self.manager.validate_secret(self.test_secret, config)

    def test_validate_secrets_multiple(self):
        """Test validation of multiple secrets"""
        configs = [
            SecretConfig(name="SECRET1", required=True, min_length=5),
            SecretConfig(name="SECRET2", required=False, default="default"),
            SecretConfig(name="SECRET3", required=True, max_length=10),
        ]

        # Set some secrets
        self.manager.set_secret("SECRET1", "valid_secret", use_keyring=False)
        self.manager.set_secret("SECRET3", "too_long_secret", use_keyring=False)

        results = self.manager.validate_secrets(configs)

        assert results["SECRET1"] is True  # Valid
        assert results["SECRET2"] is True  # Optional with default
        assert results["SECRET3"] is False  # Too long

    def test_get_missing_secrets(self):
        """Test getting list of missing required secrets"""
        configs = [
            SecretConfig(name="REQUIRED1", required=True),
            SecretConfig(name="REQUIRED2", required=True),
            SecretConfig(name="OPTIONAL1", required=False),
        ]

        # Set one required secret
        self.manager.set_secret("REQUIRED1", "value", use_keyring=False)

        missing = self.manager.get_missing_secrets(configs)
        assert "REQUIRED2" in missing
        assert "REQUIRED1" not in missing
        assert "OPTIONAL1" not in missing

    def test_export_secrets_report(self):
        """Test secrets report export"""
        configs = [
            SecretConfig(name="SECRET1", required=True, description="Test secret 1"),
            SecretConfig(name="SECRET2", required=False, description="Test secret 2"),
        ]

        # Set one secret
        self.manager.set_secret("SECRET1", "value", use_keyring=False)

        report = self.manager.export_secrets_report(configs)

        assert "timestamp" in report
        assert "app_name" in report
        assert "keyring_available" in report
        assert "secrets" in report

        # Check secret info
        secret1_info = report["secrets"]["SECRET1"]
        assert secret1_info["required"] is True
        assert secret1_info["present"] is True
        assert secret1_info["valid"] is True
        assert secret1_info["description"] == "Test secret 1"

        secret2_info = report["secrets"]["SECRET2"]
        assert secret2_info["required"] is False
        assert secret2_info["present"] is False
        assert secret2_info["valid"] is True  # Optional secrets are valid when missing

    def test_create_secrets_config(self):
        """Test default secrets configuration creation"""
        configs = self.manager.create_secrets_config()

        # Should have expected secrets
        secret_names = [config.name for config in configs]
        expected_secrets = [
            "POSTGRES_DSN",
            "DASHBOARD_SECRET_KEY",
            "API_KEY",
            "DB_PASSWORD",
            "REDIS_URL",
            "METRICS_PORT",
        ]

        for expected in expected_secrets:
            assert expected in secret_names

        # Check some specific configurations
        postgres_config = next(c for c in configs if c.name == "POSTGRES_DSN")
        assert postgres_config.required is True
        assert postgres_config.validation_regex == r"^postgresql://.*"

        # No legacy local model URL in default config


class TestSecretsValidation:
    """Test secrets validation functions"""

    @patch("utils.secrets_manager.SecretsManager")
    def test_validate_startup_secrets_success(self, mock_manager_class):
        """Test successful startup validation"""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        # Mock successful validation
        mock_manager.get_missing_secrets.return_value = []
        mock_manager.validate_secrets.return_value = {"SECRET1": True, "SECRET2": True}

        assert validate_startup_secrets()

    @patch("utils.secrets_manager.SecretsManager")
    def test_validate_startup_secrets_missing(self, mock_manager_class):
        """Test startup validation with missing secrets"""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        # Mock missing secrets
        mock_manager.get_missing_secrets.return_value = ["MISSING_SECRET"]

        assert not validate_startup_secrets()

    @patch("utils.secrets_manager.SecretsManager")
    def test_validate_startup_secrets_invalid(self, mock_manager_class):
        """Test startup validation with invalid secrets"""
        mock_manager = MagicMock()
        mock_manager_class.return_value = mock_manager

        # Mock invalid secrets
        mock_manager.get_missing_secrets.return_value = []
        mock_manager.validate_secrets.return_value = {"SECRET1": False, "SECRET2": True}

        assert not validate_startup_secrets()

    @patch("utils.secrets_manager.setup_secrets_interactive")
    @patch("utils.secrets_manager.validate_startup_secrets")
    def test_setup_secrets_interactive_success(self, mock_validate, mock_setup):
        """Test successful interactive setup"""
        mock_validate.return_value = True
        mock_setup.return_value = True

        assert setup_secrets_interactive()

    @patch("utils.secrets_manager.setup_secrets_interactive")
    @patch("utils.secrets_manager.validate_startup_secrets")
    def test_setup_secrets_interactive_failure(self, mock_validate, mock_setup):
        """Test failed interactive setup"""
        mock_validate.return_value = False
        mock_setup.return_value = False

        assert not setup_secrets_interactive()


class TestSecretsIntegration:
    """Test secrets integration with other components"""

    def test_secrets_with_environment(self):
        """Test secrets management with environment variables"""
        manager = SecretsManager()

        # Test with environment variable
        test_env_var = "TEST_ENV_SECRET"
        test_value = "env_value_123"

        # Set environment variable
        os.environ[test_env_var] = test_value

        try:
            # Should retrieve from environment
            retrieved = manager.get_secret(test_env_var)
            assert retrieved == test_value

            # Should cache the value
            assert test_env_var in manager.secrets_cache
            assert manager.secrets_cache[test_env_var] == test_value

        finally:
            # Clean up
            os.environ.pop(test_env_var, None)

    def test_secrets_validation_caching(self):
        """Test that validation results are cached"""
        manager = SecretsManager()
        config = SecretConfig(name="CACHE_TEST_SECRET", required=True, min_length=5)

        # Set a valid secret
        manager.set_secret("CACHE_TEST_SECRET", "valid_secret", use_keyring=False)

        # First validation should populate cache
        result1 = manager.validate_secret("CACHE_TEST_SECRET", config)
        assert result1 is True

        # Second validation should use cache
        result2 = manager.validate_secret("CACHE_TEST_SECRET", config)
        assert result2 is True

        # Cache key should be present
        cache_key = f"CACHE_TEST_SECRET_{hash(str(config))}"
        assert cache_key in manager.validation_cache


if __name__ == "__main__":
    pytest.main([__file__])
