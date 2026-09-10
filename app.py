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
        background: rgba(15, 23, 42, 0.6); border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px; padding: 1.2rem; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .hud-header {
        border-left: 4px solid #10b981; padding-left: 10px; margin-top: 1.5rem; margin-bottom: 1rem;
        font-weight: 700; color: #f8fafc;
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

if 'patient_ledger' not in st.session_state:
    st.session_state.patient_ledger = []

# ─── DATA INPUT GRID SETUP ───────────────────────────────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("<div class='hud-header'>📋 1. Patient Demographics & Tumor Target</div>", unsafe_allow_html=True)
    pt_id = st.text_input("Patient System Hash ID", "ZRH-2026-9843X")
    age = st.slider("Chronological Age (Years)", 18, 100, 64)
    weight = st.slider("Total Mass Target (kg)", 35, 150, 82)
    gender = st.radio("Biological Configuration", ["Female", "Male"], horizontal=True)
    
    cyp2d6_profile = st.selectbox("CYP2D6 Genomic Architecture (CPIC Axis)", [
        "*1xN/*1 (Ultra-rapid Metabolizer - Activity Score > 2.0)",
        "*1/*1 (Normal Metabolizer - Baseline Metabolic Velocity)", 
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
    st.markdown("<div class='hud-header'>📊 3. End-Organ Clearances & Safety</div>", unsafe_allow_html=True)
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

# ─── SYSTEM PHARMACOLOGY KINETIC ARCHITECTURE ENGINE ────────────────────────
gender_multiplier = 0.85 if gender == "Female" else 1.0
calculated_crcl = round(((140 - age) * weight) / (72 * creatinine) * gender_multiplier, 1)
ke = 0.025 if calculated_crcl >= 60 else 0.042 if calculated_crcl >= 30 else 0.068

if "*4/*4" in cyp2d6_profile: base_flux = 6.8
elif "*1/*10" in cyp2d6_profile: base_flux = 12.5
elif "*1/*1" in cyp2d6_profile: base_flux = 26.2
else: base_flux = 36.8  

if "CYP2C19*2/*2" in cyp2c9_c19_profile: base_flux *= 0.80
if "SULT1A1 Deletion" in sult1a1_cnv: base_flux *= 0.70
elif "SULT1A1 Amplification" in sult1a1_cnv: base_flux *= 1.20

if "Paroxetine" in cyp2d6_inhibitor: base_flux *= 0.12  
elif "Bupropion" in cyp2d6_inhibitor: base_flux *= 0.28
elif "Sertraline" in cyp2d6_inhibitor: base_flux *= 0.60
if "Rifampicin" in cyp3a4_modulator: base_flux *= 0.40  
elif "Ketoconazole" in cyp3a4_modulator: base_flux *= 1.30

if "Non-Alcoholic Fatty Liver Disease" in comorbidities: base_flux *= 0.75
hys_law_triggered = (serum_ast > 120 or serum_alt > 120) and (total_bilirubin > 2.0)
if hys_law_triggered: base_flux *= 0.30

calculated_endoxifen = round(base_flux * compliance, 2)
time_axis = list(range(1, 31))
kinetics_curve = [round(base_flux * compliance * (1 - np.exp(-ke * t)), 2) for t in time_axis]

chart_dataframe = pd.DataFrame({
    'Active Endoxifen Level (ng/mL)': kinetics_curve,
    'CPIC Efficacy Threshold Floor': [5.97] * 30
}, index=time_axis)

# ─── HIGH-CLINICAL STRATEGY DECISION ENGINE (CPIC / ASCO / ESMO) ────────────
clinical_guideline_source = "CPIC Guidelines (2023 Focused Update) & ASCO/ESMO Endocrine Mandates"

if "Negative Status" in er_status:
    suggested_drug = "Non-Endocrine Regimens (Anthracyclines/Taxanes or Target-directed Biologics)"
    suggested_dose = "Discontinue Tamoxifen Completely (0.0 mg)"
    clinical_directive = "CRITICAL CONTRAINDICATION: Tumor presents as ERα-Negative. Endocrine therapy targets are absent, predicting 100% downstream therapeutic futility."
    regimen_action = "Pivot to medical oncology standard cytotoxic chemotherapy paradigms immediately."
    alert_type = "error"
elif hys_law_triggered:
    suggested_drug = "Endocrine Therapy Interruption"
    suggested_dose = "Absolute Clinical Hold (0.0 mg)"
    clinical_directive = "ACUTE DILI HAZARD: Patient criteria trigger Hy's Law (Transaminases >3x ULN combined with Total Bilirubin >2x ULN). Fulminant hepatic failure risk is high."
    regimen_action = "Immediately suspend all endocrine variables. Initiate baseline hepatic recovery metrics and clear all alternate metabolic shunts."
    alert_type = "error"
elif calculated_endoxifen < 5.97:
    if "*4/*4" in cyp2d6_profile or "Paroxetine" in cyp2d6_inhibitor:
        suggested_drug = "Aromatase Inhibitor Switch (e.g., Anastrozole / Letrozole)"
        suggested_dose = "Anastrozole 1mg PO Daily (+ GnRH analogue if premenopausal)"
        clinical_directive = "CPIC THERAPEUTIC FAILURE ALERT: Poor CYP2D6 metabolizer status or profound competitive drug inhibition drops active Endoxifen levels below the 5.97 ng/mL efficacy floor."
        regimen_action = "Per CPIC 2023 mandates, switch alternative endocrine vector to an Aromatase Inhibitor axis to bypass the invalidated hepatic Phase-I pathway."
        alert_type = "warning"
    else:
        suggested_drug = "Tamoxifen (Optimized Dose Escalation Strategy)"
        suggested_dose = "Tamoxifen 40mg PO Daily (Split into 20mg BID)"
        clinical_directive = "SUB-OPTIMAL EXPOSURE INDICATION: Endoxifen levels fail to secure the therapeutic window baseline due to Intermediate Metabolism or compliance drops."
        regimen_action = "Escalate standard Tamoxifen profile to 40mg daily under precise monitoring, and optimize patient adherence protocols."
        alert_type = "warning"
else:
    suggested_drug = "Tamoxifen (Standard Maintenance Profile)"
    suggested_dose = "Tamoxifen 20mg PO Daily"
