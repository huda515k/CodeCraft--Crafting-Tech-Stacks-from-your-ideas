import React from 'react';
import Input from '../components/Input';
import Button from '../components/Button';

const Customers: React.FC = () => {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  return (
    <div className="flex flex-col min-h-screen">
      <header className="bg-blue-500 text-white p-4 shadow-md">
        <div className="container mx-auto flex items-center justify-between">
          <h1 className="text-xl font-bold">Customers</h1>
          <Button>Export CSV</Button>
        </div>
      </header>
      <main className="flex-grow p-4 container mx-auto">
        <section className="mb-4">
          <Input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by name..."
          />
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="border border-gray-300 px-4 py-2 rounded ml-2"
          >
            <option value="all">All</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
        </section>
        <table className="w-full border-collapse">
          <thead>
            <tr>
              <th className="border px-4 py-2">Name</th>
              <th className="border px-4 py-2">Status</th>
              <th className="border px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="border px-4 py-2">John Doe</td>
              <td className="border px-4 py-2 text-green-500">Active</td>
              <td className="border px-4 py-2">
                <Button>Edit</Button> | <Button>Delete</Button>
              </td>
            </tr>
            {/* More rows... */}
          </tbody>
        </table>
      </main>
    </div>
  );
};

export default Customers;