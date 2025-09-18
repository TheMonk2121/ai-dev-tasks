"""
Tests for end_to_end_system_validation.py

Comprehensive tests for the EndToEndSystemValidator class and validation workflow.
Tests cover unit functionality, integration workflows, and system validation phases.
"""

#!/usr/bin/env python3

import asyncio
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, mock_open, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "300_evals"))
sys.path.insert(0, str(project_root / "src"))

from scripts.evaluation.end_to_end_system_validation import (
    EndToEndSystemValidator,
    SystemValidationReport,
    ValidationResult,
    main,
)


class TestValidationResult:
    """Test cases for ValidationResult dataclass."""

    def test_validation_result_creation(self):
        """Test ValidationResult creation."""
        result = ValidationResult(
            test_name="test_database",
            status="PASS",
            details="Database connection successful",
            duration_ms=150.5,
            timestamp=datetime.now(),
        )

        assert result.test_name == "test_database"
        assert result.status == "PASS"
        assert result.details == "Database connection successful"
        assert result.duration_ms == 150.5
        assert isinstance(result.timestamp, datetime)

    def test_validation_result_statuses(self):
        """Test ValidationResult with different statuses."""
        statuses = ["PASS", "FAIL", "WARNING"]

        for status in statuses:
            result = ValidationResult(
                test_name=f"test_{status.lower()}",
                status=status,
                details=f"Test {status}",
                duration_ms=100.0,
                timestamp=datetime.now(),
            )
            assert result.status == status


class TestSystemValidationReport:
    """Test cases for SystemValidationReport dataclass."""

    def test_system_validation_report_creation(self):
        """Test SystemValidationReport creation."""
        report = SystemValidationReport(
            overall_status="PASS",
            overall_score=0.95,
            total_tests=10,
            passed_tests=9,
            failed_tests=1,
            warning_tests=0,
            validation_results=[],
            timestamp=datetime.now(),
        )

        assert report.overall_status == "PASS"
        assert report.overall_score == 0.95
        assert report.total_tests == 10
        assert report.passed_tests == 9
        assert report.failed_tests == 1
        assert report.warning_tests == 0

    def test_system_validation_report_calculation(self):
        """Test SystemValidationReport score calculation."""
        results = [
            ValidationResult("test1", "PASS", "Success", 100.0, datetime.now()),
            ValidationResult("test2", "PASS", "Success", 200.0, datetime.now()),
            ValidationResult("test3", "FAIL", "Failed", 150.0, datetime.now()),
        ]

        report = SystemValidationReport(
            overall_status="PASS",
            overall_score=0.67,  # 2/3 tests passed
            total_tests=3,
            passed_tests=2,
            failed_tests=1,
            warning_tests=0,
            validation_results=results,
            timestamp=datetime.now(),
        )

        assert report.total_tests == 3
        assert report.passed_tests == 2
        assert report.failed_tests == 1


