#!/usr/bin/env python3
"""
MCP Memory Rehydrator Server
----------------------------
Minimal HTTP server that exposes the memory rehydrator as MCP-compatible endpoints.
This allows Cursor to automatically access database-based memory rehydration.

Usage:
    python3 scripts/mcp_memory_server.py
    # Then configure Cursor to connect to http://localhost:3000/mcp
"""

import hashlib
import json
import os
import sys
import threading
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

# Add the dspy-rag-system src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system", "src"))

try:
    from utils.memory_rehydrator import build_hydration_bundle
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the ai-dev-tasks root directory")
    sys.exit(1)


class ResponseCache:
    """Simple in-memory cache for hydration bundles"""

    def __init__(self, max_size=100, ttl_seconds=300):  # 5 minutes TTL
        self.cache = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.lock = threading.Lock()

    def _generate_key(self, role, task, limit, token_budget):
        """Generate cache key from request parameters"""
        key_data = f"{role}:{task}:{limit}:{token_budget}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, role, task, limit, token_budget):
        """Get cached response if available and not expired"""
        key = self._generate_key(role, task, limit, token_budget)
        with self.lock:
            if key in self.cache:
                cached_data = self.cache[key]
                if time.time() - cached_data["timestamp"] < self.ttl_seconds:
                    return cached_data["response"]
                else:
                    # Remove expired entry
                    del self.cache[key]
        return None

    def set(self, role, task, limit, token_budget, response):
        """Cache a response"""
        key = self._generate_key(role, task, limit, token_budget)
        with self.lock:
            # Remove oldest entry if cache is full
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
                del self.cache[oldest_key]

            self.cache[key] = {"response": response, "timestamp": time.time()}

    def get_stats(self):
        """Get cache statistics"""
        with self.lock:
            return {"size": len(self.cache), "max_size": self.max_size, "ttl_seconds": self.ttl_seconds}


class ServerMetrics:
    """Server metrics and monitoring"""

    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.cache_hits = 0
        self.response_times = deque(maxlen=100)  # Keep last 100 response times
        self.error_log = deque(maxlen=50)  # Keep last 50 errors
        self.role_usage = defaultdict(int)
        self.lock = threading.Lock()

    def record_request(self, role=None, response_time=None, error=False, error_msg=None, cache_hit=False):
        """Record a request and its metrics"""
        with self.lock:
            self.request_count += 1
            if response_time is not None:
                self.response_times.append(response_time)
            if error:
                self.error_count += 1
                if error_msg:
                    self.error_log.append({"timestamp": datetime.now().isoformat(), "error": error_msg})
            if role:
                self.role_usage[role] += 1
            if cache_hit:
                self.cache_hits += 1

    def get_metrics(self):
        """Get current server metrics"""
        with self.lock:
            uptime = time.time() - self.start_time
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            error_rate = (self.error_count / self.request_count * 100) if self.request_count > 0 else 0
            cache_hit_rate = (self.cache_hits / self.request_count * 100) if self.request_count > 0 else 0

            return {
                "uptime_seconds": uptime,
                "uptime_formatted": str(timedelta(seconds=int(uptime))),
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "cache_hits": self.cache_hits,
                "error_rate_percent": round(error_rate, 2),
                "cache_hit_rate_percent": round(cache_hit_rate, 2),
                "avg_response_time_ms": round(avg_response_time * 1000, 2),
                "recent_errors": list(self.error_log)[-10:],  # Last 10 errors
                "role_usage": dict(self.role_usage),
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            }


# Global instances
server_metrics = ServerMetrics()
response_cache = ResponseCache()


