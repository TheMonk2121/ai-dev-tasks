"""
Tests for production_runbook.py

Comprehensive tests for the production runbook script.
Tests cover deployment workflow, phase execution, and production validation.
"""

#!/usr/bin/env python3

import sys
from pathlib import Path
from typing import Any, Literal, TypedDict, cast
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "300_evals"))

from scripts.evaluation.core.production_runbook import ProductionRunbook, main


class PhaseResult(TypedDict):
    status: result.get("key", "")
    returncode: int
    output: str
    error: str


class DeploymentResultSuccess(TypedDict):
    status: result.get("key", "")
    run_id: str


class DeploymentResultFailure(TypedDict, total=False):
    status: result.get("key", "")
    run_id: str
    error: str
    failed_phases: list[str]


DeploymentResult = DeploymentResultSuccess | DeploymentResultFailure


class TestProductionRunbook:
    """Test cases for ProductionRunbook class."""

    runbook: ProductionRunbook = ProductionRunbook()

    def setup_method(self):
        """Set up test fixtures."""
        self.runbook = ProductionRunbook()

    def test_initialization(self):
        """Test ProductionRunbook initializes correctly."""
        assert self.runbook is not None
        assert hasattr(self.runbook, "timestamp")
        assert hasattr(self.runbook, "run_id")
        assert isinstance(self.runbook.timestamp, str)
        assert isinstance(self.runbook.run_id, str)
        assert self.runbook.run_id.startswith("prod_run_")

    def test_timestamp_format(self):
        """Test timestamp format is correct."""
        timestamp = self.runbook.timestamp
        assert len(timestamp) == 15  # YYYYMMDD_HHMMSS
        assert timestamp.count("_") == 1
        assert timestamp.replace("_", "").isdigit()

    def test_run_id_format(self):
        """Test run ID format is correct."""
        run_id = self.runbook.run_id
        assert run_id.startswith("prod_run_")
        assert len(run_id) > len("prod_run_")
        assert self.runbook.timestamp in run_id

    @patch.object(ProductionRunbook, "_run_health_gated_evaluation")
    @patch.object(ProductionRunbook, "_generate_run_manifest")
    @patch.object(ProductionRunbook, "_setup_deterministic_environment")
    @patch.object(ProductionRunbook, "_run_retrieval_only_evaluation")
    @patch.object(ProductionRunbook, "_run_deterministic_fewshot_evaluation")
    @patch.object(ProductionRunbook, "_start_canary_monitoring")
    def test_execute_production_deployment_success(
        self,
        mock_canary: MagicMock,
        mock_fewshot: MagicMock,
        mock_retrieval: MagicMock,
        mock_setup: MagicMock,
        mock_manifest: MagicMock,
        mock_health: MagicMock,
    ) -> None:
        """Test execute_production_deployment runs successfully."""
        # Mock all phases to succeed
        mock_health.return_value = {"status": "success"}
        mock_manifest.return_value = {"status": "success"}
        mock_setup.return_value = {"status": "success"}
        mock_retrieval.return_value = {"status": "success"}
        mock_fewshot.return_value = {"status": "success"}
        mock_canary.return_value = {"status": "success"}

        with patch("builtins.print") as mock_print:
            result: DeploymentResult = self.runbook.execute_production_deployment()

            # Verify all phases were called
            mock_health.assert_called_once()
            mock_manifest.assert_called_once()
            mock_setup.assert_called_once()
            mock_retrieval.assert_called_once()
            mock_fewshot.assert_called_once()
            mock_canary.assert_called_once()

            # Verify result
            assert result.get("key", "")
            assert result.get("key", "")

            # Verify output was printed
            mock_print.assert_called()

    @patch.object(ProductionRunbook, "_run_health_gated_evaluation")
    def test_execute_production_deployment_health_failure(self, mock_health: MagicMock) -> None:
        """Test execute_production_deployment handles health check failure."""
        # Mock health check to fail
        mock_health.return_value = {"status": "failed", "error": "Health check failed"}

        with patch("builtins.print") as _mock_print:
            result: DeploymentResult = self.runbook.execute_production_deployment()

            # Verify health check was called
            mock_health.assert_called_once()

            # Verify result indicates failure
            assert result.get("key", "")
            assert "error" in result

    @patch.object(ProductionRunbook, "_run_health_gated_evaluation")
    @patch.object(ProductionRunbook, "_generate_run_manifest")
    def test_execute_production_deployment_manifest_failure(self, mock_manifest: MagicMock, mock_health: MagicMock) -> None:
        """Test execute_production_deployment handles manifest generation failure."""
        # Mock health check to succeed, manifest to fail
        mock_health.return_value = {"status": "success"}
        mock_manifest.return_value = {
            "status": "failed",
            "error": "Manifest generation failed",
        }

        with patch("builtins.print") as _mock_print:
            result: DeploymentResult = self.runbook.execute_production_deployment()

            # Verify phases were called
            mock_health.assert_called_once()
            mock_manifest.assert_called_once()

            # Verify result indicates failure
            assert result.get("key", "")
            assert "error" in result

    def test_run_health_gated_evaluation(self) -> None:
        """Test health-gated evaluation phase."""
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            # Mock subprocess success
            mock_proc = Mock()
            mock_proc.returncode = 0
            mock_proc.stdout = "Health check passed"
            mock_subprocess.return_value = mock_proc

            result: PhaseResult = self.runbook._run_health_gated_evaluation()  # type: ignore[reportPrivateUsage]

            assert result.get("key", "")
            assert "Health check passed" in result.get("key", "")
            mock_subprocess.assert_called_once()

    def test_run_health_gated_evaluation_failure(self) -> None:
        """Test health-gated evaluation phase with failure."""
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            # Mock subprocess failure
            mock_proc = Mock()
            mock_proc.returncode = 1
            mock_proc.stdout = "Health check failed"
            mock_proc.stderr = "Error details"
            mock_subprocess.return_value = mock_proc

            result: PhaseResult = self.runbook._run_health_gated_evaluation()  # type: ignore[reportPrivateUsage]

            assert result.get("key", "")
            assert "Health check failed" in result.get("key", "")
            assert "Error details" in result.get("key", "")

    def test_generate_run_manifest(self) -> None:
        """Test run manifest generation phase."""
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            # Mock subprocess success
            mock_proc = Mock()
            mock_proc.returncode = 0
            mock_proc.stdout = "Manifest generated"
            mock_subprocess.return_value = mock_proc

            result: PhaseResult = self.runbook._generate_run_manifest()  # type: ignore[reportPrivateUsage]

            assert result.get("key", "")
            assert "Manifest generated" in result.get("key", "")
            mock_subprocess.assert_called_once()

    def test_generate_run_manifest_failure(self) -> None:
        """Test run manifest generation phase with failure."""
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            # Mock subprocess failure
            mock_proc = Mock()
            mock_proc.returncode = 1
            mock_proc.stdout = "Manifest generation failed"
            mock_proc.stderr = "Error details"
            mock_subprocess.return_value = mock_proc

            result: PhaseResult = self.runbook._generate_run_manifest()  # type: ignore[reportPrivateUsage]

            assert result.get("key", "")
            assert "Manifest generation failed" in result.get("key", "")
            assert "Error details" in result.get("key", "")

    def test_setup_deterministic_environment(self) -> None:
        """Test deterministic environment setup phase."""
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            # Mock subprocess success
            mock_proc = Mock()
            mock_proc.returncode = 0
            mock_proc.stdout = "Environment setup complete"
            mock_subprocess.return_value = mock_proc

            result: PhaseResult = self.runbook._setup_deterministic_environment()  # type: ignore[reportPrivateUsage]

            assert result.get("key", "")
            assert "Environment setup complete" in result.get("key", "")
            mock_subprocess.assert_called_once()

    def test_setup_deterministic_environment_failure(self) -> None:
        """Test deterministic environment setup phase with failure."""
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            # Mock subprocess failure
            mock_proc = Mock()
            mock_proc.returncode = 1
            mock_proc.stdout = "Environment setup failed"
            mock_proc.stderr = "Error details"
            mock_subprocess.return_value = mock_proc

            result: PhaseResult = self.runbook._setup_deterministic_environment()  # type: ignore[reportPrivateUsage]

            assert result.get("key", "")
            assert "Environment setup failed" in result.get("key", "")
            assert "Error details" in result.get("key", "")

    def test_run_retrieval_only_evaluation(self) -> None:
        """Test retrieval-only evaluation phase."""
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            # Mock subprocess success
            mock_proc = Mock()
            mock_proc.returncode = 0
            mock_proc.stdout = "Retrieval evaluation complete"
            mock_subprocess.return_value = mock_proc

            result: PhaseResult = self.runbook._run_retrieval_only_evaluation()  # type: ignore[reportPrivateUsage]

            assert result.get("key", "")
            assert "Retrieval evaluation complete" in result.get("key", "")
            mock_subprocess.assert_called_once()

    def test_run_retrieval_only_evaluation_failure(self) -> None:
        """Test retrieval-only evaluation phase with failure."""
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            # Mock subprocess failure
            mock_proc = Mock()
            mock_proc.returncode = 1
            mock_proc.stdout = "Retrieval evaluation failed"
            mock_proc.stderr = "Error details"
            mock_subprocess.return_value = mock_proc

            result: PhaseResult = self.runbook._run_retrieval_only_evaluation()  # type: ignore[reportPrivateUsage]

            assert result.get("key", "")
            assert "Retrieval evaluation failed" in result.get("key", "")
            assert "Error details" in result.get("key", "")

    def test_run_deterministic_fewshot_evaluation(self) -> None:
        """Test deterministic few-shot evaluation phase."""
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            # Mock subprocess success
            mock_proc = Mock()
            mock_proc.returncode = 0
            mock_proc.stdout = "Few-shot evaluation complete"
            mock_subprocess.return_value = mock_proc

            result: PhaseResult = self.runbook._run_deterministic_fewshot_evaluation()  # type: ignore[reportPrivateUsage]

            assert result.get("key", "")
            assert "Few-shot evaluation complete" in result.get("key", "")
            mock_subprocess.assert_called_once()

    def test_run_deterministic_fewshot_evaluation_failure(self) -> None:
        """Test deterministic few-shot evaluation phase with failure."""
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            # Mock subprocess failure
            mock_proc = Mock()
            mock_proc.returncode = 1
            mock_proc.stdout = "Few-shot evaluation failed"
            mock_proc.stderr = "Error details"
            mock_subprocess.return_value = mock_proc

            result: PhaseResult = self.runbook._run_deterministic_fewshot_evaluation()  # type: ignore[reportPrivateUsage]

            assert result.get("key", "")
            assert "Few-shot evaluation failed" in result.get("key", "")
            assert "Error details" in result.get("key", "")

    def test_start_canary_monitoring(self) -> None:
        """Test canary monitoring phase."""
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            # Mock subprocess success
            mock_proc = Mock()
            mock_proc.returncode = 0
            mock_proc.stdout = "Canary monitoring started"
            mock_subprocess.return_value = mock_proc

            result: PhaseResult = self.runbook._start_canary_monitoring()  # type: ignore[reportPrivateUsage]

            assert result.get("key", "")
            assert "Canary monitoring started" in result.get("key", "")
            mock_subprocess.assert_called_once()

    def test_start_canary_monitoring_failure(self) -> None:
        """Test canary monitoring phase with failure."""
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            # Mock subprocess failure
            mock_proc = Mock()
            mock_proc.returncode = 1
            mock_proc.stdout = "Canary monitoring failed"
            mock_proc.stderr = "Error details"
            mock_subprocess.return_value = mock_proc

            result: PhaseResult = self.runbook._start_canary_monitoring()  # type: ignore[reportPrivateUsage]

            assert result.get("key", "")
            assert "Canary monitoring failed" in result.get("key", "")
            assert "Error details" in result.get("key", "")

    def test_phase_execution_order(self) -> None:
        """Test that phases are executed in correct order."""
        with patch.object(self.runbook, "_run_health_gated_evaluation") as mock_health:
            with patch.object(self.runbook, "_generate_run_manifest") as mock_manifest:
                with patch.object(self.runbook, "_setup_deterministic_environment") as mock_setup:
                    with patch.object(self.runbook, "_run_retrieval_only_evaluation") as mock_retrieval:
                        with patch.object(self.runbook, "_run_deterministic_fewshot_evaluation") as mock_fewshot:
                            with patch.object(self.runbook, "_start_canary_monitoring") as mock_canary:
                                # Mock all phases to succeed
                                mock_health.return_value = {"status": "success"}
                                mock_manifest.return_value = {"status": "success"}
                                mock_setup.return_value = {"status": "success"}
                                mock_retrieval.return_value = {"status": "success"}
                                mock_fewshot.return_value = {"status": "success"}
                                mock_canary.return_value = {"status": "success"}

                                with patch("builtins.print"):
                                    _ = self.runbook.execute_production_deployment()

                                    # Verify execution order
                                    assert mock_health.called
                                    assert mock_manifest.called
                                    assert mock_setup.called
                                    assert mock_retrieval.called
                                    assert mock_fewshot.called
                                    assert mock_canary.called

    def test_phase_failure_stops_execution(self) -> None:
        """Test that phase failure stops execution of subsequent phases."""
        with patch.object(self.runbook, "_run_health_gated_evaluation") as mock_health:
            with patch.object(self.runbook, "_generate_run_manifest") as mock_manifest:
                with patch.object(self.runbook, "_setup_deterministic_environment") as mock_setup:
                    with patch.object(self.runbook, "_run_retrieval_only_evaluation") as mock_retrieval:
                        with patch.object(self.runbook, "_run_deterministic_fewshot_evaluation") as mock_fewshot:
                            with patch.object(self.runbook, "_start_canary_monitoring") as mock_canary:
                                # Mock health check to fail
                                mock_health.return_value = {
                                    "status": "failed",
                                    "error": "Health check failed",
                                }

                                with patch("builtins.print"):
                                    result: DeploymentResult = self.runbook.execute_production_deployment()

                                    # Verify only health check was called
                                    assert mock_health.called
                                    assert not mock_manifest.called
                                    assert not mock_setup.called
                                    assert not mock_retrieval.called
                                    assert not mock_fewshot.called
                                    assert not mock_canary.called

                                    # Verify result indicates failure
                                    assert result.get("key", "")


