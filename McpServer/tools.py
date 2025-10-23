# tools.py
# Role: Provide a decorator to register MCP tools + store them in a registry.

from typing import Callable, Dict, Any

# Tool registry — MCP server uses this to register all tools at runtime
TOOLS: Dict[str, Callable[..., Any]] = {}

def tool(name: str):
    """
    Decorator to register a function as an MCP tool.
    Usage:
        @tool("summarize.readme")
        async def some_function(...):
            ...
    """
    def decorator(func: Callable[..., Any]):
        TOOLS[name] = func
        return func
    return decorator
