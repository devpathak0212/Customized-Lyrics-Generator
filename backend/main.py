import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "generation"))

from huggingface_hub import snapshot_download

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "..", "vector_database", "chroma_store_v2")

if not os.path.exists(CHROMA_PATH) or not os.listdir(CHROMA_PATH):
    print("chroma_store_v2 not found locally — downloading from Hugging Face...")
    snapshot_download(
        repo_id="Casellite/lyrics-chroma-store",
        repo_type="dataset",
        local_dir=CHROMA_PATH,
    )
    print("Download complete.")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from generate import (
    load_embed_model,
    load_chroma_collection,
    load_genai_client,
    retrieve_songs,
    extract_style_profile,
    generate_final_lyrics,
    correct_and_verify_artist,
    generate_without_retrieval,
)

app = FastAPI()

# Allow the React frontend (running on a different port/domain) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load everything ONCE at startup — same idea as @st.cache_resource, just FastAPI's version
embed_model = load_embed_model()
collection = load_chroma_collection()
client = load_genai_client()


class GenerateRequest(BaseModel):
    singer: str
    mood: str
    topic: str


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.post("/generate")
def generate(req: GenerateRequest):
    try:
        corrected_singer, is_known = correct_and_verify_artist(client, req.singer.strip())

        songs = retrieve_songs(embed_model, collection, corrected_singer, req.mood.strip(), req.topic.strip())

        if songs:
            style_profile = extract_style_profile(client, corrected_singer, songs)
            lyrics = generate_final_lyrics(client, corrected_singer, req.mood.strip(), req.topic.strip(), style_profile)
            return {
                "status": "found_in_database",
                "corrected_singer": corrected_singer,
                "songs_used": [s["title"] for s in songs],
                "lyrics": lyrics,
            }
        elif is_known:
            lyrics = generate_without_retrieval(client, corrected_singer, req.mood.strip(), req.topic.strip())
            return {
                "status": "known_artist_no_database",
                "corrected_singer": corrected_singer,
                "lyrics": lyrics,
            }
        else:
            return {
                "status": "unknown_artist",
                "message": f"We couldn't recognize '{req.singer}' as a known artist. Please enter a more well-known artist name.",
            }
    except Exception as e:
        return {
            "status": "error",
            "message": "The lyric generator is temporarily busy. Please try again in a moment.",
        }