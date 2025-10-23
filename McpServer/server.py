# McpServer/Server.py

import json, sys, asyncio
import asyncio
from mcp.server import Server  # Provided by the MCP framework
from Summarizer import Summarizer
from Tools import tool, TOOLS  
import sys

# Create a single Summarizer instance (reuse for all requests)
summarizer = Summarizer()

# ✅ Build a minimal subclass of Server and override request handling
class GitHubSummarizerServer(Server):
    async def handle_request(self, method: str, params: dict):
        """
        Called when an MCP client sends a request.
        We route tool calls manually using our TOOLS dictionary.
        """
        print(f"📩 Incoming request: method={method}, params={params}")

        if method in TOOLS:
            func = TOOLS[method]
            try:
                result = await func(**params)  # call the async tool function
                return {"result": result}
            except Exception as e:
                print(f"❌ Error while executing tool {method}: {e}")
                return {"error": str(e)}
        else:
            print(f"⚠️ Unknown tool requested: {method}")
            return {"error": f"Unknown tool '{method}'"}

# ✅ Create the server instance
server = GitHubSummarizerServer("github-ai-summarizer")

# -------- MCP Tool Definitions -------- #
@tool("summarize.readme")
async def summarize_readme(owner: str, repo: str) -> str:
    """
    Summarize the README of a GitHub repository.
    """
    return summarizer.summarize_repo_readme(owner, repo)

@tool("summarize.commits")
async def summarize_commits(owner: str, repo: str) -> str:
    """
    Summarize recent commits of the specified GitHub repository.
    """
    return summarizer.summarize_commits(owner, repo)

@tool("summarize.issues")
async def summarize_issues(owner: str, repo: str) -> str:
    """
    Summarize open issues in the GitHub repository.
    """
    return summarizer.summarize_issues(owner, repo)


@tool("summarize.pull_requests")
async def summarize_pull_requests(owner: str, repo: str) -> str:
    """
    Summarize pull requests in the GitHub repository.
    """
    return summarizer.summarize_pull_requests(owner, repo)

# -------- Entry Point to Run the Server -------- #
async def main():
    print("✅ MCP Server running (awaiting JSON-RPC from stdin)...", flush=True)

    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            if method in TOOLS:
                result = await TOOLS[method](**params)  # Run summarizer
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": f"Unknown method: {method}"
                }

            print(json.dumps(response), flush=True)

        except Exception as ex:
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": str(ex)
            }
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(main())