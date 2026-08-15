import os
import json
from difflib import get_close_matches
from dotenv import load_dotenv
from google import genai
from google.genai import types
import chromadb
from fastembed import TextEmbedding

load_dotenv()

GEMINI_MODEL = "gemini-flash-lite-latest"


def load_genai_client():
    api_key = os.environ.get("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)


def load_embed_model():
    return TextEmbedding(model_name="BAAI/bge-small-en-v1.5")


def load_chroma_collection():
    chroma_client = chromadb.PersistentClient(path="../vector_database/chroma_store_v2")
    return chroma_client.get_collection("song_lyrics")


def retrieve_songs(embed_model, collection, singer, mood, topic, top_k=5):
    query_text = f"{mood} {topic}"
    query_embedding = list(embed_model.embed([query_text]))
    query_embedding = [e.tolist() for e in query_embedding]

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        where={"artist_lower": singer.lower().strip()}
    )

    if not results["documents"][0]:
        return []

    return [
        {"title": meta["title"], "lyrics": doc}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


def get_all_artists(collection):
    all_data = collection.get(include=["metadatas"])
    artists = sorted(set(m["artist"] for m in all_data["metadatas"]))
    return artists


def suggest_similar_artists(collection, singer, n=3):
    all_artists = get_all_artists(collection)
    matches = get_close_matches(singer, all_artists, n=n, cutoff=0.6)
    return matches


def correct_and_verify_artist(client, user_input):
    prompt = f"""The user typed this as a singer/artist name: "{user_input}"

Respond with ONLY a JSON object, no other text, no markdown formatting:
{{
  "corrected_name": "the most likely correctly-spelled real artist name, fixing typos/casing",
  "is_known_artist": true or false (true only if this is a genuine, real musical artist you have confidence exists)
}}"""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.1)
    )

    text = response.text.strip()
    text = text.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(text)
        return parsed.get("corrected_name", user_input), parsed.get("is_known_artist", False)
    except json.JSONDecodeError:
        return user_input, False


def extract_style_profile(client, singer, songs):
    songs_block = "\n\n".join(f"Song: {s['title']}\n{s['lyrics'][:800]}" for s in songs)

    prompt = f"""You are a music style analyst. Below are excerpts from songs by {singer}.

{songs_block}

Extract a STYLE PROFILE describing:
- Vocabulary register (simple vs. poetic, slang usage)
- Rhyme scheme and typical line length
- Recurring imagery or motifs
- Song structure tendencies
- Emotional delivery style

Output only bullet points. Do not quote lines verbatim — describe patterns in your own words."""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.4)
    )
    return response.text


def generate_final_lyrics(client, singer, mood, topic, style_profile):
    prompt = f"""Write completely ORIGINAL song lyrics in the style of {singer}, based on this style profile.
Do not copy or paraphrase any real {singer} lyrics — use the profile only for vocabulary, structure, and tone.

STYLE PROFILE:
{style_profile}

REQUEST:
- Mood: {mood}
- Topic: {topic}
- Structure: verse 1, chorus, verse 2, chorus, bridge, final chorus

WRITING RULES — follow these strictly:
- Use specific, concrete imagery (real objects, places, sensory details) instead of vague emotional statements like "my heart is breaking" or "I feel so alone."
- Avoid songwriting clichés: no "tears like rain," "burning inside," "shattered pieces," "empty inside," or similar overused phrases.
- Vary line length naturally — mix short punchy lines with longer flowing ones, don't make every line the same length.
- Give the chorus a strong, memorable hook — a specific phrase or image that anchors the whole song, not a generic emotional summary.
- Make the verses tell a specific story with concrete details (a place, an object, a moment in time) rather than staying abstract.
- Every line should sound natural if sung aloud — read it back for rhythm, not just rhyme.

Label each section (e.g. [Verse 1], [Chorus])."""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=1.1)
    )
    return response.text


def generate_without_retrieval(client, singer, mood, topic):
    prompt = f"""Write completely ORIGINAL song lyrics in the style of {singer}, based on your knowledge
of their general songwriting style, vocabulary, and themes. Do NOT copy or paraphrase any of their
real lyrics — this must be entirely original content that merely evokes their style.

REQUEST:
- Mood: {mood}
- Topic: {topic}
- Structure: verse 1, chorus, verse 2, chorus, bridge, final chorus

WRITING RULES:
- Use specific, concrete imagery instead of vague emotional statements.
- Avoid songwriting clichés.
- Vary line length naturally.
- Give the chorus a strong, memorable hook.
- Tell a specific story with concrete details in the verses.

Label each section (e.g. [Verse 1], [Chorus])."""

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(temperature=1.1)
    )
    return response.text


if __name__ == "__main__":
    embed_model = load_embed_model()
    collection = load_chroma_collection()
    client = load_genai_client()

    singer = "Taylor Swift"
    mood = "heartbroken"
    topic = "long distance love that faded"

    print("Retrieving songs...")
    songs = retrieve_songs(embed_model, collection, singer, mood, topic)
    print(f"Retrieved {len(songs)} songs: {[s['title'] for s in songs]}\n")

    print("Extracting style profile...")
    style_profile = extract_style_profile(client, singer, songs)
    print(style_profile)
    print("\n" + "=" * 50 + "\n")

    print("Generating final lyrics...")
    lyrics = generate_final_lyrics(client, singer, mood, topic, style_profile)
    print(lyrics)