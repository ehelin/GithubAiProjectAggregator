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

type ModeType = "readme" | "commits" | "issues" | "pulls";
type ModeStatus = "pending" | "running" | "completed" | "error";

interface ModeResult {
    mode: ModeType;
    status: ModeStatus;
    response?: SummaryResponse;
    error?: string;
}

const AnalyzeRepo: FC = () =>
{
    const [owner, setOwner] = useState("");
    const [repo, setRepo] = useState("");

    // which summary type the user wants (for single mode analysis)
    const [searchParams, setSearchParams] = useSearchParams();
    const mode = (searchParams.get("mode") as ModeType) ?? "readme";

    // holds returned summary data for single mode
    const [result, setResult] = useState<SummaryResponse | null>(null);

    // holds all results for "Analyze All" mode
    const [allResults, setAllResults] = useState<ModeResult[]>([]);
    const [isAnalyzingAll, setIsAnalyzingAll] = useState(false);
    const [expandedModes, setExpandedModes] = useState<Set<ModeType>>(new Set());

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
        setAllResults([]); // Clear all results when doing single analysis
    }

    async function handleAnalyzeAll()
    {
        if (!owner || !repo) {
            alert("Enter owner and repo first.");
            return;
        }

        setIsAnalyzingAll(true);
        setResult(null); // Clear single result

        const modes: ModeType[] = ["readme", "commits", "issues", "pulls"];
        const initialResults: ModeResult[] = modes.map(m => ({ mode: m, status: "pending" as ModeStatus }));
        setAllResults(initialResults);

        // Process each mode serially with manual state tracking
        const finalResults: ModeResult[] = [...initialResults];

        for (let i = 0; i < modes.length; i++) {
            const currentMode = modes[i];

            // Update status to running
            finalResults[i] = { ...finalResults[i], status: "running" };
            setAllResults([...finalResults]);

            // Add small delay to ensure state update is visible
            await new Promise(resolve => setTimeout(resolve, 100));

            try {
                let response: SummaryResponse;

                switch (currentMode) {
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
                }

                // Update with completed result
                finalResults[i] = { ...finalResults[i], status: "completed", response };
                setAllResults([...finalResults]);

                // Auto-expand first completed result
                if (i === 0) {
                    setExpandedModes(new Set([currentMode]));
                }

            } catch (error) {
                // Update with error
                finalResults[i] = { ...finalResults[i], status: "error", error: String(error) };
                setAllResults([...finalResults]);
            }
        }

        setIsAnalyzingAll(false);
    }

    function toggleExpanded(mode: ModeType) {
        setExpandedModes(prev => {
            const newSet = new Set(prev);
            if (newSet.has(mode)) {
                newSet.delete(mode);
            } else {
                newSet.add(mode);
            }
            return newSet;
        });
    }

    return (
        <div>
            <h2>Analyze Repository</h2>

            {/* Owner / Repo Inputs */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <span style={{ fontWeight: 'bold', marginRight: '8px' }}>Owner:</span>
                <input
                    placeholder="e.g., facebook"
                    value={owner}
                    onChange={(e) => setOwner(e.target.value)}
                    style={{ padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
                />

                <span style={{ fontWeight: 'bold', marginRight: '8px' }}>Repo:</span>
                <input
                    placeholder="e.g., react"
                    value={repo}
                    onChange={(e) => setRepo(e.target.value)}
                    style={{ padding: '8px', border: '1px solid #ccc', borderRadius: '4px' }}
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
            <div style={{ marginTop: "1rem", display: "flex", gap: "12px", alignItems: "center" }}>
                <button
                    onClick={handleAnalyze}
                    style={{
                        padding: "10px 20px",
                        backgroundColor: "#3b82f6",
                        color: "#ffffff",
                        border: "none",
                        borderRadius: "6px",
                        fontWeight: "600",
                        cursor: "pointer"
                    }}
                >
                    Analyze {mode.toUpperCase()}
                </button>

                <button
                    onClick={handleAnalyzeAll}
                    disabled={isAnalyzingAll}
                    style={{
                        padding: "10px 20px",
                        backgroundColor: isAnalyzingAll ? "#9ca3af" : "#10b981",
                        color: "#ffffff",
                        border: "none",
                        borderRadius: "6px",
                        fontWeight: "600",
                        cursor: isAnalyzingAll ? "not-allowed" : "pointer"
                    }}
                >
                    {isAnalyzingAll ? "⏳ Analyzing All..." : "🚀 Analyze All Modes"}
                </button>
            </div>

            {/* Single Result Display */}
            {result && allResults.length === 0 && (
                <div style={{
                    marginTop: "1.5rem",
                    background: "#f9fafb",
                    padding: "1.5rem",
                    borderRadius: 8,
                    border: "1px solid #e5e7eb"
                }}>
                    <h3 style={{ marginTop: 0, marginBottom: "1rem", color: "#1f2937" }}>
                        Result: {mode.toUpperCase()}
                    </h3>
                    <pre style={{
                        whiteSpace: "pre-wrap",
                        margin: 0,
                        backgroundColor: "#1f2937",
                        color: "#f9fafb",
                        padding: "1rem",
                        borderRadius: "6px",
                        fontSize: "13px",
                        maxHeight: "60vh",
                        overflowY: "auto"
                    }}>
                        {JSON.stringify((result.data as any).result ?? result.data, null, 2)}
                    </pre>
                </div>
            )}

            {/* All Results Display (Accordion) */}
            {allResults.length > 0 && (
                <div style={{ marginTop: "1.5rem" }}>
                    <h3 style={{ color: "#1f2937", marginBottom: "1rem" }}>
                        Analysis Results - All Modes
                    </h3>

                    {allResults.map((modeResult, idx) => {
                        const isExpanded = expandedModes.has(modeResult.mode);
                        const statusEmoji = {
                            pending: "⏸️",
                            running: "⏳",
                            completed: "✅",
                            error: "❌"
                        };
                        const statusColor = {
                            pending: "#9ca3af",
                            running: "#3b82f6",
                            completed: "#10b981",
                            error: "#ef4444"
                        };

                        return (
                            <div
                                key={modeResult.mode}
                                style={{
                                    marginBottom: "12px",
                                    border: "1px solid #e5e7eb",
                                    borderRadius: "8px",
                                    overflow: "hidden"
                                }}
                            >
                                {/* Accordion Header */}
                                <div
                                    onClick={() => modeResult.status === "completed" && toggleExpanded(modeResult.mode)}
                                    style={{
                                        padding: "16px",
                                        backgroundColor: isExpanded ? "#f3f4f6" : "#ffffff",
                                        cursor: modeResult.status === "completed" ? "pointer" : "default",
                                        display: "flex",
                                        justifyContent: "space-between",
                                        alignItems: "center",
                                        borderBottom: isExpanded ? "1px solid #e5e7eb" : "none"
                                    }}
                                >
                                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                                        <span style={{ fontSize: "20px" }}>{statusEmoji[modeResult.status]}</span>
                                        <span style={{ fontWeight: "600", color: "#1f2937" }}>
                                            {modeResult.mode.toUpperCase()}
                                        </span>
                                        <span style={{
                                            fontSize: "12px",
                                            color: statusColor[modeResult.status],
                                            fontWeight: "600"
                                        }}>
                                            {modeResult.status.charAt(0).toUpperCase() + modeResult.status.slice(1)}
                                        </span>
                                    </div>
                                    {modeResult.status === "completed" && (
                                        <span style={{ fontSize: "18px", color: "#6b7280" }}>
                                            {isExpanded ? "▼" : "▶"}
                                        </span>
                                    )}
                                </div>

                                {/* Accordion Content */}
                                {isExpanded && modeResult.status === "completed" && modeResult.response && (
                                    <div style={{ padding: "16px", backgroundColor: "#fafafa" }}>
                                        <pre style={{
                                            whiteSpace: "pre-wrap",
                                            margin: 0,
                                            backgroundColor: "#1f2937",
                                            color: "#f9fafb",
                                            padding: "1rem",
                                            borderRadius: "6px",
                                            fontSize: "13px",
                                            maxHeight: "50vh",
                                            overflowY: "auto"
                                        }}>
                                            {JSON.stringify(
                                                modeResult.response?.data
                                                    ? ((modeResult.response.data as any).result ?? modeResult.response.data)
                                                    : modeResult.response,
                                                null,
                                                2
                                            )}
                                        </pre>
                                    </div>
                                )}

                                {/* Error Display */}
                                {modeResult.status === "error" && (
                                    <div style={{
                                        padding: "16px",
                                        backgroundColor: "#fef2f2",
                                        color: "#991b1b"
                                    }}>
                                        Error: {modeResult.error}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default AnalyzeRepo;