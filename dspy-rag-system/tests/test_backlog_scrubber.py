#!/usr/bin/env python3
"""
Unit tests for the backlog scrubber functionality.
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from n8n_workflows.backlog_scrubber import BacklogScrubber

class TestBacklogScrubber(unittest.TestCase):
    """Test backlog scrubber functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create temporary backlog file
        self.temp_dir = tempfile.mkdtemp()
        self.backlog_path = Path(self.temp_dir) / "test_backlog.md"
        
        # Sample backlog content with scoring metadata
        self.sample_content = """# Test Backlog

| ID  | Title | 🔥P | 🎯Points | Status | Description |
|-----|-------|-----|----------|--------|-------------|
| B-001 | Test Item 1 | 🔥 | 3 | todo | Test description |
<!--score: {bv:5, tc:3, rr:5, le:4, effort:3, deps:[]}-->
<!--score_total: 5.7-->
| B-002 | Test Item 2 | 🔥 | 2 | todo | Test description |
<!--score: {bv:4, tc:2, rr:3, le:3, effort:2, deps:[]}-->
<!--score_total: 6.0-->
| B-003 | Test Item 3 | ⭐ | 5 | todo | Test description |
<!--score: {bv:3, tc:1, rr:2, le:2, effort:5, deps:[]}-->
"""
        
        # Write sample content to file
        self.backlog_path.write_text(self.sample_content, encoding='utf-8')
        
        # Initialize scrubber with test file
        self.scrubber = BacklogScrubber(str(self.backlog_path))
    
    def tearDown(self):
        """Clean up test fixtures"""
        # Remove temporary files
        if self.backlog_path.exists():
            self.backlog_path.unlink()
        if self.scrubber.backup_path.exists():
            self.scrubber.backup_path.unlink()
        os.rmdir(self.temp_dir)
    
    def test_initialization(self):
        """Test scrubber initialization"""
        self.assertEqual(self.scrubber.backlog_path, self.backlog_path)
        self.assertIsNotNone(self.scrubber.scoring_formula)
        self.assertIsNotNone(self.scrubber.score_pattern)
        self.assertIsNotNone(self.scrubber.score_total_pattern)
    
    def test_read_backlog(self):
        """Test reading backlog file"""
        content = self.scrubber.read_backlog()
        self.assertIsInstance(content, str)
        self.assertIn("Test Backlog", content)
        self.assertIn("B-001", content)
    
    def test_read_backlog_file_not_found(self):
        """Test reading non-existent backlog file"""
        scrubber = BacklogScrubber("/nonexistent/file.md")
        with self.assertRaises(FileNotFoundError):
            scrubber.read_backlog()
    
    def test_parse_score_metadata(self):
        """Test parsing score metadata"""
        content = self.scrubber.read_backlog()
        scores = self.scrubber.parse_score_metadata(content)
        
        self.assertEqual(len(scores), 3)
        
        # Check first score
        first_score = scores[0]
        self.assertEqual(first_score['score_total'], 5.7)
        self.assertEqual(first_score['components']['bv'], 5)
        self.assertEqual(first_score['components']['tc'], 3)
        self.assertEqual(first_score['components']['rr'], 5)
        self.assertEqual(first_score['components']['le'], 4)
        self.assertEqual(first_score['components']['effort'], 3)
    
    def test_parse_score_metadata_invalid_json(self):
        """Test parsing invalid JSON in score metadata"""
        invalid_content = """# Test

| ID | Title | Status |
|----|-------|--------|
| B-001 | Test | todo |
<!--score: {invalid json}-->
"""
        
        scrubber = BacklogScrubber()
        scores = scrubber.parse_score_metadata(invalid_content)
        self.assertEqual(len(scores), 0)
        self.assertEqual(scrubber.stats["errors_found"], 1)
    
    def test_validate_scores(self):
        """Test score validation"""
        content = self.scrubber.read_backlog()
        scores = self.scrubber.parse_score_metadata(content)
        validated = self.scrubber.validate_scores(scores)
        
        # All scores should be valid
        self.assertEqual(len(validated), len(scores))
    
    def test_validate_scores_invalid(self):
        """Test validation of invalid scores"""
        invalid_scores = [
            {
                'components': {'bv': 11, 'tc': 5, 'rr': 5, 'le': 5, 'effort': 3},
                'score_total': 8.7
            },
            {
                'components': {'bv': 5, 'tc': 5, 'rr': 5, 'le': 5, 'effort': 0},
                'score_total': 20.0
            }
        ]
        
        validated = self.scrubber.validate_scores(invalid_scores)
        self.assertEqual(len(validated), 0)
        self.assertEqual(self.scrubber.stats["errors_found"], 2)
    
    def test_update_score_totals(self):
        """Test updating score totals"""
        content = self.scrubber.read_backlog()
        scores = self.scrubber.parse_score_metadata(content)
        validated_scores = self.scrubber.validate_scores(scores)
        
        updated_content = self.scrubber.update_score_totals(content, validated_scores)
        
        # Check that score totals are present
        self.assertIn("<!--score_total: 5.7-->", updated_content)
        self.assertIn("<!--score_total: 6.0-->", updated_content)
    
    def test_update_score_totals_new_scores(self):
        """Test adding new score totals"""
        content = """# Test

| ID | Title | Status |
|----|-------|--------|
| B-001 | Test | todo |
<!--score: {bv:5, tc:3, rr:5, le:4, effort:3, deps:[]}-->
"""
        
        scores = self.scrubber.parse_score_metadata(content)
        validated_scores = self.scrubber.validate_scores(scores)
        
        updated_content = self.scrubber.update_score_totals(content, validated_scores)
        
        # Check that new score total was added
        self.assertIn("<!--score_total: 5.7-->", updated_content)
    
    def test_create_backup(self):
        """Test backup creation"""
        success = self.scrubber.create_backup()
        self.assertTrue(success)
        self.assertTrue(self.scrubber.backup_path.exists())
    
    def test_write_backlog(self):
        """Test writing backlog file"""
        test_content = "# Updated Backlog\n\nUpdated content"
        success = self.scrubber.write_backlog(test_content)
        self.assertTrue(success)
        
        # Check that file was written
        written_content = self.backlog_path.read_text(encoding='utf-8')
        self.assertEqual(written_content, test_content)
    
    def test_scrub_backlog(self):
        """Test complete backlog scrub operation"""
        result = self.scrubber.scrub_backlog()
        
        self.assertTrue(result["success"])
        self.assertGreater(result["items_processed"], 0)
        self.assertGreaterEqual(result["scores_updated"], 0)
        self.assertIsNotNone(result["stats"]["last_run"])
    
    def test_scrub_backlog_with_errors(self):
        """Test backlog scrub with parsing errors"""
        # Create content with invalid JSON
        invalid_content = """# Test

| ID | Title | Status |
|----|-------|--------|
| B-001 | Test | todo |
<!--score: {invalid json}-->
"""
        
        self.backlog_path.write_text(invalid_content, encoding='utf-8')
        
        result = self.scrubber.scrub_backlog()
        
        # Should still succeed but with errors
        self.assertTrue(result["success"])
        self.assertGreater(result["errors_found"], 0)
    
    def test_get_statistics(self):
        """Test getting statistics"""
        stats = self.scrubber.get_statistics()
        
        self.assertIn("items_processed", stats)
        self.assertIn("scores_updated", stats)
        self.assertIn("errors_found", stats)
        self.assertIn("last_run", stats)
    
    def test_reset_statistics(self):
        """Test resetting statistics"""
        # Run a scrub to populate stats
        self.scrubber.scrub_backlog()
        
        # Reset stats
        self.scrubber.reset_statistics()
        
        stats = self.scrubber.get_statistics()
        self.assertEqual(stats["items_processed"], 0)
        self.assertEqual(stats["scores_updated"], 0)
        self.assertEqual(stats["errors_found"], 0)
        self.assertIsNone(stats["last_run"])
    
    def test_scoring_formula(self):
        """Test scoring formula calculation"""
        # Test with sample values
        bv, tc, rr, le, effort = 5, 3, 5, 4, 3
        expected_score = (5 + 3 + 5 + 4) / 3  # 17 / 3 = 5.67
        
        calculated_score = self.scrubber.scoring_formula(bv, tc, rr, le, effort)
        self.assertAlmostEqual(calculated_score, expected_score, places=1)
    
    def test_regex_patterns(self):
        """Test regex pattern matching"""
        # Test score pattern
        test_score = "<!--score: {bv:5, tc:3, rr:5, le:4, effort:3, deps:[]}-->"
        match = self.scrubber.score_pattern.search(test_score)
        self.assertIsNotNone(match)
        
        # Test score total pattern
        test_total = "<!--score_total: 5.7-->"
        match = self.scrubber.score_total_pattern.search(test_total)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "5.7")

