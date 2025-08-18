<!-- ANCHOR_KEY: graph-visualization-guide -->

<!-- ANCHOR_PRIORITY: 12 -->

<!-- ROLE_PINS: ["planner", "implementer"] -->

# 📊 Graph Visualization Guide

<!-- CONTEXT_REFERENCE: 400_guides/400_system-overview.md -->

<!-- MODULE_REFERENCE: 100_memory/100_cursor-memory-context.md -->

<!-- MODULE_REFERENCE: 000_core/000_backlog.md -->

<!-- MEMORY_CONTEXT: HIGH - Chunk relationship visualization system -->

<!-- DATABASE_SYNC: REQUIRED -->

## 🎯 **Current Status**

- **Status**: OK **ACTIVE** - Graph visualization system implemented

- **Priority**: 🔥 Critical - Essential for chunk relationship analysis

- **Points**: 5 - High complexity, advanced visualization features

- **Dependencies**: 400_guides/400_system-overview.md, dspy-rag-system/

- **Next Steps**: Monitor usage and gather feedback for improvements

<!-- ANCHOR_KEY: tldr -->

<!-- ANCHOR_PRIORITY: 0 -->

<!-- ROLE_PINS: ["planner", "implementer"] -->

## 🔎 TL;DR

| what this file is | read when | do next |
|----|----|----|
| Comprehensive guide for chunk relationship visualization using Flask and NiceGUI | You need to understand or use the visualization system | Jump to `#quick-start` for immediate usage; then review `#architecture` for technical details |

## 🚀 Quick Start

### **🐙 Wake Up Nemo (Recommended)**

``` bash
# Start all visualization components with one command
./dspy-rag-system/wake_up_nemo.sh

# This starts:
# - Flask Dashboard (port 5000)
# - NiceGUI Graph (port 8080)
# - API endpoint (/graph-data)
```

### **Individual Components**

#### **Flask Cluster Visualization**

``` bash
# Start the main dashboard
./dspy-rag-system/start_mission_dashboard.sh

# Access cluster visualization
# Open: http://localhost:5000/cluster
```

#### **NiceGUI Network Graph**

``` bash
# Start the graph visualization app
./dspy-rag-system/start_graph_visualization.sh

# Access network graph
# Open: http://localhost:8080
```

### **API Access**

``` bash
# Get visualization data directly
curl "http://localhost:5000/graph-data?max_nodes=1000&include_knn=true&include_entity=true"
```

### **🐙 Nemo Management Commands**

``` bash
# Start everything (parallel startup - recommended)
./dspy-rag-system/wake_up_nemo.sh

# Performance modes
./dspy-rag-system/wake_up_nemo.sh --parallel        # Fast parallel startup (default)
./dspy-rag-system/wake_up_nemo.sh --sequential      # Legacy sequential startup

# Stop everything (fast shutdown - recommended)
./dspy-rag-system/sleep_nemo.sh

# Performance modes
./dspy-rag-system/sleep_nemo.sh --fast              # Fast shutdown (default)
./dspy-rag-system/sleep_nemo.sh --graceful          # Legacy graceful shutdown
./dspy-rag-system/sleep_nemo.sh --force             # Force kill processes

# Check status
./dspy-rag-system/wake_up_nemo.sh --status

# Test API
./dspy-rag-system/wake_up_nemo.sh --test

# Start only specific components
./dspy-rag-system/wake_up_nemo.sh --flask-only
./dspy-rag-system/wake_up_nemo.sh --nicegui-only

# Performance testing
python scripts/performance_benchmark.py --script wake_up_nemo_parallel --iterations 3
python scripts/performance_benchmark.py --script sleep_nemo_fast --iterations 3
```

<!-- ANCHOR_KEY: architecture -->

<!-- ANCHOR_PRIORITY: 20 -->

<!-- ROLE_PINS: ["implementer"] -->

## 🏗️ Architecture

### **System Components**

    ┌─────────────────────────────────────────────────────────────┐
    │                    Visualization System                     │
    ├─────────────────────────────────────────────────────────────┤
    │  📊 GraphDataProvider (Core Engine)                        │
    │  ├── UMAP Coordinate Computation                           │
    │  ├── Cache Management (Corpus Snapshot Keyed)              │
    │  ├── Database Integration (PostgreSQL + pgvector)          │
    │  └── Feature Flag Protection                               │
    ├─────────────────────────────────────────────────────────────┤
    │  🌐 API Layer (/graph-data V1)                             │
    │  ├── Query Parameter Validation                            │
    │  ├── Response Formatting (JSON V1 Schema)                  │
    │  ├── Error Handling & Status Codes                         │
    │  └── Performance Monitoring                                │
    ├─────────────────────────────────────────────────────────────┤
    │  📈 Flask Cluster View (UMAP Scatter)                      │
    │  ├── Plotly.js Integration                                 │
    │  ├── Interactive Controls (Query, Filters, Sliders)        │
    │  ├── Real-time Updates                                     │
    │  └── Responsive Design                                     │
    ├─────────────────────────────────────────────────────────────┤
    │  🕸️ NiceGUI Network Graph (Cytoscape)                      │
    │  ├── Cytoscape.js Integration                              │
    │  ├── Force-Directed Layout                                 │
    │  ├── Node/Edge Styling & Interactions                      │
    │  └── Advanced Filtering & Navigation                       │
    └─────────────────────────────────────────────────────────────┘

