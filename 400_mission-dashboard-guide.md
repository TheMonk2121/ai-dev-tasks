<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_contributing-guidelines_code_standards.md -->
<!-- MODULE_REFERENCE: B-011-DEPLOYMENT-GUIDE_production_deployment.md -->

# Real-time Mission Dashboard Guide

## Overview

The Real-time Mission Dashboard provides live visibility into AI task execution with comprehensive monitoring, tracking, and management capabilities. This system enables real-time monitoring of AI missions, progress tracking, performance metrics, and interactive mission management.

## 🚀 Features

### Core Functionality
- **Real-time Mission Tracking**: Monitor AI task execution in real-time
- **Progress Updates**: Live progress tracking with percentage completion
- **Mission Lifecycle Management**: Create, start, update, complete, and cancel missions
- **Priority Management**: Support for low, medium, high, and critical priorities
- **Agent & Model Tracking**: Track which AI agents and models are used
- **Cost & Token Monitoring**: Monitor token usage and cost estimates
- **Error Handling**: Comprehensive error tracking and failure management

### Dashboard Interface
- **Modern Dark Theme**: Professional dark-mode interface
- **Real-time Updates**: WebSocket-based live updates
- **Interactive Cards**: Clickable mission cards with detailed views
- **Progress Bars**: Visual progress indicators for running missions
- **Status Badges**: Color-coded status and priority indicators
- **Filtering & Search**: Advanced filtering by status, priority, and text search
- **Metrics Dashboard**: Real-time statistics and performance metrics

### API Endpoints
- **RESTful API**: Complete REST API for mission management
- **WebSocket Support**: Real-time bidirectional communication
- **Rate Limiting**: Built-in rate limiting for API protection
- **Health Monitoring**: Comprehensive health check endpoints
- **Error Handling**: Robust error handling and validation

## 📋 Architecture

### Components

#### Mission Tracker (`mission_tracker.py`)
- Core mission management system
- Database integration with PostgreSQL
- Real-time metrics calculation
- Background cleanup and maintenance
- Callback system for updates

#### Mission Dashboard (`mission_dashboard.py`)
- Flask-based web application
- WebSocket integration with SocketIO
- RESTful API endpoints
- Rate limiting and security
- Production monitoring integration

#### Frontend Interface (`mission_dashboard.html`)
- Modern responsive design
- Real-time WebSocket communication
- Interactive mission management
- Advanced filtering and search
- Professional dark theme

### Data Flow
```
User Action → API Endpoint → Mission Tracker → Database
                ↓
            WebSocket Event → Frontend Update
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, for persistent storage)
- Virtual environment recommended

### Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd dspy-rag-system
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the dashboard:**
   ```bash
   ./start_mission_dashboard.sh
   ```

4. **Access the dashboard:**
   - URL: http://localhost:5002
   - Health check: http://localhost:5002/api/health

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MISSION_DASHBOARD_PORT` | 5002 | Dashboard port |
| `MISSION_DASHBOARD_HOST` | 0.0.0.0 | Dashboard host |
| `MISSION_DASHBOARD_SECRET_KEY` | mission-dashboard-secret-key | Flask secret key |
| `POSTGRES_DSN` | postgresql://ai_user:ai_password@localhost:5432/ai_agency | Database connection |
| `ENVIRONMENT` | development | Environment (development/production) |

## 📊 Usage

### Creating Missions

#### Via API
```bash
curl -X POST http://localhost:5002/api/missions \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Document Processing",
    "description": "Process uploaded documents",
    "priority": "high"
  }'
```

#### Via Dashboard
1. Click "New Mission" button
2. Fill in title, description, and priority
3. Click "Create Mission"

### Mission Lifecycle

1. **Create Mission**: Initialize with title, description, priority
2. **Start Mission**: Begin execution with agent and model info
3. **Update Progress**: Real-time progress updates (0-100%)
4. **Complete/Fail**: Finalize with results, tokens, and cost
5. **Monitor**: Real-time dashboard updates

