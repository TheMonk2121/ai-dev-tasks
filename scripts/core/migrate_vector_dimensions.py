#!/usr/bin/env python3
"""
Migrate vector dimensions from 1024 to 384 in the database.
"""

import os

# Add project paths
import sys

import psycopg

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from sentence_transformers import SentenceTransformer

from src.common.db_dsn import resolve_dsn
from src.common.psycopg3_config import Psycopg3Config


def migrate_vector_dimensions():
    """Migrate all vector embeddings from 1024 to 384 dimensions."""

    print("🔄 Migrating Vector Dimensions: 1024 → 384")
    print("=" * 50)

    # Initialize the new embedding model
    print("📥 Loading all-MiniLM-L6-v2 model...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    print(f"✅ Model loaded (dimensions: {embedder.get_sentence_embedding_dimension()})")

    try:
        with psycopg.connect(resolve_dsn(strict=False, role="migrate_vector_dimensions")) as conn:
            with conn.cursor() as cur:
                # Get all records with embeddings from atlas_node
                cur.execute(
                    """
                    SELECT node_id, content 
                    FROM atlas_node 
                    WHERE embedding IS NOT NULL 
                    AND content IS NOT NULL
                    ORDER BY created_at DESC
                """
                )

                atlas_records = cur.fetchall()
                print(f"📊 Found {len(atlas_records)} records in atlas_node to migrate")

                # Migrate atlas_node records
                for i, (node_id, content) in enumerate(atlas_records):
                    print(f"   Processing {i+1}/{len(atlas_records)}: {node_id[:50]}...")

                    # Generate new embedding
                    new_embedding = embedder.encode(content).tolist()

                    # Update the record
                    cur.execute(
                        """
                        UPDATE atlas_node 
                        SET embedding = %s 
                        WHERE node_id = %s
                    """,
                        (new_embedding, node_id),
                    )

                # Get all records with embeddings from conv_chunks
                cur.execute(
                    """
                    SELECT id, chunk_text 
                    FROM conv_chunks 
                    WHERE embedding IS NOT NULL 
                    AND chunk_text IS NOT NULL
                    ORDER BY created_at DESC
                """
                )

                conv_records = cur.fetchall()
                print(f"📊 Found {len(conv_records)} records in conv_chunks to migrate")

                # Migrate conv_chunks records
                for i, (chunk_id, chunk_text) in enumerate(conv_records):
                    print(f"   Processing {i+1}/{len(conv_records)}: chunk {chunk_id}")

                    # Generate new embedding
                    new_embedding = embedder.encode(chunk_text).tolist()

                    # Update the record
                    cur.execute(
                        """
                        UPDATE conv_chunks 
                        SET embedding = %s 
                        WHERE id = %s
                    """,
                        (new_embedding, chunk_id),
                    )

                # Commit all changes
                conn.commit()
                print("✅ Migration completed successfully!")

                # Verify the migration
                cur.execute(
                    """
                    SELECT 
                        CASE 
                            WHEN embedding IS NOT NULL THEN array_length(embedding, 1)
                            ELSE NULL
                        END as embedding_dim,
                        COUNT(*) as count
                    FROM atlas_node 
                    WHERE embedding IS NOT NULL
                    GROUP BY array_length(embedding, 1)
                """
                )

                dimensions = cur.fetchall()
                print("\\n📊 Verification - atlas_node dimensions:")
                for dim in dimensions:
                    print(f"   {dim[0]} dimensions: {dim[1]} records")

                cur.execute(
                    """
                    SELECT 
                        CASE 
                            WHEN embedding IS NOT NULL THEN array_length(embedding, 1)
                            ELSE NULL
                        END as embedding_dim,
                        COUNT(*) as count
                    FROM conv_chunks 
                    WHERE embedding IS NOT NULL
                    GROUP BY array_length(embedding, 1)
                """
                )

                dimensions = cur.fetchall()
                print("\\n📊 Verification - conv_chunks dimensions:")
                for dim in dimensions:
                    print(f"   {dim[0]} dimensions: {dim[1]} records")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def main():
    """Main migration function."""

    # Set database connection
    os.environ["POSTGRES_DSN"] = "postgresql://danieljacobs@localhost:5432/ai_agency"

    print("🚀 Starting Vector Dimension Migration")
    print("=" * 50)
    print("⚠️  WARNING: This will update all existing embeddings!")
    print("   Make sure you have a database backup before proceeding.")
    print()

    # Ask for confirmation
    response = input("Do you want to proceed? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Migration cancelled")
        return 1

    # Run migration
    success = migrate_vector_dimensions()

    if success:
        print("\\n🎉 Migration completed successfully!")
        print("   All embeddings are now 384-dimensional using all-MiniLM-L6-v2")
        return 0
    else:
        print("\\n❌ Migration failed!")
        return 1


if __name__ == "__main__":
    exit(main())
