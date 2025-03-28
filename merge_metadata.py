import pandas as pd

SCORES_FILE = "exoasteroid_output/discovery_scores.csv"
METADATA_FILE = "exoasteroid_output/tic_metadata.csv"
MERGED_FILE = "exoasteroid_output/merged_dip_metadata.csv"

def run():
    print("📂 Loading discovery scores...")
    scores_df = pd.read_csv(SCORES_FILE)

    print("📂 Loading TIC metadata...")
    metadata_df = pd.read_csv(METADATA_FILE)

    # Use actual radius column: 'rad' -> 'star_radius_rsun'
    if "rad" in metadata_df.columns:
        metadata_df = metadata_df.rename(columns={"rad": "star_radius_rsun"})

    print("🔗 Merging on 'tic_id'...")
    merged_df = pd.merge(scores_df, metadata_df, on="tic_id", how="left")

    if "depth" not in merged_df.columns or "star_radius_rsun" not in merged_df.columns:
        print("❌ Required columns 'depth' or 'star_radius_rsun' missing after merge.")
        return

    # Rename depth to match what radius estimation expects
    merged_df = merged_df.rename(columns={"depth": "dip_depth"})

    print("💾 Saving merged metadata...")
    merged_df.to_csv(MERGED_FILE, index=False)
    print(f"✅ Merged CSV saved to: {MERGED_FILE}")

if __name__ == "__main__":
    run()
