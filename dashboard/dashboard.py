from flask import Flask, render_template, jsonify, request
import psycopg2
import os
from datetime import datetime
import json
import re
from pathlib import Path

app = Flask(__name__)

def get_db_connection():
    """Connect to the existing PostgreSQL database"""
    return psycopg2.connect(
        host="localhost",
        database="ai_agency",
        user="danieljacobs"
    )

def extract_enhanced_metadata(filename, file_type, file_size, content_preview=None):
    """Extract enhanced metadata from filename and content"""
    metadata = {
        'category': 'Uncategorized',
        'tags': [],
        'priority': 'medium',
        'notes': '',
        'content_type': 'unknown',
        'processing_status': 'pending',
        'extracted_at': datetime.now().isoformat()
    }
    
    filename_lower = filename.lower()
    
    # Enhanced categorization based on filename patterns (order matters - more specific first)
    if any(word in filename_lower for word in ['test_', 'sample_', 'example_', '_test', '_sample', '_example']):
        metadata['category'] = 'Testing & Samples'
        metadata['tags'].extend(['test', 'sample', 'example'])
        metadata['priority'] = 'low'
    elif any(word in filename_lower for word in ['pricing', 'price', 'cost', 'billing']):
        metadata['category'] = 'Pricing & Billing'
        metadata['tags'].extend(['pricing', 'billing', 'financial'])
        metadata['priority'] = 'high'
    elif any(word in filename_lower for word in ['contract', 'agreement', 'legal', 'terms']):
        metadata['category'] = 'Legal & Contracts'
        metadata['tags'].extend(['legal', 'contract', 'agreement'])
        metadata['priority'] = 'high'
    elif any(word in filename_lower for word in ['marketing', 'campaign', 'ad', 'promotion']):
        metadata['category'] = 'Marketing & Campaigns'
        metadata['tags'].extend(['marketing', 'campaign', 'advertising'])
    elif any(word in filename_lower for word in ['client', 'customer', 'user', 'profile']):
        metadata['category'] = 'Client & Customer Data'
        metadata['tags'].extend(['client', 'customer', 'user'])
    elif any(word in filename_lower for word in ['invoice', 'receipt', 'payment']):
        metadata['category'] = 'Financial Records'
        metadata['tags'].extend(['financial', 'invoice', 'payment'])
        metadata['priority'] = 'high'
    elif any(word in filename_lower for word in ['report', 'analytics', 'data', 'metrics']):
        metadata['category'] = 'Reports & Analytics'
        metadata['tags'].extend(['report', 'analytics', 'data'])
    elif any(word in filename_lower for word in ['source', 'code', 'script', 'config']):
        metadata['category'] = 'Technical & Code'
        metadata['tags'].extend(['technical', 'code', 'development'])
    elif any(word in filename_lower for word in ['manual', 'guide', 'documentation', 'help']):
        metadata['category'] = 'Documentation & Guides'
        metadata['tags'].extend(['documentation', 'guide', 'manual'])
    
    # File type specific metadata
    if file_type == 'csv':
        metadata['content_type'] = 'structured_data'
        metadata['tags'].append('data')
        if 'pricing' in filename_lower:
            metadata['tags'].append('pricing_data')
    elif file_type in ['pdf', 'doc', 'docx']:
        metadata['content_type'] = 'document'
        metadata['tags'].append('document')
    elif file_type in ['txt', 'md']:
        metadata['content_type'] = 'text'
        metadata['tags'].append('text')
    elif file_type in ['jpg', 'jpeg', 'png', 'gif']:
        metadata['content_type'] = 'image'
        metadata['tags'].append('image')
    
    # Priority detection based on keywords
    if any(word in filename_lower for word in ['urgent', 'important', 'critical', 'priority']):
        metadata['priority'] = 'high'
    elif any(word in filename_lower for word in ['draft', 'temp', 'backup']):
        metadata['priority'] = 'low'
    
    # Extract date patterns from filename
    date_pattern = r'(\d{4}[-_]\d{2}[-_]\d{2})|(\d{2}[-_]\d{2}[-_]\d{4})'
    date_match = re.search(date_pattern, filename)
    if date_match:
        metadata['extracted_date'] = date_match.group()
    
    # Extract version numbers
    version_pattern = r'v(\d+\.\d+\.\d+)|version[-_](\d+\.\d+)'
    version_match = re.search(version_pattern, filename_lower)
    if version_match:
        metadata['version'] = version_match.group()
    
    # File size based metadata
    if file_size > 10 * 1024 * 1024:  # > 10MB
        metadata['size_category'] = 'large'
        metadata['tags'].append('large_file')
    elif file_size > 1 * 1024 * 1024:  # > 1MB
        metadata['size_category'] = 'medium'
    else:
        metadata['size_category'] = 'small'
    
    # Content preview analysis (if available)
    if content_preview:
        # Simple keyword extraction from content (only specific business keywords)
        content_lower = content_preview.lower()
        keywords = ['confidential', 'private', 'internal', 'public', 'draft', 'final', 'urgent', 'important']
        for keyword in keywords:
            if keyword in content_lower:
                metadata['tags'].append(keyword)
    
    # Remove duplicates from tags
    metadata['tags'] = list(set(metadata['tags']))
    
    return metadata

