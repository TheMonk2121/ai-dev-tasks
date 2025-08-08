<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->

<!-- MODULE_REFERENCE: 400_performance-optimization-guide.md -->
# Export execution data
python3 scripts/state_manager.py --export execution_data.json
```

### **Error Analysis**
```bash
# Get error statistics
python3 scripts/error_handler.py --stats

# Export error report
python3 scripts/error_handler.py --export-report error_analysis.json

# Clear error history
python3 scripts/error_handler.py --clear
```

## 📊 **Key Metadata Sources**

### **1. Backlog File (`000_backlog.md`)**
- **Task IDs**: B-001, B-002, etc.
- **Priorities**: 🔥 (Critical), 📈 (High), ⭐ (Medium), 🔧 (Low)
- **Scores**: Business value, technical complexity, risk reduction
- **Dependencies**: Prerequisite tasks
- **Status**: todo, pending, completed, failed

### **2. Execution Database (`task_execution.db`)**
- **Execution Records**: Start time, completion time, error messages
- **Performance Metrics**: Average execution time, success rate
- **Retry Statistics**: Retry counts, delays, success rates
- **Task Metadata**: Title, priority, points, description

### **3. Error Handling System**
- **Error Categories**: network, file_system, database, permission, timeout
- **Severity Levels**: low, medium, high, critical
- **Recovery Actions**: Automatic recovery procedures
- **Error Patterns**: Frequency analysis and trends

## 🎯 **Common Usage Patterns**

### **Task Prioritization**
```python
# Sort by priority and score
tasks.sort(key=lambda t: (t.priority.value, t.score_total or 0), reverse=True)

# Filter by dependencies
if not self._check_dependencies(task):
    logger.warning(f"Task {task.id} dependencies not met")
```

### **Performance Monitoring**
```python
# Track execution patterns
avg_execution_time = performance_metrics.get_avg_time(task_id)
success_rate = performance_metrics.get_success_rate(task_id)

# Optimize retry strategies
if success_rate < 0.8:
    increase_retry_delay()
```

### **Error Recovery**
```python
# Classify errors automatically
error_category = error_handler.classify_error(error)
severity = error_handler.determine_severity(error, context)

# Apply appropriate recovery
recovery_action = error_handler._get_recovery_action(error_info)
```

## 📈 **Analytics Commands**

### **Performance Analysis**
```bash
# Get comprehensive statistics
python3 scripts/state_manager.py --stats

# Analyze slow tasks
python3 scripts/process_tasks.py list --format json | jq '.[] | select(.avg_execution_time > 300)'

# Find high retry tasks
python3 scripts/process_tasks.py list --format json | jq '.[] | select(.retry_count > 3)'
```

### **Error Pattern Analysis**
```bash
# Get error statistics by category
python3 scripts/error_handler.py --stats --by-category

# Export error trends
python3 scripts/error_handler.py --export-report error_trends.json

# Analyze recovery success rates
python3 scripts/error_handler.py --stats --recovery-rates
```

### **Dependency Analysis**
```bash
# Validate all dependencies
python3 scripts/process_tasks.py validate

# Find missing dependencies
python3 scripts/process_tasks.py validate --show-missing

# Export dependency graph
python3 scripts/backlog_parser.py --export-deps dependency_graph.json
```

## 🔧 **Database Schema Reference**

### **Task Executions Table**
```sql
task_executions:
  task_id TEXT PRIMARY KEY,
  status TEXT NOT NULL,
  started_at TIMESTAMP NOT NULL,
  completed_at TIMESTAMP,
  error_message TEXT,
  retry_count INTEGER DEFAULT 0,
  progress REAL DEFAULT 0.0,
  execution_time REAL,
  metadata TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

