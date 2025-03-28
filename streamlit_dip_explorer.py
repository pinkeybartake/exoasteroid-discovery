import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import io

st.set_page_config(page_title="🪐 ExoAsteroid Explorer", layout="wide")
st.title("🔭 ExoAsteroid Dip Discovery Dashboard")

# === Load merged data ===
DATA_FILE = "exoasteroid_output/merged_dip_metadata.csv"
try:
    df = pd.read_csv(DATA_FILE)
except FileNotFoundError:
    st.error("❌ Merged data not found. Please run the merge script first.")
    st.stop()

# === Sidebar filters ===
with st.sidebar:
    st.header("🎛️ Filter Options")

    # TIC filters
    tics = sorted(df["tic_id"].unique())
    selected_tics = st.multiselect("Select TICs", tics, default=tics)

    # Label filter
    labels = df["predicted_label"].dropna().unique()
    selected_labels = st.multiselect("AI Labels", labels, default=labels)

    # ExoFOP status filter
    statuses = df["exofop_status"].dropna().unique()
    selected_statuses = st.multiselect("ExoFOP Status", statuses, default=statuses)

    # Tmag brightness filter
    bright_only = st.checkbox("🌟 Show only bright stars (Tmag < 12)", value=False)

    # Object size filters
    st.markdown("### Object Size (Radius in km)")
    min_r, max_r = 0, 20000
    radius_range = st.slider("Object radius range", min_r, max_r, (min_r, max_r), step=100)

    # Quick toggles
    moon_only = st.checkbox("🌑 Only Moon-sized (500–3000 km)", value=False)
    earth_only = st.checkbox("🌍 Only Earth-sized (5000–15000 km)", value=False)

# === Apply filters ===
filtered_df = df[
    df["tic_id"].isin(selected_tics) &
    df["predicted_label"].isin(selected_labels) &
    df["exofop_status"].isin(selected_statuses)
]

if bright_only and "Tmag" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["Tmag"] < 12]

if "object_radius_km" in filtered_df.columns:
    filtered_df = filtered_df[filtered_df["object_radius_km"].between(*radius_range)]
    if moon_only:
        filtered_df = filtered_df[filtered_df["object_radius_km"].between(500, 3000)]
    if earth_only:
        filtered_df = filtered_df[filtered_df["object_radius_km"].between(5000, 15000)]

# === Highlight ExoFOP status ===
def highlight_status(row):
    color = ""
    if "Not Found" in row["exofop_status"]:
        color = "#ffcccc"
    elif "No Planet" in row["exofop_status"]:
        color = "#fff7cc"
    elif "Known Planet" in row["exofop_status"]:
        color = "#ccffcc"
    return [f"background-color: {color}"] * len(row)

st.subheader("📋 Dip Results")
columns_to_show = [
    "tic_id", "predicted_label", "exofop_status", "dip_depth",
    "star_radius_rsun", "object_radius_km", "Tmag", "Teff"
]
available_cols = [col for col in [
    "tic_id", "predicted_label", "exofop_status", "dip_depth",
    "star_radius_rsun", "object_radius_km", "Tmag", "Teff"
] if col in filtered_df.columns]

st.dataframe(
    filtered_df[available_cols].head(500).style.apply(highlight_status, axis=1),
    use_container_width=True
)
st.download_button("📥 Download filtered results", data=filtered_df.to_csv(index=False), file_name="filtered_dips.csv")

# === Sky Map Tabs ===
st.markdown("---")
st.header("🗺️ Sky Map of Candidate TICs")
tab1, tab2 = st.tabs(["🖼️ Static Sky Map", "🌐 Interactive Plotly Map"])

with tab1:
    fig, ax = plt.subplots(figsize=(10, 5))
    for label in filtered_df["predicted_label"].unique():
        subset = filtered_df[filtered_df["predicted_label"] == label]
        ax.scatter(subset["ra_x"], subset["dec_x"], label=label, s=40, alpha=0.7, edgecolors="black")
    ax.set_title("Static Sky Map")
    ax.set_xlabel("RA (°)")
    ax.set_ylabel("Dec (°)")
    ax.invert_xaxis()
    ax.legend()
    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    st.pyplot(fig)
    st.download_button("📥 Download Sky Map Image", data=buf.getvalue(), file_name="static_sky_map.png", mime="image/png")

with tab2:
    hover_columns = ["tic_id", "Tmag_x", "Teff_x", "rad", "object_radius_km", "exofop_status"]
    hover_data = [col for col in hover_columns if col in filtered_df.columns]
    fig_plotly = px.scatter(
        filtered_df,
        x="ra_x", y="dec_x",
        color="predicted_label",
        symbol="exofop_status",
        hover_name="tic_id",
        hover_data=hover_data,
        title="Interactive Sky Map of Predicted Dips"
    )
    fig_plotly.update_layout(xaxis_title="RA", yaxis_title="Dec", xaxis_autorange="reversed")
    st.plotly_chart(fig_plotly, use_container_width=True)

# === Discovery Score Section ===
st.markdown("---")
st.header("🪐 Discovery Candidates (Scored)")

SCORED_FILE = "exoasteroid_output/discovery_scores_with_radius.csv"
try:
    df_scores = pd.read_csv(SCORED_FILE)
except FileNotFoundError:
    st.warning("⚠️ No discovery score file found. Run `discovery_scoring.py` first.")
    df_scores = None

if df_scores is not None:
    st.subheader("🎯 Filter by Discovery Score")

    score_labels = df_scores["discovery_label"].dropna().unique()
    selected_labels = st.multiselect("Select candidate types", score_labels, default=score_labels)

    score_min = st.slider("Minimum Confidence Score", 0, 100, 50)
    only_bright = st.checkbox("🌟 Only bright stars (Tmag < 12)", value=False)
    only_periodic = st.checkbox("📍 Only periodic candidates", value=False)

    filtered_candidates = df_scores[
        (df_scores["discovery_label"].isin(selected_labels)) &
        (df_scores["confidence_score"] >= score_min)
    ]

    if only_bright and "Tmag" in filtered_candidates.columns:
        filtered_candidates = filtered_candidates[filtered_candidates["Tmag"] < 12]

    if only_periodic and "periodic" in filtered_candidates.columns:
        filtered_candidates = filtered_candidates[filtered_candidates["periodic"] == True]

    st.markdown(f"📊 Showing **{len(filtered_candidates)}** candidates")
    tmag_col = "Tmag_x" if "Tmag_x" in filtered_candidates.columns else (
    "Tmag_y" if "Tmag_y" in filtered_candidates.columns else None
    )
    columns_to_show = [
    "tic_id", "predicted_label", "exofop_status", "dip_depth",
    "star_radius_rsun", "object_radius_km", tmag_col,
    "periodic", "discovery_label"
    ]
    columns_to_show = [col for col in columns_to_show if col is not None]
    st.dataframe(filtered_candidates[columns_to_show].head(500), use_container_width=True)

    st.download_button(
        "📥 Download candidate list",
        data=filtered_candidates.to_csv(index=False),
        file_name="top_discovery_candidates.csv"
    )

st.markdown("---")
st.caption("🚀 Built by Pinkey Bartake for the ExoAsteroids project")
