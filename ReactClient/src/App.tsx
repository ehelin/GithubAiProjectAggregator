// src/App.tsx

import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Sidebar from "./components/layout/Sidebar";
import Header from "./components/layout/Header";

import AnalyzeRepo from "./pages/AnalyzeRepo";
import Dashboard from "./pages/Dashboard";

const App = () =>
{
    return (
        <BrowserRouter>
            <div style={{ display: "flex", height: "100vh" }}>
                <Sidebar />

                <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
                    <Header />

                    <div style={{ padding: "1rem", overflow: "auto" }}>
                        <Routes>
                            <Route path="/analyze" element={<AnalyzeRepo />} />
                            <Route path="/dashboard" element={<Dashboard />} />

                            {/* Default redirect */}
                            <Route path="*" element={<Navigate to="/analyze" replace />} />
                        </Routes>
                    </div>
                </div>
            </div>
        </BrowserRouter>
    );
};

export default App;
