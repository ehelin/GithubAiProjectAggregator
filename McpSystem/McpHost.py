# McpHost.py (Debug Mode - In-Process MCP Server with Breakpoint Support)

import asyncio
import json
import sys
import os

# ✅ Ensure project directory is importable
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ✅ Import server logic to run in-process (instead of subprocess)
from McpServer import main as server_main


# Shared async queue to mock JSON-RPC stdin
message_queue = asyncio.Queue()


async def send_rpc(method: str, params: dict, request_id: int = 1):
    """
    Instead of writing to a subprocess stdin, we push JSON-RPC requests
    into an asyncio queue that the in-process server will read.
    """
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params
    }
    print(f"\n[MCP HOST] 📤 Sending JSON-RPC → {request}")
    await message_queue.put(json.dumps(request))


async def run_server_in_process():
    """
    Run the MCP server (McpServer.py) in the same process,
    but feed it messages from message_queue instead of sys.stdin.
    This lets breakpoints in McpServer.py and Summarizer.py still trigger.
    """
    print("[MCP HOST] 🟢 Starting MCP Server in debug mode (same process, no subprocess).")
    await server_main(input_stream=message_queue)  # <-- YOU MUST update McpServer.main to accept input_stream


async def main():
    print("[MCP HOST] ✅ Debug mode started — server + client in one process")
    
    # 1. Start the server loop in the background (non-blocking)
    asyncio.create_task(run_server_in_process())

    # 2. Give server time to initialize
    await asyncio.sleep(1)

    # 3. Send a test MCP command
    await send_rpc(
        method="summarize.readme",
        params={"owner": "microsoft", "repo": "vscode"},
        request_id=1
    )

    print("\n[MCP HOST] ✅ Request sent. If server is working, it should log activity or return a response.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[MCP HOST] 🛑 Stopped by user")
