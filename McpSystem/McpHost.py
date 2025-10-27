# McpHost.py
# ===========================================================
# Dual-mode MCP Host:
# - DEBUG mode: runs everything in one process (for breakpoints)
# - REALISTIC mode: runs server and client as subprocesses
# ===========================================================

import asyncio
import json
import os
import sys
from typing import Optional

# ✅ Import server logic for debug mode (in-process)
from McpServer import main as server_main


# ===========================================================
# 🧩 CONFIGURATION
# ===========================================================
DEBUG_MODE = True  # True = single-process debug, False = multi-process


# ===========================================================
# 🧠 Debug Mode (single process)
# ===========================================================

message_queue = asyncio.Queue()


async def send_rpc(method: str, params: dict, request_id: int = 1):
    """Push JSON-RPC requests into an async queue for the in-process server."""
    request = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": method,
        "params": params
    }
    print(f"\n[MCP HOST] 📤 Sending JSON-RPC → {request}")
    await message_queue.put(json.dumps(request))


async def run_server_in_process():
    """Run the MCP server (McpServer.py) in the same process for debugging."""
    print("[MCP HOST] 🟢 Starting MCP Server in debug mode (same process, no subprocess).")
    await server_main(input_stream=message_queue)  # McpServer.main must accept input_stream


async def run_debug_mode():
    """Run the debug mode — single process, interactive."""
    print("[MCP HOST] ✅ Debug mode started — server + client in one process")

    # 1. Start the in-process server
    asyncio.create_task(run_server_in_process())

    # 2. Give server a moment to initialize
    await asyncio.sleep(1)

    # 3. Send a test request
    await send_rpc(
        method="summarize.readme",
        params={"owner": "microsoft", "repo": "vscode"},
        request_id=1
    )

    print("\n[MCP HOST] ✅ Request sent. Server logs should reflect handling activity.")


# ===========================================================
# 🧠 Realistic Mode (multi-process)
# ===========================================================

class McpHostController:
    """
    Real MCP Host class used in production or via McpSystemApi.
    Manages server + client subprocesses and provides async send/receive methods.
    """

    def __init__(self):
        self.server_proc: Optional[asyncio.subprocess.Process] = None
        self.client_proc: Optional[asyncio.subprocess.Process] = None
        self._running = False

    # -------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------
    async def start(self):
        """Start the MCP server and client subprocesses."""
        if self._running:
            print("[MCP HOST] 🔁 Already running.")
            return

        print("[MCP HOST] 🚀 Starting MCP system (multi-process)...")

        os.makedirs("logs", exist_ok=True)

        # Start server
        self.server_proc = await asyncio.create_subprocess_exec(
            sys.executable, "McpServer.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        await asyncio.sleep(1.5)

        # Start client
        self.client_proc = await asyncio.create_subprocess_exec(
            sys.executable, "McpClient.py",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        self._running = True
        print("[MCP HOST] ✅ MCP Server and Client started.")

        # Stream logs in the background
        asyncio.create_task(self._stream_output(self.server_proc, "SERVER"))
        asyncio.create_task(self._stream_output(self.client_proc, "CLIENT"))

    async def stop(self):
        """Stop both MCP processes."""
        if not self._running:
            print("[MCP HOST] 💤 Nothing to stop.")
            return

        print("[MCP HOST] 🛑 Stopping MCP system...")
        for proc, name in [(self.client_proc, "CLIENT"), (self.server_proc, "SERVER")]:
            if proc and proc.returncode is None:
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), timeout=3)
                except asyncio.TimeoutError:
                    print(f"[MCP HOST] ⚠️ {name} not responding, forcing kill.")
                    proc.kill()

        self.server_proc = None
        self.client_proc = None
        self._running = False
        print("[MCP HOST] ✅ MCP system stopped.")

    async def restart(self):
        """Restart both processes."""
        await self.stop()
        await self.start()

    # -------------------------------------------------------
    # Request/Response
    # -------------------------------------------------------
    async def send_request(self, request: dict) -> dict:
        """Send a JSON-RPC request through the MCP client subprocess."""
        if not self.client_proc:
            raise RuntimeError("MCP Client not running — call start() first.")

        json_str = json.dumps(request) + "\n"
        print(f"[MCP HOST] 📤 Forwarding request → {json_str.strip()}")

        self.client_proc.stdin.write(json_str.encode())
        await self.client_proc.stdin.drain()

        line = await self.client_proc.stdout.readline()
        if not line:
            raise RuntimeError("No response from client.")

        print(f"[MCP HOST] 📥 Received: {line.decode().strip()}")
        try:
            return json.loads(line.decode())
        except json.JSONDecodeError:
            return {"error": "Invalid JSON", "raw": line.decode()}

    # -------------------------------------------------------
    # Helpers
    # -------------------------------------------------------
    async def _stream_output(self, proc, name):
        """Stream process output to console and file."""
        log_path = f"logs/{name.lower()}.log"
        with open(log_path, "a", encoding="utf-8") as log:
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                text = line.decode().rstrip()
                print(f"[{name}] {text}")
                log.write(text + "\n")
                log.flush()

    def is_running(self) -> bool:
        return self._running and self.client_proc and self.server_proc

# ===========================================================
# 🏁 Entry Point
# ===========================================================
async def main():
    if DEBUG_MODE:
        await run_debug_mode()
        return

    host = McpHostController()
    await host.start()

    print("\n[MCP HOST] 🟢 Host is now running. Press Ctrl+C to stop.")
    try:
        # Run indefinitely until manually stopped
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n[MCP HOST] 🛑 Stop signal received. Shutting down...")
        await host.stop()

# ------------------------------------------------
# Testing only code start
if __name__ == "__main__":
    asyncio.run(main())     
# ------------------------------------------------

