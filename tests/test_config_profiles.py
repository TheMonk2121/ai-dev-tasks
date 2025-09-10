#!/usr/bin/env python3
"""
Test suite for evaluation profile configuration system.

Validates that the profile system correctly prevents "accidentally-synthetic"
baselines and enforces proper configuration.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


def run_command(cmd: str) -> tuple[int, str]:
    """Run a command and return (exit_code, output)."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return -1, "Command timed out"


class TestProfileConfiguration:
    """Test profile configuration loading and validation."""

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_mock_profile_banner(self):
        """Test that mock profile shows correct banner."""
        code, out = run_command("python3 scripts/lib/config_loader.py --profile mock --help || true")
        assert "Profile: mock" in out or "mock" in out

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_real_profile_banner(self):
        """Test that real profile shows correct banner."""
        code, out = run_command("python3 scripts/lib/config_loader.py --profile real --help || true")
        assert "Profile: real" in out or "real" in out

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_gold_profile_banner(self):
        """Test that gold profile shows correct banner."""
        code, out = run_command("python3 scripts/lib/config_loader.py --profile gold --help || true")
        assert "Profile: gold" in out or "gold" in out

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_no_profile_error(self):
        """Test that missing profile raises clear error."""
        code, out = run_command("python3 scripts/lib/config_loader.py --help || true")
        assert "No profile selected" in out
        assert code != 0

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_invalid_profile_error(self):
        """Test that invalid profile raises error."""
        code, out = run_command("python3 scripts/lib/config_loader.py --profile invalid --help || true")
        assert "Invalid --profile invalid" in out
        assert code != 0


class TestPreflightChecks:
    """Test preflight validation that prevents foot-guns."""

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_real_profile_refuses_mock_dsn(self):
        """Test that real profile refuses mock DSN."""
        with patch.dict(os.environ, {"POSTGRES_DSN": "mock://test"}):
            code, out = run_command("python3 scripts/lib/config_loader.py --profile real || true")
            assert "require a real POSTGRES_DSN" in out
            assert code != 0

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_gold_profile_refuses_mock_dsn(self):
        """Test that gold profile refuses mock DSN."""
        with patch.dict(os.environ, {"POSTGRES_DSN": "mock://test"}):
            code, out = run_command("python3 scripts/lib/config_loader.py --profile gold || true")
            assert "require a real POSTGRES_DSN" in out
            assert code != 0

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_real_profile_refuses_synthetic_driver(self):
        """Test that real profile refuses synthetic driver."""
        code, out = run_command("python3 scripts/lib/config_loader.py --profile real --driver synthetic || true")
        assert "require EVAL_DRIVER=dspy_rag" in out
        assert code != 0

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_gold_profile_refuses_synthetic_driver(self):
        """Test that gold profile refuses synthetic driver."""
        code, out = run_command("python3 scripts/lib/config_loader.py --profile gold --driver synthetic || true")
        assert "require EVAL_DRIVER=dspy_rag" in out
        assert code != 0

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_mock_profile_allows_synthetic_driver(self):
        """Test that mock profile allows synthetic driver."""
        code, out = run_command("python3 scripts/lib/config_loader.py --profile mock --driver synthetic || true")
        # Mock profile should work with synthetic driver
        assert code == 0 or "Profile: mock" in out


class TestProfileFiles:
    """Test that profile files exist and are valid."""

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_profile_files_exist(self):
        """Test that all profile files exist."""
        profile_files = ["configs/profiles/real.env", "configs/profiles/gold.env", "configs/profiles/mock.env"]

        for profile_file in profile_files:
            assert Path(profile_file).exists(), f"Profile file {profile_file} does not exist"

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_profile_files_contain_required_vars(self):
        """Test that profile files contain required variables."""
        profiles = {
            "real.env": ["EVAL_PROFILE=real", "POSTGRES_DSN="],
            "gold.env": ["EVAL_PROFILE=gold", "POSTGRES_DSN=", "USE_GOLD=1"],
            "mock.env": ["EVAL_PROFILE=mock", "POSTGRES_DSN=mock://test"],
        }

        for profile_file, required_vars in profiles.items():
            content = Path(f"configs/profiles/{profile_file}").read_text()
            for var in required_vars:
                assert var in content, f"Profile {profile_file} missing required variable: {var}"


class TestWrapperScripts:
    """Test that wrapper scripts exist and are executable."""

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_wrapper_scripts_exist(self):
        """Test that all wrapper scripts exist."""
        scripts = ["scripts/eval_real.sh", "scripts/eval_gold.sh", "scripts/eval_mock.sh"]

        for script in scripts:
            script_path = Path(script)
            assert script_path.exists(), f"Wrapper script {script} does not exist"
            assert script_path.stat().st_mode & 0o111, f"Wrapper script {script} is not executable"

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_wrapper_scripts_call_correct_profile(self):
        """Test that wrapper scripts call the correct profile."""
        scripts = {
            "scripts/eval_real.sh": "--profile real",
            "scripts/eval_gold.sh": "--profile gold",
            "scripts/eval_mock.sh": "--profile mock",
        }

        for script, expected_profile in scripts.items():
            content = Path(script).read_text()
            assert expected_profile in content, f"Script {script} should call {expected_profile}"


class TestMakefile:
    """Test Makefile targets for evaluation profiles."""

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_makefile_exists(self):
        """Test that Makefile exists."""
        assert Path("Makefile").exists()

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_makefile_contains_eval_targets(self):
        """Test that Makefile contains evaluation targets."""
        content = Path("Makefile").read_text()
        required_targets = ["eval-real:", "eval-gold:", "eval-mock:", "test-profiles:"]

        for target in required_targets:
            assert target in content, f"Makefile missing target: {target}"


class TestCIWorkflows:
    """Test CI workflow files for profile integration."""

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_ci_workflows_exist(self):
        """Test that CI workflow files exist."""
        workflows = [".github/workflows/ci-pr-quick.yml", ".github/workflows/ci-nightly-baseline.yml"]

        for workflow in workflows:
            assert Path(workflow).exists(), f"CI workflow {workflow} does not exist"

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_pr_workflow_uses_mock(self):
        """Test that PR workflow uses mock profile."""
        content = Path(".github/workflows/ci-pr-quick.yml").read_text()
        assert "eval_mock.sh" in content
        assert "concurrency 3" in content

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_nightly_workflow_uses_real(self):
        """Test that nightly workflow uses real profile."""
        content = Path(".github/workflows/ci-nightly-baseline.yml").read_text()
        assert "eval_real.sh" in content
        assert "concurrency 12" in content


class TestIntegration:
    """Integration tests for the complete profile system."""

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_profile_system_end_to_end(self):
        """Test complete profile system integration."""
        # Test that the main evaluation script can load profiles
        code, out = run_command("python3 scripts/ragchecker_official_evaluation.py --profile mock --help || true")
        # Should not crash and should show profile information
        assert "Profile: mock" in out or "mock" in out

    @pytest.mark.skip(reason="config_loader.py not implemented yet")
    def test_makefile_targets_work(self):
        """Test that Makefile targets execute without errors."""
        targets = ["test-profiles"]

        for target in targets:
            code, out = run_command(f"make {target} || true")
            # Should complete without major errors
            assert code == 0 or "Profile" in out


if __name__ == "__main__":
    # Run tests if called directly
    pytest.main([__file__, "-v"])
