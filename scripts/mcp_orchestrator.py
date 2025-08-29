"""
MCP Server Orchestration Module
Provides load balancing, failover management, intelligent routing, and health monitoring
"""

import asyncio
import logging
import random
import statistics
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import aiohttp

logger = logging.getLogger(__name__)


class ServerStatus(Enum):
    """Server status enumeration"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RESPONSE_TIME = "response_time"
    RANDOM = "random"


@dataclass
class ServerInfo:
    """Information about an MCP server"""

    id: str
    name: str
    url: str
    port: int
    weight: int = 1
    max_connections: int = 100
    health_check_interval: int = 30
    failover_threshold: int = 3
    recovery_threshold: int = 1  # Lowered for faster recovery

    # Runtime state
    status: ServerStatus = ServerStatus.OFFLINE
    current_connections: int = 0
    response_time_ms: float = 0.0
    error_count: int = 0
    success_count: int = 0
    last_health_check: float = 0.0
    last_response_time: float = 0.0
    consecutive_failures: int = 0
    consecutive_successes: int = 0

    # Health metrics
    uptime_percentage: float = 0.0
    avg_response_time: float = 0.0
    error_rate: float = 0.0
    total_requests: int = 0

    def __post_init__(self):
        """Initialize runtime state"""
        self.health_check_url = f"{self.url}/health"
        self.metrics_url = f"{self.url}/metrics"

    def update_health_metrics(self, response_time: float, success: bool):
        """Update health metrics based on request result"""
        current_time = time.time()
        self.last_response_time = current_time
        self.response_time_ms = response_time
        self.total_requests += 1

        if success:
            self.success_count += 1
            self.consecutive_successes += 1
            self.consecutive_failures = 0
        else:
            self.error_count += 1
            self.consecutive_failures += 1
            self.consecutive_successes = 0

        # Calculate error rate
        if self.total_requests > 0:
            self.error_rate = (self.error_count / self.total_requests) * 100

        # Update status based on consecutive failures/successes
        if self.consecutive_failures >= self.failover_threshold:
            self.status = ServerStatus.UNHEALTHY
        elif self.consecutive_successes >= self.recovery_threshold:
            if self.status == ServerStatus.UNHEALTHY:
                self.status = ServerStatus.HEALTHY
            elif self.status == ServerStatus.OFFLINE:
                self.status = ServerStatus.HEALTHY
        # Immediate status update for first successful health check
        elif success and self.status == ServerStatus.OFFLINE and self.total_requests == 1:
            self.status = ServerStatus.HEALTHY

        # Update average response time (simple moving average)
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (self.avg_response_time * 0.9) + (response_time * 0.1)

    def mark_healthy(self):
        """Mark server as healthy (for testing)"""
        self.status = ServerStatus.HEALTHY
        self.last_health_check = time.time()


@dataclass
class OrchestrationConfig:
    """Configuration for the orchestration system"""

    health_check_interval: int = 30  # seconds
    failover_timeout: int = 60  # seconds
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    load_balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    enable_sticky_sessions: bool = True
    session_timeout: int = 300  # seconds
    circuit_breaker_enabled: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60  # seconds


class HealthChecker:
    """Manages health checks for MCP servers"""

    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        """Start the health checker"""
        self.session = aiohttp.ClientSession()

    async def stop(self):
        """Stop the health checker"""
        if self.session:
            await self.session.close()

    async def check_server_health(self, server: ServerInfo) -> bool:
        """Check the health of a specific server"""
        if not self.session:
            logger.warning(f"No session available for health check of {server.name}")
            return False

        try:
            logger.info(f"Checking health of {server.name} at {server.health_check_url}")
            start_time = time.time()
            timeout = aiohttp.ClientTimeout(total=10)
            async with self.session.get(server.health_check_url, timeout=timeout) as response:
                response_time = (time.time() - start_time) * 1000

                if response.status == 200:
                    try:
                        data = await response.json()
                        status = data.get("status")
                        success = status in ["healthy", "degraded"]
                        logger.info(f"Health check for {server.name}: status={status}, success={success}")
                        server.update_health_metrics(response_time, success)
                        server.last_health_check = time.time()
                        return success
                    except Exception as e:
                        logger.warning(f"Failed to parse health check response for {server.name}: {e}")
                        server.update_health_metrics(response_time, False)
                        server.last_health_check = time.time()
                        return False
                else:
                    logger.warning(f"Health check for {server.name} returned status {response.status}")
                    server.update_health_metrics(response_time, False)
                    server.last_health_check = time.time()
                    return False

        except Exception as e:
            logger.warning(f"Health check failed for {server.name}: {e}")
            server.update_health_metrics(0, False)
            server.last_health_check = time.time()
            return False

    async def check_all_servers(self, servers: List[ServerInfo]):
        """Check health of all servers"""
        tasks = [self.check_server_health(server) for server in servers]
        await asyncio.gather(*tasks, return_exceptions=True)


class LoadBalancer:
    """Load balancer for distributing requests across servers"""

    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.current_index = 0
        self.server_weights: Dict[str, int] = {}

    def select_server(self, servers: List[ServerInfo], session_id: Optional[str] = None) -> Optional[ServerInfo]:
        """Select the best server based on the load balancing strategy"""
        # Filter healthy servers
        healthy_servers = [s for s in servers if s.status in [ServerStatus.HEALTHY, ServerStatus.DEGRADED]]

        if not healthy_servers:
            return None

        # Sticky sessions
        if self.config.enable_sticky_sessions and session_id:
            # Use session_id hash to consistently route to same server
            server_index = hash(session_id) % len(healthy_servers)
            return healthy_servers[server_index]

        # Apply load balancing strategy
        if self.config.load_balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_select(healthy_servers)
        elif self.config.load_balancing_strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return self._least_connections_select(healthy_servers)
        elif self.config.load_balancing_strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(healthy_servers)
        elif self.config.load_balancing_strategy == LoadBalancingStrategy.RESPONSE_TIME:
            return self._response_time_select(healthy_servers)
        elif self.config.load_balancing_strategy == LoadBalancingStrategy.RANDOM:
            return random.choice(healthy_servers)
        else:
            return healthy_servers[0]

    def _round_robin_select(self, servers: List[ServerInfo]) -> ServerInfo:
        """Round-robin selection"""
        server = servers[self.current_index % len(servers)]
        self.current_index += 1
        return server

    def _least_connections_select(self, servers: List[ServerInfo]) -> ServerInfo:
        """Select server with least connections"""
        return min(servers, key=lambda s: s.current_connections)

    def _weighted_round_robin_select(self, servers: List[ServerInfo]) -> ServerInfo:
        """Weighted round-robin selection"""
        total_weight = sum(s.weight for s in servers)
        if total_weight == 0:
            return servers[0]

        # Simple weighted selection
        weights = [s.weight for s in servers]
        return random.choices(servers, weights=weights)[0]

    def _response_time_select(self, servers: List[ServerInfo]) -> ServerInfo:
        """Select server with best response time"""
        return min(servers, key=lambda s: s.avg_response_time)


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""

    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def can_execute(self) -> bool:
        """Check if the circuit breaker allows execution"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.config.circuit_breaker_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True

    def on_success(self):
        """Handle successful execution"""
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
        self.failure_count = 0

    def on_failure(self):
        """Handle failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.config.circuit_breaker_threshold:
            self.state = "OPEN"


class MCPOrchestrator:
    """Main orchestration system for MCP servers"""

    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.servers: Dict[str, ServerInfo] = {}
        self.health_checker = HealthChecker(config)
        self.load_balancer = LoadBalancer(config)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.session_mapping: Dict[str, str] = {}  # session_id -> server_id
        self.running = False

    async def start(self):
        """Start the orchestration system"""
        logger.info("Starting MCP orchestrator")
        await self.health_checker.start()
        self.running = True

        # Start health check loop
        logger.info("Creating health check task")
        asyncio.create_task(self._health_check_loop())
        logger.info("Health check task created")

    async def stop(self):
        """Stop the orchestration system"""
        self.running = False
        await self.health_checker.stop()

    def add_server(self, server: ServerInfo):
        """Add a server to the orchestration pool"""
        self.servers[server.id] = server
        self.circuit_breakers[server.id] = CircuitBreaker(self.config)
        logger.info(f"Added server: {server.name} ({server.url})")

    def remove_server(self, server_id: str):
        """Remove a server from the orchestration pool"""
        if server_id in self.servers:
            del self.servers[server_id]
        if server_id in self.circuit_breakers:
            del self.circuit_breakers[server_id]
        logger.info(f"Removed server: {server_id}")

    async def route_request(
        self, tool_name: str, arguments: Dict[str, Any], session_id: Optional[str] = None
    ) -> Tuple[Optional[Dict], Optional[str]]:
        """Route a request to the appropriate server"""
        # Select server
        server = self.load_balancer.select_server(list(self.servers.values()), session_id)
        if not server:
            return None, "No healthy servers available"

        # Check circuit breaker
        circuit_breaker = self.circuit_breakers[server.id]
        if not circuit_breaker.can_execute():
            return None, f"Circuit breaker open for server {server.name}"

        # Update connection count
        server.current_connections += 1

        try:
            # Make request to selected server
            start_time = time.time()
            result = await self._make_request(server, tool_name, arguments)
            response_time = (time.time() - start_time) * 1000

            # Update metrics
            server.update_health_metrics(response_time, True)
            circuit_breaker.on_success()

            # Update session mapping
            if session_id:
                self.session_mapping[session_id] = server.id

            return result, None

        except Exception as e:
            # Update metrics
            server.update_health_metrics(0, False)
            circuit_breaker.on_failure()
            return None, str(e)

        finally:
            # Decrease connection count
            server.current_connections = max(0, server.current_connections - 1)

    async def _make_request(self, server: ServerInfo, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to a specific server"""
        url = f"{server.url}/mcp/tools/call"
        payload = {"name": tool_name, "arguments": arguments}

        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, timeout=timeout) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Server {server.name} returned status {response.status}")

    async def _health_check_loop(self):
        """Continuous health check loop"""
        logger.info("Starting health check loop")
        while self.running:
            try:
                logger.info(f"Running health checks for {len(self.servers)} servers")
                await self.health_checker.check_all_servers(list(self.servers.values()))
                await asyncio.sleep(self.config.health_check_interval)
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)

    def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get orchestration statistics"""
        total_servers = len(self.servers)
        healthy_servers = len([s for s in self.servers.values() if s.status == ServerStatus.HEALTHY])
        degraded_servers = len([s for s in self.servers.values() if s.status == ServerStatus.DEGRADED])
        unhealthy_servers = len([s for s in self.servers.values() if s.status == ServerStatus.UNHEALTHY])
        offline_servers = len([s for s in self.servers.values() if s.status == ServerStatus.OFFLINE])

        total_connections = sum(s.current_connections for s in self.servers.values())
        # Calculate average response time safely
        response_times = [s.avg_response_time for s in self.servers.values() if s.avg_response_time > 0]
        try:
            avg_response_time = statistics.mean(response_times) if response_times else 0
        except statistics.StatisticsError:
            avg_response_time = 0

        return {
            "total_servers": total_servers,
            "healthy_servers": healthy_servers,
            "degraded_servers": degraded_servers,
            "unhealthy_servers": unhealthy_servers,
            "offline_servers": offline_servers,
            "total_connections": total_connections,
            "avg_response_time_ms": avg_response_time,
            "load_balancing_strategy": self.config.load_balancing_strategy.value,
            "sticky_sessions_enabled": self.config.enable_sticky_sessions,
            "circuit_breaker_enabled": self.config.circuit_breaker_enabled,
            "active_sessions": len(self.session_mapping),
        }

    def get_server_details(self) -> List[Dict[str, Any]]:
        """Get detailed information about all servers"""
        return [
            {
                "id": server.id,
                "name": server.name,
                "url": server.url,
                "port": server.port,
                "status": server.status.value,
                "current_connections": server.current_connections,
                "max_connections": server.max_connections,
                "avg_response_time_ms": server.avg_response_time,
                "error_rate_percent": server.error_rate,
                "total_requests": server.total_requests,
                "uptime_percentage": server.uptime_percentage,
                "last_health_check": server.last_health_check,
                "weight": server.weight,
            }
            for server in self.servers.values()
        ]


# Global orchestrator instance
orchestrator: Optional[MCPOrchestrator] = None


def initialize_orchestrator(config: OrchestrationConfig) -> MCPOrchestrator:
    """Initialize the global orchestrator"""
    global orchestrator
    orchestrator = MCPOrchestrator(config)
    return orchestrator


def get_orchestrator() -> Optional[MCPOrchestrator]:
    """Get the global orchestrator instance"""
    return orchestrator
