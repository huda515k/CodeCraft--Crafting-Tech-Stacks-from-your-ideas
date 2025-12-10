import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import DashboardPage from './pages/DashboardPage';
import WorkersPage from './pages/WorkersPage';
import InventoryPage from './pages/InventoryPage';
import RevenuePage from './pages/RevenuePage';

const App: React.FC = () => {
  return (
    <div className="flex flex-col min-h-screen bg-gray-100">
      <Header />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/workers" element={<WorkersPage />} />
            <Route path="/inventory" element={<InventoryPage />} />
            <Route path="/revenue" element={<RevenuePage />} />
            {/* Add more routes here */}
          </Routes>
        </main>
      </div>
    </div>
  );
};

export default App;