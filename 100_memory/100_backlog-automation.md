<!-- ANCHOR_KEY: backlog-automation -->
<!-- ANCHOR_PRIORITY: 15 -->

<!-- ROLE_PINS: ["planner", "implementer"] -->

# Backlog Automation

generate_prd: |
  Use @000_core/001_create-prd.md with backlog_id=B-XXX
  Include all metadata from backlog table
  Skip PRD generation for items with points<5 AND score_total>=3.0
  Generate PRD for items with points>=5 OR score_total<3.0

```text

## Update Status

{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: Quick summary of Update Status.

- **read when**: When you need a fast orientation or before using this file in a workflow.

- **do next**: Scan the headings below and follow any 'Quick Start' or 'Usage' sections.

```yaml
update_status: |
  Mark backlog item as done
  Update effort estimates based on actual time

```text

### Batch Operations

```yaml
batch_operations: |
  Update multiple items at once
  Recalculate priorities based on dependencies

```text

### Dependency Check

```yaml
dependency_check: |
  Verify all dependencies are met
  Block items with unmet dependencies

```text

### Points Calculation

```yaml
points_calculation: |
  Calculate total effort for sprint
  Ensure points fit within capacity

```text

### Default Executor

```yaml
default_executor: |
  If present, the specified file is auto-loaded before task execution.
  Example: <!-- default_executor: 000_core/003_process-task-list.md -->

```text

## Integration with Workflow Files

### 000_core/001_create-prd.md

- Parse backlog ID (B-001, B-002, etc.)

- Extract metadata from backlog table

- Apply PRD decision rule (skip for points<5 AND score≥3.0)

- Use AI-BACKLOG-META commands for automated PRD generation

### 000_core/002_generate-tasks.md

- Consider backlog prioritization and impact estimates

- Parse backlog metadata (points, dependencies, tech footprint)

- Parse PRD or backlog directly based on PRD decision rule

- Use points-based effort estimation for task sizing

- Track backlog status updates as tasks are completed

### 000_core/003_process-task-list.md

- Consider backlog priorities for task selection

- Parse backlog table for status and dependency information

- Check backlog dependencies before starting tasks

- Update backlog status after completion

## Usage Examples

### Starting a New Feature

```bash

# AI agent reads backlog and creates PRD

Use @000_core/001_create-prd.md with backlog_id=B-001

```text

## Updating Progress

```bash

# AI agent updates backlog status

Update backlog item B-001 status to "done"

```text

## Sprint Planning

```bash

# AI agent selects next items

Parse backlog for top 3 todo items by priority

```text

## Status Tracking

### Status Definitions

- `todo`: Not started

- `in-progress`: Currently being worked on

- `✅ done`: Completed (moved to "Completed Items" section)

- `blocked`: Cannot start due to dependencies

### Update Triggers

- **Task Completion**: Mark item as done

- **New Discovery**: Add new requirements to backlog

- **Effort Adjustment**: Update points based on actual time

- **Priority Change**: Recalculate based on new information

- **Timestamp Updates**: Update *Last Updated*and add*Previously Updated*for history

## Benefits

### For AI Agents

- **Structured Data**: Easy to parse and understand

- **Consistent Format**: Predictable metadata structure

- **Automated Updates**: Reduce manual intervention

- **Dependency Management**: Clear prerequisite tracking

### For Developers

- **Reduced Overhead**: Less manual backlog maintenance

- **Better Prioritization**: Data-driven decision making

- **Consistent Workflow**: Standardized process across projects

- **Progress Tracking**: Clear visibility into development status

## Implementation Notes

### Parsing Rules

- Use regex to extract table rows

- Parse HTML comments for metadata

- Handle missing or malformed data gracefully

- Validate dependencies before processing

### Command Execution

- Execute AI-BACKLOG-META commands in order

- Rollback changes if any step fails

- Log all operations for audit trail

- Handle errors gracefully

### Error Handling

- Skip invalid entries

- Use fallback values when metadata is missing

- Report parsing errors clearly

- Maintain backward compatibility

## n8n Backlog Scrubber Workflow ✅ **IMPLEMENTED**### Overview

The n8n backlog scrubber automatically calculates and updates scoring metadata in the backlog file. This workflow:

1.**Reads**the backlog.md file
2.**Parses**scoring metadata from HTML comments
3.**Calculates**new scores using the formula: `(BV + TC + RR + LE) / Effort`
4.**Updates**the `<!--score_total: X.X-->` comments
5.**Writes**the updated file back

### Implementation Status ✅**COMPLETED**

- *Location**: `dspy-rag-system/src/n8n_workflows/backlog_scrubber.py`
- *Webhook Server**: `dspy-rag-system/src/n8n_workflows/backlog_webhook.py`
- *Documentation**: `400_guides/400_n8n-backlog-scrubber-guide.md`
- *Tests**: `dspy-rag-system/tests/test_backlog_scrubber.py`

### Features Implemented

#### Core Functionality

- ✅ **Automated Score Calculation**: Python-based implementation with robust parsing

- ✅ **Webhook Integration**: RESTful API for n8n workflows

- ✅ **Validation & Error Handling**: Comprehensive input validation and error recovery

- ✅ **Backup Protection**: Automatic file backups before updates

- ✅ **Statistics & Monitoring**: Real-time statistics and health checks

#### n8n Integration

- ✅ **Webhook Endpoint**: `/webhook/backlog-scrubber` for triggering scrubs

- ✅ **Health Checks**: `/health` endpoint for monitoring

- ✅ **Statistics**: `/stats` endpoint for metrics

- ✅ **Dry Run Support**: Test mode for safe operations

#### Advanced Features

- ✅ **Comprehensive Testing**: 20 unit and integration tests

- ✅ **Demo Script**: Complete demonstration of all features

- ✅ **Documentation**: Complete setup and usage guide

- ✅ **Production Ready**: Error handling, logging, and monitoring

### Usage

#### Standalone Usage

```bash

# Run the backlog scrubber directly

python3 src/n8n_workflows/backlog_scrubber.py

# With custom backlog path

python3 src/n8n_workflows/backlog_scrubber.py --backlog-path /path/to/backlog.md

# Dry run (show changes without writing)

python3 src/n8n_workflows/backlog_scrubber.py --dry-run

```text

## Webhook Server

```bash

# Start the webhook server

python3 src/n8n_workflows/backlog_webhook.py

# With custom configuration

python3 src/n8n_workflows/backlog_webhook.py --host 0.0.0.0 --port 5001 --debug

```text

## n8n Workflow Integration

1. **Webhook Trigger**: Create webhook trigger in n8n
2. **HTTP Request**: Add HTTP request node to call backlog scrubber
3. **Function Node**: Add function node to process response
4. **Schedule**: Set up manual or scheduled triggers

### Benefits

- ✅ **Automatic Scoring**: No manual calculation needed

- ✅ **Consistent Updates**: All scores use same formula

- ✅ **Error Prevention**: Validates data before updating

- ✅ **Audit Trail**: Logs all changes for review

- ✅ **Webhook Integration**: Trigger from n8n workflows

- ✅ **Health Monitoring**: Real-time status checks

- ✅ **Backup Protection**: Automatic file backups

- ✅ **Validation**: Comprehensive score validation

### Integration with AI Workflow

The AI agents can now:

1. ✅ **Read**pre-calculated scores from `<!--score_total: X.X-->`
2. ✅**Prioritize**items based on scores
3. ✅**Fall back**to human priority tags when scores missing
4. ✅**Trigger**re-scoring when priorities change

This creates a**self-maintaining backlog** that stays prioritized without manual intervention.
