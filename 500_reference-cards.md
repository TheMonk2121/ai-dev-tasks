# Reference Cards

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| External evidence and best practices for consensus framework | Implementing new features or validating decisions | Use as cross-references in backlog items and PRDs |

## RAG Lessons from Jerry (LlamaIndex talk) {#rag-lessons-from-jerry}

**Why this matters**  
Naive RAG fails on complex docs; advanced parsing + multi-representation + reflection reduces hallucinations. We map these lessons to governance scaffolding to prevent "naive governance".

**Key principles → Repo mappings**
- *Garbage in, garbage out* → Phase 0 backlog validator; PRD template hygiene.
- *Multi-representations per node* (table, caption, summary) → Backlog/PRD items must have raw + summary + refs (B-100).
- *Page-level chunking as strong baseline* → Treat Consensus Checkpoints as semantic "page-chunks" in `.ai_state.jsonl`.
- *Reflection layers* (retrieval + synthesis) → Validator + post-mortem lessons at each consensus round.
- *Routing by query type* → Adaptive routing (B-101) for pointed vs. broad decisions.

**Adopted backlog items**
- **B-100**: Multi-representation indexing (raw + summary + refs)
- **B-101**: Adaptive routing (pointed vs. broad queries)
- **B-102**: Cross-reference enforcement (traceability)

## Multi-representation Indexing {#multi-representation-indexing}

**Context**: From RAG research showing that storing multiple representations of the same content improves retrieval accuracy.

**Implementation**: Each backlog/PRD item stores:
1. **Raw**: The original content (backlog row, PRD document)
2. **Summary**: Structured metadata (scores, totals, key metrics)
3. **References**: Cross-links to lessons and external evidence

**Benefits**:
- Better semantic search across different query types
- Improved context retrieval for AI agents
- Reduced hallucination through multiple validation layers

## Traceability {#traceability}

**Context**: From software engineering best practices for requirements traceability.

**Implementation**: Every active backlog item must link to:
- At least one `lessons_applied` (internal knowledge)
- At least one `reference_cards` (external evidence)

**Benefits**:
- Prevents orphaned requirements
- Ensures decisions are grounded in evidence
- Enables systematic learning from past implementations

## Cognitive Scaffolding {#cognitive-scaffolding}

**Context**: From cognitive science research on how structured examples improve learning and decision-making.

**Implementation**: Few-shot examples injected into AI memory rehydration to provide:
- Pattern recognition for common scenarios
- Decision frameworks for complex choices
- Quality standards for outputs

**Benefits**:
- Consistent AI behavior across sessions
- Improved context understanding
- Reduced cognitive load for users

## Research-Based Design {#research-based-design}

**Context**: From evidence-based software engineering practices.

**Implementation**: Schema design and extraction patterns based on:
- Academic research findings
- Industry best practices
- Empirical validation results

**Benefits**:
- More robust and validated solutions
- Reduced trial-and-error development
- Systematic knowledge accumulation

## Workflow Automation {#workflow-automation}

**Context**: From DevOps and CI/CD best practices for reducing manual overhead.

**Implementation**: Automated task generation from PRDs and backlog items including:
- Consistent template application
- Dynamic testing requirements
- Quality gate enforcement

**Benefits**:
- Reduced manual effort
- Consistent quality standards
- Faster iteration cycles

## DSPy Framework {#dspy-framework}

**Context**: From Stanford's DSPy research on declarative LLM programming.

**Implementation**: Framework for building reliable AI systems with:
- Declarative program structure
- Automatic optimization
- Built-in validation

**Benefits**:
- More reliable AI behavior
- Easier debugging and maintenance
- Systematic performance optimization

## MCP Server Architecture {#mcp-server-architecture}

**Context**: From Model Context Protocol for AI agent tool integration.

**Implementation**: Standardized interfaces for:
- Tool discovery and invocation
- Context sharing between agents
- Resource management

**Benefits**:
- Interoperable AI systems
- Reduced integration complexity
- Scalable agent architectures

## Context Analysis {#context-analysis}

**Context**: From information retrieval and NLP research on context understanding.

**Implementation**: Systematic analysis of:
- Context relevance and quality
- Information density and coverage
- Temporal and semantic relationships

**Benefits**:
- Better context selection
- Improved AI understanding
- Reduced context pollution

## Connection Pooling {#connection-pooling}

**Context**: From database performance optimization research.

**Implementation**: Efficient resource management for:
- Database connections
- API rate limiting
- Memory allocation

**Benefits**:
- Improved performance
- Better resource utilization
- Reduced system overhead

## Agile Tracking {#agile-tracking}

**Context**: From agile methodology research and best practices.

**Implementation**: Systematic tracking of:
- Sprint progress and velocity
- Burndown charts and milestones
- Team capacity and dependencies

**Benefits**:
- Better project visibility
- Improved planning accuracy
- Faster delivery cycles

## Code Quality Patterns {#code-quality-patterns}

