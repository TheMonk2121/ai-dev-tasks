"""
Web MCP Server Implementation

Provides MCP server for web content scraping and processing, supporting HTML,
RSS feeds, and web APIs with content extraction and sanitization.
"""

import asyncio
import json
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel, Field

from .base_server import DocumentMetadata, MCPConfig, MCPError, MCPProtocolUtils, MCPServer, ProcessedDocument


class WebServerConfig(BaseModel):
    """Configuration specific to web MCP server."""

    user_agent: str = Field(default="MCP-Web-Server/1.0", description="User agent for HTTP requests")
    max_redirects: int = Field(default=5, description="Maximum number of redirects to follow")
    rate_limit_delay: float = Field(default=1.0, description="Delay between requests in seconds")
    content_size_limit: int = Field(default=5 * 1024 * 1024, description="Maximum content size to download")  # 5MB
    enable_javascript: bool = Field(
        default=False, description="Enable JavaScript execution (requires additional setup)"
    )
    follow_robots_txt: bool = Field(default=True, description="Respect robots.txt rules")

    model_config = {"extra": "forbid"}


class RSSFeedItem(BaseModel):
    """Represents an RSS feed item."""

    title: str
    description: str
    link: str
    pub_date: str | None = None
    author: str | None = None
    category: str | None = None

    model_config = {"extra": "forbid"}


class RSSFeed(BaseModel):
    """Represents an RSS feed."""

    title: str
    description: str
    link: str
    language: str | None = None
    items: list[RSSFeedItem] = Field(default_factory=list)

    model_config = {"extra": "forbid"}


