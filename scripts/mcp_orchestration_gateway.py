#!/usr/bin/env python3
"""
MCP Orchestration Gateway Server
Acts as a frontend for multiple MCP servers with load balancing, failover, and intelligent routing
"""

import asyncio
import json
import logging
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

# Import orchestration components
from mcp_orchestrator import (
    LoadBalancingStrategy,
    OrchestrationConfig,
    ServerInfo,
    get_orchestrator,
    initialize_orchestrator,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrchestrationGatewayHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the orchestration gateway"""

    def __init__(self, *args, **kwargs):
        self.orchestrator = get_orchestrator()
        super().__init__(*args, **kwargs)

    def log_message(self, format, *args):
        """Custom logging to avoid cluttering output"""
        pass

    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/health":
            self.send_health_check()
        elif self.path == "/orchestration/stats":
            self.send_orchestration_stats()
        elif self.path == "/orchestration/servers":
            self.send_server_details()
        elif self.path == "/orchestration/dashboard":
            self.send_orchestration_dashboard()
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/mcp/tools/call":
            self.handle_orchestrated_tool_call()
        elif self.path == "/orchestration/servers/add":
            self.handle_add_server()
        elif self.path == "/orchestration/servers/remove":
            self.handle_remove_server()
        else:
            self.send_error(404, "Not Found")

    def send_health_check(self):
        """Send health check response"""
        if not self.orchestrator:
            self.send_error(503, "Orchestrator not available")
            return

        stats = self.orchestrator.get_orchestration_stats()

        health = {
            "status": "healthy" if stats["healthy_servers"] > 0 else "unhealthy",
            "timestamp": time.time(),
            "service": "mcp-orchestration-gateway",
            "orchestration_stats": stats,
        }

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(health).encode())

    def send_orchestration_stats(self):
        """Send orchestration statistics"""
        if not self.orchestrator:
            self.send_error(503, "Orchestrator not available")
            return

        stats = self.orchestrator.get_orchestration_stats()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(stats, indent=2).encode())

    def send_server_details(self):
        """Send detailed server information"""
        if not self.orchestrator:
            self.send_error(503, "Orchestrator not available")
            return

        server_details = self.orchestrator.get_server_details()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(server_details, indent=2).encode())

    def send_orchestration_dashboard(self):
        """Send HTML orchestration dashboard"""
        if not self.orchestrator:
            self.send_error(503, "Orchestrator not available")
            return

        stats = self.orchestrator.get_orchestration_stats()
        server_details = self.orchestrator.get_server_details()

        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>MCP Orchestration Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
        .metric-card {{ background: white; padding: 20px; margin: 10px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #666; margin-bottom: 10px; }}
        .status-healthy {{ color: #28a745; }}
        .status-degraded {{ color: #ffc107; }}
        .status-unhealthy {{ color: #dc3545; }}
        .status-offline {{ color: #6c757d; }}
        .refresh-btn {{ background: #667eea; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin-bottom: 20px; }}
        .refresh-btn:hover {{ background: #5a6fd8; }}
        .server-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        .server-table th, .server-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        .server-table th {{ background-color: #f8f9fa; font-weight: bold; }}
        .server-table tr:hover {{ background-color: #f5f5f5; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 MCP Orchestration Dashboard</h1>
            <p>Load balancing, failover, and intelligent routing for MCP servers</p>
        </div>

        <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>

        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Servers</div>
                <div class="metric-value">{stats['total_servers']}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Healthy Servers</div>
                <div class="metric-value status-healthy">{stats['healthy_servers']}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Degraded Servers</div>
                <div class="metric-value status-degraded">{stats['degraded_servers']}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Unhealthy Servers</div>
                <div class="metric-value status-unhealthy">{stats['unhealthy_servers']}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Total Connections</div>
                <div class="metric-value">{stats['total_connections']}</div>
            </div>

            <div class="metric-card">
                <div class="metric-label">Avg Response Time</div>
                <div class="metric-value">{stats['avg_response_time_ms']:.1f}ms</div>
            </div>
        </div>

        <div class="metric-card">
            <h3>⚙️ Orchestration Configuration</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 10px;">
                <div><strong>Load Balancing Strategy:</strong> {stats['load_balancing_strategy'].replace('_', ' ').title()}</div>
                <div><strong>Sticky Sessions:</strong> {'Enabled' if stats['sticky_sessions_enabled'] else 'Disabled'}</div>
                <div><strong>Circuit Breaker:</strong> {'Enabled' if stats['circuit_breaker_enabled'] else 'Disabled'}</div>
                <div><strong>Active Sessions:</strong> {stats['active_sessions']}</div>
            </div>
        </div>

        <div class="metric-card">
            <h3>🖥️ Server Details</h3>
            <table class="server-table">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>URL</th>
                        <th>Status</th>
                        <th>Connections</th>
                        <th>Response Time</th>
                        <th>Error Rate</th>
                        <th>Total Requests</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr>
                        <td>{server['name']}</td>
                        <td>{server['url']}</td>
                        <td><span class="status-{server['status']}">{server['status'].title()}</span></td>
                        <td>{server['current_connections']}/{server['max_connections']}</td>
                        <td>{server['avg_response_time_ms']:.1f}ms</td>
                        <td>{server['error_rate_percent']:.1f}%</td>
                        <td>{server['total_requests']}</td>
                    </tr>
                    ''' for server in server_details])}
                </tbody>
            </table>
        </div>

        <div class="metric-card">
            <h3>📊 Quick Actions</h3>
            <p><a href="/orchestration/stats" target="_blank">📈 View Detailed Stats</a></p>
            <p><a href="/orchestration/servers" target="_blank">🖥️ Server Details</a></p>
            <p><a href="/health" target="_blank">🏥 Health Check</a></p>
        </div>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
        """

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def handle_orchestrated_tool_call(self):
        """Handle tool calls with orchestration"""
        if not self.orchestrator:
            self.send_error(503, "Orchestrator not available")
            return

        try:
            # Read request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            request = json.loads(body.decode())

            # Extract parameters
            tool_name = request.get("name")
            arguments = request.get("arguments", {})
            session_id = self.headers.get("X-Session-ID")

            if not tool_name:
                self.send_error(400, "Missing tool name")
                return

            # Route request through orchestrator
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                result, error = loop.run_until_complete(
                    self.orchestrator.route_request(tool_name, arguments, session_id)
                )
            finally:
                loop.close()

            if error:
                self.send_error(500, f"Orchestration error: {error}")
                return

            # Send response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())

        except Exception as e:
            logger.error(f"Orchestrated tool call failed: {e}")
            self.send_error(500, f"Internal server error: {str(e)}")

    def handle_add_server(self):
        """Handle adding a server to the orchestration pool"""
        if not self.orchestrator:
            self.send_error(503, "Orchestrator not available")
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            server_data = json.loads(body.decode())

            # Create server info
            server = ServerInfo(
                id=server_data.get("id"),
                name=server_data.get("name"),
                url=server_data.get("url"),
                port=server_data.get("port", 3000),
                weight=server_data.get("weight", 1),
                max_connections=server_data.get("max_connections", 100),
            )

            # Add server to orchestrator
            self.orchestrator.add_server(server)

            response = {"message": f"Server {server.name} added successfully"}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            logger.error(f"Add server failed: {e}")
            self.send_error(500, f"Failed to add server: {str(e)}")

    def handle_remove_server(self):
        """Handle removing a server from the orchestration pool"""
        if not self.orchestrator:
            self.send_error(503, "Orchestrator not available")
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())

            server_id = data.get("server_id")
            if not server_id:
                self.send_error(400, "Missing server_id")
                return

            # Remove server from orchestrator
            self.orchestrator.remove_server(server_id)

            response = {"message": f"Server {server_id} removed successfully"}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            logger.error(f"Remove server failed: {e}")
            self.send_error(500, f"Failed to remove server: {str(e)}")


