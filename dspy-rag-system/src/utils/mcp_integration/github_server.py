"""
GitHub MCP Server Implementation

Provides MCP server for GitHub repository content processing, supporting
repository files, issues, pull requests, and documentation with GitHub API integration.
"""

import asyncio
import base64
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel, Field

from .base_server import DocumentMetadata, MCPConfig, MCPError, MCPProtocolUtils, MCPServer, ProcessedDocument


class GitHubServerConfig(BaseModel):
    """Configuration specific to GitHub MCP server."""

    api_token: Optional[str] = Field(default=None, description="GitHub API token for authenticated requests")
    rate_limit_delay: float = Field(default=1.0, description="Delay between API requests in seconds")
    max_file_size: int = Field(default=1024 * 1024, description="Maximum file size to download")  # 1MB
    include_issues: bool = Field(default=True, description="Include issues in repository processing")
    include_pull_requests: bool = Field(default=True, description="Include pull requests in repository processing")
    include_wiki: bool = Field(default=False, description="Include wiki pages in repository processing")
    max_items_per_type: int = Field(
        default=50, description="Maximum number of items to fetch per type (issues, PRs, etc.)"
    )

    model_config = {"extra": "forbid"}


class GitHubRepository(BaseModel):
    """GitHub repository information."""

    name: str
    full_name: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    issues_count: int = 0
    pull_requests_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    default_branch: str = "main"

    model_config = {"extra": "forbid"}


class GitHubIssue(BaseModel):
    """GitHub issue information."""

    number: int
    title: str
    body: Optional[str] = None
    state: str
    author: Optional[str] = None
    assignees: List[str] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    comments_count: int = 0

    model_config = {"extra": "forbid"}


class GitHubPullRequest(BaseModel):
    """GitHub pull request information."""

    number: int
    title: str
    body: Optional[str] = None
    state: str
    author: Optional[str] = None
    assignees: List[str] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    comments_count: int = 0
    review_comments_count: int = 0
    commits_count: int = 0
    changed_files: int = 0

    model_config = {"extra": "forbid"}


