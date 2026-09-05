import streamlit as st
import numpy as np
import pandas as pd
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# 1. Premium Institutional Page & Swiss UI Setup
st.set_page_config(
    page_title="Zurich Translational Systems Pharmacology Command Center", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Core Cybernetic HUD Styling Layout Matrix
st.markdown("""
    <style>
    .stApp { background-color: #060913; color: #f8fafc; }
    h1, h2, h3, h4, p, span, label, div { font-family: 'Inter', system-ui, sans-serif; }
    
    .swiss-premium-banner {
        background: linear-gradient(135deg, #022c22 0%, #0b1329 50%, #1e1b4b 100%);
        border-radius: 20px; padding: 2.5rem; position: relative; overflow: hidden;
        border: 1px solid rgba(16, 185, 129, 0.2);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); margin-bottom: 2.5rem;
    }
    .system-status { font-size: 11px; font-family: monospace; text-transform: uppercase; letter-spacing: 1px; color: #10b981; font-weight: bold; }
    .swiss-card {
        background: rgba(17, 24, 39, 0.7); border-radius: 16px; padding: 2rem;
        border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="swiss-premium-banner">
        <span class="system-status">✦ SWISS CLINICAL PHARMACOGENOMICS COMMAND UNIT // ADVANCED DEEP PGX EDITION</span>
        <h1 style='color: #ffffff !important; margin: 5px 0 0 0; font-size:32px; font-weight:800; letter-spacing:-0.5px;'>🧬 TRANSLATIONAL SYSTEMS PHARMACOLOGY DASHBOARD</h1>
        <p style='color: #94a3b8 !important; margin: 8px 0 0 0; font-size:14px; font-family: monospace;'>
            H-Informatics Engine • Lead Portfolio Architecture: Dr. Mayank Virmani | PharmD & PV Scientist
        </p>
    </div>
""", unsafe_allow_html=True)

if 'patient_ledger' not in st.session_state:
    st.session_state.patient_ledger = []

# Main Layout Input Fields Setup
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📋 1. Patient Profile & Core Genotype")
    pt_id = st.text_input("Unique Patient System Hash ID", "ZRH-2026-9843X")
    age = st.slider("Patient Chronological Age", 18, 100, 64)
    weight = st.slider("Total Mass Target (kg)", 35, 150, 82)
    gender = st.radio("Biological Configuration", ["Female", "Male"], horizontal=True)
    
    cyp2d6_profile = st.selectbox("CYP2D6 Genomic Architecture (CPIC Tier-1)", [
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
        "CYP2C19*2/*2 Poor Metabolizer (Impaired 4-Hydroxy-Tamoxifen Intermediate Conversion)",
        "CYP2C9*3 Carrier (Altered Alternate Metabolite Shunting Clearance)"
    ])
    sult1a1_cnv = st.selectbox("SULT1A1 Copy Number Variations (Phase II Conjugation)", [
        "Normal Copy Number (2 Copies - Standard Active Sulfation)",
        "SULT1A1 Deletion Variant (Low Active Endoxifen-Sulfonate Bioavailability)",
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
    total_bilirubin = st.number_input("Total Bilirubin Mass Fraction (mg/dL)", min_value=0.1, max_value=20.0, value=2.6, step=0.1)
    
    comorbidities = st.multiselect("Active Pathological Overlays", [
        "Deep Vein Thrombosis (DVT Cluster Risk)",
        "Endometrial Hyperplasia Hyper-proliferation",
        "Non-Alcoholic Fatty Liver Disease (NAFLD)",
        "Severe Retinopathy & Macular Degradation"
    ], default=["Non-Alcoholic Fatty Liver Disease (NAFLD)"])
    
    compliance = st.slider("Adherence Control (MEMS Smart-Cap %)", 10, 100, 85) / 100.0
    days_on_therapy = st.number_input("Duration Cycle Status (Days Active)", min_value=1, max_value=730, value=24)

# --- PHARMACOLOGY DEEP DEEP METABOLIC KINETIC ENGINE ---
gender_multiplier = 0.85 if gender == "Female" else 1.0
calculated_crcl = round(((140 - age) * weight) / (72 * creatinine) * gender_multiplier, 1)
ke = 0.028 if calculated_crcl >= 60 else 0.045 if calculated_crcl >= 30 else 0.065

# 1. Primary CYP2D6 Pathway Flux Calculation
if "*4/*4" in cyp2d6_profile: base_flux = 7.2
elif "*1/*10" in cyp2d6_profile: base_flux = 13.8
elif "*1/*1" in cyp2d6_profile: base_flux = 24.5
else: base_flux = 34.0  

# 2. Deep PGx Phase I Parallel Shunt & Phase II Sulfation Modifications
if "CYP2C19*2/*2" in cyp2c9_c19_profile: base_flux *= 0.82 
elif "CYP2C9*3" in cyp2c9_c19_profile: base_flux *= 0.90

if "SULT1A1 Deletion" in sult1a1_cnv: base_flux *= 0.75 
elif "SULT1A1 Amplification" in sult1a1_cnv: base_flux *= 1.15 

# 3. Xenobiotic Interactions DDI Multipliers
if "Paroxetine" in cyp2d6_inhibitor: base_flux *= 0.15 
elif "Bupropion" in cyp2d6_inhibitor: base_flux *= 0.30
elif "Sertraline" in cyp2d6_inhibitor: base_flux *= 0.65

if "Rifampicin" in cyp3a4_modulator: base_flux *= 0.45 
elif "Ketoconazole" in cyp3a4_modulator: base_flux *= 1.25 

if "Non-Alcoholic Fatty Liver Disease" in comorbidities: base_flux *= 0.80

hys_law_triggered = (serum_ast > 120 or serum_alt > 120) and (total_bilirubin > 2.0)
if hys_law_triggered: base_flux *= 0.35

calculated_endoxifen = round(base_flux * compliance * (1 - np.exp(-ke * days_on_therapy)), 2)

# Native Uncrashable Streamlit Chart Data Builder Setup
time_axis = list(range(1, 31))
kinetics_curve = [round(base_flux * compliance * (1 - np.exp(-ke * t)), 2) for t in time_axis]
chart_dataframe = pd.DataFrame({
    'Current Dynamic Concentration (ng/mL)': kinetics_curve,
    'Therapeutic Floor Target': [5.97] * 30
}, index=time_axis)

# --- DIRECTIVE PROTOCOL VERDICT ---
if "Negative Status" in er_status:
    clinical_directive = "TERMINATE ENDOCRINE SYSTEM PROTOCOL IMMEDIATELY"
    directive_notes = "Target ERα receptor architecture is entirely absent. Tamoxifen lacks biological binding efficacy."
    status_alert = st.error
elif hys_law_triggered or "Deep Vein Thrombosis (DVT Cluster Risk)" in comorbidities:
    clinical_directive = "CRITICAL MEDICAL SUSPENSION ORDERED"
    directive_notes = "🚨 IMMEDIATE SUSPENSION. Active Hy's Law indicators or profound peripheral thromboembolic parameters met."
    status_alert = st.error
elif calculated_endoxifen < 5.97:
    clinical_directive = "SUB-THERAPEUTIC PHARMACOKINETIC SPECTRUM DETECTED"
    directive_notes = f"Current concentration profile ({calculated_endoxifen} ng/mL) scales below the targeted 5.97 ng/mL threshold."
    status_alert = st.warning
else:
    clinical_directive = "OPTIMAL THERAPEUTIC MAINTENANCE STABILIZED"
    directive_notes = f"Steady-state target successfully achieved ({calculated_endoxifen} ng/mL). Therapeutic window optimized."
    status_alert = st.success

# --- 🎯 INTERACTIVE MAIN EVALUATION HUD PANEL ---
st.header("📊 4. Real-Time Clinical Evaluation Panel")
m1, m2, m3 = st.columns(3)
m1.metric("Calculated Renal CrCl", f"{calculated_crcl} mL/min")
m2.metric("Steady-State Endoxifen", f"{calculated_endoxifen} ng/mL")
m3.metric("Minimum Therapeutic Cutoff", "5.97 ng/mL")

st.markdown("#### Operational Directive Command")
status_alert(f"**{clinical_directive}** — {directive_notes}")

# --- 📈 NATIVE UNCRASHABLE PHARMACOKINETIC SIMULATION MATRIX ---
st.header("📈 5. Projected 30-Day Pharmacokinetic (PK) Accumulation Curve")
st.line_chart(chart_dataframe, height=300, use_container_width=True)

# --- 📑 DYNAMIC SYSTEMATIC CLINICAL REPORT ---
st.header("📑 6. Systematic Deep PGx Translation Report")
st.markdown(f"""
    <div class="swiss-card" style="background-color: #0d1527; border-left: 5px solid #38bdf8; margin-bottom: 2rem;">
        <h4 style="color:#38bdf8; margin-top:0; font-weight:700;">🔬 DEEP GENOMIC TRANSLATIONAL PHARMACOLOGY DISPATCH</h4>
        <p style="font-size:14px; line-height:1.6; color:#e2e8f0; margin-bottom:12px;">
            <b>Biotransformation Analysis:</b> Patient <b>{pt_id}</b> has been evaluated across an expanded pharmacogenomics network. Primary activation velocity is controlled by a <b>{cyp2d6_profile}</b> background, with active secondary phase I pathways shunted by <b>{cyp2c9_c19_profile}</b> configurations and phase II active conjugation modulated via <b>{sult1a1_cnv}</b> vectors. 
