from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
                import re
                from pathlib import Path
import os
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3

# ANCHOR_KEY: task-generation-automation
# ANCHOR_PRIORITY: 25
# ROLE_PINS: ["coder", "implementer"]
"""
Task Generation Automation System

Automates the generation of tasks from PRDs and backlog items, ensuring
consistent quality, comprehensive testing requirements, and proper quality gates.

Usage:
    python3 scripts/task_generation_automation.py --prd path/to/prd.md
    python3 scripts/task_generation_automation.py --backlog-id B-050
    python3 scripts/task_generation_automation.py --batch path/to/backlog.md
"""

@dataclass
class TaskRequirement:
    """Represents a single requirement from a PRD or backlog item."""

    id: str
    title: str
    description: str
    acceptance_criteria: list[str]
    priority: str
    estimated_time: str
    dependencies: list[str]
    effort_points: int | None = None
    complexity: str | None = None

@dataclass
class GeneratedTask:
    """Represents a generated task with all required components."""

    name: str
    priority: str
    estimated_time: str
    dependencies: list[str]
    description: str
    acceptance_criteria: list[str]
    testing_requirements: dict[str, list[str]]
    implementation_notes: str
    quality_gates: list[str]
    task_type: str
    complexity: str

class PRDParser:
    """Parses PRD files to extract requirements and technical details."""

    def __init__(self, prd_path: str):
        self.prd_path = Path(prd_path)
        self.content = self.prd_path.read_text(encoding="utf-8")

    def parse(self) -> list[TaskRequirement]:
        """Parse PRD and extract requirements."""
        requirements = []

        # Extract functional requirements - handle both formats
        fr_patterns = [
            r"#### FR-\d+\.\d+: ([^\n]+)\n- ([^\n]+)",  # FR-1.1: Title format
            r"#### FR-\d+: ([^\n]+)\n- ([^\n]+)",  # FR-1: Title format
        ]

        for pattern in fr_patterns:
            fr_matches = re.findall(pattern, self.content)
            for i, (title, description) in enumerate(fr_matches):
                requirement = TaskRequirement(
                    id=f"FR-{i+1}",
                    title=title.strip(),
                    description=description.strip(),
                    acceptance_criteria=self._extract_acceptance_criteria(title),
                    priority=self._determine_priority(title, description),
                    estimated_time=self._estimate_time(description),
                    dependencies=self._extract_dependencies(description),
                    complexity=self._assess_complexity(description),
                )
                requirements.append(requirement)

        # Extract non-functional requirements - handle both formats
        nfr_patterns = [
            r"#### NFR-\d+\.\d+: ([^\n]+)\n- ([^\n]+)",  # NFR-1.1: Title format
            r"#### NFR-\d+: ([^\n]+)\n- ([^\n]+)",  # NFR-1: Title format
        ]

        for pattern in nfr_patterns:
            nfr_matches = re.findall(pattern, self.content)
            for i, (title, description) in enumerate(nfr_matches):
                requirement = TaskRequirement(
                    id=f"NFR-{i+1}",
                    title=title.strip(),
                    description=description.strip(),
                    acceptance_criteria=self._extract_acceptance_criteria(title),
                    priority=self._determine_priority(title, description),
                    estimated_time=self._estimate_time(description),
                    dependencies=self._extract_dependencies(description),
                    complexity=self._assess_complexity(description),
                )
                requirements.append(requirement)

        return requirements

    def _extract_acceptance_criteria(self, requirement_title: str) -> list[str]:
        """Extract acceptance criteria for a requirement."""
        # Look for acceptance criteria in the PRD
        ac_pattern = r"### Acceptance Criteria\n(.*?)(?=\n###|\n##|\Z)"
        ac_match = re.search(ac_pattern, self.content, re.DOTALL)

        if ac_match:
            ac_content = ac_match.group(1)
            # Extract individual criteria
            criteria = re.findall(r"- \[ \] ([^\n]+)", ac_content)
            return [c.strip() for c in criteria if c.strip()]

        # Generate default acceptance criteria based on requirement type
        if "performance" in requirement_title.lower():
            return [
                "Performance benchmarks are defined and measurable",
                "System meets specified performance thresholds",
                "Performance tests are implemented and passing",
            ]
        elif "security" in requirement_title.lower():
            return [
                "Security requirements are implemented",
                "Security tests are passing",
                "No critical security vulnerabilities detected",
            ]
        else:
            return [
                "Requirement is fully implemented",
                "All acceptance criteria are met",
                "Tests are passing and documentation is updated",
            ]

    def _determine_priority(self, title: str, description: str) -> str:
        """Determine task priority based on content."""
        text = f"{title} {description}".lower()

        if any(word in text for word in ["critical", "essential", "must", "security", "performance"]):
            return "Critical"
        elif any(word in text for word in ["important", "high", "core", "integration"]):
            return "High"
        elif any(word in text for word in ["medium", "standard", "normal"]):
            return "Medium"
        else:
            return "Low"

    def _estimate_time(self, description: str) -> str:
        """Estimate time based on description complexity."""
        words = len(description.split())

        if words < 20:
            return "2-4 hours"
        elif words < 50:
            return "4-8 hours"
        elif words < 100:
            return "1-2 days"
        else:
            return "2-5 days"

    def _extract_dependencies(self, description: str) -> list[str]:
        """Extract dependencies from description."""
        # Look for dependency patterns
        deps = []

        # Look for references to other requirements
        dep_pattern = r"(FR-\d+\.\d+|NFR-\d+\.\d+)"
        matches = re.findall(dep_pattern, description)
        deps.extend(matches)

        # Look for external dependencies
        external_pattern = r"(Python|library|framework|API|database)"
        external_matches = re.findall(external_pattern, description, re.IGNORECASE)
        deps.extend([f"External: {match}" for match in set(external_matches)])

        return deps

    def _assess_complexity(self, description: str) -> str:
        """Assess task complexity."""
        words = len(description.split())

        if words < 30:
            return "Simple"
        elif words < 80:
            return "Medium"
        else:
            return "Complex"

