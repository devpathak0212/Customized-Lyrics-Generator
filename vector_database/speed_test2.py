import time
import pandas as pd
from sentence_transformers import SentenceTransformer

print("Loading model...")
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
print("Model loaded.")

df = pd.read_csv("../data/clean_lyrics.csv")
real_batch = df["lyrics_clean"].iloc[:64].tolist()

avg_words = sum(len(t.split()) for t in real_batch) / len(real_batch)
print(f"Average words per lyric in this batch: {avg_words:.0f}")

start = time.time()
embeddings = model.encode(real_batch, show_progress_bar=False)
elapsed = time.time() - start

print(f"Time to embed 64 REAL lyrics: {elapsed:.2f} seconds")