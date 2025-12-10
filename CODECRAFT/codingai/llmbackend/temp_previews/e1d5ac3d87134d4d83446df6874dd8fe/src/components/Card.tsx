import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
}

const Card: React.FC<CardProps> = ({ children, title, className = '', ...props }) => {
  return (
    <div className={`bg-white shadow rounded-lg p-6 ${className}`} {...props}>
      {title && <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>}
      {children}
    </div>
  );
};

export default Card;