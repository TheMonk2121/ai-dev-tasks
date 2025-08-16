<!-- DATABASE_SYNC: REQUIRED -->
<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_few-shot-context-examples.md -->
<!-- MODULE_REFERENCE: 400_guides/400_performance-optimization-guide.md -->
<!-- MEMORY_CONTEXT: MEDIUM - Documentation retrieval and indexing system -->
# 📚 Documentation Retrieval Guide

## 📚 Documentation Retrieval Guide

{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: Quick summary of 📚 Documentation Retrieval Guide.

- **read when**: When you need a fast orientation or before using this file in a workflow.

- **do next**: Scan the headings below and follow any 'Quick Start' or 'Usage' sections.

## 🎯 **Current Status**-**Status**: ✅ **ACTIVE**- Documentation retrieval system operational

- **Priority**: ⚡ High - Essential for context provision

- **Points**: 4 - Moderate complexity, ongoing maintenance

- **Dependencies**: 400_guides/400_context-priority-guide.md, dspy-rag-system

- **Next Steps**: Optimize retrieval performance and expand coverage

- **Google's Documentation**: CLeAR framework for structured documentation

- **GitHub Copilot**: Repository-specific instruction patterns

## 🏗️ **System Architecture**###**Core Components**####**1. Documentation Indexer**-**Purpose**: Scans and indexes all
documentation files

- **File**: `scripts/documentation_indexer.py`

- **Features**:
  - Automatic file discovery and categorization
  - Metadata extraction from HTML comments
  - Content chunking for optimal retrieval
  - Category-based organization

### **2. Documentation Retrieval Service**-**Purpose**: Main service for context provision

- **File**: `dspy-rag-system/src/dspy_modules/documentation_retrieval.py`

- **Features**:
  - Query processing and optimization
  - Semantic search with confidence scoring
  - Context synthesis from multiple sources
  - Task-specific context provision

#### **3. CLI Interface**-**Purpose**: Easy command-line access to the system

- **File**: `scripts/documentation_retrieval_cli.py`

- **Features**:
  - Search documentation with category filtering
  - Get context for specific tasks
  - Index documentation files
  - View system statistics

### **Integration Points**-**DSPy RAG System**: Leverages existing enhanced RAG infrastructure

- **Vector Store**: Uses PostgreSQL with PGVector for semantic search

- **AI Constitution**: Follows safety and compliance requirements

- **Memory Context**: Integrates with modular memory system

## 📋 **Usage Guide**###**Quick Start**####**1. Index Documentation**```bash

# Index all documentation files

python scripts/documentation_indexer.py

# Index specific directory

python scripts/documentation_indexer.py --root-path ./docs

```text

## **2. Search Documentation**```bash

# Basic search

python scripts/documentation_retrieval_cli.py search "how to implement RAG"

# Search with category filter

python scripts/documentation_retrieval_cli.py search "file operations" --category workflow

# Search with custom limit

python scripts/documentation_retrieval_cli.py search "DSPy implementation" --limit 10

```text

## **3. Get Context for Tasks**```bash

# Get context for development task

python scripts/documentation_retrieval_cli.py task "implement documentation indexing" --task-type development

# Get context for research task

python scripts/documentation_retrieval_cli.py task "analyze RAG performance" --task-type research

# Get context for workflow task

python scripts/documentation_retrieval_cli.py task "update backlog priorities" --task-type workflow

```text

## Validator quick start

```bash

# Dry-run (no changes)

python scripts/doc_coherence_validator.py

# Apply fixes

python scripts/doc_coherence_validator.py --no-dry-run

# Install pre-commit hook for automatic checks

./scripts/pre_commit_doc_validation.sh --install

# Run pre-commit validation manually

./scripts/pre_commit_doc_validation.sh

```text

## **4. Get Relevant Context**```bash

# Get general context

python scripts/documentation_retrieval_cli.py context "implement file splitting"

# Get workflow-specific context

python scripts/documentation_retrieval_cli.py context "file operations" --type workflow

# Get implementation context

python scripts/documentation_retrieval_cli.py context "DSPy modules" --type implementation

```text

## **Output Formats**####**JSON Format (Default)**```bash
python scripts/documentation_retrieval_cli.py search "RAG implementation" --format json

```text

Returns structured JSON with all metadata and results.

### **Text Format**```bash
python scripts/documentation_retrieval_cli.py search "RAG implementation" --format text

```text

Returns human-readable text with context and summaries.

#### **Summary Format**```bash
python scripts/documentation_retrieval_cli.py search "RAG implementation" --format summary

```text

Returns concise summary with confidence scores and source counts.

## 🔧**Advanced Usage**###**Programmatic Access**####**Direct Service Usage**```python
from dspy_modules.documentation_retrieval import create_documentation_retrieval_service

# Create service

service = create_documentation_retrieval_service("postgresql://localhost/dspy_rag")

# Get context for query

result = service.forward("how to implement RAG", "implementation")

# Search with category filter

search_result = service.search_documentation("file operations", "workflow")

# Get task-specific context

task_context = service.get_context_for_task("implement indexing", "development")

```text

## **Utility Functions**```python
from dspy_modules.documentation_retrieval import get_relevant_context, search_documentation, get_task_context

# Get relevant context

context = get_relevant_context("RAG implementation")

# Search documentation

results = search_documentation("file operations", "workflow")

# Get task context

task_context = get_task_context("implement documentation indexing", "development")

```text

## **Category System**####**Available Categories**-**core**: Core system files (100_*.md, 000_*.md, 400_*.md)

- **workflow**: Workflow files (001_*.md, 002_*.md, 003_*.md)

- **research**: Research files (500_*.md)

- **implementation**: Implementation files (*.py, *.js, *.ts)

- **guides**: Guide files (400_*-guide.md, 400_*-strategy.md)

- **completion**: Completion summaries (500_*-completion-summary.md)
- **examples**: Templates and examples (e.g., `300_examples/300_documentation-example.md`)

### **Context Types**-**general**: General context for any query

- **workflow**: Workflow and process context

- **research**: Research and analysis context

- **implementation**: Implementation and technical context

- **core**: Core system and architecture context

- **guides**: Guide and strategy context

### **Task Types**-**development**: Development and implementation tasks

- **research**: Research and analysis tasks

- **workflow**: Workflow and process tasks

- **planning**: Planning and strategy tasks

- **testing**: Testing and validation tasks

- **deployment**: Deployment and operations tasks

## 📊 **Performance and Monitoring**###**System Statistics**```bash

# Get system statistics

python scripts/documentation_retrieval_cli.py stats

# Get statistics in summary format

python scripts/documentation_retrieval_cli.py stats --format summary

```text

## **Performance Metrics**-**Indexing Speed**: Number of files indexed per minute

- **Search Latency**: Average response time for queries

- **Retrieval Accuracy**: Confidence scores for retrieved context

- **Coverage**: Percentage of documentation covered by search

### **Quality Assurance**-**Confidence Scoring**: All results include confidence scores

- **Source Attribution**: Clear indication of source documents

- **Category Filtering**: Ability to focus on specific documentation areas

- **Context Synthesis**: Intelligent combination of multiple sources

## 🔄 **Integration with Existing Systems**###**DSPy RAG System Integration**The documentation retrieval system integrates seamlessly with the existing DSPy RAG system:

- **Shared Vector Store**: Uses the same PostgreSQL + PGVector infrastructure

- **Enhanced RAG**: Leverages existing enhanced RAG capabilities

- **Model Routing**: Uses the same model routing system

- **Error Handling**: Follows the same error handling patterns

### **AI Constitution Compliance**All operations follow the AI Constitution rules:

- **Safety Validation**: All queries validated for safety

- **Context Preservation**: Maintains context integrity

- **Error Prevention**: Systematic error prevention and recovery

- **Documentation Coherence**: Preserves documentation structure

### **Memory Context Integration**Works with the modular memory context system:

- **Core Module**: Primary memory scaffold integration

- **Safety Module**: Safety requirements integration

- **State Module**: Current state integration

- **Workflow Module**: Development workflow integration

- **Guidance Module**: Context-specific guidance integration

## 🎯 **Use Cases**###**Development Tasks**```bash

# Get context for implementing new feature

python scripts/documentation_retrieval_cli.py task "implement file splitting" --task-type development

# Get context for debugging

python scripts/documentation_retrieval_cli.py context "error handling patterns" --type implementation

```text

## **Research Tasks**```bash

# Get context for research analysis

python scripts/documentation_retrieval_cli.py task "analyze RAG performance" --task-type research

# Get context for literature review

python scripts/documentation_retrieval_cli.py context "research findings" --type research

```text

## **Workflow Tasks**```bash

# Get context for process improvement

python scripts/documentation_retrieval_cli.py task "optimize workflow" --task-type workflow

# Get context for backlog management

python scripts/documentation_retrieval_cli.py context "backlog prioritization" --type workflow

```text

## **File Operations**```bash

# Get context for file deletion

python scripts/documentation_retrieval_cli.py context "file deletion safety" --type safety

# Get context for file modification

python scripts/documentation_retrieval_cli.py context "file modification workflow" --type workflow

```text

## 🔧**Configuration and Customization**###**Database Configuration**```bash

# Set database URL

export DATABASE_URL="postgresql://user:pass@localhost/dspy_rag"

# Use custom database URL

python scripts/documentation_retrieval_cli.py search "query" --db-url "postgresql://custom:url"

```text

## **Indexing Configuration**

```python

# Custom indexing patterns

indexer = DocumentationIndexer(db_connection_string)
indexer.doc_patterns = ["*.md", "*.txt", "*.rst", "*.py"]
indexer.exclude_patterns = ["node_modules/**", "venv/**", ".git/**"]

```text

## **Search Configuration**```python

# Custom search parameters

service = create_documentation_retrieval_service(db_connection_string)
result = service.forward("query", "context_type", max_results=10)

```sql

## 📈**Best Practices**###**Query Optimization**-**Be Specific**: Use specific terms rather than general ones

- **Use Categories**: Filter by relevant categories when possible

- **Combine Terms**: Use multiple relevant terms for better results

- **Task Context**: Use task-specific context types

### **Context Usage**-**Review Confidence**: Check confidence scores before using context

- **Verify Sources**: Review source documents for accuracy

- **Cross-Reference**: Use multiple queries to verify information

- **Update Regularly**: Re-index documentation when files change

### **System Maintenance**-**Regular Indexing**: Index documentation after significant changes

- **Monitor Performance**: Track search latency and accuracy

- **Update Categories**: Refine category definitions as needed

- **Backup Data**: Regular backups of indexed documentation

## 🔄 **Troubleshooting**###**Common Issues**####**No Results Found**```bash

# Check if documentation is indexed

python scripts/documentation_retrieval_cli.py stats

# Re-index documentation

python scripts/documentation_retrieval_cli.py index

```sql

## **Low Confidence Scores**-**Refine Query**: Use more specific terms

- **Check Categories**: Ensure relevant categories are included

- **Update Index**: Re-index documentation if files have changed

### **Slow Performance**-**Check Database**: Verify database connection and performance

- **Optimize Queries**: Use more specific queries

- **Limit Results**: Reduce the number of results requested

### **Debugging**```bash

# Enable debug logging

export LOG_LEVEL=DEBUG
python scripts/documentation_retrieval_cli.py search "query"

# Check system status

python scripts/documentation_retrieval_cli.py stats --format json

```

## 🎯**Future Enhancements**###**Planned Features**-**Real-time Indexing**: Automatic indexing of changed files

- **Advanced Filtering**: More sophisticated category and metadata filtering

- **Context Caching**: Cache frequently requested context

- **Performance Optimization**: Enhanced search algorithms

### **Integration Opportunities**-**IDE Integration**: Direct integration with development environments

- **CI/CD Integration**: Automated context provision in pipelines

- **Monitoring Integration**: Enhanced monitoring and alerting

- **API Expansion**: RESTful API for external access

- --

- Last Updated: 2024-08-07*
- Next Review: When system features change*

## 🔄 Research integration workflow

### Automation features

- Authoritative store + dispersal: `scripts/research_dispersal_automation.py`

- Assisted mapping/checklists: `scripts/research_integration_helper.py`

- One-shot runner: `scripts/run_research_dispersal.py`

### Manual review checklist

- [ ] Review complete research file accuracy

- [ ] Extract to 500_ buckets with cross-references

- [ ] Update 400_ anchor files with implementation-focused content

- [ ] Add/update backlog items if applicable

- [ ] Test any new scripts; update cross-references

### Critical safety notes

Before running:

- Commit current state, verify targets exist and are writable, validate research quality

After running:

- Review extracted sections, anchors, tests, and links; commit integration

<!-- GUIDE_METADATA
version: 1.0
creation_date: 2024-08-07
implementation_files: scripts/documentation_indexer.py, dspy-rag-system/src/dspy_modules/documentation_retrieval.py,
scripts/documentation_retrieval_cli.py
research_basis: 500_research-implementation-summary.md
integration: DSPy RAG System, AI Constitution, Memory Context System
- ->
