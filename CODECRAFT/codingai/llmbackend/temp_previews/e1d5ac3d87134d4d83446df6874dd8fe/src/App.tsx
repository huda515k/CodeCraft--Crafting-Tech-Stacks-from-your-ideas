import React, { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Customers from './pages/Customers';

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar isOpen={isSidebarOpen} onClose={() => setIsSidebarOpen(false)} />
      <div className="flex flex-col flex-1 overflow-y-auto">
        <Header onMenuToggle={toggleSidebar} />
        <main className="flex-1 pb-4">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/customers" element={<Customers />} />
            {/* Add more routes here for other pages */}
            <Route path="/orders" element={<div className="p-6 text-gray-700">Orders Page (Coming Soon!)</div>} />
            <Route path="/products" element={<div className="p-6 text-gray-700">Products Page (Coming Soon!)</div>} />
            <Route path="/reports" element={<div className="p-6 text-gray-700">Reports Page (Coming Soon!)</div>} />
            <Route path="/settings" element={<div className="p-6 text-gray-700">Settings Page (Coming Soon!)</div>} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;