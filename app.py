"""
OncoPGx Research & Learning Prototype
Not for clinical decision-making. No prescribing, dose adjustment, or validated prediction.
Run: streamlit run app.py
Optional PDF export: pip install reportlab
"""
import io
import json
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

APP_VERSION = "0.1-learning-prototype"
DATA_DIR = Path("oncopgx_data")
DATA_DIR.mkdir(exist_ok=True)
PV_FILE = DATA_DIR / "pv_reports.csv"
TDM_FILE = DATA_DIR / "tdm_measurements.csv"

st.set_page_config(page_title="OncoPGx | Dr. Mayank Virmani",
                   page_icon="🧬", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp {background: radial-gradient(circle at 12% 0%, #15355a 0%, #081525 38%, #050914 100%); color:#edf5ff;}
[data-testid="stHeader"] {background:rgba(4,10,22,.72);}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#102944 0%,#10162b 55%,#21143b 100%); border-right:1px solid #2c5277;}
[data-testid="stMetric"] {background:linear-gradient(135deg,rgba(17,49,76,.96),rgba(34,28,65,.96));padding:16px;border-radius:15px;border:1px solid #2c7890;box-shadow:0 8px 24px rgba(0,0,0,.22);}
[data-testid="stMetricValue"] {color:#66f0dc;}
.notice {padding:18px;border-radius:14px;background:linear-gradient(120deg,#422a16,#3b1e3b);border:1px solid #f0a34a;color:#fff4df;box-shadow:0 8px 25px rgba(0,0,0,.2);}
.small-muted {color:#b9c9df;font-size:0.9rem}
.hero {padding:28px 30px;border-radius:20px;background:linear-gradient(115deg,#073b47 0%,#11264d 50%,#41235b 100%);border:1px solid rgba(105,239,224,.45);box-shadow:0 16px 45px rgba(0,0,0,.3);margin:4px 0 22px 0;}
.hero-kicker {font-size:11px;letter-spacing:2.2px;text-transform:uppercase;font-weight:800;color:#8ff7e9;}
.hero h1 {font-size:clamp(27px,3vw,40px);line-height:1.15;color:#fff;margin:10px 0 8px 0;}
.hero p {color:#d6e6ff;margin:0;font-size:15px;}
.owner-line {margin-top:16px;padding-top:12px;border-top:1px solid rgba(255,255,255,.2);font-weight:700;color:#f8d98b;}
div[data-testid="stTabs"] button {border-radius:10px 10px 0 0;font-weight:700;}
div[data-testid="stTabs"] button[aria-selected="true"] {background:linear-gradient(90deg,#0f766e,#4338ca);color:white;border-bottom:2px solid #6df3e4;}
.stButton>button, .stDownloadButton>button, [data-testid="stFormSubmitButton"] button {background:linear-gradient(100deg,#0f9b8e,#5367dc);color:white;border:0;border-radius:10px;font-weight:750;}
.stButton>button:hover, .stDownloadButton>button:hover {background:linear-gradient(100deg,#14b8a6,#7c3aed);color:white;border:0;}
[data-testid="stExpander"] {border:1px solid #284965;border-radius:12px;}
hr {border-color:#31506d;}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero">
  <div class="hero-kicker">Precision Oncology • Pharmacogenomics • Pharmacology • Safety Monitoring</div>
  <h1>🧬 OncoPGx Research Workbench</h1>
  <p>An integrated learning platform for patient context, PGx interpretation, organ-function estimates, interaction review, TDM, PK/AUC demonstrations and pharmacovigilance case tracking.</p>
  <div class="owner-line">Research prototype • Dr. Mayank Virmani</div>
</div>
<div class="small-muted">Version {APP_VERSION} · Learning-stage project · Evidence links included in relevant modules</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="notice"><b>LEARNING / RESEARCH PROTOTYPE — NOT FOR CLINICAL DECISION-MAKING</b><br>
This app does not prescribe medicines, select a treatment for a real patient, or recommend dose changes.
Its calculations and plots are educational aids, not a validated clinical model. Verify current guidance
and all results with qualified oncology, clinical pharmacology, laboratory and pharmacovigilance professionals.
Do not enter identifiable patient information. Demo records are stored locally on the machine running Streamlit.</div>
""", unsafe_allow_html=True)

GUIDELINES = {
    "CPIC — CYP2D6 and tamoxifen (2018)": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5931215/",
    "CPIC guideline index": "https://cpicpgx.org/guidelines/",
    "PharmGKB — clinical annotations/guidelines": "https://www.pharmgkb.org/",
    "NIDDK — drug dosing in CKD / eGFR equations": "https://www.niddk.nih.gov/research-funding/research-programs/kidney-clinical-research-epidemiology/laboratory/ckd-drug-dosing",
    "FDA — drug development and drug interactions": "https://www.fda.gov/drugs/drug-interactions-labeling",
    "ICH E2A — clinical safety data management": "https://www.ich.org/page/efficacy-guidelines",
    "WHO-UMC — signal management": "https://edit.who-umc.org/signal-management/signal-management-at-umc/",
    "India — Pharmacovigilance Programme of India (PvPI)": "https://www.ipc.gov.in/PvPI/toolkit.html",
    "NCI — breast cancer treatment (patient/professional information)": "https://www.cancer.gov/types/breast/treatment",
}

def safe_read_csv(path, columns):
    if path.exists():
        try:
            df = pd.read_csv(path)
            for c in columns:
                if c not in df.columns:
                    df[c] = ""
            return df[columns]
        except Exception:
            st.warning(f"Could not read {path.name}; a blank table is shown. Keep a backup before replacing files.")
    return pd.DataFrame(columns=columns)

def save_csv(df, path):
    df.to_csv(path, index=False)

def cockcroft_gault(age, weight_kg, scr_mg_dl, sex_factor):
    # sex_factor is 0.85 for the conventional female equation, otherwise 1.0.
