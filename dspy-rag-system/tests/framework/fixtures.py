"""
Shared Test Fixtures

Common fixtures used across the DSPy RAG System test suite.
Reduces duplication and provides consistent test environments.
"""

import os
from pathlib import Path
from unittest import mock

import pytest


@pytest.fixture(scope="session")
def postgres_dsn():
    """Stable default PostgreSQL DSN; override in CI/local via env"""
    return os.getenv("POSTGRES_DSN", "postgresql://ai_user:ai_password@localhost:5432/ai_agency")


@pytest.fixture(scope="session")
def sample_docs_dir(tmp_path_factory):
    """Session-scoped directory for sample documents; lazy-loaded to avoid I/O tax"""
    d = tmp_path_factory.mktemp("docs")
    # Populate only when needed in specific tests
    return Path(d)


@pytest.fixture(scope="function")
def fast_timeout(monkeypatch):
    """Function-scoped fixture to lower timeouts in tests that import settings"""
    monkeypatch.setenv("PROCESSING_TIMEOUT", "10")
    yield


@pytest.fixture(scope="function")
def mock_subprocess_run():
    """Mock subprocess.run for fast, reliable testing without external processes"""
    with mock.patch("subprocess.run") as mock_run:
        # Default successful response
        mock_run.return_value = mock.Mock(returncode=0, stdout="chunks stored: 3", stderr="")
        yield mock_run


@pytest.fixture(scope="function")
def mock_file_operations(tmp_path):
    """Mock file operations for fast testing without actual I/O"""
    with mock.patch("pathlib.Path.exists") as mock_exists:
        with mock.patch("pathlib.Path.read_text") as mock_read:
            with mock.patch("pathlib.Path.write_text") as mock_write:
                mock_exists.return_value = True
                mock_read.return_value = "test content"
                mock_write.return_value = None

                yield {"exists": mock_exists, "read_text": mock_read, "write_text": mock_write}


@pytest.fixture(scope="function")
def mock_database_connection():
    """Mock database connection for tests that don't need real DB"""
    with mock.patch("psycopg2.connect") as mock_connect:
        mock_conn = mock.Mock()
        mock_cursor = mock.Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        yield {"connect": mock_connect, "connection": mock_conn, "cursor": mock_cursor}


@pytest.fixture(scope="function")
def sample_test_document(tmp_path):
    """Create a sample test document for document processing tests"""
    doc_path = tmp_path / "sample_document.txt"
    doc_content = """
    This is a sample document for testing.

    It contains multiple paragraphs and various content types.

    # Heading 1
    ## Heading 2

    - List item 1
    - List item 2

    **Bold text** and *italic text* for testing.
    """
    doc_path.write_text(doc_content)
    return doc_path


@pytest.fixture(scope="function")
def mock_logger():
    """Mock logger for tests that need logging verification"""
    with mock.patch("src.utils.logger.setup_logger") as mock_setup_logger:
        mock_logger_instance = mock.Mock()
        mock_setup_logger.return_value = mock_logger_instance
        yield mock_logger_instance
