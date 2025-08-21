<!-- MEMORY_CONTEXT: MEDIUM - Script optimization and performance tuning guide -->
# Script Optimization Guide

## 🔎 TL;DR {#tldr}

| what this file is | read when | do next |
|---|---|---|
| Guide for optimizing script performance and efficiency | Optimizing scripts or improving performance | Apply
optimization techniques to current scripts |




## 🎯 **Top 5 Critical Scripts & Optimization Priorities**

### 1. **`update_cursor_memory.py`** - Memory Context Updater
**Current Issues**: Re-parses entire backlog file, no caching, sequential processing
**Optimization Priority**: 🔥 **HIGH** (run after every change)

#### **Immediate Optimizations**:
```python
# Add caching layer
import hashlib
import pickle
from pathlib import Path

class CachedBacklogParser:
    def __init__(self, cache_dir: Path = Path(".cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)

    def get_backlog_hash(self, file_path: Path) -> str:
        """Get file hash for cache invalidation."""
        return hashlib.md5(file_path.read_bytes()).hexdigest()

    def load_cached_priorities(self, file_path: Path) -> Optional[List[Dict]]:
        """Load cached priorities if valid."""
        cache_file = self.cache_dir / f"backlog_priorities_{file_path.name}.pkl"
        hash_file = self.cache_dir / f"backlog_hash_{file_path.name}.txt"

        if cache_file.exists() and hash_file.exists():
            current_hash = self.get_backlog_hash(file_path)
            cached_hash = hash_file.read_text().strip()

            if current_hash == cached_hash:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)

        return None

    def save_cached_priorities(self, file_path: Path, priorities: List[Dict]):
        """Save priorities to cache."""
        cache_file = self.cache_dir / f"backlog_priorities_{file_path.name}.pkl"
        hash_file = self.cache_dir / f"backlog_hash_{file_path.name}.txt"

        with open(cache_file, 'wb') as f:
            pickle.dump(priorities, f)

        hash_file.write_text(self.get_backlog_hash(file_path))
```

## **Performance Targets**:
- **Current**: ~2-3 seconds
- **Target**: <500ms (80% improvement)
- **Memory**: <50MB

### 2. **`quick_conflict_check.py`** - Fast Conflict Detection
**Current Issues**: Sequential checks, no early exit, redundant git calls
**Optimization Priority**: 🔥 **HIGH** (pre-commit hook)

#### **Immediate Optimizations**:
```python
# Parallel execution with early exit
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing

class OptimizedConflictChecker:
    def __init__(self):
        self.max_workers = min(8, multiprocessing.cpu_count() + 2)

    def run_parallel_checks(self) -> Dict[str, bool]:
        """Run all checks in parallel with early exit on critical failures."""
        checks = [
            ("merge_markers", self.check_merge_markers),
            ("backup_files", self.check_backup_files),
            ("package_conflicts", self.check_package_conflicts),
        ]

        results = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_check = {
                executor.submit(check_func): check_name
                for check_name, check_func in checks
            }

            for future in as_completed(future_to_check):
                check_name = future_to_check[future]
                try:
                    results[check_name] = future.result()
                    # Early exit on critical failure
                    if not results[check_name] and check_name in ["merge_markers", "backup_files"]:
                        # Cancel remaining tasks
                        for f in future_to_check:
                            f.cancel()
                        break
                except Exception as e:
                    results[check_name] = False
                    self.log(f"Check {check_name} failed: {e}", "ERROR")

        return results
```

## **Performance Targets**:
- **Current**: ~5-10 seconds
- **Target**: <2 seconds (75% improvement)
- **Memory**: <30MB

### 3. **`process_tasks.py`** - Task Execution Engine
**Current Issues**: Large file size, complex state management, no batching
**Optimization Priority**: 📈 **MEDIUM** (core execution)