def start_orchestration_gateway(port: int = 3002):
    """Start the orchestration gateway server"""
    # Initialize orchestrator
    config = OrchestrationConfig(
        health_check_interval=30,
        load_balancing_strategy=LoadBalancingStrategy.ROUND_ROBIN,
        enable_sticky_sessions=True,
        circuit_breaker_enabled=True,
    )

    orchestrator = initialize_orchestrator(config)

    # Add some default servers for testing
    server1 = ServerInfo(id="server_1", name="MCP Memory Server 1", url="http://localhost:3000", port=3000, weight=1)
    server2 = ServerInfo(id="server_2", name="MCP Memory Server 2", url="http://localhost:3001", port=3001, weight=1)

    orchestrator.add_server(server1)
    orchestrator.add_server(server2)

    # Servers will be marked healthy by async health checks

    # Start orchestrator with async health checks
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(orchestrator.start())

    # Start HTTP server
    server_address = ("", port)
    httpd = HTTPServer(server_address, OrchestrationGatewayHandler)

    print(f"🚀 MCP Orchestration Gateway starting on port {port}")
    print(f"📡 Gateway endpoint: http://localhost:{port}/mcp/tools/call")
    print(f"🏥 Health check: http://localhost:{port}/health")
    print(f"📊 Orchestration dashboard: http://localhost:{port}/orchestration/dashboard")
    print(f"📈 Orchestration stats: http://localhost:{port}/orchestration/stats")
    print(f"🖥️ Server details: http://localhost:{port}/orchestration/servers")
    print("\n💡 This gateway provides load balancing and failover for multiple MCP servers!")
    print("   Press Ctrl+C to stop the server")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Orchestration gateway stopped")
        loop.run_until_complete(orchestrator.stop())


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MCP Orchestration Gateway Server")
    parser.add_argument("--port", type=int, default=3002, help="Port to run gateway on")

    args = parser.parse_args()
    start_orchestration_gateway(args.port)
