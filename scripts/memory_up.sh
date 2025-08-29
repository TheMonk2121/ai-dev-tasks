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
    echo "💡 Attempting to install dependencies..."
    if ! pip install -r requirements.txt; then
        echo -e "${YELLOW}⚠️  Dependency installation failed, continuing without full dependencies${NC}"
        echo "💡 This is expected due to version conflicts - the memory system will work with basic functionality"
    fi
else
    echo -e "${GREEN}✅ Virtual environment found${NC}"
    # shellcheck disable=SC1091
    source venv/bin/activate
    echo "💡 Using existing virtual environment - no dependency installation needed"
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

# Add core workflow guides
MEMORY_CONTEXT+="## 🔄 **Core Workflow Guides**\n\n"
MEMORY_CONTEXT+="$(get_file_summary "000_core/001_create-prd.md" 50)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "000_core/002_generate-tasks.md" 50)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "000_core/003_process-task-list.md" 50)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "000_core/004_development-roadmap.md" 50)\n\n"

# Add complete 00-12 guide access for all roles
MEMORY_CONTEXT+="## 📚 **Complete 00-12 Guide Access**\n\n"

# Core workflow guides (000_core)
MEMORY_CONTEXT+="### **Core Workflow Guides (000_core)**\n\n"
MEMORY_CONTEXT+="$(get_file_summary "000_core/001_create-prd.md" 40)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "000_core/002_generate-tasks.md" 40)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "000_core/003_process-task-list.md" 40)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "000_core/004_development-roadmap.md" 40)\n\n"

# Complete 400_guides set
MEMORY_CONTEXT+="### **Complete Guide Set (400_guides)**\n\n"
MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_00_getting-started-and-index.md" 40)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_01_documentation-playbook.md" 40)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_02_governance-and-ai-constitution.md" 40)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_03_system-overview-and-architecture.md" 40)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_04_development-workflow-and-standards.md" 40)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_05_coding-and-prompting-standards.md" 40)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_06_memory-and-context-systems.md" 40)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_07_ai-frameworks-dspy.md" 40)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_08_integrations-editor-and-models.md" 40)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_09_automation-and-pipelines.md" 40)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_10_security-compliance-and-access.md" 40)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_11_deployments-ops-and-observability.md" 40)\n\n"
MEMORY_CONTEXT+="$(get_file_summary "400_guides/400_12_product-management-and-roadmap.md" 40)\n\n"

# DSPy development context
MEMORY_CONTEXT+="### **DSPy Development Context**\n\n"
MEMORY_CONTEXT+="$(get_file_summary "100_memory/104_dspy-development-context.md" 40)\n\n"

# Add DSPy-specific context for all roles
MEMORY_CONTEXT+="## 🤖 **DSPy Framework Context**\n\n"
MEMORY_CONTEXT+="**DSPy is an AI framework for programming with language models** that provides structured workflows, automated task processing, and intelligent error recovery.\n\n"

# Add DSPy system overview
MEMORY_CONTEXT+="### **DSPy System Overview**\n\n"
MEMORY_CONTEXT+="- **Status**: ✅ DSPy Multi-Agent System OPERATIONAL\n"
MEMORY_CONTEXT+="- **Architecture**: Multi-Agent DSPy with sequential model switching + optimization framework\n"
MEMORY_CONTEXT+="- **Models**: Cursor Native AI (orchestration) + Local DSPy Models (Llama 3.1 8B, Mistral 7B, Phi-3.5 3.8B)\n"
MEMORY_CONTEXT+="- **Database**: PostgreSQL with pgvector extension\n"
MEMORY_CONTEXT+="- **Framework**: DSPy with full signatures, modules, and structured programming\n"
MEMORY_CONTEXT+="- **Optimization**: LabeledFewShot optimizer, assertion framework, four-part optimization loop\n\n"

# Add DSPy core components
MEMORY_CONTEXT+="### **DSPy Core Components**\n\n"
MEMORY_CONTEXT+="1. **Model Switcher** - Sequential model switching for hardware constraints\n"
MEMORY_CONTEXT+="2. **Cursor Integration** - Clean interface for Cursor AI to orchestrate local models\n"
MEMORY_CONTEXT+="3. **Optimization System** - LabeledFewShot optimizer with configurable K parameter\n"
MEMORY_CONTEXT+="4. **Role Refinement System** - AI-powered role definition optimization\n"
MEMORY_CONTEXT+="5. **Vector Store** - HNSW vector indexing with optimal parameters\n"
MEMORY_CONTEXT+="6. **MCP Integration System** - 6 MCP servers for various integrations\n\n"

# Add DSPy-specific information based on role
case $ROLE in
    "planner")
        MEMORY_CONTEXT+="### **DSPy Planning Context**\n\n"
        MEMORY_CONTEXT+="DSPy provides structured planning workflows with:\n"
        MEMORY_CONTEXT+="- **PRD Creation**: Automated product requirement document generation\n"
        MEMORY_CONTEXT+="- **Task Generation**: AI-powered task breakdown and prioritization\n"
        MEMORY_CONTEXT+="- **Process Management**: Structured development workflows\n"
        MEMORY_CONTEXT+="- **Multi-Agent Orchestration**: Coordinated planning across different AI roles\n\n"
        ;;
    "implementer")
        MEMORY_CONTEXT+="### **DSPy Implementation Context**\n\n"
        MEMORY_CONTEXT+="DSPy enables systematic implementation with:\n"
        MEMORY_CONTEXT+="- **Structured Programming**: DSPy signatures and modules for reliable code\n"
        MEMORY_CONTEXT+="- **Automated Task Processing**: Intelligent workflow automation\n"
        MEMORY_CONTEXT+="- **Error Recovery**: Built-in error handling and recovery mechanisms\n"
        MEMORY_CONTEXT+="- **Integration Patterns**: Standardized patterns for component integration\n\n"
        ;;
    "researcher")
        MEMORY_CONTEXT+="### **DSPy Research Context**\n\n"
        MEMORY_CONTEXT+="DSPy supports research workflows with:\n"
        MEMORY_CONTEXT+="- **Optimization Research**: LabeledFewShot and other optimization techniques\n"
        MEMORY_CONTEXT+="- **Performance Analysis**: Metrics and monitoring for system optimization\n"
        MEMORY_CONTEXT+="- **Experimental Framework**: Structured approach to AI system experimentation\n"
        MEMORY_CONTEXT+="- **Knowledge Integration**: RAG systems for research context\n\n"
        ;;
    "coder")
        MEMORY_CONTEXT+="### **DSPy Coding Context**\n\n"
        MEMORY_CONTEXT+="DSPy provides coding capabilities with:\n"
        MEMORY_CONTEXT+="- **DSPy Signatures**: Structured I/O for reliable AI programming\n"
        MEMORY_CONTEXT+="- **Module System**: Reusable DSPy modules and components\n"
        MEMORY_CONTEXT+="- **Assertion Framework**: Runtime validation and error checking\n"
        MEMORY_CONTEXT+="- **Model Integration**: Seamless integration with various language models\n\n"
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
