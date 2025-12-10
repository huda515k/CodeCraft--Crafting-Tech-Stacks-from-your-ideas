import React from 'react';
import Card from '../components/Card';
import Button from '../components/Button';

interface Worker {
  id: string;
  name: string;
  role: string;
  status: 'Active' | 'On Leave' | 'Inactive';
}

const workersData: Worker[] = [
  { id: '1', name: 'Alice Johnson', role: 'Cashier', status: 'Active' },
  { id: '2', name: 'Bob Williams', role: 'Stock Clerk', status: 'Active' },
  { id: '3', name: 'Charlie Davis', role: 'Manager', status: 'On Leave' },
  { id: '4', name: 'Diana Miller', role: 'Cashier', status: 'Active' },
  { id: '5', name: 'Eve Brown', role: 'Stock Clerk', status: 'Inactive' },
];

const WorkersPage: React.FC = () => {
  return (
    <div className="p-6 bg-gray-100 min-h-full">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Manage Workers</h1>

      <Card title="Worker List">
        <div className="mb-4 flex justify-end">
          <Button variant="primary">Add New Worker</Button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {workersData.map((worker) => (
                <tr key={worker.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {worker.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {worker.role}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      worker.status === 'Active' ? 'bg-green-100 text-green-800' :
                      worker.status === 'On Leave' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {worker.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <Button variant="secondary" size="sm" className="mr-2">Edit</Button>
                    <Button variant="danger" size="sm">Delete</Button>
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

export default WorkersPage;