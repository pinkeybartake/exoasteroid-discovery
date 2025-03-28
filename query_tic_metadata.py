from astroquery.mast import Catalogs
import pandas as pd
import os
import time

INPUT_FILE = "exoasteroid_output/predicted_dips_with_exofop_status.csv"
OUTPUT_FILE = "exoasteroid_output/tic_metadata.csv"

def query_tic_metadata(tic_id):
    try:
        cleaned = tic_id.replace("TIC", "").strip()
        catalog_data = Catalogs.query_object(f"TIC {cleaned}", catalog="TIC")
        if len(catalog_data) > 0:
            row = dict(catalog_data[0])
            row["tic_id"] = f"TIC {cleaned}"
            return row
    except Exception as e:
        print(f"⚠️ Failed for {tic_id}: {e}")
    return None

def run():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)

    if "tic_id" not in df.columns:
        possible = [col for col in df.columns if "tic" in col.lower()]
        if possible:
            df.rename(columns={possible[0]: "tic_id"}, inplace=True)
        else:
            print("❌ 'tic_id' column missing.")
            return

    results = []
    for tic_id in df["tic_id"].unique():
        print(f"🔍 Querying {tic_id}...")
        meta = query_tic_metadata(tic_id)
        if meta:
            results.append(meta)
        time.sleep(1)

    if results:
        pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
        print(f"\n✅ Metadata saved to: {OUTPUT_FILE}")
    else:
        print("❌ No TIC metadata fetched.")

if __name__ == "__main__":
    run()
