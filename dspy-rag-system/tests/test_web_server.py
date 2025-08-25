"""
Unit tests for Web MCP Server.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch
from xml.etree.ElementTree import Element, SubElement

import httpx
import pytest

from src.utils.mcp_integration.base_server import MCPConfig, MCPError
from src.utils.mcp_integration.web_server import (
    RSSFeed,
    RSSFeedItem,
    WebMCPServer,
    WebServerConfig,
)


class TestWebServerConfig:
    """Test Web Server Configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = WebServerConfig()
        assert config.user_agent == "MCP-Web-Server/1.0"
        assert config.max_redirects == 5
        assert config.rate_limit_delay == 1.0
        assert config.content_size_limit == 5 * 1024 * 1024
        assert config.enable_javascript is False
        assert config.follow_robots_txt is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = WebServerConfig(
            user_agent="Custom-Agent/2.0",
            max_redirects=10,
            rate_limit_delay=2.0,
            content_size_limit=10 * 1024 * 1024,
            enable_javascript=True,
            follow_robots_txt=False,
        )
        assert config.user_agent == "Custom-Agent/2.0"
        assert config.max_redirects == 10
        assert config.rate_limit_delay == 2.0
        assert config.content_size_limit == 10 * 1024 * 1024
        assert config.enable_javascript is True
        assert config.follow_robots_txt is False


class TestRSSFeedModels:
    """Test RSS feed models."""

    def test_rss_feed_item(self):
        """Test RSS feed item creation."""
        item = RSSFeedItem(
            title="Test Item",
            description="Test description",
            link="https://example.com/item",
            pub_date="2024-01-01T00:00:00Z",
            author="Test Author",
            category="Test Category",
        )
        assert item.title == "Test Item"
        assert item.description == "Test description"
        assert item.link == "https://example.com/item"
        assert item.pub_date == "2024-01-01T00:00:00Z"
        assert item.author == "Test Author"
        assert item.category == "Test Category"

    def test_rss_feed(self):
        """Test RSS feed creation."""
        items = [
            RSSFeedItem(title="Item 1", description="Desc 1", link="https://example.com/1"),
            RSSFeedItem(title="Item 2", description="Desc 2", link="https://example.com/2"),
        ]

        feed = RSSFeed(
            title="Test Feed",
            description="Test feed description",
            link="https://example.com/feed",
            language="en",
            items=items,
        )
        assert feed.title == "Test Feed"
        assert feed.description == "Test feed description"
        assert feed.link == "https://example.com/feed"
        assert feed.language == "en"
        assert len(feed.items) == 2


