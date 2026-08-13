import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "generation"))

import streamlit as st
from generate import (
    load_embed_model,
    load_chroma_collection,
    load_genai_client,
    retrieve_songs,
    extract_style_profile,
    generate_final_lyrics,
    correct_and_verify_artist,
    generate_without_retrieval,
)

st.set_page_config(page_title="Lyrics Generator", page_icon="🎵", layout="centered")


@st.cache_resource
def get_embed_model():
    return load_embed_model()


@st.cache_resource
def get_chroma_collection():
    return load_chroma_collection()


@st.cache_resource
def get_genai_client():
    return load_genai_client()


with st.spinner("Warming up the model — this takes about a minute on first load, then stays fast..."):
    embed_model = get_embed_model()
    collection = get_chroma_collection()
    client = get_genai_client()

st.markdown("""
<style>
    .main { padding-top: 2rem; }
    h1 { font-size: 2.2rem !important; margin-bottom: 0 !important; }
    .subtitle { color: #888; margin-bottom: 2rem; }
    .song-tag {
        display: inline-block;
        background: #f0f0f5;
        color: #333;
        padding: 4px 12px;
        border-radius: 14px;
        font-size: 0.85rem;
        margin: 3px 4px 3px 0;
    }
    .lyrics-box {
        background: #fafafa;
        border-radius: 12px;
        padding: 24px;
        white-space: pre-wrap;
        line-height: 1.7;
        font-size: 1.02rem;
        border: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎵 Lyrics Generator")
st.markdown('<p class="subtitle">Generate original lyrics in the style of an artist from our database</p>', unsafe_allow_html=True)

with st.form("lyrics_form"):
    col1, col2 = st.columns(2)
    with col1:
        singer = st.text_input("Singer name", placeholder="e.g. Taylor Swift")
    with col2:
        mood = st.text_input("Mood", placeholder="e.g. heartbroken, hopeful")
    topic = st.text_input("Topic", placeholder="e.g. long distance love")
    submitted = st.form_submit_button("✨ Generate", use_container_width=True)

if submitted:
    if not singer or not mood or not topic:
        st.warning("Please fill in all three fields.")
    else:
        with st.spinner("Checking artist name..."):
            corrected_singer, is_known = correct_and_verify_artist(client, singer.strip())

        with st.spinner("Finding songs..."):
            songs = retrieve_songs(embed_model, collection, corrected_singer, mood.strip(), topic.strip())

        if songs:
            if corrected_singer.lower() != singer.strip().lower():
                st.caption(f"Showing results for **{corrected_singer}**")

            song_count = len(songs)
            tags_html = "".join(f'<span class="song-tag">{s["title"]}</span>' for s in songs)
            st.markdown(
                f'<p style="color:#666; font-size:0.9rem; margin-bottom:6px;">Inspired by {song_count} {corrected_singer} songs:</p>{tags_html}',
                unsafe_allow_html=True
            )

            with st.spinner("Analyzing style..."):
                style_profile = extract_style_profile(client, corrected_singer, songs)

            with st.spinner("Writing lyrics..."):
                lyrics = generate_final_lyrics(client, corrected_singer, mood.strip(), topic.strip(), style_profile)

            st.markdown("### Generated Lyrics")
            st.markdown(f'<div class="lyrics-box">{lyrics}</div>', unsafe_allow_html=True)

        elif is_known:
            st.info(f"**{corrected_singer}** isn't in our song database yet, so these lyrics are generated from general style knowledge rather than specific song references.")

            with st.spinner("Writing lyrics..."):
                lyrics = generate_without_retrieval(client, corrected_singer, mood.strip(), topic.strip())

            st.markdown("### Generated Lyrics")
            st.markdown(f'<div class="lyrics-box">{lyrics}</div>', unsafe_allow_html=True)

        else:
            st.error(f"We couldn't recognize '{singer}' as a known artist. Please enter a more well-known artist name.")