class BacklogParser:
    """Parses backlog items to extract requirements."""

    def __init__(self, backlog_path: str = "000_core/000_backlog.md"):
        self.backlog_path = Path(backlog_path)
        self.content = self.backlog_path.read_text(encoding="utf-8")

    def parse_backlog_item(self, backlog_id: str) -> TaskRequirement | None:
        """Parse a specific backlog item by ID."""
        # Find the backlog item
        pattern = (
            rf"\| {re.escape(backlog_id)} \| ([^|]+) \| ([^|]+) \| (\d+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|"
        )
        match = re.search(pattern, self.content)

        if not match:
            return None

        title, emoji, points, status, description, category, workflow = match.groups()

        # Extract metadata from comments
        metadata = self._extract_metadata(backlog_id)

        requirement = TaskRequirement(
            id=backlog_id,
            title=title.strip(),
            description=description.strip(),
            acceptance_criteria=metadata.get("acceptance", []),
            priority=self._emoji_to_priority(emoji.strip()),
            estimated_time=metadata.get("est_hours", "4-8 hours"),
            dependencies=metadata.get("deps", []),
            effort_points=int(points) if points.isdigit() else None,
            complexity=self._assess_complexity(description.strip()) or "Medium",
        )

        return requirement

    def _extract_metadata(self, backlog_id: str) -> dict[str, Any]:
        """Extract metadata from backlog item comments."""
        metadata = {}

        # Find the metadata block for this item
        pattern = r"<!--score: {([^}]+)}-->\s*<!--score_total: ([^>]+)-->\s*<!-- do_next: ([^>]+) -->\s*<!-- est_hours: ([^>]+) -->\s*<!-- acceptance: ([^>]+) -->"
        match = re.search(pattern, self.content)

        if match:
            score_data, score_total, do_next, est_hours, acceptance = match.groups()

            # Parse score data
            score_match = re.search(r"deps:\[([^\]]*)\]", score_data)
            if score_match:
                deps_str = score_match.group(1)
                deps = [dep.strip().strip("\"'") for dep in deps_str.split(",") if dep.strip()]
                metadata["deps"] = deps

            metadata["est_hours"] = est_hours.strip()
            metadata["acceptance"] = [acceptance.strip()]
            metadata["do_next"] = do_next.strip()

        return metadata

    def _emoji_to_priority(self, emoji: str) -> str:
        """Convert emoji to priority level."""
        priority_map = {"🔥": "Critical", "📈": "High", "⭐": "Medium", "🔧": "Low"}
        return priority_map.get(emoji, "Medium")

    def _assess_complexity(self, description: str) -> str:
        """Assess task complexity based on description."""
        words = len(description.split())

        if words < 20:
            return "Simple"
        elif words < 50:
            return "Medium"
        else:
            return "Complex"

