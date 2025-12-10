import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  title?: string;
}

const Card: React.FC<CardProps> = ({ children, title, className = '', ...props }) => {
  return (
    <div className={`bg-white shadow rounded-lg p-6 ${className}`} {...props}>
      {title && <h2 className="text-xl font-semibold text-gray-800 mb-4">{title}</h2>}
      {children}
    </div>
  );
};

export default Card;