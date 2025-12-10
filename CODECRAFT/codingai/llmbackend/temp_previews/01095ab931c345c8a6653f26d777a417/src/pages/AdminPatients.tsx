import React, { useState } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import Modal from '../components/Modal';
import Input from '../components/Input';
import useModal from '../hooks/useModal';
import { Patient, patients as initialPatients } from '../utils/data'; // Mock data

const AdminPatients: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>(initialPatients);
  const { isOpen, openModal, closeModal } = useModal();
  const [editingPatient, setEditingPatient] = useState<Patient | null>(null);
  const [formErrors, setFormErrors] = useState<Partial<Patient>>({});

  const handleAddPatientClick = () => {
    setEditingPatient(null); // Clear for new patient
    setFormErrors({});
    openModal();
  };

  const handleEditPatientClick = (patient: Patient) => {
    setEditingPatient({ ...patient }); // Clone to avoid direct state modification
    setFormErrors({});
    openModal();
  };

  const handleDeletePatient = (id: string) => {
    if (window.confirm('Are you sure you want to delete this patient?')) {
      setPatients(patients.filter(p => p.id !== id));
    }
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const newPatient: Patient = {
      id: editingPatient?.id || `P${String(patients.length + 1).padStart(3, '0')}`,
      name: formData.get('name') as string,
      age: parseInt(formData.get('age') as string),
      gender: formData.get('gender') as string,
      status: formData.get('status') as string,
      contact: formData.get('contact') as string,
    };

    const errors: Partial<Patient> = {};
    if (!newPatient.name.trim()) errors.name = 'Name is required';
    if (!newPatient.age || newPatient.age <= 0) errors.age = 'Valid age is required';
    if (!newPatient.gender.trim()) errors.gender = 'Gender is required';
    if (!newPatient.status.trim()) errors.status = 'Status is required';
    if (!newPatient.contact.trim()) errors.contact = 'Contact is required';

    if (Object.keys(errors).length > 0) {
      setFormErrors(errors);
      return;
    }

    if (editingPatient) {
      setPatients(patients.map(p => (p.id === newPatient.id ? newPatient : p)));
    } else {
      setPatients([...patients, newPatient]);
    }
    closeModal();
  };

  const ModalForm = (
    <form onSubmit={handleSubmit}>
      <Input
        id="name"
        label="Name"
        type="text"
        defaultValue={editingPatient?.name || ''}
        error={formErrors.name}
        required
      />
      <Input
        id="age"
        label="Age"
        type="number"
        defaultValue={editingPatient?.age || ''}
        error={formErrors.age}
        required
      />
      <Input
        id="gender"
        label="Gender"
        type="text"
        defaultValue={editingPatient?.gender || ''}
        error={formErrors.gender}
        required
      />
      <Input
        id="status"
        label="Status"
        type="text"
        defaultValue={editingPatient?.status || ''}
        error={formErrors.status}
        required
      />
      <Input
        id="contact"
        label="Contact"
        type="text"
        defaultValue={editingPatient?.contact || ''}
        error={formErrors.contact}
        required
      />
      <div className="mt-4 flex justify-end space-x-2">
        <Button type="button" variant="outline" onClick={closeModal}>
          Cancel
        </Button>
        <Button type="submit" variant="primary">
          {editingPatient ? 'Save Changes' : 'Add Patient'}
        </Button>
      </div>
    </form>
  );

  return (
    <Card title="Manage Patients">
      <div className="mb-4 flex justify-end">
        <Button onClick={handleAddPatientClick} variant="primary">
          Add New Patient
        </Button>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Age
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Gender
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Contact
              </th>
              <th scope="col" className="relative px-6 py-3">
                <span className="sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {patients.map(patient => (
              <tr key={patient.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {patient.id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {patient.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {patient.age}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {patient.gender}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {patient.status}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {patient.contact}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                  <Button variant="info" size="sm" onClick={() => handleEditPatientClick(patient)}>
                    Edit
                  </Button>
                  <Button variant="danger" size="sm" onClick={() => handleDeletePatient(patient.id)}>
                    Delete
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Modal
        isOpen={isOpen}
        onClose={closeModal}
        title={editingPatient ? 'Edit Patient' : 'Add New Patient'}
        size="sm"
      >
        {ModalForm}
      </Modal>
    </Card>
  );
};

export default AdminPatients;