# Memory Context System Architecture Benchmark Results

Generated: 2025-08-31T14:29:00.981869

## 📊 Summary

### MISTRAL-7B
- **Accuracy Improvement**: 16.0%
- **Token Reduction**: -51.3%
- **Structure A Accuracy**: 0.750
- **Structure B Accuracy**: 0.870
- **Structure A Tokens**: 119
- **Structure B Tokens**: 180

### MIXTRAL-8X7B
- **Accuracy Improvement**: 6.1%
- **Token Reduction**: -51.3%
- **Structure A Accuracy**: 0.820
- **Structure B Accuracy**: 0.870
- **Structure A Tokens**: 119
- **Structure B Tokens**: 180

### GPT-4O
- **Accuracy Improvement**: 3.4%
- **Token Reduction**: -51.3%
- **Structure A Accuracy**: 0.880
- **Structure B Accuracy**: 0.910
- **Structure A Tokens**: 119
- **Structure B Tokens**: 180

## 🎯 Recommendations

✅ **YAML front-matter improves accuracy by 16.0% on mistral-7b**
   → Implement YAML front-matter for HIGH priority files

🤔 **YAML front-matter shows 6.1% improvement on mixtral-8x7b**
   → Consider YAML front-matter for critical files only

⏭️ **YAML front-matter shows minimal improvement (3.4%) on gpt-4o**
   → Keep HTML comments for simplicity

## 📋 Detailed Results

| Structure | Model | Accuracy | Latency | Input Tokens | Output Tokens | Context Efficiency |
|-----------|-------|----------|---------|--------------|---------------|-------------------|
| A | mistral-7b | 0.750 | 0.74s | 119 | 35 | 0.015 |
| A | mixtral-8x7b | 0.820 | 0.74s | 119 | 35 | 0.004 |
| A | gpt-4o | 0.880 | 0.74s | 119 | 35 | 0.001 |
| B | mistral-7b | 0.870 | 0.86s | 180 | 54 | 0.022 |
| B | mixtral-8x7b | 0.870 | 0.86s | 180 | 54 | 0.006 |
| B | gpt-4o | 0.910 | 0.86s | 180 | 54 | 0.001 |
