# === Auto Label Dips Based on Heuristics ===
# This script adds labels like 'asteroid', 'planet', 'noise' to dips based on rules

import pandas as pd
import os

input_csv = "exoasteroid_output/all_dips.csv"
output_csv = "exoasteroid_output/dip_labels_auto.csv"

if not os.path.exists(input_csv):
    raise FileNotFoundError("❌ all_dips.csv not found. Run the batch scanner first.")

# Load dip data
df = pd.read_csv(input_csv)
labels = []

# Rule-based labeling
for _, row in df.iterrows():
    depth = row['depth']
    duration = row['duration']

    if depth < 0.005 or duration < 0.01:
        label = 'noise'
    elif depth < 0.015 and duration < 0.06:
        label = 'asteroid'
    elif depth >= 0.015 and duration >= 0.06:
        label = 'planet'
    else:
        label = 'unknown'

    labels.append(label)

# Add and save
df['label'] = labels
df.to_csv(output_csv, index=False)

print(f"✅ Auto-labeled dips saved to: {output_csv}")
print("📌 Labels used: 'noise', 'asteroid', 'planet', 'unknown'")
