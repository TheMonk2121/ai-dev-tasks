#!/usr/bin/env python3
"""
Documentation Retrieval CLI

Command-line interface for the documentation retrieval system,
providing easy access to RAG-based documentation search.
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, Any, Optional

# Add the dspy-rag-system to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'dspy-rag-system', 'src'))

from dspy_modules.documentation_retrieval import (
    create_documentation_retrieval_service,
    get_relevant_context,
    search_documentation,
    get_task_context
)
from documentation_indexer import DocumentationIndexer

# Configure logging
logging.basicConfig(level=logging.INFO)
_LOG = logging.getLogger("documentation_retrieval_cli")

class DocumentationRetrievalCLI:
    """Command-line interface for documentation retrieval"""
    
    def __init__(self, db_connection_string: str = None):
        if db_connection_string is None:
            db_connection_string = os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")
        
        self.db_conn_str = db_connection_string
        self.service = create_documentation_retrieval_service(db_connection_string)
        self.indexer = DocumentationIndexer(db_connection_string)
    
    def search(self, query: str, category: str = None, limit: int = 5, format_output: str = "json") -> None:
        """Search documentation"""
        try:
            results = self.service.search_documentation(query, category, limit)
            self._print_results(results, format_output)
        except Exception as e:
            _LOG.error(f"Search failed: {e}")
            print(f"Error: {e}")
    
    def get_context(self, query: str, context_type: str = "general", format_output: str = "json") -> None:
        """Get relevant context for a query"""
        try:
            results = self.service.forward(query, context_type)
            self._print_results(results, format_output)
        except Exception as e:
            _LOG.error(f"Context retrieval failed: {e}")
            print(f"Error: {e}")
    
    def get_task_context(self, task_description: str, task_type: str = "development", format_output: str = "json") -> None:
        """Get context for a specific task"""
        try:
            results = self.service.get_context_for_task(task_description, task_type)
            self._print_results(results, format_output)
        except Exception as e:
            _LOG.error(f"Task context retrieval failed: {e}")
            print(f"Error: {e}")
    
    def index_documentation(self, root_path: str = ".", format_output: str = "json") -> None:
        """Index documentation files"""
        try:
            summary = self.indexer.index_documentation(root_path)
            self._print_results(summary, format_output)
        except Exception as e:
            _LOG.error(f"Indexing failed: {e}")
            print(f"Error: {e}")
    
    def get_stats(self, format_output: str = "json") -> None:
        """Get documentation statistics"""
        try:
            stats = self.service.get_documentation_stats()
            self._print_results(stats, format_output)
        except Exception as e:
            _LOG.error(f"Stats retrieval failed: {e}")
            print(f"Error: {e}")
    
    def _print_results(self, results: Dict[str, Any], format_output: str) -> None:
        """Print results in the specified format"""
        if format_output == "json":
            print(json.dumps(results, indent=2))
        elif format_output == "text":
            self._print_text_results(results)
        elif format_output == "summary":
            self._print_summary_results(results)
        else:
            print(json.dumps(results, indent=2))
    
    def _print_text_results(self, results: Dict[str, Any]) -> None:
        """Print results in human-readable text format"""
        if "error" in results:
            print(f"Error: {results['error']}")
            return
        
        if "query" in results:
            print(f"Query: {results['query']}")
            print()
        
        if "relevant_context" in results and results["relevant_context"]:
            print("Relevant Context:")
            print("-" * 50)
            print(results["relevant_context"])
            print()
        
        if "context_summary" in results:
            print(f"Summary: {results['context_summary']}")
            print()
        
        if "confidence_score" in results:
            print(f"Confidence: {results['confidence_score']:.2f}")
            print()
        
        if "context_metadata" in results:
            metadata = results["context_metadata"]
            if "sources" in metadata and metadata["sources"]:
                print("Sources:")
                for source in metadata["sources"]:
                    print(f"  - {source}")
                print()
            
            if "categories" in metadata and metadata["categories"]:
                print("Categories:")
                for category in metadata["categories"]:
                    print(f"  - {category}")
                print()
        
        if "results" in results and results["results"]:
            print("Retrieved Chunks:")
            print("-" * 50)
            for i, chunk in enumerate(results["results"][:3], 1):  # Show first 3 chunks
                if "content" in chunk:
                    print(f"Chunk {i}:")
                    print(chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"])
                    print()
    
    def _print_summary_results(self, results: Dict[str, Any]) -> None:
        """Print a summary of results"""
        if "error" in results:
            print(f"❌ Error: {results['error']}")
            return
        
        if "query" in results:
            print(f"🔍 Query: {results['query']}")
        
        if "context_summary" in results:
            print(f"📋 Summary: {results['context_summary']}")
        
        if "confidence_score" in results:
            confidence = results["confidence_score"]
            if confidence > 0.8:
                print(f"✅ Confidence: {confidence:.2f}")
            elif confidence > 0.5:
                print(f"⚠️  Confidence: {confidence:.2f}")
            else:
                print(f"❌ Confidence: {confidence:.2f}")
        
        if "context_metadata" in results:
            metadata = results["context_metadata"]
            if "sources" in metadata and metadata["sources"]:
                print(f"📚 Sources: {len(metadata['sources'])} files")
            if "categories" in metadata and metadata["categories"]:
                print(f"📁 Categories: {', '.join(metadata['categories'])}")
        
        if "results" in results:
            print(f"📄 Retrieved: {len(results['results'])} chunks")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Documentation Retrieval CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search documentation
  python documentation_retrieval_cli.py search "how to implement RAG"
  
  # Get context for a task
  python documentation_retrieval_cli.py context "implement file splitting" --type workflow
  
  # Get task-specific context
  python documentation_retrieval_cli.py task "implement documentation indexing" --task-type development
  
  # Index documentation
  python documentation_retrieval_cli.py index
  
  # Get statistics
  python documentation_retrieval_cli.py stats
        """
    )
    
    # Global arguments
    parser.add_argument("--db-url", help="Database connection string")
    parser.add_argument("--format", choices=["json", "text", "summary"], default="json", 
                       help="Output format")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search documentation")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--category", help="Category filter")
    search_parser.add_argument("--limit", type=int, default=5, help="Maximum results")
    
    # Context command
    context_parser = subparsers.add_parser("context", help="Get relevant context")
    context_parser.add_argument("query", help="Query for context")
    context_parser.add_argument("--type", default="general", 
                               choices=["general", "workflow", "research", "implementation", "core", "guides"],
                               help="Context type")
    
    # Task context command
    task_parser = subparsers.add_parser("task", help="Get task-specific context")
    task_parser.add_argument("description", help="Task description")
    task_parser.add_argument("--task-type", default="development",
                            choices=["development", "research", "workflow", "planning", "testing", "deployment"],
                            help="Task type")
    
    # Index command
    index_parser = subparsers.add_parser("index", help="Index documentation")
    index_parser.add_argument("--root-path", default=".", help="Root path to scan")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Get documentation statistics")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize CLI
    db_url = args.db_url or os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag")
    cli = DocumentationRetrievalCLI(db_url)
    
    try:
        if args.command == "search":
            cli.search(args.query, args.category, args.limit, args.format)
        elif args.command == "context":
            cli.get_context(args.query, args.type, args.format)
        elif args.command == "task":
            cli.get_task_context(args.description, args.task_type, args.format)
        elif args.command == "index":
            cli.index_documentation(args.root_path, args.format)
        elif args.command == "stats":
            cli.get_stats(args.format)
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        _LOG.error(f"CLI error: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
