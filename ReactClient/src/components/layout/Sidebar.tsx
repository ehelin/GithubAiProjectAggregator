// src/components/layout/Sidebar.tsx

import { FC } from "react";
import { Link } from "react-router-dom";

const Sidebar: FC = () =>
{
    return (
        <aside>
            <nav>
                <ul>
                    <li>
                        <Link to="/analyze">Analyze Repository</Link>
                    </li>
                    <li>
                        <Link to="/dashboard">Summary Dashboard</Link>
                    </li>
                    <li>
                        <Link to="/history">History</Link>
                    </li>
                </ul>
            </nav>
        </aside>
    );
};

export default Sidebar;
