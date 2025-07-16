// dashboard/src/pages/DashboardPage.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';

function DashboardPage() {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      console.error("No token found. Redirecting to login...");
      window.location.href = "/login"; // Redirect to login if no token is found
      return;
    }

    axios
      .get("http://localhost:8000/conversations/", {
        headers: {
          Authorization: token,
        },
      })
      .then((res) => {
        setConversations(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch conversations:", err.response?.data || err.message);
        setLoading(false);
        if (err.response?.status === 401) {
          // Redirect to login if unauthorized
          window.location.href = "/login";
        }
      });
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>Your Conversations</h2>
      <ul>
        {conversations.map((c) => (
          <li key={c.id}>
            <a href={`/conversation/${c.id}`}>
              Conversation {c.id} - {new Date(c.created_at).toLocaleDateString()}
            </a>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default DashboardPage;
