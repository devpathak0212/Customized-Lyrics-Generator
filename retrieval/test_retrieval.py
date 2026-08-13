import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
model.max_seq_length = 128

client = chromadb.PersistentClient(path="../vector_database/chroma_store")
collection = client.get_collection("song_lyrics")

singer = "Taylor Swift"
mood_query = "heartbreak and sadness after a breakup"

query_embedding = model.encode([mood_query]).tolist()

results = collection.query(
    query_embeddings=query_embedding,
    n_results=5,
    where={"artist": singer}
)

print(f"Query: '{mood_query}' filtered to artist='{singer}'\n")
for i, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
    print(f"{i+1}. {meta['title']}")
    print(f"   {doc[:150]}...\n")