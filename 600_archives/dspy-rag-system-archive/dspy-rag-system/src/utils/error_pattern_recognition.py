#!/usr/bin/env python3
# ANCHOR_KEY: error-pattern-recognition
# ANCHOR_PRIORITY: 25
# ROLE_PINS: ["implementer", "coder"]
"""
Advanced Error Pattern Recognition System

This module implements intelligent error pattern recognition for the DSPy RAG system.
It analyzes error patterns, categorizes them, and provides recovery suggestions.
"""

import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ErrorPattern:
    """Represents a recognized error pattern"""

    pattern_id: str
    category: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    regex_pattern: str
    recovery_suggestion: str
    model_specific: str | None = None
    context_hints: list[str] = None


@dataclass
class ErrorAnalysis:
    """Result of error pattern analysis"""

    matched_patterns: list[ErrorPattern]
    severity_score: float
    recovery_actions: list[str]
    confidence: float
    model_specific_handling: str | None = None


class ErrorPatternRecognizer:
    """Advanced error pattern recognition system"""

    def __init__(self):
        self.patterns = self._load_error_patterns()
        self.error_history = []
        self.pattern_stats = {}

    def _load_error_patterns(self) -> list[ErrorPattern]:
        """Load error patterns from configuration"""
        patterns = [
            # Database Connection Errors
            ErrorPattern(
                pattern_id="DB_CONNECTION_TIMEOUT",
                category="database",
                severity="high",
                description="Database connection timeout",
                regex_pattern=r"connection.*timeout|timeout.*connection",
                recovery_suggestion="Check database connectivity and retry with exponential backoff",
            ),
            ErrorPattern(
                pattern_id="DB_AUTHENTICATION_FAILED",
                category="database",
                severity="critical",
                description="Database authentication failure",
                regex_pattern=r"authentication.*failed|auth.*failed|invalid.*password",
                recovery_suggestion="Verify database credentials and connection parameters",
            ),
            # LLM API Errors
            ErrorPattern(
                pattern_id="LLM_TIMEOUT",
                category="llm",
                severity="medium",
                description="LLM API request timeout",
                regex_pattern=r"timeout.*llm|llm.*timeout|request.*timeout",
                recovery_suggestion="Increase timeout or retry with smaller context window",
            ),
            ErrorPattern(
                pattern_id="LLM_RATE_LIMIT",
                category="llm",
                severity="medium",
                description="LLM API rate limit exceeded",
                regex_pattern=r"rate.*limit|too.*many.*requests|429",
                recovery_suggestion="Implement exponential backoff and retry after delay",
            ),
            ErrorPattern(
                pattern_id="LLM_MODEL_NOT_FOUND",
                category="llm",
                severity="high",
                description="Requested LLM model not available",
                regex_pattern=r"model.*not.*found|model.*does.*not.*exist",
                recovery_suggestion="Check model availability or fallback to default model",
            ),
            # File Processing Errors
            ErrorPattern(
                pattern_id="FILE_NOT_FOUND",
                category="file",
                severity="medium",
                description="File not found error",
                regex_pattern=r"file.*not.*found|no.*such.*file",
                recovery_suggestion="Verify file path and permissions",
            ),
            ErrorPattern(
                pattern_id="FILE_PERMISSION_DENIED",
                category="file",
                severity="high",
                description="File permission denied",
                regex_pattern=r"permission.*denied|access.*denied",
                recovery_suggestion="Check file permissions and ownership",
            ),
            ErrorPattern(
                pattern_id="FILE_TOO_LARGE",
                category="file",
                severity="medium",
                description="File size exceeds limit",
                regex_pattern=r"file.*too.*large|size.*exceeds",
                recovery_suggestion="Split file into smaller chunks or increase size limit",
            ),
            # Security Errors
            ErrorPattern(
                pattern_id="SECURITY_VIOLATION",
                category="security",
                severity="critical",
                description="Security validation failed",
                regex_pattern=r"security.*violation|blocked.*pattern|injection.*attempt",
                recovery_suggestion="Review input validation and sanitization",
            ),
            ErrorPattern(
                pattern_id="PATH_TRAVERSAL",
                category="security",
                severity="critical",
                description="Path traversal attempt detected",
                regex_pattern=r"path.*traversal|directory.*traversal",
                recovery_suggestion="Validate file paths and implement path sanitization",
            ),
            # Network Errors
            ErrorPattern(
                pattern_id="NETWORK_TIMEOUT",
                category="network",
                severity="medium",
                description="Network request timeout",
                regex_pattern=r"network.*timeout|connection.*timed.*out",
                recovery_suggestion="Check network connectivity and retry with backoff",
            ),
            ErrorPattern(
                pattern_id="NETWORK_UNREACHABLE",
                category="network",
                severity="high",
                description="Network host unreachable",
                regex_pattern=r"unreachable|connection.*refused",
                recovery_suggestion="Verify network configuration and host availability",
            ),
            # Memory Errors
            ErrorPattern(
                pattern_id="MEMORY_ERROR",
                category="system",
                severity="high",
                description="Memory allocation error",
                regex_pattern=r"memory.*error|out.*of.*memory|memory.*allocation",
                recovery_suggestion="Reduce batch size or implement memory management",
            ),
            # Configuration Errors
            ErrorPattern(
                pattern_id="CONFIG_ERROR",
                category="configuration",
                severity="medium",
                description="Configuration error",
                regex_pattern=r"config.*error|invalid.*config|missing.*config",
                recovery_suggestion="Validate configuration files and environment variables",
            ),
            # Model-Specific Errors
            ErrorPattern(
                pattern_id="MISTRAL_CONTEXT_LIMIT",
                category="llm",
                severity="medium",
                description="Mistral context window exceeded",
                regex_pattern=r"context.*window|token.*limit",
                model_specific="mistral",
                recovery_suggestion="Reduce input length or implement chunking",
            ),
            ErrorPattern(
                pattern_id="YI_CODER_MODEL_ERROR",
                category="llm",
                severity="medium",
                description="Yi-Coder model specific error",
                regex_pattern=r"yi.*coder|yi.*model",
                model_specific="yi-coder",
                recovery_suggestion="Check Yi-Coder model availability and configuration",
            ),
        ]

        # Load additional patterns from config if available
        try:
            config_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "config", "error_patterns.json")
            if os.path.exists(config_path):
                with open(config_path) as f:
                    custom_patterns = json.load(f)
                    for pattern_data in custom_patterns:
                        patterns.append(ErrorPattern(**pattern_data))
        except Exception as e:
            logger.warning(f"Could not load custom error patterns: {e}")

        return patterns

    def analyze_error(
        self, error_message: str, error_type: str = None, context: dict[str, Any] = None
    ) -> ErrorAnalysis:
        """
        Analyze an error message and identify patterns

        Args:
            error_message: The error message to analyze
            error_type: Optional error type/exception class
            context: Optional context information (model_id, operation, etc.)

        Returns:
            ErrorAnalysis object with pattern matches and recovery suggestions
        """
        matched_patterns = []
        severity_scores = []
        recovery_actions = []
        model_specific_handling = None

        # Analyze error message against patterns
        for pattern in self.patterns:
            if re.search(pattern.regex_pattern, error_message, re.IGNORECASE):
                matched_patterns.append(pattern)
                severity_scores.append(self._get_severity_score(pattern.severity))
                recovery_actions.append(pattern.recovery_suggestion)

                # Check for model-specific handling
                if pattern.model_specific and context and context.get("model_id"):
                    if pattern.model_specific in context["model_id"].lower():
                        model_specific_handling = pattern.recovery_suggestion

        # Calculate overall severity score
        severity_score = max(severity_scores) if severity_scores else 0.0

        # Calculate confidence based on pattern matches
        confidence = min(len(matched_patterns) * 0.3, 1.0) if matched_patterns else 0.0

        # Update pattern statistics
        self._update_pattern_stats(matched_patterns)

        # Log analysis results
        logger.info(
            f"Error analysis completed: {len(matched_patterns)} patterns matched, "
            f"severity: {severity_score:.2f}, confidence: {confidence:.2f}"
        )

        return ErrorAnalysis(
            matched_patterns=matched_patterns,
            severity_score=severity_score,
            recovery_actions=recovery_actions,
            model_specific_handling=model_specific_handling,
            confidence=confidence,
        )

    def _get_severity_score(self, severity: str) -> float:
        """Convert severity string to numeric score"""
        severity_map = {"low": 0.25, "medium": 0.5, "high": 0.75, "critical": 1.0}
        return severity_map.get(severity.lower(), 0.5)

    def _update_pattern_stats(self, matched_patterns: list[ErrorPattern]):
        """Update pattern usage statistics"""
        for pattern in matched_patterns:
            if pattern.pattern_id not in self.pattern_stats:
                self.pattern_stats[pattern.pattern_id] = {
                    "count": 0,
                    "first_seen": datetime.now(),
                    "last_seen": datetime.now(),
                }

            self.pattern_stats[pattern.pattern_id]["count"] += 1
            self.pattern_stats[pattern.pattern_id]["last_seen"] = datetime.now()

    def get_pattern_statistics(self) -> dict[str, Any]:
        """Get error pattern statistics"""
        return {
            "total_patterns": len(self.patterns),
            "pattern_stats": self.pattern_stats,
            "most_common_patterns": sorted(self.pattern_stats.items(), key=lambda x: x[1]["count"], reverse=True)[:5],
        }

    def suggest_recovery_strategy(self, analysis: ErrorAnalysis) -> list[str]:
        """Suggest recovery strategies based on error analysis"""
        strategies = []

        if analysis.severity_score >= 0.75:
            strategies.append("Implement immediate retry with exponential backoff")
            strategies.append("Check system health and resource availability")

        if analysis.severity_score >= 0.5:
            strategies.append("Log detailed error context for debugging")
            strategies.append("Consider fallback mechanisms")

        if analysis.model_specific_handling:
            strategies.append(f"Apply model-specific handling: {analysis.model_specific_handling}")

        # Add pattern-specific strategies
        for pattern in analysis.matched_patterns:
            if pattern.category == "database":
                strategies.append("Verify database connectivity and credentials")
            elif pattern.category == "llm":
                strategies.append("Check LLM service availability and rate limits")
            elif pattern.category == "security":
                strategies.append("Review input validation and sanitization")
            elif pattern.category == "file":
                strategies.append("Verify file permissions and path validity")

        return strategies


# Global instance
error_recognizer = ErrorPatternRecognizer()


def analyze_error_pattern(error_message: str, error_type: str = None, context: dict[str, Any] = None) -> ErrorAnalysis:
    """
    Convenience function to analyze error patterns

    Args:
        error_message: Error message to analyze
        error_type: Optional error type
        context: Optional context information

    Returns:
        ErrorAnalysis object
    """
    return error_recognizer.analyze_error(error_message, error_type, context)


def get_error_statistics() -> dict[str, Any]:
    """Get error pattern statistics"""
    return error_recognizer.get_pattern_statistics()


def suggest_recovery_strategy(analysis: ErrorAnalysis) -> list[str]:
    """Suggest recovery strategies"""
    return error_recognizer.suggest_recovery_strategy(analysis)
