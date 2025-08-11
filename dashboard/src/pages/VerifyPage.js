import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams } from 'react-router-dom';

const REACT_APP_API_URL = process.env.REACT_APP_API_URL;

function VerifyPage() {
  const { token } = useParams();
  const [message, setMessage] = useState("");

  useEffect(() => {
    axios
      .get(`${REACT_APP_API_URL}/auth/verify/${token}`)
      .then((res) => {
        setMessage(res.data.msg);
      })
      .catch((err) => {
        setMessage(err.response?.data?.detail || "Verification failed.");
      });
  }, [token]);

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