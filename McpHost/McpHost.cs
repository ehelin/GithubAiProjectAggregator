using System;
using System.Diagnostics;
using System.Threading.Tasks;
using McpClient;   // <-- Reference to your McpClient.csproj

class McpHost
{
    static async Task Main(string[] args)
    {
        Console.WriteLine("🚀 Starting MCP Host...");

        // 1️⃣ Start Python MCP Server
        Process serverProcess = StartPythonServer();

        // Give the server a moment to initialize sockets/pipes
        Console.WriteLine("⏳ Waiting for MCP Server to initialize...");
        await Task.Delay(2000);

        // 2️⃣ Create the C# Client and attach it to the running Python server process
        var client = new McpClient.McpClient(serverProcess);

        // 3️⃣ Call MCP tools as a test
        try
        {
            string readmeResult = await client.SummarizeReadmeAsync("microsoft", "vscode");
            Console.WriteLine("\n📘 README Summary:");
            Console.WriteLine(readmeResult);

            string commitResult = await client.SummarizeCommitsAsync("microsoft", "vscode");
            Console.WriteLine("\n📝 Commit Summary:");
            Console.WriteLine(commitResult);
        }
        catch (Exception ex)
        {
            Console.WriteLine($"\n❌ Error while calling MCP tools: {ex.Message}");
        }

        Console.WriteLine("\n✅ Press ENTER to shut down...");
        Console.ReadLine();

        // 4️⃣ Clean Shutdown
        if (!serverProcess.HasExited)
        {
            // Optional graceful CloseMainWindow first
            serverProcess.Kill(true); // Force kill if needed
        }
        Console.WriteLine("🛑 MCP Server stopped. Exiting host...");
    }

    private static Process StartPythonServer()
    {
        // Absolute path to where Server.py lives
        string path = System.IO.Directory.GetCurrentDirectory();
        var parent = path.Substring(0, path.IndexOf("\\McpHost"));
        var mcpServerPath = Path.Combine(parent, "McpServer");
        //string parent1 = System.IO.Directory.GetParent(path).FullName;
        //string basePath = AppContext.BaseDirectory;
        //string parent = Directory.GetParent(AppContext.BaseDirectory).ToString();
        //string projectRoot = Directory.GetParent(AppContext.BaseDirectory)!.Parent!.Parent!.FullName;
        //string mcpServerPath = Path.Combine(projectRoot, "McpServer");

        var startInfo = new ProcessStartInfo
        {
            FileName = "python",                 // or "python3" depending on system
            Arguments = "Server.py",             // adjust path if in subfolder
            WorkingDirectory = mcpServerPath,  // ✅ important: folder where Server.py lives
            UseShellExecute = false,
            RedirectStandardInput = true,
            RedirectStandardOutput = true,
            RedirectStandardError = true,
            CreateNoWindow = true
        };

        var process = new Process { StartInfo = startInfo };
        process.Start();

        Console.WriteLine($"✅ MCP Server started (PID={process.Id}).");
        return process;
    }
}
