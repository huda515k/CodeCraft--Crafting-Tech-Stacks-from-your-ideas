import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  children?: React.ReactNode;
}

const Input: React.FC<InputProps> = ({ children, ...props }) => {
  return (
    <input
      className="border border-gray-300 rounded px-4 py-2 focus:outline-none focus:border-blue-500"
      {...props}
    >
      {children}
    </input>
  );
};

export default Input;