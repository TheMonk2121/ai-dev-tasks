# Test Organization

This directory contains all tests for the AI Dev Tasks project, organized into two main categories:

## Directory Structure

```
tests/
├── mock/                    # Mock-based unit tests
│   ├── test_*.py           # Fast unit tests with mocked dependencies
│   └── __init__.py
├── implementation/          # Real implementation tests
│   ├── test_*_real.py      # Tests with real database connections
│   ├── run_real_database_tests.py
│   └── __init__.py
└── README.md               # This file
```

## Test Categories

### Mock Tests (`tests/mock/`)
- **Purpose**: Fast unit tests with mocked dependencies
- **Requirements**: No external dependencies (database, network, etc.)
- **Speed**: Very fast (seconds)
- **Use Case**: Development, CI/CD gates, quick feedback
- **Examples**: Unit tests for individual functions, mocked database operations

### Implementation Tests (`tests/implementation/`)
- **Purpose**: Real integration tests with actual system components
- **Requirements**: Real database connection, external services
- **Speed**: Slower (minutes)
- **Use Case**: End-to-end validation, production readiness, regression testing
- **Examples**: Database operations, MCP server workflows, DSPy retriever functionality

## Running Tests

### Using the Test Runner

```bash
# Run only mock tests (fast)
python run_tests.py --mock

# Run only implementation tests (requires real database)
python run_tests.py --implementation

# Run all tests (mock + implementation)
python run_tests.py --all

# Run specific test patterns
python run_tests.py --mock --pattern "test_mcp"
python run_tests.py --implementation --pattern "test_database"

# Check database availability
python run_tests.py --check-db
```

### Using Make

```bash
# Mock tests only
make test-mock

# Implementation tests only (requires database)
make test-implementation

# All tests
make test-real

# Check database availability
make test-check-db
```

### Using pytest directly

```bash
# Mock tests
uv run pytest tests/mock/ -v

# Implementation tests (requires database)
uv run pytest tests/implementation/ -v -m database

# All tests
uv run pytest tests/ -v
```

## Database Requirements

### Mock Tests
- No database required
- Use mock DSNs (`mock://test`)
- Fast execution

### Implementation Tests
- Real PostgreSQL database required
- Set `TEST_POSTGRES_DSN` or `POSTGRES_DSN` environment variable
- Example: `export TEST_POSTGRES_DSN="postgresql://user:pass@localhost:5432/test_db"`

## Test Markers

Tests are marked with pytest markers for easy filtering:

- `@pytest.mark.unit` - Unit tests (mock-based)
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.database` - Tests requiring real database
- `@pytest.mark.mcp` - MCP memory server tests
- `@pytest.mark.dspy` - DSPy retriever tests
- `@pytest.mark.workload_isolation` - Workload isolation tests

## Development Workflow

1. **During Development**: Use mock tests for fast feedback
   ```bash
   make test-mock
   ```

2. **Before Committing**: Run all tests to ensure nothing breaks
   ```bash
   make test-real
   ```

3. **CI/CD**: Run appropriate test suite based on environment
   - Development: Mock tests only
   - Staging/Production: All tests including implementation

## Adding New Tests

### Mock Tests
- Place in `tests/mock/`
- Use `@pytest.mark.unit` marker
- Mock all external dependencies
- Keep tests fast and isolated

### Implementation Tests
- Place in `tests/implementation/`
- Use `@pytest.mark.database` marker
- Use real database connections
- Test actual system behavior

## Troubleshooting

### Mock Tests Failing
- Check that all external dependencies are properly mocked
- Ensure tests don't make real network/database calls
- Verify test isolation (no shared state)

### Implementation Tests Failing
- Verify database connection: `make test-check-db`
- Check that required database schema exists
- Ensure test database is clean and accessible
- Verify environment variables are set correctly