class TaskTemplateGenerator:
    """Generates task templates with testing requirements and quality gates."""

    def __init__(self):
        self.testing_templates = self._load_testing_templates()
        self.quality_gate_templates = self._load_quality_gate_templates()

    def generate_task(self, requirement: TaskRequirement) -> GeneratedTask:
        """Generate a complete task from a requirement."""

        # Determine task type
        task_type = self._determine_task_type(requirement)

        # Generate testing requirements
        testing_requirements = self._generate_testing_requirements(requirement, task_type)

        # Generate quality gates
        quality_gates = self._generate_quality_gates(requirement, task_type)

        # Generate implementation notes
        implementation_notes = self._generate_implementation_notes(requirement, task_type)

        task = GeneratedTask(
            name=f"Implement {requirement.title}",
            priority=requirement.priority,
            estimated_time=requirement.estimated_time,
            dependencies=requirement.dependencies,
            description=requirement.description,
            acceptance_criteria=requirement.acceptance_criteria,
            testing_requirements=testing_requirements,
            implementation_notes=implementation_notes,
            quality_gates=quality_gates,
            task_type=task_type,
            complexity=requirement.complexity or "Medium",
        )

        return task

    def _determine_task_type(self, requirement: TaskRequirement) -> str:
        """Determine the type of task based on requirement content."""
        text = f"{requirement.title} {requirement.description}".lower()

        if any(word in text for word in ["parser", "parse", "extract"]):
            return "parsing"
        elif any(word in text for word in ["test", "testing", "validation"]):
            return "testing"
        elif any(word in text for word in ["integration", "connect", "api"]):
            return "integration"
        elif any(word in text for word in ["performance", "optimization", "speed"]):
            return "performance"
        elif any(word in text for word in ["security", "authentication", "authorization"]):
            return "security"
        elif any(word in text for word in ["ui", "interface", "user"]):
            return "ui"
        elif any(word in text for word in ["database", "storage", "persistence"]):
            return "data"
        else:
            return "general"

    def _load_testing_templates(self) -> dict[str, dict[str, list[str]]]:
        """Load testing requirement templates by task type."""
        return {
            "parsing": {
                "unit_tests": [
                    "Test parsing with valid input formats",
                    "Test parsing with invalid/malformed input",
                    "Test edge cases (empty input, very large input)",
                    "Test error handling and recovery",
                ],
                "integration_tests": [
                    "Test integration with data sources",
                    "Test end-to-end parsing workflows",
                    "Test data transformation and validation",
                ],
                "performance_tests": [
                    "Test parsing speed with large datasets",
                    "Test memory usage during parsing",
                    "Test concurrent parsing operations",
                ],
                "security_tests": [
                    "Test input validation and sanitization",
                    "Test for injection attacks",
                    "Test file path handling security",
                ],
                "resilience_tests": [
                    "Test parsing under network failures",
                    "Test parsing with corrupted data",
                    "Test recovery from parsing errors",
                ],
                "edge_case_tests": [
                    "Test with maximum/minimum values",
                    "Test with special characters and Unicode",
                    "Test with concurrent access scenarios",
                ],
            },
            "testing": {
                "unit_tests": [
                    "Test test framework functionality",
                    "Test test data generation",
                    "Test test result validation",
                ],
                "integration_tests": [
                    "Test integration with CI/CD pipeline",
                    "Test test execution workflows",
                    "Test test reporting and notifications",
                ],
                "performance_tests": [
                    "Test test execution speed",
                    "Test test parallelization",
                    "Test test resource usage",
                ],
                "security_tests": [
                    "Test test data security",
                    "Test test result confidentiality",
                    "Test test environment isolation",
                ],
                "resilience_tests": [
                    "Test test execution under failures",
                    "Test test recovery mechanisms",
                    "Test test timeout handling",
                ],
                "edge_case_tests": [
                    "Test with large test datasets",
                    "Test with complex test scenarios",
                    "Test with test framework edge cases",
                ],
            },
            "integration": {
                "unit_tests": [
                    "Test individual integration components",
                    "Test API client functionality",
                    "Test data transformation logic",
                ],
                "integration_tests": [
                    "Test end-to-end integration workflows",
                    "Test API communication and data exchange",
                    "Test error handling across systems",
                ],
                "performance_tests": [
                    "Test integration response times",
                    "Test integration throughput",
                    "Test integration under load",
                ],
                "security_tests": [
                    "Test API authentication and authorization",
                    "Test data encryption in transit",
                    "Test secure communication protocols",
                ],
                "resilience_tests": [
                    "Test integration under network failures",
                    "Test integration with service outages",
                    "Test integration recovery mechanisms",
                ],
                "edge_case_tests": [
                    "Test integration with malformed data",
                    "Test integration with rate limiting",
                    "Test integration with concurrent requests",
                ],
            },
            "general": {
                "unit_tests": [
                    "Test core functionality",
                    "Test error handling",
                    "Test edge cases and boundary conditions",
                ],
                "integration_tests": [
                    "Test component interactions",
                    "Test end-to-end workflows",
                    "Test data flows and transformations",
                ],
                "performance_tests": [
                    "Test response times and throughput",
                    "Test resource usage and scalability",
                    "Test performance under load",
                ],
                "security_tests": [
                    "Test input validation and sanitization",
                    "Test access control and authorization",
                    "Test data protection and privacy",
                ],
                "resilience_tests": [
                    "Test error recovery and fault tolerance",
                    "Test system behavior under failures",
                    "Test graceful degradation",
                ],
                "edge_case_tests": [
                    "Test boundary conditions",
                    "Test unusual input scenarios",
                    "Test concurrent access patterns",
                ],
            },
        }

    def _load_quality_gate_templates(self) -> dict[str, list[str]]:
        """Load quality gate templates by task type."""
        return {
            "parsing": [
                "Code Review: All parsing logic reviewed",
                "Tests Passing: All parsing tests pass with 90%+ coverage",
                "Performance Validated: Parsing meets performance benchmarks",
                "Security Reviewed: Input validation and sanitization verified",
                "Documentation Updated: Parsing API and usage documented",
                "Error Handling: Comprehensive error handling implemented",
                "Edge Cases: Boundary conditions and edge cases tested",
            ],
            "testing": [
                "Code Review: All testing framework code reviewed",
                "Tests Passing: Framework tests pass with 95%+ coverage",
                "Performance Validated: Test execution meets performance requirements",
                "Security Reviewed: Test data and environment security verified",
                "Documentation Updated: Testing procedures and examples documented",
                "CI/CD Integration: Tests integrated into build pipeline",
                "Reporting: Test results and metrics properly reported",
            ],
            "integration": [
                "Code Review: All integration code reviewed",
                "Tests Passing: Integration tests pass with 90%+ coverage",
                "Performance Validated: Integration meets performance requirements",
                "Security Reviewed: API security and data protection verified",
                "Documentation Updated: Integration procedures documented",
                "Error Handling: Comprehensive error handling implemented",
                "Monitoring: Integration health monitoring implemented",
            ],
            "general": [
                "Code Review: All code has been reviewed",
                "Tests Passing: All tests pass with required coverage",
                "Performance Validated: Performance meets requirements",
                "Security Reviewed: Security implications considered",
                "Documentation Updated: Relevant documentation updated",
                "User Acceptance: Feature validated with stakeholders",
                "Resilience Tested: Error handling and recovery validated",
            ],
        }

    def _generate_testing_requirements(self, requirement: TaskRequirement, task_type: str) -> dict[str, list[str]]:
        """Generate testing requirements based on task type and complexity."""
        base_templates = self.testing_templates.get(task_type, self.testing_templates["general"])

        # Customize based on complexity
        if requirement.complexity == "Simple":
            # Reduce testing scope for simple tasks
            return {
                "unit_tests": base_templates["unit_tests"][:2],
                "integration_tests": base_templates["integration_tests"][:1],
                "performance_tests": [],
                "security_tests": base_templates["security_tests"][:1],
                "resilience_tests": [],
                "edge_case_tests": base_templates["edge_case_tests"][:1],
            }
        elif requirement.complexity == "Complex":
            # Expand testing scope for complex tasks
            return {
                "unit_tests": base_templates["unit_tests"]
                + ["Test advanced functionality and edge cases", "Test complex business logic and algorithms"],
                "integration_tests": base_templates["integration_tests"]
                + ["Test complex multi-component workflows", "Test system-wide integration scenarios"],
                "performance_tests": base_templates["performance_tests"]
                + ["Test scalability under high load", "Test resource optimization and efficiency"],
                "security_tests": base_templates["security_tests"]
                + ["Test advanced security scenarios", "Test compliance and regulatory requirements"],
                "resilience_tests": base_templates["resilience_tests"]
                + ["Test advanced failure scenarios", "Test disaster recovery procedures"],
                "edge_case_tests": base_templates["edge_case_tests"]
                + ["Test extreme boundary conditions", "Test complex concurrent scenarios"],
            }
        else:
            # Standard testing for medium complexity
            return base_templates

    def _generate_quality_gates(self, requirement: TaskRequirement, task_type: str) -> list[str]:
        """Generate quality gates based on task type and priority."""
        base_gates = self.quality_gate_templates.get(task_type, self.quality_gate_templates["general"])

        # Add priority-specific gates
        if requirement.priority == "Critical":
            base_gates.extend(
                [
                    "Critical Review: Senior developer review completed",
                    "Security Audit: Security team review completed",
                    "Performance Benchmark: Performance validated under stress",
                    "Disaster Recovery: Recovery procedures tested",
                ]
            )
        elif requirement.priority == "High":
            base_gates.extend(
                [
                    "Peer Review: Peer code review completed",
                    "Performance Testing: Performance requirements validated",
                    "Security Review: Security implications reviewed",
                ]
            )

        return base_gates

    def _generate_implementation_notes(self, requirement: TaskRequirement, task_type: str) -> str:
        """Generate implementation notes based on requirement and task type."""
        notes = []

        # Add task type specific notes
        if task_type == "parsing":
            notes.extend(
                [
                    "Ensure robust error handling for malformed input",
                    "Consider performance implications for large datasets",
                    "Implement proper input validation and sanitization",
                    "Add comprehensive logging for debugging",
                ]
            )
        elif task_type == "integration":
            notes.extend(
                [
                    "Implement proper retry logic for external services",
                    "Consider rate limiting and backoff strategies",
                    "Add comprehensive error handling and logging",
                    "Implement proper authentication and authorization",
                ]
            )
        elif task_type == "testing":
            notes.extend(
                [
                    "Ensure tests are isolated and repeatable",
                    "Implement proper test data management",
                    "Add comprehensive test coverage reporting",
                    "Consider test performance and execution time",
                ]
            )

        # Add complexity specific notes
        if requirement.complexity == "Complex":
            notes.extend(
                [
                    "Consider breaking down into smaller subtasks",
                    "Implement comprehensive monitoring and observability",
                    "Add detailed documentation and examples",
                    "Consider performance optimization strategies",
                ]
            )

        # Add priority specific notes
        if requirement.priority == "Critical":
            notes.extend(
                [
                    "Implement comprehensive error handling",
                    "Add detailed logging and monitoring",
                    "Consider security implications carefully",
                    "Plan for disaster recovery scenarios",
                ]
            )

        return "\n".join([f"- {note}" for note in notes])

