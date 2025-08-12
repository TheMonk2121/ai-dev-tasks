<!-- MODULE_REFERENCE: 400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_migration-upgrade-guide.md -->
<!-- MODULE_REFERENCE: 400_performance-optimization-guide.md -->
<!-- MODULE_REFERENCE: docs/100_ai-development-ecosystem.md -->
# B-011: Cursor Native AI + Specialized Agents Integration - Deployment Guide

## 📖 Overview

This document provides comprehensive deployment documentation and procedures for the AI Development Ecosystem with Cursor Native AI integration and specialized agents. It covers production deployment, monitoring, troubleshooting, and maintenance procedures.

- *Version**: 1.0.0  
- *Last Updated**: 2024-08-07  
- *Status**: Production Ready

- --

## 🚀 Deployment Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS 10.15+, Windows 10+
- **Python**: 3.9+ with pip
- **Memory**: 4GB+ RAM (8GB+ recommended)
- **Storage**: 10GB+ available space
- **Network**: Internet connection for model downloads

### Software Dependencies
```bash
# Core dependencies
python>=3.9
pip>=21.0
git>=2.25

# Optional dependencies for production
docker>=20.10
docker-compose>=1.29
pm2>=5.0 (for Node.js process management)
nginx>=1.18 (for reverse proxy)
```text

### Environment Setup
```bash
# Create deployment user
sudo useradd -m -s /bin/bash ai-ecosystem
sudo usermod -aG docker ai-ecosystem

# Set up directories
sudo mkdir -p /opt/ai-ecosystem
sudo chown ai-ecosystem:ai-ecosystem /opt/ai-ecosystem

# Install Python dependencies
sudo apt update
sudo apt install -y python3.9 python3.9-venv python3.9-dev
```text

- --

## 🔧 Local Development Deployment

### Step 1: Environment Setup
```bash
# Clone repository
git clone <https://github.com/TheMonk2121/ai-dev-tasks.git>
cd ai-dev-tasks

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```text

### Step 2: Configuration
```bash
# Create configuration directory
mkdir -p config

# Create settings file
cat > config/settings.yaml << EOF
environment: development
logging:
  level: INFO
  file: logs/ai_ecosystem.log
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

performance:
  agent_switch_timeout: 2.0
  context_load_timeout: 1.0
  max_memory_mb: 100
  max_concurrent_agents: 10

security:
  input_validation: true
  prompt_sanitization: true
  max_file_size_mb: 10

database:
  path: context_store.db
  backup_enabled: true
  backup_interval_hours: 24
EOF
```text

### Step 3: Database Initialization
```bash
# Initialize database
python -c "
from context_management_implementation import ContextManager
manager = ContextManager()
print('Database initialized successfully')
"

# Verify database
python -c "
import sqlite3
conn = sqlite3.connect('context_store.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
tables = cursor.fetchall()
print(f'Database tables: {tables}')
conn.close()
"
```text

### Step 4: Verification
```bash
# Run setup verification
python setup_verification.py

# Run tests
pytest tests/ -v

# Run performance tests
python test_performance_optimization.py

# Start development server
python main.py --dev
```text

- --

## 🏭 Production Deployment

### Method 1: Direct Deployment

#### Step 1: Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.9 python3.9-venv python3.9-dev git nginx

# Create application user
sudo useradd -m -s /bin/bash ai-ecosystem
sudo usermod -aG sudo ai-ecosystem
```text

#### Step 2: Application Deployment
```bash
# Switch to application user
sudo su - ai-ecosystem

# Clone repository
git clone <https://github.com/TheMonk2121/ai-dev-tasks.git>
cd ai-dev-tasks

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create production configuration
mkdir -p config logs backup
```text

#### Step 3: Production Configuration
```bash
# Create production settings
cat > config/settings.yaml << EOF
environment: production
logging:
  level: WARNING
  file: logs/ai_ecosystem.log
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  max_size_mb: 100
  backup_count: 5

