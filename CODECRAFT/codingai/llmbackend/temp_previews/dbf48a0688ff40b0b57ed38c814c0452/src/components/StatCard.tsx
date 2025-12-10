import React from 'react';
import Card from './Card';

interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode;
  color?: 'blue' | 'green' | 'red' | 'yellow';
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  description,
  icon,
  color = 'blue',
}) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-100',
    green: 'text-green-600 bg-green-100',
    red: 'text-red-600 bg-red-100',
    yellow: 'text-yellow-600 bg-yellow-100',
  };

  return (
    <Card className="flex items-start justify-between">
      <div>
        <h3 className="text-sm font-medium text-gray-500">{title}</h3>
        <p className="mt-1 text-3xl font-bold text-gray-900">{value}</p>
        {description && <p className="mt-2 text-sm text-gray-500">{description}</p>}
      </div>
      {icon && (
        <div className={`p-3 rounded-full ${colorClasses[color]}`}>
          {icon}
        </div>
      )}
    </Card>
  );
};

export default StatCard;