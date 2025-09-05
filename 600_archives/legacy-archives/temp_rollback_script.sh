#!/usr/bin/env bash

# Temporary PRD Test Rollback Script
# Created: $(date)
# Purpose: Clean up temporary files created during PRD workflow test

echo "🧹 Cleaning up temporary PRD test files..."

# List of temporary files created during this test
TEMP_FILES=(
    "temp_backlog_google_analytics_test.md"
    "temp_prd_google_analytics_integration.md"
    "temp_task_list_google_analytics.md"
    "temp_execution_log.md"
    ".ai_state.json"
    "temp_rollback_script.sh"
)

echo "📋 Files to be removed:"
for file in "${TEMP_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file (exists)"
    else
        echo "  ❌ $file (not found)"
    fi
done

echo ""
echo "🗑️  To clean up these files, run:"
echo "rm temp_backlog_google_analytics_test.md"
echo "rm temp_prd_google_analytics_integration.md"
echo "rm temp_task_list_google_analytics.md"
echo "rm temp_execution_log.md"
echo "rm .ai_state.json"
echo "rm temp_rollback_script.sh"
echo ""
echo "📝 Test Summary:"
echo "  - Created temporary backlog with 3 items (T-001, T-002, T-003)"
echo "  - Generated PRD for T-001 (8 points, score 2.5) using 001_create-prd.md template"
echo "  - Generated comprehensive task list using 002_generate-tasks.md workflow"
echo "  - Task list includes 8 tasks across 5 phases with 90% test coverage requirements"
echo "  - Demonstrated 003_process-task-list.md workflow with state management and execution tracking"
echo "  - All files are marked for easy cleanup"
