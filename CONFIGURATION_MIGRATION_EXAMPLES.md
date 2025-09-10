# Migration Examples

## os.getenv() Migration Examples

### Before (old pattern):
```python
import os

db_timeout = int(os.getenv('DB_CONNECT_TIMEOUT', 10))
aws_region = os.getenv('AWS_REGION', 'us-east-1')
chunk_size = int(os.getenv('CHUNK_SIZE', 450))
```

### After (pydantic-settings):
```python
from src.config import get_settings

settings = get_settings()
db_timeout = settings.performance.db_connect_timeout
aws_region = settings.security.aws_region
chunk_size = settings.rag.chunk_size
```

## Configuration Class Migration Examples

### Before (custom class):
```python
@dataclass
class TimeoutConfig:
    db_connect_timeout: int = 10
    db_read_timeout: int = 30
    # ... manual loading logic
```

### After (pydantic-settings):
```python
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class Performance(BaseModel):
    db_connect_timeout: int = Field(ge=1, le=60, default=10)
    db_read_timeout: int = Field(ge=5, le=300, default=30)
```
