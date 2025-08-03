#!/usr/bin/env python3
"""
Watch Folder for DSPy RAG System
Automatically processes new files dropped into the watch folder.
"""

import os
import sys
import time
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import logging
import os

# Add src to path
sys.path.append('src')

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class RAGFileHandler(FileSystemEventHandler):
    """Handles file events for the RAG system"""
    
    def __init__(self, watch_folder, processed_folder, supported_extensions=None):
        self.watch_folder = Path(watch_folder)
        self.processed_folder = Path(processed_folder)
        self.supported_extensions = supported_extensions or ['.txt', '.md', '.pdf', '.csv']
        
        # Create folders if they don't exist
        self.watch_folder.mkdir(exist_ok=True)
        self.processed_folder.mkdir(exist_ok=True)
        
        # Initialize notification system
        try:
            sys.path.append('.')
            from notification_system import NotificationSystem
            self.notification_system = NotificationSystem()
            logger.info("✅ Notification system initialized")
        except Exception as e:
            logger.warning(f"⚠️  Notification system not available: {e}")
            self.notification_system = None
        
        logger.info(f"🔍 Watching folder: {self.watch_folder}")
        logger.info(f"📁 Processed files will be moved to: {self.processed_folder}")
        logger.info(f"📄 Supported extensions: {', '.join(self.supported_extensions)}")
    
    def on_created(self, event):
        """Handle new file creation"""
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)
        if file_path.suffix.lower() in self.supported_extensions:
            logger.info(f"📝 New file detected: {file_path.name}")
            self.process_file(file_path)
    
    def on_moved(self, event):
        """Handle file moves (drag and drop)"""
        if event.is_directory:
            return
        
        file_path = Path(event.dest_path)
        if file_path.suffix.lower() in self.supported_extensions:
            logger.info(f"📝 File moved to watch folder: {file_path.name}")
            self.process_file(file_path)
    
    def process_file(self, file_path):
        """Process a file and add it to the RAG system"""
        try:
            logger.info(f"🔄 Processing file: {file_path.name}")
            
            # Run the add_document.py script
            result = subprocess.run([
                'python3', 'add_document.py', str(file_path)
            ], capture_output=True, text=True, cwd=os.getcwd())
            
            if result.returncode == 0:
                logger.info(f"✅ Successfully added {file_path.name} to RAG system")
                
                # Get file info for notification
                file_size = os.path.getsize(file_path)
                
                # Send notification
                if self.notification_system:
                    try:
                        # Extract chunks count from the output
                        chunks_count = 0
                        if "chunks stored:" in result.stdout:
                            for line in result.stdout.split('\n'):
                                if "chunks stored:" in line:
                                    chunks_count = int(line.split("chunks stored:")[1].strip())
                                    break
                        
                        self.notification_system.notify_file_processed(
                            file_path.name, 
                            chunks_count, 
                            file_size
                        )
                    except Exception as e:
                        logger.error(f"❌ Failed to send notification: {e}")
                
                # Move file to processed folder
                processed_path = self.processed_folder / file_path.name
                shutil.move(str(file_path), str(processed_path))
                logger.info(f"📁 Moved {file_path.name} to processed folder")
                
            else:
                logger.error(f"❌ Failed to process {file_path.name}: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ Error processing {file_path.name}: {e}")

def setup_watch_folder():
    """Set up the watch folder system"""
    
    # Define folders
    watch_folder = Path("watch_folder")
    processed_folder = Path("processed_documents")
    
    # Create the handler
    event_handler = RAGFileHandler(watch_folder, processed_folder)
    
    # Set up the observer
    observer = Observer()
    observer.schedule(event_handler, str(watch_folder), recursive=False)
    
    return observer, watch_folder

def main():
    """Main function to run the watch folder"""
    
    print("🚀 DSPy RAG System - Watch Folder")
    print("=" * 40)
    
    # Set up the watch folder
    observer, watch_folder = setup_watch_folder()
    
    print(f"\n📁 Watch folder created: {watch_folder.absolute()}")
    print("💡 Simply drag and drop files into this folder to add them to your RAG system!")
    print("\n📄 Supported file types:")
    print("   - Text files (.txt)")
    print("   - Markdown files (.md)")
    print("   - PDF files (.pdf)")
    print("\n🔄 The system will automatically:")
    print("   1. Detect new files")
    print("   2. Process and chunk them")
    print("   3. Add them to your knowledge base")
    print("   4. Move them to the processed folder")
    print("\n⏹️  Press Ctrl+C to stop watching")
    print("-" * 40)
    
    try:
        # Start watching
        observer.start()
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Stopping watch folder...")
        observer.stop()
        observer.join()
        print("✅ Watch folder stopped")

if __name__ == "__main__":
    main() 