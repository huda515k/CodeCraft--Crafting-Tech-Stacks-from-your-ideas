import React from 'react';
import Card from '../components/Card';
import StatCard from '../components/StatCard';

const RevenuePage: React.FC = () => {
  return (
    <div className="p-6 bg-gray-100 min-h-full">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Revenue Overview</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <StatCard
          title="Monthly Revenue"
          value="$55,000"
          description="Last 30 days"
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 12v-1m-4-3H9m2-2h3m-4 0c1.11 0 2.08.402 2.599 1M12 11c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2"></path></svg>}
          color="green"
        />
        <StatCard
          title="Profit Margin"
          value="25%"
          description="Average across products"
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 21h18"></path></svg>}
          color="blue"
        />
        <StatCard
          title="Average Order Value"
          value="$35.50"
          description="Higher than previous month"
          icon={<svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19V6a2 2 0 00-2-2H5a2 2 0 00-2 2v13m11 0V6a2 2 0 00-2-2h-2a2 2 0 00-2 2v13m7 0V6a2 2 0 00-2-2h-2a2 2 0 00-2 2v13"></path></svg>}
          color="yellow"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Revenue Trend (Last 6 Months)">
          <div className="h-64 flex items-center justify-center text-gray-500 bg-gray-50 border border-gray-200 rounded-md">
            Line Chart Placeholder (e.g., Monthly Revenue)
          </div>
        </Card>
        <Card title="Top Selling Categories">
          <ul className="divide-y divide-gray-200">
            <li className="py-3 flex justify-between items-center">
              <span className="text-gray-700">Produce</span>
              <span className="text-sm text-gray-500">$15,200</span>
            </li>
            <li className="py-3 flex justify-between items-center">
              <span className="text-gray-700">Dairy</span>
              <span className="text-sm text-gray-500">$12,800</span>
            </li>
            <li className="py-3 flex justify-between items-center">
              <span className="text-gray-700">Meat & Seafood</span>
              <span className="text-sm text-gray-500">$9,500</span>
            </li>
            <li className="py-3 flex justify-between items-center">
              <span className="text-gray-700">Bakery</span>
              <span className="text-sm text-gray-500">$7,100</span>
            </li>
          </ul>
        </Card>
      </div>
    </div>
  );
};

export default RevenuePage;