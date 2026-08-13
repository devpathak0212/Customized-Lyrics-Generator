import time
import pandas as pd
from sentence_transformers import SentenceTransformer

print("Loading model...")
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
model.max_seq_length = 128

df = pd.read_csv("../data/clean_lyrics.csv")
real_batch = df["lyrics_clean"].iloc[:128].tolist()

start = time.time()
embeddings = model.encode(real_batch, show_progress_bar=False, batch_size=128)
elapsed = time.time() - start

print(f"Time to embed 128 REAL lyrics: {elapsed:.2f} seconds")
print(f"Time per song: {elapsed/128:.3f} seconds")