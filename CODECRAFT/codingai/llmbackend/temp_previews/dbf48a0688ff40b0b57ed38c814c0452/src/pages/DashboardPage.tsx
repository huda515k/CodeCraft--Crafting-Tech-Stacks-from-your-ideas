import React from 'react';
import StatCard from '../components/StatCard';
import Card from '../components/Card';

const DashboardPage: React.FC = () => {
  return (
    <div className="p-6 bg-gray-100 min-h-full">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Sales Today"
          value="$1,250"
          description="20% increase from yesterday"
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 12v-1m-4-3H9m2-2h3m-4 0c1.11 0 2.08.402 2.599 1M12 11c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2"></path></svg>}
          color="blue"
        />
        <StatCard
          title="New Customers"
          value="15"
          description="3 new this week"
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h-5m-5 0h10a2 2 0 002-2V6a2 2 0 00-2-2H7a2 2 0 00-2 2v12a2 2 0 002 2zm1-8V7h4v5m-4 0h4"></path></svg>}
          color="green"
        />
        <StatCard
          title="Low Stock Items"
          value="7"
          description="Action required"
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
          color="red"
        />
        <StatCard
          title="Pending Orders"
          value="3"
          description="Needs dispatch"
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>}
          color="yellow"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Sales Overview">
          <div className="h-64 flex items-center justify-center text-gray-500 bg-gray-50 border border-gray-200 rounded-md">
            Chart Placeholder (e.g., Bar Chart for daily sales)
          </div>
        </Card>
        <Card title="Recent Activities">
          <ul className="divide-y divide-gray-200">
            <li className="py-3 flex justify-between items-center">
              <span className="text-gray-700">New order #1001 placed by John Doe</span>
              <span className="text-sm text-gray-500">2 mins ago</span>
            </li>
            <li className="py-3 flex justify-between items-center">
              <span className="text-gray-700">Inventory updated for Milk (50 units)</span>
              <span className="text-sm text-gray-500">1 hour ago</span>
            </li>
            <li className="py-3 flex justify-between items-center">
              <span className="text-gray-700">Worker Jane Doe started shift</span>
              <span className="text-sm text-gray-500">3 hours ago</span>
            </li>
            <li className="py-3 flex justify-between items-center">
              <span className="text-gray-700">Product "Organic Apples" added</span>
              <span className="text-sm text-gray-500">Yesterday</span>
            </li>
          </ul>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;