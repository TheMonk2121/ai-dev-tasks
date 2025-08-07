#!/usr/bin/env python3
"""
Tests for prompt sanitization functionality
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock

# Add src to path for imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from utils.prompt_sanitizer import (
    sanitize_prompt, validate_file_path, validate_file_size,
    validate_file_extension, sanitize_and_validate_input,
    SecurityError, load_security_config
)

class TestPromptSanitizer(unittest.TestCase):
    """Test prompt sanitization functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'system.json')
        
        # Create test config
        self.test_config = {
            "security": {
                "prompt_blocklist": ["{{", "}}", "<script>"],
                "prompt_whitelist": ["<b>", "<i>"],
                "file_validation": {
                    "max_size_mb": 50,
                    "allowed_ext": ["txt", "md", "pdf", "csv"]
                }
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(self.test_config, f)
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('utils.prompt_sanitizer.load_security_config')
    def test_sanitize_prompt_blocklist(self, mock_load_config):
        """Test prompt sanitization with block-list"""
        mock_load_config.return_value = {
            "prompt_blocklist": ["{{", "}}", "<script>"],
            "prompt_whitelist": [],
            "file_validation": {}
        }
        
        # Test valid prompt
        result = sanitize_prompt("Hello world")
        self.assertEqual(result, "Hello world")
        
        # Test blocked pattern
        with self.assertRaises(SecurityError):
            sanitize_prompt("Hello {{world}}")
        
        # Test another blocked pattern
        with self.assertRaises(SecurityError):
            sanitize_prompt("Hello <script>alert('xss')</script>")
    
    @patch('utils.prompt_sanitizer.load_security_config')
    def test_sanitize_prompt_whitelist(self, mock_load_config):
        """Test prompt sanitization with whitelist"""
        mock_load_config.return_value = {
            "prompt_blocklist": ["{{", "}}", "<script>"],
            "prompt_whitelist": ["<b>", "<i>"],
            "file_validation": {}
        }
        
        # Test whitelisted pattern
        result = sanitize_prompt("Hello <b>world</b>")
        self.assertEqual(result, "Hello <b>world</b>")
        
        # Test non-whitelisted blocked pattern
        with self.assertRaises(SecurityError):
            sanitize_prompt("Hello <script>alert('xss')</script>")
    
    def test_validate_file_path(self):
        """Test file path validation"""
        # Valid paths
        self.assertTrue(validate_file_path("document.txt"))
        self.assertTrue(validate_file_path("folder/document.pdf"))
        
        # Invalid paths
        self.assertFalse(validate_file_path("../secret.txt"))
        self.assertFalse(validate_file_path("../../../etc/passwd"))
        self.assertFalse(validate_file_path("file:///etc/passwd"))
        self.assertFalse(validate_file_path("javascript:alert('xss')"))
    
    def test_validate_file_size(self):
        """Test file size validation"""
        # Test valid size
        self.assertTrue(validate_file_size(1024 * 1024))  # 1MB
        
        # Test size too large
        self.assertFalse(validate_file_size(100 * 1024 * 1024))  # 100MB
    
    @patch('utils.prompt_sanitizer.load_security_config')
    def test_validate_file_extension(self, mock_load_config):
        """Test file extension validation"""
        mock_load_config.return_value = {
            "prompt_blocklist": [],
            "prompt_whitelist": [],
            "file_validation": {
                "allowed_ext": ["txt", "md", "pdf", "csv"]
            }
        }
        
        # Valid extensions
        self.assertTrue(validate_file_extension("document.txt"))
        self.assertTrue(validate_file_extension("readme.md"))
        self.assertTrue(validate_file_extension("data.csv"))
        
        # Invalid extensions
        self.assertFalse(validate_file_extension("script.py"))
        self.assertFalse(validate_file_extension("executable.exe"))
        self.assertFalse(validate_file_extension("no_extension"))
    
    @patch('utils.prompt_sanitizer.load_security_config')
    def test_sanitize_and_validate_input(self, mock_load_config):
        """Test comprehensive input validation"""
        mock_load_config.return_value = {
            "prompt_blocklist": ["{{", "}}", "<script>"],
            "prompt_whitelist": [],
            "file_validation": {
                "max_size_mb": 50,
                "allowed_ext": ["txt", "md", "pdf", "csv"]
            }
        }
        
        # Test valid input
        result = sanitize_and_validate_input(
            prompt="Hello world",
            file_path="document.txt",
            file_size_bytes=1024
        )
        self.assertTrue(result["overall_valid"])
        self.assertEqual(result["prompt_sanitized"], "Hello world")
        self.assertTrue(result["file_path_valid"])
        self.assertTrue(result["file_size_valid"])
        self.assertTrue(result["file_extension_valid"])
        
        # Test invalid prompt
        with self.assertRaises(SecurityError):
            sanitize_and_validate_input(
                prompt="Hello {{world}}",
                file_path="document.txt",
                file_size_bytes=1024
            )
        
        # Test invalid file path
        result = sanitize_and_validate_input(
            prompt="Hello world",
            file_path="../secret.txt",
            file_size_bytes=1024
        )
        self.assertFalse(result["overall_valid"])
        self.assertFalse(result["file_path_valid"])
    
    def test_load_security_config(self):
        """Test security configuration loading"""
        # This test would require mocking the config file path
        # For now, we'll test the fallback behavior
        with patch('utils.prompt_sanitizer.load_security_config') as mock_load:
            mock_load.side_effect = FileNotFoundError()
            config = load_security_config()
            self.assertIn("prompt_blocklist", config)
            self.assertIn("prompt_whitelist", config)
            self.assertIn("file_validation", config)

if __name__ == '__main__':
    unittest.main() 