class TaskOutputGenerator:
    """Generates formatted task output in various formats."""

    def generate_markdown(self, task: GeneratedTask) -> str:
        """Generate markdown formatted task."""
        output = []

        # Task header
        output.append(f"## {task.name}")
        output.append("")

        # Task metadata
        output.append("**Priority:** " + task.priority)
        output.append("**Estimated Time:** " + task.estimated_time)
        output.append("**Dependencies:** " + ", ".join(task.dependencies) if task.dependencies else "None")
        output.append("**Task Type:** " + task.task_type)
        output.append("**Complexity:** " + task.complexity)
        output.append("")

        # Description
        output.append("**Description:**")
        output.append(task.description)
        output.append("")

        # Acceptance criteria
        output.append("**Acceptance Criteria:**")
        for criterion in task.acceptance_criteria:
            output.append(f"- ⏹️ {criterion}")
        output.append("")

        # Testing requirements
        output.append("**Testing Requirements:**")
        for test_type, requirements in task.testing_requirements.items():
            if requirements:
                output.append(f"- **{test_type.replace('_', ' ').title()}**")
                for req in requirements:
                    output.append(f"  - ⏹️ {req}")
                output.append("")

        # Implementation notes
        output.append("**Implementation Notes:**")
        output.append(task.implementation_notes)
        output.append("")

        # Quality gates
        output.append("**Quality Gates:**")
        for gate in task.quality_gates:
            output.append(f"- ⏹️ {gate}")
        output.append("")

        return "\n".join(output)

    def generate_json(self, task: GeneratedTask) -> str:
        """Generate JSON formatted task."""
        return json.dumps(asdict(task), indent=2)

    def generate_task_list(self, tasks: list[GeneratedTask]) -> str:
        """Generate a complete task list document."""
        output = []

        # Header
        output.append("# Task List: Automated Task Generation")
        output.append("")
        output.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"**Total Tasks:** {len(tasks)}")
        output.append("")

        # Overview
        output.append("## Overview")
        output.append("This task list was automatically generated from requirements analysis.")
        output.append("Each task includes comprehensive testing requirements and quality gates.")
        output.append("")

        # Implementation phases
        output.append("## Implementation Phases")
        output.append("")

        # Phase 1: Core Implementation
        output.append("### Phase 1: Core Implementation")
        output.append("")

        for i, task in enumerate(tasks, 1):
            output.append(f"#### Task {i}: {task.name}")
            output.append("")
            output.append(f"**Priority:** {task.priority}")
            output.append(f"**Estimated Time:** {task.estimated_time}")
            output.append(f"**Dependencies:** {', '.join(task.dependencies) if task.dependencies else 'None'}")
            output.append("")
            output.append("**Description:**")
            output.append(task.description)
            output.append("")
            output.append("**Acceptance Criteria:**")
            for criterion in task.acceptance_criteria:
                output.append(f"- ⏹️ {criterion}")
            output.append("")
            output.append("**Testing Requirements:**")
            for test_type, requirements in task.testing_requirements.items():
                if requirements:
                    output.append(f"- **{test_type.replace('_', ' ').title()}**")
                    for req in requirements:
                        output.append(f"  - ⏹️ {req}")
            output.append("")
            output.append("**Quality Gates:**")
            for gate in task.quality_gates:
                output.append(f"- ⏹️ {gate}")
            output.append("")
            output.append("---")
            output.append("")

        # Quality metrics
        output.append("## Quality Metrics")
        output.append("")
        output.append("- **Test Coverage Target:** 90%+")
        output.append("- **Performance Benchmarks:** Defined per task")
        output.append("- **Security Requirements:** All security tests passing")
        output.append("- **Reliability Targets:** 99.9% uptime")
        output.append("")

        # Risk mitigation
        output.append("## Risk Mitigation")
        output.append("")
        output.append("- **Technical Risks:** Comprehensive testing and code review")
        output.append("- **Timeline Risks:** Phased approach with working increments")
        output.append("- **Resource Risks:** Clear task dependencies and resource allocation")
        output.append("")

        return "\n".join(output)

    def generate_solo_dev_task_list(self, tasks: list[GeneratedTask]) -> str:
        """Generate a solo-developer friendly task list document."""
        output = []

        # Header
        output.append("# Task List: Solo-Developer Optimized")
        output.append("")
        output.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"**Total Tasks:** {len(tasks)}")
        output.append("")

        # Overview
        output.append("## Overview")
        output.append(
            "This task list is optimized for solo development with essential quality gates and testing requirements."
        )
        output.append("Each task focuses on practical implementation with manageable complexity.")
        output.append("")

        # Implementation phases
        output.append("## Implementation Phases")
        output.append("")

        # Phase 1: Core Implementation
        output.append("### Phase 1: Core Implementation")
        output.append("")

        for i, task in enumerate(tasks, 1):
            output.append(f"#### Task {i}: {task.name}")
            output.append("")
            output.append(f"**Priority:** {task.priority}")
            output.append(f"**Estimated Time:** {task.estimated_time}")
            output.append(f"**Dependencies:** {', '.join(task.dependencies) if task.dependencies else 'None'}")
            output.append("")
            output.append("**Description:**")
            output.append(task.description)
            output.append("")
            output.append("**Acceptance Criteria:**")
            for criterion in task.acceptance_criteria:
                output.append(f"- ⏹️ {criterion}")
            output.append("")
            output.append("**Testing Requirements:**")
            # Simplified testing requirements for solo dev
            if task.testing_requirements.get("unit_tests"):
                output.append("- ⏹️ **Unit Tests** - Core functionality and error handling")
            if task.testing_requirements.get("integration_tests"):
                output.append("- ⏹️ **Integration Tests** - Component interactions and workflows")
            if task.testing_requirements.get("security_tests"):
                output.append("- ⏹️ **Security Tests** - Input validation and basic security checks")
            output.append("")
            output.append("**Implementation Notes:**")
            # Simplified implementation notes
            notes = []
            if task.priority == "Critical":
                notes.append("Focus on robust error handling and comprehensive testing")
            if "performance" in task.name.lower():
                notes.append("Include performance benchmarks and optimization considerations")
            if "security" in task.name.lower():
                notes.append("Pay special attention to input validation and security implications")
            if not notes:
                notes.append("Ensure code is well-documented and maintainable")
            output.append("\n".join([f"- {note}" for note in notes]))
            output.append("")
            output.append("**Quality Gates:**")
            # Simplified quality gates for solo dev
            solo_gates = [
                "Code Review - Self-review completed",
                "Tests Passing - All tests pass with good coverage",
                "Documentation Updated - Relevant docs updated",
            ]
            if task.priority == "Critical":
                solo_gates.append("Performance Validated - Meets performance requirements")
                solo_gates.append("Security Reviewed - Security implications considered")
            for gate in solo_gates:
                output.append(f"- ⏹️ {gate}")
            output.append("")
            output.append("---")
            output.append("")

        # Quality metrics
        output.append("## Quality Standards")
        output.append("")
        output.append("- **Test Coverage:** Good coverage with focus on critical paths")
        output.append("- **Performance:** Meets defined benchmarks")
        output.append("- **Security:** Basic security requirements satisfied")
        output.append("- **Documentation:** Clear and maintainable code")
        output.append("")

        # Risk mitigation
        output.append("## Risk Mitigation")
        output.append("")
        output.append("- **Technical Risks:** Comprehensive testing and self-review")
        output.append("- **Timeline Risks:** Phased approach with working increments")
        output.append("- **Quality Risks:** Regular check-ins and documentation updates")
        output.append("")

        return "\n".join(output)

    def generate_executable_task_list(self, tasks: list[GeneratedTask]) -> str:
        """Generate executable tasks in the format expected by 003_process-task-list.md."""
        output = []

        # Header
        output.append("# Task List: Executable Tasks")
        output.append("")
        output.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append(f"**Total Tasks:** {len(tasks)}")
        output.append("")

        # Overview
        output.append("## Overview")
        output.append("This task list is formatted for execution with the 003_process-task-list.md workflow.")
        output.append("Each task includes specific 'Do:' steps and 'Done when:' criteria for automated execution.")
        output.append("")

        # Tasks
        for i, task in enumerate(tasks, 1):
            output.append(f"### ⏳ T-{i} {task.name}")
            output.append(f"- **Priority**: {task.priority}")
            output.append(f"- **Time**: {task.estimated_time}")
            output.append(f"- **Depends on**: {', '.join(task.dependencies) if task.dependencies else 'None'}")
            output.append("")

            # Do section - actionable steps
            output.append("- **Do**:")
            do_steps = self._generate_do_steps(task)
            for step in do_steps:
                output.append(f"{step}")
            output.append("")

            # Done when section - completion criteria
            output.append("- **Done when**:")
            done_criteria = self._generate_done_criteria(task)
            for criterion in done_criteria:
                output.append(f"- ⏹️ {criterion}")
            output.append("")

            # Auto-advance and pause settings
            auto_advance = "no" if task.priority == "Critical" else "yes"
            pause_after = "yes" if task.priority == "Critical" else "no"

            output.append(f"- **Auto-Advance**: {auto_advance}")
            output.append(f"- **🛑 Pause After**: {pause_after}")
            output.append("")
            output.append("---")
            output.append("")

        # Quality standards
        output.append("## Quality Standards")
        output.append("")
        output.append("- **Test Coverage**: Good coverage with focus on critical paths")
        output.append("- **Performance**: Meets defined benchmarks")
        output.append("- **Security**: Basic security requirements satisfied")
        output.append("- **Documentation**: Clear and maintainable code")
        output.append("")

        # Risk mitigation
        output.append("## Risk Mitigation")
        output.append("")
        output.append("- **Technical Risks**: Comprehensive testing and self-review")
        output.append("- **Timeline Risks**: Phased approach with working increments")
        output.append("- **Quality Risks**: Regular check-ins and documentation updates")
        output.append("")

        return "\n".join(output)

    def _generate_do_steps(self, task: GeneratedTask) -> list[str]:
        """Generate actionable 'Do:' steps for a task."""
        steps = []

        # Base steps based on task type
        if "performance" in task.name.lower():
            steps.extend(
                [
                    "1. Set up performance measurement tools and benchmarks",
                    "2. Run baseline performance tests on current workflow",
                    "3. Identify performance bottlenecks and optimization opportunities",
                    "4. Implement performance improvements",
                    "5. Validate improvements with performance tests",
                ]
            )
        elif "security" in task.name.lower():
            steps.extend(
                [
                    "1. Review current security measures and identify gaps",
                    "2. Implement security validation and testing",
                    "3. Add input sanitization and validation",
                    "4. Test security measures with vulnerability scenarios",
                    "5. Document security improvements and procedures",
                ]
            )
        elif "testing" in task.name.lower():
            steps.extend(
                [
                    "1. Analyze current testing coverage and identify gaps",
                    "2. Design comprehensive test scenarios",
                    "3. Implement unit, integration, and system tests",
                    "4. Set up automated test execution",
                    "5. Validate test coverage and quality",
                ]
            )
        elif "integration" in task.name.lower():
            steps.extend(
                [
                    "1. Map existing system components and interfaces",
                    "2. Design integration points and data flows",
                    "3. Implement integration logic and error handling",
                    "4. Test integration with real and mock components",
                    "5. Validate end-to-end workflows",
                ]
            )
        else:
            # Generic implementation steps
            steps.extend(
                [
                    "1. Analyze requirements and design implementation approach",
                    "2. Implement core functionality with proper error handling",
                    "3. Add comprehensive testing and validation",
                    "4. Document implementation and usage procedures",
                    "5. Validate all acceptance criteria are met",
                ]
            )

        return steps

    def _generate_done_criteria(self, task: GeneratedTask) -> list[str]:
        """Generate 'Done when:' criteria for task completion validation."""
        criteria = []

        # Base criteria
        criteria.extend(
            [
                "All 'Do:' steps completed successfully",
                "Code is well-documented and maintainable",
                "Tests pass with good coverage",
            ]
        )

        # Task-specific criteria
        if "performance" in task.name.lower():
            criteria.extend(
                [
                    "Performance benchmarks are defined and measurable",
                    "System meets specified performance thresholds",
                    "Performance tests are implemented and passing",
                ]
            )
        elif "security" in task.name.lower():
            criteria.extend(
                [
                    "Security requirements are implemented",
                    "Security tests are passing",
                    "No critical security vulnerabilities detected",
                ]
            )
        elif "testing" in task.name.lower():
            criteria.extend(
                [
                    "Test coverage meets target requirements",
                    "All test scenarios are implemented and passing",
                    "Test automation is working correctly",
                ]
            )
        elif "integration" in task.name.lower():
            criteria.extend(
                [
                    "Integration points are working correctly",
                    "End-to-end workflows are validated",
                    "Error handling and recovery mechanisms tested",
                ]
            )
        else:
            # Generic criteria
            criteria.extend(
                [
                    "Requirement is fully implemented",
                    "All acceptance criteria are met",
                    "Documentation is updated and complete",
                ]
            )

        return criteria

    def _detect_task_type(self, requirements: list[TaskRequirement]) -> str:
        """Detect if this is a process improvement task or development task."""
        # Keywords that indicate process improvement vs development
        process_keywords = [
            "process",
            "workflow",
            "optimization",
            "improvement",
            "upgrade",
            "automation",
            "efficiency",
            "performance reporting",
            "testing suite",
            "canon",
            "formalize",
            "enhancement",
            "code review process",
        ]

        dev_keywords = [
            "implement",
            "develop",
            "build",
            "create",
            "code",
            "feature",
            "api",
            "database",
            "frontend",
            "backend",
            "algorithm",
            "system",
        ]

        all_text = " ".join([f"{r.title} {r.description}" for r in requirements]).lower()

        # Check for specific process improvement patterns
        if any(keyword in all_text for keyword in ["code review process", "workflow", "process upgrade"]):
            return "process_improvement"

        process_score = sum(1 for keyword in process_keywords if keyword in all_text)
        dev_score = sum(1 for keyword in dev_keywords if keyword in all_text)

        if process_score > dev_score:
            return "process_improvement"
        else:
            return "development"

