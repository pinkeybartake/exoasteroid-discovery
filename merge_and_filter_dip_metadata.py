import pandas as pd
import os

DIPS_FILE = "exoasteroid_output/predicted_dips_with_exofop_status.csv"
META_FILE = "exoasteroid_output/tic_metadata.csv"
MERGED_OUTPUT = "exoasteroid_output/merged_dip_metadata.csv"
BRIGHT_OUTPUT = "exoasteroid_output/bright_dip_candidates.csv"

def run():
    if not os.path.exists(DIPS_FILE) or not os.path.exists(META_FILE):
        print("❌ Missing input files. Please run prediction + metadata scripts first.")
        return

    df_dips = pd.read_csv(DIPS_FILE)
    df_meta = pd.read_csv(META_FILE)

    # Normalize columns if needed
    if "tic_id" not in df_dips.columns:
        df_dips.rename(columns={col: "tic_id" for col in df_dips.columns if "tic" in col.lower()}, inplace=True)

    if "tic_id" not in df_meta.columns:
        df_meta.rename(columns={col: "tic_id" for col in df_meta.columns if "tic" in col.lower()}, inplace=True)

    # Merge on TIC ID
    merged = pd.merge(df_dips, df_meta, on="tic_id", how="left")

    # Save full merged dataset
    merged.to_csv(MERGED_OUTPUT, index=False)
    print(f"✅ Merged file saved to: {MERGED_OUTPUT}")

    # Filter bright candidates (Tmag < 12)
    bright = merged[merged["Tmag"] < 12]
    bright.to_csv(BRIGHT_OUTPUT, index=False)
    print(f"🌟 Bright candidate file saved to: {BRIGHT_OUTPUT} ({len(bright)} stars)")

if __name__ == "__main__":
    run()
