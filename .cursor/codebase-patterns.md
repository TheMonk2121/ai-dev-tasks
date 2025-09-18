# Codebase Analysis and Patterns

## Type Annotation Patterns

### Modern Python 3.12 Typing (PEP 585)
The codebase consistently uses modern built-in generics:

```python
# ✅ CORRECT - Modern PEP 585 style
from typing import Any
def process_data(items: list[str], config: dict[str, Any]) -> tuple[bool, str]:
    return True, "success"

# ❌ INCORRECT - Old typing style
from typing import Dict, List, Tuple
def process_data(items: List[str], config: Dict[str, Any]) -> Tuple[bool, str]:
    return True, "success"
```

### Common Type Patterns
- **Function parameters**: Always typed with built-in generics
- **Return types**: Always annotated with `->` syntax
- **Class attributes**: Typed with proper annotations
- **Complex types**: Use `from typing import Any` only

### Database Typing Patterns
```python
# ✅ CORRECT - Modern database typing
from psycopg.rows import DictRow
import psycopg

def get_connection() -> psycopg.Connection[DictRow]:
    return psycopg.connect(dsn)

# ✅ CORRECT - Cursor-level row factory
with conn.cursor(row_factory=dict_row) as cur:
    results = cur.fetchall()  # Returns list[dict[str, Any]]

# ❌ INCORRECT - Connection-level row factory
conn = psycopg.connect(dsn, row_factory=dict_row)  # type: ignore[arg-type]
```

## Import Patterns

### Standard Import Order
```python
# 1. Standard library imports
import os
import sys
from pathlib import Path
from typing import Any

# 2. Third-party imports
import psycopg
from psycopg.rows import DictRow
from pydantic import BaseModel, Field

# 3. Local imports
from .db_dsn import resolve_dsn
from src.common.psycopg3_config import Psycopg3Config
```

### Database Import Patterns
```python
# ✅ CORRECT - Standard database imports
import psycopg
from psycopg.rows import DictRow, dict_row
from src.common.psycopg3_config import Psycopg3Config
from src.common.db_dsn import resolve_dsn

# ❌ INCORRECT - Old patterns
from typing import Dict, List, Tuple
from psycopg.rows import dict_row
```

## Database Connection Patterns

### Preferred Connection Pattern
```python
# ✅ CORRECT - Using Psycopg3Config
from src.common.psycopg3_config import Psycopg3Config

def get_data() -> list[dict[str, Any]]:
    with Psycopg3Config.get_cursor("ltst") as cur:
        cur.execute("SELECT * FROM table")
        return cur.fetchall()
```

### Context Manager Pattern
```python
# ✅ CORRECT - Proper context management
with Psycopg3Config.get_connection("retrieval") as conn:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT * FROM chunks WHERE id = %s", (chunk_id,))
        results = cur.fetchall()
```

### DSN Resolution Pattern
```python
# ✅ CORRECT - Using resolve_dsn
from src.common.db_dsn import resolve_dsn

def connect_to_db(role: str = "default") -> psycopg.Connection[DictRow]:
    dsn = resolve_dsn(role=role)
    return psycopg.connect(dsn)
```

## Pydantic Model Patterns

### Model Configuration
```python
# ✅ CORRECT - Modern Pydantic v2
from pydantic import BaseModel, ConfigDict, Field
from typing import Any

class MyModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True
    )
    
    name: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)
```

### Type Annotations in Models
```python
# ✅ CORRECT - Modern typing in Pydantic
class Provenance(BaseModel):
    run_id: str
    chunk_variant: str
    source_uri: str | None = None
    metadata: dict[str, Any] | None = None
    observed_at: datetime = Field(default_factory=datetime.utcnow)
```

## Error Handling Patterns

### Database Error Handling
```python
# ✅ CORRECT - Explicit error handling
try:
    with Psycopg3Config.get_cursor("ltst") as cur:
        cur.execute("SELECT * FROM table")
        results = cur.fetchall()
except psycopg.Error as e:
    logger.error(f"Database error: {e}")
    raise
```

### Type Safety Patterns
```python
# ✅ CORRECT - Type guards and validation
def process_items(items: list[dict[str, Any]]) -> list[str]:
    if not isinstance(items, list):
        raise TypeError("Expected list")
    
    return [item.get("name", "") for item in items if isinstance(item, dict)]
```

## Function and Class Patterns

### Function Signatures
```python
# ✅ CORRECT - Complete type annotations
def process_data(
    items: list[str], 
    config: dict[str, Any], 
    timeout: int = 30
) -> tuple[bool, list[str]]:
    """Process data with configuration and timeout."""
    return True, items
```

### Class Definitions
```python
# ✅ CORRECT - Typed class attributes
class DataProcessor:
    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.processed_count: int = 0
    
    def process(self, items: list[str]) -> list[str]:
        """Process items and return results."""
        return [item.upper() for item in items]
```

## Project-Specific Patterns

### Memory System Integration
```python
# ✅ CORRECT - Memory system patterns
from src.memory.models import Provenance, RetrievedChunk

def create_chunk(text: str, metadata: dict[str, Any]) -> RetrievedChunk:
    return RetrievedChunk(
        text=text,
        metadata=metadata,
        provenance=Provenance(
            run_id="current_run",
            ingest_run_id="ingest_123",
            chunk_variant="v1"
        )
    )
```

### DSPy Integration
```python
# ✅ CORRECT - DSPy patterns
from dspy import BootstrapFewShot, Validate
from typing import Any

class MyDSPyModule:
    def __init__(self) -> None:
        self.optimizer = BootstrapFewShot()
        self.validator = Validate()
    
    def process(self, query: str) -> dict[str, Any]:
        # DSPy processing logic
        return {"answer": "processed"}
```

## Quality Assurance Patterns

### Testing Patterns
```python
# ✅ CORRECT - Test function patterns
def test_database_connection() -> None:
    """Test database connection works correctly."""
    with Psycopg3Config.get_connection("test") as conn:
        assert conn is not None
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
            assert result[0] == 1
```

### Logging Patterns
```python
# ✅ CORRECT - Structured logging
import logging
from typing import Any

logger = logging.getLogger(__name__)

def process_with_logging(data: dict[str, Any]) -> bool:
    logger.info("Processing data", extra={"data_keys": list(data.keys())})
    try:
        # Processing logic
        return True
    except Exception as e:
        logger.error("Processing failed", extra={"error": str(e)})
        return False
```

## Anti-Patterns to Avoid

### ❌ Old Typing Patterns
```python
# DON'T DO THIS
from typing import Dict, List, Tuple, Set
def old_function(items: List[str]) -> Dict[str, Any]:
    return {"result": items}
```

### ❌ Type Ignores
```python
# DON'T DO THIS
conn = psycopg.connect(dsn, row_factory=dict_row)  # type: ignore[arg-type]
```

### ❌ Connection-Level Row Factory
```python
# DON'T DO THIS
conn = psycopg.connect(dsn, row_factory=dict_row)
```

### ❌ Direct DSN Access
```python
# DON'T DO THIS
dsn = os.getenv("POSTGRES_DSN")
conn = psycopg.connect(dsn)
```

## Summary

The codebase follows modern Python 3.12 patterns with:
- PEP 585 built-in generics (`dict[str, Any]` not `Dict[str, Any]`)
- Proper type annotations for all functions and classes
- Database patterns using `Psycopg3Config` and cursor-level row factories
- Pydantic v2 model patterns with proper configuration
- Structured error handling and logging
- Memory system and DSPy integration patterns

AI agents should follow these established patterns rather than suggesting outdated alternatives.