### **Data Flow**

1.  **User Request** → Flask/NiceGUI UI
2.  **API Call** → `/graph-data` endpoint
3.  **Data Processing** → GraphDataProvider
4.  **Database Query** → PostgreSQL + pgvector
5.  **UMAP Computation** → 2D coordinate generation
6.  **Response** → JSON V1 schema
7.  **Visualization** → Plotly/Cytoscape rendering

<!-- ANCHOR_KEY: api-reference -->

<!-- ANCHOR_PRIORITY: 15 -->

<!-- ROLE_PINS: ["implementer"] -->

## 🔌 API Reference

### **GET /graph-data**

**Purpose**: Retrieve chunk relationship data for visualization

**Parameters**: - `q` (string, optional): Search query for filtering
chunks - `include_knn` (boolean, default: true): Include KNN similarity
edges - `include_entity` (boolean, default: true): Include entity
relationship edges - `min_sim` (float, 0.0-1.0, default: 0.5): Minimum
similarity threshold - `max_nodes` (integer, 1-10000, default: 2000):
Maximum nodes to return

**Response Format (V1 Schema)**:

``` json
{
  "nodes": [
    {
      "id": "chunk_123",
      "label": "file.md:45-67",
      "anchor": "tldr",
      "coords": [0.12, -0.87],
      "category": "documentation"
    }
  ],
  "edges": [
    {
      "source": "chunk_123",
      "target": "chunk_456",
      "type": "knn",
      "weight": 0.85
    }
  ],
  "elapsed_ms": 145,
  "v": 1,
  "truncated": false
}
```

**Status Codes**: - `200`: Success - `400`: Invalid parameters - `403`:
Feature flag disabled - `500`: Internal server error

<!-- ANCHOR_KEY: flask-cluster -->

<!-- ANCHOR_PRIORITY: 10 -->

<!-- ROLE_PINS: ["planner", "implementer"] -->

## 📊 Flask Cluster Visualization

### **Features**

- **UMAP Scatter Plot**: 2D visualization of chunk relationships
- **Interactive Controls**: Query input, max nodes, similarity slider
- **Real-time Updates**: Auto-refresh every 30 seconds
- **Hover Details**: File path and line span information
- **Color Coding**: By chunk category (anchor, documentation, code,
  other)
- **Edge Visualization**: KNN and entity relationships

### **Usage**

1.  **Start Dashboard**: `./dspy-rag-system/start_mission_dashboard.sh`
2.  **Navigate**: Go to `http://localhost:5000/cluster`
3.  **Configure**: Set query, max nodes, similarity threshold
4.  **Load Graph**: Click “Load Graph” to fetch and display data
5.  **Interact**: Hover over points, use zoom/pan controls

### **Controls**

- **Search Query**: Filter chunks by content
- **Max Nodes**: Limit visualization size (1-10000)
- **Similarity Slider**: Adjust minimum similarity threshold
- **Include KNN**: Toggle KNN similarity edges
- **Include Entity**: Toggle entity relationship edges
- **Load Graph**: Fetch and display data
- **Reset View**: Reset zoom and pan

<!-- ANCHOR_KEY: nicegui-graph -->

<!-- ANCHOR_PRIORITY: 10 -->

<!-- ROLE_PINS: ["planner", "implementer"] -->

## 🕸️ NiceGUI Network Graph

### **Features**

- **Interactive Network Graph**: Force-directed layout with Cytoscape.js
- **Advanced Filtering**: Query-based filtering and edge type toggles
- **Node Interactions**: Click for details, drag to reposition
- **Edge Visualization**: Different colors for KNN vs entity
  relationships
- **Performance Monitoring**: Real-time statistics and loading states
- **Responsive Design**: Adapts to different screen sizes

### **Usage**

1.  **Start Application**:
    `./dspy-rag-system/start_graph_visualization.sh`
