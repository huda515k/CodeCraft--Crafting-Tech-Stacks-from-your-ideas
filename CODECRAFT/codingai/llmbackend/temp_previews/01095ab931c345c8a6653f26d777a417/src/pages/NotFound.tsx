import React from 'react';
import { Link } from 'react-router-dom';
import Button from '../components/Button';

const NotFound: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-theme(spacing.16))] text-center px-4">
      <h1 className="text-9xl font-extrabold text-gray-800 mb-4">404</h1>
      <p className="text-2xl md:text-3xl font-medium text-gray-600 mb-8">Page Not Found</p>
      <p className="text-gray-500 mb-8 max-w-md">
        Oops! The page you are looking for might have been removed, had its name changed, or is temporarily unavailable.
      </p>
      <Link to="/admin-dashboard">
        <Button variant="primary" size="lg">Go to Dashboard</Button>
      </Link>
    </div>
  );
};

export default NotFound;