### API Endpoints

#### Mission Management
- `GET /api/missions` - List all missions
- `GET /api/missions/<id>` - Get specific mission
- `POST /api/missions` - Create new mission
- `POST /api/missions/<id>/start` - Start mission
- `POST /api/missions/<id>/progress` - Update progress
- `POST /api/missions/<id>/complete` - Complete mission
- `POST /api/missions/<id>/fail` - Fail mission
- `POST /api/missions/<id>/cancel` - Cancel mission

#### Monitoring
- `GET /api/metrics` - Get system metrics
- `GET /api/running` - Get running missions
- `GET /api/health` - Health check

### WebSocket Events

#### Client to Server
- `connect` - Client connection
- `disconnect` - Client disconnection
- `request_update` - Request data update

#### Server to Client
- `initial_data` - Initial dashboard data
- `mission_update` - Mission state change
- `metrics_update` - Metrics update
- `data_update` - General data update

## 🎯 Mission Types

### Document Processing
- **Purpose**: Process and analyze uploaded documents
- **Agents**: IntentRouter, RetrievalAgent
- **Models**: mistral:7b-instruct, yi-coder:9b-chat-q6_k
- **Metrics**: Processing time, accuracy, token usage

### Code Generation
- **Purpose**: Generate code for various tasks
- **Agents**: CodeAgent
- **Models**: yi-coder:9b-chat-q6_k
- **Metrics**: Code quality, generation time, token usage

### System Monitoring
- **Purpose**: Health checks and performance monitoring
- **Agents**: MonitoringAgent
- **Models**: mistral:7b-instruct
- **Metrics**: System health, response times, error rates

### Data Analysis
- **Purpose**: Analytics and reporting
- **Agents**: AnalyticsAgent
- **Models**: mistral:7b-instruct
- **Metrics**: Analysis accuracy, processing time, data volume

## 📈 Metrics & Analytics

### Mission Metrics
- **Total Missions**: Total number of missions created
- **Completed Missions**: Successfully completed missions
- **Failed Missions**: Missions that failed
- **Running Missions**: Currently executing missions
- **Success Rate**: Percentage of successful missions
- **Average Duration**: Average mission execution time
- **Total Tokens**: Cumulative token usage
- **Total Cost**: Estimated total cost

### Performance Metrics
- **Response Time**: API response times
- **Throughput**: Missions per minute
- **Error Rate**: Failed missions percentage
- **Resource Usage**: CPU, memory, database usage

## 🔧 Configuration

### Database Configuration
```sql
-- Mission tracking table
CREATE TABLE missions (
    id VARCHAR(255) PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL,
    priority VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    duration FLOAT,
    progress FLOAT DEFAULT 0.0,
    error_message TEXT,
    result JSONB,
    metadata JSONB,
    agent_type VARCHAR(100),
    model_used VARCHAR(100),
    tokens_used INTEGER,
    cost_estimate FLOAT
);

-- Mission metrics table
CREATE TABLE mission_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    total_missions INTEGER,
    completed_missions INTEGER,
    failed_missions INTEGER,
    running_missions INTEGER,
    average_duration FLOAT,
    success_rate FLOAT,
    total_tokens INTEGER,
    total_cost FLOAT
);
```

### Security Configuration
- **Rate Limiting**: 100 requests per minute per IP
- **Input Validation**: Comprehensive input sanitization
- **Error Handling**: Secure error messages
- **CORS**: Configurable cross-origin settings

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python3 -m pytest tests/test_mission_dashboard.py -v

# Run specific test categories
python3 -m pytest tests/test_mission_dashboard.py::TestMissionTracker -v
python3 -m pytest tests/test_mission_dashboard.py::TestMissionDashboardAPI -v
```

### Demo Script
```bash
# Create sample missions
python3 demo_mission_dashboard.py create

