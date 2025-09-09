#!/usr/bin/env python3
"""
Tests for enhanced file validator with OpenTelemetry integration
"""

import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from utils.enhanced_file_validator import (
    EnhancedFileValidator,
    FileValidationError,
    FileCorruptionError,
    validate_file_with_tracing,
    get_quarantine_status,
)
from utils.opentelemetry_config import initialize_opentelemetry, shutdown_opentelemetry


class TestEnhancedFileValidator(unittest.TestCase):
    """Test enhanced file validator functionality"""

    def setUp(self):
        """Set up test fixtures"""
        # Initialize OpenTelemetry for testing
        initialize_opentelemetry(
            service_name="test-service",
            enable_console_exporter=True,
            enable_requests_instrumentation=False,
            enable_flask_instrumentation=False,
            enable_logging_instrumentation=False,
        )

        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp()
        self.quarantine_dir = os.path.join(self.temp_dir, "quarantine")

        # Create test files
        self.valid_txt_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.valid_txt_file, "w") as f:
            f.write("This is a valid text file for testing.")

        self.valid_csv_file = os.path.join(self.temp_dir, "test.csv")
        with open(self.valid_csv_file, "w") as f:
            f.write("name,age,city\nJohn,30,New York\nJane,25,Los Angeles")

        # Create corrupted file
        self.corrupted_file = os.path.join(self.temp_dir, "corrupted.txt")
        with open(self.corrupted_file, "wb") as f:
            f.write(b"\x00" * 1000)  # File with many null bytes

        # Create large file
        self.large_file = os.path.join(self.temp_dir, "large.txt")
        with open(self.large_file, "w") as f:
            f.write("x" * (100 * 1024 * 1024))  # 100MB file

        # Create invalid extension file
        self.invalid_ext_file = os.path.join(self.temp_dir, "test.exe")
        with open(self.invalid_ext_file, "w") as f:
            f.write("This is an executable file.")

        self.validator = EnhancedFileValidator(quarantine_dir=self.quarantine_dir)

    def tearDown(self):
        """Clean up test fixtures"""
        shutdown_opentelemetry()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_valid_text_file(self):
        """Test validation of a valid text file"""
        result = self.validator.validate_file_with_tracing(self.valid_txt_file)

        self.assertTrue(result["validation_passed"])
        self.assertFalse(result["corruption_detected"])
        self.assertIn("correlation_id", result)
        self.assertIn("integrity_checksum", result)
        self.assertEqual(result["file_extension"], "txt")

    def test_validate_valid_csv_file(self):
        """Test validation of a valid CSV file"""
        result = self.validator.validate_file_with_tracing(self.valid_csv_file)

        self.assertTrue(result["validation_passed"])
        self.assertFalse(result["corruption_detected"])
        self.assertEqual(result["file_extension"], "csv")

    def test_validate_corrupted_file(self):
        """Test validation of a corrupted file"""
        result = self.validator.validate_file_with_tracing(self.corrupted_file)

        self.assertFalse(result["validation_passed"])
        self.assertTrue(result["corruption_detected"])
        self.assertIn("quarantine_path", result)
        self.assertIn("error_message", result)

    def test_validate_large_file(self):
        """Test validation of a file that exceeds size limit"""
        result = self.validator.validate_file_with_tracing(self.large_file)

        self.assertFalse(result["validation_passed"])
        self.assertFalse(result["corruption_detected"])
        self.assertIn("error_message", result)

    def test_validate_invalid_extension(self):
        """Test validation of a file with invalid extension"""
        result = self.validator.validate_file_with_tracing(self.invalid_ext_file)

        self.assertFalse(result["validation_passed"])
        self.assertFalse(result["corruption_detected"])
        self.assertIn("error_message", result)

    def test_validate_nonexistent_file(self):
        """Test validation of a nonexistent file"""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")
        result = self.validator.validate_file_with_tracing(nonexistent_file)

        self.assertFalse(result["validation_passed"])
        self.assertFalse(result["corruption_detected"])
        self.assertIn("error_message", result)

    def test_validate_basic_file_properties(self):
        """Test basic file properties validation"""
        result = self.validator._validate_basic_file_properties(self.valid_txt_file)

        self.assertTrue(result["file_path_valid"])
        self.assertIn("file_size_bytes", result)
        self.assertEqual(result["file_extension"], "txt")

    def test_validate_file_integrity(self):
        """Test file integrity validation"""
        result = self.validator._validate_file_integrity(self.valid_txt_file)

        self.assertTrue(result["integrity_valid"])
        self.assertIn("checksum", result)
        self.assertEqual(len(result["integrity_issues"]), 0)

    def test_validate_file_integrity_corrupted(self):
        """Test file integrity validation with corrupted file"""
        with self.assertRaises(FileCorruptionError):
            self.validator._validate_file_integrity(self.corrupted_file)

    def test_detect_corruption(self):
        """Test corruption detection"""
        result = self.validator._detect_corruption(self.valid_txt_file)

        self.assertFalse(result["corruption_detected"])
        self.assertEqual(len(result["corruption_indicators"]), 0)

    def test_detect_corruption_corrupted_file(self):
        """Test corruption detection with corrupted file"""
        with self.assertRaises(FileCorruptionError):
            self.validator._detect_corruption(self.corrupted_file)

    def test_validate_security(self):
        """Test security validation"""
        result = self.validator._validate_security(self.valid_txt_file)

        self.assertTrue(result["security_valid"])
        self.assertEqual(len(result["security_violations"]), 0)

    def test_validate_security_path_traversal(self):
        """Test security validation with path traversal attempt"""
        malicious_path = os.path.join(self.temp_dir, "..", "..", "etc", "passwd")
        with self.assertRaises(FileValidationError):
            self.validator._validate_security(malicious_path)

    def test_quarantine_file(self):
        """Test file quarantine functionality"""
        test_file = os.path.join(self.temp_dir, "test_quarantine.txt")
        with open(test_file, "w") as f:
            f.write("Test file for quarantine")

        correlation_id = "test-correlation-id"
        quarantine_path = self.validator._quarantine_file(test_file, correlation_id, "test")

        self.assertTrue(os.path.exists(quarantine_path))
        self.assertFalse(os.path.exists(test_file))
        self.assertIn(correlation_id[:8], os.path.basename(quarantine_path))

    def test_get_quarantine_status(self):
        """Test quarantine status retrieval"""
        # Create some quarantined files
        quarantine_file1 = os.path.join(self.quarantine_dir, "20240101_123456_corruption_test1.txt")
        quarantine_file2 = os.path.join(self.quarantine_dir, "20240101_123457_security_test2.txt")

        with open(quarantine_file1, "w") as f:
            f.write("Quarantined file 1")
        with open(quarantine_file2, "w") as f:
            f.write("Quarantined file 2")

        status = self.validator.get_quarantine_status()

        self.assertEqual(status["total_files"], 2)
        self.assertEqual(len(status["files"]), 2)
        self.assertIn("quarantine_dir", status)

        # Check file details
        file_reasons = [f["reason"] for f in status["files"]]
        self.assertIn("corruption", file_reasons)
        self.assertIn("security", file_reasons)


