# McpSystemApi.py
# ===========================================================
# High-level application API that communicates with the MCP
# system (Host + Client + Server).  Not part of the MCP core.
# -----------------------------------------------------------
# The C# or web layer calls this module to request summaries
# or other AI-generated information, without dealing with
# pipes, subprocesses, or JSON-RPC directly.
# ===========================================================

import asyncio
import json
from typing import Any, Dict, Optional

# Import the host controller (you’ll define this class in McpHost.py)
from McpHost import McpHostController


class McpSystemApi:
    """
    Entry point for external applications (like your .NET backend).
    Handles requests to the MCP system through the host.
    """

    def __init__(self):
        # Manages the underlying MCP system lifecycle (client/server)
        self.host = McpHostController()

    # -------------------------------------------------------
    # 🧩 System Lifecycle Management
    # -------------------------------------------------------
    async def start_system(self):
        """
        Ensure the MCP host (and its client/server) are running.
        Safe to call multiple times — will no-op if already running.
        """
        print("[SYSTEM API] 🚀 Starting MCP system (host, client, server)...")
        await self.host.start()
        print("[SYSTEM API] ✅ MCP system ready.")

    async def stop_system(self):
        """Gracefully stop the MCP system."""
        print("[SYSTEM API] 🛑 Stopping MCP system...")
        await self.host.stop()

    # -------------------------------------------------------
    # 🧠 High-Level Summarization APIs
    # -------------------------------------------------------
    async def summarize_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Generate a summary of a GitHub repository's README.
        """
        await self.start_system()

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "summarize.readme",
            "params": {"owner": owner, "repo": repo}
        }

        print(f"[SYSTEM API] 📨 Sending summarize_repo for {owner}/{repo}")
        response = await self.host.send_request(request)
        print(f"[SYSTEM API] ✅ Summary received for {owner}/{repo}")
        return response

    async def summarize_commits(self, owner: str, repo: str) -> Dict[str, Any]:
        await self.start_system()

        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "summarize.commits",
            "params": {"owner": owner, "repo": repo}
        }

        print(f"[SYSTEM API] 📨 Sending summarize_commits for {owner}/{repo}")
        return await self.host.send_request(request)

    async def summarize_issues(self, owner: str, repo: str) -> Dict[str, Any]:
        await self.start_system()

        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "summarize.issues",
            "params": {"owner": owner, "repo": repo}
        }

        print(f"[SYSTEM API] 📨 Sending summarize_issues for {owner}/{repo}")
        return await self.host.send_request(request)

    async def summarize_pull_requests(self, owner: str, repo: str) -> Dict[str, Any]:
        await self.start_system()

        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "summarize.pull_requests",
            "params": {"owner": owner, "repo": repo}
        }

        print(f"[SYSTEM API] 📨 Sending summarize_pull_requests for {owner}/{repo}")
        return await self.host.send_request(request)

    # -------------------------------------------------------
    # 🧭 Utility / Health Methods
    # -------------------------------------------------------
    async def ping(self) -> bool:
        """
        Simple health check to verify that the host and server
        are responding.
        """
        try:
            await self.start_system()
            request = {"jsonrpc": "2.0", "id": 99, "method": "ping", "params": {}}
            response = await self.host.send_request(request)
            return bool(response.get("result", {}).get("ok", False))
        except Exception as ex:
            print(f"
