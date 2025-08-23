#!/usr/bin/env python3
"""
DSPy RAG System Dashboard
Flask-based web interface for the RAG system
"""

import atexit
import os
import signal
import sys
import threading
import time
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Protocol, cast, runtime_checkable

# Flask imports
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.utils import secure_filename

# Add src to path for imports
sys.path.append("src")

# ── Critical imports (hard dependencies: security + tier‑1 DSPy modules) ─────────
from dspy_modules.document_processor import DocumentProcessor
from dspy_modules.vector_store import HybridVectorStore
from utils.logger import get_logger
from utils.metadata_extractor import MetadataExtractor

# RAG system interface
from utils.rag_compatibility_shim import create_rag_interface
from utils.secrets_manager import setup_secrets_interactive, validate_startup_secrets
from utils.validator import (
    SecurityError,
    ValidationError,
    sanitize_filename,
    sanitize_prompt,
    validate_file_content,
    validate_file_path,
    validate_file_size,
    validate_query_complexity,
    validate_string_length,
)

# Optional monitoring callables (names are always defined for the linter)
create_health_endpoints: Optional[Callable[[Any], Any]] = None
initialize_production_monitoring: Optional[Callable[..., Any]] = None
try:
    from monitoring.health_endpoints import create_health_endpoints as _create_health_endpoints
    from monitoring.production_monitor import initialize_production_monitoring as _init_prod_monitoring

    create_health_endpoints = _create_health_endpoints
    initialize_production_monitoring = _init_prod_monitoring
except Exception as e:
    LOG = get_logger("dashboard")
    LOG.warning(f"Monitoring not available: {e}")

LOG = get_logger("dashboard")

# ── Structural typing for linter (interfaces we actually use) ───────────────────
@runtime_checkable
class VectorStoreProtocol(Protocol):
    def get_statistics(self) -> Dict[str, Any]: ...
    def store_document(
        self,
        *,
        document_id: str,
        filename: str,
        file_type: str,
        file_size: int,
        chunk_count: int,
        metadata: Dict[str, Any],
    ) -> Any: ...
    def store_chunk(
        self, *, document_id: str, chunk_index: int, content: str, embedding: Optional[List[float]]
    ) -> Any: ...
    def get_documents(self) -> List[Dict[str, Any]]: ...

@runtime_checkable
class DocumentProcessorProtocol(Protocol):
    def process_document(self, file_path: Path) -> Dict[str, Any]: ...

@runtime_checkable
class ProductionMonitorProtocol(Protocol):
    def start_monitoring(self, interval_seconds: int) -> None: ...
    def get_health_status(self) -> Dict[str, Any]: ...
    def get_security_events(self, hours: int) -> List[Dict[str, Any]]: ...
    def get_system_metrics(self, minutes: int) -> Any: ...

# Configuration
class DashboardConfig:
    """Dashboard configuration and settings"""

    # Flask settings
    SECRET_KEY = os.getenv("DASHBOARD_SECRET_KEY", "dev-secret-key-change-in-production")
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    UPLOAD_FOLDER = "uploads"
    ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".csv"}

    # Database settings
    POSTGRES_DSN = os.getenv("POSTGRES_DSN", "postgresql://ai_user:ai_password@localhost:5432/ai_agency")

    # Cursor Native AI settings
    CURSOR_NATIVE_AI_ENABLED = os.getenv("CURSOR_NATIVE_AI_ENABLED", "true").lower() == "true"
    CURSOR_NATIVE_AI_MODEL = os.getenv("CURSOR_NATIVE_AI_MODEL", "cursor-native-ai")

    # Processing settings
    MAX_WORKERS = int(os.getenv("DASHBOARD_WORKERS", "4"))
    PROCESSING_TIMEOUT = int(os.getenv("PROCESSING_TIMEOUT", "300"))

    # Load timeout configuration
    from utils.timeout_config import get_timeout_config

    TIMEOUT_CONFIG = get_timeout_config()

    # UI settings
    REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "5000"))  # 5 seconds
    MAX_QUERY_LENGTH = int(os.getenv("MAX_QUERY_LENGTH", "1000"))
    MAX_RESULTS = int(os.getenv("MAX_RESULTS", "10"))

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(DashboardConfig)

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize production monitoring
production_monitor = None
health_endpoints = None
try:
    if initialize_production_monitoring is not None:
        production_monitor = initialize_production_monitoring(
            service_name="ai-dev-tasks", service_version="0.3.1", environment=os.getenv("ENVIRONMENT", "development")
        )
    if create_health_endpoints is not None:
        health_endpoints = create_health_endpoints(app)
    LOG.info("Production monitoring initialized")
