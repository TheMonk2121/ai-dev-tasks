<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MEMORY_CONTEXT: HIGH - Deployment procedures and environment management -->
# 🚀 Deployment & Environment Guide

## 🚀 Deployment & Environment Guide

<!-- ANCHOR: tldr -->
{#tldr}

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: End-to-end deployment patterns and environment setup.

- **read when**: Preparing environments or planning a deploy/rollback.

- **do next**: Use `#⚡ Quick Start` for env setup; review `#🏗️ Deployment Architecture` and `#🚀 Deployment Procedures`.

- **anchors**: `tldr`, `quick-start`, `deployment architecture`, `environment setup`, `deployment procedures`, `monitoring & health checks`, `rollback procedures`

<!-- ANCHOR: quick-start -->
{#quick-start}

## 🎯 **Current Status**-**Status**: ✅ **ACTIVE**- Deployment procedures maintained

- **Priority**: 🔥 Critical - Production deployment safety

- **Points**: 4 - Moderate complexity, high importance

- **Dependencies**: 400_guides/400_context-priority-guide.md, 200_setup/202_setup-requirements.md

- **Next Steps**: Update procedures as infrastructure evolves

## ⚡ Quick Start

### **Development Environment**```python

# Development environment configuration

DEV_CONFIG = {
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "ai_dev_db",
        "user": "dev_user",
        "password": "dev_password"
    },
    "ai_models": {
        "cursor-native-ai": "local"
    },
    "monitoring": {
        "level": "debug",
        "log_level": "DEBUG"
    },
    "security": {
        "auth_required": False,
        "rate_limiting": False
    }
}

```text

## **Staging Environment**```python

# Staging environment configuration

STAGING_CONFIG = {
    "database": {
        "host": "staging-db.example.com",
        "port": 5432,
        "name": "ai_staging_db",
        "user": "staging_user",
        "password": "staging_password"
    },
    "ai_models": {
        "cursor-native-ai": "staging-api"
    },
    "monitoring": {
        "level": "info",
        "log_level": "INFO"
    },
    "security": {
        "auth_required": True,
        "rate_limiting": True
    }
}

```text

## **Production Environment**```python

# Production environment configuration

PROD_CONFIG = {
    "database": {
        "host": "prod-db.example.com",
        "port": 5432,
        "name": "ai_prod_db",
        "user": "prod_user",
        "password": "prod_password"
    },
    "ai_models": {
        "cursor-native-ai": "production-api"
    },
    "monitoring": {
        "level": "warning",
        "log_level": "WARNING"
    },
    "security": {
        "auth_required": True,
        "rate_limiting": True,
        "ssl_required": True
    }
}

```text

- --

## 🏗️ Deployment Architecture

### **Deployment Architecture Overview**```text
┌─────────────────────────────────────────────────────────────┐
│                Deployment Architecture                     │
├─────────────────────────────────────────────────────────────┤
│ 1. Load Balancer (Nginx/HAProxy)                         │
│ 2. Application Servers (Multiple instances)               │
│ 3. Database Cluster (PostgreSQL with replication)        │
│ 4. Cache Layer (Redis cluster)                           │
│ 5. AI Model Servers (GPU-enabled instances)              │
│ 6. Monitoring Stack (Prometheus + Grafana)               │
│ 7. Logging Stack (ELK Stack)                             │
└─────────────────────────────────────────────────────────────┘

```text

### **Container Architecture**####**Docker Compose Configuration**```yaml

# docker-compose.yml

version: '3.8'

services:

  # Application services

  ai-app:
    build: .
    ports:

      - "5000:5000"

    environment:

      - ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}

    depends_on:

      - postgres
      - redis

    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "<http://localhost:5000/health">]
      interval: 30s
      timeout: 10s
      retries: 3

  # Database

  postgres:
    image: postgres:15
    environment:

      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

    volumes:

      - postgres_data:/var/lib/postgresql/data

    ports:

      - "5432:5432"

    restart: unless-stopped

  # Cache

  redis:
    image: redis:7-alpine
    ports:

      - "6379:6379"

    volumes:

      - redis_data:/data

    restart: unless-stopped

  # AI Model Service

  ai-models:
    build: ./ai-models
    ports:

      - "8000:8000"

    environment:

      - MODEL_PATH=/models

    volumes:

      - model_data:/models

    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:

            - driver: nvidia

              count: 1
              capabilities: [gpu]

  # Monitoring

  prometheus:
    image: prom/prometheus
    ports:

      - "9090:9090"

    volumes:

      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml

    restart: unless-stopped

  grafana:
    image: grafana/grafana
    ports:

      - "3000:3000"

    environment:

      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}

    volumes:

      - grafana_data:/var/lib/grafana

    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  model_data:
  grafana_data:

