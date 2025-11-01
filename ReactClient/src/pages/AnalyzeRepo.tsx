// src/pages/AnalyzeRepo.tsx
import type { SummaryResponse } from "../api/mcpClient";
import type { FC } from "react";
import { useState } from "react";
import { useSearchParams } from "react-router-dom";
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
    const [searchParams, setSearchParams] = useSearchParams();
    const mode = (searchParams.get("mode") as "readme" | "commits" | "issues" | "pulls") ?? "readme";

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
            <div style={{ marginTop: "1rem", display: "flex", gap: "0.5rem" }}>
                {[
                    { id: "readme", label: "README" },
                    { id: "commits", label: "COMMITS" },
                    { id: "issues", label: "ISSUES" },
                    { id: "pulls", label: "PRS" }
                ].map(t => (
                    <button
                        key={t.id}
                        onClick={() => setSearchParams({ mode: t.id, owner, repo })}
                        style={{
                            padding: "0.5rem 1rem",
                            borderRadius: "6px",
                            border: "1px solid #ccc",
                            fontWeight: mode === t.id ? "bold" : "normal",
                            background: mode === t.id ? "#e5e7eb" : "#f9fafb",
                            boxShadow: mode === t.id ? "0 0 0 2px #3b82f6 inset" : "none",
                            cursor: "pointer"
                        }}
                    >
                        {t.label}
                    </button>
                ))}
            </div>

            {/* Analyze Action */}
            <div style={{ marginTop: "1rem" }}>
                <button onClick={handleAnalyze}>Analyze</button>
            </div>

            {/* Result Display */}
            {result ? (
                <div style={{
                    marginTop: "1rem",
                    background: "#fff",
                    padding: "1rem",
                    borderRadius: 8,
                    boxShadow: "0 1px 4px rgba(0,0,0,.08)",
                    maxHeight: "50vh",
                    overflow: "auto"
                }}>
                    <pre style={{ whiteSpace: "pre-wrap", margin: 0 }}>
                        {JSON.stringify((result.data as any).result ?? result.data, null, 2)}
                    </pre>
                </div>
            ) : null}
        </div>
    );
};

export default AnalyzeRepo;