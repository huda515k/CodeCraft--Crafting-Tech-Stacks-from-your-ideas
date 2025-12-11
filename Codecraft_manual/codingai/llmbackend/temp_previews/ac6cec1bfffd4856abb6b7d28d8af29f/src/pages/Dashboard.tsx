import React from 'react';
import { useAuth } from '../hooks/useAuth';
import Button from '../components/Button';

const Dashboard: React.FC = () => {
  const { isAuthenticated, logout } = useAuth();

  return (
    <div className="flex flex-col min-h-screen">
      <header className="bg-blue-500 text-white p-4 shadow-md">
        <div className="container mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold">Dashboard</h1>
          <Button onClick={logout}>Logout</Button>
        </div>
      </header>
      <main className="flex-grow">
        <section className="p-4 container mx-auto grid grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-2">Total Customers</h2>
            <p className="text-2xl font-semibold">50</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-2">Active Leads</h2>
            <p className="text-2xl font-semibold">10</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow-md">
            <h2 className="text-xl font-bold mb-2">Monthly Revenue</h2>
            <p className="text-2xl font-semibold">$5,000</p>
          </div>
        </section>
        <section className="p-4 container mx-auto">
          <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
          <ul>
            <li>Customer John Doe added a new lead</li>
            <li>Deal for Jane Smith moved to Qualified stage</li>
            <li>User settings updated by admin</li>
          </ul>
        </section>
      </main>
    </div>
  );
};

export default Dashboard;