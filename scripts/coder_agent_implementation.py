#!/usr/bin/env python3
"""
Coder Agent Implementation

This module implements the Coder Agent with coding best practices, code quality assessment,
performance analysis, and refactoring suggestions capabilities.

Author: AI Development Team
Date: 2024-08-06
Version: 1.0.0
"""

import asyncio
import hashlib
import json
import logging
import re
import sqlite3
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeQualityLevel(Enum):
    """Enumeration of code quality levels."""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


class AnalysisType(Enum):
    """Enumeration of analysis types."""

    QUALITY = "quality"
    PERFORMANCE = "performance"
    SECURITY = "security"
    COMPREHENSIVE = "comprehensive"


@dataclass
class CodeIssue:
    """Data structure for code issues."""

    line_number: int
    issue_type: str
    severity: str  # "low", "medium", "high", "critical"
    description: str
    suggestion: str
    category: str  # "quality", "performance", "security"


@dataclass
class CodeAnalysis:
    """Data structure for code analysis results."""

    id: str = field(default_factory=lambda: str(uuid4()))
    file_path: str = ""
    language: str = ""
    quality_score: float = 0.0
    performance_score: float = 0.0
    security_score: float = 0.0
    maintainability_score: float = 0.0
    issues: list[CodeIssue] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    best_practices: list[str] = field(default_factory=list)
    complexity_metrics: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class RefactoringSuggestion:
    """Data structure for refactoring suggestions."""

    id: str = field(default_factory=lambda: str(uuid4()))
    original_code: str = ""
    suggested_code: str = ""
    reason: str = ""
    impact: str = "low"  # "low", "medium", "high"
    effort: str = "low"  # "low", "medium", "high"
    category: str = "quality"


