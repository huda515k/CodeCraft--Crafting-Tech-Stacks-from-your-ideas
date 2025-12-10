import React from 'react';
import DashboardCard from '@components/DashboardCard';
import Card from '@components/Card';

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Dashboard Overview</h1>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <DashboardCard
          title="Total Players"
          value="125"
          icon={
            <svg className="w-6 h-6 text-accent" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h2a2 2 0 002-2V7a2 2 0 00-2-2h-2V3a1 1 0 00-1-1H8a1 1 0 00-1 1v2H5a2 2 0 00-2 2v11a2 2 0 002 2h2m-4-6h16a2 2 0 002-2V7a2 2 0 00-2-2h-2m-8-2v2m-6 4h16"></path>
            </svg>
          }
          colorClass="text-accent bg-green-100"
        />
        <DashboardCard
          title="Total Teams"
          value="15"
          icon={
            <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h2a2 2 0 002-2V7a2 2 0 00-2-2h-2V3a1 1 0 00-1-1H8a1 1 0 00-1 1v2H5a2 2 0 00-2 2v11a2 2 0 002 2h2m-4-6h16a2 2 0 002-2V7a2 2 0 00-2-2h-2m-8-2v2m-6 4h16"></path>
            </svg>
          }
          colorClass="text-blue-600 bg-blue-100"
        />
        <DashboardCard
          title="Upcoming Matches"
          value="7"
          icon={
            <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
          }
          colorClass="text-yellow-600 bg-yellow-100"
        />
      </div>

      {/* Recent Activity / Quick Links */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Recent Player Registrations</h2>
          <ul className="space-y-3">
            <li className="flex justify-between items-center text-gray-700">
              <span>Virat Kohli registered</span>
              <span className="text-sm text-gray-500">2 hours ago</span>
            </li>
            <li className="flex justify-between items-center text-gray-700">
              <span>Rohit Sharma updated profile</span>
              <span className="text-sm text-gray-500">1 day ago</span>
            </li>
            <li className="flex justify-between items-center text-gray-700">
              <span>Jasprit Bumrah registered</span>
              <span className="text-sm text-gray-500">3 days ago</span>
            </li>
          </ul>
        </Card>

        <Card>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Button variant="primary" size="lg" className="w-full">Add New Player</Button>
            <Button variant="outline" size="lg" className="w-full">Schedule Match</Button>
            <Button variant="outline" size="lg" className="w-full">Manage Teams</Button>
            <Button variant="outline" size="lg" className="w-full">View Reports</Button>
          </div>
        </Card>
      </div>

      {/* Upcoming Events/Matches */}
      <Card>
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Upcoming Matches</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 border rounded-md">
            <div>
              <p className="font-medium text-gray-900">Mumbai Indians vs Chennai Super Kings</p>
              <p className="text-sm text-gray-600">Date: 25th April 2024 | Venue: Wankhede Stadium</p>
            </div>
            <span className="px-3 py-1 text-sm font-semibold text-blue-800 bg-blue-100 rounded-full">T20</span>
          </div>
          <div className="flex items-center justify-between p-3 border rounded-md">
            <div>
              <p className="font-medium text-gray-900">Delhi Capitals vs Royal Challengers Bangalore</p>
              <p className="text-sm text-gray-600">Date: 28th April 2024 | Venue: Arun Jaitley Stadium</p>
            </div>
            <span className="px-3 py-1 text-sm font-semibold text-purple-800 bg-purple-100 rounded-full">T20</span>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Dashboard;