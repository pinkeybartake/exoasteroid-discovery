import pandas as pd
import matplotlib.pyplot as plt

# Load data with RA, Dec, label, and exofop_status
df = pd.read_csv("exoasteroid_output/tic_metadata.csv")

# Merge with predictions and ExoFOP status (optional)
try:
    df_pred = pd.read_csv("exoasteroid_output/predicted_dips_with_exofop_status.csv")
    if "tic_id" not in df_pred.columns:
        df_pred.rename(columns={"TIC ID": "tic_id"}, inplace=True)

    df = df.merge(df_pred[["tic_id", "predicted_label", "exofop_status"]], on="tic_id", how="left")
except Exception as e:
    print("⚠️ Could not merge prediction data:", e)

# Plot RA vs Dec with colors by label
plt.figure(figsize=(12, 6))
labels = df["predicted_label"].unique()

colors = {
    "planet": "limegreen",
    "asteroid": "orange",
    "noise": "gray"
}

for label in labels:
    subset = df[df["predicted_label"] == label]
    plt.scatter(subset["ra"], subset["dec"], label=label, alpha=0.7,
                s=30, edgecolor="k", color=colors.get(label, "blue"))

plt.gca().invert_xaxis()  # RA increases right to left on sky maps
plt.xlabel("Right Ascension (deg)")
plt.ylabel("Declination (deg)")
plt.title("🌠 TICs with AI-Predicted Dips on the Sky")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("exoasteroid_output/star_map_static.png")
plt.show()
