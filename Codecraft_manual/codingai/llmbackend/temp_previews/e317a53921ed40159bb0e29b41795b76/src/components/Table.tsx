import React from 'react';

interface TableProps {
  data: { id: number, name: string, email: string }[];
}

const Table = ({ data }: TableProps) => {
  return (
    <table className="w-full border-collapse">
      <thead>
        <tr className="bg-gray-200">
          <th className="border p-2">ID</th>
          <th className="border p-2">Name</th>
          <th className="border p-2">Email</th>
        </tr>
      </thead>
      <tbody>
        {data.map(item => (
          <tr key={item.id} className="bg-gray-100">
            <td className="border p-2">{item.id}</td>
            <td className="border p-2">{item.name}</td>
            <td className="border p-2">{item.email}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default Table;