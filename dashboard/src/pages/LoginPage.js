import React, { useState } from 'react';
import axios from 'axios';

const REACT_APP_API_URL = process.env.REACT_APP_API_URL;
//console.log(API_URL)

function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  

  const login = async () => {
    try {
      console.log("API URL:", REACT_APP_API_URL);
      const res = await axios.post(`${REACT_APP_API_URL}/auth/login`, {
        email,
        password
      });
      localStorage.setItem("token", res.data.access_token);
      window.location.href = "/dashboard";
    } catch (err) {
      alert("Login failed");
      console.error(err.response?.data || err.message);
    }
  };
  

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Login</h2>
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
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
          onClick={login}
        >
          Login
        </button>
        <p className="mt-4 text-center text-sm text-gray-600">
          Don't have an account? <a className="text-blue-600" href="/register">Register</a>
        </p>
      </div>
    </div>
  );
}

export default LoginPage;
