export interface Patient {
  id: string;
  name: string;
  age: number;
  gender: string;
  status: string; // e.g., Admitted, Discharged, Stable, Critical
  contact: string;
}

export const patients: Patient[] = [
  {
    id: 'P001',
    name: 'Alice Smith',
    age: 45,
    gender: 'Female',
    status: 'Admitted',
    contact: 'alice.s@example.com',
  },
  {
    id: 'P002',
    name: 'Bob Johnson',
    age: 62,
    gender: 'Male',
    status: 'Stable',
    contact: 'bob.j@example.com',
  },
  {
    id: 'P003',
    name: 'Carol White',
    age: 30,
    gender: 'Female',
    status: 'Discharged',
    contact: 'carol.w@example.com',
  },
  {
    id: 'P004',
    name: 'David Lee',
    age: 78,
    gender: 'Male',
    status: 'Critical',
    contact: 'david.l@example.com',
  },
  {
    id: 'P005',
    name: 'Emily Davis',
    age: 22,
    gender: 'Female',
    status: 'Admitted',
    contact: 'emily.d@example.com',
  },
];

export interface Doctor {
  id: string;
  name: string;
  specialty: string;
  contact: string;
}

export const doctors: Doctor[] = [
  { id: 'D001', name: 'Dr. Emily White', specialty: 'General Practitioner', contact: 'emily.w@example.com' },
  { id: 'D002', name: 'Dr. Alan Grant', specialty: 'Pediatrician', contact: 'alan.g@example.com' },
  { id: 'D003', name: 'Dr. Sarah Smith', specialty: 'Cardiologist', contact: 'sarah.s@example.com' },
];

export interface Appointment {
  id: string;
  patientId: string;
  doctorId: string;
  date: string;
  time: string;
  reason: string;
}

export const appointments: Appointment[] = [
  { id: 'A001', patientId: 'P001', doctorId: 'D001', date: '2024-05-15', time: '10:00 AM', reason: 'Routine Check-up' },
  { id: 'A002', patientId: 'P002', doctorId: 'D002', date: '2024-05-15', time: '11:30 AM', reason: 'Follow-up' },
];