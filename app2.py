# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from textwrap import dedent

st.set_page_config(page_title="Targets Matrix — Replica", layout="wide")
st.title("Peer decarbonization — Ambition Matrix (replica)")

st.markdown(
    """
    This interactive dashboard replicates the quadrant-style matrix from your screenshot:
    - Y-axis: Scope 1+2 targets (% reduction per tonne)
    - X-axis: Scope 3 targets (% reduction)
    - Quadrants split at 0–50% and 51–100% (absolute), with Not-reported companies aligned left.
    - Hover each point for SBTi status, notes, and source.
    """
)

# ---------------------------------------------------------------------
# DATA: default sample matching your screenshot (Aptar / Berlin / Greif / Novolex / Mauser / TricorBraun)
# ---------------------------------------------------------------------
# CSV upload or Google Sheet support:
st.sidebar.header("Data input")
upload = st.sidebar.file_uploader("Upload CSV (optional)", type=["csv"])
sheet_url_input = st.sidebar.text_input("Or paste published Google Sheet CSV URL (optional)")

if upload is not None:
    df = pd.read_csv(upload)
elif sheet_url_input:
    try:
        df = pd.read_csv(sheet_url_input)
    except Exception as e:
        st.sidebar.error("Couldn't read that URL as CSV. Make sure you published the sheet to web (CSV) and pasted the CSV link.")
        st.stop()
else:
    # Sample data (values chosen to mirror the screenshot layout)
    df = pd.DataFrame([
        {
            "Company": "Aptar",
            "Scope12_pct": 82.0,
            "Scope3_pct": 14.0,
            "Target_Type": "Absolute",
            "SBTi_Status": "SBT Committed (near-term)",
            "Notes": "2019-2030 (82%) / 2019-2030 (14%)",
            "Coverage": "Scope 1, 2",
            "NZ_CN": ""
        },
        {
            "Company": "Berlin Packaging",
            "Scope12_pct": 44.8,
            "Scope3_pct": 51.6,
            "Target_Type": "Absolute",
            "SBTi_Status": "SBT Verified (NZ)",
            "Notes": "2022-2030 targets: 44.8% (S1+2) / 51.6% (S3)",
            "Coverage": "Scope 1, 2 & 3",
            "NZ_CN": "NZ by 2050"
        },
        {
            "Company": "Greif",
            "Scope12_pct": 28.0,
            "Scope3_pct": np.nan,
            "Target_Type": "Absolute",
            "SBTi_Status": "SBT Committed (NZ)",
            "Notes": "2019-2030 (28%)",
            "Coverage": "Scope 1, 2",
            "NZ_CN": ""
        },
        {
            "Company": "Novolex",
            "Scope12_pct": 30.0,
            "Scope3_pct": np.nan,
            "Target_Type": "Intensity",
            "SBTi_Status": "SBT Committed (near-term)",
            "Notes": "Intensity metric; under development for Scope 3",
            "Coverage": "Not reported",
            "NZ_CN": ""
        },
        {
            "Company": "Mauser",
            "Scope12_pct": np.nan,
            "Scope3_pct": np.nan,
            "Target_Type": "Not reported",
            "SBTi_Status": "No public targets",
            "Notes": "No public targets",
            "Coverage": "Not reported",
            "NZ_CN": ""
        },
        {
            "Company": "TricorBraun",
            "Scope12_pct": np.nan,
            "Scope3_pct": np.nan,
            "Target_Type": "Not reported",
            "SBTi_Status": "No public targets",
            "Notes": "No public targets",
            "Coverage": "Not reported",
            "NZ_CN": ""
        }
    ])

# Ensure required columns exist; provide guidance if not
required_cols = {"Company", "Scope12_pct", "Scope3_pct", "Target_Type", "SBTi_Status", "Notes", "Coverage", "NZ_CN"}
if not required_cols.issubset(set(df.columns)):
    st.sidebar.warning(dedent(f"""
        Your input data is missing some columns expected by the matrix.
        Required columns:
        {sorted(list(required_cols))}
        Using the included sample dataset for preview.
    """))
    # If user provided bad CSV, fallback to sample (already assigned above if no upload)
    # Re-check: if user uploaded but columns wrong, show & stop
    if upload is not None or sheet_url_input:
        st.stop()

# Replace missing Scope3 with a tiny sentinel so they appear in the 'not reported' left area
# (we will also mark them visually in the legend)
df["Scope3_plot"] = df["Scope3_pct"].fillna(0.5)  # tiny >0 so on left
df["Scope12_plot"] = df["Scope12_pct"].fillna(0.5)

# Create a category for Not reported labels (so using 'Not reported' point style)
df["Reported3"] = df["Scope3_pct"].notna()
df["Reported12"] = df["Scope12_pct"].notna()

# Symbol & color mapping
symbol_map = {
    "Absolute": "diamond",
    "Intensity": "circle",
    "Not reported": "x"
}
# For statuses, choose colors (customize later)
status_palette = {
    "SBT Verified (near-term)": "#2b8cbe",
    "SBT Committed (near-term)": "#7bccc4",
    "SBT Committed (NZ)": "#fdae61",
    "SBT Verified (NZ)": "#d7191c",
    "No public targets": "#bdbdbd"
}

# If there are statuses not in palette, add them with default color
for s in df["SBTi_Status"].unique():
    if s not in status_palette:
        status_palette[s] = px.colors.qualitative.Plotly[len(status_palette) % len(px.colors.qualitative.Plotly)]

