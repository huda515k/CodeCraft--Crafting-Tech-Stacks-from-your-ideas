import { BrowserRouter as Router, Routes, Route, useLocation } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home/Home";
import Footer from "./components/Footer";
import Chat from "./pages/Chats/chats"; 
import BuildWorkspace from "./pages/Chats/BuildWorkspace"; 

function LayoutWrapper() {
  const location = useLocation();

  const hideLayout = location.pathname.startsWith("/chat");
  const hideLayout2 = location.pathname.startsWith("/BuildWorkspace");

  return (
    <>
      {!hideLayout && !hideLayout2 && <Navbar />}
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/BuildWorkspace" element={<BuildWorkspace />} />
      </Routes>
      {!hideLayout && <Footer />}
    </>
  );
}

export default function App() {
  return (
    <Router>
      <LayoutWrapper />
    </Router>
  );
}
