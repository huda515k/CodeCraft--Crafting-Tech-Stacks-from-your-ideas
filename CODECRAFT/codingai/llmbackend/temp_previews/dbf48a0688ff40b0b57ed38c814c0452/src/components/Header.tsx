import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm py-4 px-6 md:px-8 flex items-center justify-between z-10">
      <div className="flex items-center">
        <h1 className="text-2xl font-bold text-gray-800">Grocery CRM</h1>
      </div>
      <div className="flex items-center">
        {/* User profile or notifications can go here */}
        <span className="text-gray-700 text-sm hidden sm:block">Welcome, Admin!</span>
        {/* Example avatar placeholder */}
        <div className="ml-4 w-9 h-9 bg-gray-200 rounded-full flex items-center justify-center text-gray-600 font-semibold">A</div>
      </div>
    </header>
  );
};

export default Header;