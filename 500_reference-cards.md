# Reference Cards

Quick reference for key architectural decisions and implementations.

## Vector Store Split (Core vs Perf)

### Overview
The vector store layer is split into two complementary implementations to serve different use cases while maintaining a unified interface.

### CoreVectorStore (core.py)
**Purpose:** Stable baseline with hybrid search capabilities
**Implementation:** Wraps HybridVectorStore
**Features:**
- Dense + sparse fusion
- Span-based search
- Stable API surface
- Default for general use

**Usage:**
```python
from vector_store import CoreVectorStore
vs = CoreVectorStore(db_connection_string)
```

### PerfVectorStore (perf.py)
**Purpose:** Performance-focused with monitoring and caching
**Implementation:** Wraps EnhancedVectorStore
**Features:**
- Performance monitoring
- Caching layer
- Health checks
- Index management
- Production metrics

**Usage:**
```python
from vector_store import PerfVectorStore
vs = PerfVectorStore(db_connection_string, dimension=384)
```

### Factory Pattern
**Purpose:** Unified interface with explicit mode selection
**Usage:**
```python
from vector_store import get_vector_store

# Explicit mode selection
vs = get_vector_store(mode="perf", db_connection_string=dsn)

# Environment-driven (VECTOR_STORE_MODE=perf)
vs = get_vector_store(db_connection_string=dsn)
```

### Protocol Interface
**Purpose:** Minimal shared surface for both implementations
**Methods:**
- `add_documents(docs)` - Add documents to store
- `similarity_search(query_embedding, top_k=5)` - Search for similar vectors
- `get_stats()` - Get store statistics
- `get_health_status()` - Get health status

### Migration Guide
**From EnhancedVectorStore:**
```python
# Old
from dspy_modules.enhanced_vector_store import EnhancedVectorStore
vs = EnhancedVectorStore(dsn)

# New
from vector_store import get_vector_store
vs = get_vector_store(mode="perf", db_connection_string=dsn)
```

**From HybridVectorStore:**
```python
# Old
from dspy_modules.vector_store import HybridVectorStore
vs = HybridVectorStore(dsn)

# New
from vector_store import get_vector_store
vs = get_vector_store(mode="core", db_connection_string=dsn)
```

### Governance
- **Shadow Fork Prevention:** No more `_enhanced.py` or `_optimized.py` variants
- **Documentation Required:** All vector store changes must update docs
- **Validator Enforcement:** WARN → FAIL after migration complete

### Testing
- **E2E Tests**: `tests/e2e/test_vector_store_modes_e2e.py` validates both modes
- **Facade Testing**: Tests use explicit mode selection, no environment detection
- **Offline Operation**: Tests work without network dependencies
- **Minimal Assertions**: Focus on API presence and basic behavior

## Validator Enforcement

### Categories
- **Archive**: Prevents modification of archived files
- **Shadow Fork**: Prevents `_enhanced.py` and `_optimized.py` patterns
- **README**: Ensures README files follow governance rules
- **Multi-Rep/XRef**: Validates cross-references and multi-representation
- **Code Quality**: Validates Python code quality (Ruff, Black, Mypy)
- **Unicode Safety**: Validates Unicode character safety (RUF001, RUF002, RUF003, PLE2502)
- **Error Reduction**: Validates error reduction governance and lessons learned

### Flip Criteria
- **Archive**: 3 consecutive clean days
- **Shadow Fork**: 7 consecutive clean days
- **README**: 14 consecutive clean days (after cleanup)
- **Multi-Rep**: 5 consecutive clean days (after cleanup)

### Environment Flags
```bash
export VALIDATOR_ARCHIVE_FAIL=0    # Flip to 1 when ready
export VALIDATOR_SHADOW_FAIL=0     # Flip to 1 when ready
export VALIDATOR_README_FAIL=0     # Flip to 1 when ready
export VALIDATOR_MULTIREP_FAIL=0   # Flip to 1 when ready
export VALIDATOR_CODE_QUALITY_FAIL=0  # Flip to 1 when ready
export VALIDATOR_UNICODE_SAFETY_FAIL=0  # Flip to 1 when ready
export VALIDATOR_ERROR_REDUCTION_FAIL=0  # Flip to 1 when ready
```