class CoderDatabase:
    """Database for storing code analysis data and cache."""

    def __init__(self, db_path: str = "coder_agent.db"):
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Initialize the coder database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create code analysis table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS code_analysis (
                id TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                language TEXT NOT NULL,
                quality_score REAL NOT NULL,
                performance_score REAL NOT NULL,
                security_score REAL NOT NULL,
                maintainability_score REAL NOT NULL,
                issues TEXT,
                suggestions TEXT,
                best_practices TEXT,
                complexity_metrics TEXT,
                timestamp REAL NOT NULL
            )
        """
        )

        # Create refactoring suggestions table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS refactoring_suggestions (
                id TEXT PRIMARY KEY,
                analysis_id TEXT NOT NULL,
                original_code TEXT NOT NULL,
                suggested_code TEXT NOT NULL,
                reason TEXT,
                impact TEXT,
                effort TEXT,
                category TEXT,
                timestamp REAL NOT NULL,
                FOREIGN KEY (analysis_id) REFERENCES code_analysis (id)
            )
        """
        )

        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_file ON code_analysis(file_path)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_language ON code_analysis(language)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_analysis_timestamp ON code_analysis(timestamp)")

        conn.commit()
        conn.close()
        logger.info("Coder database initialized")

    def store_analysis(self, analysis: CodeAnalysis) -> str:
        """Store code analysis in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO code_analysis 
            (id, file_path, language, quality_score, performance_score, security_score,
             maintainability_score, issues, suggestions, best_practices, complexity_metrics, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                analysis.id,
                analysis.file_path,
                analysis.language,
                analysis.quality_score,
                analysis.performance_score,
                analysis.security_score,
                analysis.maintainability_score,
                json.dumps([asdict(issue) for issue in analysis.issues]),
                json.dumps(analysis.suggestions),
                json.dumps(analysis.best_practices),
                json.dumps(analysis.complexity_metrics),
                analysis.timestamp,
            ),
        )

        conn.commit()
        conn.close()
        return analysis.id

    def get_analysis(self, analysis_id: str) -> CodeAnalysis | None:
        """Get code analysis by ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, file_path, language, quality_score, performance_score, security_score,
                   maintainability_score, issues, suggestions, best_practices, complexity_metrics, timestamp
            FROM code_analysis WHERE id = ?
        """,
            (analysis_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            issues_data = json.loads(row[7]) if row[7] else []
            issues = [CodeIssue(**issue_data) for issue_data in issues_data]

            return CodeAnalysis(
                id=row[0],
                file_path=row[1],
                language=row[2],
                quality_score=row[3],
                performance_score=row[4],
                security_score=row[5],
                maintainability_score=row[6],
                issues=issues,
                suggestions=json.loads(row[8]) if row[8] else [],
                best_practices=json.loads(row[9]) if row[9] else [],
                complexity_metrics=json.loads(row[10]) if row[10] else {},
                timestamp=row[11],
            )

        return None


class CoderAgent:
    """Specialized agent for coding best practices and code quality improvements."""

    def __init__(self):
        self.name = "Coder Agent"
        self.capabilities = [
            "code_quality_assessment",
            "performance_analysis",
            "security_analysis",
            "refactoring_suggestions",
            "best_practices_validation",
        ]
        self.database = CoderDatabase()
        self.analysis_cache: dict[str, CodeAnalysis] = {}
        self.usage_count = 0
        self.error_count = 0
        self.last_used = time.time()

        # Language-specific patterns and rules
        self.language_patterns = {
            "python": {
                "file_extension": r"\.py$",
                "complexity_patterns": [
                    r"if.*and.*and",  # Multiple conditions
                    r"for.*for",  # Nested loops
                    r"def.*def",  # Nested functions
                ],
                "quality_patterns": [
                    r"import \*",  # Wildcard imports
                    r"print\(",  # Debug prints
                    r"TODO|FIXME",  # TODO comments
                ],
                "security_patterns": [
                    r"eval\(",  # Dangerous eval
                    r"exec\(",  # Dangerous exec
                    r"input\(",  # Unsafe input
                ],
            },
            "javascript": {
                "file_extension": r"\.js$",
                "complexity_patterns": [
                    r"if.*&&.*&&",  # Multiple conditions
                    r"for.*for",  # Nested loops
                    r"function.*function",  # Nested functions
                ],
                "quality_patterns": [
                    r"console\.log",  # Debug logs
                    r"var ",  # Old var declarations
                    r"TODO|FIXME",  # TODO comments
                ],
                "security_patterns": [
                    r"eval\(",  # Dangerous eval
                    r"innerHTML",  # XSS risk
                    r"document\.write",  # XSS risk
                ],
            },
        }

    async def process_request(self, request: dict[str, Any]) -> dict[str, Any]:
        """Process coding request."""
        start_time = time.time()

        try:
            file_path = request.get("file_path", "")
            code_content = request.get("code_content", "")
            analysis_type = request.get("analysis_type", "comprehensive")

            # Check cache first
            cache_key = self._generate_cache_key(file_path, code_content, analysis_type)
            if cache_key in self.analysis_cache:
                cached_analysis = self.analysis_cache[cache_key]
                if time.time() - cached_analysis.timestamp < 1800:  # 30 min cache
                    logger.info(f"Using cached analysis for: {file_path}")
                    return self._format_analysis_response(cached_analysis)

            # Perform code analysis
            analysis = await self._analyze_code(file_path, code_content, analysis_type)

            # Cache the results
            self.analysis_cache[cache_key] = analysis

            # Store in database
            self.database.store_analysis(analysis)

            processing_time = time.time() - start_time
            self.usage_count += 1
            self.last_used = time.time()

            response = self._format_analysis_response(analysis)
            response["processing_time"] = processing_time

            return response

        except Exception as e:
            self.error_count += 1
            logger.error(f"Error in Coder Agent: {e}")
            raise

    def can_handle(self, request: dict[str, Any]) -> bool:
        """Check if coder agent can handle the request."""
        coding_keywords = [
            "code",
            "refactor",
            "optimize",
            "quality",
            "performance",
            "security",
            "best practices",
            "pattern",
            "architecture",
            "review",
            "analyze",
            "improve",
            "fix",
        ]
        query = request.get("query", "").lower()
        return any(keyword in query for keyword in coding_keywords)

    async def _analyze_code(self, file_path: str, code_content: str, analysis_type: str) -> CodeAnalysis:
        """Analyze code and provide suggestions."""
        logger.info(f"Starting code analysis for: {file_path}")

        # Simulate analysis time based on type
        if analysis_type == "comprehensive":
            await asyncio.sleep(0.5)
        elif analysis_type == "detailed":
            await asyncio.sleep(0.3)
        else:
            await asyncio.sleep(0.2)

        # Detect language
        language = self._detect_language(file_path)

        # Perform analysis based on type
        if analysis_type == "quality":
            analysis = await self._analyze_quality(code_content, language)
        elif analysis_type == "performance":
            analysis = await self._analyze_performance(code_content, language)
        elif analysis_type == "security":
            analysis = await self._analyze_security(code_content, language)
        else:  # comprehensive
            analysis = await self._analyze_comprehensive(code_content, language)

        analysis.file_path = file_path
        analysis.language = language

        return analysis

    async def _analyze_quality(self, code_content: str, language: str) -> CodeAnalysis:
        """Analyze code quality."""
        issues = []
        suggestions = []
        best_practices = []

        # Check for common quality issues
        lines = code_content.split("\n")
        for i, line in enumerate(lines, 1):
            # Check for TODO/FIXME comments
            if re.search(r"TODO|FIXME", line, re.IGNORECASE):
                issues.append(
                    CodeIssue(
                        line_number=i,
                        issue_type="quality",
                        severity="medium",
                        description="TODO/FIXME comment found",
                        suggestion="Remove or implement the TODO/FIXME",
                        category="quality",
                    )
                )

            # Check for long lines
            if len(line) > 120:
                issues.append(
                    CodeIssue(
                        line_number=i,
                        issue_type="quality",
                        severity="low",
                        description="Line too long",
                        suggestion="Break long line into multiple lines",
                        category="quality",
                    )
                )

            # Check for debug statements
            if re.search(r"print\(|console\.log", line):
                issues.append(
                    CodeIssue(
                        line_number=i,
                        issue_type="quality",
                        severity="low",
                        description="Debug statement found",
                        suggestion="Remove debug statement for production",
                        category="quality",
                    )
                )

        # Calculate quality score
        total_lines = len(lines)
        issue_count = len([i for i in issues if i.severity in ["high", "critical"]])
        quality_score = max(0.0, 1.0 - (issue_count / max(total_lines, 1)))

        suggestions = [
            "Add type hints for better code clarity",
            "Use meaningful variable and function names",
            "Add docstrings for functions and classes",
            "Follow PEP 8 style guidelines",
        ]

        best_practices = [
            "Write self-documenting code",
            "Keep functions small and focused",
            "Use meaningful comments",
            "Follow consistent naming conventions",
        ]

        return CodeAnalysis(
            quality_score=quality_score,
            performance_score=0.8,
            security_score=0.9,
            maintainability_score=quality_score,
            issues=issues,
            suggestions=suggestions,
            best_practices=best_practices,
            complexity_metrics={
                "lines_of_code": total_lines,
                "issue_count": len(issues),
                "quality_issues": len([i for i in issues if i.category == "quality"]),
            },
        )

    async def _analyze_performance(self, code_content: str, language: str) -> CodeAnalysis:
        """Analyze code performance."""
        issues = []
        suggestions = []
        best_practices = []

        # Check for performance issues
        lines = code_content.split("\n")
        for i, line in enumerate(lines, 1):
            # Check for inefficient patterns
            if re.search(r"for.*for", line):  # Nested loops
                issues.append(
                    CodeIssue(
                        line_number=i,
                        issue_type="performance",
                        severity="medium",
                        description="Nested loop detected",
                        suggestion="Consider using list comprehension or vectorization",
                        category="performance",
                    )
                )

            # Check for string concatenation in loops
            if re.search(r'\+=.*["\']', line):
                issues.append(
                    CodeIssue(
                        line_number=i,
                        issue_type="performance",
                        severity="low",
                        description="String concatenation in loop",
                        suggestion="Use join() or list comprehension",
                        category="performance",
                    )
                )

        suggestions = [
            "Use list comprehensions instead of loops where possible",
            "Implement caching for expensive operations",
            "Use generators for large datasets",
            "Profile code to identify bottlenecks",
        ]

        best_practices = [
            "Avoid premature optimization",
            "Measure performance before optimizing",
            "Use appropriate data structures",
            "Consider algorithmic complexity",
        ]

        return CodeAnalysis(
            quality_score=0.8,
            performance_score=0.75,
            security_score=0.9,
            maintainability_score=0.8,
            issues=issues,
            suggestions=suggestions,
            best_practices=best_practices,
            complexity_metrics={
                "lines_of_code": len(lines),
                "performance_issues": len([i for i in issues if i.category == "performance"]),
            },
        )

    async def _analyze_security(self, code_content: str, language: str) -> CodeAnalysis:
        """Analyze code security."""
        issues = []
        suggestions = []
        best_practices = []

        # Check for security issues
        lines = code_content.split("\n")
        for i, line in enumerate(lines, 1):
            # Check for dangerous functions
            if re.search(r"eval\(|exec\(", line):
                issues.append(
                    CodeIssue(
                        line_number=i,
                        issue_type="security",
                        severity="critical",
                        description="Dangerous function call",
                        suggestion="Avoid eval() and exec() for security",
                        category="security",
                    )
                )

            # Check for SQL injection patterns
            if re.search(r'f".*SELECT|f".*INSERT', line, re.IGNORECASE):
                issues.append(
                    CodeIssue(
                        line_number=i,
                        issue_type="security",
                        severity="high",
                        description="Potential SQL injection",
                        suggestion="Use parameterized queries",
                        category="security",
                    )
                )

        suggestions = [
            "Use parameterized queries to prevent SQL injection",
            "Validate and sanitize all inputs",
            "Use secure authentication methods",
            "Implement proper error handling",
        ]

        best_practices = [
            "Follow OWASP security guidelines",
            "Use HTTPS for all communications",
            "Implement proper access controls",
            "Regular security audits",
        ]

        return CodeAnalysis(
            quality_score=0.9,
            performance_score=0.8,
            security_score=0.7,
            maintainability_score=0.8,
            issues=issues,
            suggestions=suggestions,
            best_practices=best_practices,
            complexity_metrics={
                "lines_of_code": len(lines),
                "security_issues": len([i for i in issues if i.category == "security"]),
            },
        )

    async def _analyze_comprehensive(self, code_content: str, language: str) -> CodeAnalysis:
        """Comprehensive code analysis."""
        # Combine all analysis types
        quality_analysis = await self._analyze_quality(code_content, language)
        performance_analysis = await self._analyze_performance(code_content, language)
        security_analysis = await self._analyze_security(code_content, language)

        # Combine issues
        all_issues = quality_analysis.issues + performance_analysis.issues + security_analysis.issues

        # Combine suggestions
        all_suggestions = list(
            set(quality_analysis.suggestions + performance_analysis.suggestions + security_analysis.suggestions)
        )

        # Combine best practices
        all_best_practices = list(
            set(
                quality_analysis.best_practices + performance_analysis.best_practices + security_analysis.best_practices
            )
        )

        # Calculate average scores
        quality_score = (
            quality_analysis.quality_score + performance_analysis.quality_score + security_analysis.quality_score
        ) / 3

        performance_score = (
            quality_analysis.performance_score
            + performance_analysis.performance_score
            + security_analysis.performance_score
        ) / 3

        security_score = (
            quality_analysis.security_score + performance_analysis.security_score + security_analysis.security_score
        ) / 3

        maintainability_score = (
            quality_analysis.maintainability_score
            + performance_analysis.maintainability_score
            + security_analysis.maintainability_score
        ) / 3

        return CodeAnalysis(
            quality_score=quality_score,
            performance_score=performance_score,
            security_score=security_score,
            maintainability_score=maintainability_score,
            issues=all_issues,
            suggestions=all_suggestions,
            best_practices=all_best_practices,
            complexity_metrics={
                "lines_of_code": len(code_content.split("\n")),
                "total_issues": len(all_issues),
                "quality_issues": len([i for i in all_issues if i.category == "quality"]),
                "performance_issues": len([i for i in all_issues if i.category == "performance"]),
                "security_issues": len([i for i in all_issues if i.category == "security"]),
            },
        )

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file path."""
        for language, patterns in self.language_patterns.items():
            if re.search(patterns["file_extension"], file_path, re.IGNORECASE):
                return language
        return "unknown"

    def _format_analysis_response(self, analysis: CodeAnalysis) -> dict[str, Any]:
        """Format code analysis into response."""
        return {
            "agent_type": "coder",
            "file_path": analysis.file_path,
            "language": analysis.language,
            "quality_score": analysis.quality_score,
            "performance_score": analysis.performance_score,
            "security_score": analysis.security_score,
            "maintainability_score": analysis.maintainability_score,
            "issues": [asdict(issue) for issue in analysis.issues],
            "suggestions": analysis.suggestions,
            "best_practices": analysis.best_practices,
            "complexity_metrics": analysis.complexity_metrics,
            "timestamp": analysis.timestamp,
        }

    def _generate_cache_key(self, file_path: str, code_content: str, analysis_type: str) -> str:
        """Generate cache key for code analysis."""
        content = f"{file_path}:{code_content}:{analysis_type}"
        return hashlib.md5(content.encode()).hexdigest()

    def get_status(self) -> dict[str, Any]:
        """Get agent status information."""
        return {
            "agent_type": "coder",
            "name": self.name,
            "capabilities": self.capabilities,
            "usage_count": self.usage_count,
            "error_count": self.error_count,
            "last_used": self.last_used,
            "cache_size": len(self.analysis_cache),
        }


