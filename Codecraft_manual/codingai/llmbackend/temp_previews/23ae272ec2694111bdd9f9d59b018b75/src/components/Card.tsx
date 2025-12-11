import React from 'react';

interface CardProps {
  title: string;
  children: React.ReactNode;
}

const Card = ({ title, children }: CardProps) => (
  <div className="bg-white shadow-md rounded-lg p-4">
    <h2 className="text-xl font-bold mb-2">{title}</h2>
    {children}
  </div>
);

export default Card;