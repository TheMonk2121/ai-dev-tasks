#!/usr/bin/env python3
"""
DSPy PostgreSQL Memory Storage Setup
Integrates DSPy with your existing PostgreSQL database for persistent memory storage.
"""

import os
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, Any, List
import dspy
from dspy.storage import DatabaseStorage

class DSPyPostgreSQLStorage:
    """Custom PostgreSQL storage for DSPy memory"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.setup_database()
    
    def setup_database(self):
        """Create DSPy tables in your existing PostgreSQL database"""
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                # Create DSPy memory tables
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS dspy_signatures (
                        id SERIAL PRIMARY KEY,
                        signature_name VARCHAR(255) UNIQUE NOT NULL,
                        prompt_structure TEXT NOT NULL,
                        success_rate FLOAT DEFAULT 0.0,
                        usage_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS dspy_examples (
                        id SERIAL PRIMARY KEY,
                        signature_id INTEGER REFERENCES dspy_signatures(id),
                        input_data JSONB NOT NULL,
                        output_data JSONB NOT NULL,
                        quality_score FLOAT DEFAULT 0.0,
                        context JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS dspy_optimizations (
                        id SERIAL PRIMARY KEY,
                        signature_name VARCHAR(255) NOT NULL,
                        optimization_type VARCHAR(100) NOT NULL,
                        old_prompt TEXT,
                        new_prompt TEXT,
                        improvement_score FLOAT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Create indexes for better performance
                cur.execute("CREATE INDEX IF NOT EXISTS idx_signatures_name ON dspy_signatures(signature_name);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_examples_signature ON dspy_examples(signature_id);")
                cur.execute("CREATE INDEX IF NOT EXISTS idx_examples_quality ON dspy_examples(quality_score);")
                
                conn.commit()
    
    def store_signature(self, signature_name: str, prompt_structure: str, success_rate: float = 0.0):
        """Store a new signature or update existing one"""
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO dspy_signatures (signature_name, prompt_structure, success_rate, usage_count)
                    VALUES (%s, %s, %s, 1)
                    ON CONFLICT (signature_name) 
                    DO UPDATE SET 
                        prompt_structure = EXCLUDED.prompt_structure,
                        success_rate = (dspy_signatures.success_rate * dspy_signatures.usage_count + EXCLUDED.success_rate) / (dspy_signatures.usage_count + 1),
                        usage_count = dspy_signatures.usage_count + 1,
                        updated_at = CURRENT_TIMESTAMP
                    RETURNING id;
                """, (signature_name, prompt_structure, success_rate))
                return cur.fetchone()[0]
    
    def store_example(self, signature_name: str, input_data: Dict, output_data: Dict, quality_score: float, context: Dict = None):
        """Store a successful example"""
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor() as cur:
                # Get signature ID
                cur.execute("SELECT id FROM dspy_signatures WHERE signature_name = %s", (signature_name,))
                signature_id = cur.fetchone()[0]
                
                # Store example
                cur.execute("""
                    INSERT INTO dspy_examples (signature_id, input_data, output_data, quality_score, context)
                    VALUES (%s, %s, %s, %s, %s)
                """, (signature_id, json.dumps(input_data), json.dumps(output_data), quality_score, json.dumps(context) if context else None))
                conn.commit()
    
    def get_best_examples(self, signature_name: str, limit: int = 5) -> List[Dict]:
        """Get the best examples for a signature"""
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT e.input_data, e.output_data, e.quality_score, e.context
                    FROM dspy_examples e
                    JOIN dspy_signatures s ON e.signature_id = s.id
                    WHERE s.signature_name = %s
                    ORDER BY e.quality_score DESC
                    LIMIT %s
                """, (signature_name, limit))
                return cur.fetchall()
    
    def get_signature_stats(self, signature_name: str) -> Dict:
        """Get statistics for a signature"""
        with psycopg2.connect(self.connection_string) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT signature_name, prompt_structure, success_rate, usage_count, created_at, updated_at
                    FROM dspy_signatures
                    WHERE signature_name = %s
                """, (signature_name,))
                return cur.fetchone()

def setup_dspy_with_postgres():
    """Configure DSPy to use your existing PostgreSQL database"""
    
    # Your existing PostgreSQL connection (from your docker-compose setup)
    connection_string = os.getenv(
        "DSPY_POSTGRES_URL", 
        "postgresql://ai_user:ai_password@localhost:5432/ai_agency"
    )
    
    # Create custom storage
    storage = DSPyPostgreSQLStorage(connection_string)
    
    # Configure DSPy to use PostgreSQL storage
    dspy.settings.configure(
        # You can add your Mistral-7B model here
        # lm=your_mistral_model,
        storage=storage
    )
    
    print("✅ DSPy configured to use PostgreSQL for memory storage")
    print(f"📊 Database: {connection_string}")
    return storage

# Example usage
if __name__ == "__main__":
    storage = setup_dspy_with_postgres()
    
    # Test the setup
    print("\n🧪 Testing PostgreSQL storage...")
    
    # Store a test signature
    signature_id = storage.store_signature(
        "prd_analysis",
        "Analyze PRD and extract requirements",
        success_rate=0.85
    )
    print(f"✅ Stored signature: {signature_id}")
    
    # Store a test example
    storage.store_example(
        "prd_analysis",
        {"prd_content": "Create webhook system"},
        {"tasks": ["Setup HTTP server", "Configure authentication"]},
        quality_score=0.9,
        context={"project": "cursor-n8n-integration"}
    )
    print("✅ Stored example")
    
    # Retrieve best examples
    examples = storage.get_best_examples("prd_analysis", limit=3)
    print(f"✅ Retrieved {len(examples)} examples")
    
    # Get signature stats
    stats = storage.get_signature_stats("prd_analysis")
    print(f"✅ Signature stats: {stats['success_rate']:.2f} success rate")
    
    print("\n🎉 DSPy PostgreSQL setup complete!") 