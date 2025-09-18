"""
Property tests for EvalSettings parsing behavior.
"""

#!/usr/bin/env python3

from __future__ import annotations

import os

import hypothesis
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.settings import EvalSettings


@pytest.mark.prop
@given(
    profile=st.from_regex(r"[a-z_]{1,20}", fullmatch=True),
    driver=st.sampled_from(["dspy_rag", "synthetic", "ragchecker"]),
    concurrency=st.integers(min_value=1, max_value=64),
    use_real_rag=st.integers(min_value=0, max_value=1),
)
@settings(max_examples=10, deadline=100)
def test_eval_settings_core_fields(profile: str, driver: str, concurrency: int, use_real_rag: int):
    """Test that core EvalSettings fields parse correctly."""
    # Set environment variables
    os.environ
    os.environ
    os.environ
    os.environ

    try:
        settings = EvalSettings()

        # Check that fields are correctly parsed
        assert settings.EVAL_PROFILE == profile
        assert settings.EVAL_DRIVER == driver
        assert settings.EVAL_CONCURRENCY == concurrency
        assert settings.RAGCHECKER_USE_REAL_RAG == use_real_rag

    finally:
        # Clean up environment variables
        for key in [
            "EVAL_PROFILE",
            "EVAL_DRIVER",
            "EVAL_CONCURRENCY",
            "RAGCHECKER_USE_REAL_RAG",
        ]:
            os.environ.pop(key, None)


@pytest.mark.prop
@given(
    gold_path=st.text(min_size=2, max_size=100).map(lambda x: f"path/{x}"),
    manifest_path=st.text(min_size=2, max_size=100).map(lambda x: f"path/{x}"),
    results_dir=st.text(min_size=2, max_size=100).map(lambda x: f"path/{x}"),
)
@settings(max_examples=10, deadline=100)
def test_eval_settings_file_paths(gold_path: str, manifest_path: str, results_dir: str):
    """Test that file path fields work correctly."""
    # Set environment variables
    os.environ
    os.environ
    os.environ

    try:
        settings = EvalSettings()

        # Check that paths are correctly set
        assert settings.GOLD_CASES_PATH == gold_path
        assert settings.MANIFEST_PATH == manifest_path
        assert settings.RESULTS_OUTPUT_DIR == results_dir

        # Test helper methods
        assert settings.get_gold_cases_path().as_posix() == gold_path
        assert settings.get_manifest_path().as_posix() == manifest_path
        assert settings.get_results_dir().as_posix() == results_dir

    finally:
        # Clean up environment variables
        for key in ["GOLD_CASES_PATH", "MANIFEST_PATH", "RESULTS_OUTPUT_DIR"]:
            os.environ.pop(key, None)


@pytest.mark.prop
@given(
    validation_strict=st.sampled_from(["1", "0", "true", "false", "TRUE", "False"]),
    allow_missing_files=st.sampled_from(["1", "0", "true", "false", "TRUE", "False"]),
    unknown_tag_warning=st.sampled_from(["1", "0", "true", "false", "TRUE", "False"]),
    check_file_existence=st.sampled_from(["1", "0", "true", "false", "TRUE", "False"]),
)
@settings(max_examples=10, deadline=100)
def test_eval_settings_boolean_fields(
    validation_strict: str,
    allow_missing_files: str,
    unknown_tag_warning: str,
    check_file_existence: str,
):
    """Test that boolean fields parse correctly from various string encodings."""
    # Set environment variables
    os.environ
    os.environ
    os.environ
    os.environ

    try:
        settings = EvalSettings()

        # Check that boolean fields are correctly parsed
        assert isinstance(settings.VALIDATION_STRICT, bool)
        assert isinstance(settings.ALLOW_MISSING_FILES, bool)
        assert isinstance(settings.UNKNOWN_TAG_WARNING, bool)
        assert isinstance(settings.CHECK_FILE_EXISTENCE, bool)

        # Verify that truthy strings become True and falsy strings become False
        expected_validation_strict = validation_strict.lower() in ["1", "true", "yes"]
        expected_allow_missing_files = allow_missing_files.lower() in [
            "1",
            "true",
            "yes",
        ]
        expected_unknown_tag_warning = unknown_tag_warning.lower() in [
            "1",
            "true",
            "yes",
        ]
        expected_check_file_existence = check_file_existence.lower() in [
            "1",
            "true",
            "yes",
        ]

        assert settings.VALIDATION_STRICT == expected_validation_strict
        assert settings.ALLOW_MISSING_FILES == expected_allow_missing_files
        assert settings.UNKNOWN_TAG_WARNING == expected_unknown_tag_warning
        assert settings.CHECK_FILE_EXISTENCE == expected_check_file_existence

    finally:
        # Clean up environment variables
        for key in [
            "VALIDATION_STRICT",
            "ALLOW_MISSING_FILES",
            "UNKNOWN_TAG_WARNING",
            "CHECK_FILE_EXISTENCE",
        ]:
            os.environ.pop(key, None)