```text

## **Kubernetes Deployment**####**Kubernetes Manifests**```yaml

# k8s/deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-development-ecosystem
  namespace: ai-ecosystem
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-development-ecosystem
  template:
    metadata:
      labels:
        app: ai-development-ecosystem
    spec:
      containers:

      - name: ai-app

        image: ai-development-ecosystem:latest
        ports:

        - containerPort: 5000

        env:

        - name: DATABASE_URL

          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url

        - name: REDIS_URL

          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
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
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
- --
apiVersion: v1
kind: Service
metadata:
  name: ai-development-ecosystem-service
  namespace: ai-ecosystem
spec:
  selector:
    app: ai-development-ecosystem
  ports:

  - protocol: TCP

    port: 80
    targetPort: 5000
  type: LoadBalancer

```text

- --

## ⚙️ Environment Setup

### **1. Development Environment Setup**####**Local Development Setup**```bash

# !/bin/bash

# setup-dev.sh

echo "🚀 Setting up Development Environment"

# Create virtual environment

python -m venv venv
source venv/bin/activate

# Install dependencies

pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup database

echo "Setting up PostgreSQL database..."
createdb ai_dev_db

# Run migrations

python manage.py migrate

# Setup environment variables

cp .env.example .env
echo "Please update .env with your local configuration"

# Setup AI models (lightweight validation)

echo "Validating AI model environment..."
python3 scripts/setup_ai_models.py --check-db --dsn "$POSTGRES_DSN"

# Run tests

echo "Running tests..."
pytest tests/

echo "✅ Development environment setup complete!"

```text

## **Development Environment Variables**```bash

# .env.development

ENV=development
DEBUG=True
DATABASE_URL=postgresql://dev_user:dev_password@localhost:5432/ai_dev_db
REDIS_URL=redis://localhost:6379/0

# AI Models (Cursor-native)

CURSOR_NATIVE_AI_URL=<http://localhost:8000>

# Security

SECRET_KEY=dev-secret-key-change-in-production
AUTH_REQUIRED=False
RATE_LIMITING=False

# Monitoring

LOG_LEVEL=DEBUG
MONITORING_ENABLED=True

```text

## **2. Staging Environment Setup**####**Staging Deployment Script**```bash

# !/bin/bash

# deploy-staging.sh

echo "🚀 Deploying to Staging Environment"

# Set environment

export ENV=staging

# Build Docker image

docker build -t ai-development-ecosystem:staging .

# Deploy to staging

docker-compose -f docker-compose.staging.yml up -d

# Run health checks

echo "Running health checks..."
./scripts/health-check.sh staging

# Run smoke tests

echo "Running smoke tests..."
pytest tests/smoke/ -v

echo "✅ Staging deployment complete!"

```text

## **Staging Environment Variables**```bash

# .env.staging

ENV=staging
DEBUG=False
DATABASE_URL=postgresql://staging_user:staging_password@staging-db:5432/ai_staging_db
REDIS_URL=redis://staging-redis:6379/0

# AI Models (Cursor-native)

CURSOR_NATIVE_AI_URL=<https://staging-ai-api.example.com>

# Security