class TestEnhancedFileValidatorFunctions(unittest.TestCase):
    """Test enhanced file validator utility functions"""

    def setUp(self):
        """Set up test fixtures"""
        initialize_opentelemetry(
            service_name="test-service",
            enable_console_exporter=True,
            enable_requests_instrumentation=False,
            enable_flask_instrumentation=False,
            enable_logging_instrumentation=False,
        )

        self.temp_dir = tempfile.mkdtemp()
        self.valid_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.valid_file, "w") as f:
            f.write("Test file content")

    def tearDown(self):
        """Clean up test fixtures"""
        shutdown_opentelemetry()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validate_file_with_tracing_function(self):
        """Test validate_file_with_tracing function"""
        result = validate_file_with_tracing(self.valid_file)

        self.assertTrue(result["validation_passed"])
        self.assertFalse(result["corruption_detected"])
        self.assertIn("correlation_id", result)

    def test_get_quarantine_status_function(self):
        """Test get_quarantine_status function"""
        status = get_quarantine_status()

        self.assertIn("quarantine_dir", status)
        self.assertIn("total_files", status)
        self.assertIn("files", status)


class TestEnhancedFileValidatorIntegration(unittest.TestCase):
    """Test enhanced file validator integration scenarios"""

    def setUp(self):
        """Set up test fixtures"""
        initialize_opentelemetry(
            service_name="test-service",
            enable_console_exporter=True,
            enable_requests_instrumentation=False,
            enable_flask_instrumentation=False,
            enable_logging_instrumentation=False,
        )

        self.temp_dir = tempfile.mkdtemp()
        self.validator = EnhancedFileValidator(quarantine_dir=os.path.join(self.temp_dir, "quarantine"))

    def tearDown(self):
        """Clean up test fixtures"""
        shutdown_opentelemetry()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_pdf_file_validation(self):
        """Test PDF file validation"""
        pdf_file = os.path.join(self.temp_dir, "test.pdf")

        # Create a simple PDF file (minimal valid PDF)
        with open(pdf_file, "wb") as f:
            f.write(
                b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Contents 4 0 R\n>>\nendobj\n4 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 12 Tf\n72 720 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000204 00000 n \ntrailer\n<<\n/Size 5\n/Root 1 0 R\n>>\nstartxref\n297\n%%EOF\n"
            )

        result = self.validator.validate_file_with_tracing(pdf_file)

        self.assertTrue(result["validation_passed"])
        self.assertEqual(result["file_extension"], "pdf")

    def test_invalid_pdf_file_validation(self):
        """Test invalid PDF file validation"""
        invalid_pdf_file = os.path.join(self.temp_dir, "invalid.pdf")

        # Create an invalid PDF file
        with open(invalid_pdf_file, "wb") as f:
            f.write(b"This is not a valid PDF file")

        result = self.validator.validate_file_with_tracing(invalid_pdf_file)

        self.assertFalse(result["validation_passed"])
        self.assertTrue(result["corruption_detected"])

    def test_empty_csv_file_validation(self):
        """Test empty CSV file validation"""
        empty_csv_file = os.path.join(self.temp_dir, "empty.csv")

        # Create an empty CSV file
        with open(empty_csv_file, "w") as f:
            pass

        result = self.validator.validate_file_with_tracing(empty_csv_file)

        self.assertFalse(result["validation_passed"])
        self.assertTrue(result["corruption_detected"])

    def test_single_line_csv_file_validation(self):
        """Test single line CSV file validation"""
        single_line_csv_file = os.path.join(self.temp_dir, "single.csv")

        # Create a single line CSV file
        with open(single_line_csv_file, "w") as f:
            f.write("This is not a proper CSV file")

        result = self.validator.validate_file_with_tracing(single_line_csv_file)

        self.assertFalse(result["validation_passed"])
        self.assertTrue(result["corruption_detected"])


if __name__ == "__main__":
    unittest.main()
