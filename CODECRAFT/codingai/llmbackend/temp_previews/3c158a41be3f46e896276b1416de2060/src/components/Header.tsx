import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="flex-shrink-0 bg-white shadow-sm h-16 flex items-center px-6">
      <div className="flex-1 text-xl font-semibold text-gray-800">
        Cricket CRM
      </div>
      {/* You can add user profile, notifications etc. here */}
      <div className="flex items-center space-x-4">
        <span className="text-sm text-gray-600">Admin User</span>
        {/* Placeholder for user avatar */}
        <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center text-gray-500">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd"></path>
          </svg>
        </div>
      </div>
    </header>
  );
};

export default Header;