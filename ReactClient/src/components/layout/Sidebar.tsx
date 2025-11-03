// src/components/layout/Sidebar.tsx

import { FC } from "react";
import { Link, useLocation } from "react-router-dom";

const Sidebar: FC = () =>
{
    const location = useLocation();

    const navItems = [
        { path: "/dashboard", label: "Dashboard", icon: "📊" },
        { path: "/analyze", label: "Analyze Repository", icon: "🔍" }
    ];

    return (
        <aside style={{
            width: '250px',
            backgroundColor: '#ffffff',
            minHeight: '100vh',
            padding: '20px 0',
            boxShadow: '2px 0 8px rgba(0,0,0,0.1)',
            borderRight: '1px solid #e5e7eb'
        }}>
            <div style={{
                padding: '0 20px 20px',
                borderBottom: '1px solid #e5e7eb',
                marginBottom: '20px'
            }}>
                <h2 style={{
                    color: '#1f2937',
                    fontSize: '18px',
                    fontWeight: 'bold',
                    margin: 0
                }}>
                    GitHub AI Aggregator
                </h2>
            </div>
            <nav>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                    {navItems.map((item) => {
                        const isActive = location.pathname === item.path;
                        return (
                            <li key={item.path} style={{ marginBottom: '8px' }}>
                                <Link
                                    to={item.path}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '12px',
                                        padding: '12px 20px',
                                        color: isActive ? '#ffffff' : '#4b5563',
                                        backgroundColor: isActive ? '#3b82f6' : 'transparent',
                                        textDecoration: 'none',
                                        fontSize: '15px',
                                        fontWeight: isActive ? '600' : '400',
                                        transition: 'all 0.2s ease',
                                        borderLeft: isActive ? '4px solid #2563eb' : '4px solid transparent'
                                    }}
                                    onMouseEnter={(e) => {
                                        if (!isActive) {
                                            e.currentTarget.style.backgroundColor = '#f3f4f6';
                                            e.currentTarget.style.color = '#1f2937';
                                        }
                                    }}
                                    onMouseLeave={(e) => {
                                        if (!isActive) {
                                            e.currentTarget.style.backgroundColor = 'transparent';
                                            e.currentTarget.style.color = '#4b5563';
                                        }
                                    }}
                                >
                                    <span style={{ fontSize: '20px' }}>{item.icon}</span>
                                    <span>{item.label}</span>
                                </Link>
                            </li>
                        );
                    })}
                </ul>
            </nav>
        </aside>
    );
};

export default Sidebar;
