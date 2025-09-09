# 300_evals/ssot/registry_core.py
from .schema import EvalSuite, EvalPass, PassConfig, MetricSpec, RunSpec

SUITE = EvalSuite(
    id="300_core",
    title="Core Evaluation Suite",
    passes=[
        EvalPass(
            id="retrieval_only_baseline",
            name="Retrieval-Only Baseline",
            description="Confirms retrieval/rerank/chunk config (450/10%/J=0.8/prefix-A).",
            tags=["retrieval", "baseline"],
            config_layers=["base", "stable"],
            config=PassConfig(
                FEW_SHOT_K=0,
                EVAL_COT=0,
                EVAL_DISABLE_CACHE=1,
                DSPY_TELEPROMPT_CACHE="false",
                TEMPERATURE=0.0,
                MAX_WORKERS=3,
                RATE_LIMIT_PROFILE="stable",
            ),
            run=RunSpec(
                kind="ragchecker",
                script="scripts/_ragchecker_eval_impl.py",
                args=[]
            ),
            metrics=[
                MetricSpec(key="f1", target=0.50, direction=">="),
                MetricSpec(key="faithfulness", target=0.80, direction=">="),
            ],
        ),
        EvalPass(
            id="deterministic_few_shot",
            name="Deterministic Few-Shot (k=5, knn, seed=42)",
            description="Records prompt_audit.few_shot_ids, prompt_hash, CoT disabled.",
            tags=["reader", "fewshot"],
            config_layers=["base", "stable", "delta_fewshot"],
            config=PassConfig(
                FEW_SHOT_K=5,
                FEW_SHOT_SELECTOR="knn",
                FEW_SHOT_SEED=42,
                EVAL_COT=0,
                EVAL_DISABLE_CACHE=1,
                DSPY_TELEPROMPT_CACHE="false",
                MAX_WORKERS=3,
                RATE_LIMIT_PROFILE="stable",
            ),
            run=RunSpec(
                kind="ragchecker",
                script="scripts/_ragchecker_eval_impl.py",
                args=[]
            ),
            metrics=[MetricSpec(key="f1", target=0.60, direction=">=")],
        ),
        EvalPass(
            id="calibrate_thresholds",
            name="Calibrate Answerable Thresholds",
            description="Runs calibration; writes metrics/calibration/thresholds.json.",
            tags=["calibration"],
            config_layers=["base", "stable"],
            config=PassConfig(),
            run=RunSpec(
                kind="calibrate",
                script="scripts/calibrate_answerable_threshold.py",
                args=[]
            ),
            metrics=[],  # calibration produces artifacts; you can add gates if exposed
        ),
        EvalPass(
            id="reader_debug_ab",
            name="Reader Debug A/B",
            description="Debug parity between teleprompt configs. See reader_debug outputs.",
            tags=["debug", "reader"],
            config_layers=["base", "stable"],
            config=PassConfig(),
            run=RunSpec(
                kind="reader_debug",
                script="scripts/reader_debug_ab.py",
                args=[]
            ),
            metrics=[],  # typically not scored; leaves traces under metrics/reader_debug/
        ),
        EvalPass(
            id="reranker_ablation_off",
            name="Reranker Ablation (OFF)",
            description="Retrieval with reranker disabled to establish baseline for uplift.",
            tags=["retrieval", "reranker", "ablation"],
            config_layers=["base", "stable", "reranker_off"],
            config=PassConfig(
                MAX_WORKERS=3,
                RATE_LIMIT_PROFILE="stable",
            ),
            run=RunSpec(
                kind="ragchecker",
                script="scripts/_ragchecker_eval_impl.py",
                args=[],
            ),
            metrics=[
                MetricSpec(key="f1", target=0.50, direction=">="),
                MetricSpec(key="faithfulness", target=0.80, direction=">="),
            ],
        ),
        EvalPass(
            id="reranker_ablation_on",
            name="Reranker Ablation (ON)",
            description="Retrieval with cross-encoder reranker enabled to measure uplift.",
            tags=["retrieval", "reranker", "ablation"],
            config_layers=["base", "stable", "reranker_on"],
            config=PassConfig(
                MAX_WORKERS=3,
                RATE_LIMIT_PROFILE="stable",
            ),
            run=RunSpec(
                kind="ragchecker",
                script="scripts/_ragchecker_eval_impl.py",
                args=[],
            ),
            metrics=[
                MetricSpec(key="f1", target=0.50, direction=">="),
                MetricSpec(key="faithfulness", target=0.80, direction=">="),
            ],
        ),
    ]
)
