#!/usr/bin/env python3
"""
Comprehensive test suite for Watch Folder module
Based on deep research analysis with all critical fixes
"""

import time
import tempfile
import shutil
import signal
import threading
from pathlib import Path
from unittest import mock
import pytest

# Mark all tests in this file as deprecated
pytestmark = pytest.mark.deprecated
import subprocess

# Import our Watch Folder module
from src.watch_folder import WatchService, _is_file_ready, _run_add_document, RAGFileHandler

# Test configuration
TEST_TIMEOUT = 10  # seconds for integration tests

# ============================================================================
# TEST HELPERS
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


@pytest.fixture
def mock_subprocess():
    """Mock subprocess for testing"""
    with mock.patch("src.watch_folder.subprocess") as mock_sub:
        mock_sub.run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 5", stderr="")
        yield mock_sub


# ============================================================================
# UNIT TESTS
# ============================================================================


def test_is_file_ready_stable(tmp_path):
    """Test file stability detection for stable files"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("stable content")

    assert _is_file_ready(file_path, polls=1, delay=0.1)


def test_is_file_ready_unstable(tmp_path):
    """Test file stability detection for unstable files"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("initial")

    # Simulate another process still writing
    def append_content():
        time.sleep(0.2)
        file_path.write_text("initial + more content")

    threading.Thread(target=append_content).start()

    # Should detect file is not stable
    assert _is_file_ready(file_path, polls=3, delay=0.2) is False


def test_is_file_ready_nonexistent(tmp_path):
    """Test file stability detection for non-existent files"""
    file_path = tmp_path / "nonexistent.txt"

    assert _is_file_ready(file_path) is False


def test_run_add_document_success(tmp_path):
    """Test successful add_document execution"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 3", stderr="")

        result = _run_add_document(file_path)

        assert result.returncode == 0
        assert "chunks stored: 3" in result.stdout
        mock_run.assert_called_once()


def test_run_add_document_failure(tmp_path):
    """Test failed add_document execution"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=1, stdout="", stderr="Error: File not found")

        result = _run_add_document(file_path)

        assert result.returncode == 1
        assert "Error: File not found" in result.stderr


def test_run_add_document_timeout(tmp_path):
    """Test add_document timeout handling"""
    file_path = tmp_path / "test.txt"
    file_path.write_text("test content")

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired("python3", 30)

        with pytest.raises(subprocess.TimeoutExpired):
            _run_add_document(file_path, timeout=1)


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


def test_watch_service_context_manager(temp_dirs):
    """Test WatchService context manager functionality"""
    watch_dir, processed_dir = temp_dirs

    with WatchService(str(watch_dir), str(processed_dir), workers=1) as service:
        assert service.observer.is_alive()
        assert service.pool._max_workers == 1

    # Should be shut down after context exit
    assert not service.observer.is_alive()


def test_file_creation_handling(temp_dirs, mock_subprocess):
    """Test handling of file creation events"""
    watch_dir, processed_dir = temp_dirs

    with WatchService(str(watch_dir), str(processed_dir), workers=1) as service:
        # Create a test file
        test_file = watch_dir / "test.txt"
        test_file.write_text("test content")

        # Wait for processing
        time.sleep(2)

        # Check if file was moved to processed directory
        processed_file = processed_dir / "test.txt"
        assert processed_file.exists()
        assert not test_file.exists()


def test_file_move_handling(temp_dirs, mock_subprocess):
    """Test handling of file move events"""
    watch_dir, processed_dir = temp_dirs

    # Create file outside watch directory
    temp_file = Path(tempfile.mktemp(suffix=".txt"))
    temp_file.write_text("test content")

    try:
        with WatchService(str(watch_dir), str(processed_dir), workers=1) as service:
            # Move file into watch directory
            shutil.move(str(temp_file), str(watch_dir / "moved.txt"))

            # Wait for processing
            time.sleep(2)

            # Check if file was moved to processed directory
            processed_file = processed_dir / "moved.txt"
            assert processed_file.exists()
            assert not (watch_dir / "moved.txt").exists()
    finally:
        # Cleanup
        if temp_file.exists():
            temp_file.unlink()


def test_unsupported_file_extension(temp_dirs):
    """Test that unsupported file extensions are ignored"""
    watch_dir, processed_dir = temp_dirs

    with WatchService(str(watch_dir), str(processed_dir), workers=1) as service:
        # Create file with unsupported extension
        test_file = watch_dir / "test.xyz"
        test_file.write_text("test content")

        # Wait a bit
        time.sleep(1)

        # File should still be in watch directory (not processed)
        assert test_file.exists()
        assert not (processed_dir / "test.xyz").exists()


# ============================================================================
# SECURITY TESTS
# ============================================================================


