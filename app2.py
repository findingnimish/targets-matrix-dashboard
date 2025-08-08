import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- SETTINGS ---
st.set_page_config(page_title="Cement Company Targets", layout="wide")

st.title("Scope 1+2 vs Scope 3 Targets | Cement Industry")

# --- SAMPLE DATA (replace with Google Sheet or CSV) ---
data = pd.DataFrame({
    "Company": ["Aptar", "Berlin", "Greif", "Novolex", "Mauser", "TricorBraun"],
    "Scope12_Reduction": [82, 44.8, 28, 30, None, None],  # % reduction
    "Scope3_Reduction": [14, 51.6, None, None, None, None],  # % reduction
    "Target_Type": ["Absolute", "Absolute", "Absolute", "Intensity", "Not reported", "Not reported"],
    "SBTi_Status": ["SBT Verified (near-term)", "SBT Verified (NZ)", "SBT Committed (NZ)",
                    "SBT Committed (near-term)", "SBT Committed (near-term)", "SBT Committed (near-term)"],
    "Notes": [
        "2019-2030 target",
        "2022-2030 target",
        "2019-2030 target",
        "2019-2030 target",
        "No public data",
        "No public data"
    ]
})

# --- FIGURE ---
fig = px.scatter(
    data,
    x="Scope3_Reduction",
    y="Scope12_Reduction",
    text="Company",
    hover_data=["SBTi_Status", "Notes"],
    color="SBTi_Status",
    symbol="Target_Type",
    size_max=15
)

# --- Quadrant lines ---
fig.add_shape(type="line", x0=50, x1=50, y0=0, y1=100,
              line=dict(color="black", dash="dot"))
fig.add_shape(type="line", x0=0, x1=100, y0=50, y1=50,
              line=dict(color="black", dash="dot"))

# --- Layout ---
fig.update_layout(
    xaxis_title="Scope 3 target (% reduction)",
    yaxis_title="Scope 1+2 target (% reduction)",
    xaxis=dict(range=[0, 100]),
    yaxis=dict(range=[0, 100]),
    template="plotly_white",
    legend_title="SBTi Status",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# --- Data table ---
with st.expander("View raw data"):
    st.dataframe(data)