class GitHubMCPServer(MCPServer):
    """MCP server for GitHub repository processing."""

    def __init__(self, config: MCPConfig):
        super().__init__(config)
        self.github_config = GitHubServerConfig()
        self._session: Optional[httpx.AsyncClient] = None
        self._last_request_time = 0

        # Supported content types
        self.supported_types = {
            "github/repository": "GitHub repository",
            "github/file": "GitHub repository file",
            "github/issue": "GitHub issue",
            "github/pull_request": "GitHub pull request",
            "github/wiki": "GitHub wiki page",
        }

    async def process_document(self, source: str, **kwargs) -> ProcessedDocument:
        """Process a GitHub repository or specific content."""
        try:
            # Validate source
            if not self.validate_source(source):
                raise MCPError(f"Invalid GitHub source: {source}", error_code="INVALID_SOURCE")

            # Parse GitHub URL
            repo_info = self._parse_github_url(source)

            # Determine content type and process accordingly
            content_type = kwargs.get("content_type", "auto")

            if content_type == "auto":
                content_type = await self._detect_content_type(source, repo_info)

            if content_type == "github/repository":
                return await self._process_repository(source, repo_info, **kwargs)
            elif content_type == "github/file":
                return await self._process_file(source, repo_info, **kwargs)
            elif content_type == "github/issue":
                return await self._process_issue(source, repo_info, **kwargs)
            elif content_type == "github/pull_request":
                return await self._process_pull_request(source, repo_info, **kwargs)
            elif content_type == "github/wiki":
                return await self._process_wiki(source, repo_info, **kwargs)
            else:
                return await self._process_repository(source, repo_info, **kwargs)

        except MCPError:
            raise
        except Exception as e:
            self.logger.error(f"Error processing GitHub content {source}: {e}")
            raise MCPError(f"GitHub processing failed: {e}", error_code="PROCESSING_ERROR")

    def supports_content_type(self, content_type: str) -> bool:
        """Check if this server supports the given content type."""
        return content_type in self.supported_types

    def get_supported_types(self) -> List[str]:
        """Get list of supported content types."""
        return list(self.supported_types.keys())

    def validate_source(self, source: str) -> bool:
        """Validate if the source is a valid GitHub URL."""
        try:
            if not source or not source.strip():
                return False

            # Check if it's a GitHub URL
            if not source.startswith(("https://github.com/", "http://github.com/")):
                return False

            # Parse URL to ensure it's valid
            parsed = urlparse(source)
            if parsed.netloc != "github.com":
                return False

            return True

        except Exception as e:
            self.logger.error(f"Source validation failed: {e}")
            return False

    def _parse_github_url(self, url: str) -> Dict[str, str]:
        """Parse GitHub URL to extract repository and path information."""
        try:
            parsed = urlparse(url)
            path_parts = parsed.path.strip("/").split("/")

            if len(path_parts) < 2:
                raise MCPError("Invalid GitHub URL format", error_code="INVALID_URL_FORMAT")

            repo_info = {
                "owner": path_parts[0],
                "repo": path_parts[1],
                "branch": "main",  # Default branch
                "path": "",
                "type": "repository",
            }

            # Handle different URL patterns
            if len(path_parts) >= 3:
                if path_parts[2] == "blob":
                    # File: /owner/repo/blob/branch/path
                    repo_info["type"] = "file"
                    repo_info["branch"] = path_parts[3] if len(path_parts) > 3 else "main"
                    repo_info["path"] = "/".join(path_parts[4:]) if len(path_parts) > 4 else ""
                elif path_parts[2] == "issues":
                    # Issue: /owner/repo/issues/number
                    repo_info["type"] = "issue"
                    repo_info["issue_number"] = path_parts[3] if len(path_parts) > 3 else ""
                elif path_parts[2] == "pull":
                    # Pull request: /owner/repo/pull/number
                    repo_info["type"] = "pull_request"
                    repo_info["pr_number"] = path_parts[3] if len(path_parts) > 3 else ""
                elif path_parts[2] == "wiki":
                    # Wiki: /owner/repo/wiki/page
                    repo_info["type"] = "wiki"
                    repo_info["page"] = path_parts[3] if len(path_parts) > 3 else "Home"
                else:
                    # Repository root or other content
                    repo_info["path"] = "/".join(path_parts[2:])

            return repo_info

        except Exception as e:
            raise MCPError(f"Failed to parse GitHub URL: {e}", error_code="URL_PARSING_ERROR")

    async def _detect_content_type(self, url: str, repo_info: Dict[str, str]) -> str:
        """Detect content type from GitHub URL."""
        return f"github/{repo_info['type']}"

    async def _get_session(self) -> httpx.AsyncClient:
        """Get or create HTTP session."""
        if self._session is None:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "MCP-GitHub-Server/1.0",
            }

            if self.github_config.api_token:
                headers["Authorization"] = f"token {self.github_config.api_token}"

            self._session = httpx.AsyncClient(
                timeout=self.config.timeout,
                headers=headers,
            )
        return self._session

    async def _rate_limit(self) -> None:
        """Implement rate limiting."""
        import time

        current_time = time.time()
        time_since_last = current_time - self._last_request_time

        if time_since_last < self.github_config.rate_limit_delay:
            delay = self.github_config.rate_limit_delay - time_since_last
            await asyncio.sleep(delay)

        self._last_request_time = time.time()

    async def _make_api_request(self, endpoint: str) -> Dict[str, Any]:
        """Make a GitHub API request."""
        await self._rate_limit()

        session = await self._get_session()
        url = f"https://api.github.com{endpoint}"

        try:
            response = await session.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise MCPError("GitHub resource not found", error_code="RESOURCE_NOT_FOUND")
            elif e.response.status_code == 403:
                raise MCPError("GitHub API rate limit exceeded", error_code="RATE_LIMIT_EXCEEDED")
            else:
                raise MCPError(f"GitHub API error: {e.response.status_code}", error_code="API_ERROR")
        except httpx.RequestError as e:
            raise MCPError(f"GitHub API request failed: {e}", error_code="REQUEST_ERROR")

    async def _process_repository(self, url: str, repo_info: Dict[str, str], **kwargs) -> ProcessedDocument:
        """Process a GitHub repository."""
        try:
            # Get repository information
            repo_data = await self._make_api_request(f"/repos/{repo_info['owner']}/{repo_info['repo']}")

            # Get README if available
            readme_content = ""
            try:
                readme_data = await self._make_api_request(f"/repos/{repo_info['owner']}/{repo_info['repo']}/readme")
                if readme_data.get("content"):
                    readme_content = base64.b64decode(readme_data["content"]).decode("utf-8")
            except MCPError:
                # README not found, continue without it
                pass

            # Get issues if enabled
            issues_content = ""
            if self.github_config.include_issues:
                try:
                    issues_data = await self._make_api_request(
                        f"/repos/{repo_info['owner']}/{repo_info['repo']}/issues?state=all&per_page={self.github_config.max_items_per_type}"
                    )
                    if isinstance(issues_data, list):
                        issues_content = await self._format_issues(issues_data)
                    else:
                        issues_content = "Error: Invalid issues data format"
                except MCPError:
                    pass

            # Get pull requests if enabled
            prs_content = ""
            if self.github_config.include_pull_requests:
                try:
                    prs_data = await self._make_api_request(
                        f"/repos/{repo_info['owner']}/{repo_info['repo']}/pulls?state=all&per_page={self.github_config.max_items_per_type}"
                    )
                    if isinstance(prs_data, list):
                        prs_content = await self._format_pull_requests(prs_data)
                    else:
                        prs_content = "Error: Invalid pull requests data format"
                except MCPError:
                    pass

            # Combine content
            content_parts = []

            # Repository header
            content_parts.append(f"# {repo_data['full_name']}")
            if repo_data.get("description"):
                content_parts.append(f"\n{repo_data['description']}")

            content_parts.append(f"\n**Language:** {repo_data.get('language', 'Unknown')}")
            content_parts.append(f"**Stars:** {repo_data.get('stargazers_count', 0)}")
            content_parts.append(f"**Forks:** {repo_data.get('forks_count', 0)}")
            content_parts.append(f"**Issues:** {repo_data.get('open_issues_count', 0)}")
            content_parts.append(f"**Created:** {repo_data.get('created_at', 'Unknown')}")
            content_parts.append(f"**Updated:** {repo_data.get('updated_at', 'Unknown')}")

            # README content
            if readme_content:
                content_parts.append(f"\n## README\n\n{readme_content}")

            # Issues
            if issues_content:
                content_parts.append(f"\n## Issues\n\n{issues_content}")

            # Pull Requests
            if prs_content:
                content_parts.append(f"\n## Pull Requests\n\n{prs_content}")

            content = "\n".join(content_parts)

            # Create metadata
            metadata = DocumentMetadata(
                source=url,
                content_type="github/repository",
                title=repo_data["full_name"],
                author=repo_data["owner"]["login"],
                created_at=repo_data.get("created_at"),
                modified_at=repo_data.get("updated_at"),
                word_count=MCPProtocolUtils.calculate_word_count(content),
            )

            return ProcessedDocument(content=content, metadata=metadata, success=True)

        except Exception as e:
            raise MCPError(f"Repository processing failed: {e}", error_code="PROCESSING_ERROR")

    async def _process_file(self, url: str, repo_info: Dict[str, str], **kwargs) -> ProcessedDocument:
        """Process a GitHub repository file."""
        try:
            # Get file content
            file_data = await self._make_api_request(
                f"/repos/{repo_info['owner']}/{repo_info['repo']}/contents/{repo_info['path']}?ref={repo_info['branch']}"
            )

            if file_data.get("type") != "file":
                raise MCPError("Not a file", error_code="NOT_A_FILE")

            # Check file size
            if file_data.get("size", 0) > self.github_config.max_file_size:
                raise MCPError("File too large", error_code="FILE_TOO_LARGE")

            # Decode content
            content = base64.b64decode(file_data["content"]).decode("utf-8")

            # Create metadata
            metadata = DocumentMetadata(
                source=url,
                content_type="github/file",
                title=file_data["name"],
                author=file_data["owner"]["login"],
                created_at=file_data.get("created_at"),
                modified_at=file_data.get("updated_at"),
                word_count=MCPProtocolUtils.calculate_word_count(content),
            )

            return ProcessedDocument(content=content, metadata=metadata, success=True)

        except Exception as e:
            raise MCPError(f"File processing failed: {e}", error_code="PROCESSING_ERROR")

    async def _process_issue(self, url: str, repo_info: Dict[str, str], **kwargs) -> ProcessedDocument:
        """Process a GitHub issue."""
        try:
            issue_number = repo_info.get("issue_number")
            if not issue_number:
                raise MCPError("Issue number not found in URL", error_code="INVALID_URL_FORMAT")

            # Get issue data
            issue_data = await self._make_api_request(
                f"/repos/{repo_info['owner']}/{repo_info['repo']}/issues/{issue_number}"
            )

            # Format issue content
            content_parts = []
            content_parts.append(f"# Issue #{issue_data['number']}: {issue_data['title']}")
            content_parts.append(f"\n**State:** {issue_data['state']}")
            content_parts.append(f"**Author:** {issue_data['user']['login']}")
            content_parts.append(f"**Created:** {issue_data['created_at']}")
            content_parts.append(f"**Updated:** {issue_data['updated_at']}")

            if issue_data.get("assignees"):
                assignees = [assignee["login"] for assignee in issue_data["assignees"]]
                content_parts.append(f"**Assignees:** {', '.join(assignees)}")

            if issue_data.get("labels"):
                labels = [label["name"] for label in issue_data["labels"]]
                content_parts.append(f"**Labels:** {', '.join(labels)}")

            if issue_data.get("body"):
                content_parts.append(f"\n## Description\n\n{issue_data['body']}")

            content = "\n".join(content_parts)

            # Create metadata
            metadata = DocumentMetadata(
                source=url,
                content_type="github/issue",
                title=f"Issue #{issue_data['number']}: {issue_data['title']}",
                author=issue_data["user"]["login"],
                created_at=issue_data["created_at"],
                modified_at=issue_data["updated_at"],
                word_count=MCPProtocolUtils.calculate_word_count(content),
            )

            return ProcessedDocument(content=content, metadata=metadata, success=True)

        except Exception as e:
            raise MCPError(f"Issue processing failed: {e}", error_code="PROCESSING_ERROR")

    async def _process_pull_request(self, url: str, repo_info: Dict[str, str], **kwargs) -> ProcessedDocument:
        """Process a GitHub pull request."""
        try:
            pr_number = repo_info.get("pr_number")
            if not pr_number:
                raise MCPError("Pull request number not found in URL", error_code="INVALID_URL_FORMAT")

            # Get PR data
            pr_data = await self._make_api_request(f"/repos/{repo_info['owner']}/{repo_info['repo']}/pulls/{pr_number}")

            # Format PR content
            content_parts = []
            content_parts.append(f"# Pull Request #{pr_data['number']}: {pr_data['title']}")
            content_parts.append(f"\n**State:** {pr_data['state']}")
            content_parts.append(f"**Author:** {pr_data['user']['login']}")
            content_parts.append(f"**Created:** {pr_data['created_at']}")
            content_parts.append(f"**Updated:** {pr_data['updated_at']}")
            content_parts.append(f"**Commits:** {pr_data['commits']}")
            content_parts.append(f"**Changed Files:** {pr_data['changed_files']}")
            content_parts.append(f"**Comments:** {pr_data['comments']}")
            content_parts.append(f"**Review Comments:** {pr_data['review_comments']}")

            if pr_data.get("assignees"):
                assignees = [assignee["login"] for assignee in pr_data["assignees"]]
                content_parts.append(f"**Assignees:** {', '.join(assignees)}")

            if pr_data.get("labels"):
                labels = [label["name"] for label in pr_data["labels"]]
                content_parts.append(f"**Labels:** {', '.join(labels)}")

            if pr_data.get("body"):
                content_parts.append(f"\n## Description\n\n{pr_data['body']}")

            content = "\n".join(content_parts)

            # Create metadata
            metadata = DocumentMetadata(
                source=url,
                content_type="github/pull_request",
                title=f"PR #{pr_data['number']}: {pr_data['title']}",
                author=pr_data["user"]["login"],
                created_at=pr_data["created_at"],
                modified_at=pr_data["updated_at"],
                word_count=MCPProtocolUtils.calculate_word_count(content),
            )

            return ProcessedDocument(content=content, metadata=metadata, success=True)

        except Exception as e:
            raise MCPError(f"Pull request processing failed: {e}", error_code="PROCESSING_ERROR")

    async def _process_wiki(self, url: str, repo_info: Dict[str, str], **kwargs) -> ProcessedDocument:
        """Process a GitHub wiki page."""
        try:
            page_name = repo_info.get("page", "Home")

            # Note: GitHub wiki API is limited, this is a simplified implementation
            # In a real implementation, you might need to scrape the wiki pages

            content = f"# Wiki Page: {page_name}\n\nThis is a placeholder for wiki content. GitHub wiki API access is limited."

            # Create metadata
            metadata = DocumentMetadata(
                source=url,
                content_type="github/wiki",
                title=f"Wiki: {page_name}",
                word_count=MCPProtocolUtils.calculate_word_count(content),
            )

            return ProcessedDocument(content=content, metadata=metadata, success=True)

        except Exception as e:
            raise MCPError(f"Wiki processing failed: {e}", error_code="PROCESSING_ERROR")

    async def _format_issues(self, issues_data: List[Dict[str, Any]]) -> str:
        """Format issues data into readable text."""
        if not issues_data:
            return "No issues found."

        lines = []
        for issue in issues_data:
            lines.append(f"### #{issue['number']}: {issue['title']}")
            lines.append(f"**State:** {issue['state']}")
            lines.append(f"**Author:** {issue['user']['login']}")
            lines.append(f"**Created:** {issue['created_at']}")

            if issue.get("body"):
                # Truncate body if too long
                body = issue["body"][:200] + "..." if len(issue["body"]) > 200 else issue["body"]
                lines.append(f"**Description:** {body}")

            lines.append("")

        return "\n".join(lines)

    async def _format_pull_requests(self, prs_data: List[Dict[str, Any]]) -> str:
        """Format pull requests data into readable text."""
        if not prs_data:
            return "No pull requests found."

        lines = []
        for pr in prs_data:
            lines.append(f"### #{pr['number']}: {pr['title']}")
            lines.append(f"**State:** {pr['state']}")
            lines.append(f"**Author:** {pr['user']['login']}")
            lines.append(f"**Created:** {pr['created_at']}")
            lines.append(f"**Commits:** {pr['commits']}")
            lines.append(f"**Changed Files:** {pr['changed_files']}")

            if pr.get("body"):
                # Truncate body if too long
                body = pr["body"][:200] + "..." if len(pr["body"]) > 200 else pr["body"]
                lines.append(f"**Description:** {body}")

            lines.append("")

        return "\n".join(lines)

    def get_github_config(self) -> Dict[str, Any]:
        """Get GitHub server configuration."""
        return self.github_config.model_dump()

    def update_github_config(self, **kwargs) -> None:
        """Update GitHub server configuration."""
        for key, value in kwargs.items():
            if hasattr(self.github_config, key):
                setattr(self.github_config, key, value)

    async def cleanup(self) -> None:
        """Cleanup resources."""
        if self._session:
            await self._session.aclose()
            self._session = None
        super().cleanup()