def test_command_injection_prevention(temp_dirs):
    """Test prevention of command injection attacks"""
    watch_dir, processed_dir = temp_dirs

    captured_commands = []

    def mock_run(cmd, **kwargs):
        captured_commands.append(cmd)
        return mock.Mock(returncode=0, stdout="success", stderr="")

    with mock.patch("src.watch_folder.subprocess.run", side_effect=mock_run):
        with WatchService(str(watch_dir), str(processed_dir), workers=1) as service:
            # Create file with potentially malicious name
            malicious_file = watch_dir / "-rm_rf.txt"
            malicious_file.write_text("malicious content")

            # Wait for processing
            time.sleep(2)

            # Check that command was executed safely
            assert len(captured_commands) > 0
            cmd = captured_commands[0]

            # Should be passed as argument, not shell command
            assert cmd[0] == "python3"
            assert cmd[1] == "add_document.py"
            assert cmd[2].endswith("-rm_rf.txt")  # Path passed as argument


def test_path_traversal_prevention(temp_dirs):
    """Test prevention of path traversal attacks"""
    watch_dir, processed_dir = temp_dirs

    with WatchService(str(watch_dir), str(processed_dir), workers=1) as service:
        # Create file with path traversal attempt
        traversal_file = watch_dir / "../../../etc/passwd.txt"
        traversal_file.write_text("malicious content")

        # Wait for processing
        time.sleep(1)

        # File should be processed safely (path normalized)
        processed_file = processed_dir / "passwd.txt"
        assert processed_file.exists()


def test_file_permission_handling(temp_dirs):
    """Test handling of file permission issues"""
    watch_dir, processed_dir = temp_dirs

    with WatchService(str(watch_dir), str(processed_dir), workers=1) as service:
        # Create file with restricted permissions
        test_file = watch_dir / "restricted.txt"
        test_file.write_text("test content")
        test_file.chmod(0o000)  # No permissions

        try:
            # Wait for processing
            time.sleep(1)

            # Should handle permission errors gracefully
            # (exact behavior depends on implementation)
        finally:
            # Restore permissions for cleanup
            test_file.chmod(0o644)


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


def test_concurrent_file_processing(temp_dirs):
    """Test concurrent processing of multiple files"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 1", stderr="")

        with WatchService(str(watch_dir), str(processed_dir), workers=4) as service:
            # Create multiple files simultaneously
            start_time = time.time()

            for i in range(10):
                test_file = watch_dir / f"test_{i}.txt"
                test_file.write_text(f"content {i}")

            # Wait for processing
            time.sleep(3)

            end_time = time.time()
            processing_time = end_time - start_time

            # Check that all files were processed
            processed_files = list(processed_dir.iterdir())
            assert len(processed_files) == 10

            # Processing should be reasonably fast with concurrent workers
            assert processing_time < 5.0


def test_large_file_handling(temp_dirs):
    """Test handling of large files"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 100", stderr="")

        with WatchService(str(watch_dir), str(processed_dir), workers=1) as service:
            # Create a large file
            large_file = watch_dir / "large.txt"
            large_content = "x" * (1024 * 1024)  # 1MB
            large_file.write_text(large_content)

            # Wait for processing
            time.sleep(2)

            # Check that file was processed
            processed_file = processed_dir / "large.txt"
            assert processed_file.exists()


def test_memory_usage_under_load(temp_dirs):
    """Test memory usage under high load"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 1", stderr="")

        with WatchService(str(watch_dir), str(processed_dir), workers=2) as service:
            # Create many files rapidly
            for i in range(50):
                test_file = watch_dir / f"rapid_{i}.txt"
                test_file.write_text(f"content {i}")
                time.sleep(0.01)  # Small delay

            # Wait for processing
            time.sleep(5)

            # Check that all files were processed
            processed_files = list(processed_dir.iterdir())
            assert len(processed_files) == 50


# ============================================================================
# RESILIENCE TESTS
# ============================================================================


def test_subprocess_failure_handling(temp_dirs):
    """Test handling of subprocess failures"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=1, stdout="", stderr="add_document.py failed")

        with WatchService(str(watch_dir), str(processed_dir), workers=1) as service:
            # Create a test file
            test_file = watch_dir / "failing.txt"
            test_file.write_text("test content")

            # Wait for processing
            time.sleep(2)

            # File should remain in watch directory (not moved to processed)
            assert test_file.exists()
            assert not (processed_dir / "failing.txt").exists()


