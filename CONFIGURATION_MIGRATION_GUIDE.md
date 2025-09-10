# Configuration Migration Guide

This guide helps you migrate from the old configuration system to pydantic-settings.

## 🎯 Migration Overview

**Before**: Scattered `os.getenv()` calls, manual YAML parsing, custom validation
**After**: Centralized, typed, validated configuration with clear precedence

## 📋 Migration Checklist

- [x] Add pydantic-settings dependency
- [x] Create typed configuration models
- [x] Set up YAML + environment variable precedence
- [x] Create environment-specific configurations
- [x] Build comprehensive test suite
- [x] Analyze existing configuration patterns
- [ ] Migrate high-priority files
- [ ] Update import statements
- [ ] Remove old configuration code
- [ ] Update documentation

## 🔄 Migration Patterns

### 1. Environment Variable Access

**Before:**
```python
import os

db_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", 10))
aws_region = os.getenv("AWS_REGION", "us-east-1")
chunk_size = int(os.getenv("CHUNK_SIZE", 450))
```

**After:**
```python
from src.config import get_settings

settings = get_settings()
db_timeout = settings.performance.db_connect_timeout
aws_region = settings.security.aws_region
chunk_size = settings.rag.chunk_size
```

### 2. Configuration Classes

**Before:**
```python
@dataclass
class TimeoutConfig:
    db_connect_timeout: int = 10
    db_read_timeout: int = 30
    # ... manual loading and validation

def load_timeout_config() -> TimeoutConfig:
    config = TimeoutConfig()
    config.db_connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", config.db_connect_timeout))
    # ... more manual loading
    return config
```

**After:**
```python
from src.config import get_settings

# Configuration is automatically loaded and validated
settings = get_settings()
timeout_config = settings.performance
```

### 3. YAML Configuration

**Before:**
```python
import yaml

def load_config():
    with open("config/system.json") as f:
        config = json.load(f)
    # Manual environment variable overrides
    config["db"]["pool_size"] = int(os.getenv("DB_POOL_SIZE", config["db"]["pool_size"]))
    return config
```

**After:**
```python
from src.config import get_settings

# YAML + environment variables automatically handled
settings = get_settings()
db_config = settings.db
```

## 🚀 High-Priority Migration Targets

Based on the analysis, these files should be migrated first:

### 1. Core Configuration Files
- `src/utils/timeout_config.py` → Use `src/config/settings.py`
- `config/env_guard.py` → Replace with pydantic-settings validation
- `scripts/validate_config.py` → Update to use new models

### 2. Scripts with Many os.getenv() Calls
- `scripts/_ragchecker_eval_impl.py` (53 calls)
- `scripts/enhanced_bedrock_client.py` (Multiple calls)
- `scripts/ragchecker_evaluation.py` (Multiple calls)

### 3. Configuration Management Files
- `src/common/role_guc_manager.py`
- `src/retrieval/memory_integration.py`
- `scripts/lessons_loader.py`

## 🔧 Step-by-Step Migration Process

### Step 1: Update Imports
Replace old configuration imports:
```python
# Old
import os
from src.utils.timeout_config import load_timeout_config  # ❌ REMOVED

# New
from src.config import get_settings
```

### Step 2: Replace os.getenv() Calls
```python
# Old
db_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", 10))

# New
settings = get_settings()
db_timeout = settings.performance.db_connect_timeout
```

### Step 3: Update Configuration Access
```python
# Old
config = load_timeout_config()
timeout = config.db_connect_timeout

# New
settings = get_settings()
timeout = settings.performance.db_connect_timeout
```

### Step 4: Remove Old Configuration Code ✅ COMPLETED
- ✅ Deleted `src/utils/timeout_config.py` (old timeout configuration)
- ✅ Deleted `config/env_guard.py` (old environment validation)
- ✅ Updated all references to use pydantic-settings
- ✅ Removed manual environment variable loading
- ✅ Cleaned up old validation functions

## 🧪 Testing Migration

### 1. Run Configuration Tests
```bash
uv run python -m pytest tests/test_config_settings.py -v
```

### 2. Test Environment Variable Overrides
```bash
export APP_DB__POOL_SIZE=16
export APP_RAG__TOPK=50
uv run python -c "from src.config import get_settings; print(get_settings().db.pool_size, get_settings().rag.topk)"
```

### 3. Test YAML Configuration
```bash
export APP_ENV=test
uv run python -c "from src.config import get_settings; print(get_settings().env)"
```

## 📊 Configuration Precedence

The new system follows this precedence order (highest to lowest):

1. **Explicit kwargs** (when creating Settings instance)
2. **Base YAML** (`configs/base.yaml`)
3. **Environment-specific YAML** (`configs/{APP_ENV}.yaml`)
4. **Environment variables** (`APP_*` with `__` nesting)
5. **.env file** (for local development)
6. **Secret files** (if configured)

## 🔒 Security Considerations

- Secret fields are automatically excluded from logging
- Use `SecretStr` for sensitive configuration
- Environment variables take precedence over YAML files
- Never commit secrets to version control

## 🐛 Common Migration Issues

### Issue 1: Import Cycles
**Problem**: Circular imports when importing settings
**Solution**: Use lazy loading with `get_settings()` function

### Issue 2: Type Conversion
**Problem**: Old code expects specific types
**Solution**: Pydantic handles type conversion automatically

### Issue 3: Default Values
**Problem**: Different default values in old vs new system
**Solution**: Update YAML files to match expected defaults

## 📈 Benefits After Migration

- **Type Safety**: Automatic validation and type conversion
- **Centralized Management**: Single source of truth for configuration
- **Better Error Messages**: Clear validation errors instead of runtime failures
- **Environment Support**: Easy switching between dev/test/prod
- **Documentation**: Auto-generated configuration documentation
- **IDE Support**: Auto-completion and type hints

## 🎉 Migration Complete

Once migration is complete, you can:

1. Remove old configuration files
2. Update documentation
3. Clean up unused imports
4. Celebrate the improved configuration system! 🎊

## 📚 Additional Resources

- [pydantic-settings Documentation](https://docs.pydantic.dev/2.0/usage/pydantic_settings/)
- [Configuration Examples](./CONFIGURATION_MIGRATION_EXAMPLES.md)
- [Focused Migration Report](./FOCUSED_CONFIGURATION_MIGRATION_REPORT.md)
