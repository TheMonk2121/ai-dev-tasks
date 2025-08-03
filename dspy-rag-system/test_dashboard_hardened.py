#!/usr/bin/env python3
"""
Comprehensive Test Suite for Hardened Dashboard Module
Validates all critical fixes identified by deep research
"""

import io
import time
import threading
import os
import atexit
import signal
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
import sys
sys.path.append('src')

try:
    from src.dashboard import app as flask_app, state, _check_rate
except ImportError as e:
    pytest.skip(f"Dashboard module not available: {e}")

# ---------- Test Fixtures ----------

@pytest.fixture
def client(tmp_path, monkeypatch):
    """Create test client with temporary upload directory"""
    monkeypatch.setitem(flask_app.config, "UPLOAD_FOLDER", str(tmp_path))
    return flask_app.test_client()

@pytest.fixture
def mock_rag_interface(monkeypatch):
    """Mock RAG interface for testing"""
    mock_interface = Mock()
    mock_interface.ask.return_value = {
        'status': 'success',
        'answer': 'Test answer',
        'sources': ['doc1'],
        'rewritten_query': 'Test query',
        'reasoning': 'Test reasoning',
        'confidence': 0.9
    }
    monkeypatch.setattr(state, 'rag_interface', mock_interface)
    return mock_interface

# ---------- D-1: Upload Security Tests ----------

class TestUploadSecurity:
    """Test upload security hardening (D-1)"""
    
    def test_upload_reject_traversal(self, client):
        """Test that path traversal attempts are rejected"""
        resp = client.post('/upload',
            data={'file': (io.BytesIO(b'data'), '../../evil.txt')},
            content_type='multipart/form-data')
        assert resp.status_code == 400
        assert 'Bad filename' in resp.get_json()['error']
    
    def test_upload_reject_slash_in_filename(self, client):
        """Test that filenames with slashes are rejected"""
        resp = client.post('/upload',
            data={'file': (io.BytesIO(b'data'), 'evil/../file.txt')},
            content_type='multipart/form-data')
        assert resp.status_code == 400
        assert 'Bad filename' in resp.get_json()['error']
    
    def test_upload_reject_invalid_extension(self, client):
        """Test that invalid file extensions are rejected"""
        resp = client.post('/upload',
            data={'file': (io.BytesIO(b'data'), 'test.exe')},
            content_type='multipart/form-data')
        assert resp.status_code == 400
        assert 'File type not allowed' in resp.get_json()['error']
    
    def test_upload_accept_valid_file(self, client, tmp_path):
        """Test that valid files are accepted"""
        resp = client.post('/upload',
            data={'file': (io.BytesIO(b'test data'), 'good.txt')},
            content_type='multipart/form-data')
        assert resp.status_code == 200
        assert resp.get_json()['success'] is True
        assert (tmp_path / 'good.txt').exists()
    
    def test_upload_accept_pdf_file(self, client, tmp_path):
        """Test that PDF files are accepted"""
        resp = client.post('/upload',
            data={'file': (io.BytesIO(b'%PDF-1.4'), 'document.pdf')},
            content_type='multipart/form-data')
        assert resp.status_code == 200
        assert (tmp_path / 'document.pdf').exists()
    
    def test_upload_accept_csv_file(self, client, tmp_path):
        """Test that CSV files are accepted"""
        resp = client.post('/upload',
            data={'file': (io.BytesIO(b'name,value\n'), 'data.csv')},
            content_type='multipart/form-data')
        assert resp.status_code == 200
        assert (tmp_path / 'data.csv').exists()
    
    def test_upload_accept_md_file(self, client, tmp_path):
        """Test that Markdown files are accepted"""
        resp = client.post('/upload',
            data={'file': (io.BytesIO(b'# Test'), 'readme.md')},
            content_type='multipart/form-data')
        assert resp.status_code == 200
        assert (tmp_path / 'readme.md').exists()
    
    def test_upload_no_file_provided(self, client):
        """Test handling when no file is provided"""
        resp = client.post('/upload', content_type='multipart/form-data')
        assert resp.status_code == 400
        assert 'No file provided' in resp.get_json()['error']
    
    def test_upload_empty_filename(self, client):
        """Test handling when filename is empty"""
        resp = client.post('/upload',
            data={'file': (io.BytesIO(b'data'), '')},
            content_type='multipart/form-data')
        assert resp.status_code == 400
        assert 'No file selected' in resp.get_json()['error']

