import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import io
import math
from datetime import datetime, date
from pathlib import Path

# Local persistence. On hosted platforms, local files may be ephemeral.
DATA_DIR = Path("oncopgx_data")
DATA_DIR.mkdir(exist_ok=True)
PV_DB = DATA_DIR / "pv_registry.csv"
TDM_DB = DATA_DIR / "tdm_measurements.csv"

def read_local_csv(path, columns):
    """Read a local research CSV safely; return an empty table if absent/unreadable."""
    try:
        if path.exists():
            df = pd.read_csv(path)
            for col in columns:
                if col not in df.columns:
                    df[col] = ""
            return df[columns]
    except Exception:
        pass
    return pd.DataFrame(columns=columns)

def append_local_row(path, columns, row):
    """Append one row to a local CSV research log."""
    df = read_local_csv(path, columns)
    df = pd.concat([df, pd.DataFrame([{c: row.get(c, "") for c in columns}])], ignore_index=True)
    df.to_csv(path, index=False)
    return df

st.set_page_config(
    page_title="OncoPGx | Precision Oncology",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- THEME --------------------

st.markdown("""
<style>
.stApp {
    background:
      radial-gradient(ellipse at 80% 0%, #102b59 0%, transparent 38%),
      radial-gradient(ellipse at 0% 80%, #101b45 0%, transparent 35%),
      #06101f;
    color: #edf5ff;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#09172d,#06101f);
    border-right: 1px solid #1b4266;
}
h1,h2,h3 { color: #e5f5ff !important; }
p, label, li { color: #c6d8f2; }
[data-testid="stMetric"] {
    background: linear-gradient(135deg,#102747,#0b1830);
    border: 1px solid #23527b;
    padding: 15px;
    border-radius: 13px;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #20496c;
    border-radius: 14px;
}
.stButton > button {
    background: linear-gradient(90deg,#087ee1,#7857ff);
    color: white;
    border: 0;
    border-radius: 9px;
}
div[data-baseweb="select"] > div {
    background-color: #0b1c35;
}
hr { border-color: #214264; }
.hero {
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #22618b;
    background: linear-gradient(115deg,#0b2344,#102253,#161640);
}
.small { color: #83b8e8; font-size: 13px; }
.warning {
    padding: 12px;
    border: 1px solid #d84b75;
    border-radius: 10px;
    background: #29152a;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