SECRET_KEY=staging-secret-key
AUTH_REQUIRED=True
RATE_LIMITING=True

# Monitoring

LOG_LEVEL=INFO
MONITORING_ENABLED=True

```text

## **3. Production Environment Setup**####**Production Deployment Script**```bash

# !/bin/bash

# deploy-production.sh

echo "🚀 Deploying to Production Environment"

# Set environment

export ENV=production

# Validate deployment

echo "Validating deployment configuration..."
./scripts/validate-deployment.sh

# Backup current deployment

echo "Creating backup..."
./scripts/backup-production.sh

# Deploy new version

echo "Deploying new version..."
kubectl apply -f k8s/

# Wait for deployment

echo "Waiting for deployment to complete..."
kubectl rollout status deployment/ai-development-ecosystem

# Run health checks

echo "Running health checks..."
./scripts/health-check.sh production

# Run smoke tests

echo "Running smoke tests..."
pytest tests/smoke/ -v

# Update monitoring

echo "Updating monitoring..."
./scripts/update-monitoring.sh

echo "✅ Production deployment complete!"

```text

## **Production Environment Variables**```bash

# .env.production

ENV=production
DEBUG=False
DATABASE_URL=postgresql://prod_user:prod_password@prod-db:5432/ai_prod_db
REDIS_URL=redis://prod-redis:6379/0

# AI Models (Cursor-native)

CURSOR_NATIVE_AI_URL=<https://prod-ai-api.example.com>

# Security

SECRET_KEY=production-secret-key
AUTH_REQUIRED=True
RATE_LIMITING=True
SSL_REQUIRED=True

# Monitoring

LOG_LEVEL=WARNING
MONITORING_ENABLED=True

```text

- --

## 🚀 Deployment Procedures

### **1. Blue-Green Deployment**####**Blue-Green Deployment Script**```bash

# !/bin/bash

# blue-green-deploy.sh

echo "🔄 Starting Blue-Green Deployment"

# Determine current environment

CURRENT_ENV=$(kubectl get service ai-development-ecosystem-service -o jsonpath='{.spec.selector.environment}')

if [ "$CURRENT_ENV" = "blue" ]; then
    NEW_ENV="green"
    OLD_ENV="blue"
else
    NEW_ENV="blue"
    OLD_ENV="green"
fi

echo "Current environment: $CURRENT_ENV"
echo "Deploying to: $NEW_ENV"

# Deploy to new environment

kubectl apply -f k8s/deployment-$NEW_ENV.yaml

# Wait for new deployment to be ready

kubectl rollout status deployment/ai-development-ecosystem-$NEW_ENV

# Run health checks on new deployment

echo "Running health checks on new deployment..."
./scripts/health-check.sh $NEW_ENV

# Switch traffic to new environment

echo "Switching traffic to $NEW_ENV..."
kubectl patch service ai-development-ecosystem-service -p "{\"spec\":{\"selector\":{\"environment\":\"$NEW_ENV\"}}}"

# Verify traffic is switched

echo "Verifying traffic switch..."
sleep 10
./scripts/verify-traffic.sh $NEW_ENV

# Scale down old environment

echo "Scaling down $OLD_ENV environment..."
kubectl scale deployment ai-development-ecosystem-$OLD_ENV --replicas=0

echo "✅ Blue-Green deployment complete!"

```text

## **2. Rolling Deployment**####**Rolling Deployment Configuration**```yaml

# k8s/rolling-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-development-ecosystem
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: ai-development-ecosystem
  template:
    metadata:
      labels:
        app: ai-development-ecosystem
    spec:
      containers:

      - name: ai-app

        image: ai-development-ecosystem:latest
        ports:

        - containerPort: 5000

        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10

```text

## **3. Canary Deployment**####**Canary Deployment Script**```bash

# !/bin/bash

# canary-deploy.sh

echo "🐦 Starting Canary Deployment"

# Deploy canary with 10% traffic

