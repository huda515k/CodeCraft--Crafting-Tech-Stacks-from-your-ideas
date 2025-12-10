import React from 'react';
import Card from '../components/Card';

const DashboardAdmin: React.FC = () => {
  const stats = [
    { title: 'Total Patients', value: '1,250', icon: '👤' },
    { title: 'Total Doctors', value: '120', icon: '🩺' },
    { title: 'Total Appointments', value: '3,400', icon: '🗓️' },
    { title: 'New Admissions Today', value: '15', icon: '🏥' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {stats.map((stat, index) => (
        <Card key={index} className="flex items-center p-5">
          <div className="flex-shrink-0 mr-4 text-3xl">{stat.icon}</div>
          <div>
            <h3 className="text-gray-500 text-sm font-medium uppercase leading-tight">{stat.title}</h3>
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
          </div>
        </Card>
      ))}

      <Card title="Recent Activities" className="lg:col-span-2">
        <ul className="divide-y divide-gray-200">
          <li className="py-3 flex justify-between items-center">
            <span>Dr. Smith scheduled a surgery for Patient A.</span>
            <span className="text-sm text-gray-500">2 hours ago</span>
          </li>
          <li className="py-3 flex justify-between items-center">
            <span>New patient admitted: John Doe.</span>
            <span className="text-sm text-gray-500">4 hours ago</span>
          </li>
          <li className="py-3 flex justify-between items-center">
            <span>Inventory alert: bandages low.</span>
            <span className="text-sm text-gray-500">yesterday</span>
          </li>
        </ul>
      </Card>

      <Card title="Upcoming Appointments" className="lg:col-span-2">
        <ul className="divide-y divide-gray-200">
          <li className="py-3 flex justify-between items-center">
            <div>
              <p className="font-medium">Patient: Jane Doe</p>
              <p className="text-sm text-gray-600">Doctor: Dr. Emily White</p>
            </div>
            <span className="text-sm text-gray-500">Today, 10:00 AM</span>
          </li>
          <li className="py-3 flex justify-between items-center">
            <div>
              <p className="font-medium">Patient: Peter Jones</p>
              <p className="text-sm text-gray-600">Doctor: Dr. Alan Grant</p>
            </div>
            <span className="text-sm text-gray-500">Today, 02:30 PM</span>
          </li>
          <li className="py-3 flex justify-between items-center">
            <div>
              <p className="font-medium">Patient: Alice Brown</p>
              <p className="text-sm text-gray-600">Doctor: Dr. Smith</p>
            </div>
            <span className="text-sm text-gray-500">Tomorrow, 09:00 AM</span>
          </li>
        </ul>
      </Card>
    </div>
  );
};

export default DashboardAdmin;