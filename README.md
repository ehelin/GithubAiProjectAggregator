# GithubAiProjectAggregator

MCP-based system that lets a local model work with a real repository context (files, commits, tests, docs) to assist the developer.  Created with ChatGPT and Claude Code as my pair programmers.

## What it does
- Exposes repo context to the model via MCP tools
- Summarizes modules and architecture
- Surfaces hotspots/refactor targets
- Keeps the developer in the review loop

## Quick start
```bash
git clone https://github.com/ehelin/GithubAiProjectAggregator.git
cd GithubAiProjectAggregator/McpServer
python McpSystemApi.py
cd GithubAiProjectAggregator/ReactClient
npm install
npm run dev
