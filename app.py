import streamlit as st
import numpy as np
import pandas as pd
import io

# ─── SAFE DEPENDENCY LOADER FOR PORTABLE DEPLOYMENTS ─────────────────────────
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    reportlab_available = True
except ImportError:
    reportlab_available = False

# Try importing Plotly for advanced visualization
try:
    import plotly.graph_objects as go
    plotly_available = True
except ImportError:
    plotly_available = False

# ─── STYLING & INTERFACE DESIGN (SWISS CYBERNETIC HUD AESTHETIC) ─────────────
st.set_page_config(
    page_title="Zurich Translational Systems Pharmacology Command Center", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #05070f; color: #f1f5f9; }
    h1, h2, h3, h4, p, span, label, div { font-family: 'Inter', system-ui, sans-serif; }
    
    .swiss-premium-banner {
        background: linear-gradient(135deg, #062426 0%, #0b1329 60%, #1e1b4b 100%);
        border-radius: 16px; padding: 2rem; position: relative;
        border: 1px solid rgba(16, 185, 129, 0.25);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6); margin-bottom: 2rem;
    }
    .system-status { font-size: 10px; font-family: monospace; text-transform: uppercase; letter-spacing: 2px; color: #10b981; font-weight: bold; }
    
    .metric-card {
        background: rgba(15, 23, 42, 0.75); 
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 12px; padding: 1.5rem; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }
    .metric-val { font-size: 26px; font-weight: 800; color: #10b981; margin: 5px 0; }
    .metric-lbl { font-size: 11px; text-transform: uppercase; color: #94a3b8; letter-spacing: 1px; }
    
    .hud-header {
        border-left: 4px solid #10b981; padding-left: 10px; margin-top: 2rem; margin-bottom: 1rem;
        font-weight: 700; color: #f8fafc; font-size: 20px;
    }
    .pharm-card {
        background: #0f172a; padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="swiss-premium-banner">
        <span class="system-status">✦ QUANTITATIVE SYSTEMS PHARMACOLOGY (QSP) ENGINE // QUANTUM TRANSLATIONAL HUB</span>
        <h1 style='color: #ffffff !important; margin: 5px 0 0 0; font-size:30px; font-weight:800; letter-spacing:-0.5px;'>🧬 TRANSLATIONAL SYSTEMS PHARMACOLOGY COMMAND CENTER</h1>
        <p style='color: #94a3b8 !important; margin: 5px 0 0 0; font-size:13px; font-family: monospace;'>
            Multi-Omic Xenobiotic Simulator • Principal Architect: Dr. Mayank Virmani | PharmD & PV Scientist
        </p>
    </div>
""", unsafe_allow_html=True)

# ─── DATA INPUT GRID SETUP ───────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='hud-header'>📋 1. Patient Demographics & Tumor Target</div>", unsafe_allow_html=True)
    pt_id = st.text_input("Patient System Hash ID", "ZRH-2026-9843X")
    age = st.slider("Chronological Age (Years)", 18, 100, 64)
    weight = st.slider("Total Mass Target (kg)", 35, 150, 82)
    gender = st.radio("Biological Configuration", ["Female", "Male"], horizontal=True)
    
    cyp2d6_profile = st.selectbox("CYP2D6 Genomic Architecture (CPIC Axis)", [
        "*1/*1 (Normal Metabolizer - Baseline Metabolic Velocity)", 
        "*1xN/*1 (Ultra-rapid Metabolizer - Activity Score > 2.0)",
        "*1/*10 (Intermediate Metabolizer - Impaired Flux Spectrum)", 
        "*4/*4 (Null Allele - Poor Metabolizer - Total Phenoconversion)"
    ])
    er_status = st.radio("Estrogen Receptor Nuclear Expression (ERα)", ["Positive Status", "Negative Status"], horizontal=True)

with col2:
    st.markdown("<div class='hud-header'>🧬 2. Secondary PGx & Xenobiotic DDIs</div>", unsafe_allow_html=True)
    cyp2c9_c19_profile = st.selectbox("CYP2C9 / CYP2C19 Parallel Shunt Velocity", [
        "Wild-Type / Extensive Turnover (Normal Baseline)",
        "CYP2C19*2/*2 Poor Metabolizer (Impaired 4-Hydroxy Conversion)",
        "CYP2C9*3 Carrier (Altered Alternate Metabolite Shunting)"
    ])
    sult1a1_cnv = st.selectbox("SULT1A1 Copy Number Variations (Phase II Conjugation)", [
        "Normal Copy Number (2 Copies - Standard Active Sulfation)",
        "SULT1A1 Deletion Variant (Low Active Endoxifen Bioavailability)",
        "SULT1A1 Amplification Variant (>3 Copies - Accelerated Clearance)"
    ])
    
    cyp2d6_inhibitor = st.selectbox("CYP2D6 Potent Core Inhibitors", [
        "None / Sub-clinical",
        "Paroxetine / Fluoxetine (Irreversible Invalidation)",
        "Bupropion / Quinidine (High Affinity Competitive Capture)",
        "Sertraline / Duloxetine (Moderate Pathway Saturation)"
    ])
    cyp3a4_modulator = st.selectbox("Secondary CYP3A4 Modulators", [
        "None / Normal Turnover",
        "Rifampicin (Extreme CYP3A4 Induction Hazard)",
        "Ketoconazole (Severe Clearance Suppression Matrix)"
    ])

with col3:
    st.markdown("<div class='hud-header'>📊 3. End-Organ Clearances & Safety Markers</div>", unsafe_allow_html=True)
    creatinine = st.number_input("Serum Creatinine Clear Marker (mg/dL)", min_value=0.2, max_value=12.0, value=1.35, step=0.05)
    serum_ast = st.number_input("Hepatic Transaminase AST (U/L)", min_value=5, max_value=3000, value=145, step=5)
    serum_alt = st.number_input("Hepatic Transaminase ALT (U/L)", min_value=5, max_value=3000, value=165, step=5)
    total_bilirubin = st.number_input("Total Bilirubin Mass Fraction (mg/dL)", min_value=0.1, max_value=20.0, value=2.4, step=0.1)
    
    comorbidities = st.multiselect("Active Pathological Overlays", [
        "Deep Vein Thrombosis (DVT Risk)",
        "Endometrial Hyperplasia Hyper-proliferation",
        "Non-Alcoholic Fatty Liver Disease (NAFLD)",
        "Severe Retinopathy & Macular Degradation"
    ], default=["Non-Alcoholic Fatty Liver Disease (NAFLD)"])
    
    compliance = st.slider("Adherence Control (MEMS Smart-Cap %)", 10, 100, 90) / 100.0

# ─── REAL-WORLD PHARMACOKINETIC TRANSLATIONAL METABOLIC ENGINE ──────────────
gender_multiplier = 0.85 if gender == "Female" else 1.0
calculated_crcl = round(((140 - age) * weight) / (72 * creatinine) * gender_multiplier, 1)

# Elimination rate constant based on renal clearance dynamics
ke = 0.025 if calculated_crcl >= 60 else 0.042 if calculated_crcl >= 30 else 0.068

# Translating your 13,001 patient abstract cohort data into metabolic flux thresholds
if "*4/*4" in cyp2d6_profile: base_flux = 8.8  # Poor Metabolizer Mean Concentration
elif "*1/*10" in cyp2d6_profile: base_flux = 14.2
elif "*1/*1" in cyp2d6_profile: base_flux = 22.3  # Extensive Metabolizer Mean Concentration
else: base_flux = 32.5  # Ultra-rapid profile

# Phenoconversion via concomitant drug inhibitors (DDI Shunts)
if "Paroxetine" in cyp2d6_inhibitor: 
    base_flux = 8.8  # Strong inhibitor switches EM to PM phenotype
elif "Bupropion" in cyp2d6_inhibitor: 
    base_flux *= 0.40
elif "Sertraline" in cyp2d6_inhibitor: 
    base_flux *= 0.65

if "CYP2C19*2/*2" in cyp2c9_c19_profile: base_flux *= 0.85
if "SULT1A1 Deletion" in sult1a1_cnv: base_flux *= 0.75

calculated_endoxifen = round(base_flux * compliance, 2)
time_axis = list(range(1, 31))
kinetics_curve = [round(calculated_endoxifen * (1 - np.exp(-ke * t)), 2) for t in time_axis]

chart_dataframe = pd.DataFrame({
    'Day': time_axis,
    'Simulated Endoxifen': kinetics_curve,
    'CPIC Threshold Floor': [5.97] * 30
})

# ─── HIGH-CLINICAL STRATEGY DECISION ENGINE (CPIC / ASCO / ESMO) ────────────
clinical_guideline_source = "CPIC Guidelines & ASCO/ESMO Endocrine Mandates"

if "Negative Status" in er_status:
    suggested_drug = "Non-Endocrine Alternative Regimens (Chemotherapy/Biologics)"
    suggested_dose = "Discontinue Tamoxifen (0.0 mg)"
    clinical_directive = "CRITICAL CONTRAINDICATION: Tumor presents as ERα-Negative. Tamoxifen action relies on nuclear receptor tracking; absolute resistance pathways active."
    status_color = "#ef4444"
elif calculated_endoxifen < 5.97:
    if "*4/*4" in cyp2d6_profile or "Paroxetine" in cyp2d6_inhibitor:
        suggested_drug = "Aromatase Inhibitor (Anastrozole/Letrozole/Exemestane)"
        suggested_dose = "Switch to Standard AI Protocol (+ LHRH Agonist if premenopausal)"
        clinical_directive = "Genomic/DDI Phenoconversion Obstruction. Active metabolic pathways cannot reach therapeutic corridor. Complete therapeutic class rotation required."
        status_color = "#ef4444"
    else:
        suggested_drug = "Tamoxifen Malate (Dose Escalation Protocol)"
        suggested_dose = "40.0 mg Daily Maintenance (Split as 20mg BID)"
        clinical_directive = "Sub-therapeutic TDM Concentration Window (<5.97 ng/mL). CPIC clinical recommendation indicates dose escalation to double baseline under precise TDM tracking."
        status_color = "#f59e0b"
else:
    suggested_drug = "Tamoxifen Malate (Standard Adjuvant Protocol)"
    suggested_dose = "20.0 mg Daily Oral Q.D."
    clinical_directive = "Therapeutic Corridor Maintained. Metabolic flux profile satisfies structural target concentration benchmarks."
    status_color = "#10b981"

# ─── REAL-TIME ENGINE ANALYTICS TILES ────────────────────────────────────────
st.markdown("<div class='hud-header'>📊 Real-Time QSP Simulated Engine Analytics</div>", unsafe_allow_html=True)

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.markdown(f"<div class='metric-card'><div class='metric-lbl'>Steady-State Endoxifen</div><div class='metric-val'>{calculated_endoxifen} ng/mL</div></div>", unsafe_allow_html=True)
with m_col2:
