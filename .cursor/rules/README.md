# Cursor AI Rules System

This directory contains Cursor AI rules extracted from the core templates (`001_PRD_TEMPLATE.md`, `002_TASK-LIST_TEMPLATE.md`, `003_EXECUTION_TEMPLATE.md`) to ensure consistent AI behavior aligned with the project's AI development ecosystem.

## Rule Organization

### Project Rules (`project/`)
AI development ecosystem specific rules:
- **`memory_system.mdc`**: Memory rehydration protocols and LTST integration
- **`ragchecker_baseline.mdc`**: RAGChecker performance baseline enforcement
- **`multi_agent_patterns.mdc`**: Multi-agent role patterns and workflows
- **`documentation_governance.mdc`**: 400_ guide integration and documentation standards

### Repository Rules (`repo/`)
General repository governance rules:
- **`code_quality.mdc`**: Python code quality standards and best practices
- **`testing_standards.mdc`**: Testing requirements and quality gates
- **`ci_cd.mdc`**: CI/CD standards and automated quality gates

### Workflow Rules (`workflow/`)
Cross-cutting workflow patterns:
- **`task_management.mdc`**: Task generation and management protocols
- **`execution_patterns.mdc`**: Execution workflow and quality standards

### Configuration Rules (`config/`)
Configuration and database standards:
- **`database_standards.mdc`**: Database and configuration management
- **`uv_management.mdc`**: UV package management and environment standards

## Rule Application

Rules are applied based on:
- **File patterns** (`globs`): Which files the rule applies to
- **Always apply** (`alwaysApply`): Whether the rule applies to all matching files
- **Description**: What the rule enforces

## Key Principles

1. **Memory-First Development**: Always run memory rehydration before major tasks
2. **RAGChecker Baseline**: No regressions allowed; improve recall while maintaining precision
3. **UV Package Management**: Use `uv run python scripts/` for all Python execution
4. **Documentation Governance**: Fold content into existing 400_ guides using anchors
5. **Multi-Agent Patterns**: Follow role-specific guidelines (Planner/Implementer/Researcher/Coder)
6. **Quality Gates**: Enforce comprehensive testing and validation standards

## Usage

These rules automatically guide Cursor AI behavior when working with files matching the specified patterns. They ensure consistent adherence to the project's sophisticated AI development ecosystem while maintaining standard repository governance practices.
