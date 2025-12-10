import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm p-4 flex items-center justify-between z-10">
      <h1 className="text-2xl font-semibold text-gray-800">Mini CRM</h1>
    </header>
  );
};

export default Header;