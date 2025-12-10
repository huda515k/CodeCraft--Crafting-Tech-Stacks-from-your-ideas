import React from 'react';
import Card from '../components/Card';
import DashboardCard from '../components/DashboardCard';
import Button from '../components/Button';

interface Customer {
  id: number;
  name: string;
  email: string;
  phone: string;
  status: 'Active' | 'Inactive' | 'Pending';
  lastActivity: string;
}

const mockCustomers: Customer[] = [
  { id: 1, name: 'Alice Smith', email: 'alice@example.com', phone: '123-456-7890', status: 'Active', lastActivity: '2 hours ago' },
  { id: 2, name: 'Bob Johnson', email: 'bob@example.com', phone: '098-765-4321', status: 'Pending', lastActivity: '1 day ago' },
  { id: 3, name: 'Charlie Brown', email: 'charlie@example.com', phone: '111-222-3333', status: 'Inactive', lastActivity: '3 days ago' },
  { id: 4, name: 'Diana Prince', email: 'diana@example.com', phone: '444-555-6666', status: 'Active', lastActivity: '5 hours ago' },
  { id: 5, name: 'Eve Adams', email: 'eve@example.com', phone: '777-888-9999', status: 'Active', lastActivity: '1 hour ago' },
];

const Dashboard: React.FC = () => {
  return (
    <div className="p-6">
      <h2 className="text-3xl font-bold text-gray-800 mb-6">Dashboard Overview</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <DashboardCard
          title="Total Customers"
          value="1,250"
          icon="👥"
          description="Increased by 5% this month"
          colorClass="text-green-600"
        />
        <DashboardCard
          title="New Leads"
          value="85"
          icon="🚀"
          description="Up 12% from last week"
          colorClass="text-blue-600"
        />
        <DashboardCard
          title="Open Deals"
          value="$50,000"
          icon="💰"
          description="5 deals currently open"
          colorClass="text-yellow-600"
        />
        <DashboardCard
          title="Conversion Rate"
          value="15.2%"
          icon="✅"
          description="Target: 18%"
          colorClass="text-red-600"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card title="Recent Customers">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Activity</th>
                    <th scope="col" className="relative px-6 py-3">
                      <span className="sr-only">Edit</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {mockCustomers.map((customer) => (
                    <tr key={customer.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{customer.name}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{customer.email}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          customer.status === 'Active' ? 'bg-green-100 text-green-800' :
                          customer.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {customer.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{customer.lastActivity}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <a href="#" className="text-indigo-600 hover:text-indigo-900">Edit</a>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4 flex justify-end">
              <Button variant="secondary" size="sm">View All Customers</Button>
            </div>
          </Card>
        </div>

        <div className="lg:col-span-1">
          <Card title="Activity Feed" className="h-full">
            <ul className="divide-y divide-gray-200">
              <li className="py-3 flex items-center">
                <span className="text-lg mr-3">📞</span>
                <div>
                  <p className="text-sm font-medium text-gray-900">Call with <span className="font-semibold">Jane Doe</span></p>
                  <p className="text-xs text-gray-500">Scheduled for tomorrow, 10:00 AM</p>
                </div>
              </li>
              <li className="py-3 flex items-center">
                <span className="text-lg mr-3">✉️</span>
                <div>
                  <p className="text-sm font-medium text-gray-900">Email sent to <span className="font-semibold">Bob Johnson</span></p>
                  <p className="text-xs text-gray-500">Subject: Project Proposal</p>
                </div>
              </li>
              <li className="py-3 flex items-center">
                <span className="text-lg mr-3">📝</span>
                <div>
                  <p className="text-sm font-medium text-gray-900">New lead from <span className="font-semibold">Website Form</span></p>
                  <p className="text-xs text-gray-500">Marketing Campaign</p>
                </div>
              </li>
              <li className="py-3 flex items-center">
                <span className="text-lg mr-3">📅</span>
                <div>
                  <p className="text-sm font-medium text-gray-900">Meeting with <span className="font-semibold">Acme Corp</span></p>
                  <p className="text-xs text-gray-500">Next Monday, 2:00 PM</p>
                </div>
              </li>
            </ul>
            <div className="mt-4 flex justify-end">
              <Button variant="secondary" size="sm">View All Activities</Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;