2.  **Access Interface**: Go to `http://localhost:8080`
3.  **Configure**: Set query, max nodes, similarity, edge types
4.  **Load Data**: Click “Load Graph Data” to fetch and render
5.  **Navigate**: Use zoom, pan, and selection tools

### **Controls**

- **Search Query**: Filter chunks by content
- **Max Nodes**: Limit graph size (1-10000)
- **Similarity Slider**: Adjust minimum similarity threshold
- **Edge Type Toggles**: Enable/disable KNN and entity edges
- **Load Graph Data**: Fetch and render network
- **Reset View**: Reset zoom and fit to view
- **Open Dashboard**: Link to main Flask dashboard

### **Interactions**

- **Node Click**: Show file path and line details
- **Node Drag**: Reposition nodes manually
- **Zoom**: Mouse wheel or zoom controls
- **Pan**: Click and drag background
- **Selection**: Click and drag to select multiple nodes

<!-- ANCHOR_KEY: configuration -->

<!-- ANCHOR_PRIORITY: 8 -->

<!-- ROLE_PINS: ["implementer"] -->

## ⚙️ Configuration

### **Environment Variables**

``` bash
# Feature flag control
GRAPH_VISUALIZATION_ENABLED=true

# Dashboard URL for NiceGUI
DASHBOARD_URL=http://localhost:5000

# Performance settings
MAX_NODES=2000
UMAP_CACHE_ENABLED=true
```

### **Performance Tuning**

- **UMAP Parameters**: Adjust `n_neighbors`, `min_dist` for different
  datasets
- **Cache Settings**: Configure cache size and invalidation policies
- **Database Optimization**: Ensure proper indexing on embeddings
- **Memory Management**: Monitor memory usage with large datasets

### **Security Considerations**

- **Feature Flags**: Use `GRAPH_VISUALIZATION_ENABLED` to disable
  features
- **Input Validation**: All query parameters are validated and sanitized
- **Rate Limiting**: Consider implementing rate limits for API endpoints
- **Access Control**: Ensure proper authentication for production use

<!-- ANCHOR_KEY: troubleshooting -->

<!-- ANCHOR_PRIORITY: 5 -->

<!-- ROLE_PINS: ["implementer"] -->

## 🔧 Troubleshooting

### **Common Issues**

#### **Flask Dashboard Not Starting**

``` bash
# Check if port 5000 is available
lsof -i :5000

# Check dependencies
pip3 install -r dspy-rag-system/requirements.txt
```

#### **NiceGUI App Not Starting**

``` bash
# Check NiceGUI installation
pip3 install nicegui>=1.4.0

# Check if Flask dashboard is running
curl http://localhost:5000/api/health
```

#### **Slow Performance**

- **Reduce max_nodes**: Lower the node limit for faster rendering
- **Enable caching**: Ensure UMAP cache is enabled
- **Check database**: Verify PostgreSQL performance and indexing
- **Monitor memory**: Check system memory usage

#### **No Data Displayed**

- **Check database**: Ensure chunks exist in the database
- **Verify API**: Test `/graph-data` endpoint directly
- **Check logs**: Review application logs for errors
- **Feature flag**: Ensure `GRAPH_VISUALIZATION_ENABLED=true`

### **Debug Commands**

``` bash
# Test API endpoint
curl "http://localhost:5000/graph-data?max_nodes=100"

# Check database connection
python3 -c "from dspy-rag-system.src.utils.database_resilience import DatabaseResilienceManager; print('DB OK')"

# Test UMAP computation
python3 -c "import umap; print('UMAP OK')"

# Check NiceGUI
python3 -c "import nicegui; print('NiceGUI OK')"
```

<!-- ANCHOR_KEY: development -->

<!-- ANCHOR_PRIORITY: 8 -->

<!-- ROLE_PINS: ["implementer"] -->

## 🛠️ Development

### **Adding New Features**

1.  **Extend GraphDataProvider**: Add new data processing methods
2.  **Update API Schema**: Modify V1 schema for new features
3.  **Enhance UIs**: Add controls and visualizations
4.  **Update Tests**: Add comprehensive test coverage
5.  **Document Changes**: Update this guide

### **Testing**

``` bash
# Run all visualization tests
python3 -m pytest dspy-rag-system/tests/test_graph_data_provider.py -v
python3 -m pytest dspy-rag-system/tests/test_graph_data_endpoint.py -v
python3 -m pytest dspy-rag-system/tests/test_nicegui_graph_view.py -v

# Run performance tests
python3 dspy-rag-system/benchmark_vector_store.py
```