class TestBacklogScrubberIntegration(unittest.TestCase):
    """Integration tests for backlog scrubber"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.backlog_path = Path(self.temp_dir) / "integration_backlog.md"
        
        # Create a more complex backlog for integration testing
        self.complex_content = """# Integration Test Backlog

## High Priority Items

| ID  | Title | 🔥P | 🎯Points | Status | Description |
|-----|-------|-----|----------|--------|-------------|
| B-001 | Critical Feature | 🔥 | 3 | todo | High business value |
<!--score: {bv:8, tc:6, rr:7, le:5, effort:3, deps:[]}-->
<!--score_total: 8.7-->
| B-002 | Important Fix | 🔥 | 2 | todo | Important technical fix |
<!--score: {bv:6, tc:8, rr:4, le:6, effort:2, deps:[]}-->
<!--score_total: 12.0-->

## Medium Priority Items

| ID  | Title | 🔥P | 🎯Points | Status | Description |
|-----|-------|-----|----------|--------|-------------|
| B-003 | Nice to Have | ⭐ | 5 | todo | Nice to have feature |
<!--score: {bv:3, tc:2, rr:2, le:3, effort:5, deps:[]}-->
<!--score_total: 2.0-->
| B-004 | Documentation | ⭐ | 1 | todo | Documentation update |
<!--score: {bv:2, tc:1, rr:1, le:2, effort:1, deps:[]}-->
<!--score_total: 6.0-->

