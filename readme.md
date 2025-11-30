# Sadeem RAG Chatbot with 5-Emotion AI

A Flask-based REST API backend and Next.js frontend for the Sadeem customer support chatbot, featuring **5-Emotion Sentiment Analysis** and **Adaptive Response Logic**.

## 🌟 New Features (v5.0)

- **5-Emotion Detection**: Classifies user messages into:
  - 😊 **Happy**: Positive, satisfied, grateful
  - 😐 **Neutral**: Calm, informational, factual
  - 😕 **Confused**: Uncertain, seeking clarification
  - 😠 **Frustrated**: Angry, annoyed, impatient
  - 😢 **Sad**: Disappointed, upset, discouraged

- **Adaptive Response Logic**: The bot adjusts its tone and content based on your emotion:
  - **Happy** → Upbeat, concise, friendly
  - **Neutral** → Professional, clear, direct
  - **Confused** → Step-by-step explanations, clarifying questions
  - **Frustrated** → Empathetic, solution-focused, escalation options
  - **Sad** → Supportive, encouraging, gentle

- **Real-time Analytics**: Live visualization of emotion distribution in the sidebar.
- **Enhanced UI**: Dark-themed, modern interface with emotion indicators.

## Tech Stack

- **Backend**: Flask, ChromaDB, Hugging Face Transformers, Google Gemini API
- **Frontend**: Next.js 15, React 19, Tailwind CSS, Lucide Icons
- **AI Models**: 
  - Emotion: `j-hartmann/emotion-english-distilroberta-base`
  - RAG Embeddings: `all-MiniLM-L6-v2`
  - Response Generation: `gemini-1.5-flash`

## Quick Start

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Add your GOOGLE_API_KEY to .env
python app.py
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 3. Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

## API Endpoints

- `POST /api/chat/message`: Send message (returns emotion data)
- `GET /api/analytics/emotions`: Get emotion statistics
- `GET /api/analytics/recent`: Get recent conversation logs

## Analytics

Conversation logs are stored in `backend/analytics.jsonl`. You can view real-time stats in the chatbot sidebar.