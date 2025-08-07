#!/usr/bin/env python3
"""
Test Suite for Documentation Coherence Validation System - B-060

Comprehensive tests for the doc_coherence_validator.py implementation.
Tests all validation tasks and edge cases.
"""

import unittest
import tempfile
import shutil
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from doc_coherence_validator import DocCoherenceValidator

class TestDocCoherenceValidator(unittest.TestCase):
    """Test cases for DocCoherenceValidator class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.validator = DocCoherenceValidator(dry_run=True)
        
        # Create test files
        self.create_test_files()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def create_test_files(self):
        """Create test markdown files for validation."""
        test_files = {
            '100_test-memory-context.md': '''# Test Memory Context
<!-- CONTEXT_REFERENCE: 400_test-system-overview.md -->
<!-- BACKLOG_REFERENCE: 000_test-backlog.md -->
Current Sprint: B-001
''',
            '400_test-system-overview.md': '''# Test System Overview
System architecture includes DSPy and PostgreSQL.
''',
            '000_test-backlog.md': '''# Test Backlog
| B-001 | Test Item | 🔥 | 2 | todo | Test description | Tech | None |
''',
            '200_test-naming-conventions.md': '''# Test Naming Conventions
Valid three-digit prefix file.
''',
            'invalid_file.md': '''# Invalid File
This file has no three-digit prefix.
''',
            'README.md': '''# Test README
This is a valid README file.
'''
        }
        
        for filename, content in test_files.items():
            file_path = Path(self.test_dir) / filename
            with open(file_path, 'w') as f:
                f.write(content)
    
    def test_initialization(self):
        """Test validator initialization."""
        validator = DocCoherenceValidator(dry_run=True)
        self.assertTrue(validator.dry_run)
        self.assertIsInstance(validator.markdown_files, list)
        self.assertIsInstance(validator.validation_results, dict)
    
    def test_should_exclude(self):
        """Test file exclusion logic."""
        # Test excluded patterns
        excluded_files = [
            'venv/test.md',
            'node_modules/test.md',
            'docs/legacy/test.md',
            '__pycache__/test.md',
            '.git/test.md'
        ]
        
        for file_path in excluded_files:
            path = Path(file_path)
            self.assertTrue(self.validator._should_exclude(path))
        
        # Test included files
        included_files = [
            '100_test.md',
            '400_test.md',
            'README.md'
        ]
        
        for file_path in included_files:
            path = Path(file_path)
            self.assertFalse(self.validator._should_exclude(path))
    
    def test_read_file(self):
        """Test file reading functionality."""
        # Test successful read
        test_file = Path(self.test_dir) / '100_test-memory-context.md'
        content = self.validator.read_file(test_file)
        self.assertIsNotNone(content)
        self.assertIn('Test Memory Context', content)
        
        # Test non-existent file
        non_existent = Path(self.test_dir) / 'non_existent.md'
        content = self.validator.read_file(non_existent)
        self.assertIsNone(content)
        self.assertIn('non_existent.md', str(self.validator.errors[-1]))
    
    def test_write_file(self):
        """Test file writing functionality."""
        test_file = Path(self.test_dir) / 'test_write.md'
        test_content = 'Test content for writing'
        
        # Test dry-run write
        result = self.validator.write_file(test_file, test_content)
        self.assertTrue(result)
        self.assertFalse(test_file.exists())  # Should not actually write in dry-run
        
        # Test actual write
        self.validator.dry_run = False
        result = self.validator.write_file(test_file, test_content)
        self.assertTrue(result)
        self.assertTrue(test_file.exists())
        
        with open(test_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, test_content)
    
    @patch('doc_coherence_validator.Path')
    def test_validate_cross_references(self, mock_path):
        """Test cross-reference validation."""
        # Mock file structure
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.suffix = '.md'
        
        # Test with valid references
        with patch.object(self.validator, 'markdown_files', [
            Path('100_test-memory-context.md'),
            Path('400_test-system-overview.md')
        ]):
            with patch.object(self.validator, 'read_file') as mock_read:
                mock_read.side_effect = [
                    '<!-- CONTEXT_REFERENCE: 400_test-system-overview.md -->',
                    'System overview content'
                ]
                
                result = self.validator.task_1_validate_cross_references()
                self.assertTrue(result)
        
        # Test with broken references
        with patch.object(self.validator, 'markdown_files', [
            Path('100_test-memory-context.md')
        ]):
            with patch.object(self.validator, 'read_file') as mock_read:
                mock_read.return_value = '<!-- CONTEXT_REFERENCE: non_existent.md -->'
                
                with patch.object(Path, 'exists') as mock_exists:
                    mock_exists.return_value = False
                    
                    result = self.validator.task_1_validate_cross_references()
                    self.assertFalse(result)
    
    def test_validate_file_naming_conventions(self):
        """Test file naming convention validation."""
        # Test with valid files
        with patch.object(self.validator, 'markdown_files', [
            Path('100_test-memory-context.md'),
            Path('200_test-naming-conventions.md'),
            Path('README.md')
        ]):
            result = self.validator.task_2_validate_file_naming_conventions()
            self.assertTrue(result)
        
        # Test with invalid files
        with patch.object(self.validator, 'markdown_files', [
            Path('invalid_file.md'),
            Path('100_test-memory-context.md')
        ]):
            result = self.validator.task_2_validate_file_naming_conventions()
            self.assertFalse(result)
    
    def test_validate_backlog_references(self):
        """Test backlog reference validation."""
        # Test with valid references
        with patch.object(self.validator, 'read_file') as mock_read:
            mock_read.side_effect = [
                '| B-001 | Test Item |',  # Backlog content
                'Reference to B-001 in documentation'  # Doc content
            ]
            
            result = self.validator.task_3_validate_backlog_references()
            self.assertTrue(result)
        
        # Test with invalid references
        with patch.object(self.validator, 'read_file') as mock_read:
            mock_read.side_effect = [
                '| B-001 | Test Item |',  # Backlog content
                'Reference to B-999 in documentation'  # Doc content with invalid ref
            ]
            
            result = self.validator.task_3_validate_backlog_references()
            self.assertFalse(result)
    
    def test_validate_memory_context_coherence(self):
        """Test memory context coherence validation."""
        # Test with coherent content
        with patch.object(self.validator, 'read_file') as mock_read:
            mock_read.side_effect = [
                'Current Sprint: B-001',  # Memory context
                '| B-001 | Test Item |',  # Backlog
                'System architecture includes DSPy'  # System overview
            ]
            
            result = self.validator.task_4_validate_memory_context_coherence()
            self.assertTrue(result)
        
        # Test with incoherent content
        with patch.object(self.validator, 'read_file') as mock_read:
            mock_read.side_effect = [
                'Current Sprint: B-999',  # Memory context with invalid ref
                '| B-001 | Test Item |',  # Backlog
                'System architecture'  # System overview
            ]
            
            result = self.validator.task_4_validate_memory_context_coherence()
            self.assertFalse(result)
    
    @patch('doc_coherence_validator.subprocess.run')
    def test_cursor_ai_semantic_validation(self, mock_run):
        """Test Cursor AI semantic validation."""
        # Mock Cursor AI as available
        self.validator.cursor_ai_enabled = True
        
        # Mock successful Cursor AI response
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '{"issues": []}'
        
        with patch.object(self.validator, 'priority_files', {
            'memory_context': ['100_test-memory-context.md']
        }):
            with patch.object(Path, 'exists') as mock_exists:
                mock_exists.return_value = True
                
                with patch.object(self.validator, 'read_file') as mock_read:
                    mock_read.return_value = 'Test content'
                    
                    result = self.validator.task_5_cursor_ai_semantic_validation()
                    self.assertTrue(result)
        
        # Test with Cursor AI issues
        mock_run.return_value.stdout = '{"issues": [{"type": "warning", "description": "Test issue"}]}'
        
        with patch.object(self.validator, 'priority_files', {
            'memory_context': ['100_test-memory-context.md']
        }):
            with patch.object(Path, 'exists') as mock_exists:
                mock_exists.return_value = True
                
                with patch.object(self.validator, 'read_file') as mock_read:
                    mock_read.return_value = 'Test content'
                    
                    result = self.validator.task_5_cursor_ai_semantic_validation()
                    self.assertFalse(result)
    
    def test_generate_validation_report(self):
        """Test validation report generation."""
        # Set up test data
        self.validator.validation_results = {
            'Cross-reference validation': True,
            'File naming conventions': False
        }
        self.validator.errors = ['Test error']
        self.validator.warnings = ['Test warning']
        
        with patch.object(Path, 'mkdir') as mock_mkdir:
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                
                result = self.validator.task_6_generate_validation_report()
                self.assertTrue(result)
                
                # Verify report was written
                mock_open.assert_called()
                mock_file.write.assert_called()
    
    def test_run_all_validations(self):
        """Test running all validation tasks."""
        # Mock all tasks to return True
        with patch.object(self.validator, 'task_1_validate_cross_references', return_value=True), \
             patch.object(self.validator, 'task_2_validate_file_naming_conventions', return_value=True), \
             patch.object(self.validator, 'task_3_validate_backlog_references', return_value=True), \
             patch.object(self.validator, 'task_4_validate_memory_context_coherence', return_value=True), \
             patch.object(self.validator, 'task_5_cursor_ai_semantic_validation', return_value=True), \
             patch.object(self.validator, 'task_6_generate_validation_report', return_value=True):
            
            result = self.validator.run_all_validations()
            self.assertTrue(result)
            self.assertEqual(len(self.validator.validation_results), 6)
        
        # Test with some failures
        with patch.object(self.validator, 'task_1_validate_cross_references', return_value=False), \
             patch.object(self.validator, 'task_2_validate_file_naming_conventions', return_value=True), \
             patch.object(self.validator, 'task_3_validate_backlog_references', return_value=True), \
             patch.object(self.validator, 'task_4_validate_memory_context_coherence', return_value=True), \
             patch.object(self.validator, 'task_5_cursor_ai_semantic_validation', return_value=True), \
             patch.object(self.validator, 'task_6_generate_validation_report', return_value=True):
            
            result = self.validator.run_all_validations()
            self.assertFalse(result)
    
    def test_cursor_ai_availability_check(self):
        """Test Cursor AI availability checking."""
        # Test when Cursor AI is available
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = self.validator._check_cursor_ai_availability()
            self.assertTrue(result)
        
        # Test when Cursor AI is not available
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            
            result = self.validator._check_cursor_ai_availability()
            self.assertFalse(result)
    
    def test_validate_file_with_cursor_ai(self):
        """Test Cursor AI file validation."""
        test_file = Path('test.md')
        
        # Test successful validation
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = '{"issues": []}'
            
            with patch.object(self.validator, 'read_file') as mock_read:
                mock_read.return_value = 'Test content'
                
                issues = self.validator._validate_file_with_cursor_ai(test_file, 'test_category')
                self.assertEqual(len(issues), 0)
        
        # Test validation with issues
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = '{"issues": [{"type": "warning", "description": "Test issue"}]}'
            
            with patch.object(self.validator, 'read_file') as mock_read:
                mock_read.return_value = 'Test content'
                
                issues = self.validator._validate_file_with_cursor_ai(test_file, 'test_category')
                self.assertEqual(len(issues), 1)
                self.assertEqual(issues[0]['issue'], 'Test issue')

class TestDocCoherenceValidatorIntegration(unittest.TestCase):
    """Integration tests for the validation system."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create a minimal project structure
        self.create_project_structure()
    
    def tearDown(self):
        """Clean up integration test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def create_project_structure(self):
        """Create a minimal project structure for testing."""
        # Create test files
        files = {
            '000_backlog.md': '''# Test Backlog
| B-001 | Test Item | 🔥 | 2 | todo | Test description | Tech | None |
''',
            '100_cursor-memory-context.md': '''# Test Memory Context
<!-- CONTEXT_REFERENCE: 400_system-overview.md -->
Current Sprint: B-001
''',
            '400_system-overview.md': '''# Test System Overview
System architecture includes DSPy and PostgreSQL.
''',
            '400_project-overview.md': '''# Test Project Overview
Project overview content.
''',
            '400_context-priority-guide.md': '''# Test Context Priority Guide
Context priority guide content.
'''
        }
        
        for filename, content in files.items():
            with open(filename, 'w') as f:
                f.write(content)
    
    def test_full_validation_workflow(self):
        """Test the complete validation workflow."""
        # Copy validator script to test directory
        validator_script = Path(__file__).parent.parent / 'scripts' / 'doc_coherence_validator.py'
        if validator_script.exists():
            shutil.copy(validator_script, self.test_dir)
            
            # Import and run validator
            sys.path.insert(0, self.test_dir)
            from doc_coherence_validator import DocCoherenceValidator
            
            validator = DocCoherenceValidator(dry_run=True)
            result = validator.run_all_validations()
            
            # Should pass with our test structure
            self.assertTrue(result)
    
    def test_validation_with_issues(self):
        """Test validation with known issues."""
        # Create a file with naming convention issues
        with open('invalid_file.md', 'w') as f:
            f.write('# Invalid File\nNo three-digit prefix.')
        
        # Copy validator script
        validator_script = Path(__file__).parent.parent / 'scripts' / 'doc_coherence_validator.py'
        if validator_script.exists():
            shutil.copy(validator_script, self.test_dir)
            
            sys.path.insert(0, self.test_dir)
            from doc_coherence_validator import DocCoherenceValidator
            
            validator = DocCoherenceValidator(dry_run=True)
            result = validator.run_all_validations()
            
            # Should fail due to naming convention issues
            self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