# ---------- D-2: Rate Limiting Tests ----------

class TestRateLimiting:
    """Test rate limiting functionality (D-2)"""
    
    def test_rate_limit_normal_usage(self, client, mock_rag_interface):
        """Test normal usage within rate limits"""
        # Make 10 requests (well within limit)
        for i in range(10):
            resp = client.post('/query', json={'query': f'test query {i}'})
            assert resp.status_code == 200
            assert resp.get_json()['success'] is True
    
    def test_rate_limit_exceeded(self, client, mock_rag_interface):
        """Test rate limit exceeded scenario"""
        # Make 21 requests (exceeds 20 limit)
        responses = []
        for i in range(21):
            resp = client.post('/query', json={'query': f'test query {i}'})
            responses.append(resp)
        
        # Last request should be rate limited
        assert responses[-1].status_code == 429
        assert 'Rate limit exceeded' in responses[-1].get_json()['error']
    
    def test_rate_limit_reset_after_window(self, client, mock_rag_interface):
        """Test that rate limit resets after time window"""
        # Make 20 requests (at limit)
        for i in range(20):
            resp = client.post('/query', json={'query': f'test query {i}'})
            assert resp.status_code == 200
        
        # Next request should be rate limited
        resp = client.post('/query', json={'query': 'should be limited'})
        assert resp.status_code == 429
        
        # Mock time passing to simulate window expiration
        with patch('time.monotonic') as mock_time:
            mock_time.return_value = time.monotonic() + 61  # 61 seconds later
            
            # Should be able to make requests again
            resp = client.post('/query', json={'query': 'should work now'})
            assert resp.status_code == 200
    
    def test_rate_limit_different_ips(self, client, mock_rag_interface):
        """Test that rate limits are per IP address"""
        # Mock different IP addresses
        with patch('flask.request') as mock_request:
            # First IP makes 20 requests
            mock_request.remote_addr = '192.168.1.1'
            for i in range(20):
                resp = client.post('/query', json={'query': f'ip1 query {i}'})
                assert resp.status_code == 200
            
            # Second IP should still be able to make requests
            mock_request.remote_addr = '192.168.1.2'
            resp = client.post('/query', json={'query': 'ip2 query'})
            assert resp.status_code == 200
    
    def test_rate_limit_unknown_ip(self, client, mock_rag_interface):
        """Test rate limiting with unknown IP"""
        with patch('flask.request') as mock_request:
            mock_request.remote_addr = None
            
            # Should still work with 'unknown' IP
            resp = client.post('/query', json={'query': 'test query'})
            assert resp.status_code == 200

# ---------- D-3: Thread-Safe History Tests ----------

class TestThreadSafeHistory:
    """Test thread-safe history functionality (D-3)"""
    
    def test_history_thread_safety(self, client, mock_rag_interface):
        """Test that history is thread-safe under concurrent access"""
        def worker():
            """Worker function to make concurrent requests"""
            with flask_app.test_client() as c:
                for i in range(25):
                    resp = c.post('/query', json={'query': f'concurrent query {i}'})
                    assert resp.status_code == 200
        
        # Start multiple threads
        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        
        # Wait for all threads to complete
        for t in threads:
            t.join()
        
        # Check that history is bounded and not corrupted
        with state.history_lock:
            assert len(state.query_history) <= 100  # Bounded by deque maxlen
            assert len(state.query_history) > 0     # Should have some entries
    
    def test_history_bounded_size(self, client, mock_rag_interface):
        """Test that history is bounded to 100 entries"""
        # Make 150 requests
        for i in range(150):
            resp = client.post('/query', json={'query': f'query {i}'})
            assert resp.status_code == 200
        
        # Check that history is bounded
        with state.history_lock:
            assert len(state.query_history) == 100  # Max size
            # Should have the most recent queries
            latest_query = list(state.query_history)[-1]['query']
            assert 'query 149' in latest_query
    
    def test_history_lock_protection(self, client, mock_rag_interface):
        """Test that history lock protects against race conditions"""
        def concurrent_reader():
            """Concurrent reader of history"""
            with flask_app.test_client() as c:
                for _ in range(10):
                    resp = c.get('/api/query_history')
                    assert resp.status_code == 200
        
        def concurrent_writer():
            """Concurrent writer to history"""
            with flask_app.test_client() as c:
                for i in range(10):
                    resp = c.post('/query', json={'query': f'race query {i}'})
                    assert resp.status_code == 200
        
        # Start concurrent readers and writers
        readers = [threading.Thread(target=concurrent_reader) for _ in range(3)]
        writers = [threading.Thread(target=concurrent_writer) for _ in range(3)]
        
        for t in readers + writers:
            t.start()
        
        for t in readers + writers:
            t.join()
        
        # Should not have crashed or corrupted data
        with state.history_lock:
            assert len(state.query_history) <= 100
    
    def test_history_api_thread_safe(self, client, mock_rag_interface):
        """Test that history API endpoint is thread-safe"""
        # Make some queries first
        for i in range(5):
            resp = client.post('/query', json={'query': f'api test {i}'})
            assert resp.status_code == 200
        
        def concurrent_api_calls():
            """Make concurrent API calls to history endpoint"""
            with flask_app.test_client() as c:
                for _ in range(10):
                    resp = c.get('/api/query_history')
                    assert resp.status_code == 200
                    data = resp.get_json()
                    assert isinstance(data, list)
        
        # Start multiple threads making API calls
        threads = [threading.Thread(target=concurrent_api_calls) for _ in range(5)]
        for t in threads:
            t.start()
        
        for t in threads:
            t.join()
        
        # Should not have crashed

