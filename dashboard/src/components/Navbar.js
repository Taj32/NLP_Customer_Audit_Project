import React from 'react';

function Navbar({ title = "Dashboard" }) {
  const logout = () => {
    localStorage.removeItem("token");
    window.location.href = "/";
  };

  return (
    <nav className="bg-gray-800 text-white p-4 flex justify-between items-center shadow">
      <h1 className="text-xl font-semibold">{title}</h1>
      <button
        onClick={logout}
        className="bg-red-500 hover:bg-red-600 px-4 py-2 rounded text-sm"
      >
        Logout
      </button>
    </nav>
  );
}

export default Navbar;
