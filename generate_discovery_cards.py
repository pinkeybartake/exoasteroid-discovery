import pandas as pd
import os

INPUT_FILE = "exoasteroid_output/discovery_scores.csv"
REPORT_FOLDER = "reports"

def create_card(row):
    tic_id = row.get("tic_id", "Unknown")
    filename = os.path.join(REPORT_FOLDER, f"{tic_id.replace(' ', '_')}_discovery_card.md")

    content = f"""# 🪐 Discovery Card: {tic_id}

**Confidence Score:** {row.get("confidence_score", 0)}  
**Label:** {row.get("discovery_label", "Unknown")}  
**AI Prediction:** {row.get("predicted_label", "N/A")}  
**ExoFOP Status:** {row.get("exofop_status", "N/A")}  
**Periodic:** {'✅ Yes' if row.get("periodic", False) else '❌ No'}  

---

### 📍 Target Info
- **RA:** {row.get("ra", 'N/A')}
- **Dec:** {row.get("dec", 'N/A')}
- **TESS Magnitude:** {row.get("Tmag", 'N/A')}
- **Star Radius (R☉):** {row.get("rad", 'N/A')}
- **Temperature (K):** {row.get("Teff", 'N/A')}

---

### 📉 Dip Properties
- **Dip Depth:** {row.get("depth", 'N/A')}
- **Duration (days):** {row.get("duration", 'N/A')}
- **Estimated Radius (km):** {row.get("estimated_radius_km", 'Pending')}

---

### 🛠️ Notes:
- Light curve and pixel data available in dashboard.
- Consider follow-up if score > 70 and star is bright (Tmag < 12).
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Generated card: {filename}")

def run():
    if not os.path.exists(INPUT_FILE):
        print("❌ discovery_scores.csv not found.")
        return

    if not os.path.exists(REPORT_FOLDER):
        os.makedirs(REPORT_FOLDER)

    df = pd.read_csv(INPUT_FILE)

    # Filter top candidates
    top = df[df["confidence_score"] >= 50]

    for _, row in top.iterrows():
        create_card(row)

    print(f"\n📝 All discovery cards saved in: {REPORT_FOLDER}")

if __name__ == "__main__":
    run()
