"""
Unit tests for GitHub MCP Server.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.utils.mcp_integration.base_server import MCPConfig, MCPError
from src.utils.mcp_integration.github_server import (
    GitHubIssue,
    GitHubMCPServer,
    GitHubPullRequest,
    GitHubRepository,
    GitHubServerConfig,
)


class TestGitHubServerConfig:
    """Test GitHub Server Configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = GitHubServerConfig()
        assert config.api_token is None
        assert config.rate_limit_delay == 1.0
        assert config.max_file_size == 1024 * 1024
        assert config.include_issues is True
        assert config.include_pull_requests is True
        assert config.include_wiki is False
        assert config.max_items_per_type == 50

    def test_custom_config(self):
        """Test custom configuration values."""
        config = GitHubServerConfig(
            api_token="test_token",
            rate_limit_delay=2.0,
            max_file_size=2 * 1024 * 1024,
            include_issues=False,
            include_pull_requests=False,
            include_wiki=True,
            max_items_per_type=100,
        )
        assert config.api_token == "test_token"
        assert config.rate_limit_delay == 2.0
        assert config.max_file_size == 2 * 1024 * 1024
        assert config.include_issues is False
        assert config.include_pull_requests is False
        assert config.include_wiki is True
        assert config.max_items_per_type == 100


class TestGitHubRepository:
    """Test GitHub Repository model."""

    def test_github_repository(self):
        """Test GitHub repository creation."""
        repo = GitHubRepository(
            name="test-repo",
            full_name="owner/test-repo",
            description="Test repository",
            language="Python",
            stars=100,
            forks=50,
            issues_count=25,
            pull_requests_count=10,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z",
            default_branch="main",
        )
        assert repo.name == "test-repo"
        assert repo.full_name == "owner/test-repo"
        assert repo.description == "Test repository"
        assert repo.language == "Python"
        assert repo.stars == 100
        assert repo.forks == 50
        assert repo.issues_count == 25
        assert repo.pull_requests_count == 10


class TestGitHubIssue:
    """Test GitHub Issue model."""

    def test_github_issue(self):
        """Test GitHub issue creation."""
        issue = GitHubIssue(
            number=1,
            title="Test Issue",
            body="This is a test issue",
            state="open",
            author="testuser",
            assignees=["user1", "user2"],
            labels=["bug", "enhancement"],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z",
            comments_count=5,
        )
        assert issue.number == 1
        assert issue.title == "Test Issue"
        assert issue.body == "This is a test issue"
        assert issue.state == "open"
        assert issue.author == "testuser"
        assert issue.assignees == ["user1", "user2"]
        assert issue.labels == ["bug", "enhancement"]
        assert issue.comments_count == 5


class TestGitHubPullRequest:
    """Test GitHub Pull Request model."""

    def test_github_pull_request(self):
        """Test GitHub pull request creation."""
        pr = GitHubPullRequest(
            number=1,
            title="Test PR",
            body="This is a test pull request",
            state="open",
            author="testuser",
            assignees=["user1"],
            labels=["feature"],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-02T00:00:00Z",
            comments_count=3,
            review_comments_count=2,
            commits_count=5,
            changed_files=10,
        )
        assert pr.number == 1
        assert pr.title == "Test PR"
        assert pr.body == "This is a test pull request"
        assert pr.state == "open"
        assert pr.author == "testuser"
        assert pr.comments_count == 3
        assert pr.review_comments_count == 2
        assert pr.commits_count == 5
        assert pr.changed_files == 10


