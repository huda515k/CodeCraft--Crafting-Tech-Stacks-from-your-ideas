import React from 'react';
import { NavLink } from 'react-router-dom';

interface SidebarLinkProps {
  to: string;
  children: React.ReactNode;
}

const SidebarLink: React.FC<SidebarLinkProps> = ({ to, children }) => {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200 ${
          isActive
            ? 'bg-accent text-white shadow-md'
            : 'text-gray-700 hover:bg-gray-100'
        }`
      }
    >
      {children}
    </NavLink>
  );
};

const Sidebar: React.FC = () => {
  return (
    <aside className="w-64 bg-white shadow-lg flex-shrink-0 p-4">
      <div className="mb-8 px-4 text-2xl font-bold text-primary">
        CRM Dashboard
      </div>
      <nav>
        <ul className="space-y-2">
          <li>
            <SidebarLink to="/">
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
              </svg>
              Dashboard
            </SidebarLink>
          </li>
          <li>
            <SidebarLink to="/players">
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h2a2 2 0 002-2V7a2 2 0 00-2-2h-2V3a1 1 0 00-1-1H8a1 1 0 00-1 1v2H5a2 2 0 00-2 2v11a2 2 0 002 2h2m-4-6h16a2 2 0 002-2V7a2 2 0 00-2-2h-2m-8-2v2m-6 4h16"></path>
              </svg>
              Players
            </SidebarLink>
          </li>
          <li>
            <SidebarLink to="/teams">
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h2a2 2 0 002-2V7a2 2 0 00-2-2h-2V3a1 1 0 00-1-1H8a1 1 0 00-1 1v2H5a2 2 0 00-2 2v11a2 2 0 002 2h2m-4-6h16a2 2 0 002-2V7a2 2 0 00-2-2h-2m-8-2v2m-6 4h16"></path>
              </svg>
              Teams
            </SidebarLink>
          </li>
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;