def test_subprocess_timeout_handling(temp_dirs):
    """Test handling of subprocess timeouts"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired("python3", 30)

        with WatchService(str(watch_dir), str(processed_dir), workers=1) as service:
            # Create a test file
            test_file = watch_dir / "timeout.txt"
            test_file.write_text("test content")

            # Wait for processing
            time.sleep(2)

            # File should remain in watch directory (not moved to processed)
            assert test_file.exists()
            assert not (processed_dir / "timeout.txt").exists()


def test_notification_system_failure(temp_dirs):
    """Test handling of notification system failures"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 5", stderr="")

        # Mock notification system to raise exception
        with mock.patch("src.watch_folder.NotificationSystem") as mock_notif:
            mock_notif.side_effect = Exception("Notification system failed")

            with WatchService(str(watch_dir), str(processed_dir), workers=1) as service:
                # Create a test file
                test_file = watch_dir / "notify_fail.txt"
                test_file.write_text("test content")

                # Wait for processing
                time.sleep(2)

                # File should still be processed and moved despite notification failure
                processed_file = processed_dir / "notify_fail.txt"
                assert processed_file.exists()
                assert not test_file.exists()


def test_graceful_shutdown(temp_dirs):
    """Test graceful shutdown behavior"""
    watch_dir, processed_dir = temp_dirs

    with WatchService(str(watch_dir), str(processed_dir), workers=2) as service:
        # Start processing some files
        for i in range(5):
            test_file = watch_dir / f"shutdown_{i}.txt"
            test_file.write_text(f"content {i}")

        # Shutdown should complete without hanging
        # (context manager handles shutdown)


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


def test_empty_file_handling(temp_dirs):
    """Test handling of empty files"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 0", stderr="")

        with WatchService(str(watch_dir), str(processed_dir), workers=1) as service:
            # Create empty file
            empty_file = watch_dir / "empty.txt"
            empty_file.write_text("")

            # Wait for processing
            time.sleep(2)

            # File should be processed
            processed_file = processed_dir / "empty.txt"
            assert processed_file.exists()


def test_special_characters_in_filename(temp_dirs):
    """Test handling of special characters in filenames"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 1", stderr="")

        with WatchService(str(watch_dir), str(processed_dir), workers=1) as service:
            # Create file with special characters
            special_file = watch_dir / "file with spaces & symbols!.txt"
            special_file.write_text("special content")

            # Wait for processing
            time.sleep(2)

            # File should be processed
            processed_file = processed_dir / "file with spaces & symbols!.txt"
            assert processed_file.exists()


def test_unicode_filename_handling(temp_dirs):
    """Test handling of Unicode filenames"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 1", stderr="")

        with WatchService(str(watch_dir), str(processed_dir), workers=1) as service:
            # Create file with Unicode name
            unicode_file = watch_dir / "文件.txt"
            unicode_file.write_text("unicode content")

            # Wait for processing
            time.sleep(2)

            # File should be processed
            processed_file = processed_dir / "文件.txt"
            assert processed_file.exists()


def test_concurrent_file_access(temp_dirs):
    """Test handling of concurrent file access"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 1", stderr="")

        with WatchService(str(watch_dir), str(processed_dir), workers=4) as service:
            # Create files from multiple threads
            def create_file(i):
                test_file = watch_dir / f"concurrent_{i}.txt"
                test_file.write_text(f"content {i}")

            threads = []
            for i in range(10):
                thread = threading.Thread(target=create_file, args=(i,))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Wait for processing
            time.sleep(3)

            # Check that all files were processed
            processed_files = list(processed_dir.iterdir())
            assert len(processed_files) == 10


# ============================================================================
# BENCHMARK TESTS
# ============================================================================


def test_processing_speed_benchmark(temp_dirs):
    """Benchmark file processing speed"""
    watch_dir, processed_dir = temp_dirs

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 1", stderr="")

        with WatchService(str(watch_dir), str(processed_dir), workers=4) as service:
            # Create files and measure processing time
            start_time = time.time()

            for i in range(20):
                test_file = watch_dir / f"benchmark_{i}.txt"
                test_file.write_text(f"content {i}")

            # Wait for processing
            time.sleep(5)

            end_time = time.time()
            total_time = end_time - start_time

            # Check that all files were processed
            processed_files = list(processed_dir.iterdir())
            assert len(processed_files) == 20

            # Processing should be reasonably fast
            assert total_time < 10.0


def test_memory_usage_benchmark(temp_dirs):
    """Benchmark memory usage during processing"""
    import psutil

    watch_dir, processed_dir = temp_dirs

    # Get initial memory usage
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    with mock.patch("src.watch_folder.subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 1", stderr="")

        with WatchService(str(watch_dir), str(processed_dir), workers=4) as service:
            # Process many files
            for i in range(100):
                test_file = watch_dir / f"memory_{i}.txt"
                test_file.write_text(f"content {i}")

            # Wait for processing
            time.sleep(10)

            # Check final memory usage
            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory

            # Memory increase should be reasonable (less than 100MB)
            assert memory_increase < 100 * 1024 * 1024


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

if __name__ == "__main__":
    print("🚀 Running Watch Folder comprehensive test suite...")

    # Run all tests
    pytest.main([__file__, "-v", "--tb=short"])
