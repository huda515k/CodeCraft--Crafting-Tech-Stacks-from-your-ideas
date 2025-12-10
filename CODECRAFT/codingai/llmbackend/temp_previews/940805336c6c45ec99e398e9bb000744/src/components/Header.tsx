import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm p-4 flex items-center justify-between sticky top-0 z-10">
      <h1 className="text-xl md:text-2xl font-semibold text-gray-800">Cricket CRM Dashboard</h1>
      {/* Could add user profile, notifications here */}
      <div className="flex items-center space-x-4">
        <span className="text-gray-600 hidden md:block">Welcome, Captain!</span>
        <div className="w-10 h-10 rounded-full bg-blue-500 text-white flex items-center justify-center font-bold">C</div>
      </div>
    </header>
  );
};

export default Header;