class TestProductionRunbookCLI:
    """Test cases for CLI interface."""

    @patch("scripts.evaluation.core.production_runbook.ProductionRunbook")
    def test_main_success(self, mock_runbook_class: MagicMock) -> None:
        """Test main function runs successfully."""
        mock_runbook = Mock()
        mock_runbook.execute_production_deployment.return_value = {
            "status": "completed",
            "run_id": "test_run",
        }
        mock_runbook_class.return_value = mock_runbook

        with patch("sys.argv", ["production_runbook.py"]):
            with patch("scripts.evaluation.core.production_runbook.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Verify runbook was created and executed
                    mock_runbook_class.assert_called_once()
                    cast(MagicMock, mock_runbook.execute_production_deployment).assert_called_once()

                    # Verify output was printed
                    mock_print.assert_called()

                    # Should complete successfully
                    mock_exit.assert_called_once_with(0)

    @patch("scripts.evaluation.core.production_runbook.ProductionRunbook")
    def test_main_deployment_failure(self, mock_runbook_class: MagicMock) -> None:
        """Test main function handles deployment failure."""
        mock_runbook = Mock()
        mock_runbook.execute_production_deployment.return_value = {
            "status": "failed",
            "error": "Deployment failed",
        }
        mock_runbook_class.return_value = mock_runbook

        with patch("sys.argv", ["production_runbook.py"]):
            with patch("scripts.evaluation.core.production_runbook.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Verify runbook was created and executed
                    mock_runbook_class.assert_called_once()
                    cast(MagicMock, mock_runbook.execute_production_deployment).assert_called_once()

                    # Verify output was printed
                    mock_print.assert_called()

                    # Should exit with error
                    mock_exit.assert_called_once_with(1)

    @patch("sys.argv", ["production_runbook.py", "--help"])
    def test_main_help(self) -> None:
        """Test main function shows help."""
        with patch("scripts.evaluation.core.production_runbook.argparse.ArgumentParser.print_help"):
            with patch("scripts.evaluation.core.production_runbook.sys.exit") as mock_exit:
                main()

                mock_exit.assert_called_once_with(0)

    @patch("scripts.evaluation.core.production_runbook.ProductionRunbook")
    def test_main_with_arguments(self, mock_runbook_class: MagicMock) -> None:
        """Test main function with command line arguments."""
        mock_runbook = Mock()
        mock_runbook.execute_production_deployment.return_value = {
            "status": "completed",
            "run_id": "test_run",
        }
        mock_runbook_class.return_value = mock_runbook

        with patch("sys.argv", ["production_runbook.py", "--verbose", "--dry-run"]):
            with patch("scripts.evaluation.core.production_runbook.sys.exit") as mock_exit:
                with patch("builtins.print") as mock_print:
                    main()

                    # Verify runbook was created and executed
                    mock_runbook_class.assert_called_once()
                    cast(MagicMock, mock_runbook.execute_production_deployment).assert_called_once()

                    # Should complete successfully
                    mock_exit.assert_called_once_with(0)


class TestProductionRunbookIntegration:
    """Integration tests for production_runbook.py."""

    def test_full_deployment_workflow(self) -> None:
        """Test full deployment workflow integration."""
        runbook = ProductionRunbook()

        # Mock all subprocess calls to succeed
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            # Mock subprocess success for all phases
            mock_proc = Mock()
            mock_proc.returncode = 0
            mock_proc.stdout = "Phase completed successfully"
            mock_proc.stderr = ""
            mock_subprocess.return_value = mock_proc

            with patch("builtins.print") as mock_print:
                result: DeploymentResult = runbook.execute_production_deployment()

                # Verify result
                assert result.get("key", "")
                assert result.get("key", "")

                # Verify all phases were executed
                assert mock_subprocess.call_count == 6  # 6 phases

                # Verify output was printed
                mock_print.assert_called()

    def test_deployment_with_mixed_results(self) -> None:
        """Test deployment with mixed success/failure results."""
        runbook = ProductionRunbook()

        # Mock subprocess calls with mixed results
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:

            def mock_subprocess_side_effect(*args: object, **kwargs: object):
                mock_proc = Mock()
                if "health" in str(result.get("key", "")
                    mock_proc.returncode = 0
                    mock_proc.stdout = "Health check passed"
                elif "manifest" in str(result.get("key", "")
                    mock_proc.returncode = 1
                    mock_proc.stdout = "Manifest generation failed"
                    mock_proc.stderr = "Error details"
                else:
                    mock_proc.returncode = 0
                    mock_proc.stdout = "Phase completed"
                return mock_proc

            mock_subprocess.side_effect = mock_subprocess_side_effect

            with patch("builtins.print") as _mock_print:
                result: DeploymentResult = runbook.execute_production_deployment()

                # Verify result indicates failure
                assert result.get("key", "")
                assert "error" in result

                # Verify only first two phases were executed
                assert mock_subprocess.call_count == 2

    def test_deployment_workflow_robustness(self) -> None:
        """Test deployment workflow robustness with various scenarios."""
        runbook = ProductionRunbook()

        # Test case 1: All phases succeed
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            mock_proc = Mock()
            mock_proc.returncode = 0
            mock_proc.stdout = "Success"
            mock_subprocess.return_value = mock_proc

            with patch("builtins.print"):
                result: DeploymentResult = runbook.execute_production_deployment()
                assert result.get("key", "")

        # Test case 2: First phase fails
        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            mock_proc = Mock()
            mock_proc.returncode = 1
            mock_proc.stdout = "Health check failed"
            mock_proc.stderr = "Error"
            mock_subprocess.return_value = mock_proc

            with patch("builtins.print"):
                result: dict[str, Any] = runbook.execute_production_deployment()
                assert result.get("key", "")

    def test_runbook_initialization_consistency(self) -> None:
        """Test runbook initialization consistency across multiple instances."""
        runbook1 = ProductionRunbook()
        runbook2 = ProductionRunbook()

        # Verify each instance has unique run_id
        assert runbook1.run_id != runbook2.run_id
        assert runbook1.timestamp != runbook2.timestamp

        # Verify format consistency
        assert runbook1.run_id.startswith("prod_run_")
        assert runbook2.run_id.startswith("prod_run_")
        assert len(runbook1.timestamp) == 15
        assert len(runbook2.timestamp) == 15

    def test_phase_output_formatting(self) -> None:
        """Test phase output formatting and display."""
        runbook = ProductionRunbook()

        with patch("scripts.evaluation.core.production_runbook.subprocess.run") as mock_subprocess:
            mock_proc = Mock()
            mock_proc.returncode = 0
            mock_proc.stdout = "Test output"
            mock_subprocess.return_value = mock_proc

            with patch("builtins.print") as mock_print:
                _ = runbook._run_health_gated_evaluation()  # type: ignore[reportPrivateUsage]

                # Verify output was printed with proper formatting
                mock_print.assert_called()
                print_calls = [result.get("key", "")
                output_text = " ".join(print_calls)
                assert "Phase 1" in output_text
                assert "Health-Gated Evaluation" in output_text


if __name__ == "__main__":
    _ = pytest.main([__file__])
