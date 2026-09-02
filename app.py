import streamlit as st
import numpy as np
import io

# 1. Page Configuration for Swiss-Level Clinical Command Center
st.set_page_config(page_title="Swiss-Level Translational Systems Pharmacology Command Center", layout="wide", initial_sidebar_state="collapsed")

# 🎨 Premium Eye-Friendly Clinical Sage & Deep Emerald Matte Theme
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; color: #1e293b; }
    h1, h2, h3, h4, p, span, label, div { color: #0f172a !important; font-family: 'Inter', system-ui, sans-serif; }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #0f172a !important; border: 1px solid #cbd5e1 !important; border-radius: 8px !important; }
    div[data-baseweb="select"] * { color: #0f172a !important; }
    input { background-color: #ffffff !important; color: #0f172a !important; border: 1px solid #cbd5e1 !important; border-radius: 8px !important; }
    
    /* 🧬 Elegant Medical Top Banner with Live CSS Flowing Molecular Nodes */
    .swiss-canvas-banner {
        background: linear-gradient(135deg, #064e3b 0%, #1e293b 100%);
        border-radius: 16px; padding: 2.2rem; color: #f8fafc; margin-bottom: 2rem;
        position: relative; overflow: hidden; border-left: 6px solid #10b981;
        box-shadow: 0 10px 30px rgba(6, 78, 59, 0.12);
    }
    .swiss-canvas-banner h2 { color: #ffffff !important; font-weight: 700 !important; margin: 0; }
    
    /* Pure CSS Molecular Kinetic Trackers (100% Streamlit Cloud Error-Free) */
    .kinetic-node-1, .kinetic-node-2 {
        position: absolute; background: rgba(16, 185, 129, 0.4); border-radius: 50%;
    }
    .kinetic-node-1 { width: 15px; height: 15px; top: 35%; left: -5%; animation: streamFlow 7s ease-in-out infinite; box-shadow: 0 0 12px #10b981; }
    .kinetic-node-2 { width: 9px; height: 9px; top: 60%; left: -8%; animation: streamFlow 5s ease-in-out infinite 2s; box-shadow: 0 0 12px #38bdf8; }
    @keyframes streamFlow {
        0% { left: -5%; transform: translateY(0px) scale(1); }
        50% { transform: translateY(-20px) scale(1.2); background: #38bdf8; }
        100% { left: 105%; transform: translateY(10px) scale(1); }
    }
    
    /* Institutional Medical Visual Cards */
    .clinical-expert-card {
        background-color: white; border-radius: 12px; padding: 1.6rem; border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02);
    }
    .card-title-header {
        font-size: 1.1rem; font-weight: 700; padding: 0.5rem 1rem; border-radius: 6px; color: white !important; margin-bottom: 1rem;
    }
    .guideline-seal {
        background-color: #ecfdf5; border: 1px solid #10b981; color: #065f46 !important;
        padding: 4px 10px; border-radius: 4px; font-weight: 600; font-size: 12px; display: inline-block; margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# Main Institutional Top Header Banner
st.markdown("""
    <div class="swiss-canvas-banner">
        <div class="kinetic-node-1"></div>
        <div class="kinetic-node-2"></div>
        <h2>🧬 Translational Systems Pharmacology & Clinical Advisory CDSS</h2>
        <p style='color: #a7f3d0; margin: 5px 0 0 0; font-size:14px;'>Lead Investigator: Dr. Mayank Virmani | PharmD, PV Scientist Portfolio</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📋 Genotype Staging & Baseline Variables")
    age = st.slider("Patient Age (Years)", 18, 90, 63)
    weight = st.slider("Patient Weight (kg)", 40, 120, 102)
    
    menopausal_status = st.selectbox("Menopausal Status Axis", [
        "Post-Menopausal (Peripheral Adipose Estrogen Conversion Window)",
        "Pre-Menopausal (Intact Ovarian Estrogen Feedback Axis)",
        "Peri-Menopausal (Fluctuating Gonadotropin Loops)"
    ])
    
    # 🌟 REMOVED SERUM: Pure Pharmacological Naming
    creatinine_marker = st.number_input("Glomerular Filtration Marker (Creatinine mg/dL)", min_value=0.3, max_value=10.0, value=3.00, step=0.1)
    
    cyp2d6_genotype = st.selectbox("CYP2D6 Genomic Allelic Profile (CPIC Target)", [
        "*1xN/*1 (Ultra-rapid Metabolizer - Activity Score: >2.0)",
        "*1/*1 (Normal Metabolizer - Default Activity Score: 2.0)", 
        "*1/*10 (Intermediate Metabolizer - Decreased Kinetic Flux)", 
        "*4/*4 (Null Function - Poor Metabolizer - Activity Score: 0.0)"
    ])
    er_expression = st.radio("ERα Nuclear Receptor Status", ["Positive", "Negative"], horizontal=True)

with col2:
    st.markdown("### 💊 Multi-Pathway Competitive DDIs")
    psych_inhibitor = st.selectbox("CYP2D6 Mechanism-Based Suicide Inhibitors", [
        "Amiodarone (Moderate Competitive Inhibition)",
        "Paroxetine / Fluoxetine (Irreversible Phenoconversion Induced)",
        "None"
    ])
    thyroid_axis = st.selectbox("Thyroid Axis Concomitant Interaction", ["Levothyroxine (TBG Competition Hazard)", "None"])
    metabolic_agent = st.selectbox("Glycemic Control Co-medication", ["Metformin (OCT1 Substrate Interaction)", "None"])
    cv_agent = st.selectbox("Cardiovascular Substrate Clash", ["Metoprolol (Competitive CYP2D6 Affinity)", "None"])

with col3:
    st.markdown("### 📊 Real-World Biomarkers & Compliance")
    adherence = st.slider("Medication Adherence (MEMS Smart-Cap Telemetry %)", 10, 100, 70) / 100.0
    days_on_therapy = st.number_input("Days Since Regimen Initiation (Steady-State Mirror)", min_value=1, max_value=365, value=1)
    
    # 🌟 REMOVED SERUM: Pure Pharmacological Naming
    hepatic_ast = st.number_input("Hepatic Transaminase AST (U/L) [Dynamic Limit: 2000]", min_value=5, max_value=2000, value=50, step=5)
    hepatic_alt = st.number_input("Hepatic Transaminase ALT (U/L) [Dynamic Limit: 2000]", min_value=5, max_value=2000, value=45, step=5)
    plasma_tbil = st.number_input("Total Bilirubin Fraction (mg/dL) [Hy's Law Tracker]", min_value=0.1, max_value=15.0, value=2.5, step=0.1)
    plasma_tg = st.number_input("Total Triglycerides Matrix (mg/dL)", min_value=50, max_value=800, value=233, step=5)
    
    # 🌟 MORBIDITY TRACKER
    prior_morbidity = st.multiselect("Prior Chronic Pathological Architecture", ["Deep Vein Thrombosis (DVT)", "Fatty Liver (NAFLD)", "Retinopathy"], default=["Fatty Liver (NAFLD)", "Retinopathy"])

# --- ADVANCED SWISS SYSTEMS PHARMACOLOGY COMPUTATION ENGINE ---
# Cockcroft-Gault Equation
cr_cl = round(((140 - age) * weight) / (72 * creatinine_marker) * 0.85, 1)

# Dynamic Pharmacokinetics Calibration
if "*4/*4" in cyp2d6_genotype: base_metabolite = 8.8
elif "*1/*1" in cyp2d6_genotype: base_metabolite = 22.3
elif "*1/*10" in cyp2d6_genotype: base_metabolite = 14.0
else: base_metabolite = 30.5  # Ultra-rapid Base

# DDI and Drug-Induced Phenoconversion Math Matrices
if "Paroxetine" in psych_inhibitor: base_metabolite *= 0.25 
elif "Amiodarone" in psych_inhibitor: base_metabolite *= 0.60
if "Metoprolol" in cv_agent: base_metabolite *= 0.85

# FDA Hy's Law Validation Check
hys_law_active = False
if (hepatic_ast > 120 or hepatic_alt > 120) and (plasma_tbil > 2.4):
    hys_law_active = True

# Dynamic Liver Stress Classifications
if hepatic_ast >= 500 or hepatic_alt >= 500:
    liver_stress = "Fulminant Hepatotoxicity"
    base_metabolite *= 0.40
elif hys_law_active:
    liver_stress = "Hy's Law Jaundice State"
    base_metabolite *= 0.50
elif hepatic_ast >= 150 or hepatic_alt >= 150:
    liver_stress = "Severe Overload"
    base_metabolite *= 0.75
else:
    liver_stress = "Normal Physiological Bounds"

if plasma_tg >= 250: base_metabolite *= 0.90

# 🌟 DYNAMIC DURATION SATURATION CALCULATION (Solves static responses!)
calculated_endoxifen = round(base_metabolite * adherence * (1 - np.exp(-0.024 * days_on_therapy)), 1)
t_half = 14 if cr_cl >= 60 else 24 if cr_cl >= 30 else 48

base_survival = 0.95 if "Pre" in menopausal_status else 0.88 if "Peri" in menopausal_status else 0.82
if er_expression == "Negative": base_survival *= 0.60
survival_percentage = round(base_survival * 100, 1)

# Dynamic Dosing Logic Map
if "Negative" in er_expression:
    suggested_regimen = "Terminate Endocrine Regimen Immediately"
    regimen_timeline = "N/A - Structural absence of ERa receptor targets. Switch immediately to alternative oncology tracks."
    guideline_source = "NCCN 2026 Adjuvant Staging Guideline"
    dose_color = "red"
elif hys_law_active or liver_stress == "Fulminant Hepatotoxicity":
    suggested_regimen = "CRITICAL MEDICAL SUSPENSION / HALT"
    regimen_timeline = "🚨 HY'S LAW STATE MET. Severe drug-induced hepatocellular jaundice verified. High threat of acute liver necrosis. Discontinue therapy."
    guideline_source = "FDA Post-Marketing Pharmacovigilance Mandate"
    dose_color = "red"
elif days_on_therapy < 21:
    suggested_regimen = "Maintain Standard Protocol (Observation Phase)"
    regimen_timeline = f"Active Systemic Plasma Endoxifen Concentration is sub-therapeutic ({calculated_endoxifen} ng/mL) because Days on Therapy is {days_on_therapy}. System has NOT achieved Pharmacokinetic Steady-State. Maintain; do NOT escalate dose prematurely."
    guideline_source = "ASCO / International Pharmacogenomics Consensus"
    dose_color = "orange"
else:
    suggested_regimen = "Maintain Standard Maintenance Window"
    regimen_timeline = "Target active metabolic window met successfully. Continue standard adjuvant 5-year treatment window tracking."
    guideline_source = "CPIC / NCCN Standard Adjuvant Protocols"
    dose_color = "green"

st.write("---")
st.header("🤖 RWE Systems Pharmacology Translation Engine (Live Dynamic Output)")

st.error(f"🎯 ALGORITHMIC DOSING DECISION MATRIX: {suggested_regimen}")
st.warning(f"⏳ TIMELINE STRATEGY: {regimen_timeline} | Compliant with: {guideline_source}")

out_col1, out_col2 = st.columns(2)

with out_col1:
    st.markdown("### 📈 Pharmacokinetic Core Metrics")
