// src/api/mcpClient.ts

export const API_BASE = "http://localhost:8000"; // or wherever MCP API runs

// Shared request model
export interface RepoRequest
{
    owner: string;
    repo: string;
}

// Shared response model (we’ll refine this when we lock data shapes)
export interface SummaryResponse
{
    status: string;
    data: any;
}

// Summarize API methods
export async function summarizeReadme(
    owner: string,
    repo: string
): Promise<SummaryResponse>
{
    var results = await postSummary('summarize/readme', owner, repo);

    return results;
}

export async function summarizeCommits(
    owner: string,
    repo: string
): Promise<SummaryResponse>
{
    return await postSummary('summarize/commits', owner, repo);
}

export async function summarizeIssues(
    owner: string,
    repo: string
): Promise<SummaryResponse>
{
    return await postSummary('summarize/issues', owner, repo);
}

export async function summarizePullRequests(
    owner: string,
    repo: string
): Promise<SummaryResponse>
{
    return await postSummary('summarize/pulls', owner, repo);
}

// summary API methods
export async function listSummaries()
{
    const res = await fetch(`${API_BASE}/summaries`);
    const json = await res.json();
    return json;
}

export async function loadSummary(owner: string, repo: string, mode: string)
{
    const res = await fetch(`${API_BASE}/summary/${owner}/${repo}/${mode}`);
    const json = await res.json();
    return json;
}

async function postSummary(
    endpoint: string,
    owner: string,
    repo: string
)
{
    const response = await fetch(`${API_BASE}/${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ owner, repo })
    });

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status} (${endpoint})`);
    }

    return response.json() as Promise<SummaryResponse>;
}

