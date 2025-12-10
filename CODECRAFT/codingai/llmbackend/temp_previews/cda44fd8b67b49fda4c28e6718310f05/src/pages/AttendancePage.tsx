import React from 'react';
import Card from '../components/Card';

interface AttendanceRecord {
  id: string;
  date: string;
  status: 'Present' | 'Absent' | 'Late';
  course: string;
}

const mockAttendance: AttendanceRecord[] = [
  { id: '1', date: '2023-10-26', status: 'Present', course: 'Mathematics' },
  { id: '2', date: '2023-10-25', status: 'Present', course: 'Physics' },
  { id: '3', date: '2023-10-24', status: 'Absent', course: 'Mathematics' },
  { id: '4', date: '2023-10-23', status: 'Late', course: 'Chemistry' },
  { id: '5', date: '2023-10-22', status: 'Present', course: 'Physics' },
  { id: '6', date: '2023-10-21', status: 'Present', course: 'Mathematics' },
];

const AttendancePage: React.FC = () => {
  return (
    <div className="container mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Attendance Overview</h1>
      <Card>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Course
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {mockAttendance.map((record) => (
                <tr key={record.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {record.date}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {record.course}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        record.status === 'Present'
                          ? 'bg-green-100 text-green-800'
                          : record.status === 'Absent'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {record.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default AttendancePage;