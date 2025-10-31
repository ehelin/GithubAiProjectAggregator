// src/pages/AnalyzeRepo.tsx
import type { SummaryResponse } from "../api/mcpClient";
import type { FC } from "react";
import { useState } from "react";
import
    {
        summarizeReadme,
        summarizeCommits,
        summarizeIssues,
        summarizePullRequests
    } from "../api/mcpClient";

const AnalyzeRepo: FC = () =>
{
    const [owner, setOwner] = useState("");
    const [repo, setRepo] = useState("");

    // which summary type the user wants
    const [mode, setMode] = useState<"readme" | "commits" | "issues" | "pulls">("readme");

    // holds returned summary data
    const [result, setResult] = useState<SummaryResponse | null>(null);

    async function handleAnalyze()
    {
        if (!owner || !repo) {
            alert("Enter owner and repo first.");
            return;
        }

        let response: SummaryResponse;

        switch (mode) {
            case "readme":
                response = await summarizeReadme(owner, repo);
                break;
            case "commits":
                response = await summarizeCommits(owner, repo);
                break;
            case "issues":
                response = await summarizeIssues(owner, repo);
                break;
            case "pulls":
                response = await summarizePullRequests(owner, repo);
                break;
            default:
                return;
        }

        setResult(response);
    }

    return (
        <div>
            <h2>Analyze Repository</h2>

            {/* Owner / Repo Inputs */}
            <div>
                <input
                    placeholder="owner (e.g., facebook)"
                    value={owner}
                    onChange={(e) => setOwner(e.target.value)}
                />

                <input
                    placeholder="repo (e.g., react)"
                    value={repo}
                    onChange={(e) => setRepo(e.target.value)}
                />
            </div>

            {/* Mode Tabs */}
            <div style={{ marginTop: "1rem" }}>
                <button onClick={() => setMode("readme")}>README</button>
                <button onClick={() => setMode("commits")}>COMMITS</button>
                <button onClick={() => setMode("issues")}>ISSUES</button>
                <button onClick={() => setMode("pulls")}>PRS</button>
            </div>

            {/* Analyze Action */}
            <div style={{ marginTop: "1rem" }}>
                <button onClick={handleAnalyze}>Analyze</button>
            </div>

            {/* Result Display */}
            {result && (
                <pre style={{ marginTop: "2rem", whiteSpace: "pre-wrap" }}>
                    {JSON.stringify(result.data, null, 2)}
                </pre>
            )}
        </div>
    );
};

export default AnalyzeRepo;