# GithubAiProjectAggregator

> MCP-based tool for aggregating, summarizing, and comparing GitHub AI / ML repositories using local models.

## 📦 Structure Overview

This project is organized into multiple independent components, each with a clear responsibility:

| Component | Role |
|----------|------|
| **Web** | C# / ASP.NET / React UI: dashboards, visualizations, project trends |
| **Aggregator Service** | C# orchestration: jobs, scheduling, storing results |
| **McpClient** | C# JSON-RPC client: sends requests to the MCP Server |
| **McpHost** | C# host runtime: spawns & transports to/from the Python MCP Server |
| **McpServer** | Python-based MCP Server: implements tools (summarization, embeddings, GitHub API) |

Within **McpServer**, the internal flow is:

```
server.py → tools.py → { github_api.py, summarizer.py, embeddings.py }
```

- `server.py` is the entrypoint and dispatcher  
- `tools.py` defines MCP-level operations (SummarizeRepo, EmbedRepo, CompareRepos)  
- `github_api.py` handles GitHub API calls  
- `summarizer.py` wraps Phi‑3 model for text summarization  
- `embeddings.py` wraps bge-m3 for converting text into numeric embeddings  

---

## 🚀 Getting Started

### Prerequisites

- .NET SDK (for Web / Aggregator / Client / Host)  
- Python 3.10+  
- GPU with VRAM (≥ 8 GB) for local model usage (Phi‑3, bge-m3)  
- GitHub token with read access to target repos  

### Setup Steps

1. **Clone the repo**  
   ```bash
   git clone https://github.com/ehelin/GithubAiProjectAggregator.git
   cd GithubAiProjectAggregator
   ```

2. **Python environment for McpServer**  
   ```bash
   cd McpServer
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **C# projects**  
   Open `GithubAiProjectAggregator.sln` in Visual Studio or via `dotnet` CLI.  
   Restore dependencies, build solution.

4. **Launch host & server**  
   From your aggregator service or host, spawn the Python MCP Server.  
   The host handles transport (stdio / WebSockets) and bridges C# → Python.

5. **Run sample request**  
   Use the Web UI or a test client to call a tool like `SummarizeRepo("owner/repo")` or `CompareRepos(...)`.  
   You should see summaries, embeddings, and comparisons in your dashboard.

---

## ⚠️ Current Status & To‑Do

- All `*.py` files currently contain stub methods; functionality not yet implemented.  
- No persistence layer included — you’ll need to wire in a database if you want to store results.  
- Host / Client / Web integration is scaffold only — routing and wiring between components remains.  
- Model loading / caching / performance tuning not yet addressed.  
- Error handling, retries, rate-limiting for GitHub API calls is not in place.

---

## 🧩 How to Contribute or Build Out

1. Pick a stub you want to implement (e.g., `summarizer.summarize_repo_readme`).  
2. Implement it using local model code (reuse from Habit Tracker if available).  
3. Write unit tests in each component (e.g., input → output stubs).  
4. Integrate through `tools.py` so MCP can route that tool.  
5. Validate end-to-end: Web → Client → Host → Server → GitHub / Model → back.  
6. Add persistence (DB) to store summaries, embeddings, comparisons over time.  
7. Add scheduling, alerting, UI filtering, etc.

---

## 🧠 Why MCP (Model-Context Protocol)?

- **Separation of concerns:** the model side (Python) is decoupled from the UI/orchestration side (C#).  
- **Extensibility:** you can swap the summarization engine, embedder, or GitHub logic without rewriting the UI.  
- **Cross-language bridging:** Python can use best-in-class ML libs; C# can own orchestration, dashboards, DB.
