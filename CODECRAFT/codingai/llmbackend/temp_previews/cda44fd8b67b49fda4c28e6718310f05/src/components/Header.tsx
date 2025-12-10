import React from 'react';
import { Link } from 'react-router-dom';
import Button from './Button';

interface HeaderProps {
  onLogout: () => void;
}

const Header: React.FC<HeaderProps> = ({ onLogout }) => {
  return (
    <header className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200 shadow-sm">
      <div className="flex items-center">
        <Link to="/dashboard" className="text-xl font-semibold text-indigo-600">
          Tuition Management
        </Link>
      </div>
      <div className="flex items-center space-x-4">
        <span className="text-gray-700">Welcome, Student!</span>
        <Button variant="secondary" size="sm" onClick={onLogout}>
          Logout
        </Button>
      </div>
    </header>
  );
};

export default Header;