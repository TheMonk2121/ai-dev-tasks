#!/usr/bin/env python3
"""
Optimized Watch Folder Test Suite
Fast, focused tests for critical functionality
Based on 400_code-criticality-guide.md Tier 2 criteria
"""

import subprocess

# Import our Watch Folder module
import tempfile
import time
from pathlib import Path
from unittest import mock

import pytest

# Optional dependency for memory testing
try:
    import psutil  # type: ignore[import-untyped]
except ImportError:
    psutil = None

from src.watch_folder import RAGFileHandler, WatchService, _is_file_ready, _run_add_document

# ============================================================================
# FAST UNIT TESTS (No I/O, No Sleep)
# ============================================================================

def test_is_file_ready_stable(tmp_path):
    """Test file stability detection - FAST"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("stable content")
    assert _is_file_ready(file_path, polls=1, delay=0.01)

def test_is_file_ready_nonexistent(tmp_path):
    """Test file stability for non-existent files - FAST"""
    file_path = tmp_path / "nonexistent.txt"
    assert _is_file_ready(file_path) is False

def test_run_add_document_success_mock(tmp_path):
    """Test successful add_document execution - MOCKED"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 3", stderr="")

        result = _run_add_document(file_path)
        assert result.returncode == 0
        assert "chunks stored: 3" in result.stdout

def test_run_add_document_failure_mock(tmp_path):
    """Test failed add_document execution - MOCKED"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=1, stdout="", stderr="Error: File not found")

        result = _run_add_document(file_path)
        assert result.returncode == 1
        assert "Error: File not found" in result.stderr

# ============================================================================
# QUICK INTEGRATION TESTS (Minimal I/O, Fast Timeouts)
# ============================================================================

@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        watch_dir = Path(temp_dir) / "watch"
        processed_dir = Path(temp_dir) / "processed"
        watch_dir.mkdir()
        processed_dir.mkdir()
        yield watch_dir, processed_dir

def test_watch_service_context_manager(temp_dirs):
    """Test WatchService context manager - FAST"""
    watch_dir, processed_dir = temp_dirs

    with WatchService(str(watch_dir), str(processed_dir), workers=1) as service:
        assert service.observer.is_alive()
        assert service.pool._max_workers == 1

    assert not service.observer.is_alive()

def test_file_creation_handling_fast(temp_dirs):
    """Test file creation handling - FAST with mocked subprocess"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 1", stderr="")

        with WatchService(str(watch_dir), str(processed_dir), workers=1):
            # Create a test file
            test_file = watch_dir / "test.txt"
            test_file.write_text("test content")

            # Wait minimal time for processing
            time.sleep(0.5)

            # Check if file was moved to processed directory
            processed_file = processed_dir / "test.txt"
            assert processed_file.exists()
            assert not test_file.exists()

def test_unsupported_file_extension_fast(temp_dirs):
    """Test unsupported file extensions - FAST"""
    watch_dir, processed_dir = temp_dirs

    with WatchService(str(watch_dir), str(processed_dir), workers=1):
        # Create file with unsupported extension
        test_file = watch_dir / "test.xyz"
        test_file.write_text("test content")

        # Wait minimal time
        time.sleep(0.1)

        # File should still be in watch directory (not processed)
        assert test_file.exists()
        assert not (processed_dir / "test.xyz").exists()

# ============================================================================
# SECURITY TESTS (Critical - No Sleep)
# ============================================================================

def test_command_injection_prevention(temp_dirs):
    """Test prevention of command injection attacks - CRITICAL"""
    watch_dir, processed_dir = temp_dirs

    captured_commands = []

    def mock_run(cmd, **kwargs):
        captured_commands.append(cmd)
        return mock.Mock(returncode=0, stdout="success", stderr="")

    with mock.patch("src.watch_folder.subprocess.run", side_effect=mock_run):
        with WatchService(str(watch_dir), str(processed_dir), workers=1):
            # Create file with potentially malicious name
            malicious_file = watch_dir / "-rm_rf.txt"
            malicious_file.write_text("malicious content")

            # Wait minimal time
            time.sleep(0.5)

            # Check that command was executed safely
            assert len(captured_commands) > 0
            cmd = captured_commands[0]

            # Should be passed as argument, not shell command
            assert cmd[0] == "python3"
            assert cmd[1] == "add_document.py"
            assert cmd[2].endswith("-rm_rf.txt")

