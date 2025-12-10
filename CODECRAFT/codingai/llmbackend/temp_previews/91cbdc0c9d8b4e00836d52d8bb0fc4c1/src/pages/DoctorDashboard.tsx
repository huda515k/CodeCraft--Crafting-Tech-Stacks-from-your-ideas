import React from 'react';
import DashboardCard from '../components/DashboardCard';

const DoctorDashboard: React.FC = () => {
  return (
    <div className="container mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Doctor Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <DashboardCard
          title="Patients Today"
          value="15"
          icon={<UserIcon className="h-6 w-6" />}
          color="bg-blue-100 text-blue-800"
        />
        <DashboardCard
          title="Upcoming Appointments"
          value="7"
          icon={<ClockIcon className="h-6 w-6" />}
          color="bg-indigo-100 text-indigo-800"
        />
        <DashboardCard
          title="New Prescriptions"
          value="5"
          icon={<PillIcon className="h-6 w-6" />}
          color="bg-teal-100 text-teal-800"
        />
        <DashboardCard
          title="Pending Lab Results"
          value="3"
          icon={<FlaskIcon className="h-6 w-6" />}
          color="bg-orange-100 text-orange-800"
        />
      </div>
      <div className="mt-8 p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Patient Queue</h2>
        <ul className="divide-y divide-gray-200">
          <li className="py-3 flex justify-between items-center">
            <span className="text-gray-900 font-medium">John Doe</span>
            <span className="text-sm text-gray-500">10:00 AM</span>
          </li>
          <li className="py-3 flex justify-between items-center">
            <span className="text-gray-900 font-medium">Jane Smith</span>
            <span className="text-sm text-gray-500">10:30 AM</span>
          </li>
          <li className="py-3 flex justify-between items-center">
            <span className="text-gray-900 font-medium">Peter Jones</span>
            <span className="text-sm text-gray-500">11:00 AM</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

// Simple SVG Icons
const UserIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372c.987 0 1.954-.108 2.91-.301M10.5 18.259a8.775 8.775 0 0 0-1.993-.301C7.89 17.958 6.924 18.066 6 18.259m-.5-11.231a3 3 0 1 1 6 0 3 3 0 0 1-6 0Z" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M12.75 2.25a7.5 7.5 0 0 0-7.5 7.5c0 3.791 2.27 6.945 5.567 8.393M17.25 2.25a7.5 7.5 0 0 1 7.5 7.5c0 3.791-2.27 6.945-5.567 8.393M12.75 12.75a.75.75 0 0 1 .75-.75h.004a.75.75 0 0 1 .75.75v.004a.75.75 0 0 1-.75.75h-.004a.75.75 0 0 1-.75-.75V12.75Z" />
  </svg>
);
const ClockIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
  </svg>
);
const PillIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m-4.5 0H12.25A2.25 2.25 0 0 0 14.5 15.75V8.25A2.25 2.25 0 0 0 12.25 6H8.25A2.25 2.25 0 0 0 6 8.25v7.5A2.25 2.25 0 0 0 8.25 18Z" />
  </svg>
);
const FlaskIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 7.5L12 12m0 0l-7.5-4.5M12 12V21m0-9.75v-3C12 5.096 10.904 4 9.5 4S7 5.096 7 6.5V9M12 12v-3.25" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75L12 17.25l7.5-4.5M4.5 12.75V15M19.5 12.75V15" />
  </svg>
);


export default DoctorDashboard;