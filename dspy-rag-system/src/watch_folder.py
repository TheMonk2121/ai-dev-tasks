#!/usr/bin/env python3.12.123.11
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
    
    LOG.info("🚀 DSPy RAG System - Watch Folder 2.0 starting", extra={
        'component': 'watch_folder',
        'action': 'startup',
        'version': '2.0'
    })
    
    # Get configuration from environment variables
    watch_dir = os.getenv("WATCH_DIR", "watch_folder")
    processed_dir = os.getenv("PROCESSED_DIR", "processed_documents")
    workers = int(os.getenv("WORKERS", "4"))
    
    LOG.info("📁 Watch folder configuration", extra={
        'component': 'watch_folder',
        'action': 'configuration',
        'watch_dir': watch_dir,
        'processed_dir': processed_dir,
        'workers': workers,
        'supported_extensions': list(SAFE_EXT)
    })
    
    LOG.info("🔄 Watch folder workflow", extra={
        'component': 'watch_folder',
        'action': 'workflow_description',
        'steps': [
            'Detect new files',
            'Wait for file stability',
            'Process and chunk them',
            'Add them to your knowledge base',
            'Move them to the processed folder'
        ]
    })
    
    with WatchService(watch_dir, processed_dir, workers):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            LOG.info("⏹️  Stopping watch folder", extra={
                'component': 'watch_folder',
                'action': 'shutdown',
                'reason': 'keyboard_interrupt'
            })
            LOG.info("✅ Watch folder stopped", extra={
                'component': 'watch_folder',
                'action': 'shutdown',
                'status': 'completed'
            })

if __name__ == "__main__":
    main() 