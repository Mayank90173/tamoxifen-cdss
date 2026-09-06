import streamlit as st
import numpy as np
import pandas as pd
import io

# Safe Dependency Loader to avoid runtime script failures on Streamlit Cloud
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    reportlab_available = True
except ImportError:
    reportlab_available = False

# 1. Page Configuration & Swiss Base Interface Setup
st.set_page_config(
    page_title="Zurich Translational Systems Pharmacology Command Center", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Tech Cybernetic Medical HUD Aesthetic (Pure CSS Standard Formatting)
st.markdown("""
    <style>
    .stApp { background-color: #060913; color: #f8fafc; }
    h1, h2, h3, h4, p, span, label, div { font-family: 'Inter', system-ui, sans-serif; }
    
    .swiss-premium-banner {
        background: linear-gradient(135deg, #022c22 0%, #0b1329 50%, #1e1b4b 100%);
        border-radius: 20px; padding: 2.5rem; position: relative; overflow: hidden;
        border: 1px solid rgba(16, 185, 129, 0.2);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7); margin-bottom: 2.5rem;
    }
    .system-status { font-size: 11px; font-family: monospace; text-transform: uppercase; letter-spacing: 1px; color: #10b981; font-weight: bold; }
    .swiss-card {
        background: rgba(17, 24, 39, 0.7); border-radius: 16px; padding: 2rem;
        border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 2rem;
    }
    .disclaimer-box {
        background-color: rgba(239, 68, 68, 0.04); border: 1px dashed rgba(239, 68, 68, 0.3);
        border-radius: 10px; padding: 1.2rem; margin-top: 2rem; font-size: 12px; color: #cbd5e1; line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="swiss-premium-banner">
        <div style="padding-left: 0.5rem;">
            <span class="system-status">✦ CLINICAL TRANSLATIONAL ONCOLOGY HUB // ACADEMIC RESEARCH SIMULATION PARADIGM</span>
            <h1 style='color: #ffffff !important; margin: 5px 0 0 0; font-size:32px; font-weight:800; letter-spacing:-0.5px;'>🧬 TRANSLATIONAL SYSTEMS PHARMACOLOGY PLATFORM</h1>
            <p style='color: #94a3b8 !important; margin: 8px 0 0 0; font-size:14px; font-family: monospace;'>
                H-Informatics Core Architecture • Lead PV Portfolio: Dr. Mayank Virmani | PharmD & PV Scientist
            </p>
        </div>
    </div>
""", unsafe_allow_html=True)

if 'patient_ledger' not in st.session_state:
    st.session_state.patient_ledger = []

# Main Input Interface Grid Setup
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📋 1. Patient Profile & Tumor Core")
    pt_id = st.text_input("Patient System Hash ID", "ZRH-2026-9843X")
    age = st.slider("Chronological Age (Years)", 18, 100, 64)
    weight = st.slider("Total Mass Target (kg)", 35, 150, 82)
    gender = st.radio("Biological Configuration", ["Female", "Male"], horizontal=True)
    diet_preference = st.radio("Patient Dietary Vector Configuration", ["Vegetarian Profile", "Non-Vegetarian Profile"], horizontal=True)
    
    cyp2d6_profile = st.selectbox("CYP2D6 Genomic Architecture (CPIC Target Axis)", [
        "*1xN/*1 (Ultra-rapid Metabolizer - Functional Activity Score: >2.0)",
        "*1/*1 (Normal Metabolizer - Baseline Metabolic Velocity)", 
        "*1/*10 (Intermediate Metabolizer - Impaired Flux Spectrum)", 
        "*4/*4 (Null Allele - Poor Metabolizer - Total Phenoconversion)"
    ])
    er_status = st.radio("Estrogen Receptor Nuclear Expression (ERα)", ["Positive Status", "Negative Status"], horizontal=True)

with col2:
    st.markdown("### 🧬 2. Extended Deep PGx Secondary Axis")
    cyp2c9_c19_profile = st.selectbox("CYP2C9 / CYP2C19 Parallel Shunt Velocity", [
        "Wild-Type / Extensive Turnover (Normal Baseline)",
        "CYP2C19*2/*2 Poor Metabolizer (Impaired 4-Hydroxy Intermediate Conversion)",
        "CYP2C9*3 Carrier (Altered Alternate Metabolite Shunting Clearance)"
    ])
    sult1a1_cnv = st.selectbox("SULT1A1 Copy Number Variations (Phase II Conjugation)", [
        "Normal Copy Number (2 Copies - Standard Active Sulfation)",
        "SULT1A1 Deletion Variant (Low Active Endoxifen Bioavailability)",
        "SULT1A1 Amplification Variant (>3 Copies - Accelerated Clearance Vector)"
    ])
    
    st.markdown("### 💊 Multi-Pathway Xenobiotic DDIs")
    cyp2d6_inhibitor = st.selectbox("CYP2D6 Potent Core Inhibitors", [
        "None / Sub-clinical",
        "Paroxetine / Fluoxetine (Irreversible Structural Invalidation)",
        "Bupropion / Quinidine (High Affinity Competitive Capture)",
        "Sertraline / Duloxetine (Moderate Pathway Saturation)"
    ])
    cyp3a4_modulator = st.selectbox("Secondary CYP3A4 Pathway Competitors", [
        "None / Normal Turnover",
        "Rifampicin (Extreme CYP3A4 Enzyme Induction Hazard)",
        "Ketoconazole (Severe Clearance Suppression Matrix)"
    ])

with col3:
    st.markdown("### 📊 3. End-Organ Load & Morbidities")
    creatinine = st.number_input("Serum Creatinine Clear Marker (mg/dL)", min_value=0.2, max_value=12.0, value=1.40, step=0.05)
    serum_ast = st.number_input("Hepatic Transaminase AST (U/L)", min_value=5, max_value=3000, value=145, step=5)
    serum_alt = st.number_input("Hepatic Transaminase ALT (U/L)", min_value=5, max_value=3000, value=165, step=5)
    total_bilirubin = st.number_input("Total Bilirubin Mass Fraction (mg/dL)", min_value=0.1, max_value=20.0, value=2.60, step=0.1)
    
    comorbidities = st.multiselect("Active Pathological Overlays", [
        "Deep Vein Thrombosis (DVT Risk)",
        "Endometrial Hyperplasia Hyper-proliferation",
        "Non-Alcoholic Fatty Liver Disease (NAFLD)",
        "Severe Retinopathy & Macular Degradation"
    ], default=["Non-Alcoholic Fatty Liver Disease (NAFLD)"])
    
    compliance = st.slider("Adherence Control (MEMS Smart-Cap %)", 10, 100, 85) / 100.0
    days_on_therapy = st.number_input("Duration Cycle Status (Days Active)", min_value=1, max_value=730, value=24)

# --- ADVANCED PHARMACOLOGICAL METABOLIC DEEP KINETIC ENGINE ---
gender_multiplier = 0.85 if gender == "Female" else 1.0
calculated_crcl = round(((140 - age) * weight) / (72 * creatinine) * gender_multiplier, 1)
ke = 0.028 if calculated_crcl >= 60 else 0.045 if calculated_crcl >= 30 else 0.065

# 1. Primary CYP2D6 Pathway Flux Calculations
if "*4/*4" in cyp2d6_profile: base_flux = 7.2
elif "*1/*10" in cyp2d6_profile: base_flux = 13.8
elif "*1/*1" in cyp2d6_profile: base_flux = 24.5
else: base_flux = 34.0  

# 2. Deep PGx Modifications
if "CYP2C19*2/*2" in cyp2c9_c19_profile: base_flux *= 0.82 
elif "CYP2C9*3" in cyp2c9_c19_profile: base_flux *= 0.90
if "SULT1A1 Deletion" in sult1a1_cnv: base_flux *= 0.75 
elif "SULT1A1 Amplification" in sult1a1_cnv: base_flux *= 1.15 

# 3. DDI Interferences
if "Paroxetine" in cyp2d6_inhibitor: base_flux *= 0.15 
elif "Bupropion" in cyp2d6_inhibitor: base_flux *= 0.30
elif "Sertraline" in cyp2d6_inhibitor: base_flux *= 0.65
if "Rifampicin" in cyp3a4_modulator: base_flux *= 0.45 
elif "Ketoconazole" in cyp3a4_modulator: base_flux *= 1.25 

if "Non-Alcoholic Fatty Liver Disease" in comorbidities: base_flux *= 0.80

hys_law_triggered = (serum_ast > 120 or serum_alt > 120) and (total_bilirubin > 2.0)
if hys_law_triggered: base_flux *= 0.35

calculated_endoxifen = round(base_flux * compliance * (1 - np.exp(-ke * days_on_therapy)), 2)
time_axis = list(range(1, 31))
kinetics_curve = [round(base_flux * compliance * (1 - np.exp(-ke * t)), 2) for t in time_axis]

# Secure Native Chart Builders to avoid canvas failures
chart_dataframe = pd.DataFrame({
    'Plasma Concentration (ng/mL)': kinetics_curve,
    'CPIC Target Limit Floor': [5.97] * 30
}, index=time_axis)

# --- CLINICAL PROTOCOL JUDGEMENT LOGIC & REGIMEN STRATEGY (HCP GRADE) ---
evidence_source = "CPIC Guidelines (2023 Update) & FDA Oncology Pharmacovigilance Mandates"

if "Negative Status" in er_status:
    clinical_directive = "CRITICAL DIRECTIVE: TERMINATE TAMOXIFEN PROTOCOL IMMEDIATELY"
    dose_advice = "Tamoxifen therapy displays structural futility due to absolute absence of ERα nuclear receptor targets."
    drug_alternative = "Discontinue anti-estrogens. Evaluate alternative cytotoxic chemotherapy regimens or appropriate monoclonal antibody configurations."
    optimum_timing = "Not Applicable (Therapy Defunct)."
    ui_status_color = "#ef4444"
    status_alert = st.error
elif hys_law_triggered or "Deep Vein Thrombosis (DVT Risk)" in comorbidities:
    clinical_directive = "CRITICAL DIRECTIVE: MANDATORY MEDICAL SUSPENSION ADVISED"
    dose_advice = "Hold all active endocrine dosing vectors immediately to mitigate catastrophic safety events."
    drug_alternative = "🚨 EMERGENCY STAT. Severe Drug-Induced Liver Injury (Hy's Law Protocol) or active acute deep vein thrombosis. Switch to alternate non-estrogenic lines once transaminase levels stabilize."
    optimum_timing = "Immediate Discontinuation Vector Triggered."
    ui_status_color = "#ef4444"
    status_alert = st.error
elif "*4/*4" in cyp2d6_profile or "Paroxetine" in cyp2d6_inhibitor:
    clinical_directive = "CRITICAL DIRECTIVE: ENZYME PATHWAY BLOCKADE - PERMANENT AGENT SWITCH REQUIRED"
    dose_advice = "Dose escalation of Tamoxifen to 40mg daily will fail completely due to functional absence of the CYP2D6 metabolizing loop (Phenoconversion Matrix)."
    drug_alternative = "Discontinue Tamoxifen. Switch patient immediately to third-generation Aromatase Inhibitors: Anastrozole 1mg orally once daily (QD) OR Letrozole 2.5mg orally once daily (QD)."
    optimum_timing = "Administer selected Aromatase Inhibitor consistently in the MORNING (AM) to minimize skeletal-arthralgia side effect profiles."
    ui_status_color = "#ef4444"
