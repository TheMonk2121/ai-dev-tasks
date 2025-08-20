<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_system-overview.md -->
<!-- CONFIGURATION_MASTER: This file is the single source of truth for all configuration -->
<!-- DATABASE_SYNC: REQUIRED -->

# Setup Requirements

<!-- ANCHOR: tldr -->
{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
| One-stop local setup guide for environment, database, and dependencies | Setting up fresh development environment or
troubleshooting setup issues | Follow setup steps in order, run verification checklist, start with S-003 Environment
Configuration |

## ⚙️ **Complete Configuration Reference**

This section consolidates ALL configuration settings from across the system. For quick start, see
`400_guides/400_project-overview.md`.

### **Environment Variables**

#### **Core Agent Configuration**

```bash
# Agent Management
ENABLED_AGENTS=IntentRouter,RetrievalAgent,CodeAgent  # Comma-separated agent list
CLARIFIER=0  # Disable ClarifierAgent (default)

# Model Management
MODEL_IDLE_EVICT_SECS=600  # Idle model eviction time
MAX_RAM_PRESSURE=85  # Maximum RAM usage percentage
LLM_TIMEOUT_SEC=90  # Overrides agent timeouts (the execution engine)
```

## **Database Configuration**

```bash
# Connection Settings
POSTGRES_DSN=postgresql://user:pass@host:port/db  # Database connection string
POOL_MIN=1  # Minimum database connections
POOL_MAX=10  # Maximum database connections
DB_MIN_CONNECTIONS=1  # Minimum database connections in pool
DB_MAX_CONNECTIONS=10  # Maximum database connections in pool

# Timeout Settings
DB_CONNECT_TIMEOUT=10  # Database connection timeout (seconds)
DB_READ_TIMEOUT=30  # Database read timeout (seconds)
DB_WRITE_TIMEOUT=60  # Database write timeout (seconds)
DB_POOL_TIMEOUT=20  # Database pool timeout (seconds)
DB_CONNECTION_TIMEOUT=30  # Database connection timeout in seconds
DB_HEALTH_CHECK_INTERVAL=60  # Database health check interval in seconds
```

## **Network & HTTP Configuration**

```bash
# HTTP Timeouts
HTTP_CONNECT_TIMEOUT=10  # HTTP connection timeout (seconds)
HTTP_READ_TIMEOUT=30  # HTTP read timeout (seconds)
HTTP_TOTAL_TIMEOUT=120  # HTTP total timeout (seconds)

# Health & Monitoring
HEALTH_CHECK_TIMEOUT=30  # Health check timeout in seconds
READY_CHECK_TIMEOUT=10  # Readiness check timeout in seconds
METRICS_PORT=9100  # Prometheus metrics endpoint port
```

## **Processing Timeouts**

```bash
# File Processing
PDF_PROCESSING_TIMEOUT=300  # PDF processing timeout (seconds)
FILE_UPLOAD_TIMEOUT=600  # File upload timeout (seconds)
CHUNK_PROCESSING_TIMEOUT=120  # Chunk processing timeout (seconds)

# LLM Processing
LLM_REQUEST_TIMEOUT=120  # LLM request timeout (seconds)
LLM_STREAM_TIMEOUT=300  # LLM stream timeout (seconds)
STARTUP_TIMEOUT=60  # System startup timeout (seconds)
```

## **Security Configuration**

```bash
# Security Settings
SECURITY_ENABLED=true  # Enable security scanning
SECURITY_SCAN_ON_STARTUP=true  # Run security scan on startup
SECURITY_VULNERABILITY_THRESHOLD=medium  # Vulnerability threshold
SECURITY_AUTO_FIX=false  # Auto-fix security issues
SECURITY_REPORT_FILE=security-report.json  # Security report file
SECURITY_MAX_FILE_SIZE=104857600  # Maximum file size (100MB)
SECURITY_MAX_FILE_MB=100  # Raise default 50 MB cap (the execution engine)
SECURITY_TOKEN_LENGTH=32  # Security token length
```

## **Production Monitoring Configuration**

```bash
# Monitoring Settings
ENVIRONMENT=production  # Set environment (development, staging, production)
OTLP_ENDPOINT=http://localhost:4317  # OpenTelemetry endpoint (the execution engine)
MONITORING_INTERVAL=30  # Monitoring cycle interval in seconds
HEALTH_CHECK_TIMEOUT=5  # Health check timeout in seconds
```

## **External Services**

```bash
# n8n Configuration
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your_api_key_here

# Redis Configuration
REDIS_URL=redis://localhost:6379  # Redis for rate limiting persistence

# Event Processing
POLL_INTERVAL=30
MAX_EVENTS_PER_CYCLE=10
```

## **Configuration Commands**

### **Config Hot-Reload**

```bash
curl -X POST http://localhost:5000/admin/reload-config
```

#### **Override Enabled Agents**

```bash
ENABLED_AGENTS=IntentRouter,RetrievalAgent make run-local
```

#### **Health & Metrics**

```bash
# Health check
curl http://localhost:5000/health

# Metrics endpoint
curl http://localhost:9100/metrics

# Readiness check
curl http://localhost:5000/ready

# Production monitoring data
curl http://localhost:5000/api/monitoring

# Dependencies health check
curl http://localhost:5000/api/health/dependencies

# Database health status
curl http://localhost:5000/api/database/health
```

## **Configuration Validation**

```bash
# Validate system configuration
python3 scripts/validate_config.py

# Check configuration syntax
python3 -c "import json; json.load(open('config/system.json'))"
```

## **Security Scanning**

```bash
# Run comprehensive security scan
python3 scripts/security_scan.py

# Run security scan with failure on vulnerabilities
python3 scripts/security_scan.py --fail-on-vulnerabilities

# Run security scan with verbose output
python3 scripts/security_scan.py --verbose

# Run individual security tools
python3 -m bandit -r src/
python3 -m safety check
python3 -m pip_audit
```

## **S-003: Environment Configuration**

⚙️ **Status**: `setup-required`

- **Priority**: Medium
- **Setup Required**: Environment variables setup
- **Setup Instructions**: Configure N8N_BASE_URL, N8N_API_KEY, POSTGRES_DSN

- **Required Environment Variables**:

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

## **S-004: Cursor IDE Setup**

🔥 **Status**: `setup-required`

- **Priority**: High
- **Setup Required**: Cursor IDE installation and configuration
- **Setup Instructions**: See `100_memory/100_cursor-memory-context.md`

- **Commands**:

```bash

# Install Cursor IDE

# Download from https://cursor.sh/

# Configure Cursor

# Enable AI features in settings

# Verify installation

# Test AI code generation

```

### Model selection in Cursor

- In-app model picker: Settings → AI → Models, or run “Change Model” from the Command Palette.
- If you toggle Auto off, you currently see: GPT‑5, GPT‑5 High, GPT‑5 Fast, Claude 4 Sonnet (availability can vary by account/region).
- For the full, up-to-date catalog, see the official list: [Cursor Docs: Models](https://docs.cursor.com/models).


## **S-005: Specialized Agents Setup**

🔥 **Status**: `setup-required`

- **Priority**: High
- **Setup Required**: Specialized agent configuration
- **Setup Instructions**: See `100_memory/100_cursor-memory-context.md`

- **Prerequisites**: <!-- Optional local model instructions archived under 600_archives/legacy-integrations to keep core docs Cursor-native -->

### **S-006: PostgreSQL Database Setup**

🔥 **Status**: `setup-required`

- **Priority**: High
- **Setup Required**: PostgreSQL installation + database creation
- **Setup Instructions**: See `400_guides/400_system-overview.md` (Architecture) and `100_memory/104_dspy-development-context.md` (modules)

- **Commands**:

```bash

# Install PostgreSQL (Ubuntu)

sudo apt-get install postgresql postgresql-contrib
sudo apt-get install postgresql-14-pgvector

# Create database and user

sudo -u postgres createdb ai_agency
sudo -u postgres createuser danieljacobs
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_agency TO danieljacobs;"

```

## **Database Schema**

```sql
-- Documents table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    chunk_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document chunks table
CREATE TABLE document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id),
    chunk_text TEXT NOT NULL,
    chunk_embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Query logs table
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    response_time FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **S-007: Python Environment Setup**

🔥 **Status**: `setup-required`

- **Priority**: High
- **Setup Required**: Python environment and dependencies

#### **Python Environment**

**⚠️ Important**: This system requires Python 3.12. The single doorway automation system is optimized for Python 3.12 and may have compatibility issues with Python 3.9.

```bash
# Verify Python 3.12 is available
python3.12 --version

# Create virtual environment with Python 3.12
python3.12 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-dspy.txt
pip install -r dashboard/requirements.txt
```

**macOS Users**: If you have Python 3.9 as default, install Python 3.12 via Homebrew:
```bash
brew install python@3.12
# The single doorway system will automatically detect and use python3.12
```

## **System Dependencies**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv postgresql postgresql-contrib git curl

# macOS
brew install git curl python3 postgresql

# Python packages
pip install flask psycopg2-binary dspy-ai transformers torch  # cSpell:ignore psycopg2-binary
```

## **S-008: Development Setup**

🔥 **Status**: `setup-required`

- **Priority**: High
- **Setup Required**: Repository setup and initial configuration

### **Development Setup**

```bash
# Clone repository
git clone https://github.com/TheMonk2121/ai-dev-tasks.git
cd ai-dev-tasks

# Setup DSPy system
cd dspy-rag-system
./setup_dspy.sh

# Start dashboard
cd ../dashboard
./start_dashboard.sh
```

## **S-009: Production Deployment Setup**

🔥 **Status**: `setup-required`

- **Priority**: Medium
- **Setup Required**: Production environment configuration

### **Production Deployment**

```bash
# Setup production environment
sudo apt-get install nginx supervisor

# Configure nginx for dashboard
sudo nano /etc/nginx/sites-available/ai-dashboard

# Setup supervisor for background processes
sudo nano /etc/supervisor/conf.d/ai-processes.conf

# Start services
sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
```

## **System Requirements**

### **Minimum Requirements**

- **CPU**: 4 cores (8+ recommended)
- **RAM**: 8GB (16GB+ recommended)
- **Storage**: 50GB SSD
- **OS**: Ubuntu 22.04 LTS or macOS 12+

#### **Recommended Requirements**

- **CPU**: 8+ cores
- **RAM**: 32GB
- **Storage**: 200GB NVMe SSD
- **GPU**: NVIDIA GPU with 8GB+ VRAM (for AI processing)

## 🧪 Testing Setup

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

## **Verification Checklist**

- [ ] n8n is running and accessible

- [ ] PostgreSQL is running with pgvector extension

- [ ] Virtual environment is activated

- [ ] All environment variables are set

- [ ] Cursor IDE is installed and configured

- [ ] All secrets are properly configured

## 📞 Support

If you encounter issues:

1. **Check the logs**: Look for error messages in console output
2. **Verify connectivity**: Test each component separately
3. **Review configuration**: Ensure all environment variables are set
4. **Check permissions**: Verify API keys and database user permissions

## 🚀 Next Steps

Once all setup items are completed:

1. **Start the event processor service**:

   ```bash
   python3 src/n8n_workflows/n8n_event_processor.py --daemon
   ```text

2. **Test the complete system**:

   ```bash
   make run-local
   ```yaml

3. **Monitor the system** using the provided endpoints

4. **Create your first workflow** in n8n

The system will be fully operational once all setup requirements are met!

## 🧩 Configuration Overview

- Canonical config lives in `config/system.json`.

- Keys to know: `enabled_agents`, per‑agent settings (`model_id`, `signature`, `timeout`, `retry_policy`), `memory` (postgres delta), `error_policy` (retries, backoff, timeouts), `fast_path` (enabled, max_length, exclude_tokens).

- Environment overrides: DB_*, POOL_*, ENABLED_AGENTS, LLM_TIMEOUT_SEC, SECURITY_MAX_FILE_MB, MODEL_IDLE_EVICT_SECS, MAX_RAM_PRESSURE.

- Hot‑reload (if enabled): `curl -X POST http://localhost:5000/admin/reload-config`

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
