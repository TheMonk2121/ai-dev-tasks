#!/usr/bin/env python3
"""
Database MCP Server Implementation

Provides MCP server for database content processing, supporting
PostgreSQL and SQLite databases with schema extraction, query execution,
and data export capabilities.
"""

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel, Field

from .base_server import DocumentMetadata, MCPConfig, MCPError, MCPServer, ProcessedDocument


class DatabaseServerConfig(BaseModel):
    """Configuration specific to Database MCP server."""

    connection_timeout: int = Field(default=30, description="Database connection timeout in seconds")
    query_timeout: int = Field(default=60, description="Query execution timeout in seconds")
    max_rows: int = Field(default=1000, description="Maximum rows to return from queries")
    include_schema: bool = Field(default=True, description="Include database schema in processing")
    include_sample_data: bool = Field(default=True, description="Include sample data in processing")
    sample_size: int = Field(default=10, description="Number of sample rows to include")
    export_format: str = Field(default="json", description="Export format (json, csv, sql)")
    enable_sql_injection_protection: bool = Field(default=True, description="Enable SQL injection protection")

    model_config = {"extra": "forbid"}


class DatabaseTable(BaseModel):
    """Database table information."""

    name: str
    table_schema: Optional[str] = Field(default=None, description="Database schema name")
    columns: List[Dict[str, Any]] = Field(default_factory=list)
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"extra": "forbid"}


class DatabaseSchema(BaseModel):
    """Database schema information."""

    database_name: str
    tables: List[DatabaseTable] = Field(default_factory=list)
    views: List[Dict[str, Any]] = Field(default_factory=list)
    indexes: List[Dict[str, Any]] = Field(default_factory=list)
    foreign_keys: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = {"extra": "forbid"}


class QueryResult(BaseModel):
    """Database query result."""

    columns: List[str] = Field(default_factory=list)
    rows: List[List[Any]] = Field(default_factory=list)
    row_count: int = 0
    execution_time_ms: float = 0.0
    query: str = ""

    model_config = {"extra": "forbid"}


