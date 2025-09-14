"""Typed configuration models for the AI Development Tasks ecosystem."""

from pathlib import Path
from typing import Annotated, Literal, cast

from pydantic import BaseModel, ConfigDict, DirectoryPath, Field, HttpUrl, NonNegativeInt, PostgresDsn, SecretStr
from pydantic_core import MultiHostUrl


class Database(BaseModel):
    """Database configuration with connection and pool settings."""

    model_config = ConfigDict(validate_assignment=True)

    dsn: PostgresDsn = Field(
        default_factory=lambda: cast(PostgresDsn, "postgresql://danieljacobs@localhost:5432/ai_agency?sslmode=disable")
    )
    pool_size: int = Field(ge=1, le=64, default=8)
    timeout_ms: int = Field(ge=100, le=60_000, default=5_000)
    connect_timeout: int = Field(ge=1, le=60, default=10)
    read_timeout: int = Field(ge=5, le=300, default=30)
    write_timeout: int = Field(ge=10, le=600, default=60)
    pool_timeout: int = Field(ge=5, le=120, default=20)


class RAG(BaseModel):
    """RAG system configuration for retrieval and generation."""

    model_config = ConfigDict(validate_assignment=True)

    fast_path_enabled: bool = True
    max_query_len: int = Field(ge=16, le=4096, default=256)
    topk: int = Field(ge=1, le=100, default=25)
    prefetch_workers: int = Field(ge=1, le=8, default=3)

    # Chunking configuration
    chunk_size: int = Field(ge=100, le=2000, default=450)
    overlap_ratio: float = Field(ge=0.0, le=0.5, default=0.10)
    jaccard_threshold: float = Field(ge=0.0, le=1.0, default=0.8)
    prefix_policy: Literal["A", "B", "C"] = "A"

    # Embedding configuration
    embedder_name: str = "BAAI/bge-large-en-v1.5"
    embedding_dim: int = Field(ge=128, le=4096, default=1024)


class Eval(BaseModel):
    """Evaluation system configuration."""

    model_config = ConfigDict(validate_assignment=True)

    driver: Literal["dspy_rag", "synthetic", "ragchecker"] = "dspy_rag"
    use_real_rag: bool = True
    disable_cache: bool = False

    # RAGChecker specific settings
    use_bedrock: bool = True
    bypass_cli: bool = False
    lessons_mode: Literal["advisory", "enforcement", "disabled"] = "advisory"

    # Evaluation thresholds
    precision_threshold: float = Field(ge=0.0, le=1.0, default=0.20)
    recall_threshold: float = Field(ge=0.0, le=1.0, default=0.45)
    f1_threshold: float = Field(ge=0.0, le=1.0, default=0.22)
    faithfulness_threshold: float = Field(ge=0.0, le=1.0, default=0.60)


class Observability(BaseModel):
    """Observability and monitoring configuration."""

    model_config = ConfigDict(validate_assignment=True)

    logfire_token: SecretStr | None = None
    endpoint: HttpUrl | None = None

    # Logging configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "text"] = "text"

    # Metrics configuration
    metrics_enabled: bool = True
    metrics_port: int = Field(ge=1024, le=65535, default=8080)


class Security(BaseModel):
    """Security and authentication configuration."""

    model_config = ConfigDict(validate_assignment=True)

    # API Keys (stored as secrets)
    openai_api_key: SecretStr | None = None
    aws_access_key_id: SecretStr | None = None
    aws_secret_access_key: SecretStr | None = None
    aws_region: str = "us-east-1"

    # Security settings
    enable_encryption: bool = True
    encryption_key_path: Path | None = None
    audit_logging: bool = True


class Performance(BaseModel):
    """Performance and resource configuration."""

    model_config = ConfigDict(validate_assignment=True)

    # Timeout settings
    http_connect_timeout: int = Field(ge=1, le=60, default=10)
    http_read_timeout: int = Field(ge=5, le=300, default=30)
    http_total_timeout: int = Field(ge=10, le=600, default=120)

    # File processing timeouts
    pdf_processing_timeout: int = Field(ge=60, le=1800, default=300)
    file_upload_timeout: int = Field(ge=120, le=3600, default=600)
    chunk_processing_timeout: int = Field(ge=30, le=600, default=120)

    # LLM API timeouts
    llm_request_timeout: int = Field(ge=30, le=600, default=120)
    llm_stream_timeout: int = Field(ge=60, le=1800, default=300)

    # System timeouts
    health_check_timeout: int = Field(ge=1, le=60, default=10)
    metrics_timeout: int = Field(ge=1, le=60, default=5)
    startup_timeout: int = Field(ge=30, le=300, default=60)

    # Memory and concurrency
    max_memory_usage_mb: int = Field(ge=100, le=32768, default=8192)
    max_concurrent_requests: int = Field(ge=1, le=100, default=10)


class Memory(BaseModel):
    """Memory system configuration."""

    model_config = ConfigDict(validate_assignment=True)

    # LTST Memory System
    ltst_enabled: bool = True
    ltst_ttl_hours: int = Field(ge=1, le=168, default=24)
    ltst_max_items: int = Field(ge=100, le=100000, default=10000)

    # Cursor Memory System
    cursor_enabled: bool = True
    cursor_auto_rehydrate: bool = True

    # Go CLI Memory System
    go_cli_enabled: bool = True
    go_cli_mock_mode: bool = True

    # Prime Memory System
    prime_enabled: bool = True
    prime_auto_start: bool = True


class Development(BaseModel):
    """Development and testing configuration."""

    model_config = ConfigDict(validate_assignment=True)

    environment: Literal["dev", "test", "prod"] = "dev"
    debug_mode: bool = False
    hot_reload: bool = True

    # Testing configuration
    test_timeout: int = Field(ge=1, le=300, default=30)
    test_parallel: bool = True
    test_workers: int = Field(ge=1, le=8, default=4)

    # Development tools
    enable_profiling: bool = False
    enable_debugging: bool = False
    watch_files: bool = True