### **Performance Metrics Table**
```sql
performance_metrics:
  task_id TEXT PRIMARY KEY,
  avg_execution_time REAL,
  success_rate REAL,
  total_executions INTEGER DEFAULT 0,
  successful_executions INTEGER DEFAULT 0,
  failed_executions INTEGER DEFAULT 0,
  last_execution TIMESTAMP,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

## 🚨 **Error Categories & Recovery**

### **Network Errors**
- **Symptoms**: Connection timeouts, HTTP errors
- **Recovery**: Retry with exponential backoff
- **Commands**: `python3 scripts/error_handler.py --retry-network`

### **File System Errors**
- **Symptoms**: Permission denied, file not found
- **Recovery**: Cleanup temporary files and retry
- **Commands**: `python3 scripts/error_handler.py --cleanup-files`

### **Database Errors**
- **Symptoms**: SQL errors, connection failures
- **Recovery**: Reconnect and retry
- **Commands**: `python3 scripts/error_handler.py --reconnect-db`

### **Timeout Errors**
- **Symptoms**: Operation timeouts
- **Recovery**: Extend timeout and retry
- **Commands**: `python3 scripts/error_handler.py --extend-timeout`

## 📋 **Status Codes Reference**

### **Task Status**
- `todo`: Task not started
- `pending`: Task ready to execute
- `running`: Task currently executing
- `completed`: Task finished successfully
- `failed`: Task failed with error

### **Priority Levels**
- `🔥`: Critical priority
- `📈`: High priority
- `⭐`: Medium priority
- `🔧`: Low priority

### **Error Severity**
- `low`: Minor issues, non-critical
- `medium`: Moderate issues, some impact
- `high`: Significant issues, high impact
- `critical`: System-breaking issues

## 🔄 **Workflow Integration**

### **Automated Sprint Planning**
```bash
# Execute top 5 priority tasks
python3 scripts/process_tasks.py auto --max-tasks 5

# Execute tasks with specific priority
python3 scripts/process_tasks.py auto --priority 🔥 --max-tasks 3

# Execute tasks excluding human-required
python3 scripts/process_tasks.py auto --exclude-human --max-tasks 10
```

### **Continuous Monitoring**
```bash
# Monitor execution status
watch -n 30 'python3 scripts/process_tasks.py status'

# Monitor error rates
watch -n 60 'python3 scripts/error_handler.py --stats'

# Monitor performance metrics
watch -n 120 'python3 scripts/state_manager.py --stats'
```

## 📊 **Export & Reporting**

### **JSON Exports**
```bash
# Export all tasks
python3 scripts/process_tasks.py list --format json > tasks.json

# Export execution history
python3 scripts/state_manager.py --export history.json

# Export error report
python3 scripts/error_handler.py --export-report errors.json
```

### **CSV Reports**
```bash
# Export task summary
python3 scripts/process_tasks.py list --format csv > tasks.csv

# Export performance metrics
python3 scripts/state_manager.py --export-csv metrics.csv
```

## 🎯 **Best Practices**

### **Data Quality**
- Always validate metadata before storage
- Maintain consistent data formats
- Capture all relevant metadata fields

### **Performance**
- Use proper database indexing
- Cache frequently accessed metadata
- Compress historical data

### **Security**
- Implement access controls for sensitive metadata
- Define clear data retention policies
- Log all metadata access and modifications

### **Scalability**
- Design for horizontal scaling
- Partition large datasets
- Archive old data to maintain performance

---

**Quick Reference Version**: 1.0  
**Last Updated**: 2024-08-07  
**Related Documentation**: `400_metadata-collection-guide.md`

<!-- METADATA_SYSTEM: 400_metadata-collection-guide.md -->
<!-- WORKFLOW_INTEGRATION: 003_process-task-list.md, scripts/process_tasks.py -->
<!-- IMPLEMENTATION_CONTEXT: 104_dspy-development-context.md, 202_setup-requirements.md -->
<!-- QUICK_REFERENCE: 400_metadata-quick-reference.md -->
<!-- MEMORY_CONTEXT: MEDIUM - Quick reference for metadata operations -->
