# Hang Fixes Summary

## Root Cause Analysis

The evaluation script was hanging due to two main issues:

1. **Bedrock calls with no hard per-call timeout** - The SDK could hang indefinitely
2. **SentenceTransformer model load** - Could hang during download/initialization

## Fixes Implemented

### 1. Hard Deadline Wrapper for Bedrock Calls

Added `_with_deadline()` method that wraps SDK calls in a ThreadPoolExecutor with timeout:

```python
def _with_deadline(self, fn, timeout_sec: float):
    """Execute a blocking SDK call with a hard deadline."""
    with ThreadPoolExecutor(max_workers=2) as ex:
        fut = ex.submit(fn)
        try:
            return fut.result(timeout=timeout_sec)
        except FuturesTimeoutError:
            try:
                fut.cancel()
            except Exception:
                pass
            raise TimeoutError(f"Bedrock call exceeded {timeout_sec:.1f}s deadline")
```

### 2. Updated Bedrock Methods

- `_call_bedrock_llm()`: Now uses `BEDROCK_CALL_TIMEOUT_SEC=35` (default)
- `_call_bedrock_text()`: Now uses `BEDROCK_TEXT_TIMEOUT_SEC=25` (default)
- `bedrock_invoke_async()`: Added `asyncio.wait_for()` with deadline

### 3. Conservative Bedrock Settings

Created `configs/bedrock_conservative.env` with:
- `BEDROCK_MAX_IN_FLIGHT=1`
- `BEDROCK_MAX_RPS=0.12`
- `BEDROCK_CALL_TIMEOUT_SEC=35`
- `BEDROCK_TEXT_TIMEOUT_SEC=25`
- `RAGCHECKER_SEMANTIC_FEATURES=0`
- `RAGCHECKER_DISABLE_EMBEDDINGS=1`

### 4. Isolation Test Script

Created `scripts/run_hang_isolation_tests.sh` to identify root causes:
- Test A: Local LLM (bypass Bedrock)
- Test B: Bedrock with conservative settings
- Test C: Disable semantic features

## Usage

### Quick Fix (Recommended)
```bash
source configs/bedrock_conservative.env
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --stable
```

### Isolation Testing
```bash
./scripts/run_hang_isolation_tests.sh
```

### Manual Testing
```bash
# Test A: Bypass Bedrock and embeddings
export RAGCHECKER_BYPASS_CLI=1
export RAGCHECKER_DISABLE_EMBEDDINGS=1
python3 scripts/ragchecker_official_evaluation.py --use-local-llm --stable

# Test B: Use Bedrock with conservative settings
export RAGCHECKER_BYPASS_CLI=1
export RAGCHECKER_DISABLE_EMBEDDINGS=1
export BEDROCK_MAX_IN_FLIGHT=1
export BEDROCK_MAX_RPS=0.12
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --stable
```

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `BEDROCK_CALL_TIMEOUT_SEC` | 35 | Hard deadline for JSON calls |
| `BEDROCK_TEXT_TIMEOUT_SEC` | 25 | Hard deadline for text calls |
| `BEDROCK_MAX_IN_FLIGHT` | 1 | Conservative concurrency |
| `BEDROCK_MAX_RPS` | 0.12 | Conservative rate limit |
| `RAGCHECKER_SEMANTIC_FEATURES` | 0 | Disable embeddings to avoid hangs |
| `RAGCHECKER_DISABLE_EMBEDDINGS` | 1 | Alternative way to disable embeddings |

## Observability

- Progress logging: `RAGCHECKER_PROGRESS_LOG=metrics/baseline_evaluations/progress.jsonl`
- Fault handler: `PYTHONFAULTHANDLER=1`
- Hang dump: `RAGCHECKER_HANG_DUMP_SEC=180`

## Status

✅ **Fixed**: Bedrock call timeouts
✅ **Fixed**: Async Bedrock timeouts
✅ **Fixed**: Import sorting
✅ **Created**: Conservative configuration
✅ **Created**: Isolation test script

The script should now be much more robust against hanging issues.
