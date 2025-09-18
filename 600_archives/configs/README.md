# DEPRECATED: This file has been moved to 600_archives/600_deprecated/configs/stable_bedrock.env.deprecated
# DEPRECATED CONFIGURATION FILES

This directory contains deprecated configuration files that have been moved to 600_archives/600_deprecated/.

## Deprecated Files:
- stable_bedrock.env → 600_archives/600_deprecated/configs/stable_bedrock.env.deprecated

## Current Configuration:
The canonical evaluation system now uses:
- scripts/configs/profiles/gold.env (primary)
- scripts/configs/profiles/real.env (alternative)
- scripts/configs/profiles/mock.env (testing only)

## Migration:
All evaluation scripts have been updated to use the gold profile configuration by default.
The gold profile includes complete RAG system settings, fusion parameters, and database configuration.

For more information, see:
- 000_core/000_evaluation-system-entry-point.md
- scripts/shell/deployment/run_evals.sh
