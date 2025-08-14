#!/usr/bin/env python3
"""
Tests for input validation utilities.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from utils.validator import (
    sanitize_prompt, validate_file_path, validate_file_size,
    validate_secrets, sanitize_filename, validate_query_complexity,
    validate_url, validate_json_structure, validate_string_length,
    validate_integer_range, validate_list_length, validate_file_content,
    validate_config_structure, SecurityError, ValidationError
)

class TestSanitizePrompt:
    """Test prompt sanitization"""
    
    def test_valid_prompt(self):
        """Test that valid prompts pass sanitization"""
        prompt = "What is Python programming?"
        result = sanitize_prompt(prompt)
        assert result == prompt
    
    def test_blocked_patterns(self):
        """Test that blocked patterns are detected"""
        blocked_patterns = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "eval('malicious code')",
            "exec('malicious code')",
            "import os",
            "from sys import",
            "__import__('os')",
            "globals()",
            "locals()",
            "vars()",
            "dir()",
            "type(",
            "open('file')",
            "file('file')",
            "read('file')",
            "write('file')",
            "subprocess.call('ls')",
            "os.system('ls')"
        ]
        
        for pattern in blocked_patterns:
            with pytest.raises(SecurityError, match="Blocked pattern detected"):
                sanitize_prompt(pattern)
    
    def test_case_insensitive_detection(self):
        """Test case-insensitive pattern detection"""
        patterns = [
            "JavaScript:alert('xss')",
            "EVAL('code')",
            "Import os",
            "From sys import"
        ]
        
        for pattern in patterns:
            with pytest.raises(SecurityError):
                sanitize_prompt(pattern)
    
    def test_null_bytes_removal(self):
        """Test that null bytes are removed"""
        prompt = "Hello\x00World"
        result = sanitize_prompt(prompt)
        assert result == "HelloWorld"
    
    def test_length_limit(self):
        """Test that prompts are limited in length"""
        long_prompt = "A" * 10001
        with pytest.raises(ValidationError, match="Prompt too long"):
            sanitize_prompt(long_prompt)

class TestValidateFilePath:
    """Test file path validation"""
    
    def test_valid_file_path(self):
        """Test that valid file paths pass validation"""
        valid_paths = [
            "document.txt",
            "file.md",
            "data.pdf",
            "info.csv"
        ]
        
        for path in valid_paths:
            assert validate_file_path(path) is True
    
    def test_path_traversal_attempts(self):
        """Test that path traversal attempts are blocked"""
        traversal_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config",
            "file/../../../etc/passwd",
            "file\\..\\..\\..\\windows\\system32"
        ]
        
        for path in traversal_paths:
            with pytest.raises(SecurityError, match="Path traversal not allowed"):
                validate_file_path(path)
    
    def test_invalid_extensions(self):
        """Test that invalid extensions are blocked"""
        invalid_paths = [
            "script.py",
            "executable.exe",
            "binary.bin",
            "script.sh"
        ]
        
        for path in invalid_paths:
            with pytest.raises(SecurityError, match="Invalid file extension"):
                validate_file_path(path)
    
    def test_suspicious_characters(self):
        """Test that suspicious characters are blocked"""
        suspicious_paths = [
            "file<.txt",
            "file>.txt",
            "file|.txt",
            "file&.txt",
            "file;.txt",
            "file`.txt",
            "file$.txt",
            "file(.txt",
            "file).txt",
            "file{.txt",
            "file}.txt"
        ]
        
        for path in suspicious_paths:
            with pytest.raises(SecurityError, match="Suspicious characters"):
                validate_file_path(path)

class TestValidateFileSize:
    """Test file size validation"""
    
    def test_valid_file_size(self):
        """Test that valid file sizes pass validation"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            file_path = f.name
        
        try:
            assert validate_file_size(file_path, max_size_mb=1) is True
        finally:
            os.unlink(file_path)
    
    def test_file_too_large(self):
        """Test that large files are rejected"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            # Create a file larger than 1MB
            f.write(b"x" * (2 * 1024 * 1024))  # 2MB
            file_path = f.name
        
        try:
            with pytest.raises(ValidationError, match="File too large"):
                validate_file_size(file_path, max_size_mb=1)
        finally:
            os.unlink(file_path)
    
    def test_nonexistent_file(self):
        """Test that nonexistent files raise error"""
        with pytest.raises(ValidationError, match="File does not exist"):
            validate_file_size("nonexistent.txt")

class TestValidateSecrets:
    """Test secrets validation"""
    
    @patch.dict(os.environ, {'DB_PASSWORD': 'secret', 'API_KEY': 'key'})
    def test_all_secrets_present(self):
        """Test when all required secrets are present"""
        required_secrets = ['DB_PASSWORD', 'API_KEY']
        validate_secrets(required_secrets)  # Should not raise
    
    @patch.dict(os.environ, {'DB_PASSWORD': 'secret'}, clear=True)
    def test_missing_secrets(self):
        """Test when required secrets are missing"""
        required_secrets = ['DB_PASSWORD', 'API_KEY']
        with pytest.raises(ValidationError, match="Missing required secrets"):
            validate_secrets(required_secrets)

class TestSanitizeFilename:
    """Test filename sanitization"""
    
    def test_valid_filename(self):
        """Test that valid filenames are unchanged"""
        filename = "document.txt"
        result = sanitize_filename(filename)
        assert result == filename
    
    def test_dangerous_characters(self):
        """Test that dangerous characters are replaced"""
        dangerous_filename = "file<>:\"/\\|?*.txt"
        result = sanitize_filename(dangerous_filename)
        
        # Check that dangerous characters are replaced
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert '"' not in result
        assert "/" not in result
        assert "\\" not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result
    
    def test_null_bytes_removal(self):
        """Test that null bytes are removed"""
        filename = "file\x00name.txt"
        result = sanitize_filename(filename)
        assert result == "file_name.txt"
    
    def test_length_limit(self):
        """Test that filenames are limited in length"""
        long_filename = "A" * 300
        result = sanitize_filename(long_filename)
        assert len(result) <= 255

class TestValidateQueryComplexity:
    """Test query complexity validation"""
    
    def test_simple_query(self):
        """Test that simple queries pass validation"""
        query = "What is Python?"
        assert validate_query_complexity(query, max_tokens=1000) is True
    
    def test_complex_query(self):
        """Test that complex queries are rejected"""
        complex_query = "What are the differences between Python and JavaScript programming languages, and how do they compare in terms of performance, syntax, and use cases for web development, machine learning, and system administration?" * 10
        
        with pytest.raises(ValidationError, match="Query too complex"):
            validate_query_complexity(complex_query, max_tokens=100)

class TestValidateUrl:
    """Test URL validation"""
    
    def test_valid_urls(self):
        """Test that valid URLs pass validation"""
        valid_urls = [
            "http://localhost:5000",
            "https://localhost:5000",
            "http://127.0.0.1:8000",
            "https://api.example.com/v1/endpoint"
        ]
        
        for url in valid_urls:
            assert validate_url(url) is True
    
    def test_invalid_urls(self):
        """Test that invalid URLs are rejected"""
        invalid_urls = [
            "not_a_url",
            "ftp://example.com",
            "file:///etc/passwd",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>"
        ]
        
        for url in invalid_urls:
            with pytest.raises(SecurityError):
                validate_url(url)
    
    def test_disallowed_domains(self):
        """Test that disallowed domains are rejected"""
        disallowed_urls = [
            "http://malicious.com",
            "https://evil.org/api",
            "http://attacker.net/data"
        ]
        
        for url in disallowed_urls:
            with pytest.raises(SecurityError, match="Domain not allowed"):
                validate_url(url)

class TestValidateJsonStructure:
    """Test JSON structure validation"""
    
    def test_valid_structure(self):
        """Test that valid JSON structures pass validation"""
        data = {"name": "test", "value": 42}
        required_fields = ["name", "value"]
        assert validate_json_structure(data, required_fields) is True
    
    def test_missing_fields(self):
        """Test that missing required fields are detected"""
        data = {"name": "test"}
        required_fields = ["name", "value"]
        
        with pytest.raises(ValidationError, match="Missing required fields"):
            validate_json_structure(data, required_fields)
    
    def test_invalid_data_type(self):
        """Test that non-dict data is rejected"""
        data = "not a dict"
        required_fields = ["name"]
        
        with pytest.raises(ValidationError, match="Data must be a dictionary"):
            validate_json_structure(data, required_fields)

class TestValidateStringLength:
    """Test string length validation"""
    
    def test_valid_length(self):
        """Test that strings within bounds pass validation"""
        text = "Hello, World!"
        assert validate_string_length(text, min_length=1, max_length=100) is True
    
    def test_too_short(self):
        """Test that short strings are rejected"""
        text = ""
        with pytest.raises(ValidationError, match="Text too short"):
            validate_string_length(text, min_length=1, max_length=100)
    
    def test_too_long(self):
        """Test that long strings are rejected"""
        text = "A" * 101
        with pytest.raises(ValidationError, match="Text too long"):
            validate_string_length(text, min_length=1, max_length=100)

class TestValidateIntegerRange:
    """Test integer range validation"""
    
    def test_valid_range(self):
        """Test that integers within range pass validation"""
        assert validate_integer_range(5, 1, 10) is True
    
    def test_below_minimum(self):
        """Test that values below minimum are rejected"""
        with pytest.raises(ValidationError, match="out of range"):
            validate_integer_range(0, 1, 10)
    
    def test_above_maximum(self):
        """Test that values above maximum are rejected"""
        with pytest.raises(ValidationError, match="out of range"):
            validate_integer_range(11, 1, 10)
    
    def test_invalid_type(self):
        """Test that non-integer values are rejected"""
        with pytest.raises(ValidationError, match="must be an integer"):
            validate_integer_range("5", 1, 10)

class TestValidateListLength:
    """Test list length validation"""
    
    def test_valid_length(self):
        """Test that lists within bounds pass validation"""
        items = [1, 2, 3, 4, 5]
        assert validate_list_length(items, max_items=10) is True
    
    def test_too_long(self):
        """Test that long lists are rejected"""
        items = list(range(11))
        with pytest.raises(ValidationError, match="too long"):
            validate_list_length(items, max_items=10)
    
    def test_invalid_type(self):
        """Test that non-list values are rejected"""
        with pytest.raises(ValidationError, match="must be a list"):
            validate_list_length("not a list", max_items=10)

class TestValidateFileContent:
    """Test file content validation"""
    
    def test_valid_content(self):
        """Test that files with valid content pass validation"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for i in range(100):
                f.write(f"Line {i}\n")
            file_path = f.name
        
        try:
            assert validate_file_content(file_path, max_lines=1000) is True
        finally:
            os.unlink(file_path)
    
    def test_too_many_lines(self):
        """Test that files with too many lines are rejected"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            for i in range(10001):
                f.write(f"Line {i}\n")
            file_path = f.name
        
        try:
            with pytest.raises(ValidationError, match="too many lines"):
                validate_file_content(file_path, max_lines=10000)
        finally:
            os.unlink(file_path)
    
    def test_nonexistent_file(self):
        """Test that nonexistent files raise error"""
        with pytest.raises(ValidationError, match="File does not exist"):
            validate_file_content("nonexistent.txt")

class TestValidateConfigStructure:
    """Test configuration structure validation"""
    
    def test_valid_config(self):
        """Test that valid configurations pass validation"""
        config = {"database": {}, "api": {}, "logging": {}}
        required_sections = ["database", "api", "logging"]
        assert validate_config_structure(config, required_sections) is True
    
    def test_missing_sections(self):
        """Test that missing sections are detected"""
        config = {"database": {}, "api": {}}
        required_sections = ["database", "api", "logging"]
        
        with pytest.raises(ValidationError, match="Missing required configuration sections"):
            validate_config_structure(config, required_sections)
    
    def test_invalid_config_type(self):
        """Test that non-dict configurations are rejected"""
        config = "not a dict"
        required_sections = ["database"]
        
        with pytest.raises(ValidationError, match="Configuration must be a dictionary"):
            validate_config_structure(config, required_sections)

if __name__ == "__main__":
    pytest.main([__file__]) 