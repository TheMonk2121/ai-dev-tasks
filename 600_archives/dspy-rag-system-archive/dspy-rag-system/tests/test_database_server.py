#!/usr/bin/env python3
import sqlite3
import sys
import tempfile
from unittest.mock import AsyncMock, Mock

import pytest

sys.path.append("src")

from utils.mcp_integration.database_server import (
    DatabaseMCPServer,
    DatabaseSchema,
    DatabaseServerConfig,
    DatabaseTable,
    MCPConfig,
    MCPError,
    QueryResult,
)


class TestDatabaseServerConfig:
    def test_default_config(self):
        config = DatabaseServerConfig()
        assert config.connection_timeout == 30
        assert config.query_timeout == 60
        assert config.max_rows == 1000
        assert config.include_schema is True
        assert config.include_sample_data is True
        assert config.sample_size == 10
        assert config.export_format == "json"
        assert config.enable_sql_injection_protection is True

    def test_custom_config(self):
        config = DatabaseServerConfig(connection_timeout=60, max_rows=500, sample_size=5, export_format="csv")
        assert config.connection_timeout == 60
        assert config.max_rows == 500
        assert config.sample_size == 5
        assert config.export_format == "csv"


class TestDatabaseTable:
    def test_table_creation(self):
        table = DatabaseTable(name="test_table")
        assert table.name == "test_table"
        assert table.columns == []
        assert table.row_count is None

    def test_table_with_columns(self):
        columns = [
            {"name": "id", "type": "INTEGER", "primary_key": True},
            {"name": "name", "type": "TEXT", "not_null": True},
        ]
        table = DatabaseTable(name="test_table", columns=columns)
        assert table.name == "test_table"
        assert len(table.columns) == 2
        assert table.columns[0]["name"] == "id"


class TestDatabaseSchema:
    def test_schema_creation(self):
        schema = DatabaseSchema(database_name="test_db")
        assert schema.database_name == "test_db"
        assert schema.tables == []
        assert schema.views == []
        assert schema.indexes == []
        assert schema.foreign_keys == []

    def test_schema_with_tables(self):
        table1 = DatabaseTable(name="table1")
        table2 = DatabaseTable(name="table2")
        schema = DatabaseSchema(database_name="test_db", tables=[table1, table2])
        assert len(schema.tables) == 2
        assert schema.tables[0].name == "table1"
        assert schema.tables[1].name == "table2"


class TestQueryResult:
    def test_query_result_creation(self):
        result = QueryResult(
            columns=["id", "name"],
            rows=[[1, "test"], [2, "test2"]],
            row_count=2,
            execution_time_ms=10.5,
            query="SELECT * FROM test",
        )
        assert result.columns == ["id", "name"]
        assert result.rows == [[1, "test"], [2, "test2"]]
        assert result.row_count == 2
        assert result.execution_time_ms == 10.5
        assert result.query == "SELECT * FROM test"