class DatabaseMCPServer(MCPServer):
    """MCP server for database content processing."""

    def __init__(self, config: MCPConfig):
        super().__init__(config)
        self.db_config = DatabaseServerConfig()
        self._connections: Dict[str, Any] = {}
        self._session: Optional[httpx.AsyncClient] = None

        # Supported content types
        self.supported_types = {
            "database/sqlite": "SQLite database files",
            "database/postgresql": "PostgreSQL database connections",
            "database/schema": "Database schema information",
            "database/query": "SQL query results",
            "database/export": "Database export data",
        }

    def supports_content_type(self, content_type: str) -> bool:
        """Check if this server supports the given content type."""
        return content_type in self.supported_types

    def get_supported_types(self) -> List[str]:
        """Get list of supported content types."""
        return list(self.supported_types.keys())

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()

    def validate_source(self, source: str) -> bool:
        """Validate if the source is a supported database connection."""
        try:
            parsed = urlparse(source)

            # SQLite file paths
            if source.endswith(".db") or source.endswith(".sqlite") or source.endswith(".sqlite3"):
                return True

            # PostgreSQL connections
            if parsed.scheme in ["postgresql", "postgres"]:
                return True

            # Direct file paths for SQLite
            if parsed.scheme == "file" and (source.endswith(".db") or source.endswith(".sqlite")):
                return True

            return False
        except Exception:
            return False

    def _get_database_type(self, source: str) -> str:
        """Determine database type from source."""
        if source.endswith((".db", ".sqlite", ".sqlite3")):
            return "sqlite"
        elif source.startswith(("postgresql://", "postgres://")):
            return "postgresql"
        else:
            return "unknown"

    def _sanitize_sql(self, sql: str) -> str:
        """Basic SQL injection protection."""
        if not self.db_config.enable_sql_injection_protection:
            return sql

        # Remove dangerous keywords
        dangerous_keywords = [
            "DROP",
            "DELETE",
            "TRUNCATE",
            "ALTER",
            "CREATE",
            "INSERT",
            "UPDATE",
            "GRANT",
            "REVOKE",
            "EXEC",
            "EXECUTE",
            "--",
            "/*",
            "*/",
        ]

        sql_upper = sql.upper()
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                raise MCPError(f"Potentially dangerous SQL keyword detected: {keyword}")

        return sql

    def _connect_sqlite(self, source: str) -> sqlite3.Connection:
        """Connect to SQLite database."""
        try:
            # Remove file:// prefix if present
            if source.startswith("file://"):
                source = source[7:]

            conn = sqlite3.connect(source, timeout=self.db_config.connection_timeout)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            return conn
        except Exception as e:
            raise MCPError(f"Failed to connect to SQLite database: {e}")

    def _get_sqlite_schema(self, conn: sqlite3.Connection) -> DatabaseSchema:
        """Extract schema from SQLite database."""
        schema = DatabaseSchema(database_name="sqlite_database")

        # Get tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        for table_row in tables:
            table_name = table_row[0]
            table = DatabaseTable(name=table_name)

            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = cursor.fetchall()

            for col_info in columns_info:
                column = {
                    "name": col_info[1],
                    "type": col_info[2],
                    "not_null": bool(col_info[3]),
                    "default_value": col_info[4],
                    "primary_key": bool(col_info[5]),
                }
                table.columns.append(column)

            # Get row count
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                table.row_count = cursor.fetchone()[0]
            except Exception:
                table.row_count = 0

            schema.tables.append(table)

        return schema

    def _execute_sqlite_query(self, conn: sqlite3.Connection, query: str) -> QueryResult:
        """Execute query on SQLite database."""
        import time

        start_time = time.time()

        try:
            cursor = conn.cursor()
            cursor.execute(query)

            # Get column names
            columns = [description[0] for description in cursor.description] if cursor.description else []

            # Get rows (limited by max_rows)
            rows = cursor.fetchmany(self.db_config.max_rows)

            execution_time = (time.time() - start_time) * 1000

            return QueryResult(
                columns=columns,
                rows=[list(row) for row in rows],
                row_count=len(rows),
                execution_time_ms=execution_time,
                query=query,
            )
        except Exception as e:
            raise MCPError(f"Query execution failed: {e}")

    def _get_sample_data_sqlite(self, conn: sqlite3.Connection, table_name: str) -> List[Dict[str, Any]]:
        """Get sample data from SQLite table."""
        try:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {self.db_config.sample_size}")
            rows = cursor.fetchall()

            # Get column names
            columns = [description[0] for description in cursor.description] if cursor.description else []

            # Convert to list of dicts
            sample_data = []
            for row in rows:
                sample_data.append(dict(zip(columns, row)))

            return sample_data
        except Exception:
            return []

    async def process_document(self, source: str) -> ProcessedDocument:
        """Process database content."""
        try:
            db_type = self._get_database_type(source)

            if db_type == "sqlite":
                return await self._process_sqlite(source)
            elif db_type == "postgresql":
                return await self._process_postgresql(source)
            else:
                raise MCPError(f"Unsupported database type: {db_type}")

        except Exception as e:
            raise MCPError(f"Database processing failed: {e}")

    async def _process_sqlite(self, source: str) -> ProcessedDocument:
        """Process SQLite database."""
        conn = None
        try:
            conn = self._connect_sqlite(source)

            # Extract schema
            schema = self._get_sqlite_schema(conn)

            # Prepare content
            content_parts = []

            if self.db_config.include_schema:
                schema_content = f"Database Schema:\n{json.dumps(schema.model_dump(), indent=2)}"
                content_parts.append(schema_content)

            if self.db_config.include_sample_data:
                sample_data = {}
                for table in schema.tables:
                    sample_data[table.name] = self._get_sample_data_sqlite(conn, table.name)

                if sample_data:
                    sample_content = f"Sample Data:\n{json.dumps(sample_data, indent=2)}"
                    content_parts.append(sample_content)

            content = "\n\n".join(content_parts)

            # Create metadata
            metadata = DocumentMetadata(
                source=source,
                content_type="database/sqlite",
                size=len(content.encode("utf-8")),
                created_at=self._get_current_timestamp(),
                title=f"SQLite Database: {source}",
                language="sql",
                word_count=len(content.split()),
                processing_time=0.0,
            )

            return ProcessedDocument(content=content, metadata=metadata, success=True)

        finally:
            if conn:
                conn.close()

    async def _process_postgresql(self, source: str) -> ProcessedDocument:
        """Process PostgreSQL database."""
        # For now, return a placeholder implementation
        # In a real implementation, you would use psycopg2 or asyncpg
        content = f"PostgreSQL database processing not yet implemented for: {source}"

        metadata = DocumentMetadata(
            source=source,
            content_type="database/postgresql",
            size=len(content.encode("utf-8")),
            created_at=self._get_current_timestamp(),
            title=f"PostgreSQL Database: {source}",
            language="sql",
            word_count=len(content.split()),
            processing_time=0.0,
        )

        return ProcessedDocument(content=content, metadata=metadata, success=True)

    async def execute_query(self, source: str, query: str) -> QueryResult:
        """Execute a SQL query on the database."""
        try:
            db_type = self._get_database_type(source)
            sanitized_query = self._sanitize_sql(query)

            if db_type == "sqlite":
                conn = self._connect_sqlite(source)
                try:
                    return self._execute_sqlite_query(conn, sanitized_query)
                finally:
                    conn.close()
            else:
                raise MCPError(f"Query execution not supported for database type: {db_type}")

        except Exception as e:
            raise MCPError(f"Query execution failed: {e}")

    async def export_data(self, source: str, table_name: str, format: str = "json") -> str:
        """Export data from a table."""
        try:
            db_type = self._get_database_type(source)

            if db_type == "sqlite":
                conn = self._connect_sqlite(source)
                try:
                    cursor = conn.cursor()
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()

                    columns = [description[0] for description in cursor.description] if cursor.description else []

                    if format.lower() == "json":
                        data = [dict(zip(columns, row)) for row in rows]
                        return json.dumps(data, indent=2)
                    elif format.lower() == "csv":
                        import csv
                        import io

                        output = io.StringIO()
                        writer = csv.writer(output)
                        writer.writerow(columns)
                        writer.writerows(rows)
                        return output.getvalue()
                    else:
                        raise MCPError(f"Unsupported export format: {format}")

                finally:
                    conn.close()
            else:
                raise MCPError(f"Export not supported for database type: {db_type}")

        except Exception as e:
            raise MCPError(f"Export failed: {e}")

    def get_server_info(self) -> Dict[str, Any]:
        """Get server information."""
        return {
            "name": self.config.server_name,
            "version": "1.0.0",
            "supported_types": list(self.supported_types.keys()),
            "database_types": ["sqlite", "postgresql"],
            "features": ["schema_extraction", "query_execution", "data_export", "sql_injection_protection"],
            "config": self.db_config.model_dump(),
        }

    async def cleanup(self) -> None:
        """Cleanup database connections."""
        for conn in self._connections.values():
            try:
                if hasattr(conn, "close"):
                    conn.close()
            except Exception:
                pass
        self._connections.clear()

        if self._session:
            await self._session.aclose()
            self._session = None
