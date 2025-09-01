# RAG Retrieval Tuning Protocol

## TL;DR

**Industry-grade methodology for systematically balancing precision and recall in RAG systems without over-optimization.** This protocol provides a repeatable, deterministic approach to tuning retrieval weights, thresholds, and reranking that prevents the precision/recall yo-yo effect.

**Key Principle**: Optimize precision first until answers stop hallucinating, then recover recall without losing that precision.

---

## 📋 **Table of Contents**

1. [Protocol Overview](#protocol-overview)
2. [Intent Declaration & Objectives](#intent-declaration--objectives)
3. [Coverage Strategy](#coverage-strategy)
4. [Hybrid Retrieval Implementation](#hybrid-retrieval-implementation)
5. [Pre-filtering & Reranking](#pre-filtering--reranking)
6. [Answer Packing & Evidence](#answer-packing--evidence)
7. [Gates & Ratchet System](#gates--ratchet-system)
8. [Tuning Algorithm](#tuning-algorithm)
9. [Integration with Development Workflow](#integration-with-development-workflow)
10. [Quick Reference](#quick-reference)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 **Protocol Overview**

### **What This Protocol Solves**

- **Precision/Recall Trade-off**: Systematic approach to balancing both metrics
- **Over-optimization**: Prevents tuning one metric at the expense of another
- **Intent Mismatch**: Different query types get different optimization strategies
- **Coverage Gaps**: Systematic approach to indexing and chunking
- **Hallucination**: Evidence-first answers with proper grounding

### **When to Use This Protocol**

- **After major system changes** that affect retrieval performance
- **When precision/recall metrics are imbalanced**
- **Before production deployment** to ensure optimal performance
- **During iterative development** to maintain performance standards
- **When adding new content types** or changing chunking strategies

### **Expected Outcomes**

- **Systematic improvement** in both precision and recall
- **Intent-aware optimization** for different query types
- **Evidence-based answers** with reduced hallucination
- **Repeatable tuning process** that can be applied consistently
- **Performance gates** that prevent regression

---

## 🎭 **Intent Declaration & Objectives**

### **Core Principle**

**Different query types have different objectives.** Optimize each intent separately rather than using a single global metric.

### **Intent Classification Matrix**

| **Intent** | **Primary Objective** | **Secondary Objective** | **Success Check** | **Example Queries** |
|------------|----------------------|-------------------------|-------------------|---------------------|
| **File/Config Lookup** | P@5 (Precision at 5) | NDCG@10 | Top answer includes exact snippet + filepath | "What's in pyproject.toml?", "Show me the database config" |
| **Troubleshoot/How-to** | NDCG@10 | R@20 (Recall at 20) | At least 2 distinct evidence chunks | "How do I fix this error?", "What's the setup process?" |
| **Project/Status** | P@5 | Faithfulness | Evidence-first summary + no contradictions | "What's the current project status?", "What are the backlog priorities?" |
| **Multi-hop/Advanced** | R@50 | Faithfulness | Correct chain across files + no hallucinated links | "How does the memory system integrate with DSPy?" |

### **Why Intent-Aware Optimization Matters**

- **Config queries** need high precision to avoid wrong settings
- **How-to queries** need good recall to find all relevant steps
- **Status queries** need faithfulness to avoid contradictions
- **Multi-hop queries** need broad recall to connect information

---

## 📚 **Coverage Strategy**

### **File Types to Index**

#### **Primary Content (Always Index)**
- **`.md` files**: Documentation and guides
- **`.py` files**: Source code with docstrings
- **`.yaml/.toml/.json`**: Configuration files
- **`.ini` files**: Legacy configuration
- **`.env.example`**: Environment templates

#### **Secondary Content (Index for Coverage)**
- **`.github/workflows/*`**: CI/CD configuration
- **`Makefile`**: Build and automation scripts
- **`scripts/*`**: Utility and automation scripts
- **`pyproject.toml`**: Python project configuration
- **`requirements*.txt`**: Dependencies

#### **Why This Matters**

- **Case 11 (0.0% F1)**: Configuration queries fail because config files aren't indexed
- **Coverage gaps**: Missing file types create blind spots in retrieval
- **Intent routing**: Different file types serve different query intents

### **Chunking Strategy**

#### **Prose Content (Documentation, README)**
- **Size**: 350-600 tokens
- **Overlap**: 20-25%
- **Rationale**: Large enough for context, small enough for precision

#### **Code Content (Source files, docstrings)**
- **Size**: 400-800 tokens
- **Overlap**: 15-20%
- **Rationale**: Preserve function/class boundaries

#### **Configuration Content (.yaml, .toml, .json)**
- **Strategy**: Line-block chunks (20-40 lines)
- **Preserve**: Keys and surrounding comments
- **Rationale**: Maintain configuration context

#### **Normalization Strategy**
- **Code/IDs**: Keep original case (e.g., `POSTGRES_DSN`)
- **Prose fields**: Lowercase for search
- **Exact matching**: Add feature for identifier matches

---

## 🔄 **Hybrid Retrieval Implementation**

### **Two-List Approach**

Return two separate result lists, then fuse them:

```python
# Step 1: Generate separate lists
bm25_results = bm25_search(query, top_k=80)
vector_results = vector_search(query, top_k=80)

# Step 2: Fuse using weighted RRF
fused_results = weighted_rrf_fusion(bm25_results, vector_results,
                                  λ_lex=0.6, λ_sem=0.4)
```

### **Initial Parameters (Restore Recall)**

```python
# Start with these to restore recall
BM25_topk = 80      # Was 10, too restrictive
Vector_topk = 80    # Was 10, too restrictive
λ_lex = 0.6         # Favor lexical for config
λ_sem = 0.4         # Semantic for conceptual queries
```

### **Weighted RRF Fusion Formula**

```
fused(d) = λ_lex / (k + rank_bm25(d)) + λ_sem / (k + rank_vector(d))
```

Where:
- `k = 60` (start here)
- `λ_lex = 0.6` (lexical weight)
- `λ_sem = 0.4` (semantic weight)

### **Why Hybrid Retrieval Works**

- **BM25**: Excellent for exact matches, configuration, file paths
- **Vector Search**: Great for conceptual similarity, semantic understanding
- **Fusion**: Combines strengths, reduces weaknesses
- **Weighted**: Can favor lexical for config queries, semantic for conceptual

---

## 🎛️ **Pre-filtering & Reranking**

### **Lightweight Pre-filter (Don't Starve Recall)**

```python
# Keep top 50 by fused score
candidates = fused_results[:50]

# Only drop if BOTH conditions are met
for candidate in candidates:
    if (cosine_similarity < 0.15 AND
        candidate not in bm25_top_20):
        drop_candidate(candidate)
```

**Rationale**: This keeps literal matches even when cosine similarity is low.

### **Reranking (Precision Lever)**

```python
# Cross-encoder on top 50 fused
reranked = cross_encoder_rerank(candidates[:50])

# Select top 6-8 for final answer
final_candidates = reranked[:8]

# Final score calculation
final_score = 0.7 * rerank_score + 0.3 * fused_score
```

**Parameters**:
- `α = 0.7` (rerank weight) - good default
- `rerank_top_n = 6-8` (final selection)

### **Tiebreakers**

```python
# Apply in order of priority
if scores_equal(candidate1, candidate2):
    # 1. Exact term bonus
    if has_exact_terms(candidate1):
        return candidate1

    # 2. Same-file proximity
    if same_file_proximity(candidate1) > same_file_proximity(candidate2):
        return candidate1

    # 3. Code-block bonus for tech queries
    if is_tech_query(query) and has_code_block(candidate1):
        return candidate1
```

---

## 📦 **Answer Packing & Evidence**

### **MMR Diversity (Avoid Near-Duplicates)**

```python
# Maximum Marginal Relevance
selected = mmr_diversity(final_candidates, λ=0.7)

# Cap context at 1200-1600 tokens
packed_context = pack_with_token_limit(selected, max_tokens=1600)
```

**Why MMR matters**: Prevents returning multiple nearly identical chunks that waste context space.

### **Evidence-First Answer Format**

```python
# Show highest-scoring snippet first
answer = f"""🔍 **Evidence from {file_path}**
```{file_extension}
{snippet}
```

**Summary**: {summary}"""
```

**Benefits**:
- **Faithfulness**: Shows actual evidence first
- **Transparency**: Users can verify sources
- **Debugging**: Easy to see what the system found

### **Context Optimization**

```python
# Require top-2 evidence chunks
if len(high_quality_chunks) < 2:
    lower_thresholds()

# Ban low-score filler
filtered_chunks = [c for c in chunks if c.score > min_threshold]
```

---

## 🚦 **Gates & Ratchet System**

### **Two-Green Rule**

**Never raise thresholds after just one good run.** Wait for two consecutive green runs before tightening.

### **Start Gates (Global)**

```python
# Initial gates - must pass these
GATES = {
    "precision": 0.12,      # Your current 0.149 passes
    "recall": 0.15,         # Force recall improvement
    "faithfulness": 0.60    # Maintain answer quality
}
```

### **Ratchet Path (Progressive Tightening)**

#### **Phase 1: Restore Recall**
- **Target**: Recall 0.15 → 0.35-0.45
- **Method**: Open funnel (raise top_k, lower cutoffs)
- **Expected**: Precision may drop slightly (acceptable)

#### **Phase 2: Improve Precision**
- **Target**: Precision 0.12 → 0.20-0.30
- **Method**: Optimize reranking and thresholds
- **Expected**: Maintain recall gains

#### **Phase 3: Push Both**
- **Target**: Recall 0.45 → 0.60-0.70, F1 0.30 → 0.40
- **Method**: Fine-tune all parameters
- **Expected**: Balanced improvement

### **Intent-Specific Gates**

```python
INTENT_GATES = {
    "config": {
        "p_at_5": 0.30,
        "faithfulness": 0.70
    },
    "how_to": {
        "ndcg_at_10": 0.60,
        "recall": 0.60
    },
    "status": {
        "p_at_5": 0.25,
        "faithfulness": 0.65
    }
}
```

---

## 🔧 **Tuning Algorithm**

### **Coordinate Ascent (Fast & Deterministic)**

No black-box optimization needed. Use systematic grid search:

```python
# Step 1: Fix rerank α=0.7, sweep retrieval parameters
for bm25_topk in [40, 80]:
    for vec_topk in [40, 80, 120]:
        test_recall_without_precision_drop()

# Step 2: Sweep fusion weights
for λ_lex in [0.5, 0.6, 0.7]:
    λ_sem = 1 - λ_lex
    test_p_at_5_and_ndcg_average()

# Step 3: Sweep pre-filter cosine
for cosine_min in [0.10, 0.15, 0.20]:
    maximize_f1()

# Step 4: If precision still < 0.20, adjust reranking
if precision < 0.20:
    α = 0.8
    rerank_top_n = 5-6
```

### **Why This Approach Works**

- **Deterministic**: Same input always produces same output
- **Fast**: No expensive optimization loops
- **Interpretable**: You know exactly what changed
- **Reversible**: Easy to rollback if needed

---

## 🔄 **Integration with Development Workflow**

### **Where This Fits in Your Process**

```
1. [PRD Creation](001_create-prd.md) → Define performance requirements
2. [Task Generation](002_generate-tasks.md) → Break down optimization work
3. [Development Roadmap](004_development-roadmap.md) → Plan tuning phases
4. **[RAG Tuning Protocol](005_rag-tuning-protocol.md)** → Execute optimization
5. [Task Implementation](003_process-task-list.md) → Deploy improvements
```

### **When to Apply During Development**

#### **Phase 1: Initial Setup**
- **After**: Basic RAG system is working
- **Goal**: Establish baseline performance
- **Focus**: Coverage and basic retrieval

#### **Phase 2: Performance Tuning**
- **After**: System has good coverage
- **Goal**: Optimize precision/recall balance
- **Focus**: Hybrid retrieval and reranking

#### **Phase 3: Production Optimization**
- **After**: Core performance is good
- **Goal**: Fine-tune for production use
- **Focus**: Gates, monitoring, and maintenance

### **Integration with Existing Tools**

- **RAGChecker**: Use for evaluation and metric tracking
- **Baseline Metrics**: Monitor performance over time
- **Pre-commit Hooks**: Enforce performance gates
- **Development Workflows**: Include tuning in task planning

---

## 📖 **Quick Reference**

### **Immediate Actions (Today)**

```python
# 1. Restore recall
BM25_topk = 80
Vector_topk = 80
λ_lex = 0.6, λ_sem = 0.4

# 2. Lower pre-filter thresholds
cosine_min = 0.15
bm25_min = 0.0

# 3. Implement evidence-first answers
show_snippet_first()
show_file_path()
```

### **Weekly Tuning Checklist**

- [ ] Check precision/recall balance
- [ ] Verify intent-specific performance
- [ ] Monitor faithfulness scores
- [ ] Check coverage gaps
- [ ] Update performance gates

### **Monthly Optimization**

- [ ] Run coordinate ascent tuning
- [ ] Update chunking strategies
- [ ] Review indexing coverage
- [ ] Optimize reranking parameters
- [ ] Validate against industry benchmarks

---

## 🚨 **Troubleshooting**

### **Common Issues & Solutions**

#### **Precision Too Low (< 0.12)**
```python
# Solutions
1. Increase rerank weight (α = 0.7 → 0.8)
2. Lower rerank_top_n (8 → 6)
3. Tighten pre-filter thresholds
4. Improve chunking quality
```

#### **Recall Too Low (< 0.15)**
```python
# Solutions
1. Increase top_k values (80 → 120)
2. Lower pre-filter thresholds
3. Add more content types to indexing
4. Improve chunking coverage
```

#### **Faithfulness Too Low (< 0.60)**
```python
# Solutions
1. Implement evidence-first answers
2. Require multiple evidence chunks
3. Improve reranking quality
4. Add hard negatives to evaluation
```

### **Performance Regression**

#### **If Recent Changes Hurt Performance**
```python
# Immediate actions
1. Revert to last known good configuration
2. Check what changed (indexing, chunking, parameters)
3. Apply changes incrementally
4. Test after each change
```

#### **Preventing Future Regressions**
```python
# Long-term solutions
1. Implement performance gates
2. Use two-green rule consistently
3. Monitor metrics continuously
4. Document all parameter changes
```

---

## 📚 **References & Further Reading**

### **Industry Standards**
- **Hybrid Retrieval**: [ArXiv: Hybrid Retrieval Models](https://arxiv.org/abs/2010.01195)
- **Adaptive Re-ranking**: [ArXiv: Adaptive Re-Ranking](https://arxiv.org/abs/2208.08942)
- **Chunking Optimization**: [ArXiv: Chunking Strategies](https://arxiv.org/abs/2505.08445)

### **Related Documentation**
- [RAGChecker Evaluation Guide](../metrics/baseline_evaluations/README.md)
- [Baseline Metrics Collection](../scripts/baseline_metrics_collector.py)
- [Performance Monitoring](../scripts/comprehensive_system_monitor.py)

### **Integration Points**
- [Development Roadmap](004_development-roadmap.md)
- [Task Implementation](003_process-task-list.md)
- [Performance Gates](../metrics/baseline_evaluations/RED_LINE_ENFORCEMENT_RULES.md)

---

## 🎯 **Success Metrics**

### **Short-term (1-2 weeks)**
- **Recall**: 0.099 → 0.25-0.35 (+15-25 pts)
- **Precision**: Maintain ≥ 0.12
- **F1**: 0.112 → 0.18-0.25
- **Case 11**: 0.0% → 15-25% F1

### **Medium-term (1-2 months)**
- **Recall**: 0.35 → 0.45-0.55
- **Precision**: 0.12 → 0.20-0.25
- **F1**: 0.25 → 0.30-0.35
- **Faithfulness**: +10-15 pts

### **Long-term (3-6 months)**
- **Recall**: 0.55 → 0.65-0.75 (baseline target)
- **Precision**: 0.25 → 0.20-0.35 (baseline target)
- **F1**: 0.35 → 0.30-0.40 (baseline target)
- **Industry Standard**: Achieve production-ready performance

---

## 🔄 **Maintenance & Updates**

### **When to Update This Protocol**

- **After major system changes** that affect retrieval
- **When new research** provides better approaches
- **Based on performance data** from your system
- **Industry best practices** evolve

### **How to Update**

1. **Document the change** with rationale
2. **Test the change** against your metrics
3. **Update the protocol** with new parameters
4. **Validate** that performance improves
5. **Communicate** changes to the team

---

## 🎉 **Conclusion**

This **RAG Retrieval Tuning Protocol** provides a systematic, industry-grade approach to optimizing your RAG system's performance. By following this methodology:

- **You'll avoid the precision/recall yo-yo effect**
- **Performance improvements will be systematic and measurable**
- **Your system will achieve production-ready metrics**
- **Tuning will become a repeatable, predictable process**

**Remember**: Optimize precision first until answers stop hallucinating, then recover recall without losing that precision. Use the gates and ratchet system to prevent over-optimization.

**Start with Phase 1 (Coverage & Hybrid Retrieval) today, and you'll see immediate improvements in your recall while maintaining precision.**

---

*Last Updated: August 31, 2025*
*Protocol Version: 1.0*
*Status: Active - Ready for Implementation*
