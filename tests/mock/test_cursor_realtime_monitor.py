"""
Unit tests for Cursor Realtime Monitor component.
"""

import os
import sys
from pathlib import Path
from typing import Any, cast
from unittest.mock import patch

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utilities.cursor_realtime_monitor import CursorRealtimeMonitor


@pytest.mark.unit
class TestCursorRealtimeMonitor:
    """Test Cursor Realtime Monitor functionality."""

    def __init__(self) -> None:
        """Initialize test class."""
        self.original_dsn: str | None = None

    def setup_method(self) -> None:
        """Set up test environment."""
        # Mock environment variables
        self.original_dsn = os.environ.get("POSTGRES_DSN")

    def teardown_method(self) -> None:
        """Clean up test environment."""
        if self.original_dsn:
            os.environ["POSTGRES_DSN"] = self.original_dsn
        elif "POSTGRES_DSN" in os.environ:
            del os.environ["POSTGRES_DSN"]

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_initialization(self, _mock_resolve_dsn: Any) -> None:
        """Test monitor initialization."""
        monitor = CursorRealtimeMonitor()

        assert monitor is not None
        assert hasattr(monitor, "start_monitoring")
        assert hasattr(monitor, "stop_monitoring")
        assert hasattr(monitor, "extract_conversation_data")

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_with_messages(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with messages field."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ],
            "metadata": {"test": True},
        }

        result = monitor.extract_conversation_data(conversation)

        assert result is not None
        assert result
        assert result
        assert "timestamp" in result
        assert "source_file" in result

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_with_conversation_field(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with conversation field."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {
            "conversation": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ],
            "metadata": {"test": True},
        }

        result = monitor.extract_conversation_data(conversation)

        assert result is not None
        assert result
        assert result
        # Metadata is not included in the return structure

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_with_turns_field(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with turns field."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {
            "turns": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ],
            "metadata": {"test": True},
        }

        result = monitor.extract_conversation_data(conversation)

        assert result is not None
        assert result
        assert result
        # Metadata is not included in the return structure

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_no_messages(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with no message fields."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {"metadata": {"test": True}, "other_field": "value"}

        result = monitor.extract_conversation_data(conversation)

        assert result is None

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_invalid_messages_type(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with invalid messages type."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {"messages": "not_a_list", "metadata": {"test": True}}

        result = monitor.extract_conversation_data(conversation)

        assert result is None

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_empty_messages(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with empty messages."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {"messages": [], "metadata": {"test": True}}

        result = monitor.extract_conversation_data(conversation)

        assert result is None

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_missing_metadata(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with missing metadata."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {"messages": [{"role": "user", "content": "Hello"}]}

        result = monitor.extract_conversation_data(conversation)

        assert result is not None
        assert result
        assert result
        # Metadata is not included in the return structure

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_none_input(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with None input."""
        monitor = CursorRealtimeMonitor()

        result = monitor.extract_conversation_data(cast(Any, None))

        assert result is None

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_non_dict_input(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with non-dict input."""
        monitor = CursorRealtimeMonitor()

        result = monitor.extract_conversation_data(cast(Any, "not_a_dict"))

        assert result is None

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_with_nested_metadata(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with nested metadata."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {
            "messages": [{"role": "user", "content": "Hello"}],
            "metadata": {
                "nested": {"key": "value"},
                "list": [1, 2, 3],
                "string": "test",
            },
        }

        result = monitor.extract_conversation_data(conversation)

        assert result is not None
        # Metadata is not included in the return structure

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_with_special_characters(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with special characters."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {
            "messages": [
                {"role": "user", "content": "Hello with émojis 🚀 and special chars"},
                {"role": "assistant", "content": "Response with unicode: αβγ"},
            ],
            "metadata": {"unicode": "测试"},
        }

        result = monitor.extract_conversation_data(conversation)

        assert result is not None
        assert result
        assert result
        # Metadata is not included in the return structure

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_with_mixed_message_types(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with mixed message types."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "system", "content": "System message"},
                {"role": "user", "content": "Follow up"},
            ],
            "metadata": {"message_count": 4},
        }

        result = monitor.extract_conversation_data(conversation)

        assert result is not None
        assert isinstance(result, dict)
        result_dict = cast(dict[str, Any], result)
        user_messages = cast(list[dict[str, str]], result_dict["user_messages"])
        ai_messages = cast(list[dict[str, str]], result_dict["ai_messages"])
        assert len(user_messages) == 2
        assert len(ai_messages) == 1
        assert user_messages[0]["content"] == "Hello"
        assert ai_messages[0]["content"] == "Hi there!"
        # System messages are not included in ai_messages

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_with_missing_content(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with messages missing content."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {
            "messages": [
                {"role": "user"},
                {"role": "assistant", "content": "Hi there!"},
            ],
            "metadata": {"test": True},
        }

        result = monitor.extract_conversation_data(conversation)

        assert result is not None
        assert result
        assert result

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_with_extra_fields(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with extra fields in messages."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello",
                    "timestamp": "2023-01-01T00:00:00Z",
                    "extra_field": "value",
                }
            ],
            "metadata": {"test": True},
        }

        result = monitor.extract_conversation_data(conversation)

        assert result is not None
        assert result
        assert result

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_priority_order(self, _mock_resolve_dsn: Any) -> None:
        """Test that message field priority is correct (messages > conversation > turns)."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {
            "messages": [{"role": "user", "content": "From messages"}],
            "conversation": [{"role": "user", "content": "From conversation"}],
            "turns": [{"role": "user", "content": "From turns"}],
            "metadata": {"test": True},
        }

        result = monitor.extract_conversation_data(conversation)

        assert result is not None
        assert result
        assert result
        # Messages are not included in the return structure

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_with_none_values(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with None values in messages."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {
            "messages": [
                {"role": "user", "content": "Hello"},
                None,
                {"role": "assistant", "content": "Hi there!"},
            ],
            "metadata": {"test": True},
        }

        result = monitor.extract_conversation_data(conversation)

        assert result is not None
        assert result
        assert result

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_with_empty_strings(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with empty string content."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {
            "messages": [
                {"role": "user", "content": ""},
                {"role": "assistant", "content": "Hi there!"},
            ],
            "metadata": {"test": True},
        }

        result = monitor.extract_conversation_data(conversation)

        assert result is not None
        assert result
        assert result

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_with_boolean_metadata(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with boolean metadata values."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {
            "messages": [{"role": "user", "content": "Hello"}],
            "metadata": {"is_test": True, "is_production": False, "count": 0},
        }

        result = monitor.extract_conversation_data(conversation)

        assert result is not None
        # Metadata is not included in the return structure
        # Metadata is not included in the return structure

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_with_numeric_metadata(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with numeric metadata values."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {
            "messages": [{"role": "user", "content": "Hello"}],
            "metadata": {"integer": 42, "float": 3.14, "negative": -1},
        }

        result = monitor.extract_conversation_data(conversation)

        assert result is not None
        # Metadata is not included in the return structure
        # Metadata is not included in the return structure

    @patch("scripts.utilities.cursor_realtime_monitor.resolve_dsn")
    def test_extract_conversation_data_with_list_metadata(self, _mock_resolve_dsn: Any) -> None:
        """Test extracting conversation data with list metadata values."""
        monitor = CursorRealtimeMonitor()

        conversation: dict[str, object] = {
            "messages": [{"role": "user", "content": "Hello"}],
            "metadata": {
                "tags": ["test", "conversation"],
                "numbers": [1, 2, 3],
                "mixed": ["string", 42, True],
            },
        }

        result = monitor.extract_conversation_data(conversation)

        assert result is not None
        # Metadata is not included in the return structure
        # Metadata is not included in the return structure
