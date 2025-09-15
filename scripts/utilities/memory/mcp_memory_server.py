#!/usr/bin/env python3
from __future__ import annotations

"""
MCP Memory Server for Cursor Integration

Provides MCP endpoints for:
- Memory system queries (LTST, unified orchestrator)
- Database access (with new schema)
- Precision evaluation tools
- Project context retrieval
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
import uuid
from collections.abc import Mapping
from pathlib import Path
from typing import cast

import httpx
import psycopg2
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel, ConfigDict, Field, field_validator

# Ensure repository root is on sys.path for absolute package imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
# Import systems using absolute package paths to avoid implicit relative imports
try:
    from scripts.utilities.cursor_working_integration import (  # type: ignore[reportMissingImports]
        CursorWorkingIntegration,
    )
    from scripts.utilities.unified_memory_orchestrator import (  # type: ignore[reportMissingImports]
        UnifiedMemoryOrchestrator,
    )

    memory_orchestrator = UnifiedMemoryOrchestrator()
    cursor_integration_class = CursorWorkingIntegration
except Exception as e:  # pragma: no cover - import environment dependent
    logging.warning(f"Could not import memory systems: {e}")
    memory_orchestrator = None
    cursor_integration_class = None

# Thread-specific integration instances
cursor_integrations = {}


def get_cursor_integration(thread_id: str | None = None) -> CursorWorkingIntegration | None:
    """Get or create a thread-specific cursor integration instance."""
    if not cursor_integration_class:
        return None

    # Use provided thread_id or create a new one
    if not thread_id:
        thread_id = f"thread_{uuid.uuid4().hex[:8]}"

    # Get or create integration for this thread
    if thread_id not in cursor_integrations:
        cursor_integrations[thread_id] = cursor_integration_class()
        # Override the thread_id to match our key
        cursor_integrations[thread_id].thread_id = thread_id
        # Ensure the thread exists in the database
        if not cursor_integrations[thread_id]._ensure_thread_exists(thread_id):
            print(f"❌ Failed to ensure thread {thread_id} exists, removing from cache")
            del cursor_integrations[thread_id]
            return None

    return cursor_integrations[thread_id]


app = FastAPI(title="MCP Memory Server", version="1.0.0")

# CORS middleware for Cursor integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class MemoryQuery(BaseModel):
    """Memory query request with Pydantic validation."""

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    query: str = Field(..., min_length=1, max_length=10000, description="Query text for memory search")
    role: str = Field(default="general", description="Role context for the query")
    max_tokens: int = Field(default=1200, ge=100, le=8000, description="Maximum tokens for response")
    systems: list[str] = Field(default=["ltst", "cursor", "prime"], description="Memory systems to query")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate query is not empty."""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        """Validate role is valid."""
        valid_roles = {"general", "planner", "implementer", "researcher", "coder"}
        if v not in valid_roles:
            raise ValueError(f"Role must be one of: {valid_roles}")
        return v

    @field_validator("systems")
    @classmethod
    def validate_systems(cls, v: list[str]) -> list[str]:
        """Validate memory systems are valid."""
        valid_systems = {"ltst", "cursor", "go_cli", "prime"}
        for system in v:
            if system not in valid_systems:
                raise ValueError(f"Invalid system: {system}. Must be one of: {valid_systems}")
        return v


class MemoryResponse(BaseModel):
    """Memory query response with Pydantic validation."""

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    success: bool = Field(..., description="Whether the query was successful")
    # Use a general JSON-compatible payload mapping (covariant value type)
    data: Mapping[str, object] = Field(default_factory=dict, description="Response data")
    error: str | None = Field(None, description="Error message if unsuccessful")


class HealthResponse(BaseModel):
    """Health check response with Pydantic validation."""

    model_config: ConfigDict = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )

    status: str = Field(..., description="Service status")
    timestamp: float = Field(..., ge=0.0, description="Response timestamp")
    service: str = Field(..., min_length=1, description="Service name")
    uptime: str = Field(..., description="Service uptime")
    error_rate: float = Field(..., ge=0.0, le=1.0, description="Error rate (0.0-1.0)")
    cache_hit_rate: float = Field(..., ge=0.0, le=1.0, description="Cache hit rate (0.0-1.0)")


