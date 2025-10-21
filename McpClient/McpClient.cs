using System;
using System.Diagnostics;
using System.IO;
using System.Text.Json;
using System.Threading.Tasks;

namespace McpClient
{
    public class McpClient
    {
        private Process _mcpProcess;

        public McpClient()
        {
            StartMcpServerIfNotRunning();
        }

        private void StartMcpServerIfNotRunning()
        {
            if (_mcpProcess != null && !_mcpProcess.HasExited)
                return;

            _mcpProcess = new Process();
            _mcpProcess.StartInfo.FileName = "python";                    // Or "python3"
            _mcpProcess.StartInfo.Arguments = "mcp_server/Server.py";     // Adjust path if needed
            _mcpProcess.StartInfo.RedirectStandardInput = true;
            _mcpProcess.StartInfo.RedirectStandardOutput = true;
            _mcpProcess.StartInfo.RedirectStandardError = true;
            _mcpProcess.StartInfo.UseShellExecute = false;
            _mcpProcess.StartInfo.CreateNoWindow = true;

            _mcpProcess.Start();
            Console.WriteLine("✅ MCP Server started.");
        }

        // ------------------------ Helper Method ------------------------ //

        private async Task<string> CallMcpToolAsync(string toolName, string owner, string repo)
        {
            var request = new
            {
                jsonrpc = "2.0",
                id = Guid.NewGuid().ToString(), // unique per request
                method = toolName,
                @params = new { owner = owner, repo = repo }
            };

            string jsonRequest = JsonSerializer.Serialize(request);
            await _mcpProcess.StandardInput.WriteLineAsync(jsonRequest);
            await _mcpProcess.StandardInput.FlushAsync();

            string responseLine = await _mcpProcess.StandardOutput.ReadLineAsync();
            if (responseLine == null)
                return "⚠ No response from MCP server.";

            using JsonDocument doc = JsonDocument.Parse(responseLine);

            if (doc.RootElement.TryGetProperty("result", out var result))
                return result.ToString();

            if (doc.RootElement.TryGetProperty("error", out var error))
                return "❌ Error from MCP: " + error.ToString();

            return "⚠ Unexpected MCP response: " + responseLine;
        }

        // ------------------------ Public Methods ------------------------ //

        public async Task<string> SummarizeReadmeAsync(string owner, string repo) =>
            await CallMcpToolAsync("summarize.readme", owner, repo);

        public async Task<string> SummarizeCommitsAsync(string owner, string repo) =>
            await CallMcpToolAsync("summarize.commits", owner, repo);

        public async Task<string> SummarizeIssuesAsync(string owner, string repo) =>
            await CallMcpToolAsync("summarize.issues", owner, repo);

        public async Task<string> SummarizePullRequestsAsync(string owner, string repo) =>
            await CallMcpToolAsync("summarize.pull_requests", owner, repo);
    }
}