class MCPMemoryHandler(BaseHTTPRequestHandler):
    """HTTP handler for MCP-compatible memory rehydration endpoints"""

    def do_GET(self):
        """Handle GET requests for MCP server info"""
        if self.path == "/mcp":
            self.send_mcp_info()
        elif self.path == "/health":
            self.send_health_check()
        elif self.path == "/metrics":
            self.send_metrics()
        elif self.path == "/status":
            self.send_status_dashboard()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests for memory rehydration"""
        if self.path == "/mcp/tools/call":
            self.handle_memory_rehydration()
        else:
            self.send_error(404, "Not Found")

    def send_mcp_info(self):
        """Send MCP server information"""
        mcp_info = {
            "name": "memory-rehydrator",
            "version": "1.0.0",
            "description": "Database-based memory rehydration for Cursor AI",
            "tools": [
                {
                    "name": "rehydrate_memory",
                    "description": "Get role-aware context from PostgreSQL database",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "role": {
                                "type": "string",
                                "enum": ["planner", "implementer", "researcher"],
                                "description": "AI role for context selection",
                            },
                            "task": {"type": "string", "description": "Specific task or query for context"},
                            "limit": {
                                "type": "integer",
                                "default": 8,
                                "description": "Maximum number of sections to return",
                            },
                            "token_budget": {
                                "type": "integer",
                                "default": 1200,
                                "description": "Token budget for context",
                            },
                        },
                        "required": ["task"],
                    },
                }
            ],
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(mcp_info).encode())

    def send_health_check(self):
        """Send health check response"""
        metrics = server_metrics.get_metrics()
        health = {
            "status": "healthy" if metrics["error_rate_percent"] < 10 else "degraded",
            "timestamp": time.time(),
            "service": "mcp-memory-rehydrator",
            "uptime": metrics["uptime_formatted"],
            "error_rate": metrics["error_rate_percent"],
            "cache_hit_rate": metrics["cache_hit_rate_percent"],
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(health).encode())

    def send_metrics(self):
        """Send detailed server metrics"""
        metrics = server_metrics.get_metrics()
        cache_stats = response_cache.get_stats()
        metrics["cache_stats"] = cache_stats

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(metrics, indent=2).encode())

    def send_status_dashboard(self):
        """Send HTML status dashboard"""
        metrics = server_metrics.get_metrics()
        cache_stats = response_cache.get_stats()

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MCP Memory Server Status</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; color: #333; border-bottom: 2px solid #007acc; padding-bottom: 10px; }}
        .metric {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007acc; }}
        .metric h3 {{ margin: 0 0 10px 0; color: #007acc; }}
        .status {{ font-weight: bold; }}
        .status.healthy {{ color: #28a745; }}
        .status.degraded {{ color: #ffc107; }}
        .status.error {{ color: #dc3545; }}
        .role-usage {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .role-item {{ background: #e9ecef; padding: 5px 10px; border-radius: 15px; font-size: 0.9em; }}
        .error-log {{ background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; max-height: 200px; overflow-y: auto; }}
        .error-item {{ margin: 5px 0; padding: 5px; background: #fff; border-radius: 3px; font-size: 0.8em; }}
        .cache-stats {{ background: #d1ecf1; border: 1px solid #bee5eb; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 MCP Memory Server Status</h1>
            <p>Database-based memory rehydration for Cursor AI</p>
        </div>

        <div class="metric">
            <h3>📊 Server Status</h3>
            <p><span class="status {'healthy' if metrics['error_rate_percent'] < 10 else 'degraded'}">
                {'🟢 Healthy' if metrics['error_rate_percent'] < 10 else '🟡 Degraded'}
            </span></p>
            <p><strong>Uptime:</strong> {metrics['uptime_formatted']}</p>
            <p><strong>Python Version:</strong> {metrics['python_version']}</p>
        </div>

        <div class="metric">
            <h3>📈 Performance Metrics</h3>
            <p><strong>Total Requests:</strong> {metrics['total_requests']}</p>
            <p><strong>Error Rate:</strong> {metrics['error_rate_percent']}%</p>
            <p><strong>Cache Hit Rate:</strong> {metrics['cache_hit_rate_percent']}%</p>
            <p><strong>Average Response Time:</strong> {metrics['avg_response_time_ms']}ms</p>
        </div>

        <div class="metric">
            <h3>💾 Cache Statistics</h3>
            <div class="cache-stats">
                <p><strong>Cache Size:</strong> {cache_stats['size']}/{cache_stats['max_size']}</p>
                <p><strong>Cache Hits:</strong> {metrics['cache_hits']}</p>
                <p><strong>TTL:</strong> {cache_stats['ttl_seconds']} seconds</p>
            </div>
        </div>

        <div class="metric">
            <h3>👥 Role Usage</h3>
            <div class="role-usage">
                {''.join([f'<span class="role-item">{role}: {count}</span>' for role, count in metrics['role_usage'].items()])}
            </div>
        </div>

        <div class="metric">
            <h3>⚠️ Recent Errors</h3>
            <div class="error-log">
                {''.join([f'<div class="error-item"><strong>{error["timestamp"]}</strong>: {error["error"]}</div>' for error in metrics['recent_errors']]) if metrics['recent_errors'] else '<p>No recent errors</p>'}
            </div>
        </div>

        <div class="metric">
            <h3>🔗 Endpoints</h3>
            <p><strong>Health Check:</strong> <code>/health</code></p>
            <p><strong>Metrics:</strong> <code>/metrics</code></p>
            <p><strong>MCP Info:</strong> <code>/mcp</code></p>
            <p><strong>Memory Rehydration:</strong> <code>POST /mcp/tools/call</code></p>
        </div>
    </div>
</body>
</html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def handle_memory_rehydration(self):
        """Handle memory rehydration requests"""
        start_time = time.time()
        role = None
        error = False
        error_msg = None
        cache_hit = False

        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            request = json.loads(body.decode())

            # Extract parameters
            tool_name = request.get("name")
            arguments = request.get("arguments", {})

            if tool_name != "rehydrate_memory":
                error = True
                error_msg = "Unknown tool"
                self.send_error(400, "Unknown tool")
                return

            # Get parameters with defaults
            role = arguments.get("role", "planner")
            task = arguments.get("task", "general context")
            limit = arguments.get("limit", 8)
            token_budget = arguments.get("token_budget", 1200)

            # Check cache first
            cached_response = response_cache.get(role, task, limit, token_budget)
            if cached_response:
                cache_hit = True
                response = cached_response
            else:
                # Build hydration bundle
                bundle = build_hydration_bundle(role=role, task=task, limit=limit, token_budget=token_budget)
                response = {"content": [{"type": "text", "text": bundle.text}], "metadata": bundle.meta}

                # Cache the response
                response_cache.set(role, task, limit, token_budget, response)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            error = True
            error_msg = str(e)
            error_response = {"error": {"code": "internal_error", "message": str(e)}}
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(error_response).encode())

        finally:
            # Record metrics
            response_time = time.time() - start_time
            server_metrics.record_request(
                role=role, response_time=response_time, error=error, error_msg=error_msg, cache_hit=cache_hit
            )

    def log_message(self, format, *args):
        """Custom logging to avoid cluttering output"""
        pass


def start_server(port=3000):
    """Start the MCP memory server"""
    server_address = ("", port)
    httpd = HTTPServer(server_address, MCPMemoryHandler)

    print(f"🚀 MCP Memory Rehydrator Server starting on port {port}")
    print(f"📡 MCP endpoint: http://localhost:{port}/mcp")
    print(f"🏥 Health check: http://localhost:{port}/health")
    print(f"📊 Metrics: http://localhost:{port}/metrics")
    print(f"📈 Status dashboard: http://localhost:{port}/status")
    print(f"🔄 Memory rehydration: POST http://localhost:{port}/mcp/tools/call")
    print("💾 Response caching enabled (TTL: 5 minutes)")
    print("\n💡 Configure Cursor to connect to this server for automatic memory rehydration!")
    print("   Press Ctrl+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MCP Memory Rehydrator Server")
    parser.add_argument("--port", type=int, default=3000, help="Port to run server on")

    args = parser.parse_args()
    start_server(args.port)