echo "Deploying canary with 10% traffic..."
kubectl apply -f k8s/canary-deployment.yaml

# Wait for canary to be ready

kubectl rollout status deployment/ai-development-ecosystem-canary

# Run tests on canary

echo "Running tests on canary..."
./scripts/test-canary.sh

# Monitor canary performance

echo "Monitoring canary performance..."
./scripts/monitor-canary.sh

# If canary is successful, gradually increase traffic

if [ $? -eq 0 ]; then
    echo "Canary successful, increasing traffic..."

    # Increase to 25%

    kubectl patch service ai-development-ecosystem-service -p '{"spec":{"selector":{"version":"canary"}}}'
    sleep 30

    # Increase to 50%

    kubectl patch service ai-development-ecosystem-service -p '{"spec":{"selector":{"version":"canary"}}}'
    sleep 30

    # Increase to 100%

    kubectl patch service ai-development-ecosystem-service -p '{"spec":{"selector":{"version":"canary"}}}'

    # Remove old deployment

    kubectl delete deployment ai-development-ecosystem-stable

    echo "✅ Canary deployment successful!"
else
    echo "❌ Canary deployment failed, rolling back..."
    kubectl delete deployment ai-development-ecosystem-canary
    exit 1
fi

```text

- --

## ⚙️ Configuration Management

### **1. Environment Configuration**####**Configuration Management System**```python

# config/environment_manager.py

import os
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class EnvironmentConfig:
    """Environment configuration class"""
    name: str
    database_url: str
    redis_url: str
    ai_model_urls: Dict[str, str]
    security_settings: Dict[str, Any]
    monitoring_settings: Dict[str, Any]

class EnvironmentManager:
    """Manage environment configurations"""

    def __init__(self):
        self.environments = {
            "development": self._get_dev_config(),
            "staging": self._get_staging_config(),
            "production": self._get_production_config()
        }

    def get_config(self, env_name: str) -> EnvironmentConfig:
        """Get configuration for environment"""
        if env_name not in self.environments:
            raise ValueError(f"Unknown environment: {env_name}")

        return self.environments[env_name]

    def _get_dev_config(self) -> EnvironmentConfig:
        """Get development configuration"""
        return EnvironmentConfig(
            name="development",
            database_url=os.getenv("DEV_DATABASE_URL", "postgresql://dev_user:dev_password@localhost:5432/ai_dev_db"),
            redis_url=os.getenv("DEV_REDIS_URL", "redis://localhost:6379/0"),
            ai_model_urls={
                "cursor-native-ai": os.getenv("DEV_CURSOR_NATIVE_AI_URL", "<http://localhost:8000">)
            },
            security_settings={
                "auth_required": False,
                "rate_limiting": False,
                "ssl_required": False
            },
            monitoring_settings={
                "log_level": "DEBUG",
                "monitoring_enabled": True
            }
        )

    def _get_staging_config(self) -> EnvironmentConfig:
        """Get staging configuration"""
        return EnvironmentConfig(
            name="staging",
            database_url=os.getenv("STAGING_DATABASE_URL"),
            redis_url=os.getenv("STAGING_REDIS_URL"),
            ai_model_urls={
                "cursor-native-ai": os.getenv("STAGING_CURSOR_NATIVE_AI_URL")
            },
            security_settings={
                "auth_required": True,
                "rate_limiting": True,
                "ssl_required": False
            },
            monitoring_settings={
                "log_level": "INFO",
                "monitoring_enabled": True
            }
        )

    def _get_production_config(self) -> EnvironmentConfig:
        """Get production configuration"""
        return EnvironmentConfig(
            name="production",
            database_url=os.getenv("PROD_DATABASE_URL"),
            redis_url=os.getenv("PROD_REDIS_URL"),
            ai_model_urls={
                "cursor-native-ai": os.getenv("PROD_CURSOR_NATIVE_AI_URL")
            },
            security_settings={
                "auth_required": True,
                "rate_limiting": True,
                "ssl_required": True
            },
            monitoring_settings={
                "log_level": "WARNING",
                "monitoring_enabled": True
            }
        )

