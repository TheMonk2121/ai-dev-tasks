# Memory Context System Architecture Research

## 🎯 Research Sprint Overview

**Duration**: 4 development days
**Branch**: `exp/memory-arch`
**Focus**: Optimize memory hierarchy for different AI model capabilities (7B vs 70B)

## 📋 Research Questions

### 1. Hierarchy Depth vs. Token Budge
- What is the optimal folder/priority granularity for 7B (8k ctx) vs 70B (32k ctx) models?
- How can we bootstrap in ≤1k tokens for 7B while allowing 70B to exploit richer links?

### 2. Explicit vs. Implicit Metadata
- When does YAML front-matter materially outperform HTML comments for retrieval accuracy?
- Could dual-encoding (front-matter + hidden comment fallback) be auto-generated?

### 3. Resilience Over Time
- How do we version or alias files so semantic embeddings don't break when filenames change?
- What migration patterns minimize "orphan chunks" in vector DBs?

### 4. Overflow Handling
- Best summarization/compression heuristics when context > 8k
- Sliding-window vs. memory-cache vs. hierarchy summarizer

### 5. Model-Specific Adaptation
- What metadata or chunk sizing should change for Mistral 7B vs Mixtral 8×7B vs GPT-4o?

## 🚀 Deliverables

| Deliverable | Description | ETA | Status |
|-------------|-------------|-----|--------|
| A. Literature digest | 2-page summary of cognitive-science & AI-retrieval papers | 1 day | todo |
| B. Benchmark harness | Script for testing memory structures across models | 2 days | todo |
| C. Design recommendations | Updated 400_memory-context-guide.md with optimal patterns | 0.5 day | todo |
| D. Proof-of-concept PR | Implement new front-matter on one HIGH file | 0.5 day | todo |

## 🧪 Benchmark Framework

### Test Structures
- **Structure A**: Flat list + HTML comments (current)
- **Structure B**: Three-tier hierarchy + YAML front-matter (proposed)

### Models to Tes
- Mistral 7B Instruct (8k context)
- Mixtral 8×7B (32k context)
- GPT-4o (128k context)

### Metrics to Collec
- **Accuracy**: Retrieval F1 score
- **Latency**: Response time in seconds
- **Token Usage**: Input/output token counts
- **Context Efficiency**: Tokens used vs. context available

## 📊 Success Criteria

### Primary Metrics
- **Retrieval F1 improvement ≥10%** on 7B models
- **Reduced token usage** while maintaining accuracy
- **Improved resilience** to file structure changes

### Secondary Metrics
- **Context utilization efficiency** (tokens used / context available)
- **Cross-model consistency** (same accuracy across model sizes)
- **Migration resilience** (performance after file renames)

## 🔬 Hypothesis Testing

### Hypothesis 1: YAML Front-Matter Performance
```
We believe a YAML front-matter + 512-token chunk
will improve retrieval F1 by ≥10% on 7B models.
We'll know it's true if benchmark shows F1 > 0.85
vs current baseline of 0.75.
```

### Hypothesis 2: Hierarchy Depth Optimization
```
We believe a three-tier hierarchy (HIGH/MEDIUM/LOW)
will reduce token usage by ≥20% while maintaining accuracy.
We'll know it's true if token usage < 6k for 7B models
vs current baseline of 7.5k.
```

### Hypothesis 3: Overflow Handling
```
We believe a sliding-window summarizer will maintain
accuracy with context overflow (>8k tokens).
We'll know it's true if F1 degradation < 5% at 12k tokens
vs baseline performance at 8k tokens.
```

## 🛠️ Implementation Plan

### Phase 1: Literature Review (Day 1)
- [ ] Research cognitive science papers on memory hierarchy
- [ ] Review AI retrieval papers on chunking and metadata
- [ ] Analyze context overflow handling techniques
- [ ] Document findings in `500_memory-arch-literature.md`

### Phase 2: Benchmark Development (Days 2-3)
- [ ] Create `scripts/memory_benchmark.py`
- [ ] Implement test structures A and B
- [ ] Set up model testing framework
- [ ] Create baseline measurements

### Phase 3: Design Recommendations (Day 4 AM)
- [ ] Update `400_memory-context-guide.md`
- [ ] Document optimal patterns
- [ ] Create migration guidelines
- [ ] Define model-specific adaptations

### Phase 4: Proof of Concept (Day 4 PM)
- [ ] Implement YAML front-matter on `100_cursor-memory-context.md`
- [ ] Add summarizer fallback for overflow
- [ ] Test with benchmark harness
- [ ] Document results

## 📚 Related Files

<!-- SYSTEM_FILES: 400_system-overview.md -->
<!-- WORKFLOW_FILES: 001_create-prd.md, 002_generate-tasks.md, 003_process-task-list.md -->