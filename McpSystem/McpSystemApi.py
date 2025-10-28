# ===========================================================
# McpSystemApi.py
# -----------------------------------------------------------
# High-level Application API + integrated FastAPI server
# -----------------------------------------------------------
# - Starts and manages the MCP Host system
# - Exposes HTTP endpoints (so C# or tools can call it)
# - Delegates work to McpHostController for real logic
# ===========================================================

import asyncio
import json
import os
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from McpHost import McpHostController

# 🔧 Debug mode: True = direct calls (VS debugger friendly), False = subprocess mode
DEBUG_MODE = os.getenv("MCP_DEBUG_MODE", "true").lower() == "true"


# ===========================================================
# 🧪 Debug Mode Controller (Direct Calls - No Subprocesses)
# ===========================================================
class McpDebugController:
    """Debug-friendly controller that calls tools directly without subprocesses."""

    def __init__(self):
        self._started = False
        self._summarizer = None

    async def start(self):
        if not self._started:
            print("[DEBUG API] 🐛 Starting MCP in DEBUG mode (direct calls, no subprocesses)...")
            # Import here to avoid circular dependency
            from Summarizer import Summarizer
            self._summarizer = Summarizer()
            self._started = True
            print("[DEBUG API] ✅ MCP DEBUG mode ready.")

    async def stop(self):
        print("[DEBUG API] 🛑 Stopping DEBUG mode...")
        self._started = False

    async def send_request(self, request: dict) -> dict:
        """Handle request by directly calling tool methods."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id", 1)

        try:
            if method == "summarize.readme":
                result = self._summarizer.summarize_repo_readme(**params)
            elif method == "summarize.commits":
                result = self._summarizer.summarize_commits(**params)
            elif method == "summarize.issues":
                result = self._summarizer.summarize_issues(**params)
            elif method == "summarize.pull_requests":
                result = self._summarizer.summarize_pull_requests(**params)
            elif method == "ping":
                result = {"ok": True, "mode": "debug"}
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown method: {method}"}
                }

            return {"jsonrpc": "2.0", "id": request_id, "result": result}

        except Exception as ex:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32000, "message": str(ex)}
            }


# ===========================================================
# 🧠 Core API class
# ===========================================================
class McpSystemApi:
    """Application API to communicate with the MCP Host."""

    def __init__(self, debug: bool = False):
        self.debug = debug or DEBUG_MODE
        if self.debug:
            print("[SYSTEM API] 🐛 Using DEBUG mode (direct calls)")
            self.host = McpDebugController()
        else:
            print("[SYSTEM API] 🚀 Using PRODUCTION mode (subprocesses)")
            self.host = McpHostController()
        self._started = False

    # -------------------------------
    # Lifecycle
    # -------------------------------
    async def start_system(self):
        if not self._started:
            print("[SYSTEM API] 🚀 Starting MCP system (Host + Client + Server)...")
            await self.host.start()
            self._started = True
            print("[SYSTEM API] ✅ MCP system ready.")
        else:
            print("[SYSTEM API] 🔁 MCP system already running.")

    async def stop_system(self):
        if self._started:
            print("[SYSTEM API] 🛑 Stopping MCP system...")
            await self.host.stop()
            self._started = False
            print("[SYSTEM API] ✅ MCP system stopped.")
        else:
            print("[SYSTEM API] 💤 MCP system not running.")

    # -------------------------------
    # Summarization endpoints
    # -------------------------------
    async def summarize_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        await self.start_system()
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "summarize.readme",
            "params": {"owner": owner, "repo": repo},
        }
        print(f"[SYSTEM API] 📨 summarize_repo({owner}/{repo})...")
        return await self.host.send_request(request)

    async def summarize_commits(self, owner: str, repo: str) -> Dict[str, Any]:
        await self.start_system()
        req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "summarize.commits",
            "params": {"owner": owner, "repo": repo},
        }
        return await self.host.send_request(req)

    async def summarize_issues(self, owner: str, repo: str) -> Dict[str, Any]:
        await self.start_system()
        req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "summarize.issues",
            "params": {"owner": owner, "repo": repo},
        }
        return await self.host.send_request(req)

    async def summarize_pulls(self, owner: str, repo: str) -> Dict[str, Any]:
        await self.start_system()
        req = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "summarize.pull_requests",
            "params": {"owner": owner, "repo": repo},
        }
        return await self.host.send_request(req)

    # -------------------------------
    # Health check
    # -------------------------------
    async def ping(self) -> bool:
        try:
            await self.start_system()
            req = {"jsonrpc": "2.0", "id": 99, "method": "ping", "params": {}}
            resp = await self.host.send_request(req)
            ok = bool(resp.get("result", {}).get("ok", False))
            print(f"[SYSTEM API] 🩺 Ping result: {ok}")
            return ok
        except Exception as ex:
            print(f"[SYSTEM API] ⚠️ Ping failed: {ex}")
            return False


# ===========================================================
# 🌐 Integrated FastAPI server
# ===========================================================

app = FastAPI(title="MCP System API", version="1.0.0")
api = McpSystemApi()  # Will auto-detect DEBUG_MODE from environment

class RepoRequest(BaseModel):
    owner: str
    repo: str


@app.get("/ping")
async def ping():
    ok = await api.ping()
    if ok:
        return {"status": "ok"}
    raise HTTPException(status_code=503, detail="MCP system unresponsive")


@app.post("/summarize/readme")
async def summarize_readme(req: RepoRequest):
    try:
        result = await api.summarize_repo(req.owner, req.repo)
        return {"status": "ok", "data": result}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@app.post("/summarize/commits")
async def summarize_commits(req: RepoRequest):
    try:
        result = await api.summarize_commits(req.owner, req.repo)
        return {"status": "ok", "data": result}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@app.post("/summarize/issues")
async def summarize_issues(req: RepoRequest):
    try:
        result = await api.summarize_issues(req.owner, req.repo)
        return {"status": "ok", "data": result}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))


@app.post("/summarize/pulls")
async def summarize_pulls(req: RepoRequest):
    try:
        result = await api.summarize_pulls(req.owner, req.repo)
        return {"status": "ok", "data": result}
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

if __name__ == "__main__":
    print("[MCP SYSTEM API] 🚀 Launching web server on http://localhost:8000")
    uvicorn.run("McpSystemApi:app", host="0.0.0.0", port=8000, reload=False)
