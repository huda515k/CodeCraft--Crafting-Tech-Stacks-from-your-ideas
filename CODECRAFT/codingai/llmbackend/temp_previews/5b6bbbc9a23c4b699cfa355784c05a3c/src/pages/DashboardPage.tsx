import React from 'react';
import Card from '../components/Card';
import Button from '../components/Button';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: string;
  color: string;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color }) => (
  <Card className="flex items-center p-4">
    <div className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center text-white text-xl ${color}`}>
      {icon}
    </div>
    <div className="ml-4">
      <p className="text-sm font-medium text-gray-500">{title}</p>
      <p className="text-2xl font-semibold text-gray-900">{value}</p>
    </div>
  </Card>
);

const DashboardPage: React.FC = () => {
  const recentActivities = [
    { id: 1, type: 'Attendance', description: 'Faculty attendance marked for today.', time: '10:30 AM' },
    { id: 2, type: 'Announcement', description: 'New holiday announcement posted.', time: 'Yesterday' },
    { id: 3, type: 'Enrollment', description: '5 new students enrolled.', time: '2 days ago' },
    { id: 4, type: 'Course Update', description: 'Math course material updated.', time: 'Last week' },
  ];

  return (
    <div className="container mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard title="Total Students" value="1250" icon="🧑‍🎓" color="bg-blue-500" />
        <StatCard title="Total Faculty" value="85" icon="👨‍🏫" color="bg-green-500" />
        <StatCard title="Active Courses" value="42" icon="📚" color="bg-purple-500" />
        <StatCard title="Pending Applications" value="12" icon="📄" color="bg-yellow-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent School Activities</h2>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Time
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {recentActivities.map((activity) => (
                  <tr key={activity.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {activity.type}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {activity.description}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {activity.time}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-6 text-right">
            <Button variant="secondary" size="sm">View All Activities</Button>
          </div>
        </Card>

        <Card>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Button className="w-full justify-start">Add New Student</Button>
            <Button className="w-full justify-start">Manage Faculty</Button>
            <Button className="w-full justify-start">Create Announcement</Button>
            <Button className="w-full justify-start">View Reports</Button>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default DashboardPage;