class TestEndToEndSystemValidator:
    """Test cases for EndToEndSystemValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = EndToEndSystemValidator()

    def test_initialization(self):
        """Test validator initializes correctly."""
        assert self.validator is not None
        assert hasattr(self.validator, "validation_results")
        assert isinstance(self.validator.validation_results, list)

    @patch("scripts.evaluation.end_to_end_system_validation.Psycopg3Config.get_cursor")
    def test_validate_database_connectivity_success(self, mock_connect):
        """Test database connectivity validation passes."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (1,)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        result = self.validator.validate_database_connectivity()

        assert result.test_name == "database_connectivity"
        assert result.status == "PASS"
        assert "successful" in result.details.lower()

    @patch("scripts.evaluation.end_to_end_system_validation.Psycopg3Config.get_cursor")
    def test_validate_database_connectivity_failure(self, mock_connect):
        """Test database connectivity validation fails."""
        mock_connect.side_effect = Exception("Connection failed")

        result = self.validator.validate_database_connectivity()

        assert result.test_name == "database_connectivity"
        assert result.status == "FAIL"
        assert "failed" in result.details.lower()

    @patch("scripts.evaluation.end_to_end_system_validation.LTSTMemorySystem")
    def test_validate_memory_system_success(self, mock_ltst_class):
        """Test memory system validation passes."""
        mock_ltst = Mock()
        mock_ltst_class.return_value = mock_ltst
        mock_ltst.health_check.return_value = True

        result = self.validator.validate_memory_system()

        assert result.test_name == "memory_system"
        assert result.status == "PASS"
        assert "healthy" in result.details.lower()

    @patch("scripts.evaluation.end_to_end_system_validation.LTSTMemorySystem")
    def test_validate_memory_system_failure(self, mock_ltst_class):
        """Test memory system validation fails."""
        mock_ltst = Mock()
        mock_ltst_class.return_value = mock_ltst
        mock_ltst.health_check.return_value = False

        result = self.validator.validate_memory_system()

        assert result.test_name == "memory_system"
        assert result.status == "FAIL"
        assert "unhealthy" in result.details.lower()

    @patch("scripts.evaluation.end_to_end_system_validation.HybridVectorStore")
    def test_validate_vector_store_success(self, mock_vector_class):
        """Test vector store validation passes."""
        mock_vector = Mock()
        mock_vector_class.return_value = mock_vector
        mock_vector.health_check.return_value = True

        result = self.validator.validate_vector_store()

        assert result.test_name == "vector_store"
        assert result.status == "PASS"
        assert "healthy" in result.details.lower()

    @patch("scripts.evaluation.end_to_end_system_validation.HybridVectorStore")
    def test_validate_vector_store_failure(self, mock_vector_class):
        """Test vector store validation fails."""
        mock_vector = Mock()
        mock_vector_class.return_value = mock_vector
        mock_vector.health_check.return_value = False

        result = self.validator.validate_vector_store()

        assert result.test_name == "vector_store"
        assert result.status == "FAIL"
        assert "unhealthy" in result.details.lower()

    @patch("scripts.evaluation.end_to_end_system_validation.RAGPipeline")
    def test_validate_rag_pipeline_success(self, mock_rag_class):
        """Test RAG pipeline validation passes."""
        mock_rag = Mock()
        mock_rag_class.return_value = mock_rag
        mock_rag.health_check.return_value = True

        result = self.validator.validate_rag_pipeline()

        assert result.test_name == "rag_pipeline"
        assert result.status == "PASS"
        assert "healthy" in result.details.lower()

    @patch("scripts.evaluation.end_to_end_system_validation.RAGPipeline")
    def test_validate_rag_pipeline_failure(self, mock_rag_class):
        """Test RAG pipeline validation fails."""
        mock_rag = Mock()
        mock_rag_class.return_value = mock_rag
        mock_rag.health_check.return_value = False

        result = self.validator.validate_rag_pipeline()

        assert result.test_name == "rag_pipeline"
        assert result.status == "FAIL"
        assert "unhealthy" in result.details.lower()

    @patch("scripts.evaluation.end_to_end_system_validation.UnifiedMemoryOrchestrator")
    def test_validate_memory_orchestrator_success(self, mock_orchestrator_class):
        """Test memory orchestrator validation passes."""
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.health_check.return_value = True

        result = self.validator.validate_memory_orchestrator()

        assert result.test_name == "memory_orchestrator"
        assert result.status == "PASS"
        assert "healthy" in result.details.lower()

    @patch("scripts.evaluation.end_to_end_system_validation.UnifiedMemoryOrchestrator")
    def test_validate_memory_orchestrator_failure(self, mock_orchestrator_class):
        """Test memory orchestrator validation fails."""
        mock_orchestrator = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator
        mock_orchestrator.health_check.return_value = False

        result = self.validator.validate_memory_orchestrator()

        assert result.test_name == "memory_orchestrator"
        assert result.status == "FAIL"
        assert "unhealthy" in result.details.lower()

    @patch("scripts.evaluation.end_to_end_system_validation.PostgreSQLCacheService")
    def test_validate_cache_service_success(self, mock_cache_class):
        """Test cache service validation passes."""
        mock_cache = Mock()
        mock_cache_class.return_value = mock_cache
        mock_cache.health_check.return_value = True

        result = self.validator.validate_cache_service()

        assert result.test_name == "cache_service"
        assert result.status == "PASS"
        assert "healthy" in result.details.lower()

    @patch("scripts.evaluation.end_to_end_system_validation.PostgreSQLCacheService")
    def test_validate_cache_service_failure(self, mock_cache_class):
        """Test cache service validation fails."""
        mock_cache = Mock()
        mock_cache_class.return_value = mock_cache
        mock_cache.health_check.return_value = False

        result = self.validator.validate_cache_service()

        assert result.test_name == "cache_service"
        assert result.status == "FAIL"
        assert "unhealthy" in result.details.lower()

    def test_validate_system_resources_success(self):
        """Test system resources validation passes."""
        with patch("scripts.evaluation.end_to_end_system_validation.psutil") as mock_psutil:
            mock_psutil.virtual_memory.return_value.percent = 50.0
            mock_psutil.disk_usage.return_value.percent = 60.0
            mock_psutil.cpu_percent.return_value = 30.0

            result = self.validator.validate_system_resources()

            assert result.test_name == "system_resources"
            assert result.status == "PASS"
            assert "healthy" in result.details.lower()

    def test_validate_system_resources_failure(self):
        """Test system resources validation fails."""
        with patch("scripts.evaluation.end_to_end_system_validation.psutil") as mock_psutil:
            mock_psutil.virtual_memory.return_value.percent = 95.0
            mock_psutil.disk_usage.return_value.percent = 90.0
            mock_psutil.cpu_percent.return_value = 95.0

            result = self.validator.validate_system_resources()

            assert result.test_name == "system_resources"
            assert result.status == "FAIL"
            assert "unhealthy" in result.details.lower()

    def test_validate_dependencies_success(self):
        """Test dependencies validation passes."""
        with patch("scripts.evaluation.end_to_end_system_validation.importlib.import_module") as mock_import:
            mock_import.return_value = Mock()

            result = self.validator.validate_dependencies()

            assert result.test_name == "dependencies"
            assert result.status == "PASS"
            assert "available" in result.details.lower()

    def test_validate_dependencies_failure(self):
        """Test dependencies validation fails."""
        with patch("scripts.evaluation.end_to_end_system_validation.importlib.import_module") as mock_import:
            mock_import.side_effect = ImportError("Module not found")

            result = self.validator.validate_dependencies()

            assert result.test_name == "dependencies"
            assert result.status == "FAIL"
            assert "missing" in result.details.lower()

    def test_run_comprehensive_validation(self):
        """Test running comprehensive validation."""
        with patch.object(self.validator, "validate_database_connectivity") as mock_db:
            with patch.object(self.validator, "validate_memory_system") as mock_memory:
                with patch.object(self.validator, "validate_vector_store") as mock_vector:
                    with patch.object(self.validator, "validate_rag_pipeline") as mock_rag:
                        with patch.object(self.validator, "validate_memory_orchestrator") as mock_orchestrator:
                            with patch.object(self.validator, "validate_cache_service") as mock_cache:
                                with patch.object(self.validator, "validate_system_resources") as mock_resources:
                                    with patch.object(self.validator, "validate_dependencies") as mock_deps:
                                        # Mock all validations to pass
                                        mock_db.return_value = ValidationResult(
                                            "db", "PASS", "OK", 100.0, datetime.now()
                                        )
                                        mock_memory.return_value = ValidationResult(
                                            "memory",
                                            "PASS",
                                            "OK",
                                            100.0,
                                            datetime.now(),
                                        )
                                        mock_vector.return_value = ValidationResult(
                                            "vector",
                                            "PASS",
                                            "OK",
                                            100.0,
                                            datetime.now(),
                                        )
                                        mock_rag.return_value = ValidationResult(
                                            "rag", "PASS", "OK", 100.0, datetime.now()
                                        )
                                        mock_orchestrator.return_value = ValidationResult(
                                            "orchestrator",
                                            "PASS",
                                            "OK",
                                            100.0,
                                            datetime.now(),
                                        )
                                        mock_cache.return_value = ValidationResult(
                                            "cache", "PASS", "OK", 100.0, datetime.now()
                                        )
                                        mock_resources.return_value = ValidationResult(
                                            "resources",
                                            "PASS",
                                            "OK",
                                            100.0,
                                            datetime.now(),
                                        )
                                        mock_deps.return_value = ValidationResult(
                                            "deps", "PASS", "OK", 100.0, datetime.now()
                                        )

                                        report = self.validator.run_comprehensive_validation()

                                        assert report.overall_status == "PASS"
                                        assert report.total_tests == 8
                                        assert report.passed_tests == 8
                                        assert report.failed_tests == 0
                                        assert len(report.validation_results) == 8

    def test_run_comprehensive_validation_with_failures(self):
        """Test running comprehensive validation with some failures."""
        with patch.object(self.validator, "validate_database_connectivity") as mock_db:
            with patch.object(self.validator, "validate_memory_system") as mock_memory:
                with patch.object(self.validator, "validate_vector_store") as mock_vector:
                    with patch.object(self.validator, "validate_rag_pipeline") as mock_rag:
                        with patch.object(self.validator, "validate_memory_orchestrator") as mock_orchestrator:
                            with patch.object(self.validator, "validate_cache_service") as mock_cache:
                                with patch.object(self.validator, "validate_system_resources") as mock_resources:
                                    with patch.object(self.validator, "validate_dependencies") as mock_deps:
                                        # Mock some validations to fail
                                        mock_db.return_value = ValidationResult(
                                            "db", "PASS", "OK", 100.0, datetime.now()
                                        )
                                        mock_memory.return_value = ValidationResult(
                                            "memory",
                                            "FAIL",
                                            "Error",
                                            100.0,
                                            datetime.now(),
                                        )
                                        mock_vector.return_value = ValidationResult(
                                            "vector",
                                            "PASS",
                                            "OK",
                                            100.0,
                                            datetime.now(),
                                        )
                                        mock_rag.return_value = ValidationResult(
                                            "rag",
                                            "FAIL",
                                            "Error",
                                            100.0,
                                            datetime.now(),
                                        )
                                        mock_orchestrator.return_value = ValidationResult(
                                            "orchestrator",
                                            "PASS",
                                            "OK",
                                            100.0,
                                            datetime.now(),
                                        )
                                        mock_cache.return_value = ValidationResult(
                                            "cache", "PASS", "OK", 100.0, datetime.now()
                                        )
                                        mock_resources.return_value = ValidationResult(
                                            "resources",
                                            "PASS",
                                            "OK",
                                            100.0,
                                            datetime.now(),
                                        )
                                        mock_deps.return_value = ValidationResult(
                                            "deps", "PASS", "OK", 100.0, datetime.now()
                                        )

                                        report = self.validator.run_comprehensive_validation()

                                        assert report.overall_status == "FAIL"
                                        assert report.total_tests == 8
                                        assert report.passed_tests == 6
                                        assert report.failed_tests == 2
                                        assert len(report.validation_results) == 8

    def test_generate_validation_report(self):
        """Test generating validation report."""
        results = [
            ValidationResult("test1", "PASS", "Success", 100.0, datetime.now()),
            ValidationResult("test2", "FAIL", "Failed", 200.0, datetime.now()),
            ValidationResult("test3", "WARNING", "Warning", 150.0, datetime.now()),
        ]

        report = self.validator._generate_validation_report(results)

        assert report.overall_status == "FAIL"  # Should fail due to FAIL result
        assert report.total_tests == 3
        assert report.passed_tests == 1
        assert report.failed_tests == 1
        assert report.warning_tests == 1
        assert report.overall_score == 0.33  # 1/3 tests passed

    def test_save_validation_report(self):
        """Test saving validation report."""
        report = SystemValidationReport(
            overall_status="PASS",
            overall_score=0.95,
            total_tests=5,
            passed_tests=5,
            failed_tests=0,
            warning_tests=0,
            validation_results=[],
            timestamp=datetime.now(),
        )

        with patch("builtins.open", mock_open()) as mock_file:
            with patch("json.dump") as mock_json_dump:
                self.validator._save_validation_report(report, "test_report.json")

                mock_file.assert_called_once_with("test_report.json", "w")
                mock_json_dump.assert_called_once()

    def test_print_validation_summary(self):
        """Test printing validation summary."""
        report = SystemValidationReport(
            overall_status="PASS",
            overall_score=0.95,
            total_tests=5,
            passed_tests=5,
            failed_tests=0,
            warning_tests=0,
            validation_results=[],
            timestamp=datetime.now(),
        )

        with patch("builtins.print") as mock_print:
            self.validator._print_validation_summary(report)

            mock_print.assert_called()
            calls = [result.get("key", "")
            summary_text = " ".join(calls)
            assert "PASS" in summary_text
            assert "5" in summary_text


class TestEndToEndSystemValidationCLI:
    """Test cases for CLI interface."""

    @patch("scripts.evaluation.end_to_end_system_validation.EndToEndSystemValidator")
    def test_main_success(self, mock_validator_class):
        """Test main function runs successfully."""
        mock_validator = Mock()
        mock_report = SystemValidationReport(
            overall_status="PASS",
            overall_score=0.95,
            total_tests=5,
            passed_tests=5,
            failed_tests=0,
            warning_tests=0,
            validation_results=[],
            timestamp=datetime.now(),
        )
        mock_validator.run_comprehensive_validation.return_value = mock_report
        mock_validator_class.return_value = mock_validator

        with patch("sys.argv", ["end_to_end_system_validation.py"]):
            with patch("scripts.evaluation.end_to_end_system_validation.sys.exit") as mock_exit:
                main()

                mock_validator.run_comprehensive_validation.assert_called_once()
                mock_exit.assert_called_once_with(0)

    @patch("scripts.evaluation.end_to_end_system_validation.EndToEndSystemValidator")
    def test_main_validation_failure(self, mock_validator_class):
        """Test main function handles validation failure."""
        mock_validator = Mock()
        mock_report = SystemValidationReport(
            overall_status="FAIL",
            overall_score=0.5,
            total_tests=5,
            passed_tests=2,
            failed_tests=3,
            warning_tests=0,
            validation_results=[],
            timestamp=datetime.now(),
        )
        mock_validator.run_comprehensive_validation.return_value = mock_report
        mock_validator_class.return_value = mock_validator

        with patch("sys.argv", ["end_to_end_system_validation.py"]):
            with patch("scripts.evaluation.end_to_end_system_validation.sys.exit") as mock_exit:
                main()

                mock_validator.run_comprehensive_validation.assert_called_once()
                mock_exit.assert_called_once_with(1)

    @patch("sys.argv", ["end_to_end_system_validation.py", "--help"])
    def test_main_help(self):
        """Test main function shows help."""
        with patch("scripts.evaluation.end_to_end_system_validation.argparse.ArgumentParser.print_help"):
            with patch("scripts.evaluation.end_to_end_system_validation.sys.exit") as mock_exit:
                main()

                mock_exit.assert_called_once_with(0)

    @patch("scripts.evaluation.end_to_end_system_validation.EndToEndSystemValidator")
    def test_main_with_output_file(self, mock_validator_class):
        """Test main function with output file."""
        mock_validator = Mock()
        mock_report = SystemValidationReport(
            overall_status="PASS",
            overall_score=0.95,
            total_tests=5,
            passed_tests=5,
            failed_tests=0,
            warning_tests=0,
            validation_results=[],
            timestamp=datetime.now(),
        )
        mock_validator.run_comprehensive_validation.return_value = mock_report
        mock_validator_class.return_value = mock_validator

        with patch(
            "sys.argv",
            ["end_to_end_system_validation.py", "--output", "test_report.json"],
        ):
            with patch("scripts.evaluation.end_to_end_system_validation.sys.exit") as mock_exit:
                with patch.object(mock_validator, "_save_validation_report") as mock_save:
                    main()

                    mock_validator.run_comprehensive_validation.assert_called_once()
                    mock_save.assert_called_once_with(mock_report, "test_report.json")
                    mock_exit.assert_called_once_with(0)


class TestEndToEndSystemValidationIntegration:
    """Integration tests for EndToEndSystemValidator."""

    def test_validation_workflow_integration(self):
        """Test complete validation workflow integration."""
        validator = EndToEndSystemValidator()

        # Mock all external dependencies
        with patch("scripts.evaluation.end_to_end_system_validation.Psycopg3Config.get_cursor"):
            with patch("scripts.evaluation.end_to_end_system_validation.LTSTMemorySystem"):
                with patch("scripts.evaluation.end_to_end_system_validation.HybridVectorStore"):
                    with patch("scripts.evaluation.end_to_end_system_validation.RAGPipeline"):
                        with patch("scripts.evaluation.end_to_end_system_validation.UnifiedMemoryOrchestrator"):
                            with patch("scripts.evaluation.end_to_end_system_validation.PostgreSQLCacheService"):
                                with patch("scripts.evaluation.end_to_end_system_validation.psutil"):
                                    with patch(
                                        "scripts.evaluation.end_to_end_system_validation.importlib.import_module"
                                    ):
                                        report = validator.run_comprehensive_validation()

                                        assert isinstance(report, SystemValidationReport)
                                        assert report.total_tests > 0
                                        assert report.overall_score >= 0.0
                                        assert report.overall_score <= 1.0

    def test_validation_with_realistic_scenario(self):
        """Test validation with realistic mixed results scenario."""
        validator = EndToEndSystemValidator()

        # Mock realistic scenario: most systems healthy, some issues
        with patch("scripts.evaluation.end_to_end_system_validation.Psycopg3Config.get_cursor") as mock_db:
            with patch("scripts.evaluation.end_to_end_system_validation.LTSTMemorySystem") as mock_ltst:
                with patch("scripts.evaluation.end_to_end_system_validation.HybridVectorStore") as mock_vector:
                    with patch("scripts.evaluation.end_to_end_system_validation.RAGPipeline") as mock_rag:
                        with patch(
                            "scripts.evaluation.end_to_end_system_validation.UnifiedMemoryOrchestrator"
                        ) as mock_orchestrator:
                            with patch(
                                "scripts.evaluation.end_to_end_system_validation.PostgreSQLCacheService"
                            ) as mock_cache:
                                with patch("scripts.evaluation.end_to_end_system_validation.psutil") as mock_psutil:
                                    with patch(
                                        "scripts.evaluation.end_to_end_system_validation.importlib.import_module"
                                    ) as mock_import:
                                        # Mock database connection success
                                        mock_conn = Mock()
                                        mock_cursor = Mock()
                                        mock_cursor.fetchone.return_value = (1,)
                                        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
                                        mock_db.return_value.__enter__.return_value = mock_conn

                                        # Mock memory system failure
                                        mock_ltst_instance = Mock()
                                        mock_ltst_instance.health_check.return_value = False
                                        mock_ltst.return_value = mock_ltst_instance

                                        # Mock other systems as healthy
                                        mock_vector_instance = Mock()
                                        mock_vector_instance.health_check.return_value = True
                                        mock_vector.return_value = mock_vector_instance

                                        mock_rag_instance = Mock()
                                        mock_rag_instance.health_check.return_value = True
                                        mock_rag.return_value = mock_rag_instance

                                        mock_orchestrator_instance = Mock()
                                        mock_orchestrator_instance.health_check.return_value = True
                                        mock_orchestrator.return_value = mock_orchestrator_instance

                                        mock_cache_instance = Mock()
                                        mock_cache_instance.health_check.return_value = True
                                        mock_cache.return_value = mock_cache_instance

                                        # Mock system resources as healthy
                                        mock_psutil.virtual_memory.return_value.percent = 50.0
                                        mock_psutil.disk_usage.return_value.percent = 60.0
                                        mock_psutil.cpu_percent.return_value = 30.0

                                        # Mock dependencies as available
                                        mock_import.return_value = Mock()

                                        report = validator.run_comprehensive_validation()

                                        assert report.overall_status == "FAIL"  # Should fail due to memory system
                                        assert report.failed_tests >= 1
                                        assert report.passed_tests >= 6  # Most systems should pass


if __name__ == "__main__":
    pytest.main([__file__])
