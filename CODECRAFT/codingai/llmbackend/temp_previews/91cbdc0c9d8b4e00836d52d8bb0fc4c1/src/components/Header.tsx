import React from 'react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm h-16 flex items-center px-6 border-b border-gray-200 sticky top-0 z-10">
      <div className="flex items-center justify-between w-full">
        <Link to="/admin-dashboard" className="text-2xl font-bold text-blue-600">
          HMS
        </Link>
        <nav className="flex items-center space-x-4">
          <span className="text-gray-700 font-medium">Welcome, Admin!</span>
          <button className="text-gray-500 hover:text-blue-600 transition-colors">
            Logout
          </button>
        </nav>
      </div>
    </header>
  );
};

export default Header;