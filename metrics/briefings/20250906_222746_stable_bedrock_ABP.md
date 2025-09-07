# Agent Briefing Pack — stable_bedrock
Generated: 2025-09-06 22:27:46

## Constraints & Targets
- Gates: precision_min=0.2, recall_min=0.45, f1_min=0.22, latency_max=30.0, faithfulness_min=0.6


## Recent Lessons
- LL-2025-09-07-aec7 | pattern=balanced_low_f1 | conf=0.50 | effects={'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'} | Lower evidence threshold; boost Jaccard similarity weight for better matching
- LL-2025-09-07-c2e2 | pattern=balanced_low_f1 | conf=0.50 | effects={'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'} | Lower evidence threshold; boost Jaccard similarity weight for better matching
- LL-2025-09-07-887c | pattern=balanced_low_f1 | conf=0.50 | effects={'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'} | Lower evidence threshold; boost Jaccard similarity weight for better matching
- LL-2025-09-07-0de0 | pattern=balanced_low_f1 | conf=0.50 | effects={'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'} | Lower evidence threshold; boost Jaccard similarity weight for better matching
- LL-2025-09-07-e32e | pattern=balanced_low_f1 | conf=0.50 | effects={'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'} | Lower evidence threshold; boost Jaccard similarity weight for better matching
- LL-2025-09-07-0cf5 | pattern=balanced_low_f1 | conf=0.50 | effects={'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'} | Lower evidence threshold; boost Jaccard similarity weight for better matching
- LL-2025-09-07-9e09 | pattern=balanced_low_f1 | conf=0.50 | effects={'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'} | Lower evidence threshold; boost Jaccard similarity weight for better matching
- LL-2025-09-07-c7a2 | pattern=balanced_low_f1 | conf=0.50 | effects={'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'} | Lower evidence threshold; boost Jaccard similarity weight for better matching


## Pattern Cards
- Pattern balanced_low_f1 → RAGCHECKER_EVIDENCE_KEEP_PERCENTILE add -5, RAGCHECKER_WEIGHT_JACCARD mul 1.05; predicted: {'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'}; scope=profile; conf=0.50
- Pattern balanced_low_f1 → RAGCHECKER_EVIDENCE_KEEP_PERCENTILE add -5, RAGCHECKER_WEIGHT_JACCARD mul 1.05; predicted: {'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'}; scope=profile; conf=0.50
- Pattern balanced_low_f1 → RAGCHECKER_EVIDENCE_KEEP_PERCENTILE add -5, RAGCHECKER_WEIGHT_JACCARD mul 1.05; predicted: {'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'}; scope=profile; conf=0.50
- Pattern balanced_low_f1 → RAGCHECKER_EVIDENCE_KEEP_PERCENTILE add -5, RAGCHECKER_WEIGHT_JACCARD mul 1.05; predicted: {'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'}; scope=profile; conf=0.50
- Pattern balanced_low_f1 → RAGCHECKER_EVIDENCE_KEEP_PERCENTILE add -5, RAGCHECKER_WEIGHT_JACCARD mul 1.05; predicted: {'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'}; scope=profile; conf=0.50
- Pattern balanced_low_f1 → RAGCHECKER_EVIDENCE_KEEP_PERCENTILE add -5, RAGCHECKER_WEIGHT_JACCARD mul 1.05; predicted: {'f1': '+0.02~+0.04', 'precision': '+0.01~+0.02', 'recall': '+0.01~+0.02'}; scope=profile; conf=0.50


## Decision Docket

- Path: `metrics/derived_configs/20250906_222746_stable_bedrock_decision_docket.md`

