import { Routes, Route, Navigate, Outlet } from 'react-router-dom';
import Layout from './components/Layout';
import AdminDashboard from './pages/AdminDashboard';
import DoctorDashboard from './pages/DoctorDashboard';
import PatientDashboard from './pages/PatientDashboard';
import PatientManagement from './pages/PatientManagement';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/admin-dashboard" replace />} />
      <Route path="/" element={<Layout />}>
        <Route path="admin-dashboard" element={<AdminDashboard />} />
        <Route path="doctor-dashboard" element={<DoctorDashboard />} />
        <Route path="patient-dashboard" element={<PatientDashboard />} />
        <Route path="patient-management" element={<PatientManagement />} />
      </Route>
      {/* Add a catch-all route for 404 if needed */}
      <Route path="*" element={<NoMatch />} />
    </Routes>
  );
}

function NoMatch() {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <h2 className="text-2xl font-bold text-gray-800">404 - Page Not Found</h2>
    </div>
  );
}

export default App;