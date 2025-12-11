import React from 'react';

interface InputProps {
  type: string;
  value?: string;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  className?: string;
}

const Input: React.FC<InputProps> = ({ type, value, onChange, placeholder, className }) => (
  <input
    type={type}
    value={value}
    onChange={onChange}
    placeholder={placeholder}
    className={`border border-gray-300 rounded px-4 py-2 focus:border-blue-500 ${className}`}
  />
);

export default Input;