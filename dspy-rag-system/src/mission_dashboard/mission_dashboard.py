#!/usr/bin/env python3.12.123.11
"""
Real-time Mission Dashboard
Flask-based web interface for monitoring AI task execution in real-time
"""

import logging
import os
import sys
import time
from collections import defaultdict
from datetime import datetime
from typing import Any, cast

# Flask imports
# Optional dependency: realtime features require Flask-SocketIO
# Install with: pip install flask-socketio
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit

# Add src to path for imports
sys.path.append("src")

try:
    from mission_dashboard.mission_tracker import MissionPriority, MissionStatus, get_mission_tracker
    from monitoring.health_endpoints import create_health_endpoints
    from monitoring.production_monitor import initialize_production_monitoring
    from utils.logger import get_logger
    from utils.secrets_manager import validate_startup_secrets

    LOG = get_logger("mission_dashboard")
except ImportError as e:
    logging.basicConfig(level=logging.INFO)
    LOG = logging.getLogger("mission_dashboard")
    LOG.warning(f"Some components not available: {e}")

    # Fallback stubs to ensure names are always bound for type checkers/runtime
    class _MissionPriorityStub:
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"

        def __init__(self, value: str):
            value_lower = (value or "").lower()
            if value_lower not in (self.LOW, self.MEDIUM, self.HIGH):
                raise ValueError("Invalid priority")
            self.value = value_lower

    class _MissionStatusStub:
        def __init__(self, value: str):
            self.value = value

    def get_mission_tracker() -> Any:  # type: ignore[no-redef]
        return None

    def create_health_endpoints(app: Any) -> Any:  # type: ignore[no-redef]
        return None

    def initialize_production_monitoring(*_args: Any, **_kwargs: Any) -> Any:  # type: ignore[no-redef]
        return None

    def validate_startup_secrets() -> Any:  # type: ignore[no-redef]
        return None

    # Bind stub classes to expected names
    MissionPriority = _MissionPriorityStub  # type: ignore[assignment]
    MissionStatus = _MissionStatusStub  # type: ignore[assignment]


# Configuration
class MissionDashboardConfig:
    """Mission Dashboard configuration and settings"""

    # Flask settings
    SECRET_KEY = os.getenv("MISSION_DASHBOARD_SECRET_KEY", "mission-dashboard-secret-key")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB max file size

    # Dashboard settings
    REFRESH_INTERVAL = int(os.getenv("MISSION_DASHBOARD_REFRESH_INTERVAL", "2000"))  # 2 seconds
    MAX_MISSIONS_DISPLAY = int(os.getenv("MISSION_DASHBOARD_MAX_DISPLAY", "50"))
    AUTO_REFRESH = os.getenv("MISSION_DASHBOARD_AUTO_REFRESH", "true").lower() == "true"

    # Database settings
    POSTGRES_DSN = os.getenv("POSTGRES_DSN", "postgresql://ai_user:ai_password@localhost:5432/ai_agency")

    # UI settings
    THEME = os.getenv("MISSION_DASHBOARD_THEME", "dark")
    SHOW_DETAILS = os.getenv("MISSION_DASHBOARD_SHOW_DETAILS", "true").lower() == "true"
    ENABLE_FILTERS = os.getenv("MISSION_DASHBOARD_ENABLE_FILTERS", "true").lower() == "true"


# Initialize Flask app
app = Flask(__name__)
app.config.from_object(MissionDashboardConfig)

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Initialize mission tracker
mission_tracker = None
try:
    mission_tracker = get_mission_tracker()
    LOG.info("Mission tracker initialized")
except Exception as e:
    LOG.error(f"Failed to initialize mission tracker: {e}")

# Initialize production monitoring
production_monitor = None
health_endpoints = None
try:
    production_monitor = initialize_production_monitoring(
        service_name="mission-dashboard", service_version="1.0.0", environment=os.getenv("ENVIRONMENT", "development")
    )
    health_endpoints = create_health_endpoints(app)
    LOG.info("Production monitoring initialized")
except Exception as e:
    LOG.warning(f"Production monitoring not available: {e}")


