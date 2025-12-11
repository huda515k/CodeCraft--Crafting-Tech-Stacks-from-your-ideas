import React from 'react';
import { Link } from 'react-router-dom';

const Patients: React.FC = () => {
  return (
    <div className="flex justify-center items-center h-screen">
      <div className="bg-white p-8 shadow-md rounded-lg w-96 mx-auto">
        <h1 className="text-2xl font-bold mb-4">Patients</h1>
        <Link to="/doctors" className="hover:text-blue-500">
          Add Patient
        </Link>
      </div>
    </div>
  );
};

export default Patients;