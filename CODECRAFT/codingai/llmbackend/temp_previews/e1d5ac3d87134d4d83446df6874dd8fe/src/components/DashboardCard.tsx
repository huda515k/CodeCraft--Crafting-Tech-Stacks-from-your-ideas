import React from 'react';
import Card from './Card';

interface DashboardCardProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  description?: string;
  colorClass?: string;
}

const DashboardCard: React.FC<DashboardCardProps> = ({
  title,
  value,
  icon,
  description,
  colorClass = 'text-indigo-600',
}) => {
  return (
    <Card className="flex items-start justify-between">
      <div>
        <h4 className="text-sm font-medium text-gray-500">{title}</h4>
        <p className={`mt-1 text-3xl font-semibold ${colorClass}`}>{value}</p>
        {description && <p className="mt-2 text-sm text-gray-500">{description}</p>}
      </div>
      {icon && <div className={`text-3xl ${colorClass}`}>{icon}</div>}
    </Card>
  );
};

export default DashboardCard;