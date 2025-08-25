#!/usr/bin/env python3
"""
Test script for Database MCP Server

This script validates the Database MCP Server functionality by creating
a test SQLite database and processing it through the server.
"""

import asyncio
import os
import sqlite3

# Add src to path
import sys
import tempfile

sys.path.append("src")

from utils.mcp_integration.database_server import DatabaseMCPServer, MCPConfig


def create_test_database():
    """Create a test SQLite database with sample data."""
    # Create temporary database file
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    # Create test database with sample data
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create users table
    cursor.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Create products table
    cursor.execute(
        """
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT,
            in_stock BOOLEAN DEFAULT 1
        )
    """
    )

    # Create orders table
    cursor.execute(
        """
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    """
    )

    # Insert sample data
    cursor.execute(
        """
        INSERT INTO users (name, email, age) VALUES
        ('John Doe', 'john@example.com', 30),
        ('Jane Smith', 'jane@example.com', 25),
        ('Bob Johnson', 'bob@example.com', 35),
        ('Alice Brown', 'alice@example.com', 28),
        ('Charlie Wilson', 'charlie@example.com', 32)
    """
    )

    cursor.execute(
        """
        INSERT INTO products (name, price, category, in_stock) VALUES
        ('Laptop', 999.99, 'Electronics', 1),
        ('Mouse', 29.99, 'Electronics', 1),
        ('Keyboard', 79.99, 'Electronics', 0),
        ('Desk Chair', 199.99, 'Furniture', 1),
        ('Coffee Mug', 12.99, 'Kitchen', 1)
    """
    )

    cursor.execute(
        """
        INSERT INTO orders (user_id, product_id, quantity) VALUES
        (1, 1, 1),
        (1, 2, 2),
        (2, 3, 1),
        (3, 4, 1),
        (4, 5, 3)
    """
    )

    conn.commit()
    conn.close()

    return db_path


async def test_database_server():
    """Test the Database MCP Server functionality."""
    print("🧪 Testing Database MCP Server...")

    # Create test database
    db_path = create_test_database()
    print(f"1. Created test database: {db_path}")

    try:
        # Initialize server
        config = MCPConfig(server_name="test_database_server")
        server = DatabaseMCPServer(config)

        print("2. Server Configuration:")
        print(f"   ✅ Server name: {server.config.server_name}")
        print(f"   ✅ Supported types: {len(server.supported_types)}")
        print(f"   ✅ Database config: {server.db_config.max_rows} max rows")

        # Test source validation
        print("\n3. Testing Source Validation:")
        print(f"   ✅ SQLite file: {server.validate_source(db_path)}")
        print(f"   ✅ PostgreSQL URL: {server.validate_source('postgresql://localhost/db')}")
        print(f"   ✅ Invalid URL: {server.validate_source('invalid://url')}")

        # Test database type detection
        print("\n4. Testing Database Type Detection:")
        print(f"   ✅ SQLite detection: {server._get_database_type(db_path)}")
        print(f"   ✅ PostgreSQL detection: {server._get_database_type('postgresql://localhost/db')}")

        # Test SQL injection protection
        print("\n5. Testing SQL Injection Protection:")
        safe_query = "SELECT * FROM users WHERE name = 'test'"
        print(f"   ✅ Safe query: {server._sanitize_sql(safe_query)}")

        try:
            server._sanitize_sql("DROP TABLE users")
            print("   ❌ Dangerous query should have been blocked")
        except Exception as e:
            print(f"   ✅ Dangerous query blocked: {str(e)[:50]}...")

        # Test schema extraction
        print("\n6. Testing Schema Extraction:")
        conn = server._connect_sqlite(db_path)
        try:
            schema = server._get_sqlite_schema(conn)
            print(f"   ✅ Database name: {schema.database_name}")
            print(f"   ✅ Tables found: {len(schema.tables)}")
            for table in schema.tables:
                print(f"      - {table.name}: {len(table.columns)} columns, {table.row_count} rows")
        finally:
            conn.close()

        # Test query execution
        print("\n7. Testing Query Execution:")
        result = await server.execute_query(db_path, "SELECT name, email FROM users LIMIT 3")
        print(f"   ✅ Query executed: {result.query}")
        print(f"   ✅ Columns: {result.columns}")
        print(f"   ✅ Rows returned: {result.row_count}")
        print(f"   ✅ Execution time: {result.execution_time_ms:.2f}ms")
        print(f"   ✅ Sample data: {result.rows[0]}")

        # Test data export
        print("\n8. Testing Data Export:")
        json_export = await server.export_data(db_path, "users", "json")
        print(f"   ✅ JSON export length: {len(json_export)} characters")

        csv_export = await server.export_data(db_path, "users", "csv")
        print(f"   ✅ CSV export lines: {len(csv_export.split(chr(10)))}")

        # Test document processing
        print("\n9. Testing Document Processing:")
        processed_doc = await server.process_document(db_path)
        print(f"   ✅ Content type: {processed_doc.metadata.content_type}")
        print(f"   ✅ Title: {processed_doc.metadata.title}")
        print(f"   ✅ Content length: {len(processed_doc.content)} characters")
        print(f"   ✅ Success: {processed_doc.success}")
        print(f"   ✅ Word count: {processed_doc.metadata.word_count}")

        # Test server information
        print("\n10. Testing Server Information:")
        info = server.get_server_info()
        print(f"   ✅ Server name: {info['name']}")
        print(f"   ✅ Version: {info['version']}")
        print(f"   ✅ Supported types: {len(info['supported_types'])}")
        print(f"   ✅ Database types: {info['database_types']}")
        print(f"   ✅ Features: {info['features']}")

        # Test cleanup
        print("\n11. Testing Cleanup:")
        await server.cleanup()
        print("   ✅ Server cleaned up successfully")

        print("\n🎉 All Database MCP Server tests completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        # Cleanup test database
        try:
            os.unlink(db_path)
            print(f"   🧹 Cleaned up test database: {db_path}")
        except Exception as e:
            print(f"   ⚠️  Failed to cleanup test database: {e}")


if __name__ == "__main__":
    asyncio.run(test_database_server())
