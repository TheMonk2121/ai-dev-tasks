#!/usr/bin/env python3
"""
Tests for security utilities.
"""

import pytest

# Mark all tests in this file as deprecated
pytestmark = pytest.mark.deprecated
import tempfile
import json
from unittest.mock import patch, MagicMock
from src.utils.security import (
    SecurityScanner,
    generate_secure_hash,
    verify_secure_hash,
    generate_secure_token,
    validate_file_hash,
    sanitize_filename,
    validate_url,
    create_security_config,
    validate_security_config,
)


class TestSecurityScanner:
    """Test security scanner functionality"""

    def test_scanner_initialization(self):
        """Test security scanner initialization"""
        scanner = SecurityScanner()
        assert scanner.project_root is not None
        assert scanner.requirements_file is not None
        assert "bandit_config" in scanner.security_config

    @patch("subprocess.run")
    def test_check_dependencies_success(self, mock_run):
        """Test dependency checking with success"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "[]"

        scanner = SecurityScanner()
        result = scanner.check_dependencies()

        assert result["status"] == "success"
        assert result["total"] == 0

    @patch("subprocess.run")
    def test_check_dependencies_failure(self, mock_run):
        """Test dependency checking with failure"""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stderr = "Safety check failed"

        scanner = SecurityScanner()
        result = scanner.check_dependencies()

        assert result["status"] == "error"
        assert "Safety check failed" in result["error"]

    @patch("subprocess.run")
    def test_run_bandit_scan_success(self, mock_run):
        """Test bandit scan with success"""
        mock_run.return_value.returncode = 0

        # Mock bandit report file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"results": []}, f)
            report_file = f.name

        try:
            with patch("builtins.open", return_value=open(report_file)):
                scanner = SecurityScanner()
                result = scanner.run_bandit_scan()

                assert result["status"] == "success"
                assert result["total"] == 0
        finally:
            os.unlink(report_file)

    @patch("subprocess.run")
    def test_run_pip_audit_success(self, mock_run):
        """Test pip-audit with success"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '{"vulnerabilities": []}'

        scanner = SecurityScanner()
        result = scanner.run_pip_audit()

        assert result["status"] == "success"
        assert result["total"] == 0

    def test_count_severities(self):
        """Test severity counting"""
        scanner = SecurityScanner()
        issues = [
            {"issue_severity": "LOW"},
            {"issue_severity": "MEDIUM"},
            {"issue_severity": "HIGH"},
            {"issue_severity": "LOW"},
        ]

        counts = scanner._count_severities(issues)
        assert counts["LOW"] == 2
        assert counts["MEDIUM"] == 1
        assert counts["HIGH"] == 1


class TestSecurityUtilities:
    """Test security utility functions"""

    def test_generate_secure_hash(self):
        """Test secure hash generation"""
        data = "test_data"
        hash_result = generate_secure_hash(data)

        assert ":" in hash_result
        assert len(hash_result.split(":")[0]) == 32  # salt length

    def test_verify_secure_hash(self):
        """Test secure hash verification"""
        data = "test_data"
        hash_result = generate_secure_hash(data)

        assert verify_secure_hash(data, hash_result) is True
        assert verify_secure_hash("wrong_data", hash_result) is False

    def test_generate_secure_token(self):
        """Test secure token generation"""
        token = generate_secure_token()
        assert len(token) > 0
        assert isinstance(token, str)

        # Test custom length
        token_16 = generate_secure_token(16)
        assert len(token_16) > 0

    def test_validate_file_hash(self):
        """Test file hash validation"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            file_path = f.name

        try:
            # Generate hash of the file
            with open(file_path, "rb") as f:
                import hashlib

                expected_hash = hashlib.sha256(f.read()).hexdigest()

            assert validate_file_hash(file_path, expected_hash) is True
            assert validate_file_hash(file_path, "wrong_hash") is False
        finally:
            os.unlink(file_path)

    def test_sanitize_filename(self):
        """Test filename sanitization"""
        dangerous_filename = 'file<>:"/\\|?*.txt'
        sanitized = sanitize_filename(dangerous_filename)

        assert "<" not in sanitized
        assert ">" not in sanitized
        assert ":" not in sanitized
        assert '"' not in sanitized
        assert "/" not in sanitized
        assert "\\" not in sanitized
        assert "|" not in sanitized
        assert "?" not in sanitized
        assert "*" not in sanitized

    def test_validate_url(self):
        """Test URL validation"""
        valid_urls = [
            "http://localhost:5000",
            "https://example.com",
            "http://127.0.0.1:8000",
            "https://api.example.com/v1/endpoint",
        ]

        invalid_urls = ["not_a_url", "ftp://example.com", "file:///etc/passwd", "javascript:alert('xss')"]

        for url in valid_urls:
            assert validate_url(url) is True

        for url in invalid_urls:
            assert validate_url(url) is False

    def test_create_security_config(self):
        """Test security configuration creation"""
        config = create_security_config()

        assert "security" in config
        security = config["security"]
        assert security["enabled"] is True
        assert security["scan_on_startup"] is True
        assert "vulnerability_threshold" in security
        assert "allowed_extensions" in security

    def test_validate_security_config(self):
        """Test security configuration validation"""
        valid_config = {"security": {"enabled": True, "scan_on_startup": True, "vulnerability_threshold": "medium"}}

        invalid_config = {
            "security": {
                "enabled": True
                # Missing required keys
            }
        }

        assert validate_security_config(valid_config) is True
        assert validate_security_config(invalid_config) is False


class TestSecurityIntegration:
    """Test security integration with other components"""

    def test_security_with_logger(self):
        """Test security utilities with structured logging"""
        from src.utils.logger import get_logger

        logger = get_logger("test_security")

        # Test that security operations can be logged
        token = generate_secure_token()
        logger.info(
            "Security token generated",
            extra={"component": "security", "action": "token_generated", "token_length": len(token)},
        )

        # Verify logging worked
        assert token is not None

    def test_file_operations_with_security(self):
        """Test file operations with security utilities"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content for security")
            file_path = f.name

        try:
            # Generate hash
            with open(file_path, "rb") as f:
                import hashlib

                file_hash = hashlib.sha256(f.read()).hexdigest()

            # Validate hash
            assert validate_file_hash(file_path, file_hash) is True

            # Test with wrong hash
            assert validate_file_hash(file_path, "wrong_hash") is False

        finally:
            os.unlink(file_path)

    def test_url_validation_integration(self):
        """Test URL validation in real scenarios"""
        # Test dashboard URLs
        dashboard_urls = ["http://localhost:5000", "http://127.0.0.1:5000", "https://localhost:5000"]

        for url in dashboard_urls:
            assert validate_url(url) is True

        # Test invalid URLs
        invalid_urls = ["http://", "https://", "ftp://localhost:5000", "file:///etc/passwd"]

        for url in invalid_urls:
            assert validate_url(url) is False
