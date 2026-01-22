import os
import uvicorn
import pandas as pd
from pathlib import Path

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# -------------------- APP SETUP --------------------
app = FastAPI(title="AI QueryTube")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- LOAD MODEL --------------------
try:
    print("Loading SentenceTransformer model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Model loaded successfully.")
except Exception as e:
    print(f"Model loading failed: {e}")
    raise e

# -------------------- ENV VARIABLE --------------------
API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_youtube_service():
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="YOUTUBE_API_KEY not found. Please set it as an environment variable."
        )
    return build("youtube", "v3", developerKey=API_KEY)

# -------------------- YOUTUBE SEARCH --------------------
def get_videos(search_query: str, max_results: int = 10):
    try:
        youtube = get_youtube_service()
        response = youtube.search().list(
            q=search_query,
            part="id,snippet",
            type="video",
            maxResults=max_results
        ).execute()

        videos = []
        for item in response.get("items", []):
            snippet = item["snippet"]
            videos.append({
                "video_id": item["id"]["videoId"],
                "title": snippet["title"],
                "description": snippet["description"],
                "thumbnail": snippet["thumbnails"]["high"]["url"]
                if "high" in snippet["thumbnails"]
                else snippet["thumbnails"]["default"]["url"]
            })
        return videos

    except Exception as e:
        print(f"YouTube search error: {e}")
        return []

# -------------------- TRANSCRIPTS --------------------
def get_transcripts(videos):
    for video in videos:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video["video_id"])
            video["transcript"] = " ".join([t["text"] for t in transcript])
        except Exception:
            video["transcript"] = ""
    return videos

# -------------------- API ENDPOINT --------------------
@app.get("/search")
def semantic_search(query: str = Query(..., description="Search query")):
    videos = get_videos(query)

    if not videos:
        return {"results": []}

    videos = get_transcripts(videos)
    df = pd.DataFrame(videos)

    df["combined_text"] = (df["title"] + " " + df["transcript"]).fillna("")

    embeddings = model.encode(df["combined_text"].tolist())
    query_embedding = model.encode(query)

    scores = cosine_similarity(
        query_embedding.reshape(1, -1),
        embeddings
    )[0]

    df["score"] = scores
    df = df.sort_values(by="score", ascending=False)

    results = df[
        ["title", "description", "thumbnail", "video_id", "score"]
    ].to_dict(orient="records")

    return {"results": results}

# -------------------- STATIC FILES --------------------
BASE_DIR = Path(__file__).resolve().parent
app.mount("/", StaticFiles(directory=BASE_DIR, html=True), name="static")

# -------------------- RUN SERVER --------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
