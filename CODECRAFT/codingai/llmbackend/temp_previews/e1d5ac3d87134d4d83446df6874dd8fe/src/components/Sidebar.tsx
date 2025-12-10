import React from 'react';
import { NavLink } from 'react-router-dom';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const navItems = [
    { name: 'Dashboard', icon: '📊', path: '/' },
    { name: 'Customers', icon: '👥', path: '/customers' },
    { name: 'Orders', icon: '📝', path: '/orders' },
    { name: 'Products', icon: '📦', path: '/products' },
    { name: 'Reports', icon: '📈', path: '/reports' },
    { name: 'Settings', icon: '⚙️', path: '/settings' },
  ];

  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-20 bg-black opacity-50 lg:hidden"
        ></div>
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-30 w-64 overflow-y-auto bg-gray-800 transition transform ease-in-out duration-300
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 lg:static lg:inset-auto`}
      >
        <div className="flex items-center justify-center h-16 bg-indigo-700 text-white text-2xl font-semibold">
          CRM App
        </div>
        <nav className="mt-8">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              onClick={onClose}
              className={({ isActive }) =>
                `flex items-center px-6 py-2 mt-4 text-gray-300 hover:bg-gray-700 hover:bg-opacity-25 hover:text-gray-100 ${
                  isActive ? 'bg-gray-700 bg-opacity-25 text-white border-l-4 border-indigo-500' : ''
                }`
              }
            >
              <span className="text-xl mr-3">{item.icon}</span>
              <span>{item.name}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
  );
};

export default Sidebar;