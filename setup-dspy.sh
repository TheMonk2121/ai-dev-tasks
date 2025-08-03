#!/bin/bash

# DSPy PostgreSQL Setup Script
# Installs DSPy and configures it to use your existing PostgreSQL database

set -e

echo "🚀 Setting up DSPy with PostgreSQL..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

print_success "Python 3 is available"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip and try again."
    exit 1
fi

print_success "pip3 is available"

# Install required packages
print_status "Installing DSPy and dependencies..."
pip3 install -r requirements-dspy.txt

print_success "Dependencies installed"

# Check if PostgreSQL is accessible
print_status "Testing PostgreSQL connection..."

# Try to connect to PostgreSQL using the default connection string
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect('postgresql://ai_user:ai_password@localhost:5432/ai_agency')
    print('✅ PostgreSQL connection successful')
    conn.close()
except Exception as e:
    print(f'❌ PostgreSQL connection failed: {e}')
    print('Please ensure your PostgreSQL database is running and accessible')
    exit(1)
"

if [ $? -eq 0 ]; then
    print_success "PostgreSQL connection verified"
else
    print_warning "PostgreSQL connection failed. You may need to:"
    print_warning "1. Start your PostgreSQL database"
    print_warning "2. Update the connection string in dspy_postgres_setup.py"
    print_warning "3. Ensure the database 'ai_agency' exists"
fi

# Test DSPy setup
print_status "Testing DSPy PostgreSQL setup..."
python3 dspy_postgres_setup.py

if [ $? -eq 0 ]; then
    print_success "DSPy PostgreSQL setup completed successfully"
else
    print_warning "DSPy setup had issues. Check the output above for details."
fi

# Test PRD processing
if [ -f "prd-cursor-n8n-integration.md" ]; then
    print_status "Testing PRD processing with DSPy..."
    python3 dspy_prd_processor.py
    
    if [ $? -eq 0 ]; then
        print_success "PRD processing test completed"
    else
        print_warning "PRD processing test had issues. Check the output above for details."
    fi
else
    print_warning "PRD file not found. Skipping PRD processing test."
fi

echo ""
print_success "DSPy PostgreSQL setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Update your PRD files and run: python3 dspy_prd_processor.py"
echo "2. Check memory statistics: python3 -c 'from dspy_prd_processor import show_memory_stats; show_memory_stats()'"
echo "3. View your PostgreSQL database to see DSPy memory tables"
echo ""
echo "🔧 Configuration:"
echo "- Database tables: dspy_signatures, dspy_examples, dspy_optimizations"
echo "- Connection: postgresql://ai_user:ai_password@localhost:5432/ai_agency"
echo "- Memory storage: Persistent across sessions" 