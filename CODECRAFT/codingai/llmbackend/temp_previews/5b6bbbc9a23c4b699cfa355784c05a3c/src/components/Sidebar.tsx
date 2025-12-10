import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: '📊' },
    { name: 'Attendance', path: '/attendance', icon: '📝' },
    { name: 'Students', path: '/students', icon: '🧑‍🎓' },
    { name: 'Faculty', path: '/faculty', icon: '👨‍🏫' },
    { name: 'Courses', path: '/courses', icon: '📚' },
    { name: 'Settings', path: '/settings', icon: '⚙️' },
  ];

  return (
    <div className="w-64 bg-gray-800 text-white flex flex-col h-full fixed md:relative z-20">
      <div className="p-4 text-2xl font-bold border-b border-gray-700">
        School Admin
      </div>
      <nav className="flex-1 px-2 py-4 space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center px-4 py-2 rounded-md text-gray-300 hover:bg-gray-700 hover:text-white transition-colors duration-200 ${
                isActive ? 'bg-gray-700 text-white' : ''
              }`
            }
          >
            <span className="mr-3 text-lg">{item.icon}</span>
            {item.name}
          </NavLink>
        ))}
      </nav>
      <div className="p-4 border-t border-gray-700">
        <NavLink
          to="/login"
          className="flex items-center px-4 py-2 rounded-md text-gray-300 hover:bg-gray-700 hover:text-white transition-colors duration-200"
        >
          <span className="mr-3 text-lg">🚪</span> Logout
        </NavLink>
      </div>
    </div>
  );
};

export default Sidebar;