"""Initial migration with pgvector and TimescaleDB support

Revision ID: 525a33d4fb92
Revises:
Create Date: 2025-09-16 22:08:30.731659

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "525a33d4fb92"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema with pgvector and TimescaleDB support."""

    # Enable required extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_stat_statements")

    # Create core tables with vector support
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS document_chunks (
            id SERIAL,
            document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
            content TEXT NOT NULL,
            content_tsv TSVECTOR,
            embedding vector(384),
            chunk_index INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id, created_at)
        )
    """
    )

    # Create vector indexes
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding ON document_chunks USING hnsw (embedding vector_cosine_ops)"
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_document_chunks_content_tsv ON document_chunks USING gin (content_tsv)")

    # Create conversation tables
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_sessions (
            id SERIAL PRIMARY KEY,
            session_id TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_messages (
            id SERIAL,
            session_id TEXT REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            embedding vector(384),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (id, created_at)
        )
    """
    )

    # Create conversation vector indexes
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_conversation_messages_embedding ON conversation_messages USING hnsw (embedding vector_cosine_ops)"
    )

    # Create TimescaleDB hypertables (if TimescaleDB is available)
    # Note: Only create hypertables if TimescaleDB extension is available
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
                -- Check if tables exist and have data
                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'document_chunks') THEN
                    -- Table exists, check if it's already a hypertable
                    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'document_chunks') THEN
                        -- Drop unique constraints that don't include created_at (TimescaleDB requirement)
                        ALTER TABLE document_chunks DROP CONSTRAINT IF EXISTS document_chunks_doc_idx_uniq;

                        -- Alter primary key to include created_at for TimescaleDB compatibility
                        ALTER TABLE document_chunks DROP CONSTRAINT IF EXISTS document_chunks_pkey;
                        ALTER TABLE document_chunks ADD PRIMARY KEY (id, created_at);

                        -- Create hypertable
                        PERFORM create_hypertable('document_chunks', 'created_at',
                                                if_not_exists => TRUE, migrate_data => TRUE);

                        -- Recreate the unique constraint with created_at
                        CREATE UNIQUE INDEX document_chunks_doc_idx_uniq
                        ON document_chunks (document_id, chunk_index, created_at);
                    END IF;
                END IF;

                IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'conversation_messages') THEN
                    -- Table exists, check if it's already a hypertable
                    IF NOT EXISTS (SELECT 1 FROM timescaledb_information.hypertables WHERE hypertable_name = 'conversation_messages') THEN
                        -- Alter primary key to include created_at for TimescaleDB compatibility
                        ALTER TABLE conversation_messages DROP CONSTRAINT IF EXISTS conversation_messages_pkey;
                        ALTER TABLE conversation_messages ADD PRIMARY KEY (id, created_at);
                        -- Create hypertable
                        PERFORM create_hypertable('conversation_messages', 'created_at',
                                                if_not_exists => TRUE, migrate_data => TRUE);
                    END IF;
                END IF;
            END IF;
        END $$;
    """
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Drop TimescaleDB hypertables
    op.execute("SELECT drop_hypertable('conversation_messages', if_exists => TRUE)")
    op.execute("SELECT drop_hypertable('document_chunks', if_exists => TRUE)")

    # Drop tables
    op.execute("DROP TABLE IF EXISTS conversation_messages CASCADE")
    op.execute("DROP TABLE IF EXISTS conversation_sessions CASCADE")
    op.execute("DROP TABLE IF EXISTS document_chunks CASCADE")
    op.execute("DROP TABLE IF EXISTS documents CASCADE")

    # Note: We don't drop extensions as they might be used by other tables