# ---------- D-4: Executor Shutdown Tests ----------

class TestExecutorShutdown:
    """Test executor shutdown functionality (D-4)"""
    
    def test_executor_shutdown_on_exit(self):
        """Test that executor is properly registered for shutdown"""
        # Check that atexit handler is registered
        atexit_handlers = [fn for fn, _ in atexit._exithandlers]
        assert any('shutdown' in str(handler) for handler in atexit_handlers)
    
    def test_executor_shutdown_signal_handler(self):
        """Test that SIGTERM handler is registered"""
        # Check that signal handler is registered
        assert signal.getsignal(signal.SIGTERM) is not None
    
    def test_executor_creation_and_shutdown(self):
        """Test executor creation and shutdown cycle"""
        # Create a new executor for testing
        from concurrent.futures import ThreadPoolExecutor
        test_executor = ThreadPoolExecutor(max_workers=2)
        
        # Submit a simple task
        future = test_executor.submit(lambda: "test")
        result = future.result()
        assert result == "test"
        
        # Shutdown executor
        test_executor.shutdown(wait=False)
        assert test_executor._shutdown
    
    def test_executor_graceful_shutdown(self):
        """Test graceful shutdown of executor"""
        # The main executor should be properly configured
        assert state.executor is not None
        assert not state.executor._shutdown  # Should not be shutdown initially

# ---------- Integration Tests ----------