# Global state
# Use monotonic clock for robust uptime tracking
start_time = time.monotonic()
request_count = 0
error_count = 0
# Track running jobs with a minimally-typed dictionary
JOBS: dict[str, dict[str, object]] = {}
JOB_DIR = Path(tempfile.gettempdir()) / "mcp_jobs"
JOB_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Cursor integration"""
    uptime_seconds = time.monotonic() - start_time
    uptime_str = f"{int(uptime_seconds // 86400)} days, {int((uptime_seconds % 86400) // 3600)}:{int((uptime_seconds % 3600) // 60):02d}:{int(uptime_seconds % 60):02d}"

    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        service="mcp-memory-rehydrator",
        uptime=uptime_str,
        error_rate=error_count / max(request_count, 1),
        cache_hit_rate=0.0,  # TODO: Implement caching
    )


@app.get("/logs")
async def proxy_logs_recent():
    """Proxy recent logs from the local log monitor (port 8001)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("http://localhost:8001/logs")
            return PlainTextResponse(content=resp.text, status_code=resp.status_code)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Log proxy error: {e}")


@app.get("/logs/mcp-server")
async def proxy_logs_mcp_server():
    """Proxy MCP-specific logs from the local log monitor (port 8001)."""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get("http://localhost:8001/logs/mcp-server")
            return PlainTextResponse(content=resp.text, status_code=resp.status_code)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Log proxy error: {e}")


@app.get("/logs/stream")
async def proxy_logs_stream():
    """Stream logs via server-sent events from the local log monitor (port 8001)."""

    async def event_stream():
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("GET", "http://localhost:8001/logs/stream") as r:
                    async for chunk in r.aiter_bytes():
                        if chunk:
                            yield chunk
        except Exception as e:
            yield f"event: error\ndata: {str(e)}\n\n".encode()

    return StreamingResponse(event_stream(), media_type="text/event-stream")


class MCPToolCall(BaseModel):
    tool_name: str
    # Arguments accepted by tools; use Mapping for covariance
    arguments: Mapping[str, object]


@app.post("/mcp/tools/call", response_model=MemoryResponse)
async def call_mcp_tool(request: MCPToolCall):
    """MCP tool call endpoint for Cursor integration"""
    global request_count, error_count
    request_count += 1

    try:
        if request.tool_name == "query_memory":
            return await query_memory_system(request.arguments)
        elif request.tool_name == "get_project_context":
            return await get_project_context(request.arguments)
        elif request.tool_name == "get_hot_context":
            return await get_hot_context(request.arguments)
        elif request.tool_name == "search_hot_memory":
            return await search_hot_memory(request.arguments)
        elif request.tool_name == "pin_hot_item":
            return await pin_hot_item(request.arguments)
        elif request.tool_name == "run_precision_eval":
            return await run_precision_evaluation(request.arguments)
        elif request.tool_name == "process_files":
            return await process_files(request.arguments)
        elif request.tool_name == "analyze_file_content":
            return await analyze_file_content(request.arguments)
        elif request.tool_name == "get_precision_eval_status":
            return await get_precision_eval_status(request.arguments)
        elif request.tool_name == "get_precision_eval_result":
            return await get_precision_eval_result(request.arguments)
        elif request.tool_name == "cancel_precision_eval":
            return await cancel_precision_eval(request.arguments)
        elif request.tool_name == "capture_user_query":
            return await capture_user_query(request.arguments)
        elif request.tool_name == "capture_ai_response":
            return await capture_ai_response(request.arguments)
        elif request.tool_name == "get_conversation_stats":
            return await get_conversation_stats(request.arguments)
        elif request.tool_name == "record_chat_history":
            return await record_chat_history(request.arguments)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {request.tool_name}")
    except Exception as e:
        error_count += 1
        return MemoryResponse(success=False, data={}, error=str(e))


async def query_memory_system(args: Mapping[str, object]) -> MemoryResponse:
    """Query the memory system using unified orchestrator"""
    if not memory_orchestrator:
        return MemoryResponse(success=False, data={}, error="Memory system not available")

    try:
        query = cast(str, args.get("query", ""))
        role = cast(str, args.get("role", "general"))
        systems = cast(list[str], args.get("systems", ["ltst", "cursor", "prime"]))

        # Use your existing unified orchestrator
        ltst_result = memory_orchestrator.get_ltst_memory(query, role)
        cursor_result = memory_orchestrator.get_cursor_memory(query, role)
        go_cli_result = memory_orchestrator.get_go_cli_memory(query)

        bundle = {
            "ltst": ltst_result,
            "cursor": cursor_result,
            "go_cli": go_cli_result,
            "query": query,
            "role": role,
            "systems": systems,
        }

        return MemoryResponse(success=True, data=bundle, error=None)
    except Exception as e:
        return MemoryResponse(success=False, data={}, error=f"Memory query failed: {str(e)}")