```text

## **2. Secrets Management**####**Kubernetes Secrets**```yaml

# k8s/secrets.yaml

apiVersion: v1
kind: Secret
metadata:
  name: db-secret
  namespace: ai-ecosystem
type: Opaque
data:
  url: cG9zdGdyZXNxbDovL3Byb2RfdXNlcjpwcm9kX3Bhc3N3b3JkQHByb2QtZGI6NTQzMi9haV9wcm9kX2Ri
  username: cHJvZF91c2Vy
  password: cHJvZF9wYXNzd29yZAo=
- --
apiVersion: v1
kind: Secret
metadata:
  name: redis-secret
  namespace: ai-ecosystem
type: Opaque
data:
  url: cmVkaXM6Ly9wcm9kLXJlZGlzOjYzNzkvMAo=
- --
apiVersion: v1
kind: Secret
metadata:
  name: ai-api-secret
  namespace: ai-ecosystem
type: Opaque
data:
  cursor-native-ai-url: aHR0cHM6Ly9jdXJzb3ItbmF0aXZlLWFpLmV4YW1wbGUuY29tCg==
  cursor-native-ai-url: aHR0cHM6Ly9wcm9kLWFpLWFwaS5leGFtcGxlLmNvbQo=

```text

## **Secrets Management Script**```bash

# !/bin/bash

# manage-secrets.sh

echo "🔐 Managing Secrets"

# Create secrets for different environments

create_secrets() {
    local env=$1

    echo "Creating secrets for $env environment..."

    # Database secrets

    kubectl create secret generic db-secret-$env \
        - -from-literal=url="$DATABASE_URL" \
        - -from-literal=username="$DB_USERNAME" \
        - -from-literal=password="$DB_PASSWORD" \
        - -namespace=ai-ecosystem

    # Redis secrets

    kubectl create secret generic redis-secret-$env \
        - -from-literal=url="$REDIS_URL" \
        - -namespace=ai-ecosystem

    # AI API secrets

    kubectl create secret generic ai-api-secret-$env \
        - -from-literal=cursor-native-ai-url="$CURSOR_NATIVE_AI_URL" \
        - -namespace=ai-ecosystem

    echo "✅ Secrets created for $env environment"
}

# Update secrets

update_secrets() {
    local env=$1

    echo "Updating secrets for $env environment..."

    # Update database secrets

    kubectl patch secret db-secret-$env \
        - -type='json' \
        - p="[{\"op\": \"replace\", \"path\": \"/data/url\", \"value\": \"$DATABASE_URL\"}]" \
        - -namespace=ai-ecosystem

    echo "✅ Secrets updated for $env environment"
}

# Main script

case "$1" in
    "create")
        create_secrets "$2"
        ;;
    "update")
        update_secrets "$2"
        ;;*)
        echo "Usage: $0 {create|update} {development|staging|production}"
        exit 1
        ;;
esac

```text

- --

## 📊 Monitoring & Health Checks

### **1. Health Check Endpoints**####**Health Check Implementation**```python

# health_checks.py

from flask import Flask, jsonify
import psycopg2
import redis
import requests
import time

app = Flask(__name__)

def check_database():
    """Check database connectivity"""
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        return False

def check_redis():
    """Check Redis connectivity"""
    try:
        r = redis.from_url(os.getenv("REDIS_URL"))
        r.ping()
        return True
    except Exception as e:
        return False

def check_ai_models():
    """Check AI model availability (Cursor-native)"""
    try:
        cursor_native_response = requests.get(f"{os.getenv('CURSOR_NATIVE_AI_URL')}/health", timeout=5)
        return cursor_native_response.status_code == 200
    except Exception:
        return False

