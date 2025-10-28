# ===========================================================
# McpClient.py — Final bridge version for Host ↔ Client ↔ Server
# -----------------------------------------------------------
# This version no longer spawns its own server.
# It listens for requests from McpHost via stdin,
# forwards them to the already running McpServer (via pipes),
# and prints responses back to stdout.
# ===========================================================

import asyncio
import json
import sys
import os


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ===========================================================
# 🔁 Bridge logic
# ===========================================================
async def handle_requests_to_existing_server(reader, writer):
    """
    Continuously read JSON-RPC requests from McpHost (stdin),
    forward them to the running McpServer via pipes,
    and send back the responses.
    """
    while True:
        try:
            # 🔹 Read next JSON-RPC request from McpHost (stdin)
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                await asyncio.sleep(0.05)
                continue

            line = line.strip()
            if not line:
                continue

            # Validate JSON input
            try:
                request = json.loads(line)
            except json.JSONDecodeError as e:
                print(json.dumps({"error": f"Invalid JSON from host: {e}"}), flush=True)
                continue

            # 🔹 Forward request to server stdin
            writer.write((json.dumps(request) + "\n").encode())
            await writer.drain()

            # 🔹 Read one full JSON response line from server stdout
            response_line = await reader.readline()
            if not response_line:
                print(json.dumps({"error": "No response from server"}), flush=True)
                continue

            # ✅ Forward response to host
            response_text = response_line.decode().strip()
            print(response_text, flush=True)

        except Exception as e:
            print(json.dumps({"error": f"Bridge failure: {str(e)}"}), flush=True)
            await asyncio.sleep(0.2)


# ===========================================================
# 🚀 Entry point
# ===========================================================
async def main():
    print("🟢 MCP Client bridge starting...", file=sys.stderr, flush=True)

    try:
        # Get a fresh event loop to avoid debugger conflicts
        loop = asyncio.get_running_loop()

        # Attach to the running McpServer process via stdio pipes
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        writer_transport, writer_protocol = await loop.connect_write_pipe(
            asyncio.streams.FlowControlMixin, sys.stdout
        )
        writer = asyncio.StreamWriter(writer_transport, writer_protocol, reader, loop)

        # Start main loop
        await handle_requests_to_existing_server(reader, writer)
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            print(f"🟢 MCP Client: Debugger event loop issue detected, using fallback mode...", file=sys.stderr, flush=True)
            # Fallback: direct stdin/stdout without pipes
            await main_fallback()
        else:
            raise


async def main_fallback():
    """Fallback mode for debugger compatibility - simpler I/O without pipes."""
    print("🟢 MCP Client fallback mode active...", file=sys.stderr, flush=True)

    while True:
        try:
            # Simple blocking read from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                await asyncio.sleep(0.05)
                continue

            line = line.strip()
            if not line:
                continue

            # Just echo back for now - this mode bypasses server
            print(json.dumps({"error": "Client running in fallback mode - pipe connections failed"}), flush=True)

        except Exception as e:
            print(json.dumps({"error": f"Fallback mode error: {str(e)}"}), flush=True)
            await asyncio.sleep(0.2)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 MCP Client shutting down.", file=sys.stderr, flush=True)
