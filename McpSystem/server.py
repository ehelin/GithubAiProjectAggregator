# McpServer/Server.py

import json
import sys
import asyncio
from Summarizer import Summarizer
from Tools import tool, TOOLS

# Reuse Summarizer instance across requests
summarizer = None

def get_summarizer():
    """
    Lazy-load the Summarizer (loads AI model on first request).
    """
    global summarizer
    if summarizer is None:
        print("⚙️ Loading AI model on first request...", file=sys.stderr, flush=True)
        summarizer = Summarizer()
    return summarizer

# ---------------- MCP TOOL DEFINITIONS ---------------- #

@tool("summarize.readme")
async def summarize_readme(owner: str, repo: str) -> str:
    return get_summarizer().summarize_repo_readme(owner, repo)

@tool("summarize.commits")
async def summarize_commits(owner: str, repo: str) -> str:
    return get_summarizer().summarize_commits(owner, repo)

@tool("summarize.issues")
async def summarize_issues(owner: str, repo: str) -> str:
    return get_summarizer().summarize_issues(owner, repo)

@tool("summarize.pull_requests")
async def summarize_pull_requests(owner: str, repo: str) -> str:
    return get_summarizer().summarize_pull_requests(owner, repo)

# ---------------- JSON-RPC SERVER LOOP ---------------- #

async def main():
    print("✅ MCP Server running (awaiting JSON-RPC on stdin)...", file=sys.stderr, flush=True)

    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            print(f"📩 Incoming request: {method} with {params}", file=sys.stderr, flush=True)

            if method in TOOLS:
                result = await TOOLS[method](**params)
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": f"Unknown method '{method}'"
                }

            # ✅ Send valid JSON-RPC response to STDOUT
            print(json.dumps(response), flush=True)

        except Exception as ex:
            error_response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": str(ex)
            }
            # ✅ Errors must still go to STDOUT (JSON-RPC spec)
            print(json.dumps(error_response), flush=True)
            print(f"❌ Exception: {ex}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    asyncio.run(main())