async def get_project_context(args: Mapping[str, object]) -> MemoryResponse:
    """Get current project context and status"""
    try:
        _ = args  # silence unused parameter in strict type checking
        # Read key project files
        project_root = Path(__file__).parent.parent

        context = {
            "project_root": str(project_root),
            "current_backlog": None,
            "system_overview": None,
            "memory_context": None,
        }

        # Try to read key files
        try:
            with open(project_root / "000_core" / "000_backlog.md") as f:
                context["current_backlog"] = f.read()[:1000] + "..." if len(f.read()) > 1000 else f.read()
        except:
            pass

        try:
            with open(project_root / "400_guides" / "400_system-overview.md") as f:
                context["system_overview"] = f.read()[:1000] + "..." if len(f.read()) > 1000 else f.read()
        except:
            pass

        try:
            with open(project_root / "100_memory" / "100_cursor-memory-context.md") as f:
                context["memory_context"] = f.read()[:1000] + "..." if len(f.read()) > 1000 else f.read()
        except:
            pass

        return MemoryResponse(success=True, data=context, error=None)
    except Exception as e:
        return MemoryResponse(success=False, data={}, error=f"Failed to get project context: {str(e)}")


async def run_precision_evaluation(args: Mapping[str, object]) -> MemoryResponse:
    """Run precision evaluation using your existing scripts"""
    try:
        config_file = cast(str, args.get("config_file", "configs/precision_evidence_filter.env"))
        script = cast(str, args.get("script", "scripts/run_precision_with_env_file.sh"))
        async_mode = bool(args.get("async", True))
        timeout_sec = int(cast(int | str, args.get("timeout_sec", 1800)))
        fast_mode = args.get("fast_mode")

        project_root = Path(__file__).parent.parent

        if async_mode:
            job_id = str(uuid.uuid4())
            stdout_path = Path(tempfile.gettempdir()) / f"precision_eval_{job_id}.out"
            stderr_path = Path(tempfile.gettempdir()) / f"precision_eval_{job_id}.err"

            env = os.environ.copy()
            if fast_mode is not None:
                env["RAGCHECKER_FAST_MODE"] = "1" if str(fast_mode).lower() in ("1", "true") else "0"
            env["RAGCHECKER_ENV_FILE"] = config_file
            env["RAGCHECKER_LOCK_ENV"] = "1"

            stdout_f = open(stdout_path, "w")
            stderr_f = open(stderr_path, "w")
            proc = subprocess.Popen(
                [script, config_file],
                cwd=project_root,
                stdout=stdout_f,
                stderr=stderr_f,
                text=True,
                env=env,
            )

            JOBS[job_id] = {
                "pid": proc.pid,
                "process": proc,
                "stdout": str(stdout_path),
                "stderr": str(stderr_path),
                "start_time": asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0,
                "timeout_sec": timeout_sec,
                "config_file": config_file,
                "script": script,
            }

            # Persist job metadata so status/result survive process reloads
            try:
                with open(JOB_DIR / f"{job_id}.json", "w", encoding="utf-8") as jf:
                    json.dump(
                        {
                            "pid": proc.pid,
                            "stdout": str(stdout_path),
                            "stderr": str(stderr_path),
                            "config_file": config_file,
                            "script": script,
                        },
                        jf,
                    )
            except Exception:
                pass

            return MemoryResponse(success=True, data={"job_id": job_id, "status": "running"}, error=None)
        else:
            env = os.environ.copy()
            if fast_mode is not None:
                env["RAGCHECKER_FAST_MODE"] = "1" if str(fast_mode).lower() in ("1", "true") else "0"
            env["RAGCHECKER_ENV_FILE"] = config_file
            env["RAGCHECKER_LOCK_ENV"] = "1"

            result = subprocess.run(
                [script, config_file],
                capture_output=True,
                text=True,
                cwd=project_root,
                timeout=timeout_sec,
                env=env,
            )

            return MemoryResponse(
                success=result.returncode == 0,
                data={
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode,
                    "config_file": config_file,
                },
                error=result.stderr if result.returncode != 0 else None,
            )
    except Exception as e:
        return MemoryResponse(success=False, data={}, error=f"Precision evaluation failed: {str(e)}")


