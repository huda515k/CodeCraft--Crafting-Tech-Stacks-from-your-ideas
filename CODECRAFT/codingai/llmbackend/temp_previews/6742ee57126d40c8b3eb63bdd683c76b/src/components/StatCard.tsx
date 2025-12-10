import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  description: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, description }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 flex flex-col justify-between transform transition-transform hover:scale-105 duration-200">
      <h3 className="text-sm font-medium text-gray-500">{title}</h3>
      <p className="mt-1 text-4xl font-bold text-gray-900">{value}</p>
      <p className="mt-3 text-sm text-gray-500">{description}</p>
    </div>
  );
};

export default StatCard;