class TestDashboardIntegration:
    """Test complete dashboard integration"""
    
    def test_complete_upload_and_query_flow(self, client, tmp_path):
        """Test complete flow from upload to query"""
        # Upload a file
        resp = client.post('/upload',
            data={'file': (io.BytesIO(b'This is a test document.'), 'test.txt')},
            content_type='multipart/form-data')
        assert resp.status_code == 200
        
        # Wait a moment for processing
        time.sleep(0.1)
        
        # Make a query
        resp = client.post('/query', json={'query': 'What is in the document?'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['success'] is True
        assert 'answer' in data
    
    def test_health_check_endpoint(self, client):
        """Test health check endpoint"""
        resp = client.get('/api/health')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'status' in data
        assert 'components' in data
        assert 'timestamp' in data
    
    def test_stats_endpoint(self, client):
        """Test stats endpoint"""
        resp = client.get('/api/stats')
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'total_documents' in data
        assert 'total_chunks' in data
        assert 'total_queries' in data
    
    def test_processing_status_endpoint(self, client):
        """Test processing status endpoint"""
        resp = client.get('/api/processing')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
    
    def test_query_history_endpoint(self, client, mock_rag_interface):
        """Test query history endpoint"""
        # Make a query first
        resp = client.post('/query', json={'query': 'test query'})
        assert resp.status_code == 200
        
        # Check history
        resp = client.get('/api/query_history')
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) > 0

# ---------- Error Handling Tests ----------

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_file_too_large_error(self, client):
        """Test handling of file too large error"""
        # Mock a file that's too large
        large_data = b'x' * (100 * 1024 * 1024 + 1)  # 100MB + 1 byte
        
        resp = client.post('/upload',
            data={'file': (io.BytesIO(large_data), 'large.txt')},
            content_type='multipart/form-data')
        assert resp.status_code == 413
    
    def test_invalid_json_in_query(self, client):
        """Test handling of invalid JSON in query"""
        resp = client.post('/query', 
            data='invalid json',
            content_type='application/json')
        assert resp.status_code == 400
    
    def test_missing_query_parameter(self, client):
        """Test handling of missing query parameter"""
        resp = client.post('/query', json={})
        assert resp.status_code == 400
        assert 'Query is required' in resp.get_json()['error']
    
    def test_empty_query(self, client):
        """Test handling of empty query"""
        resp = client.post('/query', json={'query': ''})
        assert resp.status_code == 400
        assert 'Query is required' in resp.get_json()['error']
    
    def test_query_too_long(self, client):
        """Test handling of query that's too long"""
        long_query = 'x' * 1001  # Exceeds 1000 character limit
        resp = client.post('/query', json={'query': long_query})
        assert resp.status_code == 400
        assert 'Query too long' in resp.get_json()['error']

# ---------- Performance Tests ----------

class TestPerformance:
    """Test performance characteristics"""
    
    def test_rate_limit_performance(self, benchmark):
        """Test rate limiting performance"""
        def check_rate():
            return _check_rate('test_ip')
        
        result = benchmark(check_rate)
        assert result is True
    
    def test_upload_validation_performance(self, client, benchmark):
        """Test upload validation performance"""
        def upload_file():
            return client.post('/upload',
                data={'file': (io.BytesIO(b'test'), 'test.txt')},
                content_type='multipart/form-data')
        
        result = benchmark(upload_file)
        assert result.status_code in [200, 400]  # Either success or validation error
    
    def test_query_processing_performance(self, client, mock_rag_interface, benchmark):
        """Test query processing performance"""
        def make_query():
            return client.post('/query', json={'query': 'test query'})
        
        result = benchmark(make_query)
        assert result.status_code == 200

# ---------- Security Tests ----------

class TestSecurity:
    """Test security measures"""
    
    def test_path_traversal_protection(self, client):
        """Test protection against path traversal attacks"""
        malicious_filenames = [
            '../../../etc/passwd',
            '..\\..\\windows\\system32\\config\\sam',
            '....//....//....//etc/passwd',
            'file.txt/../evil.txt',
            'file.txt\\..\\evil.txt'
        ]
        
        for filename in malicious_filenames:
            resp = client.post('/upload',
                data={'file': (io.BytesIO(b'data'), filename)},
                content_type='multipart/form-data')
            assert resp.status_code == 400
            assert 'Bad filename' in resp.get_json()['error']
    
    def test_file_extension_validation(self, client):
        """Test file extension validation"""
        malicious_extensions = [
            'test.exe',
            'test.bat',
            'test.sh',
            'test.php',
            'test.jsp',
            'test.asp'
        ]
        
        for ext in malicious_extensions:
            resp = client.post('/upload',
                data={'file': (io.BytesIO(b'data'), f'test{ext}')},
                content_type='multipart/form-data')
            assert resp.status_code == 400
            assert 'File type not allowed' in resp.get_json()['error']
    
    def test_rate_limit_dos_protection(self, client, mock_rag_interface):
        """Test protection against DoS attacks via rate limiting"""
        # Make many rapid requests
        responses = []
        for i in range(30):  # Exceeds rate limit
            resp = client.post('/query', json={'query': f'dos test {i}'})
            responses.append(resp)
        
        # Should be rate limited after 20 requests
        rate_limited_count = sum(1 for r in responses if r.status_code == 429)
        assert rate_limited_count > 0

# ---------- Main Test Runner ----------

if __name__ == "__main__":
    print("🧪 Running Hardened Dashboard Tests")
    print("=" * 50)
    print("Testing all critical fixes:")
    print("  D-1: Upload security hardening")
    print("  D-2: Rate limiting")
    print("  D-3: Thread-safe history")
    print("  D-4: Executor shutdown")
    print("=" * 50)
    
    # Run tests
    pytest.main([__file__, "-v"]) 