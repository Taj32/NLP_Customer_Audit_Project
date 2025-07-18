import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';

function DashboardPage() {
  const [conversations, setConversations] = useState([]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      window.location.href = "/";
      return;
    }

    axios
      .get("http://localhost:8000/conversations/", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }).then((res) => setConversations(res.data));
  }, []);

  return (
    <div className="bg-gray-50 min-h-screen">
      <Navbar />
      <div className="max-w-5xl mx-auto py-8 px-4">
        <h2 className="text-xl font-semibold mb-6 text-gray-800">Recent Conversations</h2>
        <ul className="space-y-4">
          {conversations.map((c) => (
            <li key={c.id} className="bg-white p-4 shadow rounded hover:shadow-lg transition">
              <a className="text-blue-700 font-medium" href={`/conversation/${c.id}`}>
                Conversation {c.id} — {new Date(c.created_at).toLocaleDateString()}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default DashboardPage;
