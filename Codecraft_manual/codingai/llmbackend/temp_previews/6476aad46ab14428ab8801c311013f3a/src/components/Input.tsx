import React from 'react';

interface InputProps {
  label?: string;
  name: string;
  type?: 'text' | 'email' | 'password';
  value?: string;
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const Input: React.FC<InputProps> = ({ label, name, type = 'text', value, onChange }) => {
  return (
    <div className="mb-4">
      {label && <label htmlFor={name} className="block text-gray-700 font-bold mb-2">{label}</label>}
      <input
        id={name}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
      />
    </div>
  );
};

export default Input;