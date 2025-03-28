import os
import matplotlib.pyplot as plt
from lightkurve import search_targetpixelfile
import pandas as pd
import shutil

INPUT_FILE = "exoasteroid_output/discovery_scores.csv"
OUTPUT_DIR = "pixel_frames"

# Ensure output folder exists
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def clean_cache_path(tic_id):
    """Remove corrupted FITS cache if exists."""
    tic_num = tic_id.replace("TIC", "").strip()
    cache_root = os.path.expanduser("~/.lightkurve/cache/mastDownload/TESS")
    if not os.path.exists(cache_root):
        return
    for root, dirs, _ in os.walk(cache_root):
        for d in dirs:
            if tic_num in d:
                corrupted_path = os.path.join(root, d)
                print(f"🧹 Removing corrupted cache: {corrupted_path}")
                shutil.rmtree(corrupted_path, ignore_errors=True)
                return

def plot_pixel_frame(tic_id):
    cleaned = tic_id.replace("TIC", "").strip()
    print(f"\n🔍 Processing {tic_id}...")

    try:
        clean_cache_path(tic_id)

        tpf_list = search_targetpixelfile(f"TIC {cleaned}", mission="TESS").download_all()
        if not tpf_list or len(tpf_list) == 0:
            print(f"⚠️ No TPFs found for {tic_id}")
            return

        tpf = None
        for candidate in tpf_list:
            if len(candidate) > 0:
                tpf = candidate
                break

        if tpf is None:
            print(f"⚠️ No usable TPFs for {tic_id}")
            return

        print(f"🧪 TPF shape: {tpf.shape}, Frames: {len(tpf)}")

        try:
            lc = tpf.to_lightcurve().remove_nans().normalize()
        except Exception as e:
            print(f"⚠️ Light curve failed: {e}")
            return

        if len(lc.flux) < 3:
            print(f"⚠️ Not enough flux points for dip detection")
            return

        dip_idx = lc.flux.argmin()
        print(f"🔽 Dip Index: {dip_idx}")

        before_idx = max(0, dip_idx - 1)
        after_idx = min(len(lc.flux) - 1, dip_idx + 1)

        fig, axes = plt.subplots(1, 3, figsize=(12, 4))
        for i, (idx, label) in enumerate(zip([before_idx, dip_idx, after_idx], ["Before Dip", "During Dip", "After Dip"])):
            try:
                frame = tpf[idx]
                if hasattr(frame, 'flux') and frame.flux is not None:
                    frame.plot(ax=axes[i], title=label, show_colorbar=False)
                else:
                    raise ValueError("Frame has no flux")
            except Exception:
                axes[i].text(0.5, 0.5, "Frame Unavailable", ha='center', va='center')
                axes[i].set_title(label)
            axes[i].set_xlabel("")

        fig.suptitle(f"TIC {cleaned} - Pixel Frame Dip Comparison", fontsize=14)
        plt.tight_layout()
        output_path = os.path.join(OUTPUT_DIR, f"{tic_id.replace(' ', '_')}_pixel_dip_frame.png")
        plt.savefig(output_path)
        plt.close()
        print(f"✅ Pixel image saved: {output_path}")

    except Exception as e:
        print(f"❌ {tic_id} - General error: {e}")

def run():
    print("📁 Loading discovery scores...")
    if not os.path.exists(INPUT_FILE):
        print("❌ discovery_scores.csv not found.")
        return

    df = pd.read_csv(INPUT_FILE)
    tics = df[df["confidence_score"] >= 50]["tic_id"].dropna().unique()

    print(f"🔭 Found {len(tics)} candidates:")
    for tic in tics:
        plot_pixel_frame(tic)

if __name__ == "__main__":
    run()
