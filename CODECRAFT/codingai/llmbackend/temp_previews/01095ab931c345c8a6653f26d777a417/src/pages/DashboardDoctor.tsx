import React from 'react';
import Card from '../components/Card';
import Button from '../components/Button';

const DashboardDoctor: React.FC = () => {
  const upcomingAppointments = [
    { time: '09:00 AM', patient: 'Alice Smith', reason: 'Routine Check-up' },
    { time: '10:30 AM', patient: 'Bob Johnson', reason: 'Follow-up on X-ray' },
    { time: '01:00 PM', patient: 'Carol White', reason: 'Flu symptoms' },
  ];

  const yourPatients = [
    { id: 'P001', name: 'Alice Smith', status: 'Stable' },
    { id: 'P002', name: 'David Lee', status: 'Under Observation' },
    { id: 'P003', name: 'Emily Clark', status: 'Recovering' },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card title="Welcome, Dr. Emily White!" className="lg:col-span-2">
        <p className="text-gray-700">Here's a quick overview of your day.</p>
      </Card>

      <Card title="Today's Appointments">
        <ul className="divide-y divide-gray-200">
          {upcomingAppointments.map((appt, index) => (
            <li key={index} className="py-3 flex justify-between items-center">
              <div>
                <p className="font-medium">{appt.time} - {appt.patient}</p>
                <p className="text-sm text-gray-600">{appt.reason}</p>
              </div>
              <Button variant="info" size="sm">View</Button>
            </li>
          ))}
          {upcomingAppointments.length === 0 && (
            <li className="py-3 text-gray-500">No appointments scheduled for today.</li>
          )}
        </ul>
        <div className="mt-4 text-right">
          <Button variant="text">View All Appointments</Button>
        </div>
      </Card>

      <Card title="Your Patients">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Patient ID
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="relative px-6 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {yourPatients.map((patient) => (
                <tr key={patient.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {patient.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {patient.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {patient.status}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Button variant="text" size="sm">View Record</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 text-right">
          <Button variant="text">View All Patients</Button>
        </div>
      </Card>
    </div>
  );
};

export default DashboardDoctor;