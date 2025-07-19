import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import Navbar from '../components/Navbar';

function ConversationPage() {
  const { id } = useParams();
  const navigate = useNavigate(); // For navigation after deletion
  const [convo, setConvo] = useState(null);
  const [isTranscriptVisible, setIsTranscriptVisible] = useState(false); // State to toggle transcript visibility
  const [isModalOpen, setIsModalOpen] = useState(false); // State to control modal visibility

  useEffect(() => {
    axios
      .get(`http://localhost:8000/conversations/${id}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })
      .then((res) => setConvo(res.data))
      .catch((err) => console.error("Failed to fetch conversation:", err));
  }, [id]);

  const handleDelete = async () => {
    try {
      await axios.delete(`http://localhost:8000/conversations/${id}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      alert("Conversation deleted successfully.");
      navigate("/dashboard"); // Redirect to the dashboard after deletion
    } catch (err) {
      console.error("Failed to delete conversation:", err);
      alert("Failed to delete the conversation. Please try again.");
    }
  };

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

        {/* Delete Button */}
        <div className="mt-6">
          <button
            className="bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700"
            onClick={() => setIsModalOpen(true)} // Open the confirmation modal
          >
            Delete Conversation
          </button>
        </div>
      </div>

      {/* Confirmation Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow-lg max-w-sm w-full">
            <h3 className="text-lg font-semibold mb-4">Are you sure?</h3>
            <p className="text-gray-700 mb-6">
              Do you really want to delete this conversation? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-4">
              <button
                className="bg-gray-300 text-gray-800 py-2 px-4 rounded hover:bg-gray-400"
                onClick={() => setIsModalOpen(false)} // Close the modal
              >
                Cancel
              </button>
              <button
                className="bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700"
                onClick={() => {
                  handleDelete();
                  setIsModalOpen(false); // Close the modal after deletion
                }}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ConversationPage;
