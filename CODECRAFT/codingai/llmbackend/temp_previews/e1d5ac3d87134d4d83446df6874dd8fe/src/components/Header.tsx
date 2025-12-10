import React from 'react';
import { Link } from 'react-router-dom';

interface HeaderProps {
  onMenuToggle?: () => void;
}

const Header: React.FC<HeaderProps> = ({ onMenuToggle }) => {
  return (
    <header className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200">
      <div className="flex items-center">
        <button
          onClick={onMenuToggle}
          className="text-gray-500 focus:outline-none lg:hidden"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M4 6h16M4 12h16M4 18h16"
            ></path>
          </svg>
        </button>
        <h1 className="text-2xl font-semibold text-gray-800 ml-4 hidden md:block">CRM Dashboard</h1>
      </div>
      <div className="flex items-center">
        {/* User Dropdown / Notifications could go here */}
        <Link to="#" className="text-gray-500 mx-4 focus:outline-none">
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
            ></path>
          </svg>
        </Link>
        <div className="relative">
          <button className="flex items-center focus:outline-none">
            <img
              className="w-8 h-8 rounded-full object-cover"
              src="https://via.placeholder.com/150/4F46E5/FFFFFF?text=JD"
              alt="User avatar"
            />
            <span className="mx-2 text-gray-700 hidden md:block">John Doe</span>
          </button>
          {/* Dropdown content can be added here */}
        </div>
      </div>
    </header>
  );
};

export default Header;