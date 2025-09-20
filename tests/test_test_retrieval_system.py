"""Tests for the retrieval system utility helpers."""

from __future__ import annotations

from typing import Any

import pytest

from scripts.evaluation.test_retrieval_system import (
    create_mock_retrieval_function,
    run_failure_mode_tests,
    test_concurrent_queries,
    test_high_volume,
    test_large_context,
)


def test_mock_retrieval_handles_edge_cases() -> None:
    fn = create_mock_retrieval_function()
    assert fn("hello")
    empty = fn("")
    assert empty["answer"] == "Not in context."
    long = fn("x" * 600)
    assert long["answer"].endswith("...")


def test_high_volume_counts_requests() -> None:
    fn = create_mock_retrieval_function()
    result = test_high_volume(fn, num_queries=5)
    assert result["total_queries"] == 5
    assert result["successful"] == 5
    assert result["failed"] == 0


def test_large_context_returns_stats() -> None:
    fn = create_mock_retrieval_function()
    result = test_large_context(fn)
    assert result["large_context_tests"]
    assert result["success_rate"] > 0


def test_concurrent_queries_reports_throughput() -> None:
    fn = create_mock_retrieval_function()
    result = test_concurrent_queries(fn, num_concurrent=3)
    assert result["concurrent_queries"] == 3
    assert result["successful"] == 3


def test_run_failure_mode_tests_summary() -> None:
    fn = create_mock_retrieval_function()
    summary = run_failure_mode_tests(fn)
    assert summary["summary"]["total"] == 4
    assert summary["summary"]["completed"] >= 1