@app.route('/health')
def health_check():
    """Comprehensive health check"""
    checks = {
        "database": check_database(),
        "redis": check_redis(),
        "ai_models": check_ai_models(),
        "timestamp": time.time()
    }

    overall_status = all(checks.values())
    status_code = 200 if overall_status else 503

    return jsonify({
        "status": "healthy" if overall_status else "unhealthy",
        "checks": checks
    }), status_code

@app.route('/ready')
def readiness_check():
    """Readiness check for Kubernetes"""
    checks = {
        "database": check_database(),
        "redis": check_redis()
    }

    overall_status = all(checks.values())
    status_code = 200 if overall_status else 503

    return jsonify({
        "status": "ready" if overall_status else "not_ready",
        "checks": checks
    }), status_code

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""

    # Implementation for Prometheus metrics

    pass

```text

## **2. Monitoring Dashboard**####**Grafana Dashboard Configuration**```json
{
  "dashboard": {
    "title": "AI Development Ecosystem",
    "panels": [
      {
        "title": "Application Health",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"ai-development-ecosystem\"}",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "http_request_duration_seconds",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "AI Model Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "ai_model_response_time_seconds",
            "legendFormat": "{{model}}"
          }
        ]
      }
    ]
  }
}

```text

- --

## 🔄 Rollback Procedures

### **1. Automated Rollback**####**Rollback Script**```bash

# !/bin/bash

# rollback.sh

echo "🔄 Starting Rollback Procedure"

# Get current deployment

CURRENT_DEPLOYMENT=$(kubectl get deployment ai-development-ecosystem -o
jsonpath='{.spec.template.spec.containers[0].image}')

# Get previous deployment

PREVIOUS_DEPLOYMENT=$(kubectl rollout history deployment/ai-development-ecosystem --revision=1 -o
jsonpath='{.spec.template.spec.containers[0].image}')

echo "Current deployment: $CURRENT_DEPLOYMENT"
echo "Rolling back to: $PREVIOUS_DEPLOYMENT"

# Rollback deployment

kubectl rollout undo deployment/ai-development-ecosystem

# Wait for rollback to complete

kubectl rollout status deployment/ai-development-ecosystem

# Run health checks

echo "Running health checks after rollback..."
./scripts/health-check.sh production

# Verify rollback

if [ $? -eq 0 ]; then
    echo "✅ Rollback successful!"
else
    echo "❌ Rollback failed!"
    exit 1
fi

```text

## **2. Database Rollback**####**Database Rollback Script**```bash

# !/bin/bash

# rollback-database.sh

echo "🔄 Starting Database Rollback"

# Create backup before rollback

echo "Creating backup..."
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Get list of migrations to rollback

MIGRATIONS_TO_ROLLBACK=$(python manage.py showmigrations --list | grep "\[X\]" | tail -5 | awk '{print $2}')

echo "Rolling back migrations: $MIGRATIONS_TO_ROLLBACK"

# Rollback migrations

for migration in $MIGRATIONS_TO_ROLLBACK; do
    echo "Rolling back migration: $migration"
    python manage.py migrate --fake $migration
done

echo "✅ Database rollback complete!"

```bash

- --

## 🔒 Security Deployment

### **1. SSL/TLS Configuration**####**SSL Certificate Management**```bash

# !/bin/bash

# setup-ssl.sh

echo "🔒 Setting up SSL/TLS"

# Generate self-signed certificate for development

if [ "$ENV" = "development" ]; then
    echo "Generating self-signed certificate for development..."
    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
fi

# Configure SSL for production

if [ "$ENV" = "production" ]; then
    echo "Configuring SSL for production..."

    # Install Let's Encrypt certificate

    certbot --nginx -d ai-ecosystem.example.com

    # Configure automatic renewal

    echo "0 12* * */usr/bin/certbot renew --quiet" | crontab -
fi

echo "✅ SSL/TLS setup complete!"

```text

## **2. Security Headers**####**Security Headers Configuration**```python

# security_headers.py

from flask import Flask
from flask_talisman import Talisman

app = Flask(__name__)

# Configure security headers

