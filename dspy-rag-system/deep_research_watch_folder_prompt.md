# Deep Research Analysis Request: Watch Folder Module

## Context for Code Review

You're reviewing code written by Mistral 7B, a local LLM. It performs well at scaffolding and code structure, but often lacks deeper reasoning, architectural foresight, or context awareness.

Your job is to act as a senior engineer performing a system-aware code review.

### Instructions:

1. Identify logic flaws, fragility, or missing edge-case handling.
2. Suggest architectural improvements where appropriate (e.g., modularization, separation of concerns, interface clarity).
3. Comment on naming, clarity, and promptability if this will be used in a RAG system.
4. If you notice redundancy, inefficiency, or memory issues, suggest fixes.
5. Offer succinct inline comments or markdown-style callouts, not essays.
6. If the code looks fine, suggest 1–2 improvements anyway based on likely future growth.

This code is likely one chunk in a broader RAG system (Retrieval-Augmented Generation), possibly involving DSPy, LangChain, or custom vector logic. Assume that, but don't over-index on it.

## Development Environment & Tools

- **Python 3.9** (not 3.10+ features like `match` statements)
- **DSPy framework** for LLM orchestration and prompt engineering
- **PostgreSQL with pgvector** for vector storage and similarity search
- **Ollama with Mistral-7B** for local LLM inference
- **Flask** for web dashboard (planned)
- **n8n** for workflow automation (planned)
- **watchdog** for file system monitoring
- **Local development** - no cloud dependencies

## Recent Improvements Made

We've already implemented critical fixes in other modules:

### VectorStore Module:
- ✅ **pgvector adapter** for direct numpy storage
- ✅ **Connection pooling** with SimpleConnectionPool
- ✅ **Singleton model** with @lru_cache for SentenceTransformer
- ✅ **Bulk inserts** with execute_values for efficiency
- ✅ **UUID document IDs** to prevent collisions
- ✅ **Metadata optimization** (once per document, not per chunk)

### RAG System Module:
- ✅ **Connection pooling & retry logic** for Ollama API calls
- ✅ **Token-aware truncation** with tiktoken to prevent crashes
- ✅ **Prompt injection prevention** with input sanitization
- ✅ **LRU caching** for identical queries
- ✅ **Enhanced error handling** with structured responses

### DocumentProcessor Module:
- ✅ **UUID-based document IDs** to prevent collisions
- ✅ **PyMuPDF integration** for better PDF handling
- ✅ **Structured chunks** with rich metadata
- ✅ **Security validation** with file path and size limits
- ✅ **CSV streaming** for memory-efficient processing

## Current Code for Review

Please review the following Watch Folder module code:

