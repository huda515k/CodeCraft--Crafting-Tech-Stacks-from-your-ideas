import React from 'react';
import Table from '../components/Table';
import { customers } from '../utils/mockData';

interface Customer {
  id: string;
  name: string;
  email: string;
  status: 'Active' | 'Inactive' | 'Pending';
}

const Customers: React.FC = () => {
  const columns = [
    { key: 'name', header: 'Name' },
    { key: 'email', header: 'Email' },
    {
      key: 'status',
      header: 'Status',
      render: (customer: Customer) => (
        <span
          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
            customer.status === 'Active'
              ? 'bg-green-100 text-green-800'
              : customer.status === 'Inactive'
              ? 'bg-red-100 text-red-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}
        >
          {customer.status}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-800">Customers</h2>
      <Table<Customer> data={customers} columns={columns} />
    </div>
  );
};

export default Customers;