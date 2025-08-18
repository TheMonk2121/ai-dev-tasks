#!/usr/bin/env python3.12.123.11
"""
Setup Test Database for Vector Enhancement Migration
Creates a local PostgreSQL database for testing the migration.
"""

import os
import sys
import subprocess
import psycopg2
from pathlib import Path

def check_postgresql_installed():
    """Check if PostgreSQL is installed"""
    try:
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"PostgreSQL found: {result.stdout.strip()}")
            return True
        else:
            print("PostgreSQL not found")
            return False
    except FileNotFoundError:
        print("PostgreSQL not found")
        return False

def create_test_database():
    """Create a test database for migration testing"""
    try:
        # Try to connect to default PostgreSQL
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            user="postgres",
            password="",
            database="postgres"
        )
        
        # Set autocommit to True for CREATE DATABASE
        conn.autocommit = True
        
        with conn.cursor() as cursor:
            # Create test database
            cursor.execute("CREATE DATABASE vector_test_db")
            print("Created test database: vector_test_db")
            
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"Could not connect to PostgreSQL: {e}")
        print("Please ensure PostgreSQL is running and accessible")
        return False
    except psycopg2.ProgrammingError as e:
        if "already exists" in str(e):
            print("Test database already exists")
            return True
        else:
            print(f"Database creation error: {e}")
            return False

def setup_test_environment():
    """Set up the test environment"""
    print("Setting up test environment for Vector Enhancement Migration")
    
    # Check PostgreSQL installation
    if not check_postgresql_installed():
        print("Please install PostgreSQL first:")
        print("  macOS: brew install postgresql")
        print("  Ubuntu: sudo apt-get install postgresql postgresql-contrib")
        return False
    
    # Create test database
    if not create_test_database():
        return False
    
    # Set environment variable for the test database
    os.environ['POSTGRES_DSN'] = "postgresql://postgres@localhost:5432/vector_test_db"
    print(f"Set POSTGRES_DSN to: {os.environ['POSTGRES_DSN']}")
    
    return True

def apply_base_schema():
    """Apply the base schema to the test database"""
    try:
        schema_file = Path(__file__).parent.parent / "config" / "database" / "schema.sql"
        
        if not schema_file.exists():
            print(f"Base schema file not found: {schema_file}")
            return False
        
        # Read and apply base schema
        with open(schema_file) as f:
            schema_sql = f.read()
        
        conn = psycopg2.connect(os.environ['POSTGRES_DSN'])
        with conn.cursor() as cursor:
            # Split and execute statements
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements):
                if statement.startswith('--') or not statement:
                    continue
                    
                try:
                    print(f"Applying base schema statement {i+1}/{len(statements)}")
                    cursor.execute(statement)
                    conn.commit()
                except Exception as e:
                    print(f"Error applying statement {i+1}: {e}")
                    print(f"Statement: {statement[:100]}...")
                    conn.rollback()
                    # Continue with next statement instead of failing completely
                    continue
        
        conn.close()
        print("Base schema applied (some statements may have failed)")
        return True
        
    except Exception as e:
        print(f"Error applying base schema: {e}")
        return False

def main():
    """Main entry point"""
    print("Vector Enhancement Migration - Test Database Setup")
    print("=" * 50)
    
    # Set up test environment
    if not setup_test_environment():
        print("Failed to set up test environment")
        sys.exit(1)
    
    # Apply base schema
    if not apply_base_schema():
        print("Failed to apply base schema")
        sys.exit(1)
    
    print("\nTest database setup completed successfully!")
    print("You can now run the vector enhancement migration:")
    print("  python3 scripts/apply_vector_enhancement.py")
    print("\nOr run the tests:")
    print("  python3 tests/test_vector_enhancement_migration.py")

if __name__ == "__main__":
    main() 