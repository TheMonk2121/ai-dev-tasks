# AI-BACKLOG-META: Automated Backlog Management

This document describes the AI-BACKLOG-META system for automated backlog management and how it integrates with the AI development workflow.

## Overview

The AI-BACKLOG-META system provides machine-readable commands and metadata that AI agents can parse to automate backlog management tasks. This reduces manual work and ensures consistency across the development workflow.

## Backlog Table Format

The backlog uses a structured Markdown table with the following fields:

| Field | Description | Example |
|-------|-------------|---------|
| `ID` | Unique identifier | `B-001`, `B-002` |
| `Title` | Feature name | `Real-time Mission Dashboard` |
| `🔥P` | Human priority | `🔥`, `⭐`, `📈`, `🔧` |
| `🎯Points` | Effort estimate | `1`, `2`, `3`, `5`, `8`, `13` |
| `Status` | Current state | `todo`, `in-progress`, `done` |
| `Problem/Outcome` | What it solves | `Need live visibility into AI task execution` |
| `Tech Footprint` | Technologies involved | `PostgreSQL + Flask UI` |
| `Dependencies` | Prerequisites | `None`, `Event ledger` |

## AI-BACKLOG-META Commands

### Parse Backlog
```yaml
parse_backlog: |
  Extract all todo items with their metadata
  Return sorted list by priority and score
```

### Generate PRD
```yaml
generate_prd: |
  Use @01_create-prd.md with backlog_id=B-XXX
  Include all metadata from backlog table
```

### Update Status
```yaml
update_status: |
  Mark backlog item as done
  Update effort estimates based on actual time
```

### Batch Operations
```yaml
batch_operations: |
  Update multiple items at once
  Recalculate priorities based on dependencies
```

### Dependency Check
```yaml
dependency_check: |
  Verify all dependencies are met
  Block items with unmet dependencies
```

### Points Calculation
```yaml
points_calculation: |
  Calculate total effort for sprint
  Ensure points fit within capacity
```

## Integration with Workflow Files

### 01_create-prd.md
- Parse backlog ID (B-001, B-002, etc.)
- Extract metadata from backlog table
- Use AI-BACKLOG-META commands for automated PRD generation

### 02_generate-tasks.md
- Consider backlog prioritization and impact estimates
- Parse backlog metadata (points, dependencies, tech footprint)
- Use points-based effort estimation for task sizing
- Track backlog status updates as tasks are completed

### 03_process-task-list.md
- Consider backlog priorities for task selection
- Parse backlog table for status and dependency information
- Check backlog dependencies before starting tasks
- Update backlog status after completion

## Usage Examples

### Starting a New Feature
```bash
# AI agent reads backlog and creates PRD
Use @01_create-prd.md with backlog_id=B-001
```

### Updating Progress
```bash
# AI agent updates backlog status
Update backlog item B-001 status to "done"
```

### Sprint Planning
```bash
# AI agent selects next items
Parse backlog for top 3 todo items by priority
```

## Status Tracking

### Status Definitions
- `todo`: Not started
- `in-progress`: Currently being worked on
- `done`: Completed
- `blocked`: Cannot start due to dependencies

### Update Triggers
- **Task Completion**: Mark item as done
- **New Discovery**: Add new requirements to backlog
- **Effort Adjustment**: Update points based on actual time
- **Priority Change**: Recalculate based on new information

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

## n8n Backlog Scrubber Workflow

### Overview
The n8n backlog scrubber automatically calculates and updates scoring metadata in the backlog file. This workflow:

1. **Reads** the backlog.md file
2. **Parses** scoring metadata from HTML comments
3. **Calculates** new scores using the formula: `(BV + TC + RR + LE) / Effort`
4. **Updates** the `<!--score_total: X.X-->` comments
5. **Writes** the updated file back

### Setup Instructions

#### 1. Create n8n Workflow
Create a new workflow in n8n with the following nodes:

**Node 1: HTTP Request (Read File)**
- Method: GET
- URL: `file:///path/to/ai-dev-tasks/00_backlog.md`
- Response Format: Text

**Node 2: Function (Parse and Calculate)**
```javascript
// Parse scoring metadata and calculate totals
const raw = $input.all()[0].json;
const updated = raw.replace(/<!--score: (.*?)-->/g, (match, json) => {
  try {
    const o = JSON.parse(json);
    const total = ((o.bv + o.tc + o.rr + o.le) / o.effort).toFixed(1);
    return `${match}\n<!--score_total: ${total}-->`;
  } catch (e) {
    return match; // Keep original if parsing fails
  }
});
return { updatedMarkdown: updated };
```

**Node 3: HTTP Request (Write File)**
- Method: POST
- URL: `file:///path/to/ai-dev-tasks/00_backlog.md`
- Body: `{{ $json.updatedMarkdown }}`

#### 2. Schedule Execution
- **Manual Trigger**: Run when adding new items
- **Scheduled**: Run weekly to recalculate scores
- **Webhook**: Trigger from other workflows

#### 3. Error Handling
- Validate JSON parsing
- Handle missing metadata gracefully
- Log calculation errors
- Rollback on failure

### Benefits
- **Automatic Scoring**: No manual calculation needed
- **Consistent Updates**: All scores use same formula
- **Error Prevention**: Validates data before updating
- **Audit Trail**: Logs all changes for review

### Integration with AI Workflow
The AI agents can now:
1. **Read** pre-calculated scores from `<!--score_total: X.X-->`
2. **Prioritize** items based on scores
3. **Fall back** to human priority tags when scores missing
4. **Trigger** re-scoring when priorities change

This creates a **self-maintaining backlog** that stays prioritized without manual intervention. 