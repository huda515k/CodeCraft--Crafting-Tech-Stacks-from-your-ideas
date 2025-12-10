import React from 'react';

interface CardProps {
  children: React.ReactNode;
  title?: string;
  className?: string;
}

const Card: React.FC<CardProps> = ({ children, title, className = '' }) => {
  return (
    <div className={`bg-white shadow-md rounded-lg p-6 ${className}`}>
      {title && <h2 className="text-xl font-semibold text-gray-800 mb-4">{title}</h2>}
      {children}
    </div>
  );
};

export default Card;