async def get_precision_eval_status(args: Mapping[str, object]) -> MemoryResponse:
    raw_job_id = args.get("job_id")
    if not raw_job_id:
        return MemoryResponse(success=False, data={}, error="Unknown job_id")
    job_id = cast(str, raw_job_id)

    if job_id in JOBS:
        job: dict[str, object] = JOBS[job_id]
        proc = cast(subprocess.Popen[str], job["process"])  # type: ignore[type-arg]
        running = proc.poll() is None
        returncode = None if running else proc.returncode
    else:
        # Fallback to persisted store
        try:
            with open(JOB_DIR / f"{job_id}.json", encoding="utf-8") as jf:
                job = cast(dict[str, object], json.load(jf))
        except Exception:
            return MemoryResponse(success=False, data={}, error="Unknown job_id")
        # Try to determine liveness via PID (POSIX)
        running = False
        returncode = None
        try:
            pid = int(cast(int | str, job.get("pid", 0)))
            _ = os.kill(pid, 0)
            running = True
        except Exception:
            running = False

    def tail(path: str, nbytes: int = 2048) -> str:
        try:
            with open(path, "rb") as f:
                _ = f.seek(0, os.SEEK_END)
                size = f.tell()
                _ = f.seek(max(0, size - nbytes))
                return f.read().decode("utf-8", errors="replace")
        except Exception:
            return ""

    return MemoryResponse(
        success=True,
        data={
            "job_id": job_id,
            "running": running,
            "returncode": returncode,
            "stdout_tail": tail(str(job.get("stdout", ""))),
            "stderr_tail": tail(str(job.get("stderr", ""))),
        },
        error=None,
    )


async def get_precision_eval_result(args: Mapping[str, object]) -> MemoryResponse:
    raw_job_id = args.get("job_id")
    if not raw_job_id:
        return MemoryResponse(success=False, data={}, error="Unknown job_id")
    job_id = cast(str, raw_job_id)

    rc: int | None = None
    job: dict[str, object] | None = None
    if job_id in JOBS:
        job = JOBS[job_id]
        proc = cast(subprocess.Popen[str], job["process"])  # type: ignore[type-arg]
        if proc.poll() is None:
            return MemoryResponse(success=False, data={}, error="Job is still running")
        rc = proc.returncode
    else:
        try:
            with open(JOB_DIR / f"{job_id}.json", encoding="utf-8") as jf:
                job = cast(dict[str, object], json.load(jf))
        except Exception:
            return MemoryResponse(success=False, data={}, error="Unknown job_id")

    try:
        assert job is not None
        with open(str(job.get("stdout", "")), encoding="utf-8", errors="replace") as fo:
            stdout = fo.read()
        with open(str(job.get("stderr", "")), encoding="utf-8", errors="replace") as fe:
            stderr = fe.read()
    except Exception as e:
        stdout, stderr = "", f"Failed to read logs: {e}"

    return MemoryResponse(
        success=(rc == 0) if rc is not None else True,
        data={
            "job_id": job_id,
            "returncode": rc,
            "stdout": stdout,
            "stderr": stderr,
            "config_file": job.get("config_file") if job else None,
        },
        error=stderr if rc not in (None, 0) else None,
    )


async def cancel_precision_eval(args: Mapping[str, object]) -> MemoryResponse:
    raw_job_id = args.get("job_id")
    job_id = cast(str, raw_job_id) if raw_job_id is not None else None
    if not job_id or job_id not in JOBS:
        return MemoryResponse(success=False, data={}, error="Unknown job_id")
    job = JOBS[job_id]
    proc = cast(subprocess.Popen[str], job["process"])  # type: ignore[type-arg]
    if proc.poll() is None:
        try:
            proc.terminate()
            return MemoryResponse(success=True, data={"job_id": job_id, "status": "terminated"}, error=None)
        except Exception as e:
            return MemoryResponse(success=False, data={}, error=str(e))
    return MemoryResponse(success=True, data={"job_id": job_id, "status": "already_finished"}, error=None)