class TestDatabaseMCPServer:
    @pytest.fixture
    def server(self):
        config = MCPConfig(server_name="test_database_server")
        return DatabaseMCPServer(config)

    @pytest.fixture
    def temp_db(self):
        """Create a temporary SQLite database for testing."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        # Create test database with sample data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create test table
        cursor.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Insert sample data
        cursor.execute(
            """
            INSERT INTO users (name, email) VALUES
            ('John Doe', 'john@example.com'),
            ('Jane Smith', 'jane@example.com'),
            ('Bob Johnson', 'bob@example.com')
        """
        )

        conn.commit()
        conn.close()

        yield db_path

        # Cleanup
        import os

        os.unlink(db_path)

    def test_server_initialization(self, server):
        assert server.config.server_name == "test_database_server"
        assert isinstance(server.db_config, DatabaseServerConfig)
        assert len(server.supported_types) == 5
        assert "database/sqlite" in server.supported_types
        assert "database/postgresql" in server.supported_types

    def test_validate_source_sqlite_file(self, server):
        assert server.validate_source("test.db") is True
        assert server.validate_source("database.sqlite") is True
        assert server.validate_source("data.sqlite3") is True
        assert server.validate_source("file:///path/to/database.db") is True

    def test_validate_source_postgresql(self, server):
        assert server.validate_source("postgresql://localhost/db") is True
        assert server.validate_source("postgres://user:pass@localhost/db") is True

    def test_validate_source_invalid(self, server):
        assert server.validate_source("invalid://url") is False
        assert server.validate_source("not_a_database.txt") is False
        assert server.validate_source("") is False

    def test_get_database_type(self, server):
        assert server._get_database_type("test.db") == "sqlite"
        assert server._get_database_type("database.sqlite") == "sqlite"
        assert server._get_database_type("postgresql://localhost/db") == "postgresql"
        assert server._get_database_type("unknown://url") == "unknown"

    def test_sanitize_sql_safe(self, server):
        safe_query = "SELECT * FROM users WHERE name = 'test'"
        assert server._sanitize_sql(safe_query) == safe_query

    def test_sanitize_sql_dangerous(self, server):
        dangerous_queries = [
            "DROP TABLE users",
            "DELETE FROM users",
            "INSERT INTO users VALUES (1, 'test')",
            "UPDATE users SET name = 'test'",
            "SELECT * FROM users -- comment",
            "SELECT * FROM users /* comment */",
        ]

        for query in dangerous_queries:
            with pytest.raises(MCPError, match="Potentially dangerous SQL keyword"):
                server._sanitize_sql(query)

    def test_sanitize_sql_disabled(self, server):
        server.db_config.enable_sql_injection_protection = False
        dangerous_query = "DROP TABLE users"
        assert server._sanitize_sql(dangerous_query) == dangerous_query

    def test_connect_sqlite_success(self, server, temp_db):
        conn = server._connect_sqlite(temp_db)
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_connect_sqlite_file_prefix(self, server, temp_db):
        conn = server._connect_sqlite(f"file://{temp_db}")
        assert isinstance(conn, sqlite3.Connection)
        conn.close()

    def test_connect_sqlite_failure(self, server):
        with pytest.raises(MCPError, match="Failed to connect to SQLite database"):
            server._connect_sqlite("/nonexistent/path/to/database.db")

    def test_get_sqlite_schema(self, server, temp_db):
        conn = server._connect_sqlite(temp_db)
        try:
            schema = server._get_sqlite_schema(conn)
            assert isinstance(schema, DatabaseSchema)
            assert schema.database_name == "sqlite_database"
            assert len(schema.tables) == 1
            assert schema.tables[0].name == "users"
            assert len(schema.tables[0].columns) == 4
            assert schema.tables[0].row_count == 3
        finally:
            conn.close()

    def test_execute_sqlite_query(self, server, temp_db):
        conn = server._connect_sqlite(temp_db)
        try:
            result = server._execute_sqlite_query(conn, "SELECT * FROM users")
            assert isinstance(result, QueryResult)
            assert result.columns == ["id", "name", "email", "created_at"]
            assert result.row_count == 3
            assert result.query == "SELECT * FROM users"
            assert result.execution_time_ms > 0
        finally:
            conn.close()

    def test_execute_sqlite_query_with_limit(self, server, temp_db):
        conn = server._connect_sqlite(temp_db)
        try:
            server.db_config.max_rows = 2
            result = server._execute_sqlite_query(conn, "SELECT * FROM users")
            assert result.row_count == 2
        finally:
            conn.close()

    def test_execute_sqlite_query_error(self, server, temp_db):
        conn = server._connect_sqlite(temp_db)
        try:
            with pytest.raises(MCPError, match="Query execution failed"):
                server._execute_sqlite_query(conn, "SELECT * FROM nonexistent_table")
        finally:
            conn.close()

    def test_get_sample_data_sqlite(self, server, temp_db):
        conn = server._connect_sqlite(temp_db)
        try:
            sample_data = server._get_sample_data_sqlite(conn, "users")
            assert isinstance(sample_data, list)
            assert len(sample_data) == 3
            assert all(isinstance(row, dict) for row in sample_data)
            assert "id" in sample_data[0]
            assert "name" in sample_data[0]
            assert "email" in sample_data[0]
        finally:
            conn.close()

    def test_get_sample_data_sqlite_with_limit(self, server, temp_db):
        conn = server._connect_sqlite(temp_db)
        try:
            server.db_config.sample_size = 2
            sample_data = server._get_sample_data_sqlite(conn, "users")
            assert len(sample_data) == 2
        finally:
            conn.close()

    def test_get_sample_data_sqlite_error(self, server, temp_db):
        conn = server._connect_sqlite(temp_db)
        try:
            sample_data = server._get_sample_data_sqlite(conn, "nonexistent_table")
            assert sample_data == []
        finally:
            conn.close()

    @pytest.mark.asyncio
    async def test_process_sqlite(self, server, temp_db):
        result = await server.process_document(temp_db)
        assert result.metadata.content_type == "database/sqlite"
        assert result.metadata.title.startswith("SQLite Database:")
        assert "Database Schema:" in result.content
        assert "Sample Data:" in result.content
        assert result.success is True

    @pytest.mark.asyncio
    async def test_process_sqlite_schema_only(self, server, temp_db):
        server.db_config.include_sample_data = False
        result = await server.process_document(temp_db)
        assert "Database Schema:" in result.content
        assert "Sample Data:" not in result.content
        assert result.success is True

    @pytest.mark.asyncio
    async def test_process_sqlite_sample_only(self, server, temp_db):
        server.db_config.include_schema = False
        result = await server.process_document(temp_db)
        assert "Database Schema:" not in result.content
        assert "Sample Data:" in result.content
        assert result.success is True

    @pytest.mark.asyncio
    async def test_process_postgresql(self, server):
        result = await server.process_document("postgresql://localhost/test")
        assert result.metadata.content_type == "database/postgresql"
        assert result.metadata.title.startswith("PostgreSQL Database:")
        assert "not yet implemented" in result.content
        assert result.success is True

    @pytest.mark.asyncio
    async def test_process_unsupported_database(self, server):
        with pytest.raises(MCPError, match="Unsupported database type"):
            await server.process_document("unknown://database")

    @pytest.mark.asyncio
    async def test_execute_query_sqlite(self, server, temp_db):
        result = await server.execute_query(temp_db, "SELECT name FROM users WHERE id = 1")
        assert isinstance(result, QueryResult)
        assert result.columns == ["name"]
        assert result.row_count == 1
        assert result.rows[0][0] == "John Doe"

    @pytest.mark.asyncio
    async def test_execute_query_unsupported_database(self, server):
        with pytest.raises(MCPError, match="Query execution not supported"):
            await server.execute_query("postgresql://localhost/test", "SELECT 1")

    @pytest.mark.asyncio
    async def test_execute_query_dangerous(self, server, temp_db):
        with pytest.raises(MCPError, match="Potentially dangerous SQL keyword"):
            await server.execute_query(temp_db, "DROP TABLE users")

    @pytest.mark.asyncio
    async def test_export_data_json(self, server, temp_db):
        result = await server.export_data(temp_db, "users", "json")
        assert isinstance(result, str)
        import json

        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 3
        assert "id" in data[0]
        assert "name" in data[0]

    @pytest.mark.asyncio
    async def test_export_data_csv(self, server, temp_db):
        result = await server.export_data(temp_db, "users", "csv")
        assert isinstance(result, str)
        lines = result.strip().split("\n")
        assert len(lines) == 4  # header + 3 data rows
        assert "id,name,email,created_at" in lines[0]

    @pytest.mark.asyncio
    async def test_export_data_unsupported_format(self, server, temp_db):
        with pytest.raises(MCPError, match="Unsupported export format"):
            await server.export_data(temp_db, "users", "xml")

    @pytest.mark.asyncio
    async def test_export_data_unsupported_database(self, server):
        with pytest.raises(MCPError, match="Export not supported"):
            await server.export_data("postgresql://localhost/test", "users", "json")

    def test_get_server_info(self, server):
        info = server.get_server_info()
        assert info["name"] == "test_database_server"
        assert info["version"] == "1.0.0"
        assert "database/sqlite" in info["supported_types"]
        assert "database/postgresql" in info["supported_types"]
        assert "sqlite" in info["database_types"]
        assert "postgresql" in info["database_types"]
        assert "schema_extraction" in info["features"]
        assert "query_execution" in info["features"]
        assert "data_export" in info["features"]
        assert "sql_injection_protection" in info["features"]

    @pytest.mark.asyncio
    async def test_cleanup(self, server):
        # Add some mock connections
        server._connections["test"] = Mock()
        mock_session = Mock()
        mock_session.aclose = AsyncMock()
        server._session = mock_session

        await server.cleanup()

        assert len(server._connections) == 0
        assert server._session is None