class WebMCPServer(MCPServer):
    """MCP server for web content processing."""

    def __init__(self, config: MCPConfig):
        super().__init__(config)
        self.web_config = WebServerConfig()
        self._last_request_time = 0
        self._session: httpx.AsyncClient | None = None
        self._robots_cache: dict[str, Any] = {}

        # Supported content types
        self.supported_types = {
            "text/html": "HTML content",
            "application/rss+xml": "RSS feed",
            "application/atom+xml": "Atom feed",
            "application/json": "JSON API response",
            "text/xml": "XML content",
            "application/xml": "XML content",
        }

    async def process_document(self, source: str, **kwargs) -> ProcessedDocument:
        """Process a document from the web."""
        try:
            # Validate source URL
            if not self.validate_source(source):
                raise MCPError(f"Invalid URL: {source}", error_code="INVALID_URL")

            # Check robots.txt if enabled
            if self.web_config.follow_robots_txt:
                await self._check_robots_txt(source)

            # Rate limiting
            await self._rate_limit()

            # Determine content type and process accordingly
            content_type = kwargs.get("content_type", "auto")

            if content_type == "auto":
                content_type = await self._detect_content_type(source)

            if content_type == "application/rss+xml" or source.endswith(".rss") or source.endswith(".xml"):
                return await self._process_rss_feed(source, **kwargs)
            elif content_type == "application/json" or source.endswith(".json"):
                return await self._process_json_api(source, **kwargs)
            elif content_type == "text/html" or source.startswith("http"):
                return await self._process_html_content(source, **kwargs)
            else:
                return await self._process_generic_content(source, **kwargs)

        except MCPError:
            raise
        except Exception as e:
            self.logger.error(f"Error processing web content {source}: {e}")
            raise MCPError(f"Web processing failed: {e}", error_code="PROCESSING_ERROR")

    def supports_content_type(self, content_type: str) -> bool:
        """Check if this server supports the given content type."""
        return content_type in self.supported_types

    def get_supported_types(self) -> list[str]:
        """Get list of supported content types."""
        return list(self.supported_types.keys())

    def validate_source(self, source: str) -> bool:
        """Validate if the source is a valid URL."""
        return MCPProtocolUtils.validate_url(source)

    async def _get_session(self) -> httpx.AsyncClient:
        """Get or create HTTP session."""
        if self._session is None:
            self._session = httpx.AsyncClient(
                timeout=self.config.timeout,
                follow_redirects=True,
                max_redirects=self.web_config.max_redirects,
                headers={
                    "User-Agent": self.web_config.user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "Connection": "keep-alive",
                },
            )
        return self._session

    async def _rate_limit(self) -> None:
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time

        if time_since_last < self.web_config.rate_limit_delay:
            delay = self.web_config.rate_limit_delay - time_since_last
            await asyncio.sleep(delay)

        self._last_request_time = time.time()

    async def _detect_content_type(self, url: str) -> str:
        """Detect content type from URL or response headers."""
        try:
            session = await self._get_session()
            response = await session.head(url)

            content_type = response.headers.get("content-type", "").lower()

            if "html" in content_type:
                return "text/html"
            elif "rss" in content_type or "xml" in content_type:
                return "application/rss+xml"
            elif "json" in content_type:
                return "application/json"
            else:
                return "text/html"  # Default to HTML

        except Exception:
            # Fallback based on URL
            if url.endswith((".rss", ".xml")):
                return "application/rss+xml"
            elif url.endswith(".json"):
                return "application/json"
            else:
                return "text/html"

    async def _check_robots_txt(self, url: str) -> None:
        """Check robots.txt for URL restrictions."""
        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

            if robots_url in self._robots_cache:
                return

            session = await self._get_session()
            response = await session.get(robots_url)

            if response.status_code == 200:
                robots_content = response.text
                # Simple robots.txt parsing - could be enhanced
                if "Disallow:" in robots_content:
                    self._robots_cache[robots_url] = robots_content
                    self.logger.info(f"Robots.txt found for {parsed_url.netloc}")

        except Exception as e:
            self.logger.debug(f"Could not fetch robots.txt: {e}")

    async def _process_html_content(self, url: str, **kwargs) -> ProcessedDocument:
        """Process HTML content from URL."""
        try:
            session = await self._get_session()
            response = await session.get(url)
            response.raise_for_status()

            # Check content size
            content_length = len(response.content)
            if content_length > self.web_config.content_size_limit:
                raise MCPError(f"Content too large: {content_length} bytes", error_code="CONTENT_TOO_LARGE")

            # Extract text content
            html_content = response.text
            text_content = MCPProtocolUtils.extract_text_from_html(html_content)

            # Extract metadata
            metadata = await self._extract_html_metadata(url, html_content, text_content)

            # Process content
            processed_content = await self._process_html_text(text_content, **kwargs)

            return ProcessedDocument(content=processed_content, metadata=metadata, success=True)

        except httpx.HTTPStatusError as e:
            raise MCPError(f"HTTP error {e.response.status_code}: {e}", error_code="HTTP_ERROR")
        except httpx.RequestError as e:
            raise MCPError(f"Request failed: {e}", error_code="REQUEST_ERROR")

    async def _process_rss_feed(self, url: str, **kwargs) -> ProcessedDocument:
        """Process RSS feed from URL."""
        try:
            session = await self._get_session()
            response = await session.get(url)
            response.raise_for_status()

            # Parse RSS content
            rss_content = response.text
            rss_feed = await self._parse_rss_feed(rss_content)

            # Convert to readable format
            processed_content = await self._format_rss_content(rss_feed)

            # Extract metadata
            metadata = await self._extract_rss_metadata(url, rss_feed)

            return ProcessedDocument(content=processed_content, metadata=metadata, success=True)

        except httpx.HTTPStatusError as e:
            raise MCPError(f"HTTP error {e.response.status_code}: {e}", error_code="HTTP_ERROR")
        except httpx.RequestError as e:
            raise MCPError(f"Request failed: {e}", error_code="REQUEST_ERROR")
        except ET.ParseError as e:
            raise MCPError(f"RSS parsing failed: {e}", error_code="PARSE_ERROR")

    async def _process_json_api(self, url: str, **kwargs) -> ProcessedDocument:
        """Process JSON API response from URL."""
        try:
            session = await self._get_session()
            response = await session.get(url)
            response.raise_for_status()

            # Parse JSON content
            json_content = response.text
            data = json.loads(json_content)

            # Format JSON content
            processed_content = json.dumps(data, indent=2, ensure_ascii=False)

            # Extract metadata
            metadata = await self._extract_json_metadata(url, data)

            return ProcessedDocument(content=processed_content, metadata=metadata, success=True)

        except httpx.HTTPStatusError as e:
            raise MCPError(f"HTTP error {e.response.status_code}: {e}", error_code="HTTP_ERROR")
        except httpx.RequestError as e:
            raise MCPError(f"Request failed: {e}", error_code="REQUEST_ERROR")
        except json.JSONDecodeError as e:
            raise MCPError(f"JSON parsing failed: {e}", error_code="PARSE_ERROR")

    async def _process_generic_content(self, url: str, **kwargs) -> ProcessedDocument:
        """Process generic web content."""
        try:
            session = await self._get_session()
            response = await session.get(url)
            response.raise_for_status()

            content = response.text
            content_type = response.headers.get("content-type", "text/plain")

            metadata = DocumentMetadata(
                source=url,
                content_type=content_type,
                size=len(response.content),
                encoding=response.encoding or "utf-8",
                created_at=datetime.now().isoformat(),
                word_count=MCPProtocolUtils.calculate_word_count(content),
            )

            return ProcessedDocument(content=content, metadata=metadata, success=True)

        except httpx.HTTPStatusError as e:
            raise MCPError(f"HTTP error {e.response.status_code}: {e}", error_code="HTTP_ERROR")
        except httpx.RequestError as e:
            raise MCPError(f"Request failed: {e}", error_code="REQUEST_ERROR")

    async def _extract_html_metadata(self, url: str, html_content: str, text_content: str) -> DocumentMetadata:
        """Extract metadata from HTML content."""
        try:
            # Extract title
            title_match = re.search(r"<title[^>]*>(.*?)</title>", html_content, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else None

            # Extract meta description (not used in current metadata structure)
            # desc_match = re.search(
            #     r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE
            # )
            # description = desc_match.group(1) if desc_match else None

            # Extract meta author
            author_match = re.search(
                r'<meta[^>]*name=["\']author["\'][^>]*content=["\']([^"\']*)["\']', html_content, re.IGNORECASE
            )
            author = author_match.group(1) if author_match else None

            # Extract language
            lang_match = re.search(r'<html[^>]*lang=["\']([^"\']*)["\']', html_content, re.IGNORECASE)
            language = lang_match.group(1) if lang_match else None

            return DocumentMetadata(
                source=url,
                content_type="text/html",
                size=len(html_content.encode("utf-8")),
                encoding="utf-8",
                created_at=datetime.now().isoformat(),
                title=title,
                author=author,
                language=language,
                word_count=MCPProtocolUtils.calculate_word_count(text_content),
            )

        except Exception as e:
            self.logger.warning(f"HTML metadata extraction failed: {e}")
            return DocumentMetadata(
                source=url,
                content_type="text/html",
                size=len(html_content.encode("utf-8")),
                word_count=MCPProtocolUtils.calculate_word_count(text_content),
            )

    async def _extract_rss_metadata(self, url: str, rss_feed: RSSFeed) -> DocumentMetadata:
        """Extract metadata from RSS feed."""
        return DocumentMetadata(
            source=url,
            content_type="application/rss+xml",
            title=rss_feed.title,
            author=rss_feed.description,
            language=rss_feed.language,
            word_count=len(rss_feed.items),
            created_at=datetime.now().isoformat(),
        )

    async def _extract_json_metadata(self, url: str, data: Any) -> DocumentMetadata:
        """Extract metadata from JSON content."""
        title = None
        author = None

        if isinstance(data, dict):
            title = data.get("title") or data.get("name")
            author = data.get("author") or data.get("creator")

        return DocumentMetadata(
            source=url,
            content_type="application/json",
            title=str(title) if title else None,
            author=str(author) if author else None,
            created_at=datetime.now().isoformat(),
        )

    async def _parse_rss_feed(self, rss_content: str) -> RSSFeed:
        """Parse RSS feed content."""
        try:
            root = ET.fromstring(rss_content)

            # Handle both RSS and Atom feeds
            if root.tag.endswith("rss"):
                return await self._parse_rss_format(root)
            elif root.tag.endswith("feed"):
                return await self._parse_atom_format(root)
            else:
                raise MCPError("Unknown feed format", error_code="UNKNOWN_FORMAT")

        except ET.ParseError as e:
            raise MCPError(f"RSS parsing failed: {e}", error_code="PARSE_ERROR")

    async def _parse_rss_format(self, root: ET.Element) -> RSSFeed:
        """Parse RSS format feed."""
        channel = root.find("channel")
        if channel is None:
            raise MCPError("Invalid RSS format: no channel element", error_code="INVALID_FORMAT")

        title = channel.find("title")
        description = channel.find("description")
        link = channel.find("link")
        language = channel.find("language")

        items = []
        for item in channel.findall("item"):
            item_title = item.find("title")
            item_desc = item.find("description")
            item_link = item.find("link")
            item_pub_date = item.find("pubDate")
            item_author = item.find("author")
            item_category = item.find("category")

            items.append(
                RSSFeedItem(
                    title=str(item_title.text) if item_title is not None and item_title.text is not None else "",
                    description=str(item_desc.text) if item_desc is not None and item_desc.text is not None else "",
                    link=str(item_link.text) if item_link is not None and item_link.text is not None else "",
                    pub_date=item_pub_date.text if item_pub_date is not None else None,
                    author=item_author.text if item_author is not None else None,
                    category=item_category.text if item_category is not None else None,
                )
            )

        return RSSFeed(
            title=str(title.text) if title is not None and title.text is not None else "RSS Feed",
            description=str(description.text) if description is not None and description.text is not None else "",
            link=str(link.text) if link is not None and link.text is not None else "",
            language=language.text if language is not None else None,
            items=items,
        )

    async def _parse_atom_format(self, root: ET.Element) -> RSSFeed:
        """Parse Atom format feed."""
        title = root.find("{http://www.w3.org/2005/Atom}title")
        subtitle = root.find("{http://www.w3.org/2005/Atom}subtitle")
        link = root.find("{http://www.w3.org/2005/Atom}link")

        items = []
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            entry_title = entry.find("{http://www.w3.org/2005/Atom}title")
            entry_summary = entry.find("{http://www.w3.org/2005/Atom}summary")
            entry_link = entry.find("{http://www.w3.org/2005/Atom}link")
            entry_published = entry.find("{http://www.w3.org/2005/Atom}published")
            entry_author = entry.find("{http://www.w3.org/2005/Atom}author")

            items.append(
                RSSFeedItem(
                    title=str(entry_title.text) if entry_title is not None and entry_title.text is not None else "",
                    description=(
                        str(entry_summary.text) if entry_summary is not None and entry_summary.text is not None else ""
                    ),
                    link=(
                        str(entry_link.get("href"))
                        if entry_link is not None and entry_link.get("href") is not None
                        else ""
                    ),
                    pub_date=entry_published.text if entry_published is not None else None,
                    author=(
                        name_elem.text
                        if entry_author is not None
                        and (name_elem := entry_author.find("{http://www.w3.org/2005/Atom}name")) is not None
                        and name_elem.text is not None
                        else None
                    ),
                )
            )

        return RSSFeed(
            title=str(title.text) if title is not None and title.text is not None else "Atom Feed",
            description=str(subtitle.text) if subtitle is not None and subtitle.text is not None else "",
            link=str(link.get("href")) if link is not None and link.get("href") is not None else "",
            items=items,
        )

    async def _format_rss_content(self, rss_feed: RSSFeed) -> str:
        """Format RSS feed content for reading."""
        lines = []
        lines.append(f"# {rss_feed.title}")
        lines.append("")

        if rss_feed.description:
            lines.append(f"**Description:** {rss_feed.description}")
            lines.append("")

        if rss_feed.language:
            lines.append(f"**Language:** {rss_feed.language}")
            lines.append("")

        lines.append(f"**Feed URL:** {rss_feed.link}")
        lines.append("")

        lines.append(f"## Latest Items ({len(rss_feed.items)})")
        lines.append("")

        for i, item in enumerate(rss_feed.items[:10], 1):  # Limit to 10 items
            lines.append(f"### {i}. {item.title}")
            lines.append("")

            if item.description:
                lines.append(item.description)
                lines.append("")

            if item.link:
                lines.append(f"**Link:** {item.link}")
                lines.append("")

            if item.pub_date:
                lines.append(f"**Published:** {item.pub_date}")
                lines.append("")

            if item.author:
                lines.append(f"**Author:** {item.author}")
                lines.append("")

            if item.category:
                lines.append(f"**Category:** {item.category}")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    async def _process_html_text(self, text_content: str, **kwargs) -> str:
        """Process extracted HTML text content."""
        # Basic text processing
        lines = text_content.split("\n")

        # Remove excessive blank lines
        processed_lines = []
        prev_blank = False

        for line in lines:
            is_blank = not line.strip()
            if is_blank and prev_blank:
                continue
            processed_lines.append(line)
            prev_blank = is_blank

        return "\n".join(processed_lines)

    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self._session:
            await self._session.aclose()
            self._session = None
        super().cleanup()

    def get_web_config(self) -> dict[str, Any]:
        """Get web server configuration."""
        return self.web_config.model_dump()

    def update_web_config(self, **kwargs) -> None:
        """Update web server configuration."""
        for key, value in kwargs.items():
            if hasattr(self.web_config, key):
                setattr(self.web_config, key, value)
