import React, { useState } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';

interface FacultyMember {
  id: number;
  name: string;
  department: string;
  status: 'present' | 'absent' | 'leave';
}

const AttendancePage: React.FC = () => {
  const [faculty, setFaculty] = useState<FacultyMember[]>([
    { id: 1, name: 'Dr. Alice Smith', department: 'Science', status: 'present' },
    { id: 2, name: 'Mr. Bob Johnson', department: 'Math', status: 'absent' },
    { id: 3, name: 'Ms. Carol White', department: 'Arts', status: 'leave' },
    { id: 4, name: 'Dr. David Brown', department: 'Science', status: 'present' },
    { id: 5, name: 'Ms. Emily Davis', department: 'Math', status: 'present' },
  ]);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);

  const handleStatusChange = (id: number, newStatus: 'present' | 'absent' | 'leave') => {
    setFaculty(prevFaculty =>
      prevFaculty.map(member =>
        member.id === id ? { ...member, status: newStatus } : member
      )
    );
  };

  const saveAttendance = () => {
    console.log(`Attendance saved for ${selectedDate}:`, faculty);
    alert('Attendance saved successfully!');
  };

  return (
    <div className="container mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Faculty Attendance</h1>

      <Card className="mb-6 p-6">
        <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0 md:space-x-4">
          <Input
            id="attendanceDate"
            label="Select Date"
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="w-full md:w-auto"
          />
          <Button variant="primary" onClick={saveAttendance} className="w-full md:w-auto">
            Save Attendance
          </Button>
        </div>
      </Card>

      <Card className="overflow-hidden">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Attendance for {selectedDate}</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Faculty Name
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Department
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {faculty.map((member) => (
                <tr key={member.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {member.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {member.department}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        member.status === 'present'
                          ? 'bg-green-100 text-green-800'
                          : member.status === 'absent'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {member.status.charAt(0).toUpperCase() + member.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                    <div className="flex justify-center space-x-2">
                      <Button
                        variant={member.status === 'present' ? 'primary' : 'secondary'}
                        size="sm"
                        onClick={() => handleStatusChange(member.id, 'present')}
                      >
                        Present
                      </Button>
                      <Button
                        variant={member.status === 'absent' ? 'danger' : 'secondary'}
                        size="sm"
                        onClick={() => handleStatusChange(member.id, 'absent')}
                      >
                        Absent
                      </Button>
                      <Button
                        variant={member.status === 'leave' ? 'secondary' : 'secondary'}
                        size="sm"
                        onClick={() => handleStatusChange(member.id, 'leave')}
                      >
                        Leave
                      </Button>
                    </div>
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