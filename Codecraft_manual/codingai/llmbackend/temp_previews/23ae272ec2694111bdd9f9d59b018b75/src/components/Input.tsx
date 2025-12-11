import React from 'react';

interface InputProps {
  value: string;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
}

const Input = ({ value, onChange, placeholder }: InputProps) => (
  <input
    className="border border-gray-300 rounded px-4 py-2 focus:outline-none"
    type="text"
    value={value}
    onChange={onChange}
    placeholder={placeholder}
  />
);

export default Input;