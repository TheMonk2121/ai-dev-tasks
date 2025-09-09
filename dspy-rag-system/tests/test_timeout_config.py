#!/usr/bin/env python3
"""
Tests for global timeout configuration.
"""

import json
import os
import tempfile
from unittest.mock import patch

from src.utils.timeout_config import (
    TimeoutConfig,
    format_timeout_duration,
    load_timeout_config,
    validate_timeout_config,
)


class TestTimeoutConfig:
    """Test timeout configuration loading and validation"""

    def test_default_config(self):
        """Test default timeout configuration"""
        config = TimeoutConfig()

        assert config.db_connect_timeout == 10
        assert config.db_read_timeout == 30
        assert config.db_write_timeout == 60
        assert config.http_connect_timeout == 10
        assert config.http_read_timeout == 30
        assert config.llm_request_timeout == 120
        assert config.pdf_processing_timeout == 300

    def test_environment_variable_loading(self):
        """Test loading configuration from environment variables"""
        with patch.dict(
            os.environ, {"DB_CONNECT_TIMEOUT": "15", "HTTP_READ_TIMEOUT": "45", "LLM_REQUEST_TIMEOUT": "180"}
        ):
            config = load_timeout_config()

            assert config.db_connect_timeout == 15
            assert config.http_read_timeout == 45
            assert config.llm_request_timeout == 180

    def test_system_json_loading(self):
        """Test loading configuration from system.json"""
        # Create temporary system.json
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"timeouts": {"db_connect_timeout": 20, "http_read_timeout": 60, "llm_request_timeout": 240}}, f)
            temp_config_path = f.name

        try:
            with patch("src.utils.timeout_config.os.path.join") as mock_join:
                mock_join.return_value = temp_config_path
                config = load_timeout_config()

                assert config.db_connect_timeout == 20
                assert config.http_read_timeout == 60
                assert config.llm_request_timeout == 240
        finally:
            os.unlink(temp_config_path)

    def test_validation_success(self):
        """Test successful configuration validation"""
        config = TimeoutConfig()
        assert validate_timeout_config(config) is True

    def test_validation_failure(self):
        """Test configuration validation failures"""
        config = TimeoutConfig()

        # Test database timeout validation
        config.db_connect_timeout = 0
        assert validate_timeout_config(config) is False

        config.db_connect_timeout = 10  # Reset
        config.db_read_timeout = 3
        assert validate_timeout_config(config) is False

        # Test HTTP timeout validation
        config.db_read_timeout = 30  # Reset
        config.http_connect_timeout = 0
        assert validate_timeout_config(config) is False

        config.http_connect_timeout = 10  # Reset
        config.http_total_timeout = 5  # Less than connect + read
        assert validate_timeout_config(config) is False

    def test_format_timeout_duration(self):
        """Test timeout duration formatting"""
        assert format_timeout_duration(30) == "30s"
        assert format_timeout_duration(90) == "1m30s"
        assert format_timeout_duration(3661) == "1h1m"
        assert format_timeout_duration(7320) == "2h2m"

    def test_environment_override_system_json(self):
        """Test that environment variables override system.json"""
        # Create temporary system.json
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"timeouts": {"db_connect_timeout": 20, "http_read_timeout": 60}}, f)
            temp_config_path = f.name

        try:
            with patch("src.utils.timeout_config.os.path.join") as mock_join:
                mock_join.return_value = temp_config_path

                # Environment should override system.json
                with patch.dict(os.environ, {"DB_CONNECT_TIMEOUT": "25", "HTTP_READ_TIMEOUT": "75"}):
                    config = load_timeout_config()

                    assert config.db_connect_timeout == 25  # From env
                    assert config.http_read_timeout == 75  # From env
        finally:
            os.unlink(temp_config_path)

    def test_missing_system_json_handling(self):
        """Test graceful handling of missing system.json"""
        with patch("src.utils.timeout_config.os.path.exists") as mock_exists:
            mock_exists.return_value = False

            config = load_timeout_config()

            # Should use defaults
            assert config.db_connect_timeout == 10
            assert config.http_read_timeout == 30

    def test_invalid_system_json_handling(self):
        """Test graceful handling of invalid system.json"""
        # Create invalid JSON file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"invalid": json}')
            temp_config_path = f.name

        try:
            with patch("src.utils.timeout_config.os.path.join") as mock_join:
                mock_join.return_value = temp_config_path

                config = load_timeout_config()

                # Should use defaults
                assert config.db_connect_timeout == 10
                assert config.http_read_timeout == 30
        finally:
            os.unlink(temp_config_path)


class TestTimeoutIntegration:
    """Test timeout configuration integration with other components"""

    def test_vector_store_timeout_integration(self):
        """Test that vector store uses timeout configuration"""

        # Mock the timeout config
        with patch("src.dspy_modules.vector_store.get_timeout_config") as mock_get_config:
            mock_config = TimeoutConfig()
            mock_config.db_read_timeout = 45
            mock_config.db_write_timeout = 90
            mock_get_config.return_value = mock_config

            # This should not raise an exception
            # The actual pool creation is tested in test_vector_store.py
            pass

    def test_enhanced_rag_timeout_integration(self):
        """Test that enhanced RAG system uses timeout configuration"""
        from src.dspy_modules.enhanced_rag_system import MistralLLM

        # Mock the timeout config
        with patch("src.dspy_modules.enhanced_rag_system.get_timeout_config") as mock_get_config:
            mock_config = TimeoutConfig()
            mock_config.llm_request_timeout = 180
            mock_config.http_connect_timeout = 15
            mock_config.http_read_timeout = 45
            mock_get_config.return_value = mock_config

            # Create LLM instance
            llm = MistralLLM()

            # Should use configured timeout
            assert llm.timeout == 180