async def process_files(args: Mapping[str, object]) -> MemoryResponse:
    """Process a list of repo-relative file paths and return lightweight analyses.

    arguments:
      - paths: list[str] (repo-relative)
      - max_bytes: int (optional, default 4000)
    """
    try:
        project_root = Path(__file__).parent.parent
        raw_paths = args.get("paths")
        max_bytes = int(cast(int | str, args.get("max_bytes", 4000)))
        if not isinstance(raw_paths, list) or not raw_paths:
            raise HTTPException(status_code=400, detail="paths must be a non-empty list of repo-relative paths")
        paths = [str(p) for p in raw_paths]

        results: list[dict[str, object]] = []
        for rel in paths:
            p = (project_root / rel).resolve()
            try:
                # Security: ensure path stays within project
                if project_root not in p.parents and p != project_root:
                    raise HTTPException(status_code=400, detail=f"Path escapes project root: {rel}")
                if not p.exists() or not p.is_file():
                    results.append({"path": rel, "error": "not_found"})
                    continue
                size = int(p.stat().st_size)
                sample = p.read_bytes()[:max_bytes]
                try:
                    text = sample.decode("utf-8", errors="replace")
                except Exception:
                    text = "<binary>"
                line_count = text.count("\n") + 1 if text and text != "<binary>" else None
                results.append(
                    {
                        "path": rel,
                        "size": size,
                        "preview": text,
                        "line_count": line_count,
                        "truncated": size > max_bytes,
                    }
                )
            except HTTPException as he:
                raise he
            except Exception as e:
                results.append({"path": rel, "error": str(e)})

        return MemoryResponse(success=True, data={"files": results}, error=None)
    except HTTPException as he:
        return MemoryResponse(success=False, data={}, error=str(he.detail))
    except Exception as e:
        return MemoryResponse(success=False, data={}, error=f"process_files failed: {str(e)}")


async def analyze_file_content(args: Mapping[str, object]) -> MemoryResponse:
    """Analyze a single dropped file provided as raw content.

    arguments:
      - filename: str
      - content: str (UTF-8 text)
      - max_preview_chars: int (optional, default 2000)
    """
    try:
        filename = cast(str, args.get("filename", "unknown"))
        content_obj = args.get("content")
        if content_obj is None:
            raise HTTPException(status_code=400, detail="content is required")
        content = cast(str, content_obj)
        max_preview_chars = int(cast(int | str, args.get("max_preview_chars", 2000)))

        preview = content[:max_preview_chars]
        line_count = content.count("\n") + 1
        file_ext = Path(filename).suffix.lower()

        # Simple heuristics for type
        is_code = file_ext in {".py", ".js", ".ts", ".go", ".rs", ".java", ".sh", ".yaml", ".yml", ".json"}
        is_markdown = file_ext in {".md"}

        # Very light “insights” for sidecar display
        insights: Mapping[str, object] | dict[str, object] = {
            "filename": filename,
            "ext": file_ext,
            "lines": line_count,
            "chars": len(content),
            "is_code": is_code,
            "is_markdown": is_markdown,
        }

        return MemoryResponse(success=True, data={"preview": preview, "insights": insights}, error=None)
    except HTTPException as he:
        return MemoryResponse(success=False, data={}, error=str(he.detail))
    except Exception as e:
        return MemoryResponse(success=False, data={}, error=f"analyze_file_content failed: {str(e)}")


# ---- Hot memory (48h warm pool) tools ----
async def get_hot_context(args: Mapping[str, object]) -> MemoryResponse:
    """Fetch recent high-signal context for the last N hours (default 48)."""
    try:
        hours = int(cast(int | str, args.get("hours", 48)))
        limit = int(cast(int | str, args.get("limit", 20)))
        # Placeholder implementation: defer to unified orchestrator if available
        data = {
            "decisions": [],
            "files": [],
            "todos": [],
            "note": "hot-context provider not wired; returning empty scaffold",
        }
        if memory_orchestrator is not None:
            func = getattr(memory_orchestrator, "get_hot_context", None)
            if callable(func):
                data = func(hours=hours, limit=limit)
        return MemoryResponse(success=True, data={"hours": hours, "limit": limit, "bundle": data}, error=None)
    except Exception as e:
        return MemoryResponse(success=False, data={}, error=str(e))


async def search_hot_memory(args: Mapping[str, object]) -> MemoryResponse:
    """Search within the recent hot memory window by keyword."""
    try:
        query = str(args.get("query", "")).strip()
        hours = int(cast(int | str, args.get("hours", 48)))
        if not query:
            return MemoryResponse(success=False, data={}, error="query is required")
        hits = []
        if memory_orchestrator is not None:
            func = getattr(memory_orchestrator, "search_hot_context", None)
            if callable(func):
                hits = func(query=query, hours=hours)
        return MemoryResponse(success=True, data={"query": query, "hours": hours, "hits": hits}, error=None)
    except Exception as e:
        return MemoryResponse(success=False, data={}, error=str(e))