### Exceptions
Use pragmas for surgical exceptions:
```html
<!-- validator:allow xref-missing -->
<!-- validator:allow multi-rep-missing -->
```

### Rollback Policy
If any flipped category shows >5% false positives in 48h, revert with consensus note.

## Consensus Framework Reference

**Purpose**: Structured decision-making process for complex technical decisions
**Use When**: Making architectural decisions, evaluating proposals, resolving conflicts
**Process**: 5-phase consensus framework with role-based validation

### 5-Phase Consensus Process

#### Phase 1: Strawman Proposal Creation
- **Purpose**: Create initial proposal for review
- **Deliverable**: Structured proposal with context, assumptions, success criteria
- **Key Elements**:
  - Clear title and description
  - Proposer identification
  - Context and references
  - Assumptions and constraints
  - Success criteria

#### Phase 2: Red Team Review
- **Purpose**: Critical analysis and risk assessment
- **Focus Areas**: Risks, alternatives, challenges
- **Deliverable**: Critique with severity scoring
- **Key Elements**:
  - Critique points
  - Risk assessment
  - Challenge questions
  - Alternative approaches
  - Severity score (0.0-1.0)

#### Phase 3: Blue Team Review
- **Purpose**: Support and enhancement suggestions
- **Focus Areas**: Support, enhancements, implementation
- **Deliverable**: Support analysis with confidence scoring
- **Key Elements**:
  - Support points
  - Enhancement suggestions
  - Implementation guidance
  - Success indicators
  - Confidence score (0.0-1.0)

#### Phase 4: Consensus Feedback
- **Purpose**: Multi-participant discussion and refinement
- **Participants**: All stakeholders provide feedback
- **Deliverable**: Refined proposal with consensus score
- **Key Elements**:
  - Participant feedback
  - Proposal refinements
  - Consensus score calculation
  - Next steps identification

#### Phase 5: Validation Checkpoint
- **Purpose**: Final validation and decision
- **Validation Levels**: Basic (0.5), Standard (0.7), Strict (0.8), Expert (0.9)
- **Deliverable**: Final decision with implementation guidance
- **Key Elements**:
  - Criteria assessment
  - Overall score calculation
  - Pass/fail determination
  - Implementation priority
  - Timeline and resource requirements

### Success Criteria
- **Minimum Consensus Score**: 0.7
- **Minimum Validation Score**: 0.7
- **Minimum Participants**: 3
- **Maximum Rounds**: 5 (configurable)
- **Round Timeout**: 24 hours

### Implementation Guidance
- Use structured templates for each phase
- Maintain clear role separation (Red Team vs Blue Team)
- Document all decisions and rationale
- Track consensus scores and validation metrics
- Provide clear next steps for accepted proposals

## Traceability Reference

**Purpose**: Track relationships between requirements, implementation, and validation
**Use When**: Managing complex features, ensuring compliance, debugging issues
**Process**: Bidirectional traceability with automated validation

### Traceability Matrix

| Component | Input | Output | Validation |
|-----------|-------|--------|------------|
| Requirements | User stories, PRDs | Backlog items | Acceptance criteria |
| Implementation | Backlog items | Code, tests, docs | Test coverage |
| Validation | Code, tests | Test results | Quality metrics |
| Deployment | Validated code | Production system | Monitoring alerts |

### Traceability Tools
- **Backlog Parser**: Extracts requirements from markdown
- **Test Coverage**: Maps tests to requirements
- **Documentation Links**: Cross-references between docs
- **Validation Checkpoints**: Ensures quality gates

### Best Practices
- Maintain bidirectional links
- Automate traceability validation
- Update links when requirements change
- Use consistent naming conventions
- Document traceability decisions

## B-001: Implement Surgical Governance Testing Coverage

Add comprehensive test coverage for governance system using surgical approach - extend existing test suites with focused test cases for archive enrollment, path normalization, JSON purity, and governance tools
