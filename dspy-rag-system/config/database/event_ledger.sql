-- Event Ledger Schema for n8n Workflow Integration
-- This schema enables automated task execution and event-driven workflows

-- Event ledger table for tracking system events
CREATE TABLE IF NOT EXISTS event_ledger (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Task execution table for n8n workflow tasks
CREATE TABLE IF NOT EXISTS task_executions (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL,
    workflow_id VARCHAR(255),
    task_type VARCHAR(100) NOT NULL,
    parameters JSONB DEFAULT '{}',
    status VARCHAR(50) DEFAULT 'pending',
    result JSONB,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflow definitions table
CREATE TABLE IF NOT EXISTS workflow_definitions (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    definition JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflow execution history
CREATE TABLE IF NOT EXISTS workflow_executions (
    id SERIAL PRIMARY KEY,
    workflow_id VARCHAR(255) NOT NULL,
    execution_id VARCHAR(255) UNIQUE NOT NULL,
    status VARCHAR(50) DEFAULT 'running',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    result JSONB,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_event_ledger_event_type ON event_ledger(event_type);
CREATE INDEX IF NOT EXISTS idx_event_ledger_status ON event_ledger(status);
CREATE INDEX IF NOT EXISTS idx_event_ledger_created_at ON event_ledger(created_at);
CREATE INDEX IF NOT EXISTS idx_task_executions_task_id ON task_executions(task_id);
CREATE INDEX IF NOT EXISTS idx_task_executions_status ON task_executions(status);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_workflow_id ON workflow_executions(workflow_id);
CREATE INDEX IF NOT EXISTS idx_workflow_executions_status ON workflow_executions(status);

-- Create triggers for updated_at
CREATE TRIGGER update_task_executions_updated_at BEFORE UPDATE ON task_executions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflow_definitions_updated_at BEFORE UPDATE ON workflow_definitions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default workflow definitions
INSERT INTO workflow_definitions (workflow_id, name, description, definition) VALUES
(
    'backlog-scrubber',
    'Backlog Scrubber Workflow',
    'Automatically calculates and updates scoring metadata in the backlog file',
    '{
        "nodes": [
            {
                "id": "read-backlog",
                "type": "httpRequest",
                "parameters": {
                    "method": "GET",
                    "url": "file:///path/to/ai-dev-tasks/000_backlog.md"
                }
            },
            {
                "id": "parse-calculate",
                "type": "function",
                "parameters": {
                    "functionCode": "// Parse scoring metadata and calculate totals"
                }
            },
            {
                "id": "write-backlog",
                "type": "httpRequest",
                "parameters": {
                    "method": "POST",
                    "url": "file:///path/to/ai-dev-tasks/000_backlog.md"
                }
            }
        ]
    }'
),
(
    'task-executor',
    'Task Execution Workflow',
    'Executes tasks from the event ledger',
    '{
        "nodes": [
            {
                "id": "poll-events",
                "type": "database",
                "parameters": {
                    "operation": "select",
                    "table": "event_ledger",
                    "where": "status = ''pending''"
                }
            },
            {
                "id": "execute-task",
                "type": "function",
                "parameters": {
                    "functionCode": "// Execute task based on event_type"
                }
            },
            {
                "id": "update-status",
                "type": "database",
                "parameters": {
                    "operation": "update",
                    "table": "event_ledger"
                }
            }
        ]
    }'
); 