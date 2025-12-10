import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const navLinks = [
    { name: 'Admin Dashboard', path: '/admin-dashboard' },
    { name: 'Doctor Dashboard', path: '/doctor-dashboard' },
    { name: 'Patient Dashboard', path: '/patient-dashboard' },
    { name: 'Patient Management', path: '/patient-management' },
    // Add more links as needed
  ];

  return (
    <aside className="w-64 bg-gray-800 text-white flex-shrink-0 min-h-screen">
      <div className="p-6 text-center border-b border-gray-700">
        <h1 className="text-xl font-bold">HMS Admin</h1>
      </div>
      <nav className="mt-6">
        <ul>
          {navLinks.map((link) => (
            <li key={link.path}>
              <NavLink
                to={link.path}
                className={({ isActive }) =>
                  `flex items-center p-4 text-sm font-medium hover:bg-gray-700 transition-colors ${
                    isActive ? 'bg-blue-600 text-white' : 'text-gray-300'
                  }`
                }
              >
                {link.name}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;