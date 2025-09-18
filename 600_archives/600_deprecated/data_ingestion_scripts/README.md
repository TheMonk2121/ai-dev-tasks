# Deprecated Data Ingestion Scripts

This directory contains deprecated data ingestion scripts that have been superseded by the enhanced main ingestion script.

## Deprecated Files

### `comprehensive_data_ingestion.py.deprecated`
- **Original Location**: `300_evals/scripts/evaluation/comprehensive_data_ingestion.py`
- **Deprecated Date**: 2025-09-16
- **Reason**: Features cherry-picked into main ingestion script
- **Replacement**: `scripts/data_processing/core/ingest_real_data.py`

## Migration

The main ingestion script (`scripts/data_processing/core/ingest_real_data.py`) now includes all the best features from the comprehensive script:

### ✅ **Cherry-Picked Features:**
1. **Targeted Directory Processing** - Focuses on 000-500 directories instead of everything
2. **Enhanced Progress Tracking** - Per-directory stats and comprehensive reporting
3. **Better Metadata Extraction** - Directory, file info, ingestion run tracking
4. **Results Persistence** - Saves detailed results to `metrics/ingestion/`
5. **Improved Error Handling** - Better error tracking and reporting

### 🔧 **Enhanced Main Script Features:**
- **Real BGE Embeddings** (not mock)
- **Token-based Chunking** with overlap
- **Document Provenance Tracking**
- **Comprehensive File Type Support**
- **Production-ready Error Handling**

## Usage

Use the enhanced main script:

```bash
# Direct usage
uv run python scripts/data_processing/core/ingest_real_data.py

# Via symlink (backward compatibility)
uv run python scripts/ingest_real_data.py

# Via setup script (updated)
uv run python scripts/utilities/setup_production_database.py
```

## Configuration

The enhanced script supports all the same environment variables as before, plus new ones for targeted processing:

- `INGEST_RUN_ID` - Unique identifier for this ingestion run
- `CHUNK_VARIANT` - Chunking strategy variant
- `CHUNK_SIZE_TOKENS` - Token size per chunk (default: 220)
- `CHUNK_OVERLAP_TOKENS` - Overlap between chunks (default: 48)
- `SOURCE_COMMIT` - Git commit hash for provenance

## Results

Results are saved to `metrics/ingestion/ingestion_results_{timestamp}.json` with detailed statistics and per-directory breakdowns.
