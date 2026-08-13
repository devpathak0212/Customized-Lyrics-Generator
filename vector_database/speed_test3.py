import time
import pandas as pd
from sentence_transformers import SentenceTransformer

print("Loading model...")
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)

model.max_seq_length = 128  # caps how many tokens the model processes per text
print("Max sequence length set to:", model.max_seq_length)

df = pd.read_csv("../data/clean_lyrics.csv")
real_batch = df["lyrics_clean"].iloc[:64].tolist()

start = time.time()
embeddings = model.encode(real_batch, show_progress_bar=False)
elapsed = time.time() - start

print(f"Time to embed 64 REAL lyrics (capped at 128 tokens): {elapsed:.2f} seconds")