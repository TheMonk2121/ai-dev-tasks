# 🔧 n8n Workflow Integration Setup Guide

> DEPRECATED: Use `400_09_automation-and-pipelines.md` (automation/pipelines), `400_11_deployments-ops-and-observability.md` (ops/monitoring), and `400_04_development-workflow-and-standards.md` (workflow hooks). Implementation details and configs live under `dspy-rag-system/`.

This guide documents the setup requirements for the n8n workflow integration system.

## 📋 **Prerequisites**

### **1. n8n Installation**
You need to have n8n installed and running. The system expects n8n to be available at `http://localhost:5678` by default.

**Installation Options:**
```bash
# Option 1: Docker (Recommended)
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Option 2: npm
npm install n8n -g
n8n start

# Option 3: Direct download
# Download from https://n8n.io/
```

### **2. Database Setup**
The event ledger schema needs to be created in your PostgreSQL database.

**Run the schema:**
```bash
# Connect to your PostgreSQL database
psql -h localhost -U your_user -d your_database

# Execute the event ledger schema
\i dspy-rag-system/config/database/event_ledger.sql
```

## 🔑 **Required Information from n8n**

### **1. n8n Base URL**
- **Default**: `http://localhost:5678`
- **Custom**: Your n8n instance URL if different
- **How to find**: Check your n8n installation URL

### **2. n8n API Key (Optional but Recommended)**
- **Location**: n8n Settings → API Keys
- **How to create**:
  1. Open n8n in your browser
  2. Go to Settings → API Keys
  3. Click "Create API Key"
  4. Copy the generated key
- **Purpose**: Authentication for secure workflow execution

### **3. Webhook URLs**
For each workflow you want to trigger, you need the webhook URL:
- **Format**: `http://localhost:5678/webhook/{workflow-id}`
- **How to find**:
  1. Open your workflow in n8n
  2. Add a "Webhook" trigger node
  3. Copy the webhook URL from the node
  4. Note the workflow ID from the URL

## ⚙️ **Configuration**

### **Environment Variables**
Add these to your environment or `.env` file:

```bash
# n8n Configuration
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your_api_key_here

# Database Configuration (if not already set)
POSTGRES_DSN=postgresql://user:pass@host:port/db
DB_MIN_CONNECTIONS=1
DB_MAX_CONNECTIONS=10
DB_CONNECTION_TIMEOUT=30
DB_HEALTH_CHECK_INTERVAL=60

# Event Processing
POLL_INTERVAL=30
MAX_EVENTS_PER_CYCLE=10
```

### **Workflow Setup**
1. **Create Backlog Scrubber Workflow**:
   - Create a new workflow in n8n
   - Add a "Webhook" trigger node
   - Add a "HTTP Request" node to read the backlog file
   - Add a "Function" node to calculate scores
   - Add a "HTTP Request" node to write the updated file
   - Note the workflow ID for configuration

2. **Create Task Executor Workflow**:
   - Create a new workflow in n8n
   - Add a "Webhook" trigger node
   - Add nodes to handle different task types
   - Configure error handling and logging
   - Note the workflow ID for configuration

## 🧪 **Testing the Connection**

### **1. Test n8n Connectivity**
```bash
# Test if n8n is accessible
curl http://localhost:5678/healthz

# Test webhook endpoint (replace with your workflow ID)
curl -X POST http://localhost:5678/webhook/your-workflow-id \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### **2. Test Database Connection**
```bash
# Test database connectivity
python3 -c "
from src.utils.database_resilience import get_database_manager
manager = get_database_manager()
print('Database connection successful')
"
```

### **3. Test Event Processing**
```bash
# Run the demo script
python3 demo_n8n_integration.py
```

## 🔍 **Troubleshooting**

### **Common Issues**

1. **n8n not accessible**:
   - Check if n8n is running: `curl http://localhost:5678/healthz`
   - Verify the port is correct (default: 5678)
   - Check firewall settings

2. **Database connection failed**:
   - Verify PostgreSQL is running
   - Check connection string in environment variables
   - Ensure the event ledger schema is created

3. **Webhook not working**:
   - Verify the workflow ID is correct
   - Check if the webhook trigger node is active
   - Ensure the workflow is published

4. **API Key authentication failed**:
   - Verify the API key is correct
   - Check if API key authentication is enabled in n8n
   - Ensure the key has proper permissions

### **Debug Commands**
```bash
# Check n8n status
curl -s http://localhost:5678/healthz | jq

# Test database connection
python3 -c "
import os
print('POSTGRES_DSN:', os.getenv('POSTGRES_DSN'))
print('N8N_BASE_URL:', os.getenv('N8N_BASE_URL'))
print('N8N_API_KEY:', 'SET' if os.getenv('N8N_API_KEY') else 'NOT SET')
"

# Test event creation
python3 -c "
from src.n8n_workflows.n8n_integration import create_event
try:
    event_id = create_event('test_event', {'test': 'data'})
    print(f'Event created successfully: {event_id}')
except Exception as e:
    print(f'Event creation failed: {e}')
"
```

## 📞 **Support**

If you encounter issues:

1. **Check the logs**: Look for error messages in the console output
2. **Verify connectivity**: Test n8n and database connections separately
3. **Review configuration**: Ensure all environment variables are set correctly
4. **Check permissions**: Verify API keys and database user permissions

## 🚀 **Next Steps**

Once the setup is complete:

1. **Start the event processor service**:
   ```bash
   python3 src/n8n_workflows/n8n_event_processor.py --daemon
   ```

2. **Create your first workflow** in n8n

3. **Test the integration** using the demo script

4. **Monitor the system** using the provided endpoints

The n8n workflow integration is now ready for production use!