# Build the Plotly figure (scatter)
fig = go.Figure()

# Plot each SBTi status as a group to control color and legend ordering
for status, color in status_palette.items():
    sub = df[df["SBTi_Status"] == status]
    if sub.empty:
        continue
    # map symbols (use the Target_Type column)
    symbols = [symbol_map.get(t, "circle") for t in sub["Target_Type"]]
    fig.add_trace(go.Scatter(
        x=sub["Scope3_plot"],
        y=sub["Scope12_plot"],
        mode="markers+text",
        text=sub["Company"],
        textposition="top center",
        marker=dict(
            size=16,
            symbol=symbols,
            color=color,
            line=dict(width=1, color="black")
        ),
        name=status,
        hovertemplate=(
            "<b>%{text}</b><br>"
            "Scope 1+2 target: %{y}%<br>"
            "Scope 3 target: %{x}%<br>"
            "Target type: %{customdata[0]}<br>"
            "Coverage: %{customdata[1]}<br>"
            "Notes: %{customdata[2]}<extra></extra>"
        ),
        customdata=np.stack([sub["Target_Type"], sub["Coverage"], sub["Notes"]], axis=1)
    ))

# Add quadrant division lines (0-50 vs 51-100) and NZ/CN top line
fig.add_shape(type="line", x0=50, x1=50, y0=0, y1=110, line=dict(color="black", width=1, dash="dash"))
fig.add_shape(type="line", x0=0, x1=110, y0=50, y1=50, line=dict(color="black", width=1, dash="dash"))

# Dotted boundaries at 0,50,100 to mimic screenshot grid
fig.add_shape(type="line", x0=0, x1=110, y0=100, y1=100, line=dict(color="gray", width=1, dash="dot"))
fig.add_shape(type="line", x0=100, x1=100, y0=0, y1=110, line=dict(color="gray", width=1, dash="dot"))

# Add quadrant labels (approx positions)
fig.add_annotation(x=12, y=98, xref="x", yref="y",
                   text="NZ/CN\n51–100% absolute", showarrow=False, font=dict(size=11))
fig.add_annotation(x=62, y=98, xref="x", yref="y",
                   text="Relevant target: furthest out until 2033", showarrow=False, font=dict(size=11), align="left")
fig.add_annotation(x=12, y=48, xref="x", yref="y",
                   text="0–50% absolute", showarrow=False, font=dict(size=11))
fig.add_annotation(x=62, y=48, xref="x", yref="y",
                   text="51–100% absolute", showarrow=False, font=dict(size=11))

# Add vertical 'AMBITION' label on left (paper coordinates)
fig.add_annotation(x=-0.08, y=0.9, xref="paper", yref="paper",
                   text="<b>AMBITION</b>", showarrow=False, textangle=-90, font=dict(size=14))

# Axis titles and ranges
fig.update_xaxes(range=[0, 110], title_text="Scope 3 target (in reduction %)", tick0=0, dtick=25)
fig.update_yaxes(range=[0, 110], title_text="Scope 1+2 targets (in reduction %)")

fig.update_layout(
    template="plotly_white",
    height=750,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.01),
    margin=dict(l=40, r=10, t=80, b=40)
)

# Render layout with two columns: chart + side info panel
col_main, col_side = st.columns([3, 1])

with col_main:
    st.plotly_chart(fig, use_container_width=True)

with col_side:
    st.markdown("### / A S  O F  J U L '25")
    st.write("")
    # Show NZ/CN highlighted card if any company has NZ_CN not empty
    nz_rows = df[df["NZ_CN"].str.strip().astype(bool)]
    if not nz_rows.empty:
        for idx, r in nz_rows.iterrows():
            st.markdown(f"**{r['Company']}**")
            st.markdown(f"- {r['NZ_CN']}")
            st.markdown(f"- Coverage: {r.get('Coverage','—')}")
            st.write("")
    else:
        st.markdown("No NZ/CN targets in sample data.")
    st.markdown("---")
    st.markdown("**Legend**")
    st.markdown("- Marker shape: Target Type (diamond = Absolute, circle = Intensity, x = Not reported)")
    st.markdown("- Marker color: SBTi status")
    st.markdown("---")
    st.markdown("**Companies (no NZ/CN)**")
    no_nz = df[df["NZ_CN"].fillna("").str.strip() == ""]
    for c in no_nz["Company"].tolist():
        st.write(c)

# Raw data & export
with st.expander("View / Download raw data and edit"):
    st.dataframe(df)
    csv = df.to_csv(index=False)
    st.download_button("Download CSV", data=csv, file_name="matrix_data.csv", mime="text/csv")

# Footnotes / sources
with st.expander("Footnotes & sources (click to expand)", expanded=False):
    st.markdown("""
    - **Notes**: This layout matches the example provided:
      - X and Y scaled 0–100 (% reduction).  
      - Companies without reported Scope 3 plotted at ~0.5% on X to sit in the "Not reported publicly" area.  
      - Use the CSV upload or Google Sheet link to replace sample data.
    - **Required CSV columns:** Company, Scope12_pct, Scope3_pct, Target_Type, SBTi_Status, Notes, Coverage, NZ_CN
    - Example published Google Sheet (publish → CSV link): `https://docs.google.com/spreadsheets/d/<id>/pub?output=csv`
    """)

