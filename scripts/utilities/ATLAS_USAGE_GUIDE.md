# 🧠 Atlas Graph Storage System - Usage Guide

## Overview

The Atlas Graph Storage System is a sophisticated memory management solution that preserves connections between conversations, decisions, code, docs, and backlog items. Unlike simple vector storage, it uses a graph-based approach to maintain relationships and enable self-healing navigation.

## 🚀 Quick Start

### 1. **Start the System**
```bash
# Start the complete Atlas system
uv run python scripts/atlas_cli.py start

# Check system status
uv run python scripts/atlas_cli.py status
```

### 2. **Capture Conversations**
```bash
# Manual capture
uv run python scripts/atlas_cli.py capture user "Your message here"
uv run python scripts/atlas_cli.py capture assistant "AI response here"

# Automatic capture (runs in background when started)
# Monitors ~/.cursor/chat_history/ for new conversation files
```

### 3. **Memory Rehydration**
```bash
# Get memory context
uv run python scripts/atlas_cli.py memory

# Custom query
uv run python scripts/atlas_cli.py memory --query "RAGChecker evaluation results"
```

### 4. **System Health**
```bash
# Check graph health
uv run python scripts/atlas_cli.py health

# Perform self-healing
uv run python scripts/atlas_cli.py heal
```

## 🏗️ Architecture

### **Core Components**

1. **Atlas Graph Storage** (`atlas_graph_storage.py`)
   - Graph-backed storage with `atlas_node`, `atlas_edge`, `atlas_evidence` tables
   - Vector embeddings + typed relationships
   - 48-hour retention policy

2. **Cursor Integration** (`cursor_atlas_integration.py`)
   - Captures Cursor conversations
   - Extracts decisions, suggestions, and concepts
   - Creates typed edges between related content

3. **Auto Capture** (`cursor_auto_capture.py`)
   - Monitors Cursor chat history files
   - Automatic conversation capture
   - Background processing

4. **Self-Healing Navigation** (`atlas_self_healing.py`)
   - Detects broken references
   - Repairs missing targets
   - Connects orphaned nodes
   - Strengthens low-confidence edges

5. **Unified System** (`atlas_unified_system.py`)
   - Combines all components
   - Health monitoring
   - Automatic repairs

### **Graph Structure**

```
Conversation Nodes
├── User Messages
├── Assistant Responses
├── Decisions (extracted from content)
└── Suggestions (extracted from content)

Typed Edges
├── decides → (conversation → decision)
├── suggests → (conversation → suggestion)
├── mentions → (conversation → concept)
└── similar_to → (node → similar node)
```

## 📊 Database Schema

### **Atlas Tables**

```sql
-- Core graph tables
atlas_node (node_id, node_type, title, content, metadata, embedding, expires_at)
atlas_edge (edge_id, source_node_id, target_node_id, edge_type, weight, evidence)
atlas_evidence (evidence_id, edge_id, evidence_type, evidence_text, confidence)

-- Legacy conversation tables (still used)
conversation_sessions (session_id, created_at, last_accessed, metadata)
conversation_context (id, session_id, context_type, context_key, context_value)
conv_chunks (id, session_id, chunk_text, embedding, entities, salience_score)
```

## 🔧 Configuration

### **Environment Variables**

```bash
# Database connection
export POSTGRES_DSN="postgresql://danieljacobs@localhost:5432/ai_agency"

# Cursor chat history directory (optional)
export CURSOR_CHAT_DIR="~/.cursor/chat_history"

# Session ID (optional, auto-generated if not set)
export CURSOR_SESSION_ID="your_session_id"
```

### **Embedding Configuration**

- **Model**: `BAAI/bge-large-en-v1.5`
- **Dimensions**: 1024
- **Similarity**: Cosine similarity
- **Index**: HNSW for fast search

## 🎯 Usage Patterns

### **1. Development Workflow**

```bash
# Start system at beginning of work session
uv run python scripts/atlas_cli.py start

# Work normally in Cursor (conversations auto-captured)
# Check status periodically
uv run python scripts/atlas_cli.py status

# Get memory context when needed
uv run python scripts/atlas_cli.py memory

# Stop system at end of session
uv run python scripts/atlas_cli.py stop
```

### **2. Memory Rehydration**

```bash
# Standard rehydration
uv run python scripts/atlas_cli.py memory

# Project-specific queries
uv run python scripts/atlas_cli.py memory --query "RAGChecker baseline requirements"
uv run python scripts/atlas_cli.py memory --query "DSPy optimization framework"
uv run python scripts/atlas_cli.py memory --query "database schema changes"
```

### **3. Health Maintenance**

```bash
# Check graph health
uv run python scripts/atlas_cli.py health

# Perform repairs if needed
uv run python scripts/atlas_cli.py heal

# Monitor over time
watch -n 60 "uv run python scripts/atlas_cli.py health"
```

## 🔍 Advanced Features

### **Self-Healing Capabilities**

1. **Missing Target Repair**
   - Finds similar nodes when targets are missing
   - Creates placeholder nodes as fallback
   - Updates edge references automatically

