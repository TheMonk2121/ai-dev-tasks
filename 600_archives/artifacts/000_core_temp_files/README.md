# 000_core Temporary Files Archive

## Overview
This directory contains temporary files that were previously stored in `000_core/` and have been archived to maintain a clean core directory structure.

## Archive Date
2025-08-20

## Files Archived

### PRD Files (Product Requirements Documents)
- `PRD-B-001-B-001.md` - Single doorway workflow PRD
- `PRD-B-001-Test-The-Single-Doorway-Workflow-With-Python-3-12.md` - Test PRD for single doorway workflow
- `PRD-B-050-Task-Generation-Automation.md` - Task generation automation PRD
- `PRD-B-084-Research-Based-Schema-Design.md` - Research-based schema design PRD
- `PRD-B-085-Code-Review-Performance-Reporting.md` - Code review performance reporting PRD
- `PRD-B-086-Test-Enhanced-Prd-Generation.md` - Enhanced PRD generation test PRD
- `PRD-B-087-Test-Enhanced-Task-Generation.md` - Enhanced task generation test PRD
- `PRD-B-088-Test-Improved-Slug-Generation.md` - Improved slug generation test PRD
- `PRD-B-089-Test-Performance-Testing-Optimized.md` - Performance testing optimization PRD
- `PRD-B-091-Test-001-Performance.md` - Performance test PRD
- `PRD-B-092-Final-Performance-Validation-Test.md` - Final performance validation test PRD
- `PRD-B-098-Lessons-Mining-From-Archived-PRDs.md` - Lessons mining from archived PRDs PRD
- `PRD-Chunk-Relationship-Visualization.md` - Chunk relationship visualization PRD

### TASKS Files (Generated Task Lists)
- `TASKS-B-001-B-001.md` - Tasks for single doorway workflow
- `TASKS-B-085-Code-Review-Performance-Reporting.md` - Tasks for code review performance reporting
- `TASKS-B-086-Test-Enhanced-Prd-Generation.md` - Tasks for enhanced PRD generation test
- `TASKS-B-087-Test-Enhanced-Task-Generation.md` - Tasks for enhanced task generation test
- `TASKS-B-088-Test-Improved-Slug-Generation.md` - Tasks for improved slug generation test
- `TASKS-B-089-Test-Performance-Testing-Optimized.md` - Tasks for performance testing optimization (v1)
- `TASKS-B-089-Test-Performance-Testing-Optimized-v2.md` - Tasks for performance testing optimization (v2)
- `TASKS-B-089-Test-Performance-Testing-Optimized-v3.md` - Tasks for performance testing optimization (v3)
- `TASKS-B-089-Test-Performance-Testing-Optimized-v4.md` - Tasks for performance testing optimization (v4)
- `TASKS-B-089-Test-Performance-Testing-Optimized-v5.md` - Tasks for performance testing optimization (v5)
- `TASKS-B-089-Test-Performance-Testing-Optimized-v6.md` - Tasks for performance testing optimization (v6)
- `TASKS-B-089-Test-Performance-Testing-Optimized-v7.md` - Tasks for performance testing optimization (v7)
- `TASKS-B-091-Test-001-Performance.md` - Tasks for performance test
- `TASKS-B-092-Final-Performance-Validation-Test.md` - Tasks for final performance validation test

### RUN Files (Execution Records)
- `RUN-B-001-B-001.md` - Execution record for single doorway workflow
- `RUN-B-001-B-001_2025-08-19.md` - Execution record for single doorway workflow (dated)
- `RUN-B-086-Test-Enhanced-Prd-Generation_2025-08-19.md` - Execution record for enhanced PRD generation test
- `RUN-B-087-Test-Enhanced-Task-Generation_2025-08-19.md` - Execution record for enhanced task generation test
- `RUN-B-088-Test-Improved-Slug-Generation_2025-08-19.md` - Execution record for improved slug generation test
- `RUN-B-091-Test-001-Performance.md` - Execution record for performance test
- `RUN-B-092-Final-Performance-Validation-Test.md` - Execution record for final performance validation test

### Backup Files
- `004_development-roadmap.md.backup` - Backup of development roadmap file

## Archive Rationale
These files were archived because:

1. **Temporary Nature**: PRD, TASKS, and RUN files are generated artifacts from the AI development workflow
2. **Core Directory Cleanup**: The `000_core/` directory should contain only essential workflow documentation
3. **Root Directory Cleanup**: Generated PRDs in the root directory should be archived to maintain clean project structure
4. **Archive Consolidation**: All PRDs from various archive locations have been consolidated into a single artifacts folder
5. **Historical Preservation**: These files contain valuable metadata about past development work
6. **Reference Value**: Future development may benefit from reviewing these patterns and approaches

## Metadata & Analysis

For detailed analysis of development patterns, metadata, and lessons learned from these archived files, see:
**[Development Patterns & Archived Metadata Analysis](../400_guides/400_development-patterns.md)**

This guide contains comprehensive analysis of:
- Development patterns and evolution
- Implementation metadata and success metrics
- Key decisions and trade-offs
- Technical architecture patterns
- Lessons learned and best practices

## Current 000_core Structure
After archiving, `000_core/` now contains only essential workflow documentation:
- `README.md` - Core directory overview
- `000_backlog.md` - Current backlog and priorities
- `001_create-prd.md` - PRD creation workflow
- `002_generate-tasks.md` - Task generation workflow
- `003_process-task-list.md` - Task execution workflow
- `004_development-roadmap.md` - Development roadmap

## Recovery Information
If needed, these files can be referenced for:
- Historical development patterns
- Backlog item completion status
- Performance testing approaches
- Workflow execution examples

## Additional Metadata Files
- **Test Reports**: `600_archives/artifacts/test_runs/` contains JSON test reports from 2025-08-13
- **Backlog Status**: `600_archives/backlog_items/B-001/status.json` contains backlog item tracking metadata
- **Test Context**: `600_archives/artifacts/test_runs/test_context.db` contains test execution context

## Archival Metadata Format
Many files contain structured archival metadata in HTML comments:
```html
<!-- ARCHIVAL_METADATA -->
<!-- completion_date: YYYY-MM-DD -->
<!-- backlog_id: B-XXX -->
<!-- implementation_notes: Detailed implementation summary -->
<!-- lessons_applied: ["lesson1", "lesson2"] -->
<!-- reference_cards: ["card1", "card2"] -->
<!-- key_decisions: ["decision1", "decision2"] -->
<!-- trade_offs: ["tradeoff1", "tradeoff2"] -->
<!-- success_metrics: ["metric1", "metric2"] -->
<!-- ARCHIVAL_METADATA -->
```

This metadata provides:
- **Implementation Status**: Completion dates and success metrics
- **Technical Decisions**: Key architectural and design choices
- **Lessons Learned**: Applied knowledge and best practices
- **Reference Links**: Connections to related documentation
- **Trade-offs**: Decision rationale and alternatives considered
