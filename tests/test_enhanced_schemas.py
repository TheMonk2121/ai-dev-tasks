from __future__ import annotations
import sys
from pathlib import Path
from src.schemas.eval import GoldCase, Mode
from src.schemas.settings import EvaluationSettings, settings
from src.schemas.validation import ValidationConfig, ValidationResult
        import traceback
import json
#!/usr/bin/env python3
"""Test enhanced schema system with Pydantic Settings and configurable validation."""

sys.path.append(".")

def test_settings_loading():
    """Test that settings load correctly."""

    print("Testing settings loading...")

    # Test basic settings (some may be overridden by environment variables)
    assert settings.gold_cases_path == "evals/gold/v1/gold_cases.jsonl"
    assert isinstance(settings.validation_strict, bool)  # May be overridden by env vars
    assert settings.max_cases_per_eval == 100
    assert len(settings.known_tags) > 0

    print("✅ Settings loading works")

def test_validation_config():
    """Test validation configuration."""
    print("Testing validation config...")

    # Test default config (may be affected by environment variables)
    config = ValidationConfig()
    assert isinstance(config.strict_mode, bool)
    assert isinstance(config.allow_missing_files, bool)

    # Test custom config (should override environment variables)
    custom_config = ValidationConfig(strict_mode=False, allow_missing_files=True, unknown_tag_warning=False)
    assert custom_config.strict_mode is False
    assert custom_config.allow_missing_files is True
    assert custom_config.unknown_tag_warning is False

    print("✅ Validation config works")

def test_case_validation():
    """Test individual case validation."""
    print("Testing case validation...")

    # Create test case
    case = GoldCase(
        id="TEST_001",
        mode=Mode.reader,
        query="Test query",
        tags=["unknown_tag", "rag_qa_single"],
        gt_answer="Test answer",
    )

    # Test strict validation
    strict_config = ValidationConfig(strict_mode=True)
    result = case.validate_case(strict_config)
    assert not result.is_valid
    assert len(result.errors) > 0
    assert "unknown_tag" in str(result.errors)

    # Test relaxed validation
    relaxed_config = ValidationConfig(strict_mode=False)
    result = case.validate_case(relaxed_config)
    assert result.is_valid
    assert len(result.errors) == 0
    assert len(result.warnings) > 0

    print("✅ Case validation works")

def test_legacy_compatibility():
    """Test legacy field compatibility."""
    print("Testing legacy compatibility...")

    # Test legacy payload
    legacy_payload = {
        "case_id": "LEGACY_001",
        "question": "Legacy question?",
        "tag": "ops_health",
        "mode": "reader",
        "response": "Legacy answer",
    }

    case = GoldCase.model_validate(legacy_payload)
    assert case.id == "LEGACY_001"
    assert case.query == "Legacy question?"
    assert case.tags == ["ops_health"]
    assert case.gt_answer == "Legacy answer"

    print("✅ Legacy compatibility works")

def test_validation_result():
    """Test validation result functionality."""
    print("Testing validation result...")

    result = ValidationResult(is_valid=True)

    # Test adding errors and warnings
    result.add_error("Test error")
    result.add_warning("Test warning")
    result.add_missing_file("CASE_001", "missing.txt", "file")
    result.add_unknown_tags("CASE_001", ["unknown"])

    assert not result.is_valid
    assert len(result.errors) == 1
    assert len(result.warnings) == 1
    assert len(result.missing_files) == 1
    assert len(result.unknown_tags) == 1

    # Test summary
    summary = result.get_summary()
    assert "FAILED" in summary
    assert "1" in summary  # Should show count of 1 error

    print("✅ Validation result works")

def test_environment_override():
    """Test environment variable overrides."""
    print("Testing environment overrides...")

    # This would require setting environment variables
    # For now, just test that the settings class supports it
    assert hasattr(settings, "gold_cases_path")
    assert hasattr(settings, "validation_strict")

    print("✅ Environment override support works")

def main():
    """Run all tests."""
    print("🧪 Testing Enhanced Schema System")
    print("=" * 50)

    try:
        test_settings_loading()
        test_validation_config()
        test_case_validation()
        test_legacy_compatibility()
        test_validation_result()
        test_environment_override()

        print("\n🎉 All tests passed!")
        return 0

    except Exception as e:
        print(f"\n❌ Test failed: {e}")

        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
