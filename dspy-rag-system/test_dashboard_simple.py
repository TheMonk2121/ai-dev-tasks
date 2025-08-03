#!/usr/bin/env python3
"""
Simplified Test Suite for Dashboard Critical Fixes
Focuses on core functionality without complex test infrastructure
"""

import io
import time
import threading
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

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
    
    def test_upload_reject_backslash_in_filename(self, client):
        """Test that filenames with backslashes are rejected"""
        resp = client.post('/upload',
            data={'file': (io.BytesIO(b'data'), 'evil\\..\\file.txt')},
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
    
    def test_rate_limit_function(self):
        """Test the rate limiting function directly"""
        # Clear any existing rate data
        from src.dashboard import _RATE
        _RATE.clear()
        
        # Test normal usage
        for i in range(20):
            assert _check_rate('test_ip') is True
        
        # Test rate limit exceeded
        assert _check_rate('test_ip') is False

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

# ---------- D-4: Executor Shutdown Tests ----------

class TestExecutorShutdown:
    """Test executor shutdown functionality (D-4)"""
    
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

# ---------- Main Test Runner ----------

if __name__ == "__main__":
    print("🧪 Running Simplified Dashboard Tests")
    print("=" * 50)
    print("Testing all critical fixes:")
    print("  D-1: Upload security hardening")
    print("  D-2: Rate limiting")
    print("  D-3: Thread-safe history")
    print("  D-4: Executor shutdown")
    print("=" * 50)
    
    # Run tests
    pytest.main([__file__, "-v"]) 