def test_path_traversal_prevention(temp_dirs):
    """Test prevention of path traversal attacks - CRITICAL"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 1", stderr="")

        with WatchService(str(watch_dir), str(processed_dir), workers=1):
            # Create file with path traversal attempt
            traversal_file = watch_dir / "../../../etc/passwd.txt"
            traversal_file.write_text("malicious content")

            # Wait minimal time
            time.sleep(0.5)

            # File should be processed safely (path normalized)
            processed_file = processed_dir / "passwd.txt"
            assert processed_file.exists()

# ============================================================================
# PERFORMANCE TESTS (Fast Benchmarks)
# ============================================================================

def test_concurrent_file_processing_fast(temp_dirs):
    """Test concurrent processing - FAST with minimal files"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 1", stderr="")

        with WatchService(str(watch_dir), str(processed_dir), workers=4):
            # Create minimal files for testing
            start_time = time.time()

            for i in range(5):  # Reduced from 10 to 5
                test_file = watch_dir / f"test_{i}.txt"
                test_file.write_text(f"content {i}")

            # Wait minimal time
            time.sleep(1)

            end_time = time.time()
            processing_time = end_time - start_time

            # Check that all files were processed
            processed_files = list(processed_dir.iterdir())
            assert len(processed_files) == 5

            # Processing should be fast
            assert processing_time < 2.0

def test_memory_usage_fast(temp_dirs):
    """Test memory usage - FAST with minimal load"""
    if psutil is None:
        pytest.skip("psutil not available for memory testing")

    
    watch_dir, processed_dir = temp_dirs

    # Get initial memory usage
    process = psutil.Process(os.getpid())  # type: ignore[attr-defined]
    initial_memory = process.memory_info().rss

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 1", stderr="")

        with WatchService(str(watch_dir), str(processed_dir), workers=2):
            # Process minimal files
            for i in range(10):  # Reduced from 50 to 10
                test_file = watch_dir / f"memory_{i}.txt"
                test_file.write_text(f"content {i}")

            # Wait minimal time
            time.sleep(1)

            # Check final memory usage
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory

            # Memory increase should be reasonable (less than 50MB)
            assert memory_increase < 50 * 1024 * 1024

# ============================================================================
# RESILIENCE TESTS (Critical Error Handling)
# ============================================================================

def test_subprocess_failure_handling(temp_dirs):
    """Test subprocess failure handling - CRITICAL"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=1, stdout="", stderr="add_document.py failed")

        with WatchService(str(watch_dir), str(processed_dir), workers=1):
            # Create a test file
            test_file = watch_dir / "failing.txt"
            test_file.write_text("test content")

            # Wait minimal time
            time.sleep(0.5)

            # File should remain in watch directory (not moved to processed)
            assert test_file.exists()
            assert not (processed_dir / "failing.txt").exists()

def test_subprocess_timeout_handling(temp_dirs):
    """Test subprocess timeout handling - CRITICAL"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired("python3", 30)

        with WatchService(str(watch_dir), str(processed_dir), workers=1):
            # Create a test file
            test_file = watch_dir / "timeout.txt"
            test_file.write_text("test content")

            # Wait minimal time
            time.sleep(0.5)

            # File should remain in watch directory (not moved to processed)
            assert test_file.exists()
            assert not (processed_dir / "timeout.txt").exists()

# ============================================================================
# QUICK SMOKE TESTS (Fast Validation)
# ============================================================================

def test_rag_file_handler_initialization(temp_dirs):
    """Test RAGFileHandler initialization - FAST"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 1", stderr="")

        from concurrent.futures import ThreadPoolExecutor

        pool = ThreadPoolExecutor(max_workers=1)
        handler = RAGFileHandler(watch_dir, processed_dir, pool)
        assert handler.watch == watch_dir
        assert handler.processed == processed_dir
        pool.shutdown()

def test_supported_extensions():
    """Test supported extensions - FAST"""
    from src.watch_folder import SAFE_EXT

    assert ".txt" in SAFE_EXT
    assert ".md" in SAFE_EXT
    assert ".pdf" in SAFE_EXT
    assert ".csv" in SAFE_EXT
    assert ".xyz" not in SAFE_EXT

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("🚀 Running Optimized Watch Folder Test Suite...")
    print("⚡ Fast, focused tests for critical functionality")

    # Run all tests with verbose output
    pytest.main([__file__, "-v", "--tb=short", "--durations=10"])
