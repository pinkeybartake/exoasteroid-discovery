import pandas as pd
import plotly.express as px

# Load star data
df = pd.read_csv("exoasteroid_output/tic_metadata.csv")
df_pred = pd.read_csv("exoasteroid_output/predicted_dips_with_exofop_status.csv")
df = df.merge(df_pred[["tic_id", "predicted_label", "exofop_status"]], on="tic_id", how="left")

fig = px.scatter(
    df,
    x="ra",
    y="dec",
    color="predicted_label",
    symbol="exofop_status",
    hover_name="tic_id",
    hover_data=["ra", "dec", "exofop_status"],
    title="🧭 Interactive Sky Map of TESS Dips",
    labels={"ra": "Right Ascension", "dec": "Declination"}
)

fig.update_layout(yaxis_title="Declination (°)", xaxis_title="RA (°)", xaxis_autorange="reversed")
fig.write_html("exoasteroid_output/interactive_star_map.html")
fig.show()
