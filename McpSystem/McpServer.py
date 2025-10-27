# McpServer.py

import json
import sys
import asyncio
from Summarizer import Summarizer
from Tools import tool, TOOLS

summarizer = None

def get_summarizer():
    global summarizer
    if summarizer is None:
        print("🧠 Loading AI Summarizer model...", file=sys.stderr, flush=True)
        summarizer = Summarizer()
    return summarizer

@tool("summarize.readme")
async def summarize_readme(owner: str, repo: str):
    return get_summarizer().summarize_repo_readme(owner, repo)

@tool("summarize.commits")
async def summarize_commits(owner: str, repo: str):
    return get_summarizer().summarize_commits(owner, repo)

@tool("summarize.issues")
async def summarize_issues(owner: str, repo: str):
    return get_summarizer().summarize_issues(owner, repo)

@tool("summarize.pull_requests")
async def summarize_pull_requests(owner: str, repo: str):
    return get_summarizer().summarize_pull_requests(owner, repo)


# ✅ Updated to prevent VS debugger from stopping on 'await' TypeError
async def main(input_stream=None):
    """
    If input_stream is None → read from sys.stdin (normal MCP mode, subprocess)
    If input_stream is an asyncio.Queue → read via queue (debug/in-process mode)
    """
    print("⚙ MCP Server running (awaiting JSON-RPC)...", file=sys.stderr, flush=True)

    while True:
        try:
            # ✅ Read next JSON-RPC message safely
            if input_stream is None:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            else:
                # No exception — check if .get() is async first
                get_method = input_stream.get
                if asyncio.iscoroutinefunction(get_method):
                    line = await get_method()
                else:
                    line = get_method()

            if not line:
                await asyncio.sleep(0.1)
                continue

            line = line.strip()
            if not line:
                continue

            request = json.loads(line)
            method = request.get("method")
            params = request.get("params", {})
            request_id = request.get("id")

            print(f"📩 Incoming request: {method} {params}", file=sys.stderr, flush=True)

            if method in TOOLS:
                result = await TOOLS[method](**params)
                response = {"jsonrpc": "2.0", "id": request_id, "result": result}
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown method: {method}"}
                }

        except Exception as ex:
            response = {
                "jsonrpc": "2.0",
                "id": request_id if 'request_id' in locals() else None,
                "error": {"code": -32000, "message": str(ex)}
            }

        print(json.dumps(response), flush=True)
