import React, { useState, useEffect } from 'react';
import Button from '../components/Button';
import Input from '../components/Input';
import Modal from '../components/Modal';
import Card from '../components/Card';
import useModal from '../hooks/useModal';
import useForm from '../hooks/useForm';
import { Patient } from '../utils/types';
import { mockPatients } from '../utils/data';

const initialPatientForm: Patient = {
  id: '',
  name: '',
  age: 0,
  gender: '',
  contact: '',
  status: 'Active',
};

const validatePatientForm = (values: Patient) => {
  const errors: { [key: string]: string } = {};
  if (!values.name) errors.name = 'Name is required';
  if (values.age <= 0) errors.age = 'Age must be positive';
  if (!values.gender) errors.gender = 'Gender is required';
  if (!values.contact) errors.contact = 'Contact is required';
  return errors;
};

const PatientManagement: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>(mockPatients);
  const { isOpen, openModal, closeModal } = useModal();
  const [isEditing, setIsEditing] = useState(false);

  const {
    values: patientForm,
    setValues: setPatientForm,
    errors: formErrors,
    handleChange,
    handleSubmit,
    resetForm,
  } = useForm(initialPatientForm, validatePatientForm);

  const handleAddPatient = () => {
    setIsEditing(false);
    resetForm();
    openModal();
  };

  const handleEditPatient = (patient: Patient) => {
    setIsEditing(true);
    setPatientForm(patient);
    openModal();
  };

  const handleDeletePatient = (id: string) => {
    if (window.confirm('Are you sure you want to delete this patient?')) {
      setPatients(prev => prev.filter(patient => patient.id !== id));
    }
  };

  const submitPatientForm = () => {
    if (isEditing) {
      setPatients(prev =>
        prev.map(p => (p.id === patientForm.id ? patientForm : p))
      );
    } else {
      setPatients(prev => [...prev, { ...patientForm, id: Date.now().toString() }]);
    }
    closeModal();
    resetForm();
  };

  return (
    <div className="container mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Patient Management</h1>

      <div className="flex justify-end mb-4">
        <Button onClick={handleAddPatient}>Add New Patient</Button>
      </div>

      <Card className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
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
                Contact
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {patients.map(patient => (
              <tr key={patient.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {patient.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {patient.age}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {patient.gender}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {patient.contact}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    patient.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {patient.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <Button variant="secondary" size="sm" className="mr-2" onClick={() => handleEditPatient(patient)}>
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
      </Card>

      <Modal
        isOpen={isOpen}
        onClose={closeModal}
        title={isEditing ? 'Edit Patient' : 'Add New Patient'}
      >
        <form onSubmit={handleSubmit(submitPatientForm)}>
          <Input
            id="name"
            name="name"
            label="Name"
            value={patientForm.name}
            onChange={handleChange}
            error={formErrors.name}
          />
          <Input
            id="age"
            name="age"
            label="Age"
            type="number"
            value={patientForm.age}
            onChange={handleChange}
            error={formErrors.age}
          />
          <div className="mb-4">
            <label htmlFor="gender" className="block text-sm font-medium text-gray-700 mb-1">
              Gender
            </label>
            <select
              id="gender"
              name="gender"
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
              value={patientForm.gender}
              onChange={handleChange}
            >
              <option value="">Select Gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
            {formErrors.gender && <p className="mt-1 text-sm text-red-600">{formErrors.gender}</p>}
          </div>
          <Input
            id="contact"
            name="contact"
            label="Contact"
            value={patientForm.contact}
            onChange={handleChange}
            error={formErrors.contact}
          />
          <div className="flex justify-end gap-2 mt-6">
            <Button type="button" variant="secondary" onClick={closeModal}>
              Cancel
            </Button>
            <Button type="submit">
              {isEditing ? 'Save Changes' : 'Add Patient'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default PatientManagement;