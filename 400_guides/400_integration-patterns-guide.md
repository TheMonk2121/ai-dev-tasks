<!-- DATABASE_SYNC: REQUIRED -->

<!-- CONTEXT_REFERENCE: 400_guides/400_cursor-context-engineering-guide.md -->

<!-- MEMORY_CONTEXT: HIGH - Integration patterns and API design -->

# 🔌 Integration Patterns Guide

## 🔌 Integration Patterns Guide

<!-- ANCHOR: tldr -->

{#tldr}

## 🎯 **Current Status**-**Status**: OK **ACTIVE**- Integration patterns maintained

- **Priority**: 🔥 Critical - System integration and API design

- **Points**: 5 - High complexity, essential for system operation

- **Dependencies**: 400_guides/400_cursor-context-engineering-guide.md,
  400_guides/400_system-overview.md

- **Next Steps**: Update patterns as new integrations are added

## 🔎 TL;DR

| what this file is | read when | do next |
|-------------------|-----------|---------|
|                   |           |         |

- **what this file is**: Integration patterns and API design for
  components and external systems.

- **read when**: Designing or modifying APIs, events, websockets, or
  cross-component flows.

- **do next**: See “API Design Principles”, “Component Integration”, and
  “Communication Patterns”.

- **anchors**: `api design principles`, `component integration`,
  `communication patterns`, `data flow`, `error handling`,
  `security integration`

------------------------------------------------------------------------

## 🔌 API Design Principles

### **1. RESTful API Design**\#### Context API (summary)

``` http

# Create context

POST /api/context { type, content, relationships }

# Get / Update / Delete context

GET|PUT|DELETE /api/context/{id}

# Search

GET /api/context/search?query=...&type=...

# Relationships

POST /api/context/{id}/relationships { target_context_id, relationship_type, strength }
GET /api/context/{id}/relationships

```text

## **Core Endpoints**```python

## AI Model API endpoints

AI_MODEL_ENDPOINTS = {
    "generate": "/api/v1/ai/generate",
    "chat": "/api/v1/ai/chat",
    "code": "/api/v1/ai/code",
    "analyze": "/api/v1/ai/analyze"
}

## Database API endpoints

DATABASE_ENDPOINTS = {
    "logs": "/api/v1/db/logs",
    "vectors": "/api/v1/db/vectors",
    "metrics": "/api/v1/db/metrics"
}

## Workflow API endpoints

WORKFLOW_ENDPOINTS = {
    "execute": "/api/v1/workflow/execute",
    "status": "/api/v1/workflow/status",
    "history": "/api/v1/workflow/history"
}

```text

## **API Response Format**```python

# Standard API response structure

API_RESPONSE_FORMAT = {
    "success": bool,
    "data": dict,
    "error": str,
    "timestamp": str,
    "request_id": str
}

# Example response

{
    "success": True,
    "data": {
        "response": "AI generated content",
        "model": "cursor-native-ai",
        "tokens_used": 150
    },
    "error": None,
    "timestamp": "2024-08-07T08:45:00Z",
    "request_id": "req_123456"
}

```text

## **2. GraphQL Integration**####**Schema Definition**```graphql

## AI Development Ecosystem GraphQL Schema

type Query {
    aiResponse(prompt: String!, model: String): AIResponse
    workflowStatus(id: ID!): WorkflowStatus
    systemMetrics: SystemMetrics
    userLogs(userId: ID!): [LogEntry]
}

type AIResponse {
    content: String!
    model: String!
    tokensUsed: Int!
    responseTime: Float!
    timestamp: String!
}

type WorkflowStatus {
    id: ID!
    status: String!
    progress: Float!
    result: String
    error: String
}

```text

## **3. WebSocket Communication**####**Real-time Updates**```python

# WebSocket message format

WEBSOCKET_MESSAGE_FORMAT = {
    "type": "update|error|complete",
    "component": "ai|workflow|dashboard",
    "data": dict,
    "timestamp": str
}

# WebSocket event handlers

WEBSOCKET_EVENTS = {
    "ai_generation_start": handle_ai_generation_start,
    "ai_generation_progress": handle_ai_generation_progress,
    "ai_generation_complete": handle_ai_generation_complete,
    "workflow_execution_start": handle_workflow_execution_start,
    "workflow_execution_progress": handle_workflow_execution_progress,
    "workflow_execution_complete": handle_workflow_execution_complete
}

```text

- --

## 🔄 Component Integration

### **1. AI Model Integration**####**Model Interface**```python

## AI model integration interface

class AIModelInterface:
    def __init__(self, model_name: str, config: dict):
        self.model_name = model_name
        self.config = config
        self.client = self._initialize_client()

    def generate(self, prompt: str,**kwargs) -> dict:
        """Generate AI response"""
        try:
            response = self.client.generate(prompt, **kwargs)
            return {
                "success": True,
                "content": response.content,
                "tokens_used": response.tokens_used,
                "model": self.model_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.model_name
            }

    def chat(self, messages: list, **kwargs) -> dict:
        """Chat with AI model"""
        try:
            response = self.client.chat(messages, **kwargs)
            return {
                "success": True,
                "content": response.content,
                "tokens_used": response.tokens_used,
                "model": self.model_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self.model_name
            }

```text

## **Model Factory**```python

# AI model factory for different models

class AIModelFactory:
    @staticmethod
    def create_model(model_name: str) -> AIModelInterface:
        if model_name == "cursor-native-ai":
            return CursorNativeAIModel()
        elif model_name == "external-model":
            return ExternalModel()
        elif model_name == "specialized-agent":
            return SpecializedAgentModel()
        else:
            raise ValueError(f"Unknown model: {model_name}")

```text

## **2. Database Integration**####**Database Interface**```python

## Database integration interface

class DatabaseInterface:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = self._create_connection_pool()

    def execute_query(self, query: str, params: dict = None) -> dict:
        """Execute database query"""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                result = cursor.fetchall()
                return {
                    "success": True,
                    "data": result,
                    "row_count": len(result)
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def insert_log(self, log_entry: dict) -> dict:
        """Insert log entry"""
        query = """
        INSERT INTO episodic_logs
        (timestamp, user_id, model_type, prompt, response, tokens_used)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            log_entry["timestamp"],
            log_entry["user_id"],
            log_entry["model_type"],
            log_entry["prompt"],
            log_entry["response"],
            log_entry["tokens_used"]
        )
        return self.execute_query(query, params)

```text

## **3. n8n Workflow Integration**####**Workflow Interface**```python

# n8n workflow integration interface

class N8nWorkflowInterface:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key
        self.session = self._create_session()

    def execute_workflow(self, workflow_id: str, data: dict) -> dict:
        """Execute n8n workflow"""
        try:
            url = f"{self.base_url}/api/v1/workflows/{workflow_id}/execute"
            headers = {"Authorization": f"Bearer {self.api_key}"}

            response = self.session.post(url, json=data, headers=headers)
            response.raise_for_status()

            return {
                "success": True,
                "execution_id": response.json()["execution_id"],
                "status": "started"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_workflow_status(self, execution_id: str) -> dict:
        """Get workflow execution status"""
        try:
            url = f"{self.base_url}/api/v1/executions/{execution_id}"
            headers = {"Authorization": f"Bearer {self.api_key}"}

            response = self.session.get(url, headers=headers)
            response.raise_for_status()

            return {
                "success": True,
                "status": response.json()["status"],
                "result": response.json().get("result")
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

```text

- --

## 📡 Communication Patterns

### **1. Synchronous Communication**####**Request-Response Pattern**```python

## Synchronous request-response pattern

def synchronous_ai_request(prompt: str, model: str) -> dict:
    """Synchronous AI request"""
    try:

        ## Initialize AI model

        ai_model = AIModelFactory.create_model(model)

        ## Generate response

        response = ai_model.generate(prompt)

        ## Log interaction

        log_entry = {
            "timestamp": datetime.now(),
            "user_id": get_current_user_id(),
            "model_type": model,
            "prompt": prompt,
            "response": response["content"],
            "tokens_used": response["tokens_used"]
        }

        db_interface = DatabaseInterface(get_db_connection_string())
        db_interface.insert_log(log_entry)

        return response
    except Exception as e:
        return {"success": False, "error": str(e)}

```text

## **2. Asynchronous Communication**####**Event-Driven Pattern**```python

# Asynchronous event-driven pattern

class EventDrivenAI:
    def __init__(self):
        self.event_queue = Queue()
        self.workers = []
        self._start_workers()

    def submit_request(self, request: dict) -> str:
        """Submit asynchronous AI request"""
        request_id = generate_request_id()
        request["request_id"] = request_id

        # Add to event queue

        self.event_queue.put(request)

        return request_id

    def get_result(self, request_id: str) -> dict:
        """Get asynchronous request result"""

        # Check if result is ready

        result = self._get_cached_result(request_id)
        if result:
            return result

        # Check if still processing

        if self._is_processing(request_id):
            return {"status": "processing"}

        return {"status": "not_found"}

    def _start_workers(self):
        """Start background workers"""
        for _ in range(4):  # 4 worker threads

            worker = threading.Thread(target=self._worker_loop)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

    def _worker_loop(self):
        """Worker thread loop"""
        while True:
            try:
                request = self.event_queue.get(timeout=1)
                self._process_request(request)
            except Empty:
                continue

```text

## **3. Message Queue Pattern**####**Redis Message Queue**```python

## Redis message queue implementation

class RedisMessageQueue:
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.pubsub = self.redis_client.pubsub()

    def publish_event(self, channel: str, event: dict):
        """Publish event to channel"""
        try:
            self.redis_client.publish(channel, json.dumps(event))
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def subscribe_to_channel(self, channel: str, callback):
        """Subscribe to channel with callback"""
        try:
            self.pubsub.subscribe(channel)
            for message in self.pubsub.listen():
                if message["type"] == "message":
                    event = json.loads(message["data"])
                    callback(event)
        except Exception as e:
            print(f"Subscription error: {e}")

```text

- --

## 🔄 Data Flow

### **1. AI Request Flow**```text
User Request → API Gateway → Authentication → AI Model → Database → Response
     ↓              ↓              ↓              ↓           ↓         ↓
  Validate      Rate Limit    Check Perms    Generate    Log Data   Format

```text

### **2. Workflow Execution Flow**```text
Trigger → n8n Workflow → AI Model → Database → Dashboard → User
   ↓           ↓            ↓          ↓          ↓         ↓
Webhook    Execute      Process    Store      Update    Notify

```text

### **3. Monitoring Data Flow**```text
System → Metrics Collector → Time Series DB → Dashboard → Alerts
  ↓            ↓                ↓              ↓         ↓
Events    Aggregate        Store Data     Visualize   Notify

```text

- --

## !️ Error Handling

### **1. API Error Handling**####**Standard Error Responses**```python

## Standard error response format

ERROR_RESPONSES = {
    "validation_error": {
        "code": 400,
        "message": "Invalid request parameters",
        "details": dict
    },
    "authentication_error": {
        "code": 401,
        "message": "Authentication required",
        "details": dict
    },
    "authorization_error": {
        "code": 403,
        "message": "Insufficient permissions",
        "details": dict
    },
    "not_found_error": {
        "code": 404,
        "message": "Resource not found",
        "details": dict
    },
    "rate_limit_error": {
        "code": 429,
        "message": "Rate limit exceeded",
        "details": dict
    },
    "internal_error": {
        "code": 500,
        "message": "Internal server error",
        "details": dict
    }
}

def handle_api_error(error_type: str, details: dict = None) -> dict:
    """Handle API errors consistently"""
    error_response = ERROR_RESPONSES.get(error_type, ERROR_RESPONSES["internal_error"])
    error_response["details"] = details or {}
    return error_response

```text

## **2. Retry Logic**####**Exponential Backoff**```python

# Retry logic with exponential backoff

def retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e

            delay = base_delay* (2 **attempt)
            time.sleep(delay)

```text

## **3. Circuit Breaker Pattern**####**Circuit Breaker Implementation**```python

## Circuit breaker pattern

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def call(self, func,*args, **kwargs):
        """Execute function with circuit breaker"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = "CLOSED"

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

```text

- --

## 🔒 Security Integration

### **1. API Authentication**####**JWT Token Authentication**```python

# JWT authentication middleware

class JWTAuthentication:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def authenticate(self, token: str) -> dict:
        """Authenticate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return {"success": True, "user_id": payload["user_id"]}
        except jwt.ExpiredSignatureError:
            return {"success": False, "error": "Token expired"}
        except jwt.InvalidTokenError:
            return {"success": False, "error": "Invalid token"}

    def generate_token(self, user_id: str) -> str:
        """Generate JWT token"""
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")

```text

## **2. Rate Limiting**####**Token Bucket Rate Limiter**```python

## Token bucket rate limiter

class TokenBucketRateLimiter:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()

    def allow_request(self, user_id: str) -> bool:
        """Check if request is allowed"""
        self._refill_tokens()

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    def _refill_tokens(self):
        """Refill tokens based on time passed"""
        now = time.time()
        time_passed = now - self.last_refill
        tokens_to_add = time_passed* self.refill_rate

        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now

```text

- --

## 📊 Performance Integration

### **1. Caching Integration**####**Multi-level Cache**```python

# Multi-level cache integration

class MultiLevelCache:
    def __init__(self):
        self.l1_cache = {}  # Memory cache

        self.l2_cache = redis.Redis()  # Redis cache

    def get(self, key: str):
        """Get value from cache"""

        # Try L1 cache first

        if key in self.l1_cache:
            return self.l1_cache[key]

        # Try L2 cache

        value = self.l2_cache.get(key)
        if value:
            self.l1_cache[key] = value  # Populate L1

            return value

        return None

    def set(self, key: str, value, ttl: int = 3600):
        """Set value in cache"""

        # Set in both caches

        self.l1_cache[key] = value
        self.l2_cache.setex(key, ttl, value)

```text

## **2. Connection Pooling**####**Database Connection Pool**```python

## Database connection pool

class DatabaseConnectionPool:
    def __init__(self, connection_string: str, max_connections: int = 10):
        self.connection_string = connection_string
        self.max_connections = max_connections
        self.pool = Queue(maxsize=max_connections)
        self._initialize_pool()

    def _initialize_pool(self):
        """Initialize connection pool"""
        for _ in range(self.max_connections):
            connection = psycopg2.connect(self.connection_string)
            self.pool.put(connection)

    def get_connection(self):
        """Get connection from pool"""
        return self.pool.get()

    def return_connection(self, connection):
        """Return connection to pool"""
        self.pool.put(connection)

```text

- --

## 🧪 Testing Integration

### **1. API Testing**####**Integration Test Framework**```python

# Integration test framework

class IntegrationTestFramework:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def test_ai_generation(self):
        """Test AI generation endpoint"""
        url = f"{self.base_url}/api/v1/ai/generate"
        data = {
            "prompt": "Hello, how are you?",
            "model": "cursor-native-ai"
        }

        response = self.session.post(url, json=data)
        assert response.status_code == 200

        result = response.json()
        assert result["success"] == True
        assert "content" in result["data"]

    def test_workflow_execution(self):
        """Test workflow execution endpoint"""
        url = f"{self.base_url}/api/v1/workflow/execute"
        data = {
            "workflow_id": "test_workflow",
            "input_data": {"test": "data"}
        }

        response = self.session.post(url, json=data)
        assert response.status_code == 200

        result = response.json()
        assert result["success"] == True
        assert "execution_id" in result["data"]

```text

## **2. Load Testing**####**API Load Testing**```python

## API load testing

def load_test_api(endpoint: str, num_requests: int = 100):
    """Load test API endpoint"""
    results = []

    for i in range(num_requests):
        start_time = time.time()

        try:
            response = requests.post(endpoint, json={"test": "data"})
            end_time = time.time()

            results.append({
                "request_id": i,
                "response_time": end_time - start_time,
                "status_code": response.status_code,
                "success": response.status_code == 200
            })
        except Exception as e:
            results.append({
                "request_id": i,
                "response_time": None,
                "status_code": None,
                "success": False,
                "error": str(e)
            })

    return results

```text

- --

## 🚀 Deployment Integration

### **1. Container Integration**####**Docker Configuration**

```dockerfile

## Dockerfile for AI development ecosystem

FROM python:3.11-slim

## Install system dependencies

RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*# Set working directory

WORKDIR /app

## Copy requirements and install Python dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

## Copy application code

COPY . .

## Expose ports

EXPOSE 5000 8000

## Health check

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f <http://localhost:5000/health> || exit 1

## Start application

CMD ["python", "app.py"]

```text

## **2. Kubernetes Integration**####**Kubernetes Deployment**```yaml

# Kubernetes deployment configuration

apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-development-ecosystem
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

```bash

- --

## 📋 Integration Checklist

### **API Integration Checklist**- [ ] RESTful API design implemented

- [ ] GraphQL schema defined

- [ ] WebSocket communication configured

- [ ] Authentication middleware integrated

- [ ] Rate limiting implemented

- [ ] Error handling standardized

- [ ] API documentation generated

- [ ] API versioning strategy defined

### **Component Integration Checklist**- [ ] AI model interfaces implemented

- [ ] Database integration configured

- [ ] n8n workflow integration tested

- [ ] Dashboard real-time updates working

- [ ] Monitoring integration active

- [ ] Security integration verified

- [ ] Performance integration optimized

- [ ] Testing integration automated

### **Deployment Integration Checklist**- [ ] Docker containers configured

- [ ] Kubernetes manifests created

- [ ] Environment variables managed

- [ ] Secrets management implemented

- [ ] Health checks configured

- [ ] Load balancing configured

- [ ] Monitoring deployed

- [ ] Backup strategies implemented

- --

## 🛠️ Tools & Scripts

### **1. API Documentation Generator**```python

## API documentation generator

def generate_api_docs():
    """Generate API documentation"""
    docs = {
        "endpoints": [],
        "schemas": [],
        "examples": []
    }

    ## Generate endpoint documentation

    for endpoint in API_ENDPOINTS:
        docs["endpoints"].append({
            "path": endpoint["path"],
            "method": endpoint["method"],
            "description": endpoint["description"],
            "parameters": endpoint["parameters"],
            "responses": endpoint["responses"]
        })

    ## Generate schema documentation

    for schema in API_SCHEMAS:
        docs["schemas"].append({
            "name": schema["name"],
            "properties": schema["properties"],
            "required": schema["required"]
        })

    return docs

```text

## **2. Integration Test Runner**```python

# Integration test runner

def run_integration_tests():
    """Run all integration tests"""
    test_results = []

    # Test API endpoints

    api_tests = [
        test_ai_generation,
        test_workflow_execution,
        test_database_operations
    ]

    for test in api_tests:
        try:
            result = test()
            test_results.append({
                "test": test.__name__,
                "status": "PASS",
                "result": result
            })
        except Exception as e:
            test_results.append({
                "test": test.__name__,
                "status": "FAIL",
                "error": str(e)
            })

    return test_results
```

------------------------------------------------------------------------

## 📚 Additional Resources

### **Integration Documentation**-**REST API Design**: <https://restfulapi.net/>

- **GraphQL Documentation**: <https://graphql.org/>

- **WebSocket Protocol**: <https://tools.ietf.org/html/rfc6455>

### **Integration Tools**-**Postman**: <https://www.postman.com/>

- **Insomnia**: <https://insomnia.rest/>

- **Swagger**: <https://swagger.io/>

### **Testing Tools**-**Pytest**: <https://docs.pytest.org/>

- **Locust**: <https://locust.io/>

- **JMeter**: <https://jmeter.apache.org/>

------------------------------------------------------------------------

- Last Updated: 2024-08-07\*
- Next Review: Monthly\*
- Integration Level: Comprehensive\*

<!-- README_AUTOFIX_START -->

## Auto-generated sections for 400_integration-patterns-guide.md

## Generated: 2025-08-18T08:03:22.752335

## Missing sections to add:

## Last Reviewed

2025-08-18

## Owner

Documentation Team

## Purpose

Describe the purpose and scope of this document

## Usage

Describe how to use this document or system

<!-- README_AUTOFIX_END -->
