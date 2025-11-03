# GithubAiProjectAggregator
> A Model Context Protocol (MCP) system that enables a local (or hybrid) model to work with real software context instead of generating code blindly.

This project demonstrates how a developer can collaborate with an AI model **that is aware of the actual codebase** — including structure, commit history, tests, and architectural patterns. The AI is not treated as a code generator that works in isolation, but as a partner that can navigate and interpret the same environment the developer works in.

The goal of this project is **clarity and augmentation**, not automation.

The developer remains the decision-maker.  
The model assists by surfacing insights.

---

## 🧭 What This System Enables

- The model can **inspect and summarize repository structure**
- Understand **commit history & code evolution**
- Identify **hotspots or refactoring targets**
- Clarify **module responsibilities and relationships**
- Help with **architecture comprehension**

Example queries this system supports:

> “Explain the purpose and interactions of the components in `services/payments`.”

> “Which modules were most frequently edited in the last month and why?”

This shifts AI from *producing code* to *supporting developer understanding*.

---

## 🧱 Architecture Overview

| Component | Role |
|----------|------|
| **Web** | React + C# UI |
| **McpClient** | C# JSON‑RPC bridge into the MCP server |
| **McpHost** | C# runtime-layer that launches and streams to Python |
| **McpServer (Python)** | Implements MCP tools and interacts with the model + repo |

**Internal flow inside McpServer:**

```
server.py        # Entry point and dispatcher
tools.py         # Defines MCP tool operations
repo_index.py    # Reads repo tree, diffs, commit metadata
summarizer.py    # Creates contextual summaries using a local model
embeddings.py    # Optional: builds vector embeddings if needed
```

---

## 🚀 Setup & Running

### Requirements
- Python 3.10+
- .NET SDK
- (Optional) GPU if running local Phi‑3 or bge‑m3 models

### Clone

```
git clone https://github.com/ehelin/GithubAiProjectAggregator.git
```

### MCP Server (Python)

```
cd McpServer
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Host + UI (C#)

Open the solution:

```
GithubAiProjectAggregator.sln
```

Run:
- `McpHost` → starts the MCP server bridge
- `Web` → opens the UI dashboard

---

## 📌 Project State

This version is **complete and stable for its intended purpose**.  
Future enhancements may be explored later, but there is **no active development underway right now.**

You can use, fork, learn from, or extend the system as-is.

---

## 🏁 Philosophy

We are not removing the developer.  
We are **raising the baseline** so the developer can focus on clarity, architecture, and intent — while the model supports understanding and insight where needed.
