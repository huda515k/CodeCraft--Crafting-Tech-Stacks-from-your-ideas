import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  title?: string;
}

const Card: React.FC<CardProps> = ({ children, title, className, ...props }) => {
  return (
    <div className={`bg-white shadow rounded-lg p-4 md:p-6 ${className || ''}`} {...props}>
      {title && <h3 className="text-lg font-semibold text-gray-800 mb-4">{title}</h3>}
      {children}
    </div>
  );
};

export default Card;