#### **Immediate Optimizations**:
```python
# Database connection pooling
import sqlite3
from contextlib import contextmanager

class OptimizedTaskManager:
    def __init__(self, db_path: str = ".cache/tasks.db"):
        self.db_path = db_path
        self._connection_pool = []
        self._max_connections = 5

    @contextmanager
    def get_db_connection(self):
        """Get database connection from pool."""
        if self._connection_pool:
            conn = self._connection_pool.pop()
        else:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row

        try:
            yield conn
        finally:
            if len(self._connection_pool) < self._max_connections:
                self._connection_pool.append(conn)
            else:
                conn.close()

    def batch_process_tasks(self, tasks: List[Task], batch_size: int = 10):
        """Process tasks in batches for better performance."""
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            with self.get_db_connection() as conn:
                # Process batch in single transaction
                conn.execute("BEGIN TRANSACTION")
                try:
                    for task in batch:
                        self._process_single_task(conn, task)
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    raise e
```

## **Performance Targets**:
- **Current**: ~10-30 seconds for full execution
- **Target**: <5 seconds (80% improvement)
- **Memory**: <100MB

### 4. **`doc_coherence_validator.py`** - Documentation Validator
**Current Issues**: Large file size, regex compilation overhead, sequential file processing
**Optimization Priority**: 📈 **MEDIUM** (documentation quality)

#### **Immediate Optimizations**:
```python
# Pre-compiled regex patterns and parallel processing
import re
from concurrent.futures import ThreadPoolExecutor

class OptimizedDocValidator:
    def __init__(self):
        # Pre-compile all regex patterns at module level
        self.patterns = {
            'heading_increment': re.compile(r"^#{1,6}\s"),
            'heading_style': re.compile(r"^(#{1,6}|\={3,}|\-{3,})"),
            'list_indent': re.compile(r"^\s*[-*+]\s"),
            'trailing_spaces': re.compile(r"\s+$"),
            'hard_tabs': re.compile(r"\t"),
            'line_length': re.compile(r"^.{121,}$"),
            'cross_reference': re.compile(r"<!--\s*([A-Z_]+):\s*([^>]+)\s*-->"),
            'file_reference': re.compile(r"`([^`]+\.md)`"),
        }

        self.max_workers = min(16, multiprocessing.cpu_count() * 2)

    def validate_files_parallel(self, files: List[Path]) -> Dict[Path, List[str]]:
        """Validate multiple files in parallel."""
        results = {}

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._validate_single_file, file): file
                for file in files
            }

            for future in as_completed(future_to_file):
                file = future_to_file[future]
                try:
                    results[file] = future.result()
                except Exception as e:
                    results[file] = [f"Validation error: {e}"]

        return results

    def _validate_single_file(self, file_path: Path) -> List[str]:
        """Validate a single file using pre-compiled patterns."""
        content = file_path.read_text()
        issues = []

        # Use pre-compiled patterns for faster matching
        for pattern_name, pattern in self.patterns.items():
            matches = pattern.findall(content)
            if matches:
                issues.append(f"{pattern_name}: {len(matches)} issues found")

        return issues
```

## **Performance Targets**:
- **Current**: ~15-45 seconds for full validation
- **Target**: <5 seconds (85% improvement)
- **Memory**: <80MB

### 5. **`conflict_audit.py`** - Comprehensive Conflict Audit
**Current Issues**: Sequential execution, no progress reporting, redundant checks
**Optimization Priority**: ⭐ **LOW** (deep audit tool)

#### **Immediate Optimizations**:
```python
# Modular checks with progress reporting
from tqdm import tqdm
import asyncio

