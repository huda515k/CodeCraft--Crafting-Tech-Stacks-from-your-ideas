import React from 'react';
import Card from '../components/Card';

interface HomeworkAssignment {
  id: string;
  title: string;
  course: string;
  dueDate: string;
  status: 'Pending' | 'Completed' | 'Overdue';
}

const mockHomework: HomeworkAssignment[] = [
  {
    id: 'hw1',
    title: 'Algebra II Worksheet',
    course: 'Mathematics',
    dueDate: '2023-11-01',
    status: 'Pending',
  },
  {
    id: 'hw2',
    title: 'Electromagnetism Lab Report',
    course: 'Physics',
    dueDate: '2023-10-30',
    status: 'Overdue',
  },
  {
    id: 'hw3',
    title: 'Chemical Reactions Summary',
    course: 'Chemistry',
    dueDate: '2023-11-05',
    status: 'Pending',
  },
  {
    id: 'hw4',
    title: 'History Essay: World War I',
    course: 'History',
    dueDate: '2023-10-25',
    status: 'Completed',
  },
];

const DashboardPage: React.FC = () => {
  return (
    <div className="container mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Student Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <Card>
          <h2 className="text-lg font-semibold text-gray-700 mb-2">Total Homework</h2>
          <p className="text-4xl font-bold text-indigo-600">{mockHomework.length}</p>
        </Card>
        <Card>
          <h2 className="text-lg font-semibold text-gray-700 mb-2">Pending Homework</h2>
          <p className="text-4xl font-bold text-yellow-500">
            {mockHomework.filter((h) => h.status === 'Pending').length}
          </p>
        </Card>
        <Card>
          <h2 className="text-lg font-semibold text-gray-700 mb-2">Overdue Homework</h2>
          <p className="text-4xl font-bold text-red-600">
            {mockHomework.filter((h) => h.status === 'Overdue').length}
          </p>
        </Card>
      </div>

      <h2 className="text-2xl font-semibold text-gray-800 mb-4">Upcoming & Pending Homework</h2>
      <Card>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Course
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Due Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {mockHomework.map((assignment) => (
                <tr key={assignment.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {assignment.title}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {assignment.course}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {assignment.dueDate}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        assignment.status === 'Pending'
                          ? 'bg-yellow-100 text-yellow-800'
                          : assignment.status === 'Completed'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {assignment.status}
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

export default DashboardPage;