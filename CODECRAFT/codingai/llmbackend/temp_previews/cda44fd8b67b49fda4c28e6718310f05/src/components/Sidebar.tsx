import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const navItems = [
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Attendance', path: '/attendance' },
  ];

  return (
    <aside className="w-64 bg-indigo-800 text-white flex flex-col p-4 shadow-lg">
      <div className="text-2xl font-bold mb-8 text-center border-b pb-4 border-indigo-700">
        TMS Admin
      </div>
      <nav className="flex-1">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.name}>
              <NavLink
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center px-4 py-2 rounded-md transition duration-200 ease-in-out ${
                    isActive
                      ? 'bg-indigo-700 text-white shadow'
                      : 'hover:bg-indigo-700 hover:text-white'
                  }`
                }
              >
                {item.name}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
      <div className="mt-auto pt-4 border-t border-indigo-700 text-sm text-indigo-200">
        &copy; 2023 Tuition Management
      </div>
    </aside>
  );
};

export default Sidebar;