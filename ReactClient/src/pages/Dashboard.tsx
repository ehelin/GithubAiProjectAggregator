import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { listSummaries, loadSummary } from "../api/mcpClient";

interface SummaryMeta
{
    owner: string;
    repo: string;
    mode: string;
}

interface SummaryData
{
    summary: string;
    key_points?: string[];
    raw?: any;
    owner: string;
    repo: string;
    mode: string;
}

export default function Dashboard()
{
    const navigate = useNavigate();
    const { state } = useLocation();

    const [data, setData] = useState<SummaryData | null>(state?.summary || null);
    const [available, setAvailable] = useState<SummaryMeta[]>([]);
    const [showRaw, setShowRaw] = useState(false);

    // Load list of summaries on initial load (through mcpClient)
    useEffect(() =>
    {
        listSummaries().then((json) =>
        {
            if (json.status === "ok") {
                setAvailable(json.data);
            }
        });
    }, []);

    // If Dashboard received summary context from Analyze screen, try to load it here (also through mcpClient)
    useEffect(() =>
    {
        if (!data && state?.owner && state?.repo && state?.mode) {
            loadSummary(state.owner, state.repo, state.mode).then((json) =>
            {
                if (json.status === "ok") {
                    setData(json.data);
                }
            });
        }
    }, [data, state]);

    // Group summaries → { owner → repo → [modes] }
    const grouped = available.reduce((acc: any, item) =>
    {
        acc[item.owner] ??= {};
        acc[item.owner][item.repo] ??= [];
        acc[item.owner][item.repo].push(item.mode);
        return acc;
    }, {});

    const handleSelect = (owner: string, repo: string, mode: string) =>
    {
        loadSummary(owner, repo, mode).then((json) =>
        {
            if (json.status === "ok") {
                setData(json.data);
            } else {
                setData(null);
            }
        });
    };

    return (
        <div className="p-8 max-w-4xl mx-auto space-y-10">
            {/* Summary Browser */}
            <section>
                <h1 className="text-2xl font-bold mb-4">Available Summaries</h1>

                {Object.keys(grouped).length === 0 && (
                    <p className="text-gray-600 mb-4">
                        No summaries found. Use <strong>Analyze</strong> to create one.
                    </p>
                )}

                <div className="space-y-4">
                    {Object.entries(grouped).map(([owner, repos]: any) => (
                        <div key={owner}>
                            <h2 className="text-lg font-semibold">{owner}</h2>
                            <div className="ml-4 space-y-2">
                                {Object.entries(repos).map(([repo, modes]: any) => (
                                    <div key={repo}>
                                        <p className="font-medium text-gray-700">{repo}</p>
                                        <div className="ml-4 flex gap-2 flex-wrap">
                                            {modes.map((mode: string) => (
                                                <button
                                                    key={mode}
                                                    onClick={() => handleSelect(owner, repo, mode)}
                                                    className="px-3 py-1 text-sm bg-gray-200 hover:bg-gray-300 rounded"
                                                >
                                                    {mode}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                <button
                    onClick={() => navigate("/analyze")}
                    className="mt-6 px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700"
                >
                    Analyze New Repository
                </button>
            </section>

            {/* Summary Display */}
            {data && (
                <section className="space-y-8 border-t pt-10">
                    <header>
                        <h1 className="text-3xl font-bold">
                            {data.owner}/{data.repo}
                        </h1>
                        <p className="text-sm text-gray-500 mt-1">Mode: {data.mode}</p>
                    </header>

                    <section>
                        <h2 className="text-xl font-semibold mb-3">Summary</h2>
                        <p className="leading-relaxed whitespace-pre-line text-gray-800">
                            {data.summary}
                        </p>
                    </section>

                    {data.key_points && data.key_points.length > 0 && (
                        <section>
                            <h2 className="text-xl font-semibold mb-3">Key Points</h2>
                            <ul className="list-disc ml-6 space-y-1 text-gray-800">
                                {data.key_points.map((point, i) => (
                                    <li key={i}>{point}</li>
                                ))}
                            </ul>
                        </section>
                    )}

                    <section>
                        <button
                            onClick={() => setShowRaw(!showRaw)}
                            className="text-sm text-blue-600 underline"
                        >
                            {showRaw ? "Hide Raw Output" : "Show Raw Output"}
                        </button>

                        {showRaw && (
                            <pre className="mt-4 p-4 bg-gray-100 rounded text-xs overflow-auto">
                                {JSON.stringify(data, null, 2)}
                            </pre>
                        )}
                    </section>
                </section>
            )}
        </div>
    );
}
