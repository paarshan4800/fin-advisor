import React from 'react'
import { Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing/Landing';
import Transactions from './pages/Transactions/Transactions';
import InsightsHub from './pages/InsightsHub/InsightsHub';

function AppRoutes() {
    return (
        <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/transactions" element={<Transactions />} />
            <Route path="/insights-hub" element={<InsightsHub />} />
        </Routes>
    )
}

export default AppRoutes