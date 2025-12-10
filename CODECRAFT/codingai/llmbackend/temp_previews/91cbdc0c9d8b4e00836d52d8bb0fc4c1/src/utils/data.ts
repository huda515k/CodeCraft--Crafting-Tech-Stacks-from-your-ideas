import { Patient } from './types';

export const mockPatients: Patient[] = [
  {
    id: '1',
    name: 'Alice Johnson',
    age: 35,
    gender: 'Female',
    contact: 'alice.j@example.com',
    status: 'Active',
  },
  {
    id: '2',
    name: 'Bob Williams',
    age: 50,
    gender: 'Male',
    contact: 'bob.w@example.com',
    status: 'Active',
  },
  {
    id: '3',
    name: 'Charlie Brown',
    age: 28,
    gender: 'Male',
    contact: 'charlie.b@example.com',
    status: 'Active',
  },
  {
    id: '4',
    name: 'Diana Prince',
    age: 42,
    gender: 'Female',
    contact: 'diana.p@example.com',
    status: 'Inactive',
  },
];