async def pin_hot_item(args: Mapping[str, object]) -> MemoryResponse:
    """Pin a specific item into the hot pool for a limited TTL."""
    try:
        item_id = cast(str | None, args.get("item_id"))
        ttl_hours = int(cast(int | str, args.get("ttl_hours", 48)))
        if not item_id:
            return MemoryResponse(success=False, data={}, error="item_id is required")
        ok = False
        if memory_orchestrator is not None:
            func = getattr(memory_orchestrator, "pin_hot_item", None)
            if callable(func):
                ok = bool(func(item_id=item_id, ttl_hours=ttl_hours))
        return MemoryResponse(success=True, data={"item_id": item_id, "ttl_hours": ttl_hours, "pinned": ok}, error=None)
    except Exception as e:
        return MemoryResponse(success=False, data={}, error=str(e))


@app.get("/mcp/tools")
async def list_tools() -> dict[str, object]:
    """List available MCP tools for Cursor"""
    return {
        "tools": [
            {
                "name": "query_memory",
                "description": "Query the memory system using unified orchestrator",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "role": {"type": "string", "default": "general"},
                        "systems": {"type": "array", "items": {"type": "string"}},
                        "max_tokens": {"type": "integer", "default": 1200},
                    },
                },
            },
            {
                "name": "get_hot_context",
                "description": "Fetch recent high-signal context for the last N hours (default 48)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "hours": {"type": "integer", "default": 48},
                        "limit": {"type": "integer", "default": 20},
                    },
                },
            },
            {
                "name": "search_hot_memory",
                "description": "Search within the recent hot memory window by keyword",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "hours": {"type": "integer", "default": 48},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "pin_hot_item",
                "description": "Pin a specific item into the hot pool for a limited TTL",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "item_id": {"type": "string"},
                        "ttl_hours": {"type": "integer", "default": 48},
                    },
                    "required": ["item_id"],
                },
            },
            {
                "name": "get_project_context",
                "description": "Get current project context and status",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "include_backlog": {"type": "boolean", "default": True},
                        "include_system_overview": {"type": "boolean", "default": True},
                    },
                },
            },
            {
                "name": "run_precision_eval",
                "description": "Run precision evaluation using existing scripts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "config_file": {"type": "string", "default": "configs/precision_evidence_filter.env"},
                        "script": {"type": "string", "default": "scripts/run_precision_with_env_file.sh"},
                        "async": {"type": "boolean", "default": True},
                        "timeout_sec": {"type": "integer", "default": 1800},
                        "fast_mode": {"type": "boolean"},
                    },
                },
            },
            {
                "name": "process_files",
                "description": "Read and summarize repo-relative files (for drag/drop paths)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "paths": {"type": "array", "items": {"type": "string"}},
                        "max_bytes": {"type": "integer", "default": 4000},
                    },
                    "required": ["paths"],
                },
            },
            {
                "name": "analyze_file_content",
                "description": "Analyze a dropped file's raw content and return a preview + insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"},
                        "content": {"type": "string"},
                        "max_preview_chars": {"type": "integer", "default": 2000},
                    },
                    "required": ["content"],
                },
            },
            {
                "name": "get_precision_eval_status",
                "description": "Check status of an async precision evaluation job",
                "inputSchema": {"type": "object", "properties": {"job_id": {"type": "string"}}, "required": ["job_id"]},
            },
            {
                "name": "get_precision_eval_result",
                "description": "Fetch outputs of a finished precision evaluation job",
                "inputSchema": {"type": "object", "properties": {"job_id": {"type": "string"}}, "required": ["job_id"]},
            },
            {
                "name": "cancel_precision_eval",
                "description": "Cancel a running precision evaluation job",
                "inputSchema": {"type": "object", "properties": {"job_id": {"type": "string"}}, "required": ["job_id"]},
            },
            {
                "name": "capture_user_query",
                "description": "Capture a user query from Cursor conversation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "metadata": {"type": "object", "default": {}},
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "capture_ai_response",
                "description": "Capture an AI response from Cursor conversation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "response": {"type": "string"},
                        "query_turn_id": {"type": "string"},
                        "metadata": {"type": "object", "default": {}},
                    },
                    "required": ["response"],
                },
            },
            {
                "name": "get_conversation_stats",
                "description": "Get conversation statistics",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                },
            },
            {
                "name": "record_chat_history",
                "description": "MANDATORY: Record conversation history automatically after every AI response",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "user_input": {"type": "string"},
                        "system_output": {"type": "string"},
                        "project_dir": {"type": "string"},
                        "file_operations": {"type": "string"},
                        "llm_name": {"type": "string"},
                        "thread_id": {"type": "string"},
                    },
                    "required": ["user_input", "system_output", "project_dir"],
                },
            },
        ]
    }