# Dashboard state
class DashboardState:
    """Dashboard state management"""

    def __init__(self):
        self.connected_clients = set()
        self.last_update = datetime.now()
        self.update_callbacks = []

        # Register mission tracker callbacks
        if mission_tracker:
            mission_tracker.add_update_callback(self._on_mission_update)

    def _on_mission_update(self, event_type: str, mission_id: str):
        """Handle mission updates and broadcast to clients"""
        try:
            # Guard for optional mission tracker to satisfy type checker and runtime
            if not mission_tracker:
                return
            mission = mission_tracker.get_mission(mission_id)
            if mission:
                # Broadcast to all connected clients
                socketio.emit(
                    "mission_update",
                    {
                        "event_type": event_type,
                        "mission_id": mission_id,
                        "mission": self._mission_to_dict(mission),
                        "timestamp": datetime.now().isoformat(),
                    },
                )

                # Update metrics
                metrics = mission_tracker.get_metrics()
                socketio.emit(
                    "metrics_update",
                    {"metrics": self._metrics_to_dict(metrics), "timestamp": datetime.now().isoformat()},
                )
        except Exception as e:
            LOG.error(f"Error handling mission update: {e}")

    def _mission_to_dict(self, mission) -> dict[str, Any]:
        """Convert mission to dictionary for JSON serialization"""
        return {
            "id": mission.id,
            "title": mission.title,
            "description": mission.description,
            "status": mission.status.value,
            "priority": mission.priority.value,
            "created_at": mission.created_at.isoformat() if mission.created_at else None,
            "started_at": mission.started_at.isoformat() if mission.started_at else None,
            "completed_at": mission.completed_at.isoformat() if mission.completed_at else None,
            "duration": mission.duration,
            "progress": mission.progress,
            "error_message": mission.error_message,
            "result": mission.result,
            "metadata": mission.metadata,
            "agent_type": mission.agent_type,
            "model_used": mission.model_used,
            "tokens_used": mission.tokens_used,
            "cost_estimate": mission.cost_estimate,
        }

    def _metrics_to_dict(self, metrics) -> dict[str, Any]:
        """Convert metrics to dictionary for JSON serialization"""
        return {
            "total_missions": metrics.total_missions,
            "completed_missions": metrics.completed_missions,
            "failed_missions": metrics.failed_missions,
            "running_missions": metrics.running_missions,
            "average_duration": metrics.average_duration,
            "success_rate": metrics.success_rate,
            "total_tokens": metrics.total_tokens,
            "total_cost": metrics.total_cost,
        }


# Initialize dashboard state
dashboard_state = DashboardState()

# Rate limiting


class RateLimiter:
    """Simple rate limiter for API endpoints"""

    def __init__(self, max_requests: int = 100, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)

    def is_allowed(self, ip: str) -> bool:
        """Check if request is allowed"""
        now = time.time()
        self.requests[ip] = [req_time for req_time in self.requests[ip] if now - req_time < self.window]

        if len(self.requests[ip]) >= self.max_requests:
            return False

        self.requests[ip].append(now)
        return True


rate_limiter = RateLimiter()


def check_rate_limit():
    """Check rate limit for current request"""
    ip = request.remote_addr or "unknown"
    if not rate_limiter.is_allowed(ip):
        return jsonify({"error": "Rate limit exceeded"}), 429
    return None


# Routes
@app.route("/")
def index():
    """Main dashboard page"""
    return render_template("mission_dashboard.html")


@app.route("/api/missions")
def get_missions():
    """Get all missions with optional filtering"""
    # Check rate limit
    rate_limit_check = check_rate_limit()
    if rate_limit_check:
        return rate_limit_check

    if not mission_tracker:
        return jsonify({"error": "Mission tracker not available"}), 503

    try:
        # Get query parameters
        status = request.args.get("status")
        priority = request.args.get("priority")
        limit = int(request.args.get("limit", 50))

        # Get missions
        tracker = cast(Any, mission_tracker)
        missions = list(tracker.get_all_missions(limit=limit))

        # Apply filters
        if status:
            missions = [m for m in missions if m.status.value == status]

        if priority:
            missions = [m for m in missions if m.priority.value == priority]

        # Convert to dict
        missions_data = [dashboard_state._mission_to_dict(m) for m in missions]

        return jsonify(
            {"missions": missions_data, "total": len(missions_data), "timestamp": datetime.now().isoformat()}
        )

    except Exception as e:
        LOG.error(f"Error getting missions: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/missions/<mission_id>")
def get_mission(mission_id):
    """Get specific mission by ID"""
    # Check rate limit
    rate_limit_check = check_rate_limit()
    if rate_limit_check:
        return rate_limit_check

    if not mission_tracker:
        return jsonify({"error": "Mission tracker not available"}), 503

    try:
        tracker = cast(Any, mission_tracker)
        mission = tracker.get_mission(mission_id)
        if not mission:
            return jsonify({"error": "Mission not found"}), 404

        return jsonify({"mission": dashboard_state._mission_to_dict(mission), "timestamp": datetime.now().isoformat()})

    except Exception as e:
        LOG.error(f"Error getting mission {mission_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/missions", methods=["POST"])
