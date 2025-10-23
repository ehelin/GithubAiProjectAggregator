namespace Test
{
    internal class Program
    {
        static async Task Main(string[] args)
        {
            var test = await RunMcpClient();
        }

        private async static Task<int> RunMcpClient()
        {
            var client = new McpClient.McpClient();

            string readme = await client.SummarizeReadmeAsync("microsoft", "vscode");
            Console.WriteLine(readme);

            string commits = await client.SummarizeCommitsAsync("microsoft", "vscode");
            Console.WriteLine(commits);

            string issues = await client.SummarizeIssuesAsync("microsoft", "vscode");
            Console.WriteLine(issues);

            string prs = await client.SummarizePullRequestsAsync("microsoft", "vscode");
            Console.WriteLine(prs);

            return 1;
        }
    }
}
