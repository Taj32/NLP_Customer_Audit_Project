import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';

function ConversationPage() {
  const { id } = useParams();
  const [convo, setConvo] = useState(null);
  const [isTranscriptVisible, setIsTranscriptVisible] = useState(false); // State to toggle transcript visibility

  useEffect(() => {
    axios.get(`http://localhost:8000/conversations/${id}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem("token")}`
      }
    }).then((res) => setConvo(res.data));
  }, [id]);

  if (!convo) return <div className="p-4">Loading...</div>;

  return (
    <div className="bg-gray-50 min-h-screen">
      <Navbar title={`Conversation ${convo.id}`} />
      <div className="max-w-4xl mx-auto py-8 px-4 bg-white shadow rounded mt-4">
        <h2 className="text-xl font-semibold mb-2 text-gray-800">Summary</h2>
        <p className="mb-4 text-gray-700">{convo.summary}</p>

        <h3 className="font-semibold text-gray-800">Sentiment: 
          <span className="ml-2 text-blue-700">{convo.sentiment_score}</span>
        </h3>

        <h3 className="font-semibold text-gray-800 mt-4">Emotion Scores:</h3>
        <ul className="list-disc list-inside text-gray-700 mb-4">
          {Object.entries(convo.emotion_scores).map(([e, s]) => (
            <li key={e}>{e}: {s.toFixed(2)}</li>
          ))}
        </ul>

        <div className="flex items-center justify-between mt-4">
          <h3 className="font-semibold text-gray-800">Transcript</h3>
          <button
            className="flex items-center text-blue-600 hover:text-blue-800"
            onClick={() => setIsTranscriptVisible(!isTranscriptVisible)} // Toggle visibility
          >
            {isTranscriptVisible ? "Hide" : "Show"}
            <svg
              className={`w-5 h-5 ml-2 transform transition-transform ${
                isTranscriptVisible ? "rotate-180" : "rotate-0"
              }`}
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
        </div>
        {isTranscriptVisible && (
          <pre className="bg-gray-100 p-4 rounded mt-2 text-sm whitespace-pre-wrap">
            {convo.transcript}
          </pre>
        )}
      </div>
    </div>
  );
}

export default ConversationPage;