### **Code Structure**

    dspy-rag-system/
    ├── src/
    │   ├── utils/
    │   │   └── graph_data_provider.py    # Core visualization engine
    │   ├── dashboard.py                  # Flask dashboard with /graph-data
    │   └── nicegui_graph_view.py         # NiceGUI network graph app
    ├── templates/
    │   └── cluster.html                  # Flask cluster visualization
    ├── tests/
    │   ├── test_graph_data_provider.py   # Core functionality tests
    │   ├── test_graph_data_endpoint.py   # API endpoint tests
    │   └── test_nicegui_graph_view.py    # NiceGUI app tests
    └── start_graph_visualization.sh      # NiceGUI startup script

<!-- ANCHOR_KEY: examples -->

<!-- ANCHOR_PRIORITY: 5 -->

<!-- ROLE_PINS: ["planner", "implementer"] -->

## 📝 Examples

### **Basic API Usage**

``` python
import requests

# Get all chunks with default settings
response = requests.get("http://localhost:5000/graph-data")
data = response.json()

# Get filtered chunks
response = requests.get(
    "http://localhost:5000/graph-data",
    params={
        "q": "machine learning",
        "max_nodes": 500,
        "min_sim": 0.7,
        "include_knn": True,
        "include_entity": False
    }
)
data = response.json()
```

### **Custom Visualization**

``` python
import plotly.graph_objects as go
import requests

# Fetch data
response = requests.get("http://localhost:5000/graph-data?max_nodes=1000")
data = response.json()

# Create custom scatter plot
fig = go.Figure(data=go.Scatter(
    x=[node['coords'][0] for node in data['nodes']],
    y=[node['coords'][1] for node in data['nodes']],
    mode='markers',
    text=[node['label'] for node in data['nodes']],
    hovertemplate='<b>%{text}</b><br>Category: %{marker.color}<extra></extra>'
))

fig.show()
```

### **Integration with Existing Systems**

``` python
from dspy_rag_system.src.utils.graph_data_provider import GraphDataProvider
from dspy_rag_system.src.utils.database_resilience import DatabaseResilienceManager

# Create provider
db_manager = DatabaseResilienceManager("postgresql://...")
provider = GraphDataProvider(db_manager=db_manager)

# Get visualization data
graph_data = provider.get_graph_data(
    query="AI development",
    max_nodes=1000,
    include_knn=True,
    include_entity=True
)

# Process results
for node in graph_data.nodes:
    print(f"Chunk: {node.label}, Category: {node.category}")
```

<!-- ANCHOR_KEY: best-practices -->

<!-- ANCHOR_PRIORITY: 8 -->

<!-- ROLE_PINS: ["planner", "implementer"] -->

## 🎯 Best Practices

### **Performance Optimization**

- **Use Caching**: Enable UMAP cache for repeated queries
- **Limit Node Count**: Use appropriate max_nodes for your use case
- **Optimize Queries**: Use specific search queries to reduce data
  volume
- **Monitor Resources**: Track memory and CPU usage

### **User Experience**

- **Progressive Loading**: Start with smaller datasets and increase
  gradually
- **Clear Feedback**: Provide loading indicators and error messages
- **Intuitive Controls**: Use familiar UI patterns and clear labels
- **Responsive Design**: Ensure usability on different screen sizes

### **Data Quality**

- **Validate Inputs**: Ensure proper input validation and sanitization
- **Handle Edge Cases**: Test with empty datasets and boundary
  conditions
- **Monitor Accuracy**: Verify UMAP coordinates represent meaningful
  relationships
- **Update Regularly**: Refresh data to reflect latest document changes

### **Security**

- **Feature Flags**: Use environment variables to control feature
  availability
- **Input Sanitization**: Validate and sanitize all user inputs
- **Access Control**: Implement proper authentication for production use
- **Error Handling**: Avoid exposing sensitive information in error
  messages

## 📚 Related Documentation

- **System Overview**: `400_guides/400_system-overview.md`
- **API Documentation**: Flask dashboard and NiceGUI app
- **Testing Guide**: `400_guides/400_testing-strategy-guide.md`
- **Deployment Guide**: `400_guides/400_deployment-environment-guide.md`
- **Security Guide**: `400_guides/400_security-best-practices-guide.md`

## 🔄 Updates and Maintenance

- **Version**: V1.0 (Initial Release)
- **Last Updated**: 2025-08-16
- **Next Review**: 2025-09-16
- **Maintainer**: AI Development Team

For questions or issues, refer to the troubleshooting section or contact
the development team.

<!-- README_AUTOFIX_START -->

## Auto-generated sections for 400_graph-visualization-guide.md

## Generated: 2025-08-18T08:03:22.747797

## Missing sections to add:

## Last Reviewed

2025-08-18

## Owner

Documentation Team

## Purpose

Describe the purpose and scope of this document

## Usage

Describe how to use this document or system

<!-- README_AUTOFIX_END -->
