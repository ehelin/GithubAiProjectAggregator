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
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from McpHost import McpHostController


# ===========================================================
# 🧠 Core API class
# ===========================================================
class McpSystemApi:
    """Application API to communicate with the MCP Host."""

    def __init__(self, debug: bool = False):
        self.debug = debug
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
api = McpSystemApi(debug=False)

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
