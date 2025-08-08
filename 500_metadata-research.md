<!-- CONTEXT_REFERENCE: 400_context-priority-guide.md -->
<!-- MODULE_REFERENCE: 400_metadata-collection-guide.md -->
<!-- MODULE_REFERENCE: 400_metadata-quick-reference.md -->

# Metadata & Governance Research

Backlog link: B-007, B-045

 
## 🔎 TL;DR
- Define required metadata taxonomy for docs/chunks/events
- Enforce provenance, owners, span offsets, and validation flags
- Govern PII handling and queryability for audits

 
## Key Findings
- Consistent identifiers (doc_id, chunk_id) and span offsets enable grounding, audits, and reproducibility.
- Provenance and last_verified fields are essential for trust and drift detection.
- Governance requires PII classification and redaction policies at ingestion and logging.

 
## Actionable Patterns
- Field dictionary: doc_id, source_path, section, chunk_id, start_offset, end_offset, owner, updated_at, provenance, validated_flag, raw_score.
- Ingestion hooks in indexer to populate fields; validators to reject incomplete records.
- Query helpers: by owner, by updated_since, by provenance for review workflows.

 
## Implementation References
- 400_metadata-collection-guide.md (taxonomy/governance)
- 400_metadata-quick-reference.md (field quick ref)
- scripts/documentation_indexer.py (emit fields)
- dspy-rag-system/config/database/vector_enhancement_schema.sql (columns)

 
## Citations
- 400_metadata-collection-guide.md
- 400_metadata-quick-reference.md