**Context**: From software engineering research on code quality and maintainability.

**Implementation**: Systematic patterns for:
- Code organization and structure
- Error handling and resilience
- Testing and validation

**Benefits**:
- More maintainable code
- Reduced technical debt
- Better developer productivity

## Refactoring Strategies {#refactoring-strategies}

**Context**: From software evolution and refactoring research.

**Implementation**: Systematic approaches for:
- Identifying refactoring opportunities
- Planning and executing changes
- Validating improvements

**Benefits**:
- Safer code evolution
- Improved system design
- Reduced maintenance costs

## Observability Best Practices {#observability-best-practices}

**Context**: From SRE and DevOps research on system observability.

**Implementation**: Comprehensive monitoring including:
- Metrics, logging, and tracing
- Alerting and incident response
- Performance analysis

**Benefits**:
- Better system reliability
- Faster incident resolution
- Improved user experience

## Local Development {#local-development}

**Context**: From developer productivity research and tooling best practices.

**Implementation**: Optimized local development environment with:
- Fast feedback loops
- Integrated tooling
- Consistent environments

**Benefits**:
- Faster development cycles
- Better developer experience
- Reduced environment issues

## LangExtract {#langextract}

**Context**: From information extraction and NLP research.

**Implementation**: Advanced extraction capabilities for:
- Structured data extraction
- Schema validation
- Quality assessment

**Benefits**:
- More accurate data extraction
- Better data quality
- Reduced manual processing

## N8N Workflows {#n8n-workflows}

**Context**: From workflow automation and integration research.

**Implementation**: Visual workflow automation for:
- Process orchestration
- Data transformation
- System integration

**Benefits**:
- Reduced manual work
- Better process consistency
- Improved system integration

## Extraction Services {#extraction-services}

**Context**: From microservices and API design research.

**Implementation**: Specialized services for:
- Content extraction and processing
- Schema validation and transformation
- Quality assessment and feedback

**Benefits**:
- Better separation of concerns
- Improved scalability
- Easier maintenance

## Backlog Management {#backlog-management}

**Context**: From product management and agile research.

**Implementation**: Systematic backlog practices including:
- Prioritization frameworks
- Estimation techniques
- Progress tracking

**Benefits**:
- Better product planning
- Improved team alignment
- Faster value delivery

## Project Tracking {#project-tracking}

**Context**: From project management research and best practices.

**Implementation**: Comprehensive project tracking including:
- Milestone management
- Risk assessment
- Resource allocation

**Benefits**:
- Better project visibility
- Improved decision making
- Reduced project risks

## Status Tracking {#status-tracking}

**Context**: From workflow management and process optimization research.

**Implementation**: Automated status tracking for:
- Work item progress
- Time tracking and estimation
- Stale item detection

**Benefits**:
- Better progress visibility
- Improved planning accuracy
- Reduced manual overhead

## Notification Systems {#notification-systems}

**Context**: From human-computer interaction research on notification design.

**Implementation**: Intelligent notification systems for:
- Context-aware alerts
- Priority-based filtering
- User preference management

**Benefits**:
- Better user experience
- Reduced notification fatigue
- Improved information flow

## Service Architecture {#service-architecture}

**Context**: From distributed systems and microservices research.

**Implementation**: Robust service architecture including:
- Service discovery and communication
- Fault tolerance and resilience
- Performance optimization

**Benefits**:
- Better system reliability
- Improved scalability
- Easier maintenance

## Extraction Validation {#extraction-validation}

**Context**: From data quality and validation research.

**Implementation**: Systematic validation for:
- Data accuracy and completeness
- Schema compliance
- Business rule enforcement

**Benefits**:
- Better data quality
- Reduced errors
- Improved trust in data

## Structured Extraction {#structured-extraction}

**Context**: From information extraction and NLP research.

**Implementation**: Advanced extraction techniques for:
- Semi-structured data processing
- Schema inference and validation
- Quality assessment

**Benefits**:
- More accurate extraction
- Better data structure
- Reduced manual processing

## Performance Optimization {#performance-optimization}

**Context**: From systems performance research and optimization techniques.

**Implementation**: Systematic performance optimization including:
- Profiling and bottleneck identification
- Resource optimization
- Caching and acceleration

**Benefits**:
- Better system performance
- Improved user experience
- Reduced resource costs

## Role Detection Patterns {#role-detection-patterns}

**Context**: From AI agent and multi-agent systems research.

**Implementation**: Intelligent role detection for:
- Context-aware agent selection
- Task-specific optimization
- Resource allocation

**Benefits**:
- Better agent utilization
- Improved task completion
- Reduced resource waste

## MCP Integration Patterns {#mcp-integration-patterns}

**Context**: From AI agent integration and tool usage research.

**Implementation**: Standardized patterns for:
- Tool discovery and registration
- Context sharing and management
- Resource coordination

**Benefits**:
- Better agent interoperability
- Improved tool utilization
- Reduced integration complexity
