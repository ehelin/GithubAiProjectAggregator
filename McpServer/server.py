# entrypoint, registers tools/resources/events.
class my_class(object):
    pass

# 1. server.py
# Role: The entrypoint.
# What it does:
#   Starts the MCP server (JSON-RPC loop).
#   Registers tools/resources/events that the client can call.
#   Routes requests to the correct implementation module (summarizer, embeddings, github_api).
# Think of it like: Program.cs in .NET — the main bootstrapper.
