# GitHub Actions Workflow Configuration

## Linter Warnings

Some GitHub Actions workflow files may trigger false-positive linter warnings about `runner` context variables. These warnings can be safely ignored as they relate to standard GitHub Actions syntax.

### Common False Positives

- `${{ runner.os }}`: Provides the operating system of the runner
- `${{ runner.temp }}`: Provides a temporary directory for the runner
- `${{ runner.arch }}`: Provides the architecture of the runner

These context variables are part of the standard GitHub Actions context and are completely valid.

## Recommended Action

If you see warnings about unrecognized `runner` named-values, you can safely disregard them. They do not indicate a problem with your workflow configuration.