performance:
  agent_switch_timeout: 2.0
  context_load_timeout: 1.0
  max_memory_mb: 100
  max_concurrent_agents: 10
  monitoring_enabled: true
  alerting_enabled: true

security:
  input_validation: true
  prompt_sanitization: true
  max_file_size_mb: 10
  rate_limiting_enabled: true
  max_requests_per_minute: 100

database:
  path: /opt/ai-ecosystem/data/context_store.db
  backup_enabled: true
  backup_interval_hours: 6
  backup_retention_days: 30

monitoring:
  health_check_interval: 30
  performance_metrics_interval: 60
  alert_threshold_memory_mb: 80
  alert_threshold_response_time_ms: 5000
EOF

# Create data directory
sudo mkdir -p /opt/ai-ecosystem/data
sudo chown ai-ecosystem:ai-ecosystem /opt/ai-ecosystem/data
```text

#### Step 4: Service Configuration
```bash
# Create systemd service
sudo tee /etc/systemd/system/ai-ecosystem.service << EOF
[Unit]
Description=AI Development Ecosystem
After=network.target

[Service]
Type=simple
User=ai-ecosystem
Group=ai-ecosystem
WorkingDirectory=/home/ai-ecosystem/ai-dev-tasks
Environment=PATH=/home/ai-ecosystem/ai-dev-tasks/venv/bin
Environment=PYTHONPATH=/home/ai-ecosystem/ai-dev-tasks
ExecStart=/home/ai-ecosystem/ai-dev-tasks/venv/bin/python main.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ai-ecosystem
sudo systemctl start ai-ecosystem

