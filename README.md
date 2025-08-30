# Customer Satisfaction Analytics System

This project is a **Customer Satisfaction Analytics System** designed to help businesses gain actionable insights from real-world customer interactions. By leveraging **Natural Language Processing (NLP)** and **Generative AI**, the system captures, analyzes, and summarizes conversations, providing businesses with a deeper understanding of customer sentiment, emotions, and overall satisfaction.

---

## Features

### 1. **Conversation Analysis Pipeline**
- **Audio Recording**: Captures customer conversations in real-time.
- **Transcription**: Converts audio recordings into text using **OpenAI Whisper**.
- **Emotion Classification**: Identifies emotions (e.g., happiness, anger, sadness) using a custom-trained **EmotionClassifier**.
- **Sentiment Analysis**: Determines the overall sentiment (positive, neutral, negative) of conversations.
- **Summarization**: Generates concise summaries of conversations using **Hugging Face Transformers**.

### 2. **Dashboard for Insights**
- **Business Overview**: Displays key insights such as common emotions, sentiment distribution, and recent conversations.
- **Search Functionality**: Allows users to search conversations by keywords, sentiment, or date.
- **Data Visualization**: Provides interactive bar charts for emotion and sentiment analysis using **Recharts**.

### 3. **User Authentication**
- **Registration and Login**: Secure user authentication with email verification.
- **Email Verification**: Ensures account authenticity by sending verification links via email.

### 4. **Database Integration**
- **Supabase**: Stores user data, conversation transcripts, sentiment scores, emotion scores, and summaries.
- **PostgreSQL**: Backend database for managing structured data.

---

## Technical Stack

### Backend
- **FastAPI**: Provides a robust and scalable REST API for the application.
- **SQLAlchemy**: ORM for database interactions.
- **Supabase**: Cloud-based PostgreSQL database for data storage.
- **SMTP**: Used for sending email verification links.

### Frontend
- **React.js**: Interactive user interface for the dashboard.
- **Recharts**: Data visualization library for displaying insights.
- **Axios**: Handles API requests to the backend.

### NLP and AI
- **Hugging Face Transformers**: Summarization and sentiment analysis models.
- **PyTorch**: Framework for running deep learning models.
- **OpenAI Whisper**: Transcription of audio files.
- **NLTK**: Tokenization and text preprocessing.

---

## Project Workflow

1. **Conversation Pipeline**:
   - Record audio conversations.
   - Transcribe audio into text.
   - Analyze emotions and sentiment.
   - Summarize the conversation.
   - Push the processed data to the database.

2. **Dashboard**:
   - Fetch and display insights from the database.
   - Allow users to explore conversations and their summaries.
   - Provide visualizations for emotion and sentiment trends.

3. **Authentication**:
   - Users register and verify their email.
   - Verified users can log in and access the dashboard.

---

## Installation and Setup

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL database
- FFMPEG (required for OpenAI Whisper)

### Backend Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/NLP_Customer_Audit_Project.git
   cd NLP_Customer_Audit_Project