## Low Priority Items

| ID  | Title | 🔥P | 🎯Points | Status | Description |
|-----|-------|-----|----------|--------|-------------|
| B-005 | Future Enhancement | 🔧 | 8 | todo | Future enhancement |
<!--score: {bv:2, tc:1, rr:1, le:1, effort:8, deps:[]}-->
<!--score_total: 0.6-->
"""
        
        self.backlog_path.write_text(self.complex_content, encoding='utf-8')
        self.scrubber = BacklogScrubber(str(self.backlog_path))
    
    def tearDown(self):
        """Clean up integration test fixtures"""
        if self.backlog_path.exists():
            self.backlog_path.unlink()
        if self.scrubber.backup_path.exists():
            self.scrubber.backup_path.unlink()
        os.rmdir(self.temp_dir)
    
    def test_complex_backlog_processing(self):
        """Test processing a complex backlog with multiple sections"""
        result = self.scrubber.scrub_backlog()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["items_processed"], 5)
        self.assertGreaterEqual(result["scores_updated"], 0)
    
    def test_score_validation_complex(self):
        """Test score validation with complex backlog"""
        content = self.scrubber.read_backlog()
        scores = self.scrubber.parse_score_metadata(content)
        validated = self.scrubber.validate_scores(scores)
        
        # All scores should be valid
        self.assertEqual(len(validated), 5)
        
        # Check that scores are calculated correctly
        expected_scores = [8.7, 12.0, 2.0, 6.0, 0.6]
        actual_scores = [score['score_total'] for score in validated]
        
        for expected, actual in zip(expected_scores, actual_scores):
            self.assertAlmostEqual(expected, actual, places=1)
    
    def test_backup_and_restore(self):
        """Test backup creation and file integrity"""
        # Run scrub to create backup
        result = self.scrubber.scrub_backlog()
        self.assertTrue(result["success"])
        
        # Check backup exists
        self.assertTrue(self.scrubber.backup_path.exists())
        
        # Check original file still exists and is readable
        self.assertTrue(self.backlog_path.exists())
        content = self.backlog_path.read_text(encoding='utf-8')
        self.assertIn("Integration Test Backlog", content)

if __name__ == "__main__":
    unittest.main() 