# Check service status
sudo systemctl status ai-ecosystem
```text

#### Step 5: Nginx Configuration
```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/ai-ecosystem << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass <http://127.0.0.1:8000;>
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias /home/ai-ecosystem/ai-dev-tasks/static/;
    }

    location /health {
        proxy_pass <http://127.0.0.1:8000/health;>
        access_log off;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/ai-ecosystem /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```text

### Method 2: Docker Deployment

#### Step 1: Dockerfile
```dockerfile
# Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs backup data

# Create non-root user
RUN useradd -m -u 1000 ai-ecosystem && \
    chown -R ai-ecosystem:ai-ecosystem /app

# Switch to non-root user
USER ai-ecosystem

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('<http://localhost:8000/health'>)"

# Start application
CMD ["python", "main.py"]
```text

#### Step 2: Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  ai-ecosystem:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=WARNING
      - MAX_MEMORY_MB=100
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./backup:/app/backup
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('<http://localhost:8000/health'>)"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - ai-ecosystem
    restart: unless-stopped
```text

#### Step 3: Deployment Commands
```bash
# Build and start services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f ai-ecosystem

# Scale services
docker-compose up -d --scale ai-ecosystem=3
```text

### Method 3: Kubernetes Deployment

#### Step 1: Namespace and ConfigMap
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-ecosystem
- --
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-ecosystem-config
  namespace: ai-ecosystem
data:
  settings.yaml: |
    environment: production
    logging:
      level: WARNING
      file: logs/ai_ecosystem.log
    performance:
      agent_switch_timeout: 2.0
      context_load_timeout: 1.0
      max_memory_mb: 100
      max_concurrent_agents: 10
```text

#### Step 2: Deployment
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-ecosystem
  namespace: ai-ecosystem
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-ecosystem
  template:
    metadata:
      labels:
        app: ai-ecosystem
    spec:
      containers:
      - name: ai-ecosystem
        image: ai-ecosystem:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "WARNING"
        - name: MAX_MEMORY_MB
          value: "100"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: config
          mountPath: /app/config
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: config
        configMap:
          name: ai-ecosystem-config
      - name: data
        persistentVolumeClaim:
          claimName: ai-ecosystem-data
      - name: logs
        emptyDir: {}
```text

#### Step 3: Service and Ingress
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-ecosystem-service
  namespace: ai-ecosystem
spec:
  selector:
    app: ai-ecosystem
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
- --
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-ecosystem-ingress
  namespace: ai-ecosystem
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: ai-ecosystem.your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ai-ecosystem-service
            port:
              number: 80
```text

#### Step 4: Deployment Commands
```bash
# Apply Kubernetes resources
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/persistent-volume.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Check deployment status
kubectl get pods -n ai-ecosystem
kubectl get services -n ai-ecosystem
kubectl get ingress -n ai-ecosystem

# View logs
kubectl logs -f deployment/ai-ecosystem -n ai-ecosystem
```text

- --

## 📊 Monitoring & Alerting

### Health Checks
```python
# health_check.py
import requests
import time
import json

def check_health():
    """Check application health."""
    try:
        response = requests.get("<http://localhost:8000/health",> timeout=10)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return False, {"error": str(e)}

def check_performance():
    """Check performance metrics."""
    try:
        response = requests.get("<http://localhost:8000/api/performance/report",> timeout=10)
        if response.status_code == 200:
            metrics = response.json()
            
            # Check memory usage
            memory_mb = metrics["metrics"]["memory_usage"]["current"]
            if memory_mb > 80:
                return False, {"error": f"High memory usage: {memory_mb}MB"}
            
            # Check response time
            response_time = metrics["metrics"]["response_time"]["current"]
            if response_time > 5.0:
                return False, {"error": f"High response time: {response_time}s"}
            
            return True, metrics
        else:
            return False, {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return False, {"error": str(e)}
```text

### Monitoring Script
```bash
# !/bin/bash
# scripts/monitor.sh

LOG_FILE="/var/log/ai-ecosystem-monitor.log"
ALERT_EMAIL="admin@your-domain.com"

# Check application health
check_health() {
    python3 -c "
import requests
try:
    response = requests.get('<http://localhost:8000/health',> timeout=10)
    if response.status_code == 200:
        print('HEALTHY')
    else:
        print('UNHEALTHY')
except Exception as e:
    print('ERROR')
"
}

# Check performance
check_performance() {
    python3 -c "
import requests
try:
    response = requests.get('<http://localhost:8000/api/performance/report',> timeout=10)
    if response.status_code == 200:
        metrics = response.json()
        memory_mb = metrics['metrics']['memory_usage']['current']
        if memory_mb > 80:
            print('PERFORMANCE_WARNING')
        else:
            print('PERFORMANCE_OK')
    else:
        print('PERFORMANCE_ERROR')
except Exception as e:
    print('PERFORMANCE_ERROR')
"
}

# Main monitoring loop
while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Health check
    health_status=$(check_health)
    if [ "$health_status" != "HEALTHY" ]; then
        echo "$timestamp - Health check failed: $health_status" >> "$LOG_FILE"
        echo "Health check failed at $timestamp" | mail -s "AI Ecosystem Alert" "$ALERT_EMAIL"
    fi
    
    # Performance check
    perf_status=$(check_performance)
    if [ "$perf_status" != "PERFORMANCE_OK" ]; then
        echo "$timestamp - Performance warning: $perf_status" >> "$LOG_FILE"
        if [ "$perf_status" = "PERFORMANCE_WARNING" ]; then
            echo "Performance warning at $timestamp" | mail -s "AI Ecosystem Performance Alert" "$ALERT_EMAIL"
        fi
    fi
    
    sleep 60
done
```text

### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai-ecosystem'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s
```text

### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "AI Ecosystem Dashboard",
    "panels": [
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "ai_ecosystem_memory_usage_mb",
            "legendFormat": "Memory (MB)"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "ai_ecosystem_response_time_seconds",
            "legendFormat": "Response Time (s)"
          }
        ]
      },
      {
        "title": "Active Agents",
        "type": "stat",
        "targets": [
          {
            "expr": "ai_ecosystem_concurrent_agents",
            "legendFormat": "Active Agents"
          }
        ]
      }
    ]
  }
}
```markdown

- --

## 🛠️ Troubleshooting Guide

### Common Issues

#### Issue 1: Application Won't Start**Symptoms**: Service fails to start, logs show errors
- *Diagnosis**:
```bash
# Check service status
sudo systemctl status ai-ecosystem

