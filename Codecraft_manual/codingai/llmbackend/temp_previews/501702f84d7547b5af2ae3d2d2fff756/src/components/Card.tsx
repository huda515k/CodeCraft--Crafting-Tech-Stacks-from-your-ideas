import React from 'react';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  children?: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ title, children, ...props }) => {
  return (
    <div className="bg-white p-4 rounded shadow-lg" {...props}>
      {title && <h2 className="text-lg font-bold mb-4">{title}</h2>}
      {children}
    </div>
  );
};

export default Card;