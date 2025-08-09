<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_system-overview.md -->

# Setup Requirements

<!-- ANCHOR: tldr -->
<a id="tldr"></a>

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- Purpose: One-stop local setup (venv, DB, deps)

- Read after: project/system overview; use for fresh envs

- Outputs: verified env with health checks

### **S-003: Environment Configuration** ⚙️

**Status**: `setup-required`
**Priority**: Medium
**Setup Required**: Environment variables setup
**Setup Instructions**: Configure N8N_BASE_URL, N8N_API_KEY, POSTGRES_DSN

**Required Environment Variables:**

```bash

# n8n Configuration

N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your_api_key_here

# Database Configuration

POSTGRES_DSN=postgresql://user:pass@host:port/db
DB_MIN_CONNECTIONS=1
DB_MAX_CONNECTIONS=10
DB_CONNECTION_TIMEOUT=30
DB_HEALTH_CHECK_INTERVAL=60

# Event Processing

POLL_INTERVAL=30
MAX_EVENTS_PER_CYCLE=10

```

### **S-004: Cursor IDE Setup** 🔥

**Status**: `setup-required`
**Priority**: High
**Setup Required**: Cursor IDE installation and configuration
**Setup Instructions**: See `CURSOR_NATIVE_AI_STRATEGY.md`

**Commands:**

```bash

# Install Cursor IDE

# Download from https://cursor.sh/

# Configure Cursor

# Enable AI features in settings

# Verify installation

# Test AI code generation

```

### **S-005: Specialized Agents Setup** 🔥

**Status**: `setup-required`
**Priority**: High
**Setup Required**: Specialized agent configuration
**Setup Instructions**: See `CURSOR_NATIVE_AI_STRATEGY.md`

**Prerequisites:**

<!-- Optional local model instructions archived under 600_archives/legacy-integrations to keep core docs Cursor-native
-->

### **S-006: PostgreSQL Database Setup** 🔥

**Status**: `setup-required`
**Priority**: High
**Setup Required**: PostgreSQL installation + database creation
**Setup Instructions**: See `400_system-overview.md` (Architecture) and `104_dspy-development-context.md` (modules)

**Commands:**

```bash

# Install PostgreSQL (Ubuntu)

sudo apt-get install postgresql postgresql-contrib
sudo apt-get install postgresql-14-pgvector

# Create database and user

sudo -u postgres createuser danieljacobs
sudo -u postgres createdb ai_agency
sudo -u postgres psql -c "ALTER USER danieljacobs WITH PASSWORD 'your_password';"

# Enable pgvector extension

sudo -u postgres psql ai_agency -c "CREATE EXTENSION IF NOT EXISTS vector;"

```

### **S-007: Virtual Environment Setup** ⚙️

**Status**: `setup-required`
**Priority**: Medium
**Setup Required**: Python virtual environment + dependencies
**Setup Instructions**: See `400_project-overview.md`

**Commands:**

```bash

# Create and activate virtual environment

python3 -m venv venv
source venv/bin/activate

# Install dependencies

pip install -r dspy-rag-system/requirements.txt

```

### **S-008: Cursor IDE Configuration** 🔥

**Status**: `setup-required`
**Priority**: High
**Setup Required**: Cursor IDE (Cursor-native AI is default). Local Code Model integration is optional.
**Setup Instructions**: For optional Local Code Model integration, see `600_archives/legacy-integrations/`

**Cursor Configuration:**

1. Open Cursor Settings
2. Go to AI → Custom Models
3. Add Local Code Model configuration:

   ```json
   {
     "name": "Local Code Model-9B-Chat-Q6_K",
     "apiBase": "http://localhost:1234/v1",
     "apiKey": "lm-studio"
   }
   ```

### **S-009: Secrets Management Setup** 🔥

**Status**: `setup-required`
**Priority**: High
**Setup Required**: Environment secrets configuration
**Setup Instructions**: See `C8_COMPLETION_SUMMARY.md`

**Required Secrets:**

```bash

# Database

POSTGRES_DSN=postgresql://user:pass@host:port/db
DB_PASSWORD=your_database_password

# Dashboard

DASHBOARD_SECRET_KEY=your_secret_key

# AI Models

OLLAMA_API_KEY=your_ollama_key

# n8n (if using authentication)

N8N_API_KEY=your_n8n_api_key

```

### **S-010: System Dependencies** ⚙️

**Status**: `setup-required`
**Priority**: Medium
**Setup Required**: System packages and tools
**Setup Instructions**: See `400_system-overview.md`

**System Packages:**

```bash

# Ubuntu/Debian

sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib git curl

# macOS

brew install git curl python3 postgresql

# Python packages

pip install flask psycopg2-binary dspy-ai transformers torch

```

## 🧪 **Testing Setup**

### **Test Commands**

```bash

# Test n8n connectivity

curl http://localhost:5678/healthz

# (Optional) Local model checks are archived under 600_archives/legacy-integrations/

# Test database connection

python3 -c "from src.utils.database_resilience import get_database_manager; print('Database OK')"

# Test event processing

python3 demo_n8n_integration.py

```

### **Verification Checklist**

- [ ] n8n is running and accessible

- [ ] PostgreSQL is running with pgvector extension

- [ ] Virtual environment is activated

- [ ] All environment variables are set

- [ ] Cursor IDE is installed and configured

- [ ] All secrets are properly configured

## 📞 **Support**

If you encounter issues:

1. **Check the logs**: Look for error messages in console output
2. **Verify connectivity**: Test each component separately
3. **Review configuration**: Ensure all environment variables are set
4. **Check permissions**: Verify API keys and database user permissions

## 🚀 **Next Steps**

Once all setup items are completed:

1. **Start the event processor service**:

   ```bash
   python3 src/n8n_workflows/n8n_event_processor.py --daemon
   ```

2. **Test the complete system**:

   ```bash
   make run-local
   ```

3. **Monitor the system** using the provided endpoints

4. **Create your first workflow** in n8n

The system will be fully operational once all setup requirements are met!

## 🧩 Configuration Overview (moved here)

- Canonical config lives in `config/system.json`.

- Keys to know: `enabled_agents`, per‑agent settings (`model_id`, `signature`, `timeout`, `retry_policy`), `memory` (postgres delta), `error_policy` (retries, backoff, timeouts), `fast_path` (enabled, max_length, exclude_tokens).

- Environment overrides: DB_*, POOL_*, ENABLED_AGENTS, LLM_TIMEOUT_SEC, SECURITY_MAX_FILE_MB, MODEL_IDLE_EVICT_SECS, MAX_RAM_PRESSURE.

- Hot‑reload (if enabled): `curl -X POST http://localhost:5000/admin/reload-config`.

Minimal example (trimmed):

```json
{
  "version": "0.3.1",
  "enabled_agents": ["IntentRouter", "RetrievalAgent", "CodeAgent"],
  "memory": { "type": "postgres_delta" },
  "error_policy": { "max_retries": 3, "backoff_factor": 2.0, "timeout_seconds": 30 },
  "fast_path": { "enabled": true, "max_length": 50 }
}

```
