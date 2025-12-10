import React from 'react';
import Card from '../components/Card';
import Button from '../components/Button';

const DashboardPatient: React.FC = () => {
  const myAppointments = [
    { date: '2024-05-10', time: '10:00 AM', doctor: 'Dr. Smith', type: 'Follow-up' },
    { date: '2024-06-01', time: '02:00 PM', doctor: 'Dr. White', type: 'Annual Check-up' },
  ];

  const recentDiagnoses = [
    { date: '2024-04-15', diagnosis: 'Common Cold', doctor: 'Dr. Smith' },
    { date: '2024-03-01', diagnosis: 'Minor Allergy', doctor: 'Dr. Jones' },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <Card title="Welcome, John Doe!" className="lg:col-span-2">
        <p className="text-gray-700">Your health information at a glance.</p>
      </Card>

      <Card title="Upcoming Appointments">
        <ul className="divide-y divide-gray-200">
          {myAppointments.map((appt, index) => (
            <li key={index} className="py-3 flex justify-between items-center">
              <div>
                <p className="font-medium">{appt.date} - {appt.time}</p>
                <p className="text-sm text-gray-600">With {appt.doctor} for {appt.type}</p>
              </div>
              <Button variant="info" size="sm">Details</Button>
            </li>
          ))}
          {myAppointments.length === 0 && (
            <li className="py-3 text-gray-500">No upcoming appointments.</li>
          )}
        </ul>
        <div className="mt-4 text-right">
          <Button variant="text">Schedule New Appointment</Button>
        </div>
      </Card>

      <Card title="Recent Diagnoses">
        <ul className="divide-y divide-gray-200">
          {recentDiagnoses.map((diag, index) => (
            <li key={index} className="py-3 flex justify-between items-center">
              <div>
                <p className="font-medium">{diag.date}: {diag.diagnosis}</p>
                <p className="text-sm text-gray-600">Diagnosed by {diag.doctor}</p>
              </div>
              <Button variant="text" size="sm">View Report</Button>
            </li>
          ))}
          {recentDiagnoses.length === 0 && (
            <li className="py-3 text-gray-500">No recent diagnoses found.</li>
          )}
        </ul>
        <div className="mt-4 text-right">
          <Button variant="text">View Full Medical History</Button>
        </div>
      </Card>
    </div>
  );
};

export default DashboardPatient;