def get_documents_with_metadata():
    """Get all documents with enhanced metadata from the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get documents with metadata
        cursor.execute("""
            SELECT 
                filename, 
                file_type, 
                file_size, 
                chunk_count,
                status,
                created_at,
                metadata
            FROM documents 
            ORDER BY created_at DESC
        """)
        
        documents = []
        for row in cursor.fetchall():
            # Parse metadata JSON if it exists
            metadata = {}
            if row[6]:  # metadata column
                try:
                    metadata = json.loads(row[6]) if isinstance(row[6], str) else row[6]
                except:
                    metadata = {}
            
            # Extract enhanced metadata if not already present
            if not metadata.get('category') or metadata.get('category') == 'Uncategorized':
                enhanced_metadata = extract_enhanced_metadata(
                    row[0],  # filename
                    row[1],  # file_type
                    row[2],  # file_size
                    None     # content_preview (not available in this query)
                )
                # Merge with existing metadata
                metadata.update(enhanced_metadata)
            
            # Ensure required fields exist
            metadata.setdefault('category', 'Uncategorized')
            metadata.setdefault('tags', [])
            metadata.setdefault('priority', 'medium')
            metadata.setdefault('notes', '')
            
            documents.append({
                'filename': row[0],
                'file_type': row[1] or 'Unknown',
                'file_size': row[2] or 0,
                'chunk_count': row[3] or 0,
                'status': row[4] or 'unknown',
                'created_at': row[5],
                'priority': metadata.get('priority', 'medium'),
                'tags': metadata.get('tags', []),
                'notes': metadata.get('notes', ''),
                'category': metadata.get('category', 'Uncategorized'),
                'content_type': metadata.get('content_type', 'unknown'),
                'size_category': metadata.get('size_category', 'medium'),
                'version': metadata.get('version', ''),
                'extracted_date': metadata.get('extracted_date', ''),
                'processing_status': metadata.get('processing_status', 'pending')
            })
        
        conn.close()
        return documents
    except Exception as e:
        print(f"Error getting documents: {e}")
        return []

def get_processing_stats():
    """Get enhanced processing statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get basic stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed
            FROM documents
        """)
        
        row = cursor.fetchone()
        stats = {
            'total_documents': row[0],
            'completed': row[1],
            'pending': row[2],
            'failed': row[3]
        }
        
        # Get chunk statistics
        cursor.execute("SELECT COUNT(*) FROM document_chunks")
        stats['total_chunks'] = cursor.fetchone()[0]
        
        # Get recent activity (last 24 hours)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM documents 
            WHERE created_at > NOW() - INTERVAL '24 hours'
        """)
        stats['recent_activity'] = cursor.fetchone()[0]
        
        # Get category breakdown
        cursor.execute("""
            SELECT 
                COALESCE(metadata->>'category', 'Uncategorized') as category,
                COUNT(*) as count
            FROM documents 
            GROUP BY metadata->>'category'
            ORDER BY count DESC
        """)
        
        category_stats = {}
        for row in cursor.fetchall():
            category_stats[row[0]] = row[1]
        stats['category_breakdown'] = category_stats
        
        # Get file type breakdown
        cursor.execute("""
            SELECT 
                file_type,
                COUNT(*) as count
            FROM documents 
            WHERE file_type IS NOT NULL
            GROUP BY file_type
            ORDER BY count DESC
        """)
        
        file_type_stats = {}
        for row in cursor.fetchall():
            file_type_stats[row[0]] = row[1]
        stats['file_type_breakdown'] = file_type_stats
        
        # Get size statistics
        cursor.execute("""
            SELECT 
                AVG(file_size) as avg_size,
                MAX(file_size) as max_size,
                MIN(file_size) as min_size
            FROM documents 
            WHERE file_size IS NOT NULL
        """)
        
        size_row = cursor.fetchone()
        if size_row[0]:
            stats['avg_file_size'] = int(size_row[0])
            stats['max_file_size'] = int(size_row[1])
            stats['min_file_size'] = int(size_row[2])
        
        conn.close()
        return stats
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {
            'total_documents': 0,
            'completed': 0,
            'pending': 0,
            'failed': 0,
            'total_chunks': 0,
            'recent_activity': 0,
            'category_breakdown': {},
            'file_type_breakdown': {},
            'avg_file_size': 0,
            'max_file_size': 0,
            'min_file_size': 0
        }

def get_rag_queries():
    """Get recent RAG queries (if available)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if query_logs table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'query_logs'
            )
        """)
        
        if cursor.fetchone()[0]:
            cursor.execute("""
                SELECT question, answer, response_time, created_at
                FROM query_logs
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            queries = []
            for row in cursor.fetchall():
                queries.append({
                    'question': row[0],
                    'answer': row[1][:100] + "..." if len(row[1]) > 100 else row[1],
                    'response_time': row[2],
                    'created_at': row[3]
                })
        else:
            queries = []
        
        conn.close()
        return queries
    except Exception as e:
        print(f"Error getting RAG queries: {e}")
        return []

@app.route('/')
def dashboard():
    """Main dashboard page"""
    documents = get_documents_with_metadata()
    stats = get_processing_stats()
    queries = get_rag_queries()
    
    return render_template('dashboard.html', 
                         documents=documents, 
                         stats=stats,
                         queries=queries)

@app.route('/api/documents')
def api_documents():
    """API endpoint for documents"""
    documents = get_documents_with_metadata()
    return jsonify(documents)

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    stats = get_processing_stats()
    return jsonify(stats)

@app.route('/api/queries')
def api_queries():
    """API endpoint for RAG queries"""
    queries = get_rag_queries()
    return jsonify(queries)

@app.route('/api/metadata/<filename>')
def api_metadata(filename):
    """API endpoint to get metadata for a specific file"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT metadata FROM documents WHERE filename = %s
        """, (filename,))
        
        row = cursor.fetchone()
        if row and row[0]:
            metadata = json.loads(row[0]) if isinstance(row[0], str) else row[0]
        else:
            metadata = {}
        
        conn.close()
        return jsonify(metadata)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)})

if __name__ == '__main__':
    print("🚀 Starting Document Management Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5001")
    print("🔍 Health check available at: http://localhost:5001/health")
    app.run(debug=True, host='0.0.0.0', port=5001) 