# Check logs
sudo journalctl -u ai-ecosystem -f

# Check Python environment
source venv/bin/activate
python -c "import sys; print(sys.path)"
```markdown

- *Solutions**:
1. **Missing dependencies**: `pip install -r requirements.txt`
2. **Permission issues**: `sudo chown -R ai-ecosystem:ai-ecosystem /opt/ai-ecosystem`
3. **Database issues**: Reinitialize database
4. **Port conflicts**: Check if port 8000 is available

#### Issue 2: High Memory Usage
- *Symptoms**: Memory usage > 100MB, slow performance
- *Diagnosis**:
```bash
# Check memory usage
ps aux | grep python
free -h

# Check performance metrics
curl <http://localhost:8000/api/performance/report>
```markdown

- *Solutions**:
1. **Restart application**: `sudo systemctl restart ai-ecosystem`
2. **Clear caches**: Restart to clear agent and context caches
3. **Reduce concurrent agents**: Update configuration
4. **Memory optimization**: Check for memory leaks

#### Issue 3: Agent Not Responding
- *Symptoms**: Agent requests timeout or fail
- *Diagnosis**:
```bash
# Check agent status
curl <http://localhost:8000/api/agents/status>

# Check agent logs
tail -f logs/ai_ecosystem.log | grep -i agent
```markdown

- *Solutions**:
1. **Restart agent framework**: Restart the application
2. **Check agent configuration**: Verify agent settings
3. **Clear agent cache**: Restart to clear agent cache
4. **Check dependencies**: Ensure all agent dependencies are installed

#### Issue 4: Database Errors
- *Symptoms**: Context operations fail, database errors in logs
- *Diagnosis**:
```bash
# Check database file
ls -la context_store.db

# Check database integrity
sqlite3 context_store.db "PRAGMA integrity_check;"

# Check database size
du -h context_store.db
```markdown

- *Solutions**:
1. **Database corruption**: Restore from backup
2. **Permission issues**: Fix file permissions
3. **Disk space**: Check available disk space
4. **Database locks**: Restart application

#### Issue 5: Performance Issues
- *Symptoms**: Slow response times, high latency
- *Diagnosis**:
```bash
# Check performance metrics
curl <http://localhost:8000/api/performance/report>

# Check system resources
top
iostat 1 5
```markdown

- *Solutions**:
1. **Optimize configuration**: Adjust performance settings
2. **Scale horizontally**: Add more instances
3. **Optimize database**: Add indexes, optimize queries
4. **Resource limits**: Increase memory/CPU limits

### Debugging Commands
```bash
# Check application status
sudo systemctl status ai-ecosystem

# View real-time logs
sudo journalctl -u ai-ecosystem -f

# Check performance
curl -s <http://localhost:8000/api/performance/report> | jq

# Check health
curl -s <http://localhost:8000/health>

# Check agent status
curl -s <http://localhost:8000/api/agents/status>

# Check database
sqlite3 context_store.db ".tables"

# Check memory usage
ps aux | grep python | grep -v grep

# Check network connections
netstat -tlnp | grep 8000

# Check disk usage
df -h
du -sh /opt/ai-ecosystem/data/
```text

- --

## 🔄 Backup & Recovery

### Backup Procedures
```bash
# !/bin/bash
# scripts/backup.sh

BACKUP_DIR="/opt/ai-ecosystem/backup"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Database backup
sqlite3 context_store.db ".backup $BACKUP_DIR/context_store_$DATE.db"

# Configuration backup
cp config/settings.yaml "$BACKUP_DIR/settings_$DATE.yaml"

# Log backup
tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" logs/

# Application backup
tar -czf "$BACKUP_DIR/app_$DATE.tar.gz" --exclude=venv --exclude=__pycache__ .

# Clean old backups (keep last 30 days)
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.yaml" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```text

