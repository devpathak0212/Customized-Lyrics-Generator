# The Songwriter's Archive

A RAG-based lyrics generator that writes original songs in the style of a chosen artist. Give it a singer, a mood, and a topic — it retrieves real reference tracks from a database of ~30,000 songs, extracts a style profile from them, and generates brand-new lyrics that evoke that artist's voice without copying their actual lines.

**Live demo:** [customized-lyrics-generator.vercel.app](https://customized-lyrics-generator.vercel.app)

---

## How it works

1. **Retrieve** — the user's mood/topic is embedded and matched against songs by the requested artist in a vector database
2. **Analyze** — an LLM call extracts a style profile from the retrieved songs (vocabulary, rhyme scheme, imagery, structure) without quoting them directly
3. **Generate** — a second LLM call writes fully original lyrics using that style profile plus the user's requested mood and topic

If the requested artist isn't in the database but is a real, recognized artist, the system falls back to generating from general style knowledge instead of reference tracks. If the artist can't be recognized at all, the user is asked to try a better-known name. Artist name typos and casing are automatically corrected before lookup.

---

## Tech stack

| Layer | Technology |
|---|---|
| Dataset | [mrYou/lyrics-dataset](https://huggingface.co/datasets/mrYou/lyrics-dataset) (~30k songs, Hugging Face) |
| Embeddings | [fastembed](https://github.com/qdrant/fastembed) running `BAAI/bge-small-en-v1.5` |
| Vector database | [ChromaDB](https://www.trychroma.com/) |
| LLM | Google Gemini (`gemini-flash-lite-latest`) via the `google-genai` SDK |
| Backend | FastAPI |
| Frontend | React (Vite) |
| Backend hosting | [Render](https://render.com) (free tier) |
| Frontend hosting | [Vercel](https://vercel.com) (free tier) |
| Vector store hosting | [Hugging Face Datasets](https://huggingface.co/datasets) (auto-downloaded at backend startup) |

Chosen to run entirely on free tiers with no ongoing cost. The embedding model runs locally/on-server (no API costs), and Gemini's free tier covers generation.

---

## Project structure

```
.
├── data/
│   ├── fetch_data.py         # downloads the raw dataset
│   ├── clean_data.py         # strips section tags, dedupes, cleans text
│   └── clean_lyrics.csv      # cleaned dataset (not tracked in git)
├── vector_database/
│   └── ingestion_v2.py       # embeds all songs and builds the Chroma collection
├── generation/
│   └── generate.py           # retrieval + style extraction + generation pipeline
├── backend/
│   ├── main.py                # FastAPI app, downloads chroma_store_v2 at startup if missing
│   └── requirements.txt
├── frontend-react/
│   └── src/
│       ├── App.jsx
│       └── App.css
└── requirements.txt
```

---

## Running locally

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the project root:
```
GEMINI_API_KEY=your_key_here
```
Get a free key at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

Start the server:
```bash
uvicorn main:app --reload
```

The first run will automatically download the vector database (`chroma_store_v2`) from Hugging Face if it isn't already present locally.

### 2. Frontend

```bash
cd frontend-react
npm install
npm run dev
```

By default the frontend points at the deployed Render backend. To point it at your local backend instead, change `API_URL` in `src/App.jsx` to `http://localhost:8000`.

### 3. Rebuilding the dataset (optional)

Only needed if you want to re-embed the songs from scratch:
```bash
cd data
python fetch_data.py
python clean_data.py
cd ../vector_database
python ingestion_v2.py
```

---

## Notes

- Generated lyrics are checked against a strict prompt instructing the model to produce fully original content and never quote or closely paraphrase real lyrics from the reference tracks.
- Gemini's free tier occasionally returns temporary `503` errors under high demand; the backend catches these and returns a clean error message rather than failing silently.
- The vector database (`chroma_store_v2`) is too large for GitHub's file size limits, so it's hosted separately as a Hugging Face dataset and pulled automatically when the backend starts.

---

## License

Personal project, built for learning purposes.