# Example usage and testing
async def main():
    """Example usage of the Coder Agent."""
    agent = CoderAgent()

    # Test different types of code analysis
    test_requests = [
        {
            "file_path": "example.py",
            "code_content": """
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

# TODO: Optimize this function
print("Debug: Calculating fibonacci")

for i in range(10):
    result = calculate_fibonacci(i)
    print(f"Fibonacci({i}) = {result}")
""",
            "analysis_type": "quality",
        },
        {
            "file_path": "performance_example.py",
            "code_content": """
def inefficient_string_builder():
    result = ""
    for i in range(1000):
        result += str(i)  # Inefficient string concatenation
    return result

def nested_loops():
    for i in range(100):
        for j in range(100):
            for k in range(100):
                pass  # Triple nested loop
""",
            "analysis_type": "performance",
        },
        {
            "file_path": "security_example.py",
            "code_content": """
import sqlite3

def unsafe_query(user_input):
    query = f"SELECT * FROM users WHERE name = '{user_input}'"
    return eval(query)  # Dangerous eval usage

def unsafe_exec(code):
    exec(code)  # Dangerous exec usage
""",
            "analysis_type": "security",
        },
    ]

    for i, request in enumerate(test_requests, 1):
        print(f"\n--- Test Code Analysis {i} ---")
        print(f"File: {request['file_path']}")
        print(f"Type: {request['analysis_type']}")

        try:
            response = await agent.process_request(request)
            print(f"Agent: {response['agent_type']}")
            print(f"Language: {response['language']}")
            print(f"Quality Score: {response['quality_score']:.2f}")
            print(f"Performance Score: {response['performance_score']:.2f}")
            print(f"Security Score: {response['security_score']:.2f}")
            print(f"Issues Found: {len(response['issues'])}")
            print(f"Suggestions: {len(response['suggestions'])}")
            print(f"Processing Time: {response.get('processing_time', 0):.3f}s")
        except Exception as e:
            print(f"Error: {e}")

    # Print agent status
    print("\n--- Agent Status ---")
    status = agent.get_status()
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
