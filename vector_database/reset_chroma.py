import chromadb

client = chromadb.PersistentClient(path="./chroma_store")
client.delete_collection(name="song_lyrics")
print("Test collection cleared")