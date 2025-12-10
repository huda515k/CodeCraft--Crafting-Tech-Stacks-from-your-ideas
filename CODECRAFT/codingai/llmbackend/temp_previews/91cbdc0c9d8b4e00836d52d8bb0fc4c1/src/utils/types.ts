export interface Patient {
  id: string;
  name: string;
  age: number;
  gender: 'Male' | 'Female' | 'Other' | string;
  contact: string;
  status: 'Active' | 'Inactive';
}

export interface Doctor {
  id: string;
  name: string;
  specialty: string;
  contact: string;
}

export interface Appointment {
  id: string;
  patientId: string;
  doctorId: string;
  date: string;
  time: string;
  status: 'Scheduled' | 'Completed' | 'Cancelled';
}