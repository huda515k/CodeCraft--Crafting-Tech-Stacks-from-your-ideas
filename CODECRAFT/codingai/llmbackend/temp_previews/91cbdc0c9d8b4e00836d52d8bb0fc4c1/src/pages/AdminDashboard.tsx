import React from 'react';
import DashboardCard from '../components/DashboardCard';

const AdminDashboard: React.FC = () => {
  return (
    <div className="container mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Admin Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <DashboardCard
          title="Total Patients"
          value="1,200"
          icon={<UserGroupIcon className="h-6 w-6" />}
          color="bg-green-100 text-green-800"
        />
        <DashboardCard
          title="Total Doctors"
          value="150"
          icon={<MedicalBagIcon className="h-6 w-6" />}
          color="bg-purple-100 text-purple-800"
        />
        <DashboardCard
          title="Appointments Today"
          value="85"
          icon={<CalendarIcon className="h-6 w-6" />}
          color="bg-yellow-100 text-yellow-800"
        />
        <DashboardCard
          title="Pending Requests"
          value="12"
          icon={<BellIcon className="h-6 w-6" />}
          color="bg-red-100 text-red-800"
        />
      </div>
      <div className="mt-8 p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
        <div className="flex flex-wrap gap-4">
          <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">Add New User</button>
          <button className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700">Manage Departments</button>
          <button className="px-4 py-2 bg-teal-600 text-white rounded-md hover:bg-teal-700">View Reports</button>
        </div>
      </div>
    </div>
  );
};

// Simple SVG Icons (replace with actual icon library if preferred)
const UserGroupIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a4.5 4.5 0 0 0 2.343-2.339A3.375 3.375 0 0 0 18 12.671V12a3.75 3.75 0 0 0-3.75-3.75H12A3.75 3.75 0 0 0 8.25 12v.671L12 17.25l-.424.424A4.5 4.5 0 0 0 18 18.72ZM9 7.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0ZM12 18.75h.008v.008H12v-.008ZM12 12h.008v.008H12V12Z" />
  </svg>
);
const MedicalBagIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v6m3-3H9m12 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
  </svg>
);
const CalendarIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0v-7.5m18 7.5v-7.5" />
  </svg>
);
const BellIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.108 5.455 1.31m5.714 0a24.248 24.248 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
  </svg>
);

export default AdminDashboard;