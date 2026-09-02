import streamlit as st
import numpy as np

# 1. Advanced Institutional Page Settings
st.set_page_config(page_title="Translational Systems Pharmacology Command Center", layout="wide", initial_sidebar_state="collapsed")

# 🧬 Ultra-Premium Hospital Dashboard CSS - Soft Slate, Deep Teal & Animated Molecular Receptor Matrix
st.markdown("""
    <style>
    /* Executive Deep Space Slate Theme - Maximum Eye Comfort */
    .stApp { background-color: #0b0f19; color: #f1f5f9; }
    h1, h2, h3, h4, p, span, label, div { font-family: 'Inter', system-ui, sans-serif; }
    
    /* Input Box Styles */
    div[data-baseweb="select"] > div { background-color: #111827 !important; color: #ffffff !important; border: 1px solid #1f2937 !important; border-radius: 8px !important; }
    div[data-baseweb="select"] * { color: #ffffff !important; }
    input { background-color: #111827 !important; color: #ffffff !important; border: 1px solid #1f2937 !important; }
    
    /* 🟫 High-Tech Animated Hepatic Receptor Compartment Banner */
    .liver-visual-canvas {
        background: linear-gradient(135deg, #1e1b4b 0%, #042f2e 100%);
        border-radius: 16px; padding: 2.5rem; position: relative; overflow: hidden;
        border: 2px solid #0d9488; box-shadow: 0 20px 40px rgba(13, 148, 136, 0.2); margin-bottom: 2.5rem;
    }
    .clinical-banner h1 { color: #ffffff !important; font-weight: 700 !important; margin: 0; }
    
    /* 🔴 Floating Parent Drug Atoms and Bound Metabolite Vectors */
    .binding-atom-1, .binding-atom-2, .receptor-pocket {
        position: absolute; border-radius: 50%;
    }
    .binding-atom-1 {
        width: 14px; height: 14px; background: #38bdf8; top: 40%; left: -5%;
        animation: receptorLock 6s cubic-bezier(0.4, 0, 0.2, 1) infinite; box-shadow: 0 0 15px #38bdf8;
    }
    .binding-atom-2 {
        width: 10px; height: 10px; background: #f43f5e; top: 65%; left: -10%;
        animation: receptorLock 4s linear infinite 1.5s; box-shadow: 0 0 15px #f43f5e;
    }
    .receptor-pocket {
        width: 40px; height: 40px; border: 2px dashed #10b981; top: 45%; right: 20%;
        background: rgba(16, 185, 129, 0.1); animation: pulsePocket 2s infinite alternate;
    }
    
    @keyframes receptorLock {
        0% { left: -5%; transform: scale(1) rotate(0deg); }
        70% { left: 78%; top: 47%; transform: scale(1.4) rotate(180deg); background: #10b981; box-shadow: 0 0 25px #10b981; }
        100% { left: 110%; top: 50%; transform: scale(1); }
    }
    @keyframes pulsePocket {
        0% { box-shadow: 0 0 5px rgba(16, 185, 129, 0.3); transform: scale(1); }
        100% { box-shadow: 0 0 20px rgba(16, 185, 129, 0.7); transform: scale(1.1); }
    }
    
    /* Institutional Advisory Cards */
    .diagnostic-report-frame {
        background-color: #111827; border-radius: 14px; padding: 2rem;
        border: 1px solid #1f2937; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3); margin-top: 2rem;
    }
    .report-section-header {
        font-size: 1.15rem; font-weight: 700; color: #0ea5e9; border-bottom: 2px solid #1f2937;
        padding-bottom: 0.5rem; margin-bottom: 1rem; margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Main Executive Banner with Live Molecular Binding Stream
st.markdown("""
    <div class="liver-visual-canvas">
        <div class="binding-atom-1"></div>
        <div class="binding-atom-2"></div>
        <div class="receptor-pocket"></div>
        <h1 style='color: #ffffff !important; margin:0; font-size:28px; font-weight:800;'>🧬 CLINICAL PHARMACOLOGY COMMAND CENTER</h1>
        <p style='color: #94a3b8 !important; margin: 8px 0 0 0; font-size:14px; font-family: monospace;'>
            Active Core: [HEPATIC CYOTOCHROME P450 RECEPTOR BINDING MATRIX & PHASE I/II ADME LIVE TRACER]
        </p>
    </div>
""", unsafe_allow_html=True)

# Layout Setup - 3 Column Input Grid
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📋 Genotype & Baseline Stratification")
    age = st.slider("Patient Age (Years)", 18, 90, 63)
    weight = st.slider("Patient Weight (kg)", 40, 120, 102)
    
    menopausal_status = st.selectbox("Menopausal Status Axis", [
        "Pre-Menopausal (Intact Ovarian Estrogen Feedback)",
        "Peri-Menopausal (Fluctuating Gonadotropin Loops)",
        "Post-Menopausal (Peripheral Adipose Estrogen Conversion)"
    ])
    
    serum_creatinine = st.number_input("Serum Creatinine (mg/dL) [Nephron Constant]", min_value=0.3, max_value=10.0, value=3.00, step=0.1)
    
    cyp2d6_genotype = st.selectbox("CYP2D6 Deep Allelic Variant (CPIC Target)", [
        "*1xN/*1 (Ultra-rapid Metabolizer - Activity Score: >2.0)",
        "*1/*1 (Normal Metabolizer - Default Activity Score: 2.0)", 
        "*1/*10 (Intermediate Metabolizer - Decreased Kinetic Flux)", 
        "*4/*4 (Null Function - Poor Metabolizer - Activity Score: 0.0)"
    ])
    er_expression = st.radio("ERα Nuclear Receptor Pathway Status", ["Positive", "Negative"], horizontal=True)

with col2:
    st.markdown("#### 💊 Multi-Pathway Competitive Inhibitors (DDI)")
    psych_inhibitor = st.selectbox("Mechanism-Based Suicidal Inhibitors", [
        "Amiodarone (Moderate Competitive Inhibition)",
        "Paroxetine / Fluoxetine (Irreversible Phenoconversion Inducers)",
        "None"
    ])
    thyroid_axis = st.selectbox("Thyroid Pathway Axis", ["Levothyroxine (TBG Competition Hazard)", "None"])
    metabolic_agent = st.selectbox("Glycemic Control Axis", ["Metformin (OCT1 Translocalization Inter-play)", "None"])
    cv_agent = st.selectbox("Cardiovascular Substrate Clash", ["Metoprolol (Competitive CYP2D6 Affinity)", "None"])

with col3:
    st.markdown("#### 📊 Real-World Lab Biomarkers")
    adherence = st.slider("Medication Adherence (MEMS Cap Telemetry %)", 10, 100, 70) / 100.0
    days_on_therapy = st.number_input("Days Since Treatment Initiation", min_value=1, max_value=365, value=1)
    
    serum_ast = st.number_input("Serum AST Level (U/L) [Dynamic Range: 5-2000]", min_value=5, max_value=2000, value=50, step=5)
    serum_alt = st.number_input("Serum ALT Level (U/L) [Dynamic Range: 5-2000]", min_value=5, max_value=2000, value=45, step=5)
    serum_tg = st.number_input("Serum Triglycerides (mg/dL) [Lipid Biomarker]", min_value=50, max_value=800, value=233, step=5)
    
    prior_morbidity = st.multiselect("Prior Chronic Pathological Architecture", ["Deep Vein Thrombosis (DVT)", "Fatty Liver (NAFLD)", "Retinopathy"])

st.write("---")

# 🔘 THE GRAND MASTER SUBMIT BUTTON requested by the Pharmacologist
run_engine = st.button("🚀 EXECUTE SYSTEMS PHARMACOLOGY SIMULATION ENGINE", use_container_width=True)

if run_engine:
    # --- CORE PHARMACOLOGY COMPUTATION MATRIX ---
    cr_cl = round(((140 - age) * weight) / (72 * serum_creatinine) * 0.85, 1)

    if "*4/*4" in cyp2d6_genotype: base_metabolite = 8.8
    elif "*1/*1" in cyp2d6_genotype: base_metabolite = 22.3
    elif "*1/*10" in cyp2d6_genotype: base_metabolite = 14.0
    else: base_metabolite = 30.5  # Ultra-rapid base

    # DDI & Suicide Phenoconversion Multipliers
    if "Paroxetine" in psych_inhibitor: base_metabolite *= 0.25 
    elif "Amiodarone" in psych_inhibitor: base_metabolite *= 0.60
    if "Metoprolol" in cv_agent: base_metabolite *= 0.85

    liver_stress = "Fulminant Hepatotoxicity" if (serum_ast >= 500 or serum_alt >= 500) else "Severe" if (serum_ast >= 150 or serum_alt >= 150) else "Normal"
    if liver_stress == "Severe": base_metabolite *= 0.75
    elif liver_stress == "Fulminant Hepatotoxicity": base_metabolite *= 0.40
    if serum_tg >= 250: base_metabolite *= 0.90

    calculated_endoxifen = round(base_metabolite * adherence * (1 - np.exp(-0.024 * days_on_therapy)), 1)
    t_half = 14 if cr_cl >= 60 else 24 if cr_cl >= 30 else 48

    base_survival = 0.95 if "Pre" in menopausal_status else 0.88 if "Peri" in menopausal_status else 0.82
    if er_expression == "Negative": base_survival *= 0.60
    survival_percentage = round(base_survival * 100, 1)

    # Guideline Management Determination
    if "Negative" in er_expression:
        suggested_regimen = "Terminate Endocrine Regimen Immediately"
        regimen_timeline = "N/A - Structural absence of ERa receptor targets. Switch to alternative oncology protocols."
        guideline_source = "NCCN 2026 Adjuvant Staging Guideline"
        dose_color = "#ef4444"
    elif liver_stress == "Fulminant Hepatotoxicity" or serum_tg >= 500:
        suggested_regimen = "Emergency Toxicological Suspension"
        regimen_timeline = "Fulminant transaminase breakdown or hypertriglyceridemia-pancreatitis crisis risk. Halt substance input."
        guideline_source = "FDA Post-Marketing Pharmacovigilance Safety Mandate"
        dose_color = "#ef4444"
    elif "Post-Menopausal" in menopausal_status and ("*4/*4" in cyp2d6_genotype or "Paroxetine" in psych_inhibitor):
        suggested_regimen = "Switch to Alternative Protocols"
        regimen_timeline = "Biotransformation blocked completely by null alleles or irreversible phenoconversion. Alternative pathways preferred."
        guideline_source = "CPIC 2026 Consensus / NCCN Endocrine Update"
        dose_color = "#ef4444"
    elif days_on_therapy < 21:
        suggested_regimen = "Maintain Standard Protocol (Observation Phase)"
        regimen_timeline = f"Current active metabolite is sub-therapeutic ({calculated_endoxifen} ng/mL) because Days on Therapy is {days_on_therapy}. System has NOT achieved Pharmacokinetic Steady-State. Maintain administration; do NOT alter kinetics prematurely."
        guideline_source = "ASCO / International Pharmacogenomics Consensus"
        dose_color = "#10b981"
    else:
        suggested_regimen = "Maintain Standard Maintenance"
        regimen_timeline = "Target active metabolic window met successfully. Continue standard adjuvant clinical window."
        guideline_source = "CPIC / NCCN Standard Adjuvant Protocols"
        dose_color = "#10b981"