@pytest.mark.prop
@given(
    max_cases=st.integers(min_value=1, max_value=1000),
    sample_size=st.integers(min_value=1, max_value=500),
    timeout=st.integers(min_value=30, max_value=3600),
)
@settings(max_examples=10, deadline=100)
def test_eval_settings_integer_fields(max_cases: int, sample_size: int, timeout: int):
    """Test that integer fields work correctly."""
    # Set environment variables
    os.environ
    os.environ
    os.environ

    try:
        settings = EvalSettings()

        # Check that integer fields are correctly parsed
        assert isinstance(settings.MAX_CASES_PER_EVAL, int)
        assert isinstance(settings.DEFAULT_SAMPLE_SIZE, int)
        assert isinstance(settings.TIMEOUT_SECONDS, int)

        # Check that values match input
        assert settings.MAX_CASES_PER_EVAL == max_cases
        assert settings.DEFAULT_SAMPLE_SIZE == sample_size
        assert settings.TIMEOUT_SECONDS == timeout

    finally:
        # Clean up environment variables
        for key in ["MAX_CASES_PER_EVAL", "DEFAULT_SAMPLE_SIZE", "TIMEOUT_SECONDS"]:
            os.environ.pop(key, None)


@pytest.mark.prop
@given(
    default_model=st.text(min_size=1, max_size=100).filter(lambda x: "\x00" not in x),
    fallback_model=st.text(min_size=1, max_size=100).filter(lambda x: "\x00" not in x),
    dspy_model=st.text(min_size=1, max_size=100).filter(lambda x: "\x00" not in x),
)
@settings(max_examples=10, deadline=100)
def test_eval_settings_model_fields(default_model: str, fallback_model: str, dspy_model: str):
    """Test that model fields work correctly."""
    # Set environment variables
    os.environ
    os.environ
    os.environ

    try:
        settings = EvalSettings()

        # Check that model fields are correctly set
        assert settings.DEFAULT_MODEL == default_model
        assert settings.FALLBACK_MODEL == fallback_model
        assert settings.DSPY_MODEL == dspy_model

    finally:
        # Clean up environment variables
        for key in ["DEFAULT_MODEL", "FALLBACK_MODEL", "DSPY_MODEL"]:
            os.environ.pop(key, None)


@pytest.mark.prop
def test_eval_settings_defaults():
    """Test that EvalSettings has sensible defaults."""
    # Clear environment to test defaults
    env_keys = [
        "EVAL_PROFILE",
        "EVAL_DRIVER",
        "EVAL_CONCURRENCY",
        "RAGCHECKER_USE_REAL_RAG",
        "GOLD_CASES_PATH",
        "MANIFEST_PATH",
        "RESULTS_OUTPUT_DIR",
        "VALIDATION_STRICT",
        "ALLOW_MISSING_FILES",
        "UNKNOWN_TAG_WARNING",
        "CHECK_FILE_EXISTENCE",
        "MAX_CASES_PER_EVAL",
        "DEFAULT_SAMPLE_SIZE",
        "TIMEOUT_SECONDS",
        "DEFAULT_MODEL",
        "FALLBACK_MODEL",
        "DSPY_MODEL",
    ]

    # Clear environment
    for key in env_keys:
        os.environ.pop(key, None)

    try:
        settings = EvalSettings()

        # Check that defaults are set
        assert settings.EVAL_PROFILE == "default"
        assert settings.EVAL_DRIVER == "local"
        assert settings.EVAL_CONCURRENCY == 8
        assert settings.RAGCHECKER_USE_REAL_RAG == 1

        assert settings.GOLD_CASES_PATH == "evals/datasets/dev_gold.jsonl"
        assert settings.MANIFEST_PATH == "evals/metrics/manifests/manifest.json"
        assert settings.RESULTS_OUTPUT_DIR == "evals/metrics/baseline_evaluations"

        assert settings.VALIDATION_STRICT is True
        assert settings.ALLOW_MISSING_FILES is False
        assert settings.UNKNOWN_TAG_WARNING is True
        assert settings.CHECK_FILE_EXISTENCE is True

        assert settings.MAX_CASES_PER_EVAL == 100
        assert settings.DEFAULT_SAMPLE_SIZE == 50
        assert settings.TIMEOUT_SECONDS == 300

        assert "anthropic" in settings.DEFAULT_MODEL
        assert "anthropic" in settings.FALLBACK_MODEL
        assert "openai" in settings.DSPY_MODEL

    finally:
        # Clean up environment
        for key in env_keys:
            os.environ.pop(key, None)