class TestWebMCPServer:
    """Test Web MCP Server."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return MCPConfig(server_name="test_web_server")

    @pytest.fixture
    def server(self, config):
        """Create test server."""
        return WebMCPServer(config)

    def test_server_initialization(self, config):
        """Test server initialization."""
        server = WebMCPServer(config)
        assert server.config == config
        assert server.config.server_name == "test_web_server"
        assert len(server.supported_types) > 0
        assert isinstance(server.web_config, WebServerConfig)

    def test_supported_content_types(self, server):
        """Test supported content types."""
        types = server.get_supported_types()
        assert "text/html" in types
        assert "application/rss+xml" in types
        assert "application/atom+xml" in types
        assert "application/json" in types
        assert "text/xml" in types
        assert "application/xml" in types

    def test_supports_content_type(self, server):
        """Test content type support checking."""
        assert server.supports_content_type("text/html") is True
        assert server.supports_content_type("application/rss+xml") is True
        assert server.supports_content_type("application/json") is True
        assert server.supports_content_type("unsupported/type") is False

    def test_validate_source(self, server):
        """Test source validation."""
        # Valid URLs
        assert server.validate_source("https://example.com") is True
        assert server.validate_source("http://localhost:8080") is True
        assert server.validate_source("https://api.example.com/v1/data") is True

        # Invalid URLs
        assert server.validate_source("") is False
        assert server.validate_source("not-a-url") is False
        # Note: MCPProtocolUtils.validate_url accepts any valid URL scheme, including ftp
        # The web server will handle protocol-specific validation in process_document

    @pytest.mark.asyncio
    async def test_rate_limiting(self, server):
        """Test rate limiting functionality."""
        import time

        start_time = time.time()

        # First call should not delay
        await server._rate_limit()
        first_call_time = time.time() - start_time

        # Second call should delay
        await server._rate_limit()
        second_call_time = time.time() - start_time

        # Second call should take longer due to rate limiting
        assert second_call_time > first_call_time

    @pytest.mark.asyncio
    async def test_detect_content_type_html(self, server):
        """Test content type detection for HTML."""
        with patch.object(server, "_get_session") as mock_get_session:
            mock_response = MagicMock()
            mock_response.headers = {"content-type": "text/html; charset=utf-8"}
            mock_session = AsyncMock()
            mock_session.head.return_value = mock_response
            mock_get_session.return_value = mock_session

            content_type = await server._detect_content_type("https://example.com")
            assert content_type == "text/html"

    @pytest.mark.asyncio
    async def test_detect_content_type_rss(self, server):
        """Test content type detection for RSS."""
        with patch.object(server, "_get_session") as mock_get_session:
            mock_response = MagicMock()
            mock_response.headers = {"content-type": "application/rss+xml"}
            mock_session = AsyncMock()
            mock_session.head.return_value = mock_response
            mock_get_session.return_value = mock_session

            content_type = await server._detect_content_type("https://example.com/feed.rss")
            assert content_type == "application/rss+xml"

    @pytest.mark.asyncio
    async def test_detect_content_type_fallback(self, server):
        """Test content type detection fallback."""
        with patch.object(server, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.head.side_effect = Exception("Network error")
            mock_get_session.return_value = mock_session

            # Should fallback based on URL
            content_type = await server._detect_content_type("https://example.com/feed.rss")
            assert content_type == "application/rss+xml"

            content_type = await server._detect_content_type("https://example.com/data.json")
            assert content_type == "application/json"

            content_type = await server._detect_content_type("https://example.com/page")
            assert content_type == "text/html"

    @pytest.mark.asyncio
    async def test_process_html_content(self, server):
        """Test HTML content processing."""
        html_content = """
        <html>
            <head>
                <title>Test Page</title>
                <meta name="description" content="Test description">
                <meta name="author" content="Test Author">
            </head>
            <body>
                <h1>Hello World</h1>
                <p>This is a test page.</p>
            </body>
        </html>
        """

        with patch.object(server, "_get_session") as mock_get_session:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html_content
            mock_response.content = html_content.encode("utf-8")
            mock_response.headers = {"content-type": "text/html"}
            mock_response.raise_for_status.return_value = None

            mock_session = AsyncMock()
            mock_session.get.return_value = mock_response
            mock_get_session.return_value = mock_session

            result = await server._process_html_content("https://example.com")

            assert result.success is True
            assert "Hello World" in result.content
            assert result.metadata.title == "Test Page"
            assert result.metadata.author == "Test Author"
            assert result.metadata.content_type == "text/html"

    @pytest.mark.asyncio
    async def test_process_json_api(self, server):
        """Test JSON API processing."""
        json_data = {"title": "Test API Response", "author": "API Author", "data": {"key": "value"}}

        with patch.object(server, "_get_session") as mock_get_session:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = json.dumps(json_data)
            mock_response.headers = {"content-type": "application/json"}
            mock_response.raise_for_status.return_value = None

            mock_session = AsyncMock()
            mock_session.get.return_value = mock_response
            mock_get_session.return_value = mock_session

            result = await server._process_json_api("https://api.example.com/data")

            assert result.success is True
            assert '"title": "Test API Response"' in result.content
            assert result.metadata.title == "Test API Response"
            assert result.metadata.author == "API Author"
            assert result.metadata.content_type == "application/json"

    @pytest.mark.asyncio
    async def test_process_rss_feed(self, server):
        """Test RSS feed processing."""
        rss_content = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>Test RSS Feed</title>
                <description>Test feed description</description>
                <link>https://example.com/feed</link>
                <language>en</language>
                <item>
                    <title>Test Item 1</title>
                    <description>Test item description</description>
                    <link>https://example.com/item1</link>
                    <pubDate>2024-01-01T00:00:00Z</pubDate>
                    <author>Test Author</author>
                </item>
            </channel>
        </rss>
        """

        with patch.object(server, "_get_session") as mock_get_session:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = rss_content
            mock_response.headers = {"content-type": "application/rss+xml"}
            mock_response.raise_for_status.return_value = None

            mock_session = AsyncMock()
            mock_session.get.return_value = mock_response
            mock_get_session.return_value = mock_session

            result = await server._process_rss_feed("https://example.com/feed.rss")

            assert result.success is True
            assert "Test RSS Feed" in result.content
            assert "Test Item 1" in result.content
            assert result.metadata.title == "Test RSS Feed"
            assert result.metadata.content_type == "application/rss+xml"

    @pytest.mark.asyncio
    async def test_http_error_handling(self, server):
        """Test HTTP error handling."""
        with patch.object(server, "_get_session") as mock_get_session:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "404 Not Found", request=MagicMock(), response=mock_response
            )

            mock_session = AsyncMock()
            mock_session.get.return_value = mock_response
            mock_get_session.return_value = mock_session

            with pytest.raises(MCPError) as exc_info:
                await server._process_html_content("https://example.com/notfound")

            assert exc_info.value.error_code == "HTTP_ERROR"

    @pytest.mark.asyncio
    async def test_content_too_large(self, server):
        """Test content size limit handling."""
        large_content = "x" * (server.web_config.content_size_limit + 1000)

        with patch.object(server, "_get_session") as mock_get_session:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = large_content
            mock_response.content = large_content.encode("utf-8")
            mock_response.headers = {"content-type": "text/html"}
            mock_response.raise_for_status.return_value = None

            mock_session = AsyncMock()
            mock_session.get.return_value = mock_response
            mock_get_session.return_value = mock_session

            with pytest.raises(MCPError) as exc_info:
                await server._process_html_content("https://example.com/large")

            assert exc_info.value.error_code == "CONTENT_TOO_LARGE"

    @pytest.mark.asyncio
    async def test_parse_rss_format(self, server):
        """Test RSS format parsing."""
        # Create a simple RSS XML structure
        root = Element("rss")
        root.set("version", "2.0")
        channel = SubElement(root, "channel")

        title = SubElement(channel, "title")
        title.text = "Test RSS Feed"

        description = SubElement(channel, "description")
        description.text = "Test description"

        link = SubElement(channel, "link")
        link.text = "https://example.com/feed"

        item = SubElement(channel, "item")
        item_title = SubElement(item, "title")
        item_title.text = "Test Item"
        item_desc = SubElement(item, "description")
        item_desc.text = "Test item description"
        item_link = SubElement(item, "link")
        item_link.text = "https://example.com/item"

        rss_feed = await server._parse_rss_format(root)

        assert rss_feed.title == "Test RSS Feed"
        assert rss_feed.description == "Test description"
        assert rss_feed.link == "https://example.com/feed"
        assert len(rss_feed.items) == 1
        assert rss_feed.items[0].title == "Test Item"

    @pytest.mark.asyncio
    async def test_format_rss_content(self, server):
        """Test RSS content formatting."""
        items = [
            RSSFeedItem(
                title="Item 1",
                description="Description 1",
                link="https://example.com/1",
                pub_date="2024-01-01T00:00:00Z",
                author="Author 1",
                category="Category 1",
            ),
            RSSFeedItem(
                title="Item 2",
                description="Description 2",
                link="https://example.com/2",
                pub_date="2024-01-02T00:00:00Z",
                author="Author 2",
                category="Category 2",
            ),
        ]

        feed = RSSFeed(
            title="Test Feed",
            description="Test description",
            link="https://example.com/feed",
            language="en",
            items=items,
        )

        formatted_content = await server._format_rss_content(feed)

        assert "# Test Feed" in formatted_content
        assert "**Description:** Test description" in formatted_content
        assert "**Language:** en" in formatted_content
        assert "## Latest Items (2)" in formatted_content
        assert "### 1. Item 1" in formatted_content
        assert "### 2. Item 2" in formatted_content
        assert "**Link:** https://example.com/1" in formatted_content
        assert "**Published:** 2024-01-01T00:00:00Z" in formatted_content
        assert "**Author:** Author 1" in formatted_content
        assert "**Category:** Category 1" in formatted_content

    @pytest.mark.asyncio
    async def test_extract_html_metadata(self, server):
        """Test HTML metadata extraction."""
        html_content = """
        <html lang="en">
            <head>
                <title>Test Page Title</title>
                <meta name="description" content="Test page description">
                <meta name="author" content="Test Page Author">
            </head>
            <body>
                <h1>Hello World</h1>
                <p>This is test content.</p>
            </body>
        </html>
        """

        text_content = "Hello World This is test content."

        metadata = await server._extract_html_metadata("https://example.com", html_content, text_content)

        assert metadata.title == "Test Page Title"
        assert metadata.author == "Test Page Author"
        assert metadata.language == "en"
        assert metadata.content_type == "text/html"
        assert metadata.word_count == 6  # "Hello World This is test content"

    @pytest.mark.asyncio
    async def test_cleanup(self, server):
        """Test server cleanup."""
        # Mock session
        mock_session = AsyncMock()
        server._session = mock_session

        await server.cleanup()

        # Session should be closed and set to None
        mock_session.aclose.assert_called_once()
        assert server._session is None

    def test_get_web_config(self, server):
        """Test getting web configuration."""
        config = server.get_web_config()

        assert "user_agent" in config
        assert "max_redirects" in config
        assert "rate_limit_delay" in config
        assert "content_size_limit" in config
        assert "enable_javascript" in config
        assert "follow_robots_txt" in config

    def test_update_web_config(self, server):
        """Test updating web configuration."""
        original_delay = server.web_config.rate_limit_delay

        server.update_web_config(rate_limit_delay=2.0)

        assert server.web_config.rate_limit_delay == 2.0
        assert server.web_config.rate_limit_delay != original_delay

    @pytest.mark.asyncio
    async def test_process_document_invalid_url(self, server):
        """Test processing document with invalid URL."""
        with pytest.raises(MCPError) as exc_info:
            await server.process_document("not-a-url")

        assert exc_info.value.error_code == "INVALID_URL"

    @pytest.mark.asyncio
    async def test_process_document_html(self, server):
        """Test processing HTML document."""
        html_content = "<html><head><title>Test</title></head><body><h1>Hello</h1></body></html>"

        with patch.object(server, "_get_session") as mock_get_session:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html_content
            mock_response.content = html_content.encode("utf-8")
            mock_response.headers = {"content-type": "text/html"}
            mock_response.raise_for_status.return_value = None

            mock_session = AsyncMock()
            mock_session.get.return_value = mock_response
            mock_session.head.return_value = mock_response
            mock_get_session.return_value = mock_session

            result = await server.process_document("https://example.com")

            assert result.success is True
            assert "Hello" in result.content
            assert result.metadata.content_type == "text/html"

    @pytest.mark.asyncio
    async def test_process_document_rss(self, server):
        """Test processing RSS document."""
        rss_content = """<?xml version="1.0" encoding="UTF-8"?>
        <rss version="2.0">
            <channel>
                <title>Test Feed</title>
                <description>Test description</description>
                <link>https://example.com/feed</link>
            </channel>
        </rss>
        """

        with patch.object(server, "_get_session") as mock_get_session:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = rss_content
            mock_response.headers = {"content-type": "application/rss+xml"}
            mock_response.raise_for_status.return_value = None

            mock_session = AsyncMock()
            mock_session.get.return_value = mock_response
            mock_session.head.return_value = mock_response
            mock_get_session.return_value = mock_session

            result = await server.process_document("https://example.com/feed.rss")

            assert result.success is True
            assert "Test Feed" in result.content
            assert result.metadata.content_type == "application/rss+xml"