### Recovery Procedures
```bash
# !/bin/bash
# scripts/recover.sh

BACKUP_DIR="/opt/ai-ecosystem/backup"
RESTORE_DATE="$1"

if [ -z "$RESTORE_DATE" ]; then
    echo "Usage: $0 <backup_date>"
    echo "Available backups:"
    ls -la "$BACKUP_DIR"/*.db | awk '{print $9}' | sed 's/.*context_store_\(.*\)\.db/\1/'
    exit 1
fi

# Stop application
sudo systemctl stop ai-ecosystem

# Restore database
cp "$BACKUP_DIR/context_store_$RESTORE_DATE.db" context_store.db

# Restore configuration
cp "$BACKUP_DIR/settings_$RESTORE_DATE.yaml" config/settings.yaml

# Restore logs
tar -xzf "$BACKUP_DIR/logs_$RESTORE_DATE.tar.gz"

# Start application
sudo systemctl start ai-ecosystem

echo "Recovery completed from backup: $RESTORE_DATE"
```text

### Automated Backup
```bash
# Add to crontab
# crontab -e
0 2 * * */opt/ai-ecosystem/scripts/backup.sh >> /var/log/ai-ecosystem-backup.log 2>&1
```text

- --

## 🔒 Security Hardening

### Firewall Configuration
```bash
# UFW firewall setup
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 8000/tcp  # Deny direct access to app port
sudo ufw enable
```bash

### SSL/TLS Configuration
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
0 12* * */usr/bin/certbot renew --quiet
```text

### Security Headers
```nginx
# nginx.conf
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass <http://127.0.0.1:8000;>
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```text

- --

## 📈 Performance Optimization

### Application Optimization
```python
# performance_config.py
import os

# Performance settings
PERFORMANCE_CONFIG = {
    "agent_cache_size": 50,
    "context_cache_size": 1000,
    "max_concurrent_requests": 100,
    "request_timeout": 30,
    "memory_limit_mb": 100,
    "gc_threshold": 0.8,
    "log_level": "WARNING",
    "monitoring_interval": 60,
}

# Environment-specific settings
if os.getenv("ENVIRONMENT") == "production":
    PERFORMANCE_CONFIG.update({
        "log_level": "ERROR",
        "monitoring_interval": 30,
        "memory_limit_mb": 200,
    })
```text

### Database Optimization
```sql
- - Database optimization
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = 10000;
PRAGMA temp_store = MEMORY;

- - Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_contexts_type ON contexts(type);
CREATE INDEX IF NOT EXISTS idx_contexts_created_at ON contexts(created_at);
CREATE INDEX IF NOT EXISTS idx_contexts_owner_id ON contexts(owner_id);
```text

### System Optimization
```bash
# /etc/sysctl.conf optimizations
echo "net.core.somaxconn = 65535" >> /etc/sysctl.conf
echo "net.ipv4.tcp_max_syn_backlog = 65535" >> /etc/sysctl.conf
echo "vm.swappiness = 10" >> /etc/sysctl.conf
echo "vm.dirty_ratio = 15" >> /etc/sysctl.conf
echo "vm.dirty_background_ratio = 5" >> /etc/sysctl.conf

# Apply changes
sudo sysctl -p
```

- --

## 📞 Support & Maintenance

### Maintenance Schedule
- **Daily**: Monitor logs, check performance metrics
- **Weekly**: Review error patterns, update dependencies
- **Monthly**: Security updates, performance optimization
- **Quarterly**: Major updates, backup testing

### Support Contacts
- **Technical Issues**: tech-support@your-domain.com
- **Performance Issues**: performance@your-domain.com
- **Security Issues**: security@your-domain.com

### Documentation Updates
- Keep deployment guide updated with new procedures
- Document any custom configurations
- Maintain troubleshooting knowledge base
- Update monitoring and alerting procedures

- --

- This deployment guide is maintained as part of the AI Development Ecosystem project. For updates and contributions, see the project repository.*
