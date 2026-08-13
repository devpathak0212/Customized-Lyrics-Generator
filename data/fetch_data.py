from datasets import load_dataset
import pandas as pd

dataset = load_dataset("mrYou/lyrics-dataset", split="train")

df = pd.DataFrame(dataset)
print("Columns found:", df.columns.tolist())
print(len(df))

df.to_csv("raw_lyrics.csv", index=False)