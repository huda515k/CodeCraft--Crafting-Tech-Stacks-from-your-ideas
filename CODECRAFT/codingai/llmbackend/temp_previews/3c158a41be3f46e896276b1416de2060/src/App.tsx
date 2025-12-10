import { Routes, Route } from 'react-router-dom';
import Layout from '@components/Layout';
import Dashboard from '@pages/Dashboard';
import Players from '@pages/Players';
import Teams from '@pages/Teams';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="players" element={<Players />} />
        <Route path="teams" element={<Teams />} />
      </Route>
    </Routes>
  );
}

export default App;