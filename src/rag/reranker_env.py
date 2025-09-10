from __future__ import annotations
import os


def _b(*names: str, default: bool = False) -> bool:
    for n in names:
        v = os.getenv(n)
        if v is not None:
            return v.strip().lower() in {"1", "true", "yes", "on"}
    return default


def _i(*names: str, default: int = 0) -> int:
    for n in names:
        v = os.getenv(n)
        if v is not None:
            try:
                return int(v)
            except ValueError:
                pass
    return default


def _s(*names: str, default: str = "") -> str:
    for n in names:
        v = os.getenv(n)
        if v:
            return v
    return default


def _device(spec: str) -> str:
    if spec != "auto":
        return spec
    try:
        import torch  # type: ignore

        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            return "mps"
    except Exception:
        pass
    return "cpu"


RERANK_ENABLE = _b("RERANK_ENABLE", "RERANKER_ENABLED", default=False)
RERANK_INPUT_TOPK = _i("RERANK_INPUT_TOPK", "RERANK_POOL", default=50)
RERANK_KEEP = _i("RERANK_KEEP", "RERANK_TOPN", default=12)
RERANK_BATCH = _i("RERANK_BATCH", default=8)
RERANKER_MODEL = _s("RERANKER_MODEL", default="cross-encoder/ms-marco-MiniLM-L-6-v2")
TORCH_DEVICE = _device(_s("TORCH_DEVICE", default="auto"))

RERANK_CACHE_BACKEND = _s("RERANK_CACHE_BACKEND", default="sqlite")  # sqlite|postgres
RERANK_CACHE_DSN = _s("RERANK_CACHE_DSN", default="")
RERANK_CACHE_PATH = _s("RERANK_CACHE_PATH", default=".cache/rerank.sqlite")


def log_config(logger_print=print):
    logger_print(
        f"[reranker] enable={int(RERANK_ENABLE)} model={RERANKER_MODEL} "
        f"input_topk={RERANK_INPUT_TOPK} keep={RERANK_KEEP} "
        f"batch={RERANK_BATCH} device={TORCH_DEVICE} "
        f"cache={RERANK_CACHE_BACKEND}"
    )

