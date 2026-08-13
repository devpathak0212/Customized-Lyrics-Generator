from fastembed import TextEmbedding

print("Loading model...")
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

sample_texts = [
    "I walk in the room there's a beautiful sunshine ray",
    "He says he really loves me too"
]

embeddings = list(model.embed(sample_texts))

print("Number of embeddings:", len(embeddings))
print("Embedding dimension:", len(embeddings[0]))
print("First 5 values of first embedding:", embeddings[0][:5])