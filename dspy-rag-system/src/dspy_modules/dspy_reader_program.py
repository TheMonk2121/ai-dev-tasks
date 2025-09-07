import json
import os
import sys

import dspy

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dspy_modules.reader.entrypoint import build_reader_context
from dspy_modules.retriever.limits import load_limits
from dspy_modules.retriever.pg import run_fused_query
from dspy_modules.retriever.query_rewrite import build_channel_queries
from dspy_modules.retriever.rerank import mmr_rerank, per_file_cap


# ---- Model config (swap as needed)
def _lm():
    # Examples:
    # return dspy.LM(model="openai/gpt-4o-mini", max_tokens=512, temperature=0.2)
    # return dspy.LM(model="ollama/llama2", max_tokens=512, temperature=0.2)
    # Keep tokens low & temp ~0.2 for stability; limit concurrency outside (CI runner)
    model_name = os.getenv("DSPY_MODEL", "anthropic.claude-3-haiku-20240307-v1:0")
    if "/" not in model_name:
        model_name = f"bedrock/{model_name}"
    return dspy.LM(model=model_name, max_tokens=512, temperature=0.2)


# ---- Signatures
class AnswerSig(dspy.Signature):
    """Answer the question using the provided context. Keep it concise."""

    context: str = dspy.InputField()
    question: str = dspy.InputField()
    answer: str = dspy.OutputField(desc="short answer")


# ---- Program (baseline: retrieval → compact context → answer)
class RAGAnswer(dspy.Module):
    def __init__(self):
        super().__init__()
        self.gen = dspy.Predict(AnswerSig)

    def forward(self, question: str, tag: str):
        limits = load_limits(tag)
        qs = build_channel_queries(question, tag)
        # For now, use empty vector - the retrieval system will handle this safely
        rows = run_fused_query(
            qs["short"],
            qs["title"],
            qs["bm25"],
            qvec=[],  # empty vector for now
            tag=tag,
            k=limits["shortlist"],
            return_components=True,
        )
        rows = mmr_rerank(
            rows, alpha=float(os.getenv("MMR_ALPHA", "0.85")), per_file_penalty=0.10, k=limits["shortlist"]
        )
        rows = per_file_cap(rows, cap=int(os.getenv("PER_FILE_CAP", "5")))[: limits["topk"]]
        context, _meta = build_reader_context(rows, question, tag, compact=bool(int(os.getenv("READER_COMPACT", "1"))))
        out = self.gen(context=context, question=question)
        return dspy.Prediction(answer=out.answer)


# ---- Metric (SQuAD-style F1)
def _norm(s):
    s = (s or "").lower().strip()
    s = __import__("re").sub(r"[^a-z0-9\s]", " ", s)
    s = __import__("re").sub(r"\s+", " ", s)
    return s


def f1(pred, golds):
    p = _norm(pred)
    best = 0.0
    for g in golds:
        g = _norm(g)
        pt = p.split()
        gt = g.split()
        if not pt and not gt:
            return 1.0
        if not pt or not gt:
            continue
        cs = sum(min(pt.count(t), gt.count(t)) for t in set(pt))
        if cs == 0:
            continue
        pr = cs / len(pt)
        rc = cs / len(gt)
        best = max(best, 2 * pr * rc / (pr + rc))
    return best


# ---- Data loaders
def load_jsonl(path):
    return [json.loads(l) for l in open(path, "r", encoding="utf-8") if l.strip()]


def to_examples(rows):
    # rows should include: id/case_id (ignored here), query, tag, answers
    ex = []
    for r in rows:
        q = r["query"]
        tag = r.get("tag", "rag_qa_single")
        answers = r.get("answers", [])
        ex.append(dspy.Example(question=q, tag=tag, answers=answers).with_inputs("question", "tag"))
    return ex


# ---- Compile (Teleprompt) and export
def compile_and_save(dev_path="evals/dspy/dev.jsonl", out_dir="artifacts/dspy"):
    dspy.settings.configure(lm=_lm())
    os.makedirs(out_dir, exist_ok=True)
    dev = to_examples(load_jsonl(dev_path))
    prog = RAGAnswer()

    # Teleprompter: BootstrapFewShot is a robust default
    from dspy.teleprompt import BootstrapFewShot

    def metric(example, pred, trace=None):
        return f1(pred.answer, example.answers)

    tele = BootstrapFewShot(
        metric=metric,
        max_bootstrapped_demos=min(4, max(2, len(dev) // 3)),
        max_labeled_demos=min(8, max(4, len(dev) // 2)),
    )
    compiled = tele.compile(prog, trainset=dev)

    # Persist program
    compiled_path = os.path.join(out_dir, "rag_answer_compiled.json")
    # DSPy 3.0 uses different save method
    try:
        compiled.save(compiled_path)
    except AttributeError:
        # Fallback for different DSPy versions
        import pickle

        with open(compiled_path, "wb") as f:
            pickle.dump(compiled, f)
    print(f"[DSPy] saved compiled program → {compiled_path}")


if __name__ == "__main__":
    compile_and_save()
