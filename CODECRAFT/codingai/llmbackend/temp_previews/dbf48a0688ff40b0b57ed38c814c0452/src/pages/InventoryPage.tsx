import React from 'react';
import Card from '../components/Card';
import Button from '../components/Button';

interface InventoryItem {
  id: string;
  name: string;
  category: string;
  stock: number;
  price: number;
}

const inventoryData: InventoryItem[] = [
  { id: 'p1', name: 'Milk (1L)', category: 'Dairy', stock: 150, price: 2.99 },
  { id: 'p2', name: 'Bread (Whole Wheat)', category: 'Bakery', stock: 80, price: 3.49 },
  { id: 'p3', name: 'Organic Apples (per kg)', category: 'Produce', stock: 45, price: 4.99 },
  { id: 'p4', name: 'Chicken Breast (per kg)', category: 'Meat', stock: 60, price: 9.99 },
  { id: 'p5', name: 'Eggs (dozen)', category: 'Dairy', stock: 120, price: 3.79 },
];

const InventoryPage: React.FC = () => {
  return (
    <div className="p-6 bg-gray-100 min-h-full">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Inventory Management</h1>

      <Card title="Product List">
        <div className="mb-4 flex justify-end">
          <Button variant="primary">Add New Product</Button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Product Name
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Stock
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Price
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {inventoryData.map((item) => (
                <tr key={item.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {item.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {item.category}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      item.stock < 50 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                    }`}>
                      {item.stock}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    ${item.price.toFixed(2)}
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

export default InventoryPage;