async def capture_user_query(args: Mapping[str, object]) -> MemoryResponse:
    """Capture a user query from Cursor conversation"""
    try:
        # Get thread-specific integration
        thread_id = cast(str | None, args.get("thread_id"))
        cursor_integration = get_cursor_integration(thread_id)

        if not cursor_integration:
            return MemoryResponse(success=False, data={}, error="Cursor integration not available")

        query = cast(str, args.get("query", ""))
        metadata = cast(dict[str, str | int | float | bool | None], args.get("metadata", {}))

        if not query:
            return MemoryResponse(success=False, data={}, error="Query is required")

        # Async path using psycopg3 pool for concurrency safety
        try:
            from scripts.utilities.memory.db_async_pool import ensure_thread_exists, insert_user_turn, pool

            async with pool.connection() as conn:  # type: ignore[attr-defined]
                tid = await ensure_thread_exists(conn, cursor_integration.thread_id)
                turn_id, _ = await insert_user_turn(conn, thread_id=tid, content=query, metadata=metadata)
        except Exception as e:
            return MemoryResponse(success=False, data={}, error=str(e))

        if turn_id:
            return MemoryResponse(
                success=True,
                data={
                    "turn_id": turn_id,
                    "message": "User query captured successfully",
                    "session_id": cursor_integration.session_id,
                    "thread_id": cursor_integration.thread_id,
                },
                error=None,
            )
        else:
            return MemoryResponse(success=False, data={}, error="Failed to capture user query")

    except Exception as e:
        return MemoryResponse(success=False, data={}, error=str(e))


async def capture_ai_response(args: Mapping[str, object]) -> MemoryResponse:
    """Capture an AI response from Cursor conversation"""
    try:
        # Get thread-specific integration
        thread_id = cast(str | None, args.get("thread_id"))
        cursor_integration = get_cursor_integration(thread_id)

        if not cursor_integration:
            return MemoryResponse(success=False, data={}, error="Cursor integration not available")

        response = cast(str, args.get("response", ""))
        raw_query_turn_id = args.get("query_turn_id")
        metadata = cast(dict[str, str | int | float | bool | None], args.get("metadata", {}))

        if not response:
            return MemoryResponse(success=False, data={}, error="Response is required")

        if raw_query_turn_id is None:
            return MemoryResponse(success=False, data={}, error="query_turn_id is required")

        query_turn_id = cast(str, raw_query_turn_id)

        # Async parent validation and insert using psycopg3 helpers
        try:
            from scripts.utilities.memory.db_async_pool import insert_ai_turn, pool

            async with pool.connection() as conn:  # type: ignore[attr-defined]
                try:
                    turn_id, _tid, _seq = await insert_ai_turn(
                        conn,
                        parent_turn_id=query_turn_id,
                        content=response,
                        metadata=metadata,
                        status="final",
                        explicit_thread_id=cast(str | None, args.get("thread_id")),
                        allow_supersede=False,
                    )
                except ValueError as ve:
                    code = str(ve)
                    if code in ("unknown_query_turn_id", "query_turn_not_user_role"):
                        return MemoryResponse(success=False, data={"error": code}, error=None)
                    return MemoryResponse(success=False, data={}, error=code)
                except LookupError as le:
                    parts = str(le).split(":")
                    if len(parts) == 3 and parts[0] == "thread_id_mismatch":
                        return MemoryResponse(
                            success=False,
                            data={"error": "thread_id_mismatch", "expected": parts[1], "got": parts[2]},
                            error=None,
                        )
                    return MemoryResponse(success=False, data={}, error=str(le))
                except FileExistsError:
                    return MemoryResponse(
                        success=False,
                        data={"error": "parent_already_answered", "query_turn_id": query_turn_id},
                        error=None,
                    )
        except Exception as e:
            return MemoryResponse(success=False, data={}, error=str(e))

        if turn_id:
            return MemoryResponse(
                success=True,
                data={
                    "turn_id": turn_id,
                    "message": "AI response captured successfully",
                    "session_id": cursor_integration.session_id,
                    "thread_id": cursor_integration.thread_id,
                },
                error=None,
            )
        else:
            return MemoryResponse(success=False, data={}, error="Failed to capture AI response")

    except Exception as e:
        return MemoryResponse(success=False, data={}, error=str(e))


