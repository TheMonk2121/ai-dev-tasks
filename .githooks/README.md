# Git Hooks

This directory contains versioned git hooks for the AI Dev Tasks project.

## 🎯 Purpose

Versioned git hooks ensure:
- **Consistency**: Every team member gets the same hook logic
- **Code Review**: Hooks are tracked in git and can be reviewed
- **Easy Updates**: Changes propagate via git pulls
- **Documentation**: Clear explanation of what each hook does
- **Safety**: Hooks survive clean/clone operations

## 📁 Hook Files

### `pre-commit`
- **Purpose**: Runs pre-commit framework checks before commits
- **Features**: 
  - Conflict detection
  - Security scanning (Bandit)
  - Code formatting (Ruff, Black)
  - Markdown linting
  - Type checking (Pyright)
- **Framework**: Uses pre-commit.com configuration

### `commit-msg`
- **Purpose**: Validates commit message format
- **Features**:
  - Commit message linting
  - Conventional commit format validation
- **Framework**: Uses pre-commit.com configuration

### `post-commit`
- **Purpose**: Post-commit automation and workflow integration
- **Features**:
  - Triggers Scribe for backlog changes
  - Updates cursor memory for core documentation changes
  - Suggests README context updates for backlog items
- **Custom**: Project-specific automation

## 🚀 Bootstrap Setup

### For New Team Members

1. **Clone the repository**
2. **Run the bootstrap script**:
   ```bash
   # Set git to use versioned hooks
   git config core.hooksPath .githooks
   
   # Install pre-commit hooks
   pre-commit install --hook-type pre-commit --hook-type commit-msg -f
   
   # Ensure permissions
   chmod +x .githooks/*
   ```

### For Existing Team Members

After pulling updates that include hook changes:
```bash
# Update hooks
git pull
chmod +x .githooks/*
```

## 🔧 Maintenance

### Updating Hooks

1. **Modify hook files** in `.githooks/`
2. **Test locally** before committing
3. **Commit changes** to version control
4. **Team members pull** to get updates

### Adding New Hooks

1. **Create hook file** in `.githooks/`
2. **Add shebang**: `#!/usr/bin/env bash`
3. **Set permissions**: `chmod +x .githooks/new-hook`
4. **Update this README**
5. **Test and commit**

### Troubleshooting

#### Hooks Not Running
```bash
# Check git config
git config core.hooksPath

# Should output: .githooks

# If not set, run:
git config core.hooksPath .githooks
```

#### Permission Issues
```bash
# Fix permissions
chmod +x .githooks/*
```

#### Pre-commit Issues
```bash
# Reinstall pre-commit hooks
pre-commit install --hook-type pre-commit --hook-type commit-msg -f
```

## 📋 Hook Requirements

### Shebang
All hooks must start with:
```bash
#!/usr/bin/env bash
```

### Permissions
All hooks must be executable:
```bash
chmod +x .githooks/*
```

### Non-Interactive
Hooks must not prompt for input - they should:
- ✅ Fail fast with clear error messages
- ✅ Print status information
- ❌ Never prompt for user input

## 🔗 Related Files

- `.pre-commit-config.yaml` - Pre-commit framework configuration
- `scripts/hook_timer.sh` - Hook timing utilities
- `pyproject.toml` - Python tool configuration
- `.markdownlint.jsonc` - Markdown linting rules

## 📚 Resources

- [Git Hooks Documentation](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [Pre-commit Framework](https://pre-commit.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
