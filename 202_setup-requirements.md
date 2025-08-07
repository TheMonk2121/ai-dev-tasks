# 🔧 Setup Requirements - Manual Configuration Needed

This document lists all items that require manual setup or configuration on your end before they can be fully utilized.

<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- SYSTEM_FILES: 400_system-overview_advanced_features.md, dspy-rag-system/README.md -->
<!-- CONFIG_FILES: 201_model-configuration.md, docs/CONFIG_REFERENCE.md -->
<!-- INTEGRATION_FILES: 103_yi-coder-integration.md -->

<!-- MODULE_REFERENCE: 400_deployment-environment-guide_additional_resources.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide_environment_setup.md -->
<!-- MODULE_REFERENCE: 100_ai-development-ecosystem_advanced_lens_technical_implementation.md -->
<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->
### **AI Development Ecosystem Context**
This setup guide is part of a comprehensive AI-powered development ecosystem that transforms ideas into working software using AI agents (Cursor Native AI + Specialized Agents). The ecosystem provides structured workflows, automated task processing, and intelligent error recovery to make AI-assisted development efficient and reliable.

**Key Components:**
- **Planning Layer**: PRD Creation, Task Generation, Process Management
- **AI Execution Layer**: Cursor Native AI (Foundation), Specialized Agents (Enhancements)
- **Core Systems**: DSPy RAG System, N8N Workflows, Dashboard, Testing Framework
- **Supporting Infrastructure**: PostgreSQL + PGVector, File Watching, Notification System

## 📋 **Setup Required Items**

### **S-001: n8n Installation & Configuration** 🔥
**Status**: `setup-required`  
**Priority**: High  
**Setup Required**: n8n installation + API key + webhook setup  
**Setup Instructions**: See `dspy-rag-system/docs/N8N_SETUP_GUIDE.md`

**Information Needed from n8n:**
- **n8n Base URL**: Your n8n instance URL (default: http://localhost:5678)
- **API Key**: Generated from n8n Settings → API Keys
- **Webhook URLs**: For each workflow you want to trigger
- **Workflow IDs**: Identifiers for your n8n workflows

### **S-002: PostgreSQL Event Ledger Schema** 🔥
**Status**: `setup-required`  
**Priority**: High  
**Setup Required**: Database schema creation  
**Setup Instructions**: Run `config/database/event_ledger.sql` in PostgreSQL

**Commands:**
```bash
# Connect to PostgreSQL
psql -h localhost -U your_user -d your_database

# Execute the schema
\i dspy-rag-system/config/database/event_ledger.sql
```

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
- **macOS**: LM Studio ≥ 0.2.18 (`brew install --cask lm-studio`)
- **Linux**: Download AppImage from https://lmstudio.ai/
- **Storage**: 5GB+ for model download

**Model Download:**
1. Launch LM Studio → Models
2. Search "Yi-Coder-9B-Chat-GGUF"
3. Download Yi-Coder-9B-Chat-Q6_K.gguf (≈ 4.9 GB)

**LM Studio Configuration:**
- Context Length: 8092
- GPU Offload: 48 / 48 (full)
- Evaluation Batch Size: 384
- Offload KV Cache to GPU: On
- Flash Attention: On

### **S-006: PostgreSQL Database Setup** 🔥
**Status**: `setup-required`  
**Priority**: High  
**Setup Required**: PostgreSQL installation + database creation  
**Setup Instructions**: See `docs/ARCHITECTURE.md`

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
**Setup Required**: Cursor IDE + Yi-Coder integration  
**Setup Instructions**: See `103_yi-coder-integration.md`

**Cursor Configuration:**
1. Open Cursor Settings
2. Go to AI → Custom Models
3. Add Yi-Coder configuration:
   ```json
   {
     "name": "Yi-Coder-9B-Chat-Q6_K",
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
**Setup Instructions**: See `400_system-overview_advanced_features.md`

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

# Test Ollama
ollama list

# Test LM Studio
curl http://localhost:1234/v1/models

# Test database connection
python3 -c "from src.utils.database_resilience import get_database_manager; print('Database OK')"

# Test event processing
python3 demo_n8n_integration.py
```

### **Verification Checklist**
- [ ] n8n is running and accessible
- [ ] Ollama is running with Mistral model
- [ ] LM Studio is running with Yi-Coder model
- [ ] PostgreSQL is running with pgvector extension
- [ ] Virtual environment is activated
- [ ] All environment variables are set
- [ ] Cursor IDE is configured with Yi-Coder
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