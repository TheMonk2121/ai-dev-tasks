<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
# "category": "Pricing & Billing",


  "category": "Pricing & Billing",
  "priority": "high",
  "tags": ["pricing", "financial", "confidential"],
  "content_type": "structured_data",
  "size_category": "medium",
  "version": "v2.1.0",
  "extracted_date": "2024-01-15",
  "processing_status": "completed"
}

```text

### **Cursor IDE Integration**####**Development Workflow**-**PRD Creation**: Use `001_create-prd.md` in Cursor

- **Task Generation**: Use `002_generate-tasks.md` for implementation

- **Task Execution**: Use `003_process-task-list.md` for AI-driven development

- **State Management**: Automatic `.ai_state.json` handling

#### **AI Agent Configuration**```json
    {
      "customModels": [
        {
          "title": "Cursor Native AI Local",
          "model": "cursor-native-ai",
          "baseURL": "<http://localhost:11434/v1",>
          "apiKey": ""
        }
      ],
      "defaultModel": "cursor-native-ai"
    }

```

### **Performance Optimization**####**Caching Strategies**-**State Caching**: `.ai_state.json` for context persistence

- **Vector Caching**: Redis for frequently accessed embeddings

- **Result Caching**: Memoization for repeated queries

- **Connection Pooling**: Database connection optimization

#### **Scalability Features**-**Horizontal Scaling**: Multiple processing nodes

- **Load Balancing**: Distributed processing across nodes

- **Queue Management**: Redis-based job queuing

- **Resource Monitoring**: Real-time resource usage tracking

- --
