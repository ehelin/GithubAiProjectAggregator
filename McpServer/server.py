# McpServer/Server.py

import asyncio
from mcp.server import Server  # Provided by the MCP framework
from Summarizer import Summarizer

# Create the MCP server instance (name is arbitrary but should be unique)
server = Server("github-ai-summarizer")

# Create a single Summarizer instance (reuse for all requests)
summarizer = Summarizer()

# -------- MCP Tool Definitions -------- #
@server.tool("summarize.readme")
async def summarize_readme(owner: str, repo: str) -> str:
    """
    Summarize the README of a GitHub repository.
    """
    return summarizer.summarize_repo_readme(owner, repo)

@server.tool("summarize.commits")
async def summarize_commits(owner: str, repo: str) -> str:
    """
    Summarize recent commits of the specified GitHub repository.
    """
    return summarizer.summarize_commits(owner, repo)

@server.tool("summarize.issues")
async def summarize_issues(owner: str, repo: str) -> str:
    """
    Summarize open issues in the GitHub repository.
    """
    return summarizer.summarize_issues(owner, repo)


@server.tool("summarize.pull_requests")
async def summarize_pull_requests(owner: str, repo: str) -> str:
    """
    Summarize pull requests in the GitHub repository.
    """
    return summarizer.summarize_pull_requests(owner, repo)

# -------- Entry Point to Run the Server -------- #
if __name__ == "__main__":
    # This keeps the server running and ready for MCP client requests
    asyncio.run(server.run())