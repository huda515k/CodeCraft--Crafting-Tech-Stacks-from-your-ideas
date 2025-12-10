import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const navItems = [
    { name: 'Dashboard', path: '/' },
    { name: 'Workers', path: '/workers' },
    { name: 'Inventory', path: '/inventory' },
    { name: 'Revenue', path: '/revenue' },
  ];

  return (
    <aside className="w-64 bg-gray-800 text-white min-h-screen p-4 sticky top-0 left-0 hidden md:block">
      <div className="mb-8 text-center">
        <h2 className="text-3xl font-extrabold text-blue-400">CRM</h2>
      </div>
      <nav>
        <ul>
          {navItems.map((item) => (
            <li key={item.name} className="mb-2">
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `block py-2 px-4 rounded-md transition duration-200 ease-in-out ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'hover:bg-gray-700 text-gray-300'
                  }`
                }
              >
                {item.name}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;