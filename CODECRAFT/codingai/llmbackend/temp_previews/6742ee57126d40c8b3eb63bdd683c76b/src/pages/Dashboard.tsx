import React from 'react';
import StatCard from '../components/StatCard';
import { dashboardStats } from '../utils/mockData';

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-800">Dashboard Overview</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dashboardStats.map((stat, index) => (
          <StatCard
            key={index}
            title={stat.title}
            value={stat.value}
            description={stat.description}
          />
        ))}
      </div>
    </div>
  );
};

export default Dashboard;