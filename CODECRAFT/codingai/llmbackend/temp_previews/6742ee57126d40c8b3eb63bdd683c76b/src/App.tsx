import React, { useState } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import Customers from './pages/Customers';
import Leads from './pages/Leads';

type Page = 'Dashboard' | 'Customers' | 'Leads';

const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<Page>('Dashboard');

  const renderPage = () => {
    switch (currentPage) {
      case 'Dashboard':
        return <Dashboard />;
      case 'Customers':
        return <Customers />;
      case 'Leads':
        return <Leads />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar currentPage={currentPage} onNavigate={setCurrentPage} />
        <main className="flex-1 p-6 overflow-auto bg-gray-50">
          {renderPage()}
        </main>
      </div>
    </div>
  );
};

export default App;