Talisman(app,
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data: https:",
        'font-src': "'self' https:",
    },
    force_https=True,
    strict_transport_security=True,
    session_cookie_secure=True,
    session_cookie_httponly=True
)

```text

- --

## ⚡ Performance Optimization

### **1. Resource Optimization**####**Resource Limits Configuration**```yaml

# k8s/resource-limits.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-development-ecosystem
spec:
  template:
    spec:
      containers:

      - name: ai-app

        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        env:

        - name: PYTHONUNBUFFERED

          value: "1"

        - name: PYTHONDONTWRITEBYTECODE

          value: "1"

```text

## **2. Caching Configuration**####**Redis Caching Setup**

```python

# caching_config.py

import redis
from functools import wraps
import json

# Redis connection

redis_client = redis.from_url(os.getenv("REDIS_URL"))

def cache_result(ttl=3600):
    """Cache decorator for function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            # Generate cache key

            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache

            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)

            # Execute function

            result = func(*args, **kwargs)

            # Cache result

            redis_client.setex(cache_key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator

```text

- --

## 🔧 Troubleshooting

### **1. Common Deployment Issues**####**Troubleshooting Guide**```bash

# !/bin/bash

# troubleshoot.sh

echo "🔧 Troubleshooting Deployment Issues"

# Check pod status

check_pods() {
    echo "Checking pod status..."
    kubectl get pods -n ai-ecosystem

    # Check pod logs

    echo "Checking pod logs..."
    kubectl logs -n ai-ecosystem deployment/ai-development-ecosystem --tail=50
}

# Check service status

check_services() {
    echo "Checking service status..."
    kubectl get services -n ai-ecosystem

    # Check endpoints

    echo "Checking endpoints..."
    kubectl get endpoints -n ai-ecosystem
}

# Check database connectivity

check_database() {
    echo "Checking database connectivity..."
    kubectl exec -n ai-ecosystem deployment/ai-development-ecosystem -- \
        python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
}

# Check AI model connectivity

check_ai_models() {
    echo "Checking AI model connectivity..."
    kubectl exec -n ai-ecosystem deployment/ai-development-ecosystem -- \
        curl -f "$CURSOR_NATIVE_AI_URL/health"
}

# Main troubleshooting

case "$1" in
    "pods")
        check_pods
        ;;
    "services")
        check_services
        ;;
    "database")
        check_database
        ;;
    "ai-models")
        check_ai_models
        ;;
    "all")
        check_pods
        check_services
        check_database
        check_ai_models
        ;;*)
        echo "Usage: $0 {pods|services|database|ai-models|all}"
        exit 1
        ;;
esac

```text

## **2. Performance Troubleshooting**####**Performance Analysis Script**```bash

# !/bin/bash

# performance-analysis.sh

echo "📊 Performance Analysis"

# Check CPU usage

echo "CPU Usage:"
kubectl top pods -n ai-ecosystem

# Check memory usage

echo "Memory Usage:"
kubectl top pods -n ai-ecosystem --containers

# Check network usage

echo "Network Usage:"
kubectl exec -n ai-ecosystem deployment/ai-development-ecosystem -- \
    netstat -i

# Check disk usage

echo "Disk Usage:"
kubectl exec -n ai-ecosystem deployment/ai-development-ecosystem -- \
    df -h

# Check application metrics

echo "Application Metrics:"
kubectl exec -n ai-ecosystem deployment/ai-development-ecosystem -- \
    curl -s <http://localhost:5000/metrics>

```bash

- --

## 📋 Deployment Checklist

### **Pre-Deployment Checklist**- [ ] All tests pass (unit, integration, e2e)

- [ ] Code review completed

- [ ] Security scan passed

- [ ] Performance benchmarks met

- [ ] Documentation updated

- [ ] Environment variables configured

- [ ] Secrets updated

- [ ] Database migrations ready

- [ ] Backup completed

### **Deployment Checklist**- [ ] Health checks pass

- [ ] Smoke tests pass

- [ ] Monitoring configured

- [ ] Logging configured

- [ ] SSL certificates valid

- [ ] Load balancer configured

- [ ] Auto-scaling configured

- [ ] Rollback plan ready

### **Post-Deployment Checklist**- [ ] Application responding correctly

- [ ] Database connections stable

- [ ] AI models accessible

- [ ] Monitoring alerts configured

- [ ] Performance metrics normal

- [ ] Error rates acceptable

- [ ] User acceptance testing passed

- [ ] Documentation updated

- --

## 🛠️ Deployment Tools

### **1. Deployment Automation**####**Deployment Pipeline Script**```bash

# !/bin/bash

# deploy-pipeline.sh

echo "🚀 Starting Deployment Pipeline"

# Validate deployment

echo "Step 1: Validating deployment..."
./scripts/validate-deployment.sh
if [ $? -ne 0 ]; then
    echo "❌ Deployment validation failed"
    exit 1
fi

# Run tests

echo "Step 2: Running tests..."
./scripts/run-tests.sh
if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi

# Build image

echo "Step 3: Building Docker image..."
docker build -t ai-development-ecosystem:$VERSION .
if [ $? -ne 0 ]; then
    echo "❌ Docker build failed"
    exit 1
fi

# Deploy to staging

echo "Step 4: Deploying to staging..."
./scripts/deploy-staging.sh
if [ $? -ne 0 ]; then
    echo "❌ Staging deployment failed"
    exit 1
fi

# Run staging tests

echo "Step 5: Running staging tests..."
./scripts/test-staging.sh
if [ $? -ne 0 ]; then
    echo "❌ Staging tests failed"
    exit 1
fi

# Deploy to production

echo "Step 6: Deploying to production..."
./scripts/deploy-production.sh
if [ $? -ne 0 ]; then
    echo "❌ Production deployment failed"
    exit 1
fi

# Verify production

echo "Step 7: Verifying production deployment..."
./scripts/verify-production.sh
if [ $? -ne 0 ]; then
    echo "❌ Production verification failed"
    exit 1
fi

echo "✅ Deployment pipeline completed successfully!"

```text

## **2. Environment Management**####**Environment Management Script**```bash

# !/bin/bash

# manage-environments.sh

echo "🌍 Environment Management"

# Create environment

create_environment() {
    local env_name=$1

    echo "Creating environment: $env_name"

    # Create namespace

    kubectl create namespace ai-ecosystem-$env_name

    # Apply configurations

    kubectl apply -f k8s/ -n ai-ecosystem-$env_name

    # Setup monitoring

    kubectl apply -f monitoring/ -n ai-ecosystem-$env_name

    echo "✅ Environment $env_name created"
}

# Delete environment

delete_environment() {
    local env_name=$1

    echo "Deleting environment: $env_name"

    # Delete namespace (this will delete all resources)

    kubectl delete namespace ai-ecosystem-$env_name

    echo "✅ Environment $env_name deleted"
}

# Main script

case "$1" in
    "create")
        create_environment "$2"
        ;;
    "delete")
        delete_environment "$2"
        ;;*)
        echo "Usage: $0 {create|delete} {environment_name}"
        exit 1
        ;;
esac

```

- --

## 📚 Additional Resources

### **Deployment Documentation**-**Kubernetes Documentation**: <https://kubernetes.io/docs/>

- **Docker Documentation**: <https://docs.docker.com/>

- **Helm Documentation**: <https://helm.sh/docs/>

### **Monitoring Tools**-**Prometheus**: <https://prometheus.io/>

- **Grafana**: <https://grafana.com/>

- **ELK Stack**: <https://www.elastic.co/elk-stack>

### **Deployment Best Practices**-**12-Factor App**: <https://12factor.net/>

- **GitOps**: <https://www.gitops.tech/>

- **Infrastructure as Code**: <https://www.terraform.io/>

- --

- Last Updated: 2024-08-07*
- Next Review: Monthly*
- Deployment Level: Production Ready*
