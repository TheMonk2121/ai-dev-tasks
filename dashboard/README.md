<!-- CONTEXT_REFERENCE: 400_guides/400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_deployment-environment-guide.md -->
<!-- MODULE_REFERENCE: 400_guides/400_performance-optimization-guide.md -->

# Document Management Dashboard

## 🔎 TL;DR

| what this file is | read when | do next |
|---|---|---|
|  |  |  |

- **what this file is**: Quick summary of Document Management Dashboard.

- **read when**: When you need a fast orientation or before using this file in a workflow.

- **do next**: Scan the headings below and follow any 'Quick Start' or 'Usage' sections.

A modern, interactive web dashboard for managing and visualizing documents in your RAG system with enhanced metadata
capabilities. This dashboard integrates with the v0.3.1 Ultra-Minimal Router architecture for intelligent document
processing and analysis.

## 🚀 Quick Start

### Prerequisites

- Python 3.9+

- PostgreSQL with `ai_agency` database

- Your existing RAG system running

### Installation & Startup

1. **Navigate to the dashboard directory:**```bash
   cd dashboard
   ```text

2.**Install dependencies:**```bash
   python3 -m pip install -r requirements.txt
   ```text

3.**Start the dashboard:**```bash
   ./start_dashboard.sh
   ```text

   Or manually:
   ```bash
   python3 dashboard.py
   ```html

