import pandas as pd
import chromadb
from fastembed import TextEmbedding
from tqdm import tqdm

print("Loading cleaned data...")
df = pd.read_csv("../data/clean_lyrics.csv")
print(f"Loaded {len(df)} songs")

print("Loading fastembed model...")
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

client = chromadb.PersistentClient(path="./chroma_store_v2")
collection = client.get_or_create_collection(
    name="song_lyrics",
    metadata={"hnsw:space": "cosine"}
)

batch_size = 128
for start in tqdm(range(0, len(df), batch_size), desc="Embedding + storing"):
    batch = df.iloc[start:start + batch_size]

    embeddings = list(model.embed(batch["lyrics_clean"].tolist()))
    embeddings = [e.tolist() for e in embeddings]

    collection.upsert(
        ids=[f"{row.artist}::{row.title}::{i}" for i, row in zip(batch.index, batch.itertuples())],
        embeddings=embeddings,
        documents=batch["lyrics_clean"].tolist(),
        metadatas=[
            {"artist": row.artist, "artist_lower": row.artist.lower().strip(), "title": row.title}
            for row in batch.itertuples()
        ]
    )

print(f"\nDone. Total songs in collection: {collection.count()}")