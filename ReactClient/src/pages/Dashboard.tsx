import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { listSummaries, loadSummary } from "../api/mcpClient";

// Simple markdown renderer for summary text
const renderMarkdown = (text: string) => {
    const lines = text.split('\n');
    const elements: React.ReactNode[] = [];

    lines.forEach((line, index) => {
        let element: React.ReactNode;

        // Skip lines that are just a forward slash
        if (line.trim() === '/') {
            return;
        }

        // Handle headings
        if (line.startsWith('#### ')) {
            element = <h4 key={index} style={{ fontSize: '16px', fontWeight: '600', marginTop: '16px', marginBottom: '8px', color: '#1f2937', wordWrap: 'break-word' }}>{line.replace('#### ', '')}</h4>;
        } else if (line.startsWith('### ')) {
            element = <h3 key={index} style={{ fontSize: '18px', fontWeight: '700', marginTop: '20px', marginBottom: '10px', color: '#111827', wordWrap: 'break-word' }}>{line.replace('### ', '')}</h3>;
        } else if (line.startsWith('## ')) {
            element = <h2 key={index} style={{ fontSize: '20px', fontWeight: '700', marginTop: '24px', marginBottom: '12px', color: '#111827', wordWrap: 'break-word' }}>{line.replace('## ', '')}</h2>;
        } else if (line.trim() === '') {
            element = <div key={index} style={{ height: '8px' }} />;
        } else {
            // Handle bold text within the line
            const parts = line.split(/(\*\*.*?\*\*)/g);
            const formattedLine = parts.map((part, i) => {
                if (part.startsWith('**') && part.endsWith('**')) {
                    return <strong key={i} style={{ fontWeight: '600', color: '#1f2937' }}>{part.slice(2, -2)}</strong>;
                }
                return <span key={i}>{part}</span>;
            });
            element = <p key={index} style={{ marginBottom: '8px', lineHeight: '1.6', color: '#374151', wordWrap: 'break-word' }}>{formattedLine}</p>;
        }

        elements.push(element);
    });

    return <div style={{ wordWrap: 'break-word', overflowWrap: 'break-word' }}>{elements}</div>;
};

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

                <div className="space-y-2">
                    {Object.entries(grouped).map(([owner, repos]: any) => (
                        Object.entries(repos).map(([repo, modes]: any) => (
                            <div key={`${owner}-${repo}`} style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                                <span style={{ fontWeight: 'bold', marginRight: '8px' }}>Owner:</span>
                                <span>{owner}</span>
                                <span style={{ fontWeight: 'bold', marginRight: '8px' }}>Repo:</span>
                                <span>{repo}</span>
                                {modes.map((mode: string) => (
                                    <button
                                        key={mode}
                                        onClick={() => handleSelect(owner, repo, mode)}
                                        className="px-3 py-1 text-sm bg-blue-100 hover:bg-blue-200 rounded"
                                    >
                                        {mode}
                                    </button>
                                ))}
                            </div>
                        ))
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
                    <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
                        <div>
                            {data.owner && data.repo && (
                                <h1 className="text-3xl font-bold">
                                    {data.owner}/{data.repo}
                                </h1>
                            )}
                            {data.mode && (
                                <p className="text-sm text-gray-500 mt-1">Mode: {data.mode}</p>
                            )}
                        </div>
                        <button
                            onClick={() => setShowRaw(!showRaw)}
                            style={{
                                padding: '8px 16px',
                                backgroundColor: showRaw ? '#3b82f6' : '#f3f4f6',
                                color: showRaw ? '#ffffff' : '#1f2937',
                                border: '1px solid #e5e7eb',
                                borderRadius: '6px',
                                fontWeight: '600',
                                cursor: 'pointer',
                                transition: 'all 0.2s ease',
                                flexShrink: 0
                            }}
                        >
                            {showRaw ? "Show Formatted" : "Show Raw JSON"}
                        </button>
                    </header>

                    {!showRaw ? (
                        <>
                            <section style={{
                                backgroundColor: '#f9fafb',
                                padding: '24px',
                                borderRadius: '8px',
                                border: '1px solid #e5e7eb'
                            }}>
                                <h2 style={{
                                    fontSize: '20px',
                                    fontWeight: '700',
                                    marginBottom: '16px',
                                    color: '#111827',
                                    borderBottom: '2px solid #3b82f6',
                                    paddingBottom: '8px'
                                }}>
                                    Summary
                                </h2>
                                <div>
                                    {renderMarkdown(data.summary)}
                                </div>
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
                        </>
                    ) : (
                        <section>
                            <pre style={{
                                padding: '24px',
                                backgroundColor: '#1f2937',
                                color: '#f9fafb',
                                borderRadius: '8px',
                                fontSize: '13px',
                                overflowY: 'auto',
                                maxHeight: '70vh',
                                lineHeight: '1.5',
                                whiteSpace: 'pre-wrap',
                                wordWrap: 'break-word',
                                overflowWrap: 'break-word'
                            }}>
                                {JSON.stringify(data, null, 2)}
                            </pre>
                        </section>
                    )}
                </section>
            )}
        </div>
    );
}
