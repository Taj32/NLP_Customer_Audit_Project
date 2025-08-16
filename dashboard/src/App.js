// dashboard/src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ConversationPage from './pages/ConversationPage';
import RegisterPage from './pages/RegisterPage';
import VerifyPage from './pages/VerifyPage'; // Import the VerifyPage

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/conversation/:id" element={<ConversationPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/verify/:token" element={<VerifyPage />} /> {/* Add this route */}
      </Routes>
    </Router>
  );
}

export default App;
