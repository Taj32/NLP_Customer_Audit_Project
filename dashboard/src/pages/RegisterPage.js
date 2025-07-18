import React, { useState } from 'react';
import axios from 'axios';

function RegisterPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [businessName, setBusinessName] = useState("");

  const register = async () => {
    try {
      await axios.post("http://localhost:8000/auth/register", {
        email,
        password,
        business_name: businessName
      });
      window.location.href = "/";
    } catch (err) {
      alert("Registration failed");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Create an Account</h2>
        <input
          className="w-full border px-3 py-2 mb-4 rounded"
          placeholder="Business Name"
          onChange={(e) => setBusinessName(e.target.value)}
        />
        <input
          className="w-full border px-3 py-2 mb-4 rounded"
          placeholder="Email"
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          className="w-full border px-3 py-2 mb-4 rounded"
          placeholder="Password"
          type="password"
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700"
          onClick={register}
        >
          Register
        </button>
        <p className="mt-4 text-center text-sm text-gray-600">
          Already have an account? <a className="text-blue-600" href="/">Login</a>
        </p>
      </div>
    </div>
  );
}

export default RegisterPage;

