import React from 'react';
import { Link } from 'react-router-dom';

const Dashboard: React.FC = () => {
  return (
    <div className="flex justify-center items-center h-screen">
      <div className="bg-white p-8 shadow-md rounded-lg w-96 mx-auto">
        <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
        <ul className="list-disc list-inside">
          <li><Link to="/doctors" className="hover:text-blue-500">Doctors</Link></li>
          <li><Link to="/appointments" className="hover:text-blue-500">Appointments</Link></li>
          <li><Link to="/patients" className="hover:text-blue-500">Patients</Link></li>
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;