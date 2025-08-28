#!/bin/bash

# Unified Memory System Launcher
# Fires up all memory rehydration systems with one command

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧠 Unified Memory System Launcher${NC}"
echo ""

# Check if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}❌ Error: Not in project root directory${NC}"
    echo "💡 Run this script from the ai-dev-tasks project root"
    exit 1
fi

# Check if virtual environment exists
if [ ! -f "venv/bin/python" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
    echo "💡 Creating virtual environment..."
    python3 -m venv venv
    # shellcheck disable=SC1091
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo -e "${GREEN}✅ Virtual environment found${NC}"
    # shellcheck disable=SC1091
    source venv/bin/activate
fi

# Default values
QUERY="current project status and core documentation"
ROLE="planner"
FORMAT="cursor"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -q|--query)
            QUERY="$2"
            shift 2
            ;;
        -r|--role)
            ROLE="$2"
            shift 2
            ;;
        -f|--format)
            FORMAT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -q, --query TEXT    Query for memory retrieval (default: 'current project status and core documentation')"
            echo "  -r, --role ROLE     Role for context retrieval (default: planner)"
            echo "                      Choices: planner, implementer, researcher, coder"
            echo "  -f, --format FORMAT Output format (default: cursor)"
            echo "                      Choices: cursor, json"
            echo "  -h, --help          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Default: planner role"
            echo "  $0 -q 'DSPy integration' -r coder     # Coder role for DSPy query"
            echo "  $0 -f json                            # JSON output format"
            echo ""
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "💡 Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}📝 Query:${NC} $QUERY"
echo -e "${BLUE}🎭 Role:${NC} $ROLE"
echo -e "${BLUE}🔧 Format:${NC} $FORMAT"
echo ""

# Function to read file content
read_file() {
    local file="$1"
    if [ -f "$file" ]; then
        cat "$file"
    else
        echo "File not found: $file"
    fi
}

# Function to get file summary
get_file_summary() {
    local file="$1"
    local max_lines="${2:-50}"
    if [ -f "$file" ]; then
        head -n "$max_lines" "$file"
        if [ "$(wc -l < "$file")" -gt "$max_lines" ]; then
            echo ""
            echo "... (truncated)"
        fi
    else
        echo "File not found: $file"
    fi
}

echo -e "${GREEN}🚀 Generating Unified Memory Context...${NC}"
echo ""

# Create unified memory context
MEMORY_CONTEXT=""

# Add core memory context
MEMORY_CONTEXT+="# 🧠 **UNIFIED MEMORY CONTEXT BUNDLE**\n\n"
MEMORY_CONTEXT+="## 📋 **Project Overview**\n\n"
MEMORY_CONTEXT+="$(get_file_summary "100_memory/100_cursor-memory-context.md" 100)\n\n"

# Add system overview
MEMORY_CONTEXT+="## 🏗️ **System Architecture**\n\n"
MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_03_system-overview-and-architecture.md" 100)\n\n"

# Add current backlog
MEMORY_CONTEXT+="## 📋 **Current Priorities**\n\n"
MEMORY_CONTEXT+="$(get_file_summary "000_core/000_backlog.md" 150)\n\n"

# Add role-specific context
case $ROLE in
    "planner")
        MEMORY_CONTEXT+="## 🎯 **Planner Context**\n\n"
        MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_00_getting-started-and-index.md" 60)\n\n"
        MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_03_system-overview-and-architecture.md" 40)\n\n"
        ;;
    "implementer")
        MEMORY_CONTEXT+="## 🔧 **Implementer Context**\n\n"
        MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_04_development-workflow-and-standards.md" 50)\n\n"
        MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_05_coding-and-prompting-standards.md" 50)\n\n"
        MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_09_automation-and-pipelines.md" 40)\n\n"
        ;;
    "researcher")
        MEMORY_CONTEXT+="## 🔬 **Researcher Context**\n\n"
        MEMORY_CONTEXT+="$(get_file_summary "500_research-index.md" 100)\n\n"
        ;;
    "coder")
        MEMORY_CONTEXT+="## 💻 **Coder Context**\n\n"
        MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_07_ai-frameworks-dspy.md" 50)\n\n"
        MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_08_integrations-editor-and-models.md" 50)\n\n"
        MEMORY_CONTEXT+="$(get_file_summary "100_memory/104_dspy-development-context.md" 40)\n\n"
        ;;
esac

# Add development environment info
MEMORY_CONTEXT+="## 🔧 **Development Environment**\n\n"
MEMORY_CONTEXT+="- **Virtual Environment**: $(if [ -n "$VIRTUAL_ENV" ]; then echo "✅ Active"; else echo "❌ Not Active"; fi)\n"
MEMORY_CONTEXT+="- **Python Version**: $(python3 --version)\n"
MEMORY_CONTEXT+="- **Project Root**: $(pwd)\n"
MEMORY_CONTEXT+="- **Query**: $QUERY\n"
MEMORY_CONTEXT+="- **Role**: $ROLE\n"
MEMORY_CONTEXT+="- **Timestamp**: $(date)\n\n"

# Add recent changes
MEMORY_CONTEXT+="## 📝 **Recent Changes**\n\n"
MEMORY_CONTEXT+="$(git log --oneline -5 2>/dev/null || echo "Git history not available")\n\n"

# Add system status
MEMORY_CONTEXT+="## 🟢 **System Status**\n\n"
MEMORY_CONTEXT+="- **Database Sync**: ✅ N/A (intentionally removed as part of B-1004 quality gate simplification)\n"
MEMORY_CONTEXT+="- **LTST Memory**: $(if [ -f "dspy-rag-system/src/utils/memory_rehydrator.py" ]; then echo "✅ Available"; else echo "❌ Not Found"; fi)\n"
MEMORY_CONTEXT+="- **Go CLI**: $(if [ -f "dspy-rag-system/src/cli/memory_rehydration_cli" ]; then echo "✅ Available"; else echo "❌ Not Found"; fi)\n\n"

# Add usage tips
MEMORY_CONTEXT+="## 💡 **Usage Tips**\n\n"
MEMORY_CONTEXT+="- Copy this bundle into Cursor chat for immediate context\n"
MEMORY_CONTEXT+="- Use different roles (planner, implementer, researcher, coder) for specific context\n"
MEMORY_CONTEXT+="- Check system status above for troubleshooting\n"
MEMORY_CONTEXT+="- Run \`./scripts/memory_up.sh -h\` for more options\n\n"

MEMORY_CONTEXT+="---\n"
MEMORY_CONTEXT+="*Generated by Unified Memory System Launcher - $(date)*\n"

# Output results
if [ "$FORMAT" = "json" ]; then
    # Create JSON output
    JSON_OUTPUT=$(cat <<EOF
{
  "query": "$QUERY",
  "role": "$ROLE",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "venv_active": $(if [ -n "$VIRTUAL_ENV" ]; then echo "true"; else echo "false"; fi),
  "memory_context": $(echo -e "$MEMORY_CONTEXT" | jq -Rs .)
}
EOF
)
    echo "$JSON_OUTPUT"
else
    # Output formatted for Cursor chat
    echo -e "$MEMORY_CONTEXT"
fi

echo ""
echo -e "${GREEN}✅ Unified memory context generated successfully!${NC}"
echo ""
echo -e "${BLUE}💡 Tips:${NC}"
echo "  - Copy the formatted output above into Cursor chat"
echo "  - Use --format json for programmatic access"
echo "  - Use --role to get role-specific context"
echo "  - This provides comprehensive project context without relying on broken rehydration systems"
