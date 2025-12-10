import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import DashboardAdmin from './pages/DashboardAdmin';
import DashboardDoctor from './pages/DashboardDoctor';
import DashboardPatient from './pages/DashboardPatient';
import AdminPatients from './pages/AdminPatients';
import NotFound from './pages/NotFound';

function App() {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="relative flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
        <Header />
        <main className="flex-1 p-6 md:p-8">
          <Routes>
            <Route path="/" element={<DashboardAdmin />} /> {/* Default route */}
            <Route path="/admin-dashboard" element={<DashboardAdmin />} />
            <Route path="/admin-patients" element={<AdminPatients />} />
            <Route path="/doctor-dashboard" element={<DashboardDoctor />} />
            <Route path="/patient-dashboard" element={<DashboardPatient />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;