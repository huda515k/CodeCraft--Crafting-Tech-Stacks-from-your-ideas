import React from 'react';
import DashboardCard from '../components/DashboardCard';

const PatientDashboard: React.FC = () => {
  return (
    <div className="container mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Patient Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <DashboardCard
          title="Next Appointment"
          value="Mon, Apr 22"
          icon={<CalendarCheckIcon className="h-6 w-6" />}
          color="bg-green-100 text-green-800"
        />
        <DashboardCard
          title="Past Appointments"
          value="12"
          icon={<HistoryIcon className="h-6 w-6" />}
          color="bg-gray-100 text-gray-800"
        />
        <DashboardCard
          title="New Messages"
          value="2"
          icon={<ChatIcon className="h-6 w-6" />}
          color="bg-blue-100 text-blue-800"
        />
        <DashboardCard
          title="Prescriptions Due"
          value="1"
          icon={<ClipboardIcon className="h-6 w-6" />}
          color="bg-yellow-100 text-yellow-800"
        />
      </div>
      <div className="mt-8 p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">My Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-gray-500 text-sm">Name:</p>
            <p className="text-gray-900 font-medium">Sarah Johnson</p>
          </div>
          <div>
            <p className="text-gray-500 text-sm">DOB:</p>
            <p className="text-gray-900 font-medium">1990-05-15</p>
          </div>
          <div>
            <p className="text-gray-500 text-sm">Contact:</p>
            <p className="text-gray-900 font-medium">sarah.j@example.com</p>
          </div>
          <div>
            <p className="text-gray-500 text-sm">Primary Doctor:</p>
            <p className="text-gray-900 font-medium">Dr. Emily White</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Simple SVG Icons
const CalendarCheckIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
  </svg>
);
const HistoryIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
  </svg>
);
const ChatIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 12a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H7.5m2.25 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H9m2.25 0a.375.375 0 1 1-.75 0 .375.375 0 0 1 .75 0Zm0 0H10.5M4.875 18.75h-.008v.008H4.875v-.008ZM6 18.75h-.008v.008H6v-.008ZM7.125 18.75h-.008v.008H7.125v-.008ZM.75 2.25c0-.414.336-.75.75-.75h1.5a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1-.75-.75v-1.5ZM3 15.75h-.008v.008H3v-.008ZM4.125 15.75h-.008v.008H4.125v-.008ZM5.25 15.75h-.008v.008H5.25v-.008ZM6.375 15.75h-.008v.008H6.375v-.008ZM12 4.5a.75.75 0 0 1 .75-.75h1.5a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1-.75-.75v-1.5ZM16.5 4.5a.75.75 0 0 1 .75-.75h1.5a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1-.75-.75v-1.5ZM21 4.5a.75.75 0 0 1 .75-.75h1.5a.75.75 0 0 1 .75.75v1.5a.75.75 0 0 1-.75.75h-1.5a.75.75 0 0 1-.75-.75v-1.5Z" />
  </svg>
);
const ClipboardIcon = (props: React.SVGProps<SVGSVGElement>) => (
  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" {...props}>
    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 7.5L12 12m0 0l-7.5-4.5M12 12V21m0-9.75v-3C12 5.096 10.904 4 9.5 4S7 5.096 7 6.5V9M12 12v-3.25" />
    <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75L12 17.25l7.5-4.5M4.5 12.75V15M19.5 12.75V15" />
  </svg>
);

export default PatientDashboard;