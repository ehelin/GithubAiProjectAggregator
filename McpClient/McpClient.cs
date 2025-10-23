using System;
using System.Diagnostics;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;

namespace McpClient
{
    public class McpClient
    {
        private readonly Process _mcpProcess;

        public McpClient(Process existingProcess)
        {
            if (existingProcess == null)
                throw new ArgumentNullException(nameof(existingProcess));

            if (existingProcess.HasExited)
                throw new InvalidOperationException("The MCP server process has already exited.");

            _mcpProcess = existingProcess;
        }

        // ------------------------------------------------------
        //  Public API Methods
        // ------------------------------------------------------

        public async Task<string> SummarizeReadmeAsync(string owner, string repo) =>
            await CallMcpToolAsync("summarize.readme", owner, repo);

        public async Task<string> SummarizeCommitsAsync(string owner, string repo) =>
            await CallMcpToolAsync("summarize.commits", owner, repo);

        public async Task<string> SummarizeIssuesAsync(string owner, string repo) =>
            await CallMcpToolAsync("summarize.issues", owner, repo);

        public async Task<string> SummarizePullRequestsAsync(string owner, string repo) =>
            await CallMcpToolAsync("summarize.pull_requests", owner, repo);

        // ------------------------------------------------------
        //  Core JSON-RPC Call Logic
        // ------------------------------------------------------

        private async Task<string> CallMcpToolAsync(string toolName, string owner, string repo)
        {
            var request = new
            {
                jsonrpc = "2.0",
                id = Guid.NewGuid().ToString(),
                method = toolName,
                @params = new { owner = owner, repo = repo }
            };

            string jsonRequest = JsonSerializer.Serialize(request);

            // Send request to the Python MCP server
            await _mcpProcess.StandardInput.WriteLineAsync(jsonRequest);
            await _mcpProcess.StandardInput.FlushAsync();

            // Read and parse the response
            string? responseLine = await _mcpProcess.StandardOutput.ReadLineAsync();
            if (responseLine == null)
                return "⚠ No response received from MCP server.";

            using var doc = JsonDocument.Parse(responseLine);

            // Successful result
            if (doc.RootElement.TryGetProperty("result", out var result))
                return result.ToString();

            // Error from JSON-RPC server
            if (doc.RootElement.TryGetProperty("error", out var error))
                return "❌ MCP Error: " + error.ToString();

            // Unexpected format
            return "⚠ Unexpected JSON-RPC response: " + responseLine;
        }
    }
}
