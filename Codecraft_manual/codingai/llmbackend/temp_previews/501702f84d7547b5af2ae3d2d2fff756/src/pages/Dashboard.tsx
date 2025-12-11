import React, { useState } from 'react';
import { Button, Card, Input, Modal } from '../components';

const Dashboard: React.FC = () => {
  const [showModal, setShowModal] = useState(false);
  const [newTask, setNewTask] = useState('');

  const handleAddTask = () => {
    if (newTask.trim()) {
      // Logic to add task
      console.log('New task added:', newTask);
      setNewTask('');
      setShowModal(false);
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <Card title="Add Task" className="mb-4">
        <Input
          type="text"
          value={newTask}
          onChange={(e) => setNewTask(e.target.value)}
          placeholder="Enter task..."
        />
        <Button onClick={() => setShowModal(true)}>Add</Button>
      </Card>
      {showModal && (
        <Modal onClose={() => setShowModal(false)}>
          <h2 className="text-lg font-bold mb-4">Add New Task</h2>
          <Input
            type="text"
            value={newTask}
            onChange={(e) => setNewTask(e.target.value)}
            placeholder="Enter task..."
          />
          <Button onClick={handleAddTask}>Submit</Button>
        </Modal>
      )}
    </div>
  );
};

export default Dashboard;