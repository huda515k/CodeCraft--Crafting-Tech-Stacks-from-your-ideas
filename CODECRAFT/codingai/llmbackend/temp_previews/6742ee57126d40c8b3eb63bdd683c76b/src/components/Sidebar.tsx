import React from 'react';
import Button from './Button';

interface SidebarProps {
  currentPage: 'Dashboard' | 'Customers' | 'Leads';
  onNavigate: (page: 'Dashboard' | 'Customers' | 'Leads') => void;
}

const Sidebar: React.FC<SidebarProps> = ({ currentPage, onNavigate }) => {
  const navItems = [
    { name: 'Dashboard', page: 'Dashboard' },
    { name: 'Customers', page: 'Customers' },
    { name: 'Leads', page: 'Leads' },
  ];

  return (
    <aside className="w-64 bg-gray-800 text-white flex flex-col p-4 shadow-lg">
      <nav className="flex-1">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.page}>
              <Button
                variant={currentPage === item.page ? 'primary' : 'ghost'}
                onClick={() => onNavigate(item.page as 'Dashboard' | 'Customers' | 'Leads')}
                className="w-full text-left justify-start"
              >
                {item.name}
              </Button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;