import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="sticky top-0 bg-white border-b border-gray-200 z-30">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 -mb-px">
          {/* Header: Left side */}
          <div className="flex">
            {/* Hamburger button (visible on mobile, handled by App.tsx/Sidebar.tsx for now) */}
            <button
              className="text-gray-500 hover:text-gray-600 lg:hidden"
              aria-controls="sidebar"
              aria-expanded="false" // This state is actually managed in Sidebar
            >
              <span className="sr-only">Open sidebar</span>
              <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <rect x="4" y="5" width="16" height="2" />
                <rect x="4" y="11" width="16" height="2" />
                <rect x="4" y="17" width="16" height="2" />
              </svg>
            </button>
          </div>

          {/* Header: Right side */}
          <div className="flex items-center">
            {/* User button */}
            <div className="relative inline-flex">
              <button
                className="inline-flex justify-center items-center group"
                aria-haspopup="true"
                // Assuming a user menu would be implemented here
              >
                <img
                  className="w-8 h-8 rounded-full"
                  src="https://via.placeholder.com/32"
                  width="32"
                  height="32"
                  alt="User"
                />
                <div className="flex items-center truncate">
                  <span className="truncate ml-2 text-sm font-medium group-hover:text-gray-800">
                    Admin User
                  </span>
                  <svg
                    className="w-3 h-3 shrink-0 ml-1 fill-current text-gray-400"
                    viewBox="0 0 12 12"
                  >
                    <path d="M5.9 11.4L.5 6l1.4-1.4 4 4 4-4 1.4 1.4z" />
                  </svg>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;