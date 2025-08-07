#!/usr/bin/env python3
"""
Documentation Indexer for RAG System

Scans and indexes all documentation files for the enhanced RAG system,
providing relevant context on-demand to solve context overload.
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re

# Add the dspy-rag-system to the path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dspy-rag-system', 'src'))

from dspy_modules.vector_store import HybridVectorStore
from utils.database_resilience import get_database_manager

_LOG = logging.getLogger("documentation_indexer")

class DocumentationIndexer:
    """Indexes documentation files for RAG-based retrieval"""
    
    def __init__(self, db_connection_string: str):
        self.db_conn_str = db_connection_string
        self.vector_store = HybridVectorStore(db_connection_string)
        self.db_manager = get_database_manager(db_connection_string)
        
        # Documentation file patterns
        self.doc_patterns = [
            "*.md",  # Markdown files
            "*.txt",  # Text files
            "*.rst",  # ReStructuredText files
        ]
        
        # Exclude patterns
        self.exclude_patterns = [
            "node_modules/**",
            "venv/**",
            ".git/**",
            "__pycache__/**",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".DS_Store",
            "*.log",
            "*.tmp",
            "*.bak",
        ]
        
        # Documentation categories
        self.doc_categories = {
            "core": ["100_*.md", "000_*.md", "400_*.md"],
            "workflow": ["001_*.md", "002_*.md", "003_*.md"],
            "research": ["500_*.md"],
            "implementation": ["*.py", "*.js", "*.ts"],
            "guides": ["400_*-guide.md", "400_*-strategy.md"],
            "completion": ["500_*-completion-summary.md"],
        }
    
    def scan_documentation_files(self, root_path: str = ".") -> List[Dict[str, Any]]:
        """Scan for documentation files and extract metadata"""
        docs = []
        root = Path(root_path)
        
        _LOG.info(f"Scanning documentation files in {root}")
        
        for pattern in self.doc_patterns:
            for file_path in root.rglob(pattern):
                # Check if file should be excluded
                if self._should_exclude(file_path):
                    continue
                
                try:
                    doc_info = self._extract_document_info(file_path)
                    if doc_info:
                        docs.append(doc_info)
                except Exception as e:
                    _LOG.error(f"Error processing {file_path}: {e}")
        
        _LOG.info(f"Found {len(docs)} documentation files")
        return docs
    
    def _should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded from indexing"""
        file_str = str(file_path)
        
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.endswith("/**"):
                # Directory pattern
                dir_pattern = pattern[:-3]
                if dir_pattern in file_str:
                    return True
            elif pattern.startswith("*."):
                # File extension pattern
                if file_path.suffix == pattern[1:]:
                    return True
            else:
                # Exact pattern match
                if pattern in file_str:
                    return True
        
        return False
    
    def _extract_document_info(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract metadata and content from a documentation file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                return None
            
            # Generate file hash
            file_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Extract metadata from HTML comments
            metadata = self._extract_metadata(content)
            
            # Determine category
            category = self._determine_category(file_path, content)
            
            # Extract title and description
            title, description = self._extract_title_description(content)
            
            # Split content into chunks
            chunks = self._split_content(content)
            
            return {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_hash": file_hash,
                "category": category,
                "title": title,
                "description": description,
                "metadata": metadata,
                "chunks": chunks,
                "size_bytes": len(content.encode()),
                "line_count": len(content.split('\n')),
                "last_modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            }
            
        except Exception as e:
            _LOG.error(f"Error extracting info from {file_path}: {e}")
            return None
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from HTML comments in the content"""
        metadata = {}
        
        # Extract HTML comments
        comment_pattern = r'<!--\s*([^:]+):\s*([^>]+)\s*-->'
        matches = re.findall(comment_pattern, content)
        
        for key, value in matches:
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()
            metadata[key] = value
        
        # Parse CONTEXT_INDEX JSON block if present
        try:
            ctx_start = content.find("<!-- CONTEXT_INDEX")
            if ctx_start != -1:
                ctx_end = content.find("CONTEXT_INDEX -->", ctx_start)
                if ctx_end != -1:
                    ctx_block = content[ctx_start:ctx_end]
                    json_start = ctx_block.find("{")
                    if json_start != -1:
                        ctx_json = ctx_block[json_start:]
                        metadata["context_index"] = json.loads(ctx_json)
        except Exception:
            # Non-fatal: ignore bad/missing context index
            pass

        return metadata
    
    def _determine_category(self, file_path: Path, content: str) -> str:
        """Determine the category of a documentation file"""
        file_name = file_path.name.lower()
        
        # Check category patterns
        for category, patterns in self.doc_categories.items():
            for pattern in patterns:
                if pattern.startswith("*."):
                    # Extension pattern
                    if file_path.suffix == pattern[1:]:
                        return category
                else:
                    # Filename pattern
                    if pattern.replace("*", "").lower() in file_name:
                        return category
        
        # Default category based on content analysis
        if "research" in content.lower() or "500_" in file_name:
            return "research"
        elif "guide" in content.lower() or "400_" in file_name:
            return "guides"
        elif "completion" in content.lower() or "summary" in content.lower():
            return "completion"
        elif "workflow" in content.lower() or "process" in content.lower():
            return "workflow"
        else:
            return "core"
    
    def _extract_title_description(self, content: str) -> Tuple[str, str]:
        """Extract title and description from content"""
        lines = content.split('\n')
        title = ""
        description = ""
        
        # Look for title in first few lines
        for line in lines[:10]:
            line = line.strip()
            if line.startswith('# '):
                title = line[2:].strip()
                break
            elif line.startswith('## '):
                title = line[3:].strip()
                break
        
        # Look for description in first few lines
        for line in lines[:20]:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('<!--'):
                description = line[:200]  # First 200 chars
                break
        
        return title, description
    
    def _split_content(self, content: str, max_chunk_size: int = 1000) -> List[Dict[str, Any]]:
        """Split content into chunks for indexing"""
        chunks = []
        
        # Split by sections (headers)
        sections = re.split(r'(?=^#{1,6}\s)', content, flags=re.MULTILINE)
        
        for i, section in enumerate(sections):
            if not section.strip():
                continue
            
            # Further split large sections
            if len(section) > max_chunk_size:
                # Split by paragraphs
                paragraphs = re.split(r'\n\s*\n', section)
                for j, paragraph in enumerate(paragraphs):
                    if len(paragraph.strip()) > 50:  # Minimum chunk size
                        chunks.append({
                            "chunk_id": f"{i}_{j}",
                            "content": paragraph.strip(),
                            "start_line": self._find_start_line(content, section, i),
                            "end_line": self._find_end_line(content, section, i),
                        })
            else:
                chunks.append({
                    "chunk_id": str(i),
                    "content": section.strip(),
                    "start_line": self._find_start_line(content, section, i),
                    "end_line": self._find_end_line(content, section, i),
                })
        
        return chunks
    
    def _find_start_line(self, full_content: str, section: str, section_index: int) -> int:
        """Find the starting line number of a section"""
        lines = full_content.split('\n')
        section_start = 0
        
        for i, line in enumerate(lines):
            if section.strip() in line:
                section_start = i + 1
                break
        
        return section_start
    
    def _find_end_line(self, full_content: str, section: str, section_index: int) -> int:
        """Find the ending line number of a section"""
        lines = full_content.split('\n')
        section_end = len(lines)
        
        # Find the next section or end of file
        for i, line in enumerate(lines):
            if line.strip().startswith('#') and i > section_index:
                section_end = i
                break
        
        return section_end
    
    def index_documentation(self, root_path: str = ".") -> Dict[str, Any]:
        """Index all documentation files"""
        _LOG.info("Starting documentation indexing...")
        
        # Scan for documentation files
        docs = self.scan_documentation_files(root_path)
        
        if not docs:
            _LOG.warning("No documentation files found")
            return {"status": "no_files_found", "count": 0}
        
        # Index each document
        indexed_count = 0
        errors = []
        
        for doc in docs:
            try:
                self._index_document(doc)
                indexed_count += 1
                _LOG.info(f"Indexed {doc['file_name']}")
            except Exception as e:
                error_msg = f"Error indexing {doc['file_name']}: {e}"
                _LOG.error(error_msg)
                errors.append(error_msg)
        
        # Generate summary
        summary = {
            "status": "completed",
            "total_files": len(docs),
            "indexed_files": indexed_count,
            "errors": errors,
            "categories": self._count_categories(docs),
            "timestamp": datetime.now().isoformat(),
        }
        
        _LOG.info(f"Indexing completed: {indexed_count}/{len(docs)} files indexed")
        return summary
    
    def _index_document(self, doc: Dict[str, Any]) -> None:
        """Index a single document in the vector store"""
        # Store document metadata
        metadata = {
            "file_path": doc["file_path"],
            "file_name": doc["file_name"],
            "file_hash": doc["file_hash"],
            "category": doc["category"],
            "title": doc["title"],
            "description": doc["description"],
            "size_bytes": doc["size_bytes"],
            "line_count": doc["line_count"],
            "last_modified": doc["last_modified"],
            "indexed_at": datetime.now().isoformat(),
        }
        
        # Store each chunk
        for chunk in doc["chunks"]:
            chunk_metadata = metadata.copy()
            chunk_metadata.update({
                "chunk_id": chunk["chunk_id"],
                "start_line": chunk["start_line"],
                "end_line": chunk["end_line"],
                "chunk_size": len(chunk["content"]),
            })
            
            # Store in vector store
            self.vector_store.forward(
                operation="store_chunks",
                chunks=[chunk["content"]],
                metadata=chunk_metadata
            )
    
    def _count_categories(self, docs: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count documents by category"""
        categories = {}
        for doc in docs:
            category = doc["category"]
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def search_documentation(self, query: str, category: str = None, limit: int = 5) -> Dict[str, Any]:
        """Search documentation using the RAG system"""
        search_params = {
            "query": query,
            "limit": limit,
        }
        
        if category:
            search_params["category"] = category
        
        results = self.vector_store.forward(operation="search", **search_params)
        
        # Add search metadata
        results["search_query"] = query
        results["search_category"] = category
        results["search_timestamp"] = datetime.now().isoformat()
        
        return results
    
    def get_documentation_stats(self) -> Dict[str, Any]:
        """Get statistics about indexed documentation"""
        # This would query the database for statistics
        # For now, return basic info
        return {
            "indexed_at": datetime.now().isoformat(),
            "vector_store_stats": self.vector_store.get_stats(),
        }


def main():
    """Main function for documentation indexing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Documentation Indexer for RAG System")
    parser.add_argument("--db-url", default=None, help="Database connection string")
    parser.add_argument("--root-path", default=".", help="Root path to scan for documentation")
    parser.add_argument("--search", help="Search query to test")
    parser.add_argument("--category", help="Category filter for search")
    parser.add_argument("--stats", action="store_true", help="Show indexing statistics")
    
    args = parser.parse_args()
    
    # Get database URL
    if args.db_url:
        db_url = args.db_url
    else:
        # Try to get from environment or use default
        db_url = os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")
    
    # Initialize indexer
    indexer = DocumentationIndexer(db_url)
    
    if args.search:
        # Perform search
        results = indexer.search_documentation(args.search, args.category)
        print(json.dumps(results, indent=2))
    elif args.stats:
        # Show statistics
        stats = indexer.get_documentation_stats()
        print(json.dumps(stats, indent=2))
    else:
        # Perform indexing
        summary = indexer.index_documentation(args.root_path)
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