except Exception as e:
    LOG.warning(f"Production monitoring not available: {e}")

# Rate limiting (D-2)
_RATE = defaultdict(lambda: deque())  # No maxlen - we control it manually

def _check_rate(ip: str, limit=20, window=60):
    """Token bucket rate limiter"""
    now = time.monotonic()
    q = _RATE[ip]
    q.append(now)
    while q and now - q[0] > window:
        q.popleft()
    if len(q) > limit:
        return False
    return True

# Global state
class DashboardState:
    """Global dashboard state management"""

    def __init__(self):
        self.processing_files: Dict[str, Dict] = {}
        self.processing_lock = threading.Lock()
        self.rag_interface: Optional[Any] = None
        self.vector_store: Optional[VectorStoreProtocol] = None
        self.document_processor: Optional[DocumentProcessorProtocol] = None
        self.metadata_extractor: Optional[MetadataExtractor] = None
        self.graph_data_provider: Optional[Any] = None

        # Thread-safe executor with proper shutdown (D-4)
        self.executor = ThreadPoolExecutor(max_workers=DashboardConfig.MAX_WORKERS)
        atexit.register(lambda: self.executor.shutdown(wait=False))

        def _sigterm(*_):
            self.executor.shutdown(wait=False)

        signal.signal(signal.SIGTERM, _sigterm)

        self.stats = {
            "total_documents": 0,
            "total_chunks": 0,
            "total_queries": 0,
            "last_query_time": None,
            "system_uptime": datetime.now(),
            "processing_queue": 0,
        }

        # Thread-safe history with deque (D-3)
        self.query_history = deque(maxlen=100)
        self.history_lock = threading.Lock()

    def update_processing_file(
        self, filename: str, status: str, progress: int = 0, chunks: int = 0, error: Optional[str] = None
    ):
        """Update processing file status"""
        with self.processing_lock:
            self.processing_files[filename] = {
                "status": status,
                "progress": progress,
                "chunks": chunks,
                "error": error,
                "timestamp": datetime.now().isoformat(),
            }
            # Emit real-time update
            socketio.emit(
                "file_status_update",
                {"filename": filename, "status": status, "progress": progress, "chunks": chunks, "error": error},
            )

    def remove_processing_file(self, filename: str):
        """Remove file from processing list"""
        with self.processing_lock:
            if filename in self.processing_files:
                del self.processing_files[filename]

    def add_query_to_history(self, query: str, response: str, sources: List[str], response_time: float):
        """Add query to history with thread safety (D-3)"""
        with self.history_lock:
            self.query_history.append(
                {
                    "query": query,
                    "response": response,
                    "sources": sources,
                    "response_time": response_time,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            self.stats["total_queries"] += 1
            self.stats["last_query_time"] = datetime.now().isoformat()

# Initialize global state
state = DashboardState()

# Helper functions
def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return Path(filename).suffix.lower() in DashboardConfig.ALLOWED_EXTENSIONS

def get_file_size_mb(file_path: Path) -> float:
    """Get file size in MB"""
    try:
        return file_path.stat().st_size / (1024 * 1024)
    except OSError:
        return 0.0

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def initialize_components():
    """Initialize RAG system components with secrets validation (C-8)"""
    try:
        LOG.info("Initializing RAG system components...")

        # Validate secrets on startup (C-8)
        LOG.info("🔐 Validating secrets on startup...")
        if not validate_startup_secrets():
            LOG.error("❌ Secrets validation failed")
            LOG.info("🔧 Starting interactive secrets setup...")
            if not setup_secrets_interactive():
                LOG.error("❌ Interactive secrets setup failed")
                return False
            LOG.info("✅ Secrets setup completed")

        # Initialize vector store (cast for structural typing)
        state.vector_store = cast(
            "VectorStoreProtocol", HybridVectorStore(DashboardConfig.POSTGRES_DSN)  # expected interface at call sites
        )
        LOG.info("✅ Vector store initialized")

        # Initialize document processor (cast for structural typing)
        state.document_processor = cast("DocumentProcessorProtocol", DocumentProcessor())
        LOG.info("✅ Document processor initialized")

        # Initialize metadata extractor
        state.metadata_extractor = MetadataExtractor()
        LOG.info("✅ Metadata extractor initialized")

        # Initialize enhanced RAG interface with Cursor Native AI
        state.rag_interface = create_rag_interface(
            DashboardConfig.POSTGRES_DSN, None, DashboardConfig.CURSOR_NATIVE_AI_MODEL
        )
        LOG.info("✅ Enhanced RAG interface initialized with Cursor Native AI")

        # Start production monitoring if available
        if production_monitor:
            production_monitor.start_monitoring(interval_seconds=30)
            LOG.info("✅ Production monitoring started")

        # Update stats
        try:
            stats = state.vector_store.get_statistics()
            state.stats["total_documents"] = stats.get("total_documents", 0)
            state.stats["total_chunks"] = stats.get("total_chunks", 0)
        except Exception as e:
            LOG.warning(f"Could not get initial stats: {e}")

        LOG.info("🎉 All components initialized successfully")
        return True

    except Exception as e:
        LOG.error(f"Failed to initialize components: {e}")
        return False

def process_file_async(file_path: Path):
    """Process file asynchronously"""
    filename = file_path.name

    try:
        state.update_processing_file(filename, "processing", 10)

        # Check file size
        file_size_mb = get_file_size_mb(file_path)
        if file_size_mb > 100:  # 100MB limit
            state.update_processing_file(filename, "error", 0, 0, f"File too large: {file_size_mb:.1f}MB")
            return

        state.update_processing_file(filename, "processing", 20)

        # Process document
        if state.document_processor:
            result = state.document_processor.process_document(file_path)

            if result.get("success"):
                chunks = result.get("chunks", [])
                state.update_processing_file(filename, "processing", 60, len(chunks))

                # Store in vector database
                if state.vector_store:
                    doc_id = result.get("document_id", str(time.time()))
                    metadata = result.get("metadata", {})

                    # Store document metadata
                    state.vector_store.store_document(
                        document_id=doc_id,
                        filename=filename,
                        file_type=file_path.suffix,
                        file_size=int(file_path.stat().st_size),
                        chunk_count=len(chunks),
                        metadata=metadata,
                    )

                    # Store chunks
                    for i, chunk in enumerate(chunks):
                        state.vector_store.store_chunk(
                            document_id=doc_id,
                            chunk_index=i,
                            content=chunk.get("content", ""),
                            embedding=chunk.get("embedding"),
                        )

                    state.update_processing_file(filename, "completed", 100, len(chunks))

                    # Update stats
                    state.stats["total_documents"] += 1
                    state.stats["total_chunks"] += len(chunks)

                    # Move to processed folder
                    processed_dir = Path("processed_documents")
                    processed_dir.mkdir(exist_ok=True)
                    processed_path = processed_dir / filename
                    file_path.rename(processed_path)

                else:
                    state.update_processing_file(filename, "error", 0, 0, "Vector store not available")
            else:
                error_msg = result.get("error", "Unknown processing error")
                state.update_processing_file(filename, "error", 0, 0, error_msg)
        else:
            state.update_processing_file(filename, "error", 0, 0, "Document processor not available")

    except Exception as e:
        LOG.exception(f"Error processing {filename}")
        state.update_processing_file(filename, "error", 0, 0, str(e))

    finally:
        # Remove from processing after a delay
        def remove_after_delay():
            time.sleep(10)  # Keep status visible for 10 seconds
            state.remove_processing_file(filename)

        threading.Thread(target=remove_after_delay, daemon=True).start()

# Flask routes
@app.route("/")
def index():
    """Main dashboard page"""
    return render_template("dashboard.html", config=DashboardConfig)

@app.route("/cluster")
def cluster_visualization():
    """Cluster visualization page for chunk relationships"""
    return render_template("cluster.html", config=DashboardConfig)

@app.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload with comprehensive input validation (C-7)"""
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        raw_filename = cast(str, file.filename or "")
        if raw_filename == "":
            return jsonify({"error": "No file selected"}), 400

        # Comprehensive input validation
        try:
            # Validate file path and extension
            validate_file_path(raw_filename, list(DashboardConfig.ALLOWED_EXTENSIONS))

            # Sanitize filename
            filename = sanitize_filename(secure_filename(raw_filename))

            # Validate string length
            validate_string_length(filename, min_length=1, max_length=255)

        except (SecurityError, ValidationError) as e:
            LOG.warning(f"File validation failed: {e}")
            return jsonify({"error": f"File validation failed: {e}"}), 400

        # Secure upload directory with path confinement
        upload_dir = Path(app.config["UPLOAD_FOLDER"]).resolve()
        upload_dir.mkdir(exist_ok=True)
        file_path = (upload_dir / filename).resolve()

        # Double-check path confinement
        if not str(file_path).startswith(str(upload_dir)):
            LOG.warning(f"Path traversal attempt: {file_path}")
            return jsonify({"error": "Path traversal detected"}), 400

        # Save file temporarily to check size
        file.save(str(file_path))

        try:
            # Validate file size
            validate_file_size(str(file_path), max_size_mb=50)

            # Validate file content (basic check)
            validate_file_content(str(file_path), max_lines=10000)

        except (SecurityError, ValidationError) as e:
            # Clean up invalid file
            if file_path.exists():
                file_path.unlink()
            LOG.warning(f"File content validation failed: {e}")
            return jsonify({"error": f"File content validation failed: {e}"}), 400

        # Start async processing
        state.executor.submit(process_file_async, file_path)

        LOG.info(
            f"File uploaded successfully: {filename}",
            extra={
                "component": "dashboard",
                "action": "file_upload",
                "filename": filename,
                "file_size": file_path.stat().st_size,
            },
        )

        return jsonify(
            {"success": True, "message": f"File {filename} uploaded and processing started", "filename": filename}
        )

    except RequestEntityTooLarge:
        return jsonify({"error": "File too large"}), 413
    except Exception as e:
        LOG.exception("Upload error")
        return jsonify({"error": str(e)}), 500

@app.route("/query", methods=["POST"])
def query_rag():
    """Handle RAG queries with comprehensive input validation (C-7)"""
    try:
        # Rate limiting check
        ip = request.remote_addr or "unknown"
        if not _check_rate(ip):
            return jsonify({"error": "Rate limit exceeded"}), 429

        # Validate JSON structure
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON data"}), 400

            query = data.get("query", "").strip()

        except Exception as e:
            LOG.warning(f"JSON parsing error: {e}")
            return jsonify({"error": "Invalid JSON format"}), 400

        # Comprehensive query validation
        try:
            # Validate query presence
            if not query:
                return jsonify({"error": "Query is required"}), 400

            # Validate string length
            validate_string_length(query, min_length=1, max_length=DashboardConfig.MAX_QUERY_LENGTH)

            # Validate query complexity
            validate_query_complexity(query, max_tokens=1000)

            # Sanitize prompt for security
            sanitized_query = sanitize_prompt(query)

        except (SecurityError, ValidationError) as e:
            LOG.warning(f"Query validation failed: {e}")
            return jsonify({"error": f"Query validation failed: {e}"}), 400

        if not state.rag_interface:
            return jsonify({"error": "RAG system not available"}), 503

        # Process query with enhanced DSPy processing
        start_time = time.time()
        result = state.rag_interface.ask(sanitized_query)
        response_time = time.time() - start_time

        if result.get("status") == "success":
            response = result.get("answer", "")
            sources = result.get("sources", [])

            # Add to history
            state.add_query_to_history(sanitized_query, response, sources, response_time)

            LOG.info(
                "Query processed successfully",
                extra={
                    "component": "dashboard",
                    "action": "query_processed",
                    "query_length": len(sanitized_query),
                    "response_time": response_time,
                    "fast_path": result.get("fast_path", False),
                },
            )

            return jsonify(
                {
                    "success": True,
                    "answer": response,
                    "sources": sources,
                    "response_time": response_time,
                    "rewritten_query": result.get("rewritten_query", ""),
                    "reasoning": result.get("reasoning", ""),
                    "confidence": result.get("confidence", 0.8),
                    "fast_path": result.get("fast_path", False),
                }
            )
        else:
            error_msg = result.get("error", "Unknown error")
            LOG.error(f"RAG query failed: {error_msg}")
            return jsonify({"error": error_msg}), 500

    except Exception as e:
        LOG.exception("Query error")
        return jsonify({"error": str(e)}), 500

@app.route("/api/stats")
def get_stats():
    """Get system statistics"""
    try:
        # Get current stats from vector store
        if state.vector_store:
            try:
                db_stats = state.vector_store.get_statistics()
                state.stats["total_documents"] = db_stats.get("total_documents", 0)
                state.stats["total_chunks"] = db_stats.get("total_chunks", 0)
            except Exception as e:
                LOG.warning(f"Could not get DB stats: {e}")

        # Calculate uptime
        uptime = datetime.now() - state.stats["system_uptime"]

        return jsonify(
            {
                "total_documents": state.stats["total_documents"],
                "total_chunks": state.stats["total_chunks"],
                "total_queries": state.stats["total_queries"],
                "last_query_time": state.stats["last_query_time"],
                "uptime_seconds": int(uptime.total_seconds()),
                "processing_files": len(state.processing_files),
                "processing_queue": state.stats["processing_queue"],
            }
        )

    except Exception as e:
        LOG.exception("Stats error")
        return jsonify({"error": str(e)}), 500

@app.route("/api/processing")
def get_processing_status():
    """Get file processing status"""
    try:
        with state.processing_lock:
            return jsonify(list(state.processing_files.values()))
    except Exception as e:
        LOG.exception("Processing status error")
        return jsonify({"error": str(e)}), 500

@app.route("/api/query_history")
def get_query_history():
    """Get query history with thread safety (D-3)"""
    try:
        limit = request.args.get("limit", 20, type=int)
        with state.history_lock:
            return jsonify(list(state.query_history)[-limit:])
    except Exception as e:
        LOG.exception("Query history error")
        return jsonify({"error": str(e)}), 500

@app.route("/api/documents")
def get_documents():
    """Get document list"""
    try:
        if not state.vector_store:
            return jsonify({"error": "Vector store not available"}), 503

        documents = state.vector_store.get_documents()
        return jsonify(documents)

    except Exception as e:
        LOG.exception("Documents error")
        return jsonify({"error": str(e)}), 500

@app.route("/api/health")
def dashboard_health_check():
    """Health check endpoint"""
    try:
        components_status = {
            "vector_store": state.vector_store is not None,
            "document_processor": state.document_processor is not None,
            "rag_interface": state.rag_interface is not None,
            "metadata_extractor": state.metadata_extractor is not None,
        }

        all_healthy = all(components_status.values())

        return jsonify(
            {
                "status": "healthy" if all_healthy else "degraded",
                "components": components_status,
                "timestamp": datetime.now().isoformat(),
            }
        )

    except Exception as e:
        LOG.exception("Health check error")
        return jsonify({"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}), 500

@app.route("/api/monitoring")
def monitoring_data():
    """Production monitoring data endpoint"""
    try:
        if not production_monitor:
            return (
                jsonify({"error": "Production monitoring not available", "timestamp": datetime.now().isoformat()}),
                503,
            )

        # Get monitoring data
        health_status = production_monitor.get_health_status()
        security_events = production_monitor.get_security_events(hours=1)
        system_metrics = production_monitor.get_system_metrics(minutes=30)

        return (
            jsonify(
                {
                    "health": health_status,
                    "security_events": security_events,
                    "system_metrics": system_metrics,
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    except Exception as e:
        LOG.error(f"Monitoring data error: {e}")
        return jsonify({"error": str(e), "timestamp": datetime.now().isoformat()}), 503

@app.route("/graph-data")
def get_graph_data():
    """Get chunk relationship data for visualization"""
    try:
        # Check feature flag
        feature_flag_enabled = os.getenv("GRAPH_VISUALIZATION_ENABLED", "true").lower() == "true"
        if not feature_flag_enabled:
            return jsonify({"error": "Graph visualization feature is disabled"}), 403

        # Get query parameters with validation
        query = request.args.get("q", type=str)
        include_knn = request.args.get("include_knn", "true", type=str).lower() == "true"
        include_entity = request.args.get("include_entity", "true", type=str).lower() == "true"
        min_sim = request.args.get("min_sim", 0.5, type=float)
        max_nodes = request.args.get("max_nodes", 2000, type=int)

        # Input validation
        if min_sim < 0.0 or min_sim > 1.0:
            return jsonify({"error": "min_sim must be between 0.0 and 1.0"}), 400

        if max_nodes < 1 or max_nodes > 10000:
            return jsonify({"error": "max_nodes must be between 1 and 10000"}), 400

        # Validate query length if provided
        if query and len(query) > DashboardConfig.MAX_QUERY_LENGTH:
            return jsonify({"error": f"Query too long (max {DashboardConfig.MAX_QUERY_LENGTH} characters)"}), 400

        # Initialize GraphDataProvider if not already done
        if not hasattr(state, "graph_data_provider") or state.graph_data_provider is None:
            from utils.database_resilience import DatabaseResilienceManager
            from utils.graph_data_provider import GraphDataProvider

            db_manager = DatabaseResilienceManager(DashboardConfig.POSTGRES_DSN)
            state.graph_data_provider = GraphDataProvider(
                db_manager=db_manager,
                max_nodes=max_nodes,
                cache_enabled=True,
                feature_flag_enabled=feature_flag_enabled,
            )

        # Check if GraphDataProvider is available
        if state.graph_data_provider is None:
            return jsonify({"error": "Graph data provider not available"}), 503

        # Get graph data
        graph_data = state.graph_data_provider.get_graph_data(
            query=query,
            include_knn=include_knn,
            include_entity=include_entity,
            min_sim=min_sim,
            max_nodes=max_nodes,
        )

        # Convert to JSON-serializable format
        response_data = {
            "nodes": [
                {
                    "id": node.id,
                    "label": node.label,
                    "anchor": node.anchor,
                    "coords": list(node.coords),
                    "category": node.category,
                }
                for node in graph_data.nodes
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "type": edge.type,
                    "weight": edge.weight,
                }
                for edge in graph_data.edges
            ],
            "elapsed_ms": graph_data.elapsed_ms,
            "v": graph_data.v,
            "truncated": graph_data.truncated,
        }

        return jsonify(response_data)

    except ValueError as e:
        LOG.warning(f"Graph data validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception:
        LOG.exception("Graph data error")
        return jsonify({"error": "Internal server error"}), 500

# SocketIO events
@socketio.on("connect")
def handle_connect():
    """Handle client connection"""
    LOG.info("Client connected")
    emit("connected", {"message": "Connected to dashboard"})

@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection"""
    LOG.info("Client disconnected")

@socketio.on("request_stats")
def handle_stats_request():
    """Handle stats request from client"""
    try:
        # Get current stats
        if state.vector_store:
            try:
                db_stats = state.vector_store.get_statistics()
                state.stats["total_documents"] = db_stats.get("total_documents", 0)
                state.stats["total_chunks"] = db_stats.get("total_chunks", 0)
            except Exception as e:
                LOG.warning(f"Could not get DB stats: {e}")

        uptime = datetime.now() - state.stats["system_uptime"]

        emit(
            "stats_update",
            {
                "total_documents": state.stats["total_documents"],
                "total_chunks": state.stats["total_chunks"],
                "total_queries": state.stats["total_queries"],
                "last_query_time": state.stats["last_query_time"],
                "uptime_seconds": int(uptime.total_seconds()),
                "processing_files": len(state.processing_files),
            },
        )

    except Exception as e:
        LOG.exception("Stats request error")
        emit("error", {"message": str(e)})

# Error handlers
@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({"error": "File too large"}), 413

@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handle rate limit exceeded error"""
    return jsonify({"error": "Rate limit exceeded"}), 429

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    LOG.exception("Internal server error")
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(404)
def not_found(e):
    """Handle not found error"""
    return jsonify({"error": "Not found"}), 404

def main():
    """Main function to run the dashboard"""
    LOG.info(
        "🚀 DSPy RAG System Dashboard starting", extra={"component": "dashboard", "action": "startup", "version": "2.0"}
    )

    # Initialize components
    if not initialize_components():
        LOG.error(
            "❌ Failed to initialize components",
            extra={"component": "dashboard", "action": "initialization", "status": "failed"},
        )
        return

    # Create upload directory
    upload_dir = Path(DashboardConfig.UPLOAD_FOLDER)
    upload_dir.mkdir(exist_ok=True)

    LOG.info(
        "📊 Dashboard Configuration",
        extra={
            "component": "dashboard",
            "action": "configuration",
            "upload_folder": DashboardConfig.UPLOAD_FOLDER,
            "max_file_size": format_file_size(DashboardConfig.MAX_CONTENT_LENGTH),
            "allowed_extensions": list(DashboardConfig.ALLOWED_EXTENSIONS),
            "workers": DashboardConfig.MAX_WORKERS,
            "cursor_model": DashboardConfig.CURSOR_NATIVE_AI_MODEL,
        },
    )

    LOG.info(
        "🌐 Starting dashboard server",
        extra={
            "component": "dashboard",
            "action": "server_start",
            "host": "0.0.0.0",
            "port": 5000,
            "health_url": "http://localhost:5000/api/health",
        },
    )

    try:
        # Run with SocketIO
        socketio.run(app, host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        LOG.info(
            "⏹️  Stopping dashboard",
            extra={"component": "dashboard", "action": "shutdown", "reason": "keyboard_interrupt"},
        )
        state.executor.shutdown(wait=True)
        LOG.info("✅ Dashboard stopped", extra={"component": "dashboard", "action": "shutdown", "status": "completed"})

if __name__ == "__main__":
    main()
