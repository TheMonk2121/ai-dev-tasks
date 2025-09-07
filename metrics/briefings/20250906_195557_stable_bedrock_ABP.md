# Agent Briefing Pack — stable_bedrock
Generated: 2025-09-06 19:55:57

## Constraints & Targets
- Gates: precision_min=0.2, recall_min=0.45, f1_min=0.22, latency_max=30.0, faithfulness_min=0.6


## Recent Lessons
- LL-2025-09-07-781b | pattern=balanced_low_f1 | conf=0.50 | effects={'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'} | Lower evidence threshold; boost Jaccard similarity weight for better matching
- LL-2025-09-06-001 | pattern=high_precision_low_recall | conf=0.60 | effects={'recall': '+0.03~+0.06', 'precision': '-0.01~0'} | Lower evidence threshold and boost Jaccard weight to improve recall while maintaining precision
- LL-2025-09-06-002 | pattern=test_new_key | conf=0.80 | effects={'test': '+0.01'} | Test adding new parameter


## Pattern Cards
- Pattern balanced_low_f1 → RAGCHECKER_EVIDENCE_KEEP_PERCENTILE add -5, RAGCHECKER_WEIGHT_JACCARD mul 1.05; predicted: {'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'}; scope=profile; conf=0.50


## Decision Docket

- Path: `metrics/derived_configs/20250906_195557_stable_bedrock_decision_docket.md`