async def get_conversation_stats(args: Mapping[str, object]) -> MemoryResponse:
    """Get conversation statistics"""
    try:
        # Get thread-specific integration
        thread_id = cast(str | None, args.get("thread_id"))
        cursor_integration = get_cursor_integration(thread_id)

        if not cursor_integration:
            return MemoryResponse(success=False, data={}, error="Cursor integration not available")

        stats = cursor_integration.get_session_stats()

        return MemoryResponse(
            success=True,
            data={
                "stats": stats,
                "session_id": cursor_integration.session_id,
                "thread_id": cursor_integration.thread_id,
            },
            error=None,
        )

    except Exception as e:
        return MemoryResponse(success=False, data={}, error=str(e))


async def record_chat_history(args: Mapping[str, object]) -> MemoryResponse:
    """MANDATORY: Record conversation history automatically after every AI response"""
    try:
        # Get thread-specific integration
        thread_id = cast(str | None, args.get("thread_id"))
        cursor_integration = get_cursor_integration(thread_id)

        if not cursor_integration:
            return MemoryResponse(success=False, data={}, error="Cursor integration not available")

        user_input = cast(str, args.get("user_input", ""))
        system_output = cast(str, args.get("system_output", ""))
        project_dir = cast(str, args.get("project_dir", "/Users/danieljacobs/Code/ai-dev-tasks"))
        file_operations = cast(str, args.get("file_operations", ""))
        llm_name = cast(str, args.get("llm_name", "cursor-ai"))

        if not user_input.strip() or not system_output.strip():
            return MemoryResponse(success=False, data={}, error="user_input and system_output are required")

        # Async psycopg3 path for atomic user + AI capture
        try:
            from scripts.utilities.memory.db_async_pool import (
                ensure_thread_exists,
                insert_ai_turn,
                insert_user_turn,
                pool,
            )

            async with pool.connection() as conn:  # type: ignore[attr-defined]
                tid = await ensure_thread_exists(conn, cursor_integration.thread_id)
                query_turn_id, _useq = await insert_user_turn(
                    conn,
                    thread_id=tid,
                    content=user_input,
                    metadata={"source": "auto_record", "project_dir": project_dir, "llm_name": llm_name},
                )
                response_turn_id, _tid, _aseq = await insert_ai_turn(
                    conn,
                    parent_turn_id=query_turn_id,
                    content=system_output,
                    metadata={
                        "source": "auto_record",
                        "project_dir": project_dir,
                        "llm_name": llm_name,
                        "file_operations": file_operations,
                    },
                    status="final",
                    explicit_thread_id=tid,
                    allow_supersede=False,
                )
        except Exception as e:
            return MemoryResponse(success=False, data={}, error=str(e))

        # Also write to .chat_history file for compatibility
        chat_history_file = Path(project_dir) / ".chat_history"
        timestamp = int(time.time())

        # Create or append to .chat_history file
        with open(chat_history_file, "a", encoding="utf-8") as f:
            _ = f.write(f"{timestamp}\n")
            _ = f.write(f"U: {user_input}\n")
            _ = f.write(f"S: {system_output}\n")
            _ = f.write(f"file_op: {file_operations or 'none'}\n")
            _ = f.write(f"{llm_name}\n\n")

        return MemoryResponse(
            success=True,
            data={
                "message": "Chat history recorded successfully",
                "query_turn_id": query_turn_id,
                "response_turn_id": response_turn_id,
                "session_id": cursor_integration.session_id,
                "thread_id": cursor_integration.thread_id,
                "chat_history_file": str(chat_history_file),
                "timestamp": timestamp,
            },
            error=None,
        )

    except Exception as e:
        return MemoryResponse(success=False, data={}, error=str(e))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="MCP Memory Server")
    _ = parser.add_argument("--port", type=int, default=3000, help="Port to run on")
    _ = parser.add_argument("--host", type=str, default="localhost", help="Host to bind to")

    args = parser.parse_args()

    _ = print(f"🚀 Starting MCP Memory Server on {args.host}:{args.port}")
    _ = print(f"📡 Health check: http://{args.host}:{args.port}/health")
    _ = print(f"🔧 MCP tools: http://{args.host}:{args.port}/mcp/tools")
    # Helpful import diagnostics
    _ = print(f"🧩 PYTHONPATH={os.environ.get('PYTHONPATH','')}")
    try:
        _ = print(f"🧭 sys.path[:3]={sys.path[:3]}")
    except Exception:
        pass

    uvicorn.run(app, host=cast(str, args.host), port=cast(int, args.port))