# Run full demo
python3 demo_mission_dashboard.py run

# Show statistics
python3 demo_mission_dashboard.py stats
```

## 🔍 Troubleshooting

### Common Issues

#### Dashboard Not Starting
- **Check port availability**: Ensure port 5002 is free
- **Verify dependencies**: Run `pip install -r requirements.txt`
- **Check Python version**: Ensure Python 3.8+ is installed

#### Database Connection Issues
- **Verify PostgreSQL**: Ensure PostgreSQL is running
- **Check credentials**: Verify database user and password
- **Test connection**: Use `psql` to test database connectivity

#### WebSocket Connection Issues
- **Check firewall**: Ensure port 5002 is accessible
- **Verify CORS**: Check CORS configuration for cross-origin requests
- **Browser console**: Check browser console for WebSocket errors

### Logs and Debugging
- **Application logs**: Check `logs/mission_dashboard.log`
- **Database logs**: Check PostgreSQL logs
- **Browser logs**: Check browser developer console
- **Network logs**: Use browser network tab for API debugging

## 🚀 Production Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5002

CMD ["python3", "src/mission_dashboard/mission_dashboard.py"]
```

### Environment Configuration
```bash
# Production environment variables
export MISSION_DASHBOARD_PORT=5002
export MISSION_DASHBOARD_HOST=0.0.0.0
export MISSION_DASHBOARD_SECRET_KEY=your-secure-secret-key
export POSTGRES_DSN=postgresql://user:pass@host:5432/db
export ENVIRONMENT=production
```

### Monitoring and Alerting
- **Health checks**: Regular health endpoint monitoring
- **Metrics collection**: Prometheus/Grafana integration
- **Log aggregation**: Centralized logging with ELK stack
- **Alerting**: Set up alerts for failures and performance issues

## 🔮 Future Enhancements

### Planned Features
- **Advanced Analytics**: Detailed performance analytics
- **Mission Templates**: Predefined mission templates
- **Batch Operations**: Bulk mission management
- **Integration APIs**: Third-party system integration
- **Mobile Support**: Mobile-responsive interface
- **Advanced Filtering**: More sophisticated filtering options

### Performance Optimizations
- **Caching**: Redis-based caching for improved performance
- **Database Optimization**: Query optimization and indexing
- **Load Balancing**: Horizontal scaling support
- **CDN Integration**: Static asset delivery optimization

## 📚 API Reference

### Mission Object
```json
{
  "id": "uuid",
  "title": "Mission Title",
  "description": "Mission Description",
  "status": "pending|running|completed|failed|cancelled",
  "priority": "low|medium|high|critical",
  "created_at": "2024-08-06T06:30:00Z",
  "started_at": "2024-08-06T06:31:00Z",
  "completed_at": "2024-08-06T06:35:00Z",
  "duration": 300.5,
  "progress": 100.0,
  "error_message": null,
  "result": {"status": "completed"},
  "metadata": {"type": "document_processing"},
  "agent_type": "IntentRouter",
  "model_used": "mistral:7b-instruct",
  "tokens_used": 1500,
  "cost_estimate": 0.15
}
```

### Metrics Object
```json
{
  "total_missions": 100,
  "completed_missions": 85,
  "failed_missions": 5,
  "running_missions": 10,
  "average_duration": 45.2,
  "success_rate": 85.0,
  "total_tokens": 150000,
  "total_cost": 15.0
}
```

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

### Code Standards
- **Python**: PEP 8 style guide
- **JavaScript**: ESLint configuration
- **HTML/CSS**: Consistent formatting
- **Documentation**: Comprehensive docstrings

### Testing Guidelines
- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **API Tests**: Test all API endpoints
- **UI Tests**: Test user interface functionality

## 📄 License

This project is part of the AI Development Ecosystem and follows the same licensing terms as the main project.

---

**Last Updated**: 2024-08-06  
**Version**: 1.0.0  
**Status**: Production Ready ✅ 