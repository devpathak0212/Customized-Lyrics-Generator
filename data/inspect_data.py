import pandas as pd

df = pd.read_csv("raw_lyrics.csv")

print("Total rows:", len(df))
print("\nMissing values per column:")
print(df[["title", "artist", "lyrics"]].isna().sum())

print("\nLanguage breakdown (top 5):")
print(df["language"].value_counts().head())

print("\nSample lyrics (first 500 chars) for Taylor Swift:")
sample = df[df["artist"] == "Taylor Swift"].iloc[0]
print("Title:", sample["title"])
print(sample["lyrics"][:500])