4.**Access the dashboard:**- Main Dashboard: [<http://localhost:5001>](http://localhost:5001)
  - Health Check: [<http://localhost:5001/health>](http://localhost:5001/health)

## 📊 Features

### Enhanced Metadata System

- **Automatic Categorization**: Documents are automatically categorized based on filename patterns

- **Smart Tagging**: Automatic tag extraction from filenames and content

- **Priority Detection**: Intelligent priority assignment based on keywords

- **Content Type Analysis**: Automatic detection of document types (CSV, PDF, etc.)

- **Size Classification**: Documents categorized by size (small, medium, large)

- **Version Detection**: Automatic extraction of version numbers from filenames

- **Date Extraction**: Pattern-based date extraction from filenames

### Interactive Dashboard

- **Real-time Statistics**: Live processing statistics and analytics

- **Advanced Filtering**: Filter by priority, category, and search terms

- **Document Cards**: Rich document information with metadata badges

- **Modal Views**: Detailed metadata inspection for each document

- **Responsive Design**: Works on desktop and mobile devices

### API Endpoints

- `GET /` - Main dashboard page

- `GET /api/documents` - JSON list of all documents

- `GET /api/stats` - Processing statistics

- `GET /api/metadata/<filename>` - Metadata for specific document

- `GET /health` - System health check

## 🏷️ Metadata Categories

The system automatically categorizes documents into these categories:

| Category | Keywords | Priority |
|----------|----------|----------|
| **Pricing & Billing**| pricing, price, cost, billing | High |
|**Legal & Contracts**| contract, agreement, legal, terms | High |
|**Marketing & Campaigns**| marketing, campaign, ad, promotion | Medium |
|**Client & Customer Data**| client, customer, user, profile | Medium |
|**Reports & Analytics**| report, analytics, data, metrics | Medium |
|**Technical & Code**| source, code, script, config | Medium |
|**Testing & Samples**| test, sample, example | Low |
|**Documentation & Guides**| manual, guide, documentation, help | Medium |
|**Financial Records**| invoice, receipt, payment | High |

## 🎨 Content Type Badges

Documents are automatically tagged with content types:

- **📊 Structured Data**(CSV files)

- **📄 Document**(PDF, DOC, DOCX)

- **📝 Text**(TXT, MD)

- **🖼️ Image**(JPG, PNG, GIF)

- **❓ Unknown**(other file types)

## 📏 Size Categories

Documents are classified by size:

- **Small**: < 1MB

- **Medium**: 1MB - 10MB

- **Large**: > 10MB

## 🔧 Configuration

### Database Connection

The dashboard connects to your existing PostgreSQL database. Update the connection settings in `dashboard.py`:

```python
def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "ai_agency"),
        user=os.getenv("DB_USER", "danieljacobs"),
        password=os.getenv("DB_PASSWORD", "")
    )

```markdown

- *Note**: The dashboard now supports environment variables for secure configuration. Update `start_dashboard.sh` to use
environment variables instead of hardcoded credentials.

### Custom Metadata Extraction

You can customize metadata extraction by modifying the `extract_enhanced_metadata()` function in `dashboard.py`.

## 📁 File Structure

```text

dashboard/
├── dashboard.py              # Main Flask application

├── requirements.txt          # Python dependencies

├── start_dashboard.sh       # Startup script

├── README.md               # This documentation

├── templates/
│   └── dashboard.html      # Main dashboard template

└── static/
    ├── css/
    │   └── style.css       # Dashboard styling

    └── js/
        └── app.js          # Interactive functionality

```markdown

## 🎯 Usage Examples

### Viewing Document Metadata

1. Open the dashboard at [<http://localhost:5001>](http://localhost:5001)
2. Click "🔍 View Metadata" on any document card
3. View detailed metadata in the modal popup

### Filtering Documents

1. Use the search box to find documents by name, category, or tags
2. Use the priority filter to show only high/medium/low priority documents
3. Use the category filter to show documents by category

### Monitoring System Health

1. Click "💚 System Health" in the Quick Actions section
2. View real-time system status notifications

## 🔄 Integration with Your RAG System

The dashboard integrates seamlessly with your existing DSPy RAG system:

- **Database Integration**: Reads from your existing `documents` and `document_chunks` tables in `dspy-rag-system/config/database/schema.sql`
- **Metadata Enhancement**: Automatically enhances existing documents with new metadata using `dspy-rag-system/src/utils/metadata_extractor.py` patterns
- **AI Integration**: Cursor Native AI integration for intelligent metadata extraction
- **Real-time Updates**: Reflects changes from your watch folder and processing pipeline

- **Query Logging**: Displays recent RAG queries (if `query_logs` table exists)

- **Testing Integration**: Follows patterns from `dspy-rag-system/tests/` for comprehensive testing

## 🚨 Troubleshooting

### Common Issues

- *Port 5000/5001 already in use:**```bash

# Find and kill the process

lsof -ti:5001 | xargs kill -9

# Or use a different port in dashboard.py

```**Database connection failed:**- Ensure PostgreSQL is running

- Check database credentials in `dashboard.py`

- Verify `ai_agency` database exists**No documents showing:**- Check if documents exist in your database

- Verify the `documents` table structure

- Check database permissions

## Debug Mode

The dashboard runs in debug mode by default. Check the console output for detailed error messages.

## 🔮 Future Enhancements

- **AI-Powered Metadata**: Integration with DSPy RAG system for intelligent metadata extraction

- **Security Improvements**: Environment variable configuration and input validation

- **Performance Optimization**: Database indexing and query optimization

- **Testing Framework**: Comprehensive test suite following `dspy-rag-system/tests/` patterns

- **Error Handling**: Enhanced error recovery and graceful degradation

- **Real-time Updates**: WebSocket-based live updates

## 📞 Support

For issues or questions:

1. Check the console output for error messages
2. Verify database connectivity
3. Ensure all dependencies are installed
4. Check file permissions on the dashboard directory

- --

- *Dashboard Status**: ✅ Ready for production use with your RAG system
- *C-2: Central Retry Wrapper**: ✅ **COMPLETED** - Configurable retry logic with exponential backoff

<!-- README_AUTOFIX_START -->
# Auto-generated sections for README.md
# Generated: 2025-08-17T21:51:30.661755

## Missing sections to add:

## Last Reviewed

2025-08-17

## Owner

[Document owner/maintainer information]

## Purpose

[Describe the purpose and scope of this document]

## Usage

[Describe how to use this document or system]

<!-- README_AUTOFIX_END -->
