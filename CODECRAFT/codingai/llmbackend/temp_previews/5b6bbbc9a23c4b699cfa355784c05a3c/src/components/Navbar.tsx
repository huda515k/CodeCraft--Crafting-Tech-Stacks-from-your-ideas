import React from 'react';

const Navbar: React.FC = () => {
  return (
    <header className="bg-white shadow-sm h-16 flex items-center justify-between px-6 z-10">
      <div className="text-xl font-semibold text-gray-800">
        Welcome, Admin!
      </div>
      <div className="flex items-center space-x-4">
        <button className="text-gray-600 hover:text-gray-800 focus:outline-none">
          🔔
        </button>
        <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white font-medium">
          A
        </div>
      </div>
    </header>
  );
};

export default Navbar;