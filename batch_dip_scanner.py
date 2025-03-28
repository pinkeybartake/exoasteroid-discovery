# Batch Dip Scanner for ExoAsteroids - Multi-TIC Processing

from lightkurve import search_lightcurve, search_targetpixelfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# === Config ===
tic_file = "tics.txt"  # one TIC ID per line
dip_threshold = 0.995
output_folder = "exoasteroid_output"
os.makedirs(output_folder, exist_ok=True)

# === Master Dip Collection ===
all_dips = []

# === Load TICs ===
with open(tic_file, "r") as f:
    tic_ids = [line.strip() for line in f if line.strip()]

for tic_id in tic_ids:
    try:
        print(f"\n🔭 Processing {tic_id}...")

        # Step 1: Download and clean light curve
        lc_collection = search_lightcurve(tic_id, author="SPOC", mission="TESS").download_all()
        lc = lc_collection.stitch().normalize().remove_outliers()

        flux = lc.flux.value
        time = lc.time.value

        # Step 2: Dip detection
        dip_events = []
        start = None
        for i in range(len(flux)):
            if flux[i] < dip_threshold:
                if start is None:
                    start = i
            else:
                if start is not None:
                    end = i
                    event = {
                        "TIC": tic_id,
                        "start_index": start,
                        "end_index": end - 1,
                        "start_time": time[start],
                        "end_time": time[end - 1],
                        "depth": 1 - np.min(flux[start:end]),
                        "duration": time[end - 1] - time[start]
                    }
                    dip_events.append(event)
                    start = None

        if not dip_events:
            print("⚠️  No dips found for this target.")
            continue

        # Save dip CSV for this TIC
        df = pd.DataFrame(dip_events)
        csv_path = os.path.join(output_folder, f"{tic_id.replace(' ', '_')}_dips.csv")
        df.to_csv(csv_path, index=False)
        print(f"✅ Saved dips to {csv_path}")

        # Save dips to master list
        all_dips.extend(dip_events)

        # Step 3: Pixel Frame
        tpf = search_targetpixelfile(tic_id, mission="TESS").download()
        first_dip = dip_events[0]
        frame_index = first_dip['start_index']
        frame = tpf.flux[frame_index]

        plt.figure(figsize=(6, 6))
        plt.imshow(frame.value, cmap='plasma', origin='lower')
        plt.colorbar(label='Flux (e⁻/s)')
        plt.title(f"{tic_id} - Pixel Frame During Dip")
        pixel_path = os.path.join(output_folder, f"{tic_id.replace(' ', '_')}_pixel_dip_frame.png")
        plt.savefig(pixel_path)
        plt.close()
        print(f"🖼️  Saved pixel image: {pixel_path}")

        # Step 4: Print ExoFOP link
        tic_num = tic_id.split()[1]
        exofop_url = f"https://exofop.ipac.caltech.edu/tess/target.php?id={tic_num}"
        print("🔗 ExoFOP:", exofop_url)

    except Exception as e:
        print(f"❌ Error processing {tic_id}: {e}")

# === Save Merged Dip CSV ===
if all_dips:
    all_dips_df = pd.DataFrame(all_dips)
    merged_path = os.path.join(output_folder, "all_dips.csv")
    all_dips_df.to_csv(merged_path, index=False)
    print(f"\n📦 Merged all dip data to: {merged_path}")
else:
    print("\n⚠️ No dips found in any targets. Try lowering the threshold or using different TICs.")
