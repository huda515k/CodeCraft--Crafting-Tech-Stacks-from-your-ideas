import React, { useState } from 'react';
import Modal from '../components/Modal';
import Button from '../components/Button';

const Doctors: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [name, setName] = useState('');
  const [specialization, setSpecialization] = useState('');

  const handleAddDoctor = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle add doctor logic here
    console.log('Adding doctor:', name, specialization);
    setIsOpen(false);
    setName('');
    setSpecialization('');
  };

  return (
    <div className="flex justify-center items-center h-screen">
      <div className="bg-white p-8 shadow-md rounded-lg w-96 mx-auto">
        <h1 className="text-2xl font-bold mb-4">Doctors</h1>
        <Button onClick={() => setIsOpen(true)}>Add Doctor</Button>
        {isOpen && (
          <Modal onClose={() => setIsOpen(false)}>
            <form onSubmit={handleAddDoctor}>
              <Input label="Name" name="name" value={name} onChange={(e) => setName(e.target.value)} />
              <Input
                label="Specialization"
                name="specialization"
                value={specialization}
                onChange={(e) => setSpecialization(e.target.value)}
              />
              <Button type="submit">Add</Button>
            </form>
          </Modal>
        )}
      </div>
    </div>
  );
};

export default Doctors;