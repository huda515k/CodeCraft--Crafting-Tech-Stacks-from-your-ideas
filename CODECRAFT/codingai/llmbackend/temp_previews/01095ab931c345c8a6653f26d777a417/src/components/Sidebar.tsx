import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navItems = [
    {
      label: 'Admin',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h-5v-9h5v9zM15 3H7a2 2 0 00-2 2v14a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2z"></path>
        </svg>
      ),
      subItems: [
        { name: 'Admin Dashboard', path: '/admin-dashboard' },
        { name: 'Manage Patients', path: '/admin-patients' },
      ],
    },
    {
      label: 'Doctor',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
      ),
      subItems: [
        { name: 'Doctor Dashboard', path: '/doctor-dashboard' },
        // { name: 'Appointments', path: '/doctor-appointments' },
      ],
    },
    {
      label: 'Patient',
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
        </svg>
      ),
      subItems: [
        { name: 'Patient Dashboard', path: '/patient-dashboard' },
        // { name: 'My History', path: '/patient-history' },
      ],
    },
  ];

  return (
    <>
      {/* Sidebar toggle for mobile */}
      <div className="absolute inset-y-0 left-0 z-40 sm:hidden">
        <button
          className="p-3 text-gray-500 focus:outline-none focus:bg-gray-100 focus:text-gray-600"
          onClick={() => setSidebarOpen(!sidebarOpen)}
        >
          <svg
            className="h-6 w-6"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            {sidebarOpen ? (
              <path d="M6 18L18 6M6 6l12 12"></path>
            ) : (
              <path d="M4 6h16M4 12h16M4 18h16"></path>
            )}
          </svg>
        </button>
      </div>

      {/* Backdrop for mobile sidebar */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-gray-900 bg-opacity-50 sm:hidden"
          onClick={() => setSidebarOpen(false)}
        ></div>
      )}

      {/* Sidebar */}
      <div
        className={`flex flex-col absolute z-40 left-0 top-0 lg:static lg:left-auto lg:top-auto lg:translate-x-0 transform h-screen overflow-y-scroll lg:overflow-y-auto no-scrollbar w-64 lg:w-20 lg:sidebar-expanded:!w-64 2xl:!w-64 shrink-0 bg-gray-800 p-4 transition-all duration-200 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-64'
        }`}
      >
        {/* Sidebar Header */}
        <div className="flex justify-between mb-10 pr-3 sm:px-2">
          {/* Close button for mobile */}
          <button
            className="lg:hidden text-gray-500 hover:text-gray-400"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-controls="sidebar"
            aria-expanded={sidebarOpen}
          >
            <span className="sr-only">Close sidebar</span>
            <svg
              className="w-6 h-6 fill-current"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path d="M10.7 18.7l1.4-1.4L7.8 13H20v-2H7.8l4.3-4.3-1.4-1.4L4 12z" />
            </svg>
          </button>
          {/* Logo */}
          <NavLink end to="/admin-dashboard" className="block text-white text-2xl font-bold">
            HMS
          </NavLink>
        </div>

        {/* Links */}
        <div className="space-y-6">
          {navItems.map((item, index) => (
            <div key={index}>
              <h3 className="text-xs uppercase text-gray-500 font-semibold pl-3 pb-2">
                <span
                  className="hidden lg:block lg:sidebar-expanded:hidden 2xl:hidden text-center w-6"
                  aria-hidden="true"
                >
                  •••
                </span>
                <span className="lg:hidden lg:sidebar-expanded:block 2xl:block">{item.label}</span>
              </h3>
              <ul className="mt-2">
                {item.subItems.map((subItem, subIndex) => (
                  <li className="mb-1 last:mb-0" key={subIndex}>
                    <NavLink
                      end
                      to={subItem.path}
                      className={({ isActive }) =>
                        `block text-gray-200 hover:text-white truncate transition duration-150 py-2 px-3 rounded-md ${
                          isActive ? 'bg-primary-600 text-white' : 'hover:bg-gray-700'
                        }`
                      }
                      onClick={() => setSidebarOpen(false)} // Close sidebar on nav for mobile
                    >
                      <div className="flex items-center">
                        {item.icon && <span className="mr-3">{item.icon}</span>}
                        <span className="text-sm font-medium lg:opacity-0 lg:sidebar-expanded:opacity-100 2xl:opacity-100 duration-200">
                          {subItem.name}
                        </span>
                      </div>
                    </NavLink>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </>
  );
};

export default Sidebar;