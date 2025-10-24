
# McpHost.py

import asyncio
import json
import subprocess
import sys
import os, importlib.util

server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "McpServer", "Server.py"))
spec = importlib.util.spec_from_file_location("server_module", server_path)
server_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server_module)

server_main = server_module.main

async def run_mcp_command(method: str, params: dict):
    """
    Send a JSON-RPC command to the MCP server process and return the result.
    """
    
    await server_main()  # Runs server in same process

    SERVER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "McpServer", "Server.py"))
    
    # Launch server process if not already running
    process = await asyncio.create_subprocess_exec(
        sys.executable, SERVER_PATH,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    # Build JSON-RPC message
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }

    # Send it
    process.stdin.write((json.dumps(request) + "\n").encode())
    await process.stdin.drain()

    # Read one response line
    # response_line = await process.stdout.readline()
    while True:
        response_line = await process.stdout.readline()
        if not response_line:
            raise Exception("Server did not return any data (possible crash).")
        if response_line.strip():  # Only break if not empty (not just \r\n)
            break

    response = json.loads(response_line.decode())

    return response.get("result", response.get("error", "No result"))

async def main():
    print("🚀 MCP Host started")
    
    # Example call: summarize README from microsoft/vscode
    result = await run_mcp_command(
        "summarize.readme",
        {"owner": "microsoft", "repo": "vscode"}
    )

    print("✅ Result from MCP Server:\n")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
