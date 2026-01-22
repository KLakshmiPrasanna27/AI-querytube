🎥 AI-QueryTube – AI Powered YouTube Search Engine

AI-QueryTube is an AI-powered web application that enables users to search YouTube videos using natural language queries.
It leverages semantic search with Sentence Transformers to return the most relevant videos instead of simple keyword matching.

🚀 Features

🔍 Semantic search over YouTube videos

🧠 AI-based relevance ranking using sentence embeddings

📄 Automatic YouTube transcript extraction

⚡ FastAPI backend for high-performance APIs

🌐 Simple and responsive frontend (HTML, CSS, JavaScript)

🔗 YouTube Data API integration

🛠️ Tech Stack
Backend

Python

FastAPI

Sentence Transformers

Scikit-learn

YouTube Transcript API

YouTube Data API

Frontend

HTML

CSS

JavaScript

📂 Project Structure
AI-QueryTube/
│
├── main.py              # FastAPI backend logic
├── index.html           # Frontend UI
├── style.css            # Styling
├── script.js            # Frontend functionality
├── AI-QueryTube AI.pdf  # Project documentation
└── README.md            # Project overview

⚙️ How It Works

User enters a natural language query

Backend fetches YouTube video transcripts

Transcripts are converted into embeddings

Query embedding is compared using cosine similarity

Most relevant videos are returned to the user

▶️ How to Run the Project Locally
1️⃣ Clone the repository
git clone https://github.com/KLakshmiPrasanna27/AI-QueryTube.git
cd AI-QueryTube

2️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the FastAPI server
uvicorn main:app --reload

5️⃣ Open in browser
http://127.0.0.1:8000

🔐 API Configuration

Generate a YouTube Data API Key

Add it to your environment variables or directly in main.py

YOUTUBE_API_KEY = "your_api_key_here"
