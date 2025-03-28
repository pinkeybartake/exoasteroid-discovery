import pandas as pd
import os

INPUT_FILE = "exoasteroid_output/merged_dip_metadata.csv"
PERIODICITY_FILE = "exoasteroid_output/periodicity_flags.csv"
OUTPUT_FILE = "exoasteroid_output/discovery_scores.csv"

def classify_discovery(row):
    score = 0

    # Not in ExoFOP
    if isinstance(row.get("exofop_status"), str) and "Not Found" in row["exofop_status"]:
        score += 20

    # AI label
    if row.get("predicted_label") in ["planet", "asteroid"]:
        score += 10

    # Depth
    if row.get("depth", 0) > 0.01:
        score += 10

    # Duration
    if 0.05 <= row.get("duration", 0) <= 0.15:
        score += 10

    # Brightness
    if row.get("Tmag", 99) < 12:
        score += 10

    # Periodicity flag
    if row.get("periodic") == True:
        score += 20

    # Clean dip shape (optional placeholder)
    if row.get("dip_shape", "") == "u_shaped":
        score += 10

    # Not near edge
    if not row.get("near_edge", False):
        score += 10

    # Final label
    label = "Noise"
    if score >= 70:
        label = "Likely Planet"
    elif score >= 50:
        label = "Possible Asteroid"
    elif score >= 30:
        label = "Interesting Noise"

    return pd.Series({"confidence_score": score, "discovery_label": label})

def run():
    if not os.path.exists(INPUT_FILE):
        print("❌ Missing input file.")
        return

    df = pd.read_csv(INPUT_FILE)

    # Optional: merge periodicity flags
    if os.path.exists(PERIODICITY_FILE):
        periodic_df = pd.read_csv(PERIODICITY_FILE)
        df = pd.merge(df, periodic_df, on="tic_id", how="left")
        print("🔁 Periodicity flags merged.")

    result = df.copy()
    result[["confidence_score", "discovery_label"]] = result.apply(classify_discovery, axis=1)

    result.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Discovery scores updated: {OUTPUT_FILE}")

if __name__ == "__main__":
    run()
