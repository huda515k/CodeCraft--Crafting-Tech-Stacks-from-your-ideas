import React from 'react';
import Card from './Card';

interface DashboardCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  color?: string; // Tailwind color classes like 'bg-blue-100 text-blue-800'
}

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  value,
  icon,
  color = 'bg-blue-100 text-blue-800',
}) => {
  return (
    <Card className="flex items-center p-4">
      <div className={`flex-shrink-0 p-3 rounded-full ${color.split(' ')[0]} ${color.split(' ')[1]}`}>
        {icon}
      </div>
      <div className="ml-4">
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        <p className="text-2xl font-semibold text-gray-900">{value}</p>
      </div>
    </Card>
  );
};

export default DashboardCard;