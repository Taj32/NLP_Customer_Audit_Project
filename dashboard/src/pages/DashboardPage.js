import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Navbar from '../components/Navbar';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';


function aggregateEmotions(conversations) {
  const totals = {};

  conversations.forEach((c) => {
    const scores = c.emotion_scores || {};
    Object.entries(scores).forEach(([emotion, score]) => {
      totals[emotion] = (totals[emotion] || 0) + score;
    });
  });

  // Optional: sort by score
  return Object.entries(totals)
    .map(([emotion, score]) => ({ emotion, score }))
    .sort((a, b) => b.score - a.score);
}

function aggregateSentiments(conversations) {
  const counts = { positive: 0, neutral: 0, negative: 0 };

  conversations.forEach((c) => {
    const sentiment = (c.sentiment_score || "").toLowerCase();
    if (sentiment in counts) {
      counts[sentiment] += 1;
    }
  });

  return Object.entries(counts).map(([sentiment, count]) => ({ sentiment, count }));
}



function DashboardPage() {
  const [conversations, setConversations] = useState([]);
  const emotionData = aggregateEmotions(conversations);
  const sentimentData = aggregateSentiments(conversations);


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
      })
      .then((res) => {
        // Ensure conversations is always an array
        setConversations(Array.isArray(res.data) ? res.data : []);
      })
      .catch((err) => {
        console.error("Failed to fetch conversations:", err.response?.data || err.message);
        setConversations([]); // Default to an empty array on error
      });
  }, []);

  return (
    <div className="bg-gray-50 min-h-screen">
      <Navbar />
      <div className="px-6 py-4">
        <h3 className="text-2xl font-semibold mb-4 text-gray-800">Insights</h3>

        <div className="flex flex-wrap gap-4">
          {/* Emotion Chart */}
          <div className="flex-1 min-w-[300px] h-[400px] bg-white p-4 shadow rounded">
            <h4 className="text-lg font-semibold mb-2">Common Emotions</h4>
            <ResponsiveContainer width="100%" height="90%">
              <BarChart data={emotionData}>
                <XAxis
                  dataKey="emotion"
                  tick={{ fontSize: 10 }}
                  angle={-45}
                  textAnchor="end"
                  interval={0}
                  height={80}
                />
                <YAxis />
                <Tooltip />
                <Bar dataKey="score" fill="#3182ce" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Sentiment Chart */}
          <div className="flex-1 min-w-[300px] h-[400px] bg-white p-4 shadow rounded">
            <h4 className="text-lg font-semibold mb-2">Sentiment Distribution</h4>
            <ResponsiveContainer width="100%" height="90%">
              <BarChart data={sentimentData}>
                <XAxis dataKey="sentiment" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#4FD1C5" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-8 px-4">
        <h2 className="text-xl font-semibold mb-6 text-gray-800">Recent Conversations</h2>
        {conversations.length === 0 ? (
          <p className="text-gray-600">No conversations found.</p>
        ) : (
          <ul className="space-y-4">
            {conversations.map((c) => (
              <li key={c.id} className="bg-white p-4 shadow rounded hover:shadow-lg transition">
                <a className="text-blue-700 font-medium" href={`/conversation/${c.id}`}>
                  Conversation {c.id} — {new Date(c.created_at).toLocaleDateString()}
                </a>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default DashboardPage;
