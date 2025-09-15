-- Fix Atlas schema to match specification
-- This script migrates the existing atlas tables to match the recommended schema

-- Step 1: Add missing columns to atlas_node
ALTER TABLE atlas_node 
ADD COLUMN IF NOT EXISTS expires_at TIMESTAMPTZ;

-- Step 2: Add missing indexes to atlas_node
CREATE INDEX IF NOT EXISTS idx_node_type ON atlas_node(node_type);
CREATE INDEX IF NOT EXISTS idx_node_meta_gin ON atlas_node USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_node_embed_hnsw ON atlas_node USING hnsw (embedding vector_cosine_ops);

-- Step 3: Fix atlas_edge table structure
-- First, let's check if we need to add missing columns
ALTER TABLE atlas_edge 
ADD COLUMN IF NOT EXISTS evidence JSONB DEFAULT '{}';

-- Update existing evidence text to JSONB if it exists and is not already JSONB
UPDATE atlas_edge 
SET evidence = to_jsonb(evidence::text) 
WHERE evidence IS NOT NULL 
  AND evidence != '' 
  AND evidence::text !~ '^[{\[].*[}\]]$';

-- Step 4: Add missing indexes to atlas_edge
CREATE INDEX IF NOT EXISTS idx_edge_src ON atlas_edge(source_node_id);
CREATE INDEX IF NOT EXISTS idx_edge_tgt ON atlas_edge(target_node_id);

-- Step 5: Add proper constraints and defaults
ALTER TABLE atlas_node 
ALTER COLUMN metadata SET DEFAULT '{}',
ALTER COLUMN created_at SET DEFAULT now(),
ALTER COLUMN updated_at SET DEFAULT now();

ALTER TABLE atlas_edge 
ALTER COLUMN evidence SET DEFAULT '{}',
ALTER COLUMN metadata SET DEFAULT '{}',
ALTER COLUMN created_at SET DEFAULT now();

-- Step 6: Add comments for documentation
COMMENT ON TABLE atlas_node IS 'Atlas knowledge graph nodes with semantic embeddings';
COMMENT ON TABLE atlas_edge IS 'Atlas knowledge graph edges with provenance evidence';
COMMENT ON COLUMN atlas_node.expires_at IS 'Optional expiration timestamp for temporary nodes';
COMMENT ON COLUMN atlas_edge.evidence IS 'Provenance evidence linking to document chunks or other sources';
