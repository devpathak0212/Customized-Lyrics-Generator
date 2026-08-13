import re
import pandas as pd

df = pd.read_csv("raw_lyrics.csv")

# drop rows with missing title or lyrics
before = len(df)
df = df.dropna(subset=["title", "artist", "lyrics"])
print(f"Dropped {before - len(df)} rows with missing values")

def clean_lyrics(text):
    text = re.sub(r"\[.*?\]", "", text)      # remove [Verse One], [Chorus] etc.
    text = re.sub(r"\s+", " ", text).strip() # collapse extra whitespace/newlines
    return text

df["lyrics_clean"] = df["lyrics"].apply(clean_lyrics)

# drop anything that's suspiciously short after cleaning (likely broken/empty entries)
before = len(df)
df = df[df["lyrics_clean"].str.len() > 50]
print(f"Dropped {before - len(df)} rows with very short lyrics")

# drop exact duplicate songs (same artist + title)
before = len(df)
df = df.drop_duplicates(subset=["artist", "title"])
print(f"Dropped {before - len(df)} duplicate rows")

print(f"\nFinal row count: {len(df)}")

# sanity check on the same Taylor Swift song from before
sample = df[df["artist"] == "Taylor Swift"].iloc[0]
print("\nCleaned sample:")
print(sample["lyrics_clean"][:500])

df.to_csv("clean_lyrics.csv", index=False)
print("\nSaved to clean_lyrics.csv")