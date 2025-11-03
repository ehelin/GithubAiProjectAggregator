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
DEBUG_MODE = False  # True = single-process debug, False = multi-process


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
    print("[MCP HOST] 🟢 Starting MCP Server in debug mode (same process, no subprocess).", flush=True)
    await server_main(input_stream=message_queue)  # McpServer.main must accept input_stream


async def run_debug_mode():
    """Run the debug mode — single process, interactive."""
    print("[MCP HOST] ✅ Debug mode started — server + client in one process", flush=True)

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

    print("\n[MCP HOST] ✅ Request sent. Server logs should reflect handling activity.", flush=True)


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
        self.lock = asyncio.Lock()
        self.last_output: Optional[str] = None  # ⬅️ added to hold latest line

    # -------------------------------------------------------
    # Lifecycle
    # -------------------------------------------------------
    async def start(self):
        """Start the MCP server and client subprocesses."""
        if self._running:
            print("[MCP HOST] 🔁 Already running.", flush=True)
            return

        print("[MCP HOST] 🚀 Starting MCP system (multi-process)...", flush=True)

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
        print("[MCP HOST] ✅ MCP Server and Client started.", flush=True)

        # ✅ Stream logs in the background (single reader per process)
        asyncio.create_task(self._stream_output(self.server_proc, "SERVER"))
        asyncio.create_task(self._stream_output(self.client_proc, "CLIENT"))

    async def stop(self):
        """Stop both MCP processes."""
        if not self._running:
            print("[MCP HOST] 💤 Nothing to stop.", flush=True)
            return

        print("[MCP HOST] 🛑 Stopping MCP system...", flush=True)
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
        print("[MCP HOST] ✅ MCP system stopped.", flush=True)

    async def restart(self):
        """Restart both processes."""
        await self.stop()
        await self.start()

    async def list_summaries(self):
        base = os.path.join(os.path.dirname(__file__), "summaries")
        result = []

        if not os.path.exists(base):
            return result

        for owner in os.listdir(base):
            owner_path = os.path.join(base, owner)
            if not os.path.isdir(owner_path):
                continue

            for repo in os.listdir(owner_path):
                repo_path = os.path.join(owner_path, repo)
                if not os.path.isdir(repo_path):
                    continue

                for filename in os.listdir(repo_path):
                    if filename.endswith(".json"):
                        mode = filename[:-5]
                        result.append({"owner": owner, "repo": repo, "mode": mode})

        return result

    async def load_summary(self, owner: str, repo: str, mode: str):
        path = os.path.join(os.path.dirname(__file__), "summaries", owner, repo, f"{mode}.json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # -------------------------------------------------------
    # Request/Response
    # -------------------------------------------------------
    async def send_request(self, request: dict) -> dict:
        async with self.lock:
            if not self.client_proc:
                raise RuntimeError("MCP Client not running — call start() first.")

            # Check if client process died
            if self.client_proc.returncode is not None:
                raise RuntimeError(f"MCP Client process died with code {self.client_proc.returncode}")

            json_str = json.dumps(request) + "\n"
            print(f"[MCP HOST] 📤 Forwarding request → {json_str.strip()}")

            try:
                self.client_proc.stdin.write(json_str.encode())
                await self.client_proc.stdin.drain()
            except RuntimeError as ex:
                if "Event loop is closed" in str(ex):
                    print("[MCP HOST] ⚠️ Debugger closed event loop; ignoring.", flush=True)
                    return {"error": "Event loop closed (debugger interference)", "hint": "Try running without debugger or use DEBUG_MODE"}
                raise
            except BrokenPipeError:
                return {"error": "Client process stdin closed", "hint": "Client may have crashed - check logs"}

            # Wait for response with timeout
            # max_wait = 5.0  # seconds
            max_wait = 300.0  # 5 minutes
            wait_interval = 0.1
            waited = 0.0
            initial_output = self.last_output

            while waited < max_wait:
                await asyncio.sleep(wait_interval)
                waited += wait_interval

                # Check if we got new output (different from before request)
                if self.last_output and self.last_output != initial_output:
                    break

            if not self.last_output or self.last_output == initial_output:
                return {"error": "Timeout waiting for response from client", "hint": "Check server/client logs"}

            print(f"[MCP HOST] 📥 Received (latest): {self.last_output}")

            # Check if output is an error message (not JSON)
            if self.last_output.startswith("RuntimeError") or self.last_output.startswith("Error"):
                return {"error": "Client error", "message": self.last_output, "hint": "Client failed to connect to server"}

            try:
                return json.loads(self.last_output)
            except json.JSONDecodeError:
                return {"error": "Invalid JSON from client", "raw": self.last_output}

    # -------------------------------------------------------
    # Helpers
    # -------------------------------------------------------
    async def _stream_output(self, proc, name):
        """Continuously read process stdout and log/store."""
        log_path = f"logs/{name.lower()}.log"
        with open(log_path, "a", encoding="utf-8") as log:
            async for line in proc.stdout:
                text = line.decode().rstrip()
                self.last_output = text  # update shared output
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

    print("\n[MCP HOST] 🟢 Host is now running. Press Ctrl+C to stop.", flush=True)
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n[MCP HOST] 🛑 Stop signal received. Shutting down...", flush=True)
        await host.stop()


# ------------------------------------------------
# Testing only code start
if __name__ == "__main__":
    asyncio.run(main())
# ------------------------------------------------
