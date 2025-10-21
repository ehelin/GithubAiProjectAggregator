namespace Test
{
    internal class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Hello, World!");
        }

        private async static Task RunMcpClien()
        {
            var client = new McpClient.McpClient();

            string readme = await client.SummarizeReadmeAsync("microsoft", "vscode");
            string commits = await client.SummarizeCommitsAsync("microsoft", "vscode");
            string issues = await client.SummarizeIssuesAsync("microsoft", "vscode");
            string prs = await client.SummarizePullRequestsAsync("microsoft", "vscode");

            Console.WriteLine(readme);
            Console.WriteLine(commits);
            Console.WriteLine(issues);
            Console.WriteLine(prs);
        }
    }
}
