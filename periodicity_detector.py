import pandas as pd
from lightkurve import search_lightcurve
from astropy.timeseries import LombScargle
import os
import lightkurve as lk
lk.conf.cache_location = "C:/Users/pinke/.lightkurve/cache"  # optional if needed



INPUT_FILE = "exoasteroid_output/predicted_dip_labels.csv"  
OUTPUT_FILE = "exoasteroid_output/periodicity_flags.csv"

def detect_periodicity(tic_id):
    tic_number = tic_id.replace("TIC", "").strip()
    try:
        # Search and download light curve
        search_result = search_lightcurve(f"TIC {tic_number}", mission="TESS")
        lc = search_result.download_all().stitch().remove_nans().normalize().flatten()

        # Use Lomb-Scargle to detect periodic signals
        ls = LombScargle(lc.time.value, lc.flux.value)
        period = ls.autopower(nyquist_factor=2)[0]
        peak_power = max(ls.autopower(nyquist_factor=2)[1])

        # Simple threshold for periodicity
        is_periodic = peak_power > 0.1  # You can tune this
        return {"tic_id": tic_id, "periodic": is_periodic, "peak_power": peak_power}
    except Exception as e:
        print(f"⚠️ {tic_id} - Error: {e}")
        return {"tic_id": tic_id, "periodic": False, "peak_power": 0}

def run():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Input file not found: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)
    if "tic_id" not in df.columns:
        tic_col = [c for c in df.columns if "tic" in c.lower()]
        if tic_col:
            df.rename(columns={tic_col[0]: "tic_id"}, inplace=True)
        else:
            print("❌ No TIC column found.")
            return

    results = []
    for tic_id in df["tic_id"].unique():
        print(f"🔍 Checking periodicity for {tic_id}...")
        result = detect_periodicity(tic_id)
        results.append(result)

    out_df = pd.DataFrame(results)
    out_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\n✅ Periodicity flags saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    run()
