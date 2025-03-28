import pandas as pd
import numpy as np

INPUT_FILE = "exoasteroid_output/merged_dip_metadata.csv"
OUTPUT_FILE = "exoasteroid_output/discovery_scores_with_radius.csv"
R_SUN_KM = 695700  # Solar radius in kilometers

def calculate_object_radius_km(depth, star_radius_rsun):
    if pd.isna(depth) or pd.isna(star_radius_rsun) or depth <= 0:
        return np.nan
    return R_SUN_KM * star_radius_rsun * np.sqrt(depth)

def run():
    print(f"📂 Loading: {INPUT_FILE}")
    df = pd.read_csv(INPUT_FILE)

    if "dip_depth" not in df.columns or "star_radius_rsun" not in df.columns:
        print("❌ Required columns 'dip_depth' or 'star_radius_rsun' missing.")
        return

    print("📏 Calculating object radius...")
    df["object_radius_km"] = df.apply(
        lambda row: calculate_object_radius_km(row["dip_depth"], row["star_radius_rsun"]),
        axis=1
    )

    print("💾 Saving with radius estimate...")
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Done: {OUTPUT_FILE}")

if __name__ == "__main__":
    run()
