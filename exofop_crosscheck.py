import pandas as pd
import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_PATH = "exoasteroid_output/predicted_dip_labels.csv"
OUTPUT_PATH = "exoasteroid_output/predicted_dips_with_exofop_status.csv"

def check_exofop(tic_id):
    """
    Check if the given TIC ID exists in the ExoFOP-TESS database.
    """
    base_url = "https://exofop.ipac.caltech.edu/tess/target.php"
    params = {"id": tic_id.replace("TIC ", "").strip()}
    try:
        r = requests.get(base_url, params=params, timeout=10)
        content = r.text.lower()
        if "no target found" in content:
            return tic_id, "❌ Not Found"
        elif "planet name" in content or "ephemeris" in content:
            return tic_id, "✅ Known Planet"
        else:
            return tic_id, "🟡 Found (No Planet Listed)"
    except Exception as e:
        return tic_id, f"⚠️ Error: {e}"

def run():
    if not os.path.exists(INPUT_PATH):
        print(f"❌ Input file not found: {INPUT_PATH}")
        return

    df = pd.read_csv(INPUT_PATH)
    if "tic_id" not in df.columns:
        possible_cols = [col for col in df.columns if "tic" in col.lower()]
        if possible_cols:
            df.rename(columns={possible_cols[0]: "tic_id"}, inplace=True)
            print(f"ℹ️ Renamed column '{possible_cols[0]}' to 'tic_id'")
        else:
            print("❌ No TIC ID column found in input file.")
            return

    tic_ids = df["tic_id"].unique()
    print(f"🔍 Checking {len(tic_ids)} TICs against ExoFOP using parallel requests...")

    results = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_tic = {executor.submit(check_exofop, tic): tic for tic in tic_ids}
        for future in as_completed(future_to_tic):
            tic_id, status = future.result()
            print(f"{tic_id}: {status}")
            results[tic_id] = status

    df["exofop_status"] = df["tic_id"].map(results)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\n✅ ExoFOP check complete. Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    run()
