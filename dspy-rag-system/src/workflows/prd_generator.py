#!/usr/bin/env python3
"""
Performance-enabled PRD generator for 001_create-prd workflow.
Integrates performance collection with PRD generation process.
"""

import logging
import os
import re
from typing import Any

try:
    from ..monitoring.performance_collector import PerformanceTracker
    from ..monitoring.performance_storage import store_workflow_data
except ImportError:
    # Fallback for direct execution
    from monitoring.performance_collector import PerformanceTracker

    store_workflow_data = None

logger = logging.getLogger(__name__)


class PRDGenerator:
    """Performance-enabled PRD generator"""

    def __init__(self, template_path: str = "000_core/001_create-prd-TEMPLATE.md"):
        self.template_path = template_path
        self.tracker = PerformanceTracker()
        self.workflow_data = None

    def generate_prd(
        self,
        backlog_item_id: str,
        backlog_data: dict[str, Any],
        output_path: str | None = None,
    ) -> tuple[str, dict[str, Any]]:
        """Generate PRD with performance tracking"""

        # Start performance tracking
        with self.tracker.track_workflow(
            backlog_item_id=backlog_item_id,
            prd_file_path=output_path or f"artifacts/prds/PRD-{backlog_item_id}.md",
            task_count=0,
        ) as workflow:

            try:
                # Load and process template
                with self.tracker.track_template_processing(
                    template_type="hybrid",
                    complexity_score=1.0,
                ):
                    template_content = self._load_template()
                    template_sections = self._parse_template_sections(template_content)

                # Integrate context from backlog
                with self.tracker.track_context_integration(
                    context_source="backlog",
                    context_size=len(str(backlog_data)),
                ):
                    context_data = self._extract_context_data(backlog_data)

                # Generate PRD content
                prd_content = self._generate_prd_content(template_sections, context_data, backlog_item_id)

                # Validate PRD
                with self.tracker.track_validation(
                    validation_rules=["acceptance_criteria", "quality_gates"],
                    quality_gates=3,
                ):
                    self._validate_prd(prd_content)

                # Save PRD
                if output_path:
                    self._save_prd(prd_content, output_path)

                # Get performance analysis
                analysis = workflow.get_analysis()
                performance_summary = self._generate_performance_summary(analysis)

                # Apply quality gates if analysis is available
                if analysis:
                    try:
                        from ..monitoring.quality_gates import get_quality_summary, validate_workflow_quality
                    except ImportError:
                        # Fallback for direct execution
                        from monitoring.quality_gates import get_quality_summary, validate_workflow_quality

                    quality_result = validate_workflow_quality(analysis)
                    quality_summary = get_quality_summary(analysis)

                    # Add quality gate results to analysis
                    analysis["quality_gates"] = quality_result
                    analysis["quality_summary"] = quality_summary

                    # Log quality gate results
                    logger.info(
                        f"Quality gates: {len(quality_result.get('passed_gates', []))}/{len(quality_result.get('total_gates', []))} passed"
                    )

                # Add performance summary to PRD
                final_prd = self._add_performance_summary(prd_content, performance_summary)

                return final_prd, analysis or {}

            except Exception as e:
                logger.error(f"Failed to generate PRD: {e}")
                # Error handling is done by context manager
                raise

    def _load_template(self) -> str:
        """Load template content"""
        try:
            with open(self.template_path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Template not found: {self.template_path}")

    def _parse_template_sections(self, template_content: str) -> dict[str, str]:
        """Parse template into sections"""
        sections = {}

        # Extract template sections
        section_pattern = r"### \*\*(\d+\. .*?)\*\*\n(.*?)(?=### \*\*\d+\.|$)"
        matches = re.findall(section_pattern, template_content, re.DOTALL)

        for title, content in matches:
            sections[title] = content.strip()

        return sections

    def _extract_context_data(self, backlog_data: dict[str, Any]) -> dict[str, Any]:
        """Extract context data from backlog item"""
        context = {
            "backlog_item_id": backlog_data.get("id"),
            "title": backlog_data.get("title", ""),
            "description": backlog_data.get("description", ""),
            "points": backlog_data.get("points", 0),
            "score_total": backlog_data.get("score_total", 0.0),
            "dependencies": backlog_data.get("dependencies", []),
            "metadata": backlog_data.get("metadata", {}),
        }

        return context

    def _generate_prd_content(
        self,
        template_sections: dict[str, str],
        context_data: dict[str, Any],
        backlog_item_id: str,
    ) -> str:
        """Generate PRD content from template and context"""

        # Start with PRD header
        prd_content = f"""# Product Requirements Document: {context_data['title']}

> ⚠️**Auto-Skip Note**> This PRD was generated because either `points≥5` or `score_total<3.0`.
> Remove this banner if you manually forced PRD creation.

## 0. Project Context & Implementation Guide

### Current Tech Stack
- **Backend**: Python 3.12, FastAPI, PostgreSQL, pgvector
- **Frontend**: NiceGUI, HTML/CSS/JavaScript
- **Infrastructure**: Docker, Local-first development
- **Development**: Poetry, pytest, pre-commit, Ruff, Pyright

### Repository Layout
```
ai-dev-tasks/
├── 000_core/              # Core workflow templates and backlog
├── 100_memory/            # Memory context and LTST system
├── 200_setup/             # Configuration and setup
├── 300_examples/          # Example implementations
├── 400_guides/            # Development guides and documentation
├── 500_research/          # Research and analysis
├── 600_archives/          # Legacy and archived content
├── dspy-rag-system/       # Main application code
├── artifacts/             # Generated artifacts (PRDs, tasks, etc.)
└── scripts/               # Utility scripts and automation
```

### Development Patterns
- **Models**: `dspy-rag-system/src/models/` - Data models and business logic
- **Services**: `dspy-rag-system/src/services/` - Business services and utilities
- **Monitoring**: `dspy-rag-system/src/monitoring/` - Performance monitoring and metrics
- **Workflows**: `dspy-rag-system/src/workflows/` - Workflow automation and templates

### Local Development
```bash
# Setup
cd dspy-rag-system
poetry install
poetry run pre-commit install

# Run tests
poetry run pytest

# Start development server
poetry run python src/main.py
```

### Common Tasks
- **Add new workflow**: Create template in `000_core/`, add generator in `src/workflows/`
- **Add new monitoring**: Add collector in `src/monitoring/`, update schema
- **Add new service**: Create service in `src/services/`, add tests
- **Add new model**: Create model in `src/models/`, add database migration

"""

        # Generate sections based on context
        sections = self._generate_sections(context_data)

        for section_title, section_content in sections.items():
            prd_content += f"\n## {section_title}\n\n{section_content}\n"

        return prd_content

    def _generate_sections(self, context_data: dict[str, Any]) -> dict[str, str]:
        """Generate PRD sections based on context data"""
        sections = {}

        # Section 1: Problem Statement
        sections["1. Problem Statement"] = self._generate_problem_statement(context_data)

        # Section 2: Solution Overview
        sections["2. Solution Overview"] = self._generate_solution_overview(context_data)

        # Section 3: Acceptance Criteria
        sections["3. Acceptance Criteria"] = self._generate_acceptance_criteria(context_data)

        # Section 4: Technical Approach
        sections["4. Technical Approach"] = self._generate_technical_approach(context_data)

        # Section 5: Risks and Mitigation
        sections["5. Risks and Mitigation"] = self._generate_risks_mitigation(context_data)

        # Section 6: Testing Strategy
        sections["6. Testing Strategy"] = self._generate_testing_strategy(context_data)

        # Section 7: Implementation Plan
        sections["7. Implementation Plan"] = self._generate_implementation_plan(context_data)

        return sections

    def _generate_problem_statement(self, context_data: dict[str, Any]) -> str:
        """Generate problem statement section"""
        title = context_data.get("title", "Unknown")
        description = context_data.get("description", "")

        return f"""### What's broken?
{description}

### Why does it matter?
This backlog item addresses a critical need in the AI development ecosystem workflow.

### What's the opportunity?
Successfully implementing {title} will improve workflow efficiency and developer productivity."""

    def _generate_solution_overview(self, context_data: dict[str, Any]) -> str:
        """Generate solution overview section"""
        title = context_data.get("title", "Unknown")

        return f"""### What are we building?
{title}

### How does it work?
The solution will integrate with existing workflow components and follow established patterns.

### What are the key features?
- Feature 1: [To be defined based on specific backlog item]
- Feature 2: [To be defined based on specific backlog item]
- Feature 3: [To be defined based on specific backlog item]"""

    def _generate_acceptance_criteria(self, context_data: dict[str, Any]) -> str:
        """Generate acceptance criteria section"""
        # Use points in the generated content
        points = context_data.get("points", 0)
        complexity = "High" if points >= 5 else "Medium" if points >= 3 else "Low"

        return f"""### How do we know it's done?
- [ ] All acceptance criteria are met
- [ ] Performance requirements are satisfied
- [ ] Integration tests pass
- [ ] Documentation is updated

### What does success look like?
- Workflow completes successfully within performance thresholds
- All quality gates pass
- No regressions in existing functionality
- Complexity level: {complexity} ({points} points)

### What are the quality gates?
- [ ] Code review completed
- [ ] Tests pass with >90% coverage
- [ ] Performance benchmarks met
- [ ] Documentation updated"""

    def _generate_technical_approach(self, context_data: dict[str, Any]) -> str:
        """Generate technical approach section"""
        return """### What technology?
- Python 3.12 for backend logic
- PostgreSQL with pgvector for data storage
- NiceGUI for dashboard interface
- Performance monitoring with custom collectors

### How does it integrate?
- Integrates with existing LTST memory system
- Connects to performance monitoring infrastructure
- Follows established workflow patterns

### What are the constraints?
- Must maintain backward compatibility
- Performance overhead must be <5%
- Must work in local-first environment"""

    def _generate_risks_mitigation(self, context_data: dict[str, Any]) -> str:
        """Generate risks and mitigation section"""
        return """### What could go wrong?
- **Risk 1**: Performance impact on existing workflows
- **Risk 2**: Integration complexity with existing systems
- **Risk 3**: Data migration challenges

### How do we handle it?
- **Mitigation 1**: Comprehensive performance testing and monitoring
- **Mitigation 2**: Incremental integration with feature flags
- **Mitigation 3**: Thorough testing and rollback procedures

### What are the unknowns?
- Exact performance impact on different workflow types
- Integration complexity with specific components
- User adoption and feedback"""

    def _generate_testing_strategy(self, context_data: dict[str, Any]) -> str:
        """Generate testing strategy section"""
        return """### What needs testing?
- Performance impact on workflow execution
- Integration with existing systems
- Data consistency and integrity
- Error handling and recovery

### How do we test it?
- Unit tests for individual components
- Integration tests for workflow end-to-end
- Performance benchmarks and load testing
- User acceptance testing

### What's the coverage target?
- >90% code coverage for new functionality
- 100% coverage for critical paths
- Performance regression testing"""

    def _generate_implementation_plan(self, context_data: dict[str, Any]) -> str:
        """Generate implementation plan section"""
        points = context_data.get("points", 0)
        estimated_hours = points * 2  # Rough estimate: 2 hours per point

        return f"""### What are the phases?
1. **Phase 1**: Design and planning ({estimated_hours//3} hours)
2. **Phase 2**: Implementation ({estimated_hours//2} hours)
3. **Phase 3**: Testing and validation ({estimated_hours//6} hours)

### What are the dependencies?
- Existing workflow infrastructure
- Performance monitoring system
- Database schema updates

### What's the timeline?
- Total estimated time: {estimated_hours} hours
- Dependencies: {', '.join(context_data.get('dependencies', []))}
- Target completion: Based on priority and resource availability"""

    def _validate_prd(self, prd_content: str) -> dict[str, Any]:
        """Validate PRD content"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        # Check for required sections
        required_sections = [
            "Problem Statement",
            "Solution Overview",
            "Acceptance Criteria",
            "Technical Approach",
            "Risks and Mitigation",
            "Testing Strategy",
            "Implementation Plan",
        ]

        for section in required_sections:
            if section not in prd_content:
                validation_result["errors"].append(f"Missing section: {section}")
                validation_result["valid"] = False

        # Check for placeholder content
        placeholder_patterns = [
            r"\[.*?\]",  # [placeholder] content
            r"To be defined",
            r"Unknown",
        ]

        for pattern in placeholder_patterns:
            matches = re.findall(pattern, prd_content)
            if matches:
                validation_result["warnings"].append(f"Found placeholder content: {matches[:3]}")

        return validation_result

    def _save_prd(self, prd_content: str, output_path: str):
        """Save PRD to file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(prd_content)

        logger.info(f"PRD saved to: {output_path}")

    def _generate_performance_summary(self, analysis: dict[str, Any] | None) -> dict[str, Any]:
        """Generate performance summary for PRD"""
        if not analysis:
            return {
                "workflow_id": "N/A",
                "total_duration_ms": 0.0,
                "performance_score": 0.0,
                "success": False,
                "error_count": 0,
                "bottlenecks_count": 0,
                "warnings_count": 0,
                "recommendations_count": 0,
                "collection_points": {},
            }

        # Extract collection point durations
        collection_points = {}
        if "collection_points" in analysis:
            for point in analysis["collection_points"]:
                point_name = point["collection_point"].replace("_", " ").title()
                collection_points[point_name] = point.get("duration_ms", 0.0)

        # Extract quality gate information
        quality_summary = analysis.get("quality_summary", {})
        quality_gates = analysis.get("quality_gates", {})

        # Use quality_gates in the return value
        quality_gates_passed = len(quality_gates.get("passed_gates", []))
        quality_gates_total = len(quality_gates.get("total_gates", []))

        return {
            "workflow_id": analysis.get("workflow_id", "N/A"),
            "total_duration_ms": analysis.get("total_duration_ms", 0.0),
            "performance_score": analysis.get("performance_score", 0.0),
            "success": analysis.get("success", False),
            "error_count": analysis.get("error_count", 0),
            "bottlenecks_count": len(analysis.get("bottlenecks", [])),
            "warnings_count": len(analysis.get("warnings", [])),
            "recommendations_count": len(analysis.get("recommendations", [])),
            "collection_points": collection_points,
            "quality_status": quality_summary.get("overall_status", "N/A"),
            "quality_passed": quality_gates_passed,
            "quality_total": quality_gates_total,
            "quality_score": (quality_gates_passed / max(quality_gates_total, 1)) * 100,
        }

    def _add_performance_summary(self, prd_content: str, performance_summary: dict[str, Any]) -> str:
        """Add performance summary to PRD"""
        summary_template = f"""

---

## **Performance Metrics Summary**

> 📊 **Workflow Performance Data**
> - **Workflow ID**: `{performance_summary['workflow_id']}`
> - **Total Duration**: `{performance_summary['total_duration_ms']:.1f}ms`
> - **Performance Score**: `{performance_summary['performance_score']:.1f}/100`
> - **Success**: `{performance_summary['success']}`
> - **Error Count**: `{performance_summary['error_count']}`

> 🔍 **Performance Analysis**
> - **Bottlenecks**: `{performance_summary['bottlenecks_count']}`
> - **Warnings**: `{performance_summary['warnings_count']}`
> - **Recommendations**: `{performance_summary['recommendations_count']}`

> 🚦 **Quality Gates**
> - **Overall Status**: `{performance_summary.get('quality_status', 'N/A')}`
> - **Gates Passed**: `{performance_summary.get('quality_passed', 0)}/{performance_summary.get('quality_total', 0)}`
> - **Quality Score**: `{performance_summary.get('quality_score', 0):.1f}%`

> 📈 **Collection Points**
"""

        # Add collection point details
        for point_name, duration in performance_summary["collection_points"].items():
            summary_template += f"> - **{point_name}**: `{duration:.1f}ms`\n"

        return prd_content + summary_template


# Convenience function for easy integration
def generate_prd_with_performance(
    backlog_item_id: str,
    backlog_data: dict[str, Any],
    output_path: str | None = None,
) -> tuple[str, dict[str, Any]]:
    """Generate PRD with performance tracking"""
    generator = PRDGenerator()
    return generator.generate_prd(backlog_item_id, backlog_data, output_path)
