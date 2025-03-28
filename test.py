import pandas as pd

scores_df = pd.read_csv("exoasteroid_output/discovery_scores.csv")
metadata_df = pd.read_csv("exoasteroid_output/tic_metadata.csv")

print("\n📄 Columns in discovery_scores.csv:")
print(scores_df.columns)

print("\n📄 Columns in tic_metadata.csv:")
print(metadata_df.columns)
