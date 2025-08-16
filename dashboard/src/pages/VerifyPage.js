import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const REACT_APP_API_URL = process.env.REACT_APP_API_URL;

function VerifyPage() {
  const { token } = useParams();
  const [message, setMessage] = useState("Verifying...");
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get(`${REACT_APP_API_URL}/auth/verify/${token}`)
      .then((res) => {
        setMessage(res.data.msg);
        setTimeout(() => navigate("/login"), 3000); // Redirect after 3 seconds
      })
      .catch((err) => {
        setMessage(err.response?.data?.detail || "Verification failed.");
      });
  }, [token, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded shadow-md text-center">
        <h1 className="text-2xl font-bold mb-4">Email Verification</h1>
        <p>{message}</p>
      </div>
    </div>
  );
}

export default VerifyPage;