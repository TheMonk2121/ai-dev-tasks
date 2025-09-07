# 🚨 Residual Risk Register

**Top 5 production risks and mitigation strategies**

## 1. Config Drift Risk

### **Risk Description**
Configuration parameters drift over time, leading to performance degradation or system instability.

### **Mitigation Strategy**
- **Manifests + Active-Pointer**: All configurations versioned with CONFIG_HASH
- **CI Gate**: Fails build if manifests missing or mismatched
- **Automated Validation**: Health checks validate configuration consistency

### **Monitoring**
- Configuration hash validation in every evaluation
- Automated drift detection in CI/CD pipeline
- Alert on configuration parameter changes

### **Response Plan**
1. Detect drift via manifest comparison
2. Rollback to last known good configuration
3. Investigate root cause of drift
4. Update configuration locking mechanisms

---

## 2. Cache Contamination Risk

### **Risk Description**
Evaluation cache contains data from previous runs, contaminating current evaluation results.

### **Mitigation Strategy**
- **EVAL_DISABLE_CACHE=1**: All evaluations run with cache disabled
- **Canary Check**: Retrieved contexts must span current RUN only
- **Cache Isolation**: Separate cache namespaces per evaluation run

### **Monitoring**
- Cache hit rate monitoring (should be 0% in evaluations)
- Retrieved context run ID validation
- Cache size and content validation

### **Response Plan**
1. Clear all caches immediately
2. Re-run evaluation with fresh cache
3. Validate retrieved contexts match current run
4. Investigate cache isolation mechanisms

---

## 3. Prefix Leakage to Sparse Risk

### **Risk Description**
Evaluation prefixes leak into BM25 text, contaminating sparse retrieval results.

### **Mitigation Strategy**
- **Never allow bm25_text to start with prefix**: Strict validation
- **Fail build if >0 rows**: Zero tolerance for prefix leakage
- **Dual-text storage**: Separate embedding_text and bm25_text fields

### **Monitoring**
- Automated prefix detection in BM25 text
- Build failure on any prefix leakage detected
- Regular audits of text field isolation

### **Response Plan**
1. Immediate build failure on detection
2. Audit all text fields for prefix contamination
3. Re-ingest data with proper text isolation
4. Update ingestion pipeline to prevent future leakage

---

## 4. Embedder Swap/Resize Risk

### **Risk Description**
Embedding model changes or dimension changes break vector similarity calculations.

### **Mitigation Strategy**
- **Guarded by vector(…) column type**: Database enforces dimension consistency
- **Assert emb_dim before insert**: Validation at ingestion time
- **Rebuild IVFFLAT/HNSW on change**: Index reconstruction required

### **Monitoring**
- Embedding dimension validation
- Vector similarity score distribution monitoring
- Index health checks after model changes

### **Response Plan**
1. Detect dimension mismatch via validation
2. Rebuild vector indexes with new dimensions
3. Re-ingest all embeddings with new model
4. Validate similarity score distributions

---

## 5. Reranker Cold Starts Risk

### **Risk Description**
Reranker model cold starts during traffic cause latency spikes and timeouts.

### **Mitigation Strategy**
- **Prewarm at process start**: Load model before serving traffic
- **Alert if download happens during traffic**: Monitor model loading
- **Model caching**: Keep model in memory between requests

### **Monitoring**
- Model loading time monitoring
- Reranker latency distribution tracking
- Cold start detection and alerting

### **Response Plan**
1. Detect cold start via latency spike
2. Prewarm model in background
3. Route traffic to warm instances
4. Scale up warm instances if needed

---

## Risk Monitoring Dashboard

### **Real-Time Alerts**
- Configuration drift detection
- Cache contamination alerts
- Prefix leakage detection
- Embedding dimension mismatches
- Reranker cold start detection

### **Daily Health Checks**
- Configuration consistency validation
- Cache isolation verification
- Text field isolation audit
- Vector index health check
- Model availability verification

### **Weekly Risk Assessment**
- Review all risk metrics
- Update mitigation strategies
- Test response procedures
- Document lessons learned
- Update risk register

---

## Emergency Response Procedures

### **Critical Risk Response (All Risks)**
1. **Immediate**: Stop affected systems
2. **Assess**: Determine scope and impact
3. **Mitigate**: Apply appropriate response plan
4. **Validate**: Verify fix effectiveness
5. **Document**: Record incident and resolution

### **Escalation Matrix**
- **Level 1**: Automated detection and response
- **Level 2**: On-call engineer intervention
- **Level 3**: Team lead escalation
- **Level 4**: Management notification

### **Communication Plan**
- **Internal**: Team Slack channel for incidents
- **External**: Status page for service disruptions
- **Post-Incident**: Detailed incident report within 24 hours

---

## Risk Register Maintenance

### **Review Schedule**
- **Monthly**: Risk assessment and mitigation review
- **Quarterly**: Risk register update and strategy refresh
- **Annually**: Complete risk register overhaul

### **Update Triggers**
- New system components added
- Significant configuration changes
- Performance threshold changes
- New threat vectors identified

### **Documentation Requirements**
- All risks must have clear mitigation strategies
- Response plans must be tested and validated
- Monitoring must be automated and reliable
- Escalation procedures must be documented

---

**Last Updated**: 2025-09-07  
**Next Review**: 2025-10-07  
**Owner**: Production Engineering Team
