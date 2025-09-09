#!/usr/bin/env python3
"""
Tests for OpenTelemetry configuration module
"""

import unittest
import tempfile
from unittest.mock import patch, MagicMock

from utils.opentelemetry_config import (
    OpenTelemetryConfig,
    initialize_opentelemetry,
    get_tracer,
    get_correlation_id,
    set_correlation_id,
    generate_correlation_id,
    trace_operation,
    add_span_attribute,
    record_exception,
    shutdown_opentelemetry,
    ot_config,
)


class TestOpenTelemetryConfig(unittest.TestCase):
    """Test OpenTelemetry configuration functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.config = OpenTelemetryConfig()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures"""
        if self.config._initialized:
            self.config.shutdown()
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test OpenTelemetry initialization"""
        # Test basic initialization
        self.config.initialize(service_name="test-service", service_version="1.0.0", environment="test")

        self.assertTrue(self.config._initialized)
        self.assertIsNotNone(self.config._tracer)
        self.assertIsNotNone(self.config._tracer_provider)

    def test_initialization_with_otlp(self):
        """Test initialization with OTLP endpoint"""
        with patch("utils.opentelemetry_config.OTLPSpanExporter") as mock_otlp:
            self.config.initialize(service_name="test-service", otlp_endpoint="http://localhost:4317")

            self.assertTrue(self.config._initialized)
            mock_otlp.assert_called_once()

    def test_double_initialization(self):
        """Test that double initialization is handled gracefully"""
        self.config.initialize()
        self.assertTrue(self.config._initialized)

        # Second initialization should be ignored
        with patch("utils.opentelemetry_config.logger") as mock_logger:
            self.config.initialize()
            mock_logger.warning.assert_called_once()

    def test_get_tracer_before_initialization(self):
        """Test getting tracer before initialization raises error"""
        with self.assertRaises(RuntimeError):
            self.config.get_tracer()

    def test_get_tracer_provider_before_initialization(self):
        """Test getting tracer provider before initialization raises error"""
        with self.assertRaises(RuntimeError):
            self.config.get_tracer_provider()

    def test_correlation_id_generation(self):
        """Test correlation ID generation"""
        correlation_id = self.config.generate_correlation_id()

        self.assertIsInstance(correlation_id, str)
        self.assertEqual(len(correlation_id), 36)  # UUID length
        self.assertEqual(self.config.get_correlation_id(), correlation_id)

    def test_correlation_id_setting(self):
        """Test setting correlation ID"""
        test_id = "test-correlation-id"
        self.config.set_correlation_id(test_id)

        self.assertEqual(self.config.get_correlation_id(), test_id)

    def test_trace_operation_context_manager(self):
        """Test trace operation context manager"""
        self.config.initialize()

        with self.config.trace_operation("test-operation") as span:
            self.assertIsNotNone(span)
            span.set_attribute("test.attribute", "test_value")

    def test_trace_operation_without_initialization(self):
        """Test trace operation without initialization"""
        with patch("utils.opentelemetry_config.logger") as mock_logger:
            with self.config.trace_operation("test-operation") as span:
                self.assertIsNone(span)
                mock_logger.warning.assert_called_once()

    def test_add_span_attribute(self):
        """Test adding span attributes"""
        self.config.initialize()

        with self.config.trace_operation("test-operation") as span:
            self.config.add_span_attribute("test.key", "test_value")
            # Attribute should be added to the span

    def test_record_exception(self):
        """Test recording exceptions in spans"""
        self.config.initialize()

        with self.config.trace_operation("test-operation") as span:
            try:
                raise ValueError("Test exception")
            except ValueError as e:
                self.config.record_exception(e)
                # Exception should be recorded in the span

    def test_shutdown(self):
        """Test OpenTelemetry shutdown"""
        self.config.initialize()
        self.assertTrue(self.config._initialized)

        self.config.shutdown()
        self.assertFalse(self.config._initialized)


class TestOpenTelemetryFunctions(unittest.TestCase):
    """Test OpenTelemetry utility functions"""

    def setUp(self):
        """Set up test fixtures"""
        # Reset the global instance for each test
        if ot_config._initialized:
            ot_config.shutdown()

    def tearDown(self):
        """Clean up test fixtures"""
        if ot_config._initialized:
            ot_config.shutdown()

    def test_initialize_opentelemetry(self):
        """Test initialize_opentelemetry function"""
        initialize_opentelemetry(service_name="test-service", service_version="1.0.0")

        self.assertTrue(ot_config._initialized)

    def test_get_tracer_function(self):
        """Test get_tracer function"""
        initialize_opentelemetry()
        tracer = get_tracer()

        self.assertIsNotNone(tracer)

    def test_correlation_id_functions(self):
        """Test correlation ID utility functions"""
        # Test generate_correlation_id
        correlation_id = generate_correlation_id()
        self.assertIsInstance(correlation_id, str)
        self.assertEqual(len(correlation_id), 36)

        # Test set_correlation_id
        test_id = "test-id"
        set_correlation_id(test_id)
        self.assertEqual(get_correlation_id(), test_id)

    def test_trace_operation_function(self):
        """Test trace_operation function"""
        initialize_opentelemetry()

        with trace_operation("test-operation") as span:
            self.assertIsNotNone(span)

    def test_add_span_attribute_function(self):
        """Test add_span_attribute function"""
        initialize_opentelemetry()

        with trace_operation("test-operation") as span:
            add_span_attribute("test.key", "test_value")
            # Attribute should be added

    def test_record_exception_function(self):
        """Test record_exception function"""
        initialize_opentelemetry()

        with trace_operation("test-operation") as span:
            try:
                raise ValueError("Test exception")
            except ValueError as e:
                record_exception(e)
                # Exception should be recorded

    def test_shutdown_opentelemetry(self):
        """Test shutdown_opentelemetry function"""
        initialize_opentelemetry()
        self.assertTrue(ot_config._initialized)

        shutdown_opentelemetry()
        self.assertFalse(ot_config._initialized)


class TestOpenTelemetryIntegration(unittest.TestCase):
    """Test OpenTelemetry integration with file operations"""

    def setUp(self):
        """Set up test fixtures"""
        # Reset the global instance
        if ot_config._initialized:
            ot_config.shutdown()

        initialize_opentelemetry(
            service_name="test-service",
            enable_console_exporter=True,
            enable_requests_instrumentation=False,
            enable_flask_instrumentation=False,
            enable_logging_instrumentation=False,
        )

    def tearDown(self):
        """Clean up test fixtures"""
        shutdown_opentelemetry()

    def test_file_operation_tracing(self):
        """Test tracing file operations"""
        with trace_operation(
            "file_upload", {"file.name": "test.txt", "file.size": 1024, "file.type": "text/plain"}
        ) as span:
            # Simulate file processing
            add_span_attribute("processing.step", "validation")
            add_span_attribute("processing.step", "checksum")

            # Simulate success
            span.set_attribute("result", "success")

    def test_error_tracing(self):
        """Test tracing errors"""
        with trace_operation("file_processing") as span:
            try:
                # Simulate an error
                raise FileNotFoundError("File not found")
            except FileNotFoundError as e:
                record_exception(e)
                span.set_attribute("error.type", "FileNotFoundError")

    def test_correlation_id_propagation(self):
        """Test correlation ID propagation"""
        correlation_id = generate_correlation_id()

        with trace_operation("request_processing") as span:
            span.set_attribute("correlation.id", correlation_id)

            # Simulate nested operation
            with trace_operation("file_validation") as nested_span:
                nested_span.set_attribute("correlation.id", correlation_id)
                nested_span.set_attribute("validation.type", "checksum")


if __name__ == "__main__":
    unittest.main()
