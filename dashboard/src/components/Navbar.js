import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

function Navbar({ title = "Dashboard" }) {
  const location = useLocation();
  const navigate = useNavigate();

  const isConversationPage = location.pathname.startsWith('/conversation/');

  const logout = () => {
    localStorage.removeItem("token");
    window.location.href = "/";
  };

  const goToDashboard = () => {
    navigate('/dashboard'); // Adjust the path if your dashboard has a different route
  };

  return (
    <nav className="bg-gray-800 text-white p-4 flex justify-between items-center shadow">
      <h1 className="text-xl font-semibold">{title}</h1>
      <div className="flex gap-2">
        {isConversationPage && (
          <button
            onClick={goToDashboard}
            className="bg-gray-500 hover:bg-blue-600 px-4 py-2 rounded text-sm"
          >
            Go Back to Dashboard
          </button>
        )}
        <button
          onClick={logout}
          className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded text-sm"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}

export default Navbar;