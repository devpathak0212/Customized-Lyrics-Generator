import chromadb

client = chromadb.PersistentClient(path="./chroma_store")

collection = client.get_or_create_collection(name="song_lyrics")

# insert 3 dummy test rows just to prove read/write works
collection.add(
    ids=["test1", "test2", "test3"],
    documents=[
        "This is a test lyric about sunshine and love",
        "This is a test lyric about heartbreak and rain",
        "This is a test lyric about dancing all night"
    ],
    metadatas=[
        {"artist": "Test Artist A"},
        {"artist": "Test Artist B"},
        {"artist": "Test Artist A"}
    ]
)

print("Collection count:", collection.count())

results = collection.query(
    query_texts=["a sad song about rain"],
    n_results=2
)
print("\nQuery results:")
print(results["documents"])
print(results["metadatas"])