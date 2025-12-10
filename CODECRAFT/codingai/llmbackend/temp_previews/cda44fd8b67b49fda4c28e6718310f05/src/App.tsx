import { Routes, Route, Navigate } from 'react-router-dom';
import { useState } from 'react';

import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DashboardPage from './pages/DashboardPage';
import AttendancePage from './pages/AttendancePage';
import Layout from './components/Layout';

function App() {
  // Simple authentication state simulation
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);

  // In a real app, this would involve API calls and token management
  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleSignup = () => {
    // After signup, typically auto-login or redirect to login
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
  };

  return (
    <Routes>
      <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
      <Route path="/signup" element={<SignupPage onSignup={handleSignup} />} />

      {isAuthenticated ? (
        <Route path="/" element={<Layout onLogout={handleLogout} />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="attendance" element={<AttendancePage />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Route>
      ) : (
        <Route path="*" element={<Navigate to="/login" replace />} />
      )}
    </Routes>
  );
}

export default App;