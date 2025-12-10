import React from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';

const Customers: React.FC = () => {
  const mockCustomers = [
    { id: 1, name: 'Alice Smith', email: 'alice@example.com', company: 'Tech Solutions Inc.', status: 'Active' },
    { id: 2, name: 'Bob Johnson', email: 'bob@example.com', company: 'Global Innovations', status: 'Pending' },
    { id: 3, name: 'Charlie Brown', email: 'charlie@example.com', company: 'Creative Agency', status: 'Inactive' },
    { id: 4, name: 'Diana Prince', email: 'diana@example.com', company: 'Wonder Corp', status: 'Active' },
    { id: 5, name: 'Eve Adams', email: 'eve@example.com', company: 'Future Enterprises', status: 'Active' },
    { id: 6, name: 'Frank White', email: 'frank@example.com', company: 'Data Systems', status: 'Active' },
    { id: 7, name: 'Grace Taylor', email: 'grace@example.com', company: 'Software Co.', status: 'Pending' },
  ];

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-gray-800">Customers</h2>
        <Button variant="primary">Add New Customer</Button>
      </div>

      <Card>
        <div className="mb-4 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <Input type="text" placeholder="Search customers..." className="max-w-xs" />
          <div className="flex gap-2">
            <Button variant="secondary" size="sm">Filter</Button>
            <Button variant="secondary" size="sm">Export</Button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Company</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th scope="col" className="relative px-6 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {mockCustomers.map((customer) => (
                <tr key={customer.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{customer.name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{customer.email}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{customer.company}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      customer.status === 'Active' ? 'bg-green-100 text-green-800' :
                      customer.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {customer.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <a href="#" className="text-indigo-600 hover:text-indigo-900 mr-2">Edit</a>
                    <a href="#" className="text-red-600 hover:text-red-900">Delete</a>
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

export default Customers;