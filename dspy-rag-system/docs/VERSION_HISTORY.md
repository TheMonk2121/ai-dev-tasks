# Version History

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Complete version history and changelog for DSPy RAG system | Checking system updates or understanding changes | Review recent changes or plan next version |



## TL;DR

- Tracks notable changes to the DSPy RAG system.
- Highlights security, reliability, and integration milestones.

## v0.3.1-rc3

- Core hardening: database resilience, connection pooling, retry logic
- Production monitoring: health checks, OpenTelemetry, alerts
- Dashboard security hardening and watch-folder stability polling
- Central retry wrapper with configurable exponential backoff
- Enhanced DSPy RAG: pre-RAG and post-RAG logic
- VectorStore performance: pooling, caching, bulk ops
- Watch folder security: command injection prevention, stability polling
- Metadata extractor: schema validation, regex safety, date parsing cache
- Document processor: UUID-based IDs, PyMuPDF integration, security validation

## v0.3.0

- Enhanced DSPy integration with pre/post-RAG logic
- Mission dashboard with real-time WebSocket updates

## v0.2.x

- CSV ingestion support and vector enhancements
- Error recovery and retry wrapper foundations
