#!/bin/bash
# Setup script for real database integration tests

set -e

echo "🧪 Setting up real database integration tests..."

# Check if we're in the project root
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Check for required environment variables
if [ -z "$TEST_POSTGRES_DSN" ] && [ -z "$POSTGRES_DSN" ]; then
    echo "❌ No database DSN found. Please set TEST_POSTGRES_DSN or POSTGRES_DSN"
    echo "   Example: export TEST_POSTGRES_DSN='postgresql://user:pass@localhost:5432/test_db'"
    exit 1
fi

# Check if DSN is not a mock
if [[ "$TEST_POSTGRES_DSN" == mock://* ]] || [[ "$POSTGRES_DSN" == mock://* ]]; then
    echo "❌ Mock DSN detected. Real database required for integration tests."
    echo "   Please set a real PostgreSQL connection string."
    exit 1
fi

echo "✅ Database DSN configured"

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv not found. Please install uv first."
    exit 1
fi

echo "✅ uv found"

# Install test dependencies
echo "📦 Installing test dependencies..."
uv sync --extra dev

# Check if pytest is available
if ! uv run pytest --version &> /dev/null; then
    echo "❌ pytest not available. Please check your environment."
    exit 1
fi

echo "✅ pytest available"

# Test database connectivity
echo "🔌 Testing database connectivity..."
if ! uv run python -c "
import os
import psycopg
from psycopg.rows import dict_row

dsn = os.getenv('TEST_POSTGRES_DSN') or os.getenv('POSTGRES_DSN')
try:
    conn = psycopg.connect(dsn)
    conn.row_factory = dict_row
    with conn.cursor() as cur:
        cur.execute('SELECT 1 as test')
        result = cur.fetchone()
        if result['test'] == 1:
            print('✅ Database connection successful')
        else:
            print('❌ Database connection test failed')
            exit(1)
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"; then
    exit 1
fi

# Create test database schema if needed
echo "🗄️  Setting up test database schema..."
uv run python -c "
import os
import psycopg
from psycopg.rows import dict_row

dsn = os.getenv('TEST_POSTGRES_DSN') or os.getenv('POSTGRES_DSN')
conn = psycopg.connect(dsn)
conn.row_factory = dict_row

try:
    with conn.cursor() as cur:
        # Check if pgvector extension is available
        cur.execute(\"SELECT extname FROM pg_extension WHERE extname = 'vector'\")
        vector_ext = cur.fetchone()
        
        if not vector_ext:
            print('⚠️  pgvector extension not found. Some tests may be skipped.')
        else:
            print('✅ pgvector extension available')
        
        # Check for document_chunks table
        cur.execute(\"\"\"
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'document_chunks'
        \"\"\")
        chunks_table = cur.fetchone()
        
        if not chunks_table:
            print('⚠️  document_chunks table not found. Some tests may be skipped.')
        else:
            print('✅ document_chunks table found')
        
        # Check for conversation tables
        cur.execute(\"\"\"
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('conversation_sessions', 'conversation_messages')
        \"\"\")
        conv_tables = cur.fetchall()
        
        if not conv_tables:
            print('⚠️  Conversation tables not found. Some tests may be skipped.')
        else:
            print('✅ Conversation tables found')
    
    conn.close()
    print('✅ Database schema check complete')
    
except Exception as e:
    print(f'❌ Database schema check failed: {e}')
    exit(1)
"

echo ""
echo "🎉 Real database integration tests setup complete!"
echo ""
echo "To run the tests:"
echo "  # Run all real database tests"
echo "  uv run python tests/integration/run_real_database_tests.py --all"
echo ""
echo "  # Run specific test patterns"
echo "  uv run python tests/integration/run_real_database_tests.py --pattern test_mcp_memory_server_real.py"
echo ""
echo "  # Run with verbose output"
echo "  uv run python tests/integration/run_real_database_tests.py --all --verbose"
echo ""
echo "  # Check database availability only"
echo "  uv run python tests/integration/run_real_database_tests.py --check-db"
