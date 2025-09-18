# Global Cursor Settings Recommendations

## User-Level Settings (Settings > Rules for AI)

Configure these in Cursor's global settings to apply across all projects:

```yaml
# My Global Coding Preferences
- Use modern Python 3.12 typing patterns (PEP 585)
- Use built-in generics: dict[str, Any], list[str], tuple[str, int]
- Import only from typing import Any for complex types
- Never use typing.Dict, typing.List, typing.Tuple, typing.Set
- Fix root causes instead of using # type: ignore
- Use absolute imports, no sys.path hacks
- Document all public functions and classes
- Use type hints for all parameters and return types
- Follow existing codebase patterns and conventions
- Use context managers for resource management
- Handle errors explicitly with proper exception types
- Use meaningful variable and function names
- Keep functions under 50 lines (100 for complex logic)
- Use snake_case for variables and functions
- Use PascalCase for classes
- Use UPPER_CASE for constants
- Group imports: standard library, third-party, local
- Use parameterized queries for database operations
- Use transactions for multi-statement operations
- Follow project-specific quality gates and standards
```

## IDE Configuration

### Type Checking
- Enable strict type checking
- Use basedpyright or pyright for type checking
- Enable type hints in function signatures
- Show type information in hover tooltips

### Code Formatting
- Use black for Python formatting
- Use ruff for linting
- Enable format on save
- Use 120 character line length

### Import Organization
- Group imports: standard library, third-party, local
- Sort imports alphabetically within groups
- Remove unused imports automatically
- Use absolute imports

### Error Handling
- Show type errors as warnings/errors
- Highlight unused variables
- Show missing type annotations
- Enable strict mode for type checking

## Project-Specific Overrides

These global settings will be overridden by project-specific rules in:
1. `.cursor/rules/` directory (highest priority)
2. `.cursorrules` file
3. `AGENTS.md` file

The project-specific rules take precedence over global settings, ensuring consistency within the project while maintaining flexibility across different projects.

## Memory and Context

### Context Preservation
- Maintain context across sessions
- Use structured logging with request/run IDs
- Record metrics (dataset hash, seed, profile)
- Preserve state in `.ai_state.json` (git-ignored)

### Memory Integration
- Use LTST for long-term semantic tracking
- Use Cursor memory for IDE integration
- Use Go CLI memory for command-line interface
- Use Prime for primary memory orchestration

## Quality Assurance

### Pre-commit Hooks
- Type checking with pyright
- Linting with ruff
- Formatting with black
- Testing with pytest

### CI/CD Integration
- Run quality gates on every commit
- Use project-specific evaluation profiles
- Follow GitHub Actions best practices
- Maintain database health checks

## Best Practices

### Code Generation
- Use AI-generated code as starting point
- Review and refine all generated code
- Follow existing project patterns
- Maintain consistency with codebase

### Error Prevention
- Follow established coding standards
- Use type hints consistently
- Handle errors explicitly
- Test all changes thoroughly

### Documentation
- Document all public APIs
- Maintain up-to-date documentation
- Use clear and concise comments
- Follow project documentation standards