def main():
    """Main entry point for the task generation automation."""
    # FORCE PRE-WORKFLOW ENFORCEMENT
    print("🚀 ENFORCING PRE-WORKFLOW REQUIREMENTS...")
    try:
        subprocess.run(
            [sys.executable, "scripts/pre_workflow_hook.py", "task generation automation", "implementer", "unit"],
            check=True,
        )
    except subprocess.CalledProcessError:
        print("❌ Pre-workflow enforcement failed - cannot proceed")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Automate task generation from PRDs and backlog items")
    parser.add_argument("--prd", help="Path to PRD file")
    parser.add_argument("--backlog-id", help="Backlog item ID (e.g., B-050)")
    parser.add_argument("--batch", help="Path to backlog file for batch processing")
    parser.add_argument(
        "--output", choices=["markdown", "json", "task-list"], default="task-list", help="Output format"
    )
    parser.add_argument("--output-file", help="Output file path")
    parser.add_argument("--preview", action="store_true", help="Preview generated tasks without saving")

    args = parser.parse_args()

    if not any([args.prd, args.backlog_id, args.batch]):
        parser.error("Must specify either --prd, --backlog-id, or --batch")

    try:
        tasks = []

        if args.prd:
            # Parse PRD
            prd_parser = PRDParser(args.prd)
            requirements = prd_parser.parse()

            task_generator = TaskTemplateGenerator()
            for requirement in requirements:
                task = task_generator.generate_task(requirement)
                tasks.append(task)

            # Sort tasks using backlog-style prioritization logic
            def calculate_task_priority(task):
                """Calculate priority score using backlog-style logic."""
                # Base priority mapping (from backlog lanes)
                priority_scores = {
                    "Critical": 8.0,  # P0 equivalent
                    "High": 6.0,  # P1 equivalent
                    "Medium": 4.0,  # P2 equivalent
                    "Low": 2.0,  # Below P2
                }

                base_score = priority_scores.get(task.priority, 3.0)

                # Adjust based on task characteristics (like backlog scoring)
                adjustments = 0

                # Boost for performance/security/critical tasks
                if any(keyword in task.name.lower() for keyword in ["performance", "security", "critical", "safety"]):
                    adjustments += 1.0

                # Boost for testing/validation tasks
                if any(keyword in task.name.lower() for keyword in ["test", "validate", "verify", "check"]):
                    adjustments += 0.5

                # Reduce for documentation/cleanup tasks
                if any(keyword in task.name.lower() for keyword in ["document", "cleanup", "archive"]):
                    adjustments -= 0.5

                return base_score + adjustments

            # Sort by calculated priority (highest first)
            tasks.sort(key=calculate_task_priority, reverse=True)

        elif args.backlog_id:
            # Parse backlog item
            backlog_parser = BacklogParser()
            requirement = backlog_parser.parse_backlog_item(args.backlog_id)

            if requirement:
                task_generator = TaskTemplateGenerator()
                task = task_generator.generate_task(requirement)
                tasks.append(task)
            else:
                print(f"Error: Backlog item {args.backlog_id} not found")
                sys.exit(1)

        elif args.batch:
            # Batch processing from backlog file
            backlog_parser = BacklogParser(args.batch)
            # This would need to be implemented for batch processing
            print("Batch processing not yet implemented")
            sys.exit(1)

        # Detect task type and generate appropriate output
        output_generator = TaskOutputGenerator()

        # Detect if this is a process improvement task
        if args.prd:
            prd_parser = PRDParser(args.prd)
            requirements = prd_parser.parse()
        elif args.backlog_id:
            # For backlog items, try to get the actual title from the backlog
            try:

                backlog_content = Path("000_core/000_backlog.md").read_text()

                # Look for the backlog item in the table format
                table_pattern = rf"\| {args.backlog_id} \| ([^|]+) \|"
                table_match = re.search(table_pattern, backlog_content)

                if table_match:
                    title = table_match.group(1).strip()
                else:
                    # Look for the backlog item in the P0/P1/P2 format
                    p_pattern = rf"- {args.backlog_id} — ([^\n]+)"
                    p_match = re.search(p_pattern, backlog_content)
                    title = p_match.group(1).strip() if p_match else f"Backlog Item {args.backlog_id}"

                requirements = [
                    TaskRequirement(
                        id=args.backlog_id,
                        title=title,
                        description=title,  # Use title as description for better detection
                        acceptance_criteria=[],
                        priority="Medium",
                        estimated_time="2-4 hours",
                        dependencies=[],
                    )
                ]
            except Exception:
                # Fallback to generic description
                requirements = [
                    TaskRequirement(
                        id=args.backlog_id,
                        title=f"Backlog Item {args.backlog_id}",
                        description="Process improvement task",
                        acceptance_criteria=[],
                        priority="Medium",
                        estimated_time="2-4 hours",
                        dependencies=[],
                    )
                ]
        else:
            requirements = []

        if args.output == "markdown":
            output = output_generator.generate_markdown(tasks[0])
        elif args.output == "json":
            output = output_generator.generate_json(tasks[0])
        else:  # task-list
            # Always use executable format for 003_process-task-list.md compatibility
            output = output_generator.generate_executable_task_list(tasks)

        # Handle output
        if args.preview:
            print("=== PREVIEW ===")
            print(output)
            print("=== END PREVIEW ===")
        elif args.output_file:
            with open(args.output_file, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Tasks written to {args.output_file}")
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
