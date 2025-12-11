import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'primary' | 'secondary' | 'danger';
}

const Button = ({ children, onClick, type = 'primary' }: ButtonProps) => (
  <button
    className={`bg-${type}-500 hover:bg-${type}-700 text-white font-bold py-2 px-4 rounded`}
    onClick={onClick}
  >
    {children}
  </button>
);

export default Button;