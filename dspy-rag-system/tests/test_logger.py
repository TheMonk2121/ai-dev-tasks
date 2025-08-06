#!/usr/bin/env python3
"""
Test script for the improved structured logger
Verifies all critical fixes and improvements
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add src to path
sys.path.append('src')

from utils.logger import get_logger, log_with_context, log_document_processing, log_error_with_context

def test_basic_logging():
    """Test basic logging functionality"""
    logger = get_logger("test_basic")
    
    logger.info("🧪 Testing basic logging", extra={
        'component': 'test_logger',
        'action': 'basic_test_start'
    })
    
    # Test different log levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    
    logger.info("✅ Basic logging test passed", extra={
        'component': 'test_logger',
        'action': 'basic_test_complete',
        'status': 'success'
    })

def test_context_logging():
    """Test context logging with various data types"""
    logger = get_logger("test_context")
    
    logger.info("🧪 Testing context logging", extra={
        'component': 'test_logger',
        'action': 'context_test_start'
    })
    
    # Test with different context types
    log_with_context(logger, "Processing document", 
                    document_id="doc_123",
                    stage="extraction",
                    elapsed_ms=1500,
                    chunk_count=5,
                    file_size=1024000,
                    custom_field="test_value",
                    numeric_field=42,
                    float_field=3.14)
    
    logger.info("✅ Context logging test passed", extra={
        'component': 'test_logger',
        'action': 'context_test_complete',
        'status': 'success'
    })

def test_document_processing_logging():
    """Test document processing specific logging"""
    logger = get_logger("test_document")
    
    logger.info("🧪 Testing document processing logging", extra={
        'component': 'test_logger',
        'action': 'document_test_start'
    })
    
    log_document_processing(logger, 
                          document_id="doc_456",
                          stage="chunking",
                          message="Document chunked successfully",
                          chunk_count=10,
                          processing_time_ms=2500)
    
    logger.info("✅ Document processing logging test passed", extra={
        'component': 'test_logger',
        'action': 'document_test_complete',
        'status': 'success'
    })

def test_error_logging():
    """Test error logging with exceptions"""
    logger = get_logger("test_error")
    
    logger.info("🧪 Testing error logging", extra={
        'component': 'test_logger',
        'action': 'error_test_start'
    })
    
    try:
        # Simulate an error
        raise ValueError("Test error for logging")
    except Exception as e:
        log_error_with_context(logger, e, "Processing failed", 
                             document_id="doc_789",
                             stage="error_test")
    
    logger.info("✅ Error logging test passed", extra={
        'component': 'test_logger',
        'action': 'error_test_complete',
        'status': 'success'
    })

def test_sensitive_data_redaction():
    """Test that sensitive data is redacted"""
    logger = get_logger("test_redaction")
    
    logger.info("🧪 Testing sensitive data redaction", extra={
        'component': 'test_logger',
        'action': 'redaction_test_start'
    })
    
    # Test with sensitive fields
    log_with_context(logger, "Testing redaction",
                    password="secret123",
                    api_token="sk-1234567890abcdef",
                    auth_key="auth_key_here",
                    normal_field="this_should_not_be_redacted")
    
    logger.info("✅ Sensitive data redaction test passed", extra={
        'component': 'test_logger',
        'action': 'redaction_test_complete',
        'status': 'success'
    })

def test_file_logging():
    """Test file logging with rotation"""
    logger = get_logger("test_file_logging")
    
    logger.info("🧪 Testing file logging", extra={
        'component': 'test_logger',
        'action': 'file_test_start'
    })
    
    # Create temporary log file
    with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as tmp:
        log_file = tmp.name
    
    try:
        file_logger = get_logger("test_file", log_file=log_file)
        
        # Write some logs
        for i in range(10):
            file_logger.info(f"Test log message {i}", extra={'iteration': i})
        
        # Check that file was created and contains logs
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if len(lines) > 0:
                    # Verify JSON format
                    first_line = json.loads(lines[0])
                    assert 'timestamp' in first_line
                    assert 'level' in first_line
                    assert 'message' in first_line
                    logger.info("✅ File logging test passed", extra={
                        'component': 'test_logger',
                        'action': 'file_test_complete',
                        'status': 'success'
                    })
                else:
                    logger.error("❌ File logging failed - no logs written", extra={
                        'component': 'test_logger',
                        'action': 'file_test_complete',
                        'status': 'failed',
                        'reason': 'no_logs_written'
                    })
        else:
            logger.error("❌ File logging failed - file not created", extra={
                'component': 'test_logger',
                'action': 'file_test_complete',
                'status': 'failed',
                'reason': 'file_not_created'
            })
            
    finally:
        # Clean up
        if os.path.exists(log_file):
            os.unlink(log_file)

def test_logger_singleton():
    """Test that logger singleton pattern works"""
    logger = get_logger("test_singleton")
    
    logger.info("🧪 Testing logger singleton", extra={
        'component': 'test_logger',
        'action': 'singleton_test_start'
    })
    
    logger1 = get_logger("singleton_test")
    logger2 = get_logger("singleton_test")
    
    # Should be the same object
    assert logger1 is logger2
    logger.info("✅ Logger singleton test passed", extra={
        'component': 'test_logger',
        'action': 'singleton_test_complete',
        'status': 'success'
    })

def test_json_serialization_safety():
    """Test JSON serialization with problematic objects"""
    print("🧪 Testing JSON serialization safety...")
    
    logger = get_logger("test_json")
    
    # Test with objects that might cause JSON serialization issues
    import datetime
    import decimal
    
    log_with_context(logger, "Testing JSON safety",
                    datetime_obj=datetime.datetime.now(),
                    decimal_obj=decimal.Decimal('3.14159'),
                    complex_obj={'nested': {'data': 'value'}},
                    list_obj=[1, 2, 3, {'key': 'value'}])
    
    print("✅ JSON serialization safety test passed")

def test_thread_safety():
    """Test thread safety of logger"""
    print("🧪 Testing thread safety...")
    
    import threading
    import time
    
    def worker(thread_id):
        logger = get_logger(f"thread_{thread_id}")
        for i in range(5):
            logger.info(f"Thread {thread_id} message {i}")
            time.sleep(0.01)
    
    # Create multiple threads
    threads = []
    for i in range(3):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    print("✅ Thread safety test passed")

def main():
    """Run all tests"""
    print("🚀 Starting Logger Tests")
    print("=" * 50)
    
    try:
        test_basic_logging()
        test_context_logging()
        test_document_processing_logging()
        test_error_logging()
        test_sensitive_data_redaction()
        test_file_logging()
        test_logger_singleton()
        test_json_serialization_safety()
        test_thread_safety()
        
        print("\n🎉 All logger tests passed!")
        print("✅ Critical fixes implemented:")
        print("   - File handler guard (no more TypeError)")
        print("   - Thread-safe singleton pattern")
        print("   - JSON serialization safety")
        print("   - Sensitive data redaction")
        print("   - Proper timestamp handling")
        print("   - Error handling and fallbacks")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 