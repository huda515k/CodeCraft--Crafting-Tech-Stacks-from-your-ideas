import React from 'react';
import Card from './Card';

interface DashboardCardProps {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  colorClass?: string;
}

const DashboardCard: React.FC<DashboardCardProps> = ({ title, value, icon, colorClass = 'text-accent' }) => {
  return (
    <Card className="flex items-center space-x-4">
      <div className={`p-3 rounded-full bg-opacity-20 ${colorClass}`}>
        {icon}
      </div>
      <div>
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
    </Card>
  );
};

export default DashboardCard;