# Agent Briefing Pack — stable_bedrock
Generated: 2025-09-06 17:35:04

## Constraints & Targets
- Gates: precision_min=0.2, recall_min=0.45, f1_min=0.22, latency_max=30.0, faithfulness_min=0.6

## Recent Lessons
- LL-2025-09-06-001 | pattern=high_precision_low_recall | conf=0.60 | effects={'recall': '+0.03~+0.06', 'precision': '-0.01~0'} | Lower evidence threshold and boost Jaccard weight to improve recall while maintaining precision
- LL-2025-09-06-002 | pattern=test_new_key | conf=0.80 | effects={'test': '+0.01'} | Test adding new parameter

## Decision Docket

- Path: `metrics/derived_configs/20250906_173504_stable_bedrock_decision_docket.md`