class TestGitHubMCPServer:
    """Test GitHub MCP Server."""

    @pytest.fixture
    def config(self):
        """Create test configuration."""
        return MCPConfig(server_name="test_github_server")

    @pytest.fixture
    def server(self, config):
        """Create test server."""
        return GitHubMCPServer(config)

    def test_server_initialization(self, config):
        """Test server initialization."""
        server = GitHubMCPServer(config)
        assert server.config == config
        assert server.config.server_name == "test_github_server"
        assert len(server.supported_types) > 0
        assert isinstance(server.github_config, GitHubServerConfig)

    def test_supported_content_types(self, server):
        """Test supported content types."""
        types = server.get_supported_types()
        assert "github/repository" in types
        assert "github/file" in types
        assert "github/issue" in types
        assert "github/pull_request" in types
        assert "github/wiki" in types
        assert len(types) == 5

    def test_supports_content_type(self, server):
        """Test content type support checking."""
        assert server.supports_content_type("github/repository") is True
        assert server.supports_content_type("github/file") is True
        assert server.supports_content_type("github/issue") is True
        assert server.supports_content_type("unsupported/type") is False

    def test_validate_source(self, server):
        """Test source validation."""
        # Valid GitHub URLs
        assert server.validate_source("https://github.com/owner/repo") is True
        assert server.validate_source("https://github.com/owner/repo/blob/main/file.txt") is True
        assert server.validate_source("https://github.com/owner/repo/issues/1") is True
        assert server.validate_source("https://github.com/owner/repo/pull/1") is True
        assert server.validate_source("https://github.com/owner/repo/wiki/Home") is True

        # Invalid URLs
        assert server.validate_source("") is False
        assert server.validate_source("   ") is False
        assert server.validate_source("https://gitlab.com/owner/repo") is False
        assert server.validate_source("https://example.com") is False

    def test_parse_github_url_repository(self, server):
        """Test parsing repository URL."""
        url = "https://github.com/owner/repo"
        repo_info = server._parse_github_url(url)

        assert repo_info["owner"] == "owner"
        assert repo_info["repo"] == "repo"
        assert repo_info["type"] == "repository"
        assert repo_info["branch"] == "main"
        assert repo_info["path"] == ""

    def test_parse_github_url_file(self, server):
        """Test parsing file URL."""
        url = "https://github.com/owner/repo/blob/main/src/file.py"
        repo_info = server._parse_github_url(url)

        assert repo_info["owner"] == "owner"
        assert repo_info["repo"] == "repo"
        assert repo_info["type"] == "file"
        assert repo_info["branch"] == "main"
        assert repo_info["path"] == "src/file.py"

    def test_parse_github_url_issue(self, server):
        """Test parsing issue URL."""
        url = "https://github.com/owner/repo/issues/123"
        repo_info = server._parse_github_url(url)

        assert repo_info["owner"] == "owner"
        assert repo_info["repo"] == "repo"
        assert repo_info["type"] == "issue"
        assert repo_info["issue_number"] == "123"

    def test_parse_github_url_pull_request(self, server):
        """Test parsing pull request URL."""
        url = "https://github.com/owner/repo/pull/456"
        repo_info = server._parse_github_url(url)

        assert repo_info["owner"] == "owner"
        assert repo_info["repo"] == "repo"
        assert repo_info["type"] == "pull_request"
        assert repo_info["pr_number"] == "456"

    def test_parse_github_url_wiki(self, server):
        """Test parsing wiki URL."""
        url = "https://github.com/owner/repo/wiki/Getting-Started"
        repo_info = server._parse_github_url(url)

        assert repo_info["owner"] == "owner"
        assert repo_info["repo"] == "repo"
        assert repo_info["type"] == "wiki"
        assert repo_info["page"] == "Getting-Started"

    def test_parse_github_url_invalid(self, server):
        """Test parsing invalid GitHub URL."""
        with pytest.raises(MCPError) as exc_info:
            server._parse_github_url("https://github.com/owner")

        assert exc_info.value.error_code == "URL_PARSING_ERROR"

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
    async def test_make_api_request_success(self, server):
        """Test successful API request."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"name": "test-repo"}
        mock_response.raise_for_status.return_value = None

        with patch.object(server, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.get.return_value = mock_response
            mock_get_session.return_value = mock_session

            result = await server._make_api_request("/repos/owner/repo")

            assert result == {"name": "test-repo"}

    @pytest.mark.asyncio
    async def test_make_api_request_404(self, server):
        """Test API request with 404 error."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=MagicMock(), response=mock_response
        )

        with patch.object(server, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.get.return_value = mock_response
            mock_get_session.return_value = mock_session

            with pytest.raises(MCPError) as exc_info:
                await server._make_api_request("/repos/owner/repo")

            assert exc_info.value.error_code == "RESOURCE_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_make_api_request_rate_limit(self, server):
        """Test API request with rate limit error."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "403 Forbidden", request=MagicMock(), response=mock_response
        )

        with patch.object(server, "_get_session") as mock_get_session:
            mock_session = AsyncMock()
            mock_session.get.return_value = mock_response
            mock_get_session.return_value = mock_session

            with pytest.raises(MCPError) as exc_info:
                await server._make_api_request("/repos/owner/repo")

            assert exc_info.value.error_code == "RATE_LIMIT_EXCEEDED"

    @pytest.mark.asyncio
    async def test_process_repository(self, server):
        """Test repository processing."""
        repo_data = {
            "full_name": "owner/test-repo",
            "description": "Test repository",
            "language": "Python",
            "stargazers_count": 100,
            "forks_count": 50,
            "open_issues_count": 25,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
            "owner": {"login": "owner"},
        }

        with patch.object(server, "_make_api_request") as mock_api:
            # Mock different API calls to return appropriate data
            mock_api.side_effect = [
                repo_data,  # Repository data
                {"content": ""},  # README (empty)
                [],  # Issues (empty list)
                [],  # Pull requests (empty list)
            ]

            repo_info = {"owner": "owner", "repo": "test-repo"}
            result = await server._process_repository("https://github.com/owner/repo", repo_info)

            assert result.success is True
            assert result.metadata.content_type == "github/repository"
            assert result.metadata.title == "owner/test-repo"
            assert result.metadata.author == "owner"
            assert "Test repository" in result.content
            assert "Python" in result.content
            assert "100" in result.content  # Stars

    @pytest.mark.asyncio
    async def test_process_file(self, server):
        """Test file processing."""
        file_data = {
            "type": "file",
            "name": "test.py",
            "content": "ZGVmIGhlbGxvKCk6CiAgICBwcmludCgiSGVsbG8sIHdvcmxkISIpCg==",  # base64 encoded
            "size": 50,
            "owner": {"login": "owner"},
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
        }

        with patch.object(server, "_make_api_request") as mock_api:
            mock_api.return_value = file_data

            repo_info = {"owner": "owner", "repo": "test-repo", "path": "test.py", "branch": "main"}
            result = await server._process_file("https://github.com/owner/repo/blob/main/test.py", repo_info)

            assert result.success is True
            assert result.metadata.content_type == "github/file"
            assert result.metadata.title == "test.py"
            assert result.metadata.author == "owner"
            assert "def hello():" in result.content

    @pytest.mark.asyncio
    async def test_process_file_too_large(self, server):
        """Test file processing with file too large."""
        file_data = {
            "type": "file",
            "name": "large.py",
            "content": "test",
            "size": 2 * 1024 * 1024,  # 2MB
        }

        with patch.object(server, "_make_api_request") as mock_api:
            mock_api.return_value = file_data

            repo_info = {"owner": "owner", "repo": "test-repo", "path": "large.py", "branch": "main"}

            with pytest.raises(MCPError) as exc_info:
                await server._process_file("https://github.com/owner/repo/blob/main/large.py", repo_info)

            assert exc_info.value.error_code == "PROCESSING_ERROR"

    @pytest.mark.asyncio
    async def test_process_file_not_a_file(self, server):
        """Test file processing with non-file content."""
        file_data = {
            "type": "dir",
            "name": "directory",
        }

        with patch.object(server, "_make_api_request") as mock_api:
            mock_api.return_value = file_data

            repo_info = {"owner": "owner", "repo": "test-repo", "path": "directory", "branch": "main"}

            with pytest.raises(MCPError) as exc_info:
                await server._process_file("https://github.com/owner/repo/blob/main/directory", repo_info)

            assert exc_info.value.error_code == "PROCESSING_ERROR"

    @pytest.mark.asyncio
    async def test_process_issue(self, server):
        """Test issue processing."""
        issue_data = {
            "number": 123,
            "title": "Test Issue",
            "body": "This is a test issue description",
            "state": "open",
            "user": {"login": "testuser"},
            "assignees": [{"login": "user1"}, {"login": "user2"}],
            "labels": [{"name": "bug"}, {"name": "enhancement"}],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
        }

        with patch.object(server, "_make_api_request") as mock_api:
            mock_api.return_value = issue_data

            repo_info = {"owner": "owner", "repo": "test-repo", "issue_number": "123"}
            result = await server._process_issue("https://github.com/owner/repo/issues/123", repo_info)

            assert result.success is True
            assert result.metadata.content_type == "github/issue"
            assert result.metadata.title == "Issue #123: Test Issue"
            assert result.metadata.author == "testuser"
            assert "Test Issue" in result.content
            assert "This is a test issue description" in result.content
            assert "user1, user2" in result.content  # Assignees
            assert "bug, enhancement" in result.content  # Labels

    @pytest.mark.asyncio
    async def test_process_issue_missing_number(self, server):
        """Test issue processing with missing issue number."""
        repo_info = {"owner": "owner", "repo": "test-repo"}

        with pytest.raises(MCPError) as exc_info:
            await server._process_issue("https://github.com/owner/repo/issues", repo_info)

        assert exc_info.value.error_code == "PROCESSING_ERROR"

    @pytest.mark.asyncio
    async def test_process_pull_request(self, server):
        """Test pull request processing."""
        pr_data = {
            "number": 456,
            "title": "Test PR",
            "body": "This is a test pull request description",
            "state": "open",
            "user": {"login": "testuser"},
            "assignees": [{"login": "user1"}],
            "labels": [{"name": "feature"}],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
            "commits": 5,
            "changed_files": 10,
            "comments": 3,
            "review_comments": 2,
        }

        with patch.object(server, "_make_api_request") as mock_api:
            mock_api.return_value = pr_data

            repo_info = {"owner": "owner", "repo": "test-repo", "pr_number": "456"}
            result = await server._process_pull_request("https://github.com/owner/repo/pull/456", repo_info)

            assert result.success is True
            assert result.metadata.content_type == "github/pull_request"
            assert result.metadata.title == "PR #456: Test PR"
            assert result.metadata.author == "testuser"
            assert "Test PR" in result.content
            assert "This is a test pull request description" in result.content
            assert "5" in result.content  # Commits
            assert "10" in result.content  # Changed files

    @pytest.mark.asyncio
    async def test_process_wiki(self, server):
        """Test wiki processing."""
        repo_info = {"owner": "owner", "repo": "test-repo", "page": "Getting-Started"}
        result = await server._process_wiki("https://github.com/owner/repo/wiki/Getting-Started", repo_info)

        assert result.success is True
        assert result.metadata.content_type == "github/wiki"
        assert result.metadata.title == "Wiki: Getting-Started"
        assert "Getting-Started" in result.content

    @pytest.mark.asyncio
    async def test_format_issues(self, server):
        """Test issues formatting."""
        issues_data = [
            {
                "number": 1,
                "title": "Bug fix",
                "body": "This is a bug fix",
                "state": "open",
                "user": {"login": "user1"},
                "created_at": "2024-01-01T00:00:00Z",
            },
            {
                "number": 2,
                "title": "Feature request",
                "body": "This is a feature request",
                "state": "closed",
                "user": {"login": "user2"},
                "created_at": "2024-01-02T00:00:00Z",
            },
        ]

        formatted = await server._format_issues(issues_data)

        assert "### #1: Bug fix" in formatted
        assert "### #2: Feature request" in formatted
        assert "user1" in formatted
        assert "user2" in formatted
        assert "This is a bug fix" in formatted
        assert "This is a feature request" in formatted

    @pytest.mark.asyncio
    async def test_format_issues_empty(self, server):
        """Test formatting empty issues list."""
        formatted = await server._format_issues([])
        assert formatted == "No issues found."

    @pytest.mark.asyncio
    async def test_format_pull_requests(self, server):
        """Test pull requests formatting."""
        prs_data = [
            {
                "number": 1,
                "title": "Add feature",
                "body": "This adds a new feature",
                "state": "open",
                "user": {"login": "user1"},
                "created_at": "2024-01-01T00:00:00Z",
                "commits": 3,
                "changed_files": 5,
            },
        ]

        formatted = await server._format_pull_requests(prs_data)

        assert "### #1: Add feature" in formatted
        assert "user1" in formatted
        assert "This adds a new feature" in formatted
        assert "3" in formatted  # Commits
        assert "5" in formatted  # Changed files

    @pytest.mark.asyncio
    async def test_format_pull_requests_empty(self, server):
        """Test formatting empty pull requests list."""
        formatted = await server._format_pull_requests([])
        assert formatted == "No pull requests found."

    @pytest.mark.asyncio
    async def test_process_document_repository(self, server):
        """Test processing repository document."""
        with patch.object(server, "_process_repository") as mock_process:
            mock_process.return_value = MagicMock(success=True)

            result = await server.process_document("https://github.com/owner/repo")

            assert result.success is True
            mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_document_file(self, server):
        """Test processing file document."""
        with patch.object(server, "_process_file") as mock_process:
            mock_process.return_value = MagicMock(success=True)

            result = await server.process_document("https://github.com/owner/repo/blob/main/file.txt")

            assert result.success is True
            mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_document_issue(self, server):
        """Test processing issue document."""
        with patch.object(server, "_process_issue") as mock_process:
            mock_process.return_value = MagicMock(success=True)

            result = await server.process_document("https://github.com/owner/repo/issues/123")

            assert result.success is True
            mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_document_invalid_source(self, server):
        """Test processing document with invalid source."""
        with pytest.raises(MCPError) as exc_info:
            await server.process_document("not-a-github-url")

        assert exc_info.value.error_code == "INVALID_SOURCE"

    def test_get_github_config(self, server):
        """Test getting GitHub configuration."""
        config = server.get_github_config()

        assert "api_token" in config
        assert "rate_limit_delay" in config
        assert "max_file_size" in config
        assert "include_issues" in config
        assert "include_pull_requests" in config
        assert "include_wiki" in config
        assert "max_items_per_type" in config

    def test_update_github_config(self, server):
        """Test updating GitHub configuration."""
        original_delay = server.github_config.rate_limit_delay

        server.update_github_config(rate_limit_delay=2.0)

        assert server.github_config.rate_limit_delay == 2.0
        assert server.github_config.rate_limit_delay != original_delay

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

    @pytest.mark.asyncio
    async def test_server_info(self, server):
        """Test server information."""
        info = server.get_server_info()

        assert info["name"] == "test_github_server"
        assert info["version"] == "1.0.0"
        assert "github/repository" in info["supported_types"]
        assert info["cache_size"] == 0
