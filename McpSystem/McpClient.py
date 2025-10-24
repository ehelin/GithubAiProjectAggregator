
# McpClient.py
import asyncio
import json
import sys
import os

# ✅ Ensure project root is in sys.path (important if run from VS or terminal)
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


async def send_mcp_command(method: str, params: dict):
    """
    Sends a JSON-RPC request to the running MCP server process via stdin,
    and reads back the response from stdout.
    """
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }

    # Write the request to STDOUT for MCP Server to pick up
    print(json.dumps(request), flush=True)  # <-- this goes to server.stdin


async def main():
    """
    This client assumes the MCP Server is already running and
    waiting for JSON-RPC on stdin (like in McpHost debug mode).
    You will run this script separately and pipe its output to server.
    """
    print("🟢 MCP Client started.")
    print("⚠ This client expects that McpServer.py is already running and")
    print("⚠ listening for JSON-RPC input (via stdin).")

    # Example: summarize README from microsoft/vscode
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "summarize.readme",
        "params": {
            "owner": "microsoft",
            "repo": "vscode"
        }
    }

    # Send to stdout (which should be piped to server stdin)
    print("\n📤 Sending request:")
    print(json.dumps(request), flush=True)

    print("\n✅ Done. If piped to server.stdin, you should see a response appear there.")
    print("⛔ Note: This standalone client does NOT capture the server's response.")
    print("   It only prints the JSON-RPC request to stdout.")

if __name__ == "__main__":
    # No need for asyncio here unless you expand to full pipe-mode
    asyncio.run(main())
