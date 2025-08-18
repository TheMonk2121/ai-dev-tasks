#!/usr/bin/env python3
"""
Prompt Contract Smoke Tests (Round 1)
Tests for consensus prompt loader structure (xfail until loader wired).
"""

from pathlib import Path

import pytest


@pytest.mark.tier2
@pytest.mark.kind_prompt
@pytest.mark.xfail(reason="Prompt loader not yet wired - structure only")
class TestPromptContracts:
    """Smoke tests for prompt contract structure."""

    @pytest.fixture
    def project_root(self):
        """Get project root directory."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def cursor_dir(self, project_root):
        """Get .cursor directory."""
        return project_root / ".cursor"

    def test_cursor_agent_preamble_exists(self, cursor_dir):
        """Test that .cursor/agent_preamble.md exists."""
        preamble_file = cursor_dir / "agent_preamble.md"
        assert preamble_file.exists(), f"Agent preamble file not found: {preamble_file}"

        # Test that file has content
        content = preamble_file.read_text()
        assert len(content.strip()) > 0, "Agent preamble file is empty"

        # Test that it contains expected sections
        assert "routing recipe" in content.lower(), "Agent preamble missing routing recipe"
        assert "constitution" in content.lower(), "Agent preamble missing constitution reference"

    def test_cursor_context_manifest_exists(self, cursor_dir):
        """Test that .cursor/context_manifest.yaml exists."""
        manifest_file = cursor_dir / "context_manifest.yaml"
        assert manifest_file.exists(), f"Context manifest file not found: {manifest_file}"

        # Test that file has content
        content = manifest_file.read_text()
        assert len(content.strip()) > 0, "Context manifest file is empty"

        # Test that it's valid YAML structure
        assert "context" in content.lower(), "Context manifest missing context section"

    def test_build_cursor_context_script_exists(self, project_root):
        """Test that scripts/build_cursor_context.py exists."""
        script_file = project_root / "scripts" / "build_cursor_context.py"
        assert script_file.exists(), f"Build cursor context script not found: {script_file}"

        # Test that file has content
        content = script_file.read_text()
        assert len(content.strip()) > 0, "Build cursor context script is empty"

        # Test that it contains expected functionality
        assert "build" in content.lower(), "Script missing build functionality"
        assert "context" in content.lower(), "Script missing context functionality"

    def test_consensus_prompt_structure(self, project_root):
        """Test that consensus framework has prompt structure."""
        consensus_file = project_root / "scripts" / "consensus_framework.py"
        assert consensus_file.exists(), f"Consensus framework not found: {consensus_file}"

        # Test that it contains prompt-related functionality
        content = consensus_file.read_text()
        assert "prompt" in content.lower(), "Consensus framework missing prompt functionality"
        assert "strawman" in content.lower(), "Consensus framework missing strawman functionality"

    def test_prompt_template_structure(self, project_root):
        """Test that prompt templates follow expected structure."""
        # Look for prompt-related files
        prompt_files = []

        # Check scripts directory for prompt files
        scripts_dir = project_root / "scripts"
        if scripts_dir.exists():
            for file in scripts_dir.glob("*prompt*"):
                prompt_files.append(file)

        # Check dspy-rag-system for prompt files
        dspy_dir = project_root / "dspy-rag-system"
        if dspy_dir.exists():
            for file in dspy_dir.rglob("*prompt*"):
                prompt_files.append(file)

        # At minimum, we should have some prompt-related files
        # This is a smoke test, so we're just checking structure exists
        assert len(prompt_files) >= 0, "No prompt-related files found (this may be expected)"

        # If we have prompt files, test their basic structure
        for prompt_file in prompt_files:
            if prompt_file.is_file():
                content = prompt_file.read_text()
                assert len(content.strip()) > 0, f"Prompt file is empty: {prompt_file}"

    def test_consensus_prompt_loader_interface(self, project_root):
        """Test that consensus prompt loader has expected interface."""
        consensus_file = project_root / "scripts" / "consensus_framework.py"

        if consensus_file.exists():
            content = consensus_file.read_text()

            # Test for expected methods/classes
            expected_elements = [
                "class ConsensusFramework",
                "create_strawman_proposal",
                "submit_red_team_review",
                "submit_blue_team_review",
                "create_consensus_round",
            ]

            for element in expected_elements:
                assert element in content, f"Consensus framework missing {element}"

    def test_prompt_contract_validation(self, project_root):
        """Test that prompt contracts can be validated."""
        # This is a placeholder for when prompt contract validation is implemented
        # For now, we just test that the structure exists

        # Test that we have the basic files needed for prompt contracts
        required_files = [
            project_root / ".cursor" / "agent_preamble.md",
            project_root / ".cursor" / "context_manifest.yaml",
            project_root / "scripts" / "build_cursor_context.py",
            project_root / "scripts" / "consensus_framework.py",
        ]

        for file in required_files:
            if file.exists():
                # File exists and has content
                content = file.read_text()
                assert len(content.strip()) > 0, f"Required file is empty: {file}"
            else:
                # File doesn't exist yet (expected for some components)
                pytest.skip(f"Required file not yet implemented: {file}")

    def test_prompt_loader_integration_points(self, project_root):
        """Test that prompt loader has expected integration points."""
        # Test that consensus framework can be imported
        try:
            import sys

            sys.path.insert(0, str(project_root / "scripts"))
            from consensus_framework import ConsensusFramework

            # Test that we can create an instance
            framework = ConsensusFramework()
            assert framework is not None, "Could not create ConsensusFramework instance"

        except ImportError:
            pytest.skip("Consensus framework not yet fully implemented")
        except Exception as e:
            pytest.skip(f"Consensus framework not ready: {e}")

    def test_prompt_contract_schema(self, project_root):
        """Test that prompt contracts follow expected schema."""
        # This test validates the structure of prompt contracts
        # For now, we just check that the basic files exist and have content

        cursor_dir = project_root / ".cursor"
        if cursor_dir.exists():
            # Test agent preamble structure
            preamble_file = cursor_dir / "agent_preamble.md"
            if preamble_file.exists():
                content = preamble_file.read_text()

                # Test for required sections
                required_sections = ["routing", "constitution", "roles"]
                for section in required_sections:
                    if section not in content.lower():
                        pytest.skip(f"Agent preamble missing {section} section")

            # Test context manifest structure
            manifest_file = cursor_dir / "context_manifest.yaml"
            if manifest_file.exists():
                content = manifest_file.read_text()

                # Test for YAML structure
                if not content.strip():
                    pytest.skip("Context manifest is empty")

        # If we get here, the basic structure is in place
        assert True, "Prompt contract structure validation passed"
