import os
import uvicorn
import pandas as pd
import numpy as np
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
 
app = FastAPI()
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
try:
    print("Loading SentenceTransformer model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    raise e
 
API_KEY = os.environ.get("YOUTUBE_API_KEY", "AIzaSyAuPiFnbTL1911kG2Lv7d5jAZ6kvmMYsIs")
 
def get_youtube_service():
    if API_KEY == "YOUR_YOUTUBE_API_KEY":
        raise HTTPException(
            status_code=500,
            detail="YouTube API Key is missing. Please set YOUTUBE_API_KEY environment variable or update the code."
        )
    return build("youtube", "v3", developerKey=API_KEY)
 
def get_videos(search_query, max_results=10):
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
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            videos.append({
                "video_id": video_id,
                "title": snippet["title"],
                "description": snippet["description"],
                "thumbnail": snippet["thumbnails"]["high"]["url"]
                if "high" in snippet["thumbnails"]
                else snippet["thumbnails"]["default"]["url"]
            })
        return videos
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return []
 
def get_transcripts(videos):
    updated_videos = []
    for video in videos:
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video["video_id"])
            transcript_text = " ".join([t["text"] for t in transcript_list])
            video["transcript"] = transcript_text
        except Exception:
            video["transcript"] = ""
        updated_videos.append(video)
    return updated_videos
 
@app.get("/search")
def semantic_search(query: str = Query(..., description="The search query")):
    videos = get_videos(query, max_results=10)
 
    if not videos:
        return {"results": []}
 
    videos_with_transcripts = get_transcripts(videos)
    df = pd.DataFrame(videos_with_transcripts)
 
    df["combined_text"] = df["title"] + " " + df["transcript"]
    df["combined_text"].fillna("", inplace=True)
 
    embeddings = model.encode(df["combined_text"].tolist())
    query_embedding = model.encode(query)
 
    similarity_scores = cosine_similarity(
        query_embedding.reshape(1, -1),
        embeddings
    )[0]
 
    df["score"] = similarity_scores
    results_df = df.sort_values(by="score", ascending=False)
 
    api_results = results_df[
        ["title", "description", "thumbnail", "video_id", "score"]
    ].to_dict(orient="records")
 
    return {"results": api_results}
 
app.mount("/", StaticFiles(directory=".", html=True), name="static")
 
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
