"""
OpenTelemetry Configuration Module

Provides centralized OpenTelemetry setup for distributed tracing and monitoring.
"""

import os
import logging
import uuid
from typing import Optional, Any
from contextlib import contextmanager

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    BatchSpanProcessor
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor

logger = logging.getLogger(__name__)

class OpenTelemetryConfig:
    """Centralized OpenTelemetry configuration manager"""
    
    def __init__(self):
        self._initialized = False
        self._tracer_provider = None
        self._tracer = None
        self._correlation_id = None
        
    def initialize(self, 
                  service_name: str = "ai-dev-tasks",
                  service_version: str = "0.3.1",
                  environment: str = "development",
                  otlp_endpoint: str | None = None,
                  enable_console_exporter: bool = True,
                  enable_requests_instrumentation: bool = True,
                  enable_flask_instrumentation: bool = True,
                  enable_logging_instrumentation: bool = True) -> None:
        """
        Initialize OpenTelemetry with the specified configuration.
        
        Args:
            service_name: Name of the service for tracing
            service_version: Version of the service
            environment: Environment (development, staging, production)
            otlp_endpoint: OTLP endpoint for sending traces (optional)
            enable_console_exporter: Enable console span exporter for development
            enable_requests_instrumentation: Enable HTTP requests instrumentation
            enable_flask_instrumentation: Enable Flask instrumentation
            enable_logging_instrumentation: Enable logging instrumentation
        """
        if self._initialized:
            logger.warning("OpenTelemetry already initialized")
            return
            
        try:
            # Create resource with service information
            resource = Resource.create({
                "service.name": service_name,
                "service.version": service_version,
                "deployment.environment": environment,
                "host.name": os.uname().nodename if hasattr(os, 'uname') else "unknown"
            })
            
            # Create tracer provider
            self._tracer_provider = TracerProvider(resource=resource)
            
            # Add span processors
            if enable_console_exporter:
                console_exporter = ConsoleSpanExporter()
                self._tracer_provider.add_span_processor(
                    BatchSpanProcessor(console_exporter)
                )
            
            # Add OTLP exporter if endpoint is provided
            if otlp_endpoint:
                otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
                self._tracer_provider.add_span_processor(
                    BatchSpanProcessor(otlp_exporter)
                )
            
            # Set the tracer provider
            trace.set_tracer_provider(self._tracer_provider)
            
            # Create tracer
            self._tracer = trace.get_tracer(__name__)
            
            # Enable instrumentations
            if enable_requests_instrumentation:
                RequestsInstrumentor().instrument()
                logger.info("HTTP requests instrumentation enabled")
            
            if enable_flask_instrumentation:
                FlaskInstrumentor().instrument()
                logger.info("Flask instrumentation enabled")
            
            if enable_logging_instrumentation:
                LoggingInstrumentor().instrument()
                logger.info("Logging instrumentation enabled")
            
            self._initialized = True
            logger.info(f"OpenTelemetry initialized for service: {service_name} v{service_version}")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry: {e}")
            raise
    
    def get_tracer(self) -> trace.Tracer:
        """Get the configured tracer"""
        if not self._initialized:
            raise RuntimeError("OpenTelemetry not initialized. Call initialize() first.")
        return self._tracer
    
    def get_tracer_provider(self) -> TracerProvider:
        """Get the tracer provider"""
        if not self._initialized:
            raise RuntimeError("OpenTelemetry not initialized. Call initialize() first.")
        return self._tracer_provider
    
    def generate_correlation_id(self) -> str:
        """Generate a unique correlation ID for request tracking"""
        correlation_id = str(uuid.uuid4())
        self._correlation_id = correlation_id
        return correlation_id
    
    def get_correlation_id(self) -> str | None:
        """Get the current correlation ID"""
        return self._correlation_id
    
    def set_correlation_id(self, correlation_id: str) -> None:
        """Set the correlation ID for the current context"""
        self._correlation_id = correlation_id
    
    @contextmanager
    def trace_operation(self, operation_name: str, attributes: dict[str, Any] | None = None):
        """
        Context manager for tracing operations.
        
        Args:
            operation_name: Name of the operation being traced
            attributes: Additional attributes to add to the span
        """
        if not self._initialized:
            logger.warning("OpenTelemetry not initialized, skipping trace")
            yield
            return
        
        tracer = self.get_tracer()
        with tracer.start_as_current_span(operation_name, attributes=attributes or {}) as span:
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
    
    def add_span_attribute(self, key: str, value: Any) -> None:
        """Add an attribute to the current span"""
        if not self._initialized:
            return
        
        current_span = trace.get_current_span()
        if current_span.is_recording():
            current_span.set_attribute(key, value)
    
    def record_exception(self, exception: Exception) -> None:
        """Record an exception in the current span"""
        if not self._initialized:
            return
        
        current_span = trace.get_current_span()
        if current_span.is_recording():
            current_span.record_exception(exception)
            current_span.set_status(trace.Status(trace.StatusCode.ERROR, str(exception)))
    
    def shutdown(self) -> None:
        """Shutdown OpenTelemetry and flush any remaining spans"""
        if self._tracer_provider:
            self._tracer_provider.shutdown()
            self._initialized = False
            logger.info("OpenTelemetry shutdown complete")

# Global OpenTelemetry configuration instance
ot_config = OpenTelemetryConfig()

def initialize_opentelemetry(**kwargs) -> None:
    """Initialize OpenTelemetry with the given configuration"""
    ot_config.initialize(**kwargs)

def get_tracer() -> trace.Tracer:
    """Get the configured tracer"""
    return ot_config.get_tracer()

def get_correlation_id() -> str | None:
    """Get the current correlation ID"""
    return ot_config.get_correlation_id()

def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current context"""
    ot_config.set_correlation_id(correlation_id)

def generate_correlation_id() -> str:
    """Generate a unique correlation ID"""
    return ot_config.generate_correlation_id()

@contextmanager
def trace_operation(operation_name: str, attributes: dict[str, Any] | None = None):
    """Context manager for tracing operations"""
    with ot_config.trace_operation(operation_name, attributes) as span:
        yield span

def add_span_attribute(key: str, value: Any) -> None:
    """Add an attribute to the current span"""
    ot_config.add_span_attribute(key, value)

def record_exception(exception: Exception) -> None:
    """Record an exception in the current span"""
    ot_config.record_exception(exception)

def shutdown_opentelemetry() -> None:
    """Shutdown OpenTelemetry"""
    ot_config.shutdown() 