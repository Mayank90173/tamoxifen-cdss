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

# Clearance Constant calculation based on Renal Profile
ke = 0.025 if calculated_crcl >= 60 else 0.042 if calculated_crcl >= 30 else 0.068

# Base Flux mapping for Tamoxifen to Active Endoxifen (ng/mL) transformation
if "*4/*4" in cyp2d6_profile: base_flux = 6.8
elif "*1/*10" in cyp2d6_profile: base_flux = 12.5
elif "*1/*1" in cyp2d6_profile: base_flux = 26.2
else: base_flux = 36.8  # Ultra-rapid metabolizer

# PGx Modifiers mapping
if "CYP2C19*2/*2" in cyp2c9_c19_profile: base_flux *= 0.80
if "SULT1A1 Deletion" in sult1a1_cnv: base_flux *= 0.70
elif "SULT1A1 Amplification" in sult1a1_cnv: base_flux *= 1.20

# DDI Modifiers mapping
if "Paroxetine" in cyp2d6_inhibitor: base_flux *= 0.12  # Complete phenoconversion to poor metabolizer
elif "Bupropion" in cyp2d6_inhibitor: base_flux *= 0.28
elif "Sertraline" in cyp2d6_inhibitor: base_flux *= 0.60
if "Rifampicin" in cyp3a4_modulator: base_flux *= 0.40  # Shunts to alternate low affinity targets
elif "Ketoconazole" in cyp3a4_modulator: base_flux *= 1.30

# Metabolic adjustments for Liver Disease & DILI
if "Non-Alcoholic Fatty Liver Disease" in comorbidities: base_flux *= 0.75
hys_law_triggered = (serum_ast > 3 * 40 or serum_alt > 3 * 40) and (total_bilirubin > 2.0)
if hys_law_triggered: base_flux *= 0.30

# Steady-state kinetic integration
calculated_endoxifen = round(base_flux * compliance, 2)
time_axis = list(range(1, 31))
kinetics_curve = [round(base_flux * compliance * (1 - np.exp(-ke * t)), 2) for t in time_axis]

chart_dataframe = pd.DataFrame({
    'Active Endoxifen Level (ng/mL)': kinetics_curve,
    'CPIC Efficacy Threshold Floor': [5.97] * 30
}, index=time_axis)

# ─── SYSTEM DYNAMICS MATRICES (RECEPTORS & TOXICOLOGY) ───────────────────────
st.write("---")
tab1, tab2, tab3 = st.tabs(["🎯 Receptor Optimization Mapping", "⚠️ Advanced Toxicological Profiling", "📋 Clinical Decision Directives"])

with tab1:
    st.markdown("### 🧬 Systemic Receptor Occupancy & Target Dynamics")
    
    # Mathematical models representing competitive inhibition metrics
    er_affinity = "100%" if "Positive" in er_status else "0% (Absolute Pathway Invalidation)"
    cyp2d6_saturation = "92% Saturation" if "Paroxetine" in cyp2d6_inhibitor or "Bupropion" in cyp2d6_inhibitor else "Minimal / Control Baseline"
    
    r_col1, r_col2 = st.columns(2)
    with r_col1:
        st.markdown(f"""
        <div class="metric-card">
            <h5>Nuclear Estrogen Receptor Alpha (ERα) Target Affinity</h5>
            <h2 style='color:#38bdf8;'>{er_affinity}</h2>
            <p style='font-size:12px; color:#94a3b8;'>Tamoxifen must undergo metabolic bioactivation into 4-hydroxy-tamoxifen and <strong>Endoxifen</strong> to achieve 30-100x higher binding affinity to ERα than parent compound.</p>
        </div>
        """, unsafe_allow_html=True)
    with r_col2:
        st.markdown(f"""
        <div class="metric-card">
            <h5>CYP2D6 Catalytic Complex Competitive Saturation</h5>
            <h2 style='color:#fbbf24;'>{cyp2d6_saturation}</h2>
            <p style='font-size:12px; color:#94a3b8;'>Co-administration of SSRIs/SNRIs blocks the substrate binding pocket of the CYP2D6 enzyme, forcing chemical phenoconversion regardless of genetic wildtype.</p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("### ☠️ Multi-Organ Systems Toxicity Quantitation Matrix")
    
    # Calculate relative toxicity scores
    dili_score = 95 if hys_law_triggered else (45 if "Non-Alcoholic Fatty Liver Disease" in comorbidities else 15)
    thrombotic_score = 85 if "Deep Vein Thrombosis (DVT Risk)" in comorbidities else 25
    uterine_hyperplasia_score = 75 if "Endometrial Hyperplasia Hyper-proliferation" in comorbidities else 20
    
    t_col1, t_col2, t_col3 = st.columns(3)
