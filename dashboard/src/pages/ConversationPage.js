// dashboard/src/pages/ConversationPage.js
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

function ConversationPage() {
  const { id } = useParams();
  const [convo, setConvo] = useState(null);

  useEffect(() => {
    axios.get(`http://localhost:8000/conversations/${id}`, {
      headers: {
        Authorization: localStorage.getItem("token")
      }
    }).then((res) => setConvo(res.data));
  }, [id]);

  if (!convo) return <div>Loading...</div>;

  return (
    <div>
      <h2>Conversation {convo.id}</h2>
      <p><strong>Summary:</strong> {convo.summary}</p>
      <p><strong>Sentiment:</strong> {convo.sentiment_score}</p>
      <p><strong>Emotion Scores:</strong></p>
      <ul>
        {Object.entries(convo.emotion_scores).map(([emotion, score]) => (
          <li key={emotion}>{emotion}: {score.toFixed(2)}</li>
        ))}
      </ul>
      <hr />
      <p><strong>Transcript:</strong></p>
      <pre>{convo.transcript}</pre>
    </div>
  );
}

export default ConversationPage;
