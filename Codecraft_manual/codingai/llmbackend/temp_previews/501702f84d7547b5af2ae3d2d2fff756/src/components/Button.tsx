import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({ children, ...props }) => {
  return (
    <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600" {...props}>
      {children}
    </button>
  );
};

export default Button;