class OptimizedConflictAuditor:
    def __init__(self):
        self.check_modules = {
            'dependencies': self.check_dependency_conflicts,
            'circular': self.check_circular_dependencies,
            'imports': self.check_import_conflicts,
            'configs': self.check_config_conflicts,
        }

    async def run_audit_with_progress(self, modules: List[str] = None) -> Dict[str, Any]:
        """Run audit with progress bars and parallel execution."""
        if modules is None:
            modules = list(self.check_modules.keys())

        results = {}

        # Create progress bar
        with tqdm(total=len(modules), desc="Running conflict audit") as pbar:
            # Run checks in parallel
            tasks = []
            for module in modules:
                if module in self.check_modules:
                    task = asyncio.create_task(self._run_check_async(module))
                    tasks.append((module, task))

            # Collect results with progress updates
            for module, task in tasks:
                try:
                    results[module] = await task
                    pbar.update(1)
                    pbar.set_postfix({"current": module})
                except Exception as e:
                    results[module] = {"error": str(e)}
                    pbar.update(1)

        return results

    async def _run_check_async(self, module: str) -> Dict[str, Any]:
        """Run a single check asynchronously."""
        check_func = self.check_modules[module]

        # Run CPU-bound checks in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, check_func)
```

## **Performance Targets**:
- **Current**: ~30-90 seconds for full audit
- **Target**: <15 seconds (75% improvement)
- **Memory**: <120MB

## 🚀 **Implementation Strategy**

### **Phase 1: Quick Wins (1-2 days)**
1. **Add caching to `update_cursor_memory.py`**
2. **Implement parallel processing in `quick_conflict_check.py`**
3. **Add progress bars to long-running scripts**
4. **Create performance benchmark baseline**

### **Phase 2: Core Optimizations (3-5 days)**
1. **Optimize `process_tasks.py` with connection pooling**
2. **Implement pre-compiled regex in `doc_coherence_validator.py`**
3. **Add modular checks to `conflict_audit.py`**
4. **Create automated performance monitoring**

### **Phase 3: Advanced Optimizations (1 week)**
1. **Implement async processing where applicable**
2. **Add intelligent caching with TTL**
3. **Create script dependency graph for optimal execution order**
4. **Implement resource usage monitoring**

## 📊 **Performance Monitoring**

### **Baseline Your Current Performance**:
```bash
# Run performance benchmark
python scripts/performance_benchmark.py --iterations 5

# Monitor specific script
python scripts/performance_benchmark.py --script update_cursor_memory --iterations 10
```

## **Track Improvements**:
```bash
# Save baseline results
python scripts/performance_benchmark.py --save baseline_results.json

# After optimizations, compare
python scripts/performance_benchmark.py --save optimized_results.json
```

## 🔧 **Quick Optimization Checklist**

- [ ] **Caching**: Add file hash-based caching for expensive operations
- [ ] **Parallelization**: Use ThreadPoolExecutor for I/O-bound tasks
- [ ] **Early Exit**: Stop processing on critical failures
- [ ] **Progress Reporting**: Add tqdm progress bars for long operations
- [ ] **Memory Management**: Implement proper cleanup and connection pooling
- [ ] **Regex Optimization**: Pre-compile patterns at module level
- [ ] **Batch Processing**: Process items in batches instead of one-by-one
- [ ] **Resource Monitoring**: Track memory and CPU usage

## 📈 **Expected Performance Gains**

| Script | Current Time | Target Time | Improvement |
|--------|-------------|-------------|-------------|
| `update_cursor_memory.py` | 2-3s | <500ms | 80% |
| `quick_conflict_check.py` | 5-10s | <2s | 75% |
| `process_tasks.py` | 10-30s | <5s | 80% |
| `doc_coherence_validator.py` | 15-45s | <5s | 85% |
| `conflict_audit.py` | 30-90s | <15s | 75% |

**Total Time Savings**: ~60-120 seconds per development cycle
**Memory Reduction**: ~50-70% across all scripts
**Developer Experience**: Significantly faster feedback loops

## 🎯 **Next Steps**

1. **Run baseline benchmark**: `python scripts/performance_benchmark.py`
2. **Start with Phase 1 optimizations** (highest impact, lowest effort)
3. **Implement caching layer** for `update_cursor_memory.py`
4. **Add parallel processing** to `quick_conflict_check.py`
5. **Monitor performance improvements** with regular benchmarks

This optimization strategy will significantly improve your development workflow by reducing script execution times and providing faster feedback loops for your AI development ecosystem.
