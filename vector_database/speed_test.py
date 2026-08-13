import time
from sentence_transformers import SentenceTransformer

print("Loading model...")
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
print("Model loaded.")

sample_texts = ["This is a test lyric about sunshine and love"] * 64

start = time.time()
embeddings = model.encode(sample_texts, show_progress_bar=False)
elapsed = time.time() - start

print(f"Time to embed 64 texts: {elapsed:.2f} seconds")