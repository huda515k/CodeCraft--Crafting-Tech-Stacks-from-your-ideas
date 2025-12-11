import React, { useState } from 'react';
import { Table } from 'antd';
import Button from '../components/Button';
import Modal from '../components/Modal';
import Input from '../components/Input';

const columns = [
  {
    title: 'Name',
    dataIndex: 'name',
    key: 'name',
  },
  {
    title: 'Email',
    dataIndex: 'email',
    key: 'email',
  },
  {
    title: 'Role',
    dataIndex: 'role',
    key: 'role',
  },
  {
    title: 'Actions',
    key: 'action',
    render: (_, record) => (
      <Button type="button" onClick={() => handleEdit(record)}>
        Edit
      </Button>
    ),
  },
];

const data = [
  {
    key: '1',
    name: 'John Doe',
    email: 'john.doe@example.com',
    role: 'Admin',
  },
  {
    key: '2',
    name: 'Jane Smith',
    email: 'jane.smith@example.com',
    role: 'User',
  },
];

const Dashboard: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalType, setModalType] = useState<'edit' | 'add'>('add');
  const [formState, setFormState] = useState({
    name: '',
    email: '',
    role: 'User',
  });

  const handleEdit = (record) => {
    setIsModalOpen(true);
    setModalType('edit');
    setFormState(record);
  };

  const handleAdd = () => {
    setIsModalOpen(true);
    setModalType('add');
    setFormState({
      name: '',
      email: '',
      role: 'User',
    });
  };

  const handleSave = () => {
    // Save logic here
    setIsModalOpen(false);
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-6">Attendance Management</h1>
      <Button type="button" onClick={handleAdd} className="mb-4">
        Add New User
      </Button>
      <Card title="Users">
        <Table dataSource={data} columns={columns} />
      </Card>
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        {modalType === 'add' && (
          <>
            <h2 className="text-xl font-bold mb-4">Add User</h2>
            <Input
              type="text"
              value={formState.name}
              onChange={(e) => setFormState({ ...formState, name: e.target.value })}
              placeholder="Name"
              className="mb-4"
            />
            <Input
              type="email"
              value={formState.email}
              onChange={(e) => setFormState({ ...formState, email: e.target.value })}
              placeholder="Email"
              className="mb-4"
            />
            <select
              value={formState.role}
              onChange={(e) => setFormState({ ...formState, role: e.target.value })}
              className="border border-gray-300 rounded px-4 py-2 mb-4"
            >
              <option value="User">User</option>
              <option value="Admin">Admin</option>
            </select>
          </>
        )}
        {modalType === 'edit' && (
          <>
            <h2 className="text-xl font-bold mb-4">Edit User</h2>
            <Input
              type="text"
              value={formState.name}
              onChange={(e) => setFormState({ ...formState, name: e.target.value })}
              placeholder="Name"
              className="mb-4"
            />
            <Input
              type="email"
              value={formState.email}
              onChange={(e) => setFormState({ ...formState, email: e.target.value })}
              placeholder="Email"
              className="mb-4"
            />
            <select
              value={formState.role}
              onChange={(e) => setFormState({ ...formState, role: e.target.value })}
              className="border border-gray-300 rounded px-4 py-2 mb-4"
            >
              <option value="User">User</option>
              <option value="Admin">Admin</option>
            </select>
          </>
        )}
        <Button type="button" onClick={handleSave} className="mt-4">
          Save
        </Button>
      </Modal>
    </div>
  );
};

export default Dashboard;