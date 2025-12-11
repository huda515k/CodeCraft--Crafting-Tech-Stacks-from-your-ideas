import React from 'react';
import { Table } from '../components/Table';

const Dashboard = () => {
  const data = [
    { id: 1, name: 'John Doe', email: 'john@example.com' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com' },
  ];

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <Table data={data} />
    </div>
  );
};

export default Dashboard;