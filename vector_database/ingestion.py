import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

print("Loading cleaned data...")
df = pd.read_csv("../data/clean_lyrics.csv")
print(f"Loaded {len(df)} songs")

print("Loading embedding model...")
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
model.max_seq_length = 128  # caps token length for speed — plenty for style signal

client = chromadb.PersistentClient(path="./chroma_store")
collection = client.get_or_create_collection(
    name="song_lyrics",
    metadata={"hnsw:space": "cosine"}
)

batch_size = 128
for start in tqdm(range(0, len(df), batch_size), desc="Embedding + storing"):
    batch = df.iloc[start:start + batch_size]

    embeddings = model.encode(
        batch["lyrics_clean"].tolist(),
        show_progress_bar=False,
        batch_size=batch_size
    ).tolist()

    collection.upsert(
        ids=[f"{row.artist}::{row.title}::{i}" for i, row in zip(batch.index, batch.itertuples())],
        embeddings=embeddings,
        documents=batch["lyrics_clean"].tolist(),
        metadatas=[{"artist": row.artist, "title": row.title} for row in batch.itertuples()]
    )

print(f"\nDone. Total songs in collection: {collection.count()}")