2. **Orphaned Node Connection**
   - Identifies nodes with no connections
   - Creates similarity-based connections
   - Improves graph connectivity

3. **Low Confidence Edge Management**
   - Removes very low confidence edges
   - Strengthens moderately low confidence edges
   - Maintains graph quality

### **Graph Traversal**

```python
# Search related conversations
from utilities.atlas_graph_storage import AtlasGraphStorage

storage = AtlasGraphStorage()
related = storage.search_related_conversations("graph storage", limit=5)

# Get conversation graph
graph = storage.get_conversation_graph("session_id")
print(f"Nodes: {len(graph['nodes'])}, Edges: {len(graph['edges'])}")
```

### **Custom Integration**

```python
# Manual conversation capture
from utilities.cursor_atlas_integration import CursorAtlasIntegration

integration = CursorAtlasIntegration()
turn_id = integration.capture_user_message(
    "Custom message",
    metadata={"custom": "data"}
)
```

## 📈 Monitoring & Metrics

### **Health Score Calculation**

- **Base Score**: Connectivity ratio (edges/nodes) × 50
- **Penalty**: Broken references ratio × 100
- **Range**: 0-100 (higher is better)

### **Key Metrics**

- **Total Nodes**: Number of conversation/decision/suggestion nodes
- **Total Edges**: Number of typed relationships
- **Health Score**: Overall graph health (0-100)
- **Broken References**: Count by severity (high/medium/low)
- **Orphaned Nodes**: Nodes with no connections

### **Recommendations**

The system provides automatic recommendations:
- 🔴 **High Priority**: Fix broken references (missing targets)
- 🟡 **Medium Priority**: Connect orphaned nodes
- 🟢 **Low Priority**: Review low-confidence edges
- 💡 **Action Items**: Run self-healing repairs

## 🚨 Troubleshooting

### **Common Issues**

1. **Import Errors**
   ```bash
   # Ensure you're in the project root
   cd /Users/danieljacobs/Code/ai-dev-tasks
   
   # Use uv run for proper environment
   uv run python scripts/atlas_cli.py status
   ```

2. **Database Connection Issues**
   ```bash
   # Check PostgreSQL is running
   psql -d ai_agency -c "SELECT 1;"
   
   # Verify DSN
   echo $POSTGRES_DSN
   ```

3. **Low Health Scores**
   ```bash
   # Check for broken references
   uv run python scripts/atlas_cli.py health
   
   # Perform repairs
   uv run python scripts/atlas_cli.py heal
   ```

4. **Memory Context Issues**
   ```bash
   # Check if conversations are being captured
   uv run python scripts/atlas_cli.py status
   
   # Verify session ID
   echo $CURSOR_SESSION_ID
   ```

### **Debug Mode**

```bash
# Enable debug logging
export ATLAS_DEBUG=1
uv run python scripts/atlas_cli.py status
```

## 🔄 Integration with Existing Systems

### **Memory Rehydration Protocol**

The Atlas system integrates with the existing memory rehydration:

```bash
# Enhanced memory rehydration with Atlas data
export POSTGRES_DSN="postgresql://danieljacobs@localhost:5432/ai_agency"
uv run python scripts/utilities/unified_memory_orchestrator.py --systems ltst cursor --role planner "current project status and core documentation"
```

### **RAGChecker Integration**

Atlas conversations can inform RAGChecker evaluations:

```bash
# Get conversation context for evaluation
uv run python scripts/atlas_cli.py memory --query "RAGChecker evaluation results"

# Use in evaluation
uv run python scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable
```

## 📚 API Reference

### **AtlasGraphStorage**

```python
class AtlasGraphStorage:
    def store_conversation_turn(session_id, role, content, metadata=None, related_nodes=None)
    def get_conversation_graph(session_id)
    def search_related_conversations(query, limit=10)
```

### **CursorAtlasIntegration**

```python
class CursorAtlasIntegration:
    def capture_user_message(content, metadata=None)
    def capture_assistant_response(content, metadata=None)
    def get_conversation_context(limit=10)
    def get_memory_context()
```

### **SelfHealingNavigator**

```python
class SelfHealingNavigator:
    def detect_broken_references()
    def repair_broken_references(broken_refs)
    def get_graph_health_report()
```

## 🎉 Success Metrics

The Atlas system is working correctly when:

- ✅ **Health Score**: >70/100
- ✅ **Broken References**: 0 high severity
- ✅ **Memory Context**: Rich conversation history
- ✅ **Auto Capture**: Conversations stored automatically
- ✅ **Self-Healing**: Issues detected and repaired

## 🔮 Future Enhancements

- **Real-time Dashboard**: Web interface for graph visualization
- **Advanced Analytics**: Conversation pattern analysis
- **Multi-Agent Support**: Support for multiple AI agents
- **Export/Import**: Graph backup and restore
- **API Endpoints**: REST API for external integration

---

**🎯 The Atlas Graph Storage System provides a robust, self-healing memory architecture that preserves the rich context and connections between all your AI conversations, decisions, and project knowledge.**