def create_mission():
    """Create a new mission"""
    # Check rate limit
    rate_limit_check = check_rate_limit()
    if rate_limit_check:
        return rate_limit_check

    if not mission_tracker:
        return jsonify({"error": "Mission tracker not available"}), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        title = data.get("title")
        description = data.get("description", "")
        priority_str = data.get("priority", "medium")
        metadata = data.get("metadata", {})

        if not title:
            return jsonify({"error": "Title is required"}), 400

        # Convert priority string to enum
        try:
            priority = MissionPriority(priority_str.lower())
        except ValueError:
            priority = MissionPriority.MEDIUM

        # Create mission
        mission_id = mission_tracker.create_mission(
            title=title, description=description, priority=priority, metadata=metadata
        )

        return (
            jsonify(
                {
                    "mission_id": mission_id,
                    "message": "Mission created successfully",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            201,
        )

    except Exception as e:
        LOG.error(f"Error creating mission: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/missions/<mission_id>/start", methods=["POST"])
def start_mission(mission_id):
    """Start a mission"""
    # Check rate limit
    rate_limit_check = check_rate_limit()
    if rate_limit_check:
        return rate_limit_check

    if not mission_tracker:
        return jsonify({"error": "Mission tracker not available"}), 503

    try:
        data = request.get_json() or {}
        agent_type = str(data.get("agent_type") or "unknown")
        model_used = str(data.get("model_used") or "unknown")

        tracker = cast(Any, mission_tracker)
        success = tracker.start_mission(mission_id=mission_id, agent_type=agent_type, model_used=model_used)

        if not success:
            return jsonify({"error": "Failed to start mission"}), 400

        return jsonify({"message": "Mission started successfully", "timestamp": datetime.now().isoformat()})

    except Exception as e:
        LOG.error(f"Error starting mission {mission_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/missions/<mission_id>/progress", methods=["POST"])
def update_mission_progress(mission_id):
    """Update mission progress"""
    # Check rate limit
    rate_limit_check = check_rate_limit()
    if rate_limit_check:
        return rate_limit_check

    if not mission_tracker:
        return jsonify({"error": "Mission tracker not available"}), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        progress = data.get("progress", 0.0)
        result = data.get("result")

        tracker = cast(Any, mission_tracker)
        success = tracker.update_mission_progress(mission_id=mission_id, progress=progress, result=result)

        if not success:
            return jsonify({"error": "Failed to update mission progress"}), 400

        return jsonify({"message": "Mission progress updated successfully", "timestamp": datetime.now().isoformat()})

    except Exception as e:
        LOG.error(f"Error updating mission progress {mission_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/missions/<mission_id>/complete", methods=["POST"])
def complete_mission(mission_id):
    """Complete a mission"""
    # Check rate limit
    rate_limit_check = check_rate_limit()
    if rate_limit_check:
        return rate_limit_check

    if not mission_tracker:
        return jsonify({"error": "Mission tracker not available"}), 503

    try:
        data = request.get_json() or {}
        result = data.get("result")
        tokens_used = data.get("tokens_used")
        cost_estimate = data.get("cost_estimate")

        tracker = cast(Any, mission_tracker)
        success = tracker.complete_mission(
            mission_id=mission_id, result=result, tokens_used=tokens_used, cost_estimate=cost_estimate
        )

        if not success:
            return jsonify({"error": "Failed to complete mission"}), 400

        return jsonify({"message": "Mission completed successfully", "timestamp": datetime.now().isoformat()})

    except Exception as e:
        LOG.error(f"Error completing mission {mission_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/missions/<mission_id>/fail", methods=["POST"])
def fail_mission(mission_id):
    """Fail a mission"""
    # Check rate limit
    rate_limit_check = check_rate_limit()
    if rate_limit_check:
        return rate_limit_check

    if not mission_tracker:
        return jsonify({"error": "Mission tracker not available"}), 503

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        error_message = data.get("error_message", "Unknown error")

        tracker = cast(Any, mission_tracker)
        success = tracker.fail_mission(mission_id=mission_id, error_message=error_message)

        if not success:
            return jsonify({"error": "Failed to fail mission"}), 400

        return jsonify({"message": "Mission failed successfully", "timestamp": datetime.now().isoformat()})

    except Exception as e:
        LOG.error(f"Error failing mission {mission_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/missions/<mission_id>/cancel", methods=["POST"])
def cancel_mission(mission_id):
    """Cancel a mission"""
    # Check rate limit
    rate_limit_check = check_rate_limit()
    if rate_limit_check:
        return rate_limit_check

    if not mission_tracker:
        return jsonify({"error": "Mission tracker not available"}), 503

    try:
        tracker = cast(Any, mission_tracker)
        success = tracker.cancel_mission(mission_id=mission_id)

        if not success:
            return jsonify({"error": "Failed to cancel mission"}), 400

        return jsonify({"message": "Mission cancelled successfully", "timestamp": datetime.now().isoformat()})

    except Exception as e:
        LOG.error(f"Error cancelling mission {mission_id}: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/metrics")
def get_metrics():
    """Get mission metrics"""
    # Check rate limit
    rate_limit_check = check_rate_limit()
    if rate_limit_check:
        return rate_limit_check

    if not mission_tracker:
        return jsonify({"error": "Mission tracker not available"}), 503

    try:
        tracker = cast(Any, mission_tracker)
        metrics = tracker.get_metrics()

        return jsonify({"metrics": dashboard_state._metrics_to_dict(metrics), "timestamp": datetime.now().isoformat()})

    except Exception as e:
        LOG.error(f"Error getting metrics: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/running")
def get_running_missions():
    """Get currently running missions"""
    # Check rate limit
    rate_limit_check = check_rate_limit()
    if rate_limit_check:
        return rate_limit_check

    if not mission_tracker:
        return jsonify({"error": "Mission tracker not available"}), 503

    try:
        tracker = cast(Any, mission_tracker)
        running_missions = list(tracker.get_running_missions())
        missions_data = [dashboard_state._mission_to_dict(m) for m in running_missions]

        return jsonify(
            {"missions": missions_data, "count": len(missions_data), "timestamp": datetime.now().isoformat()}
        )

    except Exception as e:
        LOG.error(f"Error getting running missions: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/health")
def dashboard_health():
    """Health check endpoint"""
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "mission_tracker": mission_tracker is not None,
            "production_monitor": production_monitor is not None,
            "uptime": time.time(),
        }

        return jsonify(health_status)

    except Exception as e:
        LOG.error(f"Health check error: {e}")
        return jsonify({"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}), 500


# SocketIO events
@socketio.on("connect")
def handle_connect():
    """Handle client connection"""
    try:
        dashboard_state.connected_clients.add(request.sid)  # type: ignore[attr-defined]
        LOG.info(f"Client connected: {request.sid}")  # type: ignore[attr-defined]

        # Send initial data
        if mission_tracker:
            missions = mission_tracker.get_all_missions(limit=20)
            metrics = mission_tracker.get_metrics()

            emit(
                "initial_data",
                {
                    "missions": [dashboard_state._mission_to_dict(m) for m in missions],
                    "metrics": dashboard_state._metrics_to_dict(metrics),
                    "timestamp": datetime.now().isoformat(),
                },
            )

    except Exception as e:
        LOG.error(f"Error handling client connection: {e}")


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection"""
    try:
        dashboard_state.connected_clients.discard(request.sid)  # type: ignore[attr-defined]
        LOG.info(f"Client disconnected: {request.sid}")  # type: ignore[attr-defined]

    except Exception as e:
        LOG.error(f"Error handling client disconnection: {e}")


@socketio.on("request_update")
def handle_update_request():
    """Handle client update request"""
    try:
        if mission_tracker:
            missions = mission_tracker.get_all_missions(limit=20)
            metrics = mission_tracker.get_metrics()

            emit(
                "data_update",
                {
                    "missions": [dashboard_state._mission_to_dict(m) for m in missions],
                    "metrics": dashboard_state._metrics_to_dict(metrics),
                    "timestamp": datetime.now().isoformat(),
                },
            )

    except Exception as e:
        LOG.error(f"Error handling update request: {e}")


# Error handlers
@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({"error": "Request too large"}), 413


@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handle rate limit exceeded error"""
    return jsonify({"error": "Rate limit exceeded"}), 429


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    LOG.error(f"Internal server error: {e}")
    return jsonify({"error": "Internal server error"}), 500


@app.errorhandler(404)
def not_found(e):
    """Handle not found error"""
    return jsonify({"error": "Not found"}), 404


def main():
    """Main application entry point"""
    try:
        # Validate startup secrets
        validate_startup_secrets()

        # Get configuration
        host = os.getenv("MISSION_DASHBOARD_HOST", "0.0.0.0")
        port = int(os.getenv("MISSION_DASHBOARD_PORT", "5002"))
        debug = os.getenv("MISSION_DASHBOARD_DEBUG", "false").lower() == "true"

        LOG.info(f"Starting Mission Dashboard on {host}:{port}")

        # Start the application
        socketio.run(app, host=host, port=port, debug=debug)

    except KeyboardInterrupt:
        LOG.info("Shutting down Mission Dashboard...")
    except Exception as e:
        LOG.error(f"Error starting Mission Dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
