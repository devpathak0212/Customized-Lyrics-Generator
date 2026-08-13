from sentence_transformers import SentenceTransformer

print("Loading nomic-embed-text (first run downloads it, ~500MB, may take a minute)...")
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)

sample_texts = [
    "I walk in the room there's a beautiful sunshine ray",
    "He says he really loves me too"
]

embeddings = model.encode(sample_texts)

print("Number of embeddings:", len(embeddings))
print("Embedding dimension:", len(embeddings[0]))
print("First 5 values of first embedding:", embeddings[0][:5])