```python
#!/usr/bin/env python3
"""
Watch Folder 2.0 – hardened for production
Python 3.9 compatible
"""

import os
import sys
import time
import shutil
import logging
import subprocess
import shlex
import signal
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent

# Add src to path for imports
sys.path.append('src')

# Import structured logger from core
try:
    from utils.logger import get_logger
    LOG = get_logger("watch_folder")
except ImportError:
    # Fallback to basic logging if structured logger not available
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    LOG = logging.getLogger("watch_folder")

SAFE_EXT = {".txt", ".md", ".pdf", ".csv"}

# ---------- helpers ----------
def _is_file_ready(p: Path, polls: int = 2, delay: float = 0.5) -> bool:
    """Return True when file size is stable."""
    try:
        size = p.stat().st_size
        for _ in range(polls):
            time.sleep(delay)
            new = p.stat().st_size
            if new != size:
                size = new
            else:
                return True
        return False
    except (OSError, FileNotFoundError):
        return False

def _run_add_document(file_path: Path, timeout: int = 300) -> subprocess.CompletedProcess:
    """Secure wrapper around add_document.py."""
    cmd = ["python3", "add_document.py", str(file_path)]
    # never interpolate user path into shell string
    return subprocess.run(cmd,
                          capture_output=True,
                          text=True,
                          cwd=os.getcwd(),
                          timeout=timeout,
                          check=False)

# ---------- service ----------
class RAGFileHandler(FileSystemEventHandler):
    def __init__(self, watch: Path, processed: Path, pool: ThreadPoolExecutor):
        self.watch = watch
        self.processed = processed
        self.pool = pool
        
        # Create folders if they don't exist
        self.watch.mkdir(exist_ok=True)
        self.processed.mkdir(exist_ok=True)
        
        # Initialize notification system (optional)
        try:
            sys.path.append('.')
            from notification_system import NotificationSystem
            self.notification_system = NotificationSystem()
            LOG.info("✅ Notification system initialized")
        except Exception as e:
            LOG.warning(f"⚠️  Notification system not available: {e}")
            self.notification_system = None
        
        LOG.info("Watching %s", self.watch)
        LOG.info("Processed files will be moved to: %s", self.processed)
        LOG.info("Supported extensions: %s", ', '.join(SAFE_EXT))

    # watchdog passes subclass specific events – use common method
    def on_created(self, event: FileCreatedEvent):
        self._maybe_queue(Path(event.src_path))

    def on_moved(self, event: FileMovedEvent):
        self._maybe_queue(Path(event.dest_path))

    # ---- internal ----
    def _maybe_queue(self, file_path: Path):
        if file_path.suffix.lower() not in SAFE_EXT:
            return
        LOG.info("Detected %s", file_path.name)
        # schedule async processing
        self.pool.submit(self._process_file_safe, file_path)

    def _process_file_safe(self, file_path: Path):
        try:
            if not _is_file_ready(file_path):
                LOG.warning("File not stable: %s", file_path)
                return
            
            LOG.info("Processing file: %s", file_path.name)
            res = _run_add_document(file_path)
            
            if res.returncode == 0:
                LOG.info("add_document success for %s", file_path.name,
                         extra={"stdout": res.stdout.strip()})
                
                # Send notification if available
                if self.notification_system:
                    try:
                        # Extract chunks count from the output
                        chunks_count = 0
                        if "chunks stored:" in res.stdout:
                            for line in res.stdout.split('\n'):
                                if "chunks stored:" in line:
                                    chunks_count = int(line.split("chunks stored:")[1].strip())
                                    break
                        
                        file_size = os.path.getsize(file_path)
                        self.notification_system.notify_file_processed(
                            file_path.name, 
                            chunks_count, 
                            file_size
                        )
                    except Exception as e:
                        LOG.error("Failed to send notification: %s", e)
                
                # Move file to processed folder
                processed_path = self.processed / file_path.name
                shutil.move(str(file_path), str(processed_path))
                LOG.info("Moved %s to processed folder", file_path.name)
                
            else:
                LOG.error("add_document failed for %s – %s",
                          file_path.name, res.stderr.strip())
                
        except subprocess.TimeoutExpired:
            LOG.error("add_document timeout for %s", file_path.name)
        except Exception as exc:
            LOG.exception("Unhandled error processing %s: %s", file_path.name, exc)

class WatchService:
    """Context-manager driven wrapper – handles graceful shutdown."""
    def __init__(self, watch_dir="watch_folder", processed_dir="processed_documents",
                 workers: int = 4):
        self.watch = Path(watch_dir)
        self.processed = Path(processed_dir)
        self.pool = ThreadPoolExecutor(max_workers=workers)
        self.handler = RAGFileHandler(self.watch, self.processed, self.pool)
        self.observer = Observer()

    def __enter__(self):
        self.observer.schedule(self.handler, str(self.watch), recursive=False)
        self.observer.start()
        LOG.info("Observer started")
        return self

    def __exit__(self, exc_type, exc, tb):
        LOG.info("Shutting down watch service…")
        self.observer.stop()
        self.observer.join()
        self.pool.shutdown(wait=True)

def setup_watch_folder():
    """Legacy function for backward compatibility"""
    watch_folder = Path("watch_folder")
    processed_folder = Path("processed_documents")
    
    # Create the handler with a single worker for legacy compatibility
    pool = ThreadPoolExecutor(max_workers=1)
    event_handler = RAGFileHandler(watch_folder, processed_folder, pool)
    
    # Set up the observer
    observer = Observer()
    observer.schedule(event_handler, str(watch_folder), recursive=False)
    
    return observer, watch_folder

def main():
    """Main function to run the watch folder"""
    
    print("🚀 DSPy RAG System - Watch Folder 2.0")
    print("=" * 40)
    
    # Get configuration from environment variables
    watch_dir = os.getenv("WATCH_DIR", "watch_folder")
    processed_dir = os.getenv("PROCESSED_DIR", "processed_documents")
    workers = int(os.getenv("WORKERS", "4"))
    
    print(f"\n📁 Watch folder: {watch_dir}")
    print(f"📁 Processed folder: {processed_dir}")
    print(f"🔧 Workers: {workers}")
    print("\n📄 Supported file types:")
    print("   - Text files (.txt)")
    print("   - Markdown files (.md)")
    print("   - PDF files (.pdf)")
    print("   - CSV files (.csv)")
    print("\n🔄 The system will automatically:")
    print("   1. Detect new files")
    print("   2. Wait for file stability")
    print("   3. Process and chunk them")
    print("   4. Add them to your knowledge base")
    print("   5. Move them to the processed folder")
    print("\n⏹️  Press Ctrl+C to stop watching")
    print("-" * 40)
    
    with WatchService(watch_dir, processed_dir, workers):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Stopping watch folder...")
            print("✅ Watch folder stopped")

if __name__ == "__main__":
    main()
```

## Critical Request: Test Code for Every Improvement

**IMPORTANT**: For every improvement you suggest, please provide the **actual test code** to validate that improvement. This is crucial because:

1. **We want to test the implementation, not just the idea**
2. **Deep research approaches testing differently** - we want to see your testing methodology
3. **Production readiness** requires comprehensive test coverage
4. **We need specific, runnable test code** for every suggested fix

### Test Requirements:
- **Unit tests** for individual functions/methods
- **Integration tests** for component interactions
- **Performance tests** with benchmarks and thresholds
- **Security tests** for vulnerabilities and validation
- **Resilience tests** for error handling and failure scenarios
- **Edge case tests** for boundary conditions and unusual inputs
- **Complete setup/teardown** with proper isolation
- **Specific assertions** and expected outcomes
- **Performance benchmarks** where applicable

Please provide the **complete test code** for every improvement you suggest, not just test descriptions. We want to see your testing approach and implementation.

## Review Focus Areas

Given this is a file system monitoring component in a RAG system, please focus on:

1. **Subprocess Security**: Command injection prevention, safe argument passing
2. **File System Reliability**: Race conditions, partial writes, concurrent access
3. **Error Handling**: Graceful failure recovery, resource cleanup
4. **Resource Management**: Memory usage, thread management, process isolation
5. **Concurrent Processing**: Thread safety, deadlock prevention, performance
6. **Notification Integration**: Error handling, fallback mechanisms
7. **Production Readiness**: Logging, monitoring, configuration management

Please provide your analysis with specific, actionable improvements and the complete test code to validate each improvement. 