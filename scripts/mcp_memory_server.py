#!/usr/bin/env python3
"""
MCP Memory Server for Cursor Integration

Provides MCP endpoints for:
- Memory system queries (LTST, unified orchestrator)
- Database access (with new schema)
- Precision evaluation tools
- Project context retrieval
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel

# Add project paths
# sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system" / "src"))  # REMOVED: DSPy venv consolidated into main project
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Import your existing systems
try:
    from ltst_memory_integration import LTSTMemoryIntegration
    from unified_memory_orchestrator import UnifiedMemoryOrchestrator

    memory_orchestrator = UnifiedMemoryOrchestrator()
except ImportError as e:
    logging.warning(f"Could not import memory systems: {e}")
    memory_orchestrator = None
    LTSTMemoryIntegration = None

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
    query: str
    role: str = "general"
    max_tokens: int = 1200
    systems: list[str] = ["ltst", "cursor", "prime"]


class MemoryResponse(BaseModel):
    success: bool
    data: dict[str, Any]
    error: str | None = None


class HealthResponse(BaseModel):
    status: str
    timestamp: float
    service: str
    uptime: str
    error_rate: float
    cache_hit_rate: float


# Global state
# Use monotonic clock for robust uptime tracking
start_time = time.monotonic()
request_count = 0
error_count = 0
JOBS: dict[str, dict[str, Any]] = {}
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
    arguments: dict[str, Any]


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
        else:
            raise HTTPException(status_code=400, detail=f"Unknown tool: {request.tool_name}")
    except Exception as e:
        error_count += 1
        return MemoryResponse(success=False, data={}, error=str(e))


async def query_memory_system(args: dict[str, Any]) -> MemoryResponse:
    """Query the memory system using unified orchestrator"""
    if not memory_orchestrator:
        return MemoryResponse(success=False, data={}, error="Memory system not available")

    try:
        query = args.get("query", "")
        role = args.get("role", "general")
        systems = args.get("systems", ["ltst", "cursor", "prime"])

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

        return MemoryResponse(success=True, data=bundle)
    except Exception as e:
        return MemoryResponse(success=False, data={}, error=f"Memory query failed: {str(e)}")


async def get_project_context(args: dict[str, Any]) -> MemoryResponse:
    """Get current project context and status"""
    try:
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

        return MemoryResponse(success=True, data=context)
    except Exception as e:
        return MemoryResponse(success=False, data={}, error=f"Failed to get project context: {str(e)}")


async def run_precision_evaluation(args: dict[str, Any]) -> MemoryResponse:
    """Run precision evaluation using your existing scripts"""
    try:
        config_file = args.get("config_file", "configs/precision_evidence_filter.env")
        script = args.get("script", "scripts/run_precision_with_env_file.sh")
        async_mode = bool(args.get("async", True))
        timeout_sec = int(args.get("timeout_sec", 1800))
        fast_mode = args.get("fast_mode")

        project_root = Path(__file__).parent.parent

        if async_mode:
            job_id = str(uuid.uuid4())
            stdout_path = Path(tempfile.gettempdir()) / f"precision_eval_{job_id}.out"
            stderr_path = Path(tempfile.gettempdir()) / f"precision_eval_{job_id}.err"

            env = os.environ.copy()
            if fast_mode is not None:
                env["RAGCHECKER_FAST_MODE"] = "1" if str(fast_mode) in ("1", "true", "True") else "0"
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

            return MemoryResponse(success=True, data={"job_id": job_id, "status": "running"})
        else:
            env = os.environ.copy()
            if fast_mode is not None:
                env["RAGCHECKER_FAST_MODE"] = "1" if str(fast_mode) in ("1", "true", "True") else "0"
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


async def get_precision_eval_status(args: dict[str, Any]) -> MemoryResponse:
    job_id = args.get("job_id")
    if not job_id:
        return MemoryResponse(success=False, data={}, error="Unknown job_id")

    if job_id in JOBS:
        job = JOBS[job_id]
        proc: subprocess.Popen = job["process"]
        running = proc.poll() is None
        returncode = None if running else proc.returncode
    else:
        # Fallback to persisted store
        try:
            with open(JOB_DIR / f"{job_id}.json", encoding="utf-8") as jf:
                job = json.load(jf)
        except Exception:
            return MemoryResponse(success=False, data={}, error="Unknown job_id")
        # Try to determine liveness via PID (POSIX)
        running = False
        returncode = None
        try:
            pid = int(job.get("pid"))
            os.kill(pid, 0)
            running = True
        except Exception:
            running = False

    def tail(path: str, nbytes: int = 2048) -> str:
        try:
            with open(path, "rb") as f:
                f.seek(0, os.SEEK_END)
                size = f.tell()
                f.seek(max(0, size - nbytes))
                return f.read().decode("utf-8", errors="replace")
        except Exception:
            return ""

    return MemoryResponse(
        success=True,
        data={
            "job_id": job_id,
            "running": running,
            "returncode": returncode,
            "stdout_tail": tail(job.get("stdout", "")),
            "stderr_tail": tail(job.get("stderr", "")),
        },
    )


async def get_precision_eval_result(args: dict[str, Any]) -> MemoryResponse:
    job_id = args.get("job_id")
    if not job_id:
        return MemoryResponse(success=False, data={}, error="Unknown job_id")

    rc = None
    job = None
    if job_id in JOBS:
        job = JOBS[job_id]
        proc: subprocess.Popen = job["process"]
        if proc.poll() is None:
            return MemoryResponse(success=False, data={}, error="Job is still running")
        rc = proc.returncode
    else:
        try:
            with open(JOB_DIR / f"{job_id}.json", encoding="utf-8") as jf:
                job = json.load(jf)
        except Exception:
            return MemoryResponse(success=False, data={}, error="Unknown job_id")

    try:
        with open(job.get("stdout", ""), encoding="utf-8", errors="replace") as fo:
            stdout = fo.read()
        with open(job.get("stderr", ""), encoding="utf-8", errors="replace") as fe:
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
            "config_file": job.get("config_file") if isinstance(job, dict) else None,
        },
        error=stderr if rc not in (None, 0) else None,
    )


async def cancel_precision_eval(args: dict[str, Any]) -> MemoryResponse:
    job_id = args.get("job_id")
    if not job_id or job_id not in JOBS:
        return MemoryResponse(success=False, data={}, error="Unknown job_id")
    job = JOBS[job_id]
    proc: subprocess.Popen = job["process"]
    if proc.poll() is None:
        try:
            proc.terminate()
            return MemoryResponse(success=True, data={"job_id": job_id, "status": "terminated"})
        except Exception as e:
            return MemoryResponse(success=False, data={}, error=str(e))
    return MemoryResponse(success=True, data={"job_id": job_id, "status": "already_finished"})


async def process_files(args: dict[str, Any]) -> MemoryResponse:
    """Process a list of repo-relative file paths and return lightweight analyses.

    arguments:
      - paths: list[str] (repo-relative)
      - max_bytes: int (optional, default 4000)
    """
    try:
        project_root = Path(__file__).parent.parent
        paths = args.get("paths") or []
        max_bytes = int(args.get("max_bytes", 4000))
        if not isinstance(paths, list) or not paths:
            raise HTTPException(status_code=400, detail="paths must be a non-empty list of repo-relative paths")

        results: list[dict[str, Any]] = []
        for rel in paths:
            p = (project_root / rel).resolve()
            try:
                # Security: ensure path stays within project
                if project_root not in p.parents and p != project_root:
                    raise HTTPException(status_code=400, detail=f"Path escapes project root: {rel}")
                if not p.exists() or not p.is_file():
                    results.append({"path": rel, "error": "not_found"})
                    continue
                size = p.stat().st_size
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

        return MemoryResponse(success=True, data={"files": results})
    except HTTPException as he:
        return MemoryResponse(success=False, data={}, error=str(he.detail))
    except Exception as e:
        return MemoryResponse(success=False, data={}, error=f"process_files failed: {str(e)}")


async def analyze_file_content(args: dict[str, Any]) -> MemoryResponse:
    """Analyze a single dropped file provided as raw content.

    arguments:
      - filename: str
      - content: str (UTF-8 text)
      - max_preview_chars: int (optional, default 2000)
    """
    try:
        filename = args.get("filename") or "unknown"
        content = args.get("content")
        if content is None:
            raise HTTPException(status_code=400, detail="content is required")
        max_preview_chars = int(args.get("max_preview_chars", 2000))

        preview = content[:max_preview_chars]
        line_count = content.count("\n") + 1
        file_ext = Path(filename).suffix.lower()

        # Simple heuristics for type
        is_code = file_ext in {".py", ".js", ".ts", ".go", ".rs", ".java", ".sh", ".yaml", ".yml", ".json"}
        is_markdown = file_ext in {".md"}

        # Very light “insights” for sidecar display
        insights: dict[str, Any] = {
            "filename": filename,
            "ext": file_ext,
            "lines": line_count,
            "chars": len(content),
            "is_code": is_code,
            "is_markdown": is_markdown,
        }

        return MemoryResponse(success=True, data={"preview": preview, "insights": insights})
    except HTTPException as he:
        return MemoryResponse(success=False, data={}, error=str(he.detail))
    except Exception as e:
        return MemoryResponse(success=False, data={}, error=f"analyze_file_content failed: {str(e)}")


@app.get("/mcp/tools")
async def list_tools():
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
        ]
    }


if __name__ == "__main__":
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="MCP Memory Server")
    parser.add_argument("--port", type=int, default=3000, help="Port to run on")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind to")

    args = parser.parse_args()

    print(f"🚀 Starting MCP Memory Server on {args.host}:{args.port}")
    print(f"📡 Health check: http://{args.host}:{args.port}/health")
    print(f"🔧 MCP tools: http://{args.host}:{args.port}/mcp/tools")
    # Helpful import diagnostics
    print(f"🧩 PYTHONPATH={os.environ.get('PYTHONPATH','')}")
    try:
        print(f"🧭 sys.path[:3]={sys.path[:3]}")
    except Exception:
        pass

    uvicorn.run(app, host=args.host, port=args.port)
