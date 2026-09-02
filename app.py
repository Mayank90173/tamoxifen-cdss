import streamlit as st
import numpy as np

# 1. Page Configuration for Ultra-Premium Medical Sage UI Workspace
st.set_page_config(page_title="RWD-PGx Advanced Systems Oncology Core", layout="wide", initial_sidebar_state="collapsed")

# Professional Clinical Sage-Grey & Deep Emerald Anti-Glare Palette
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; color: #1e293b; }
    h1, h2, h3, h4, p, span, label { color: #0f172a !important; font-family: 'Inter', sans-serif; }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #0f172a !important; border: 1px solid #cbd5e1 !important; }
    div[role="radiogroup"] label { color: #0f172a !important; }
    
    /* 🧬 Live High-Tech Medical Banner with Floating Biomolecules */
    .clinical-banner {
        background: linear-gradient(135deg, #064e3b 0%, #1e293b 100%);
        border-radius: 14px; padding: 2.5rem; color: #f8fafc; margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(6, 78, 59, 0.15);
        position: relative; overflow: hidden;
        border-left: 6px solid #10b981;
    }
    .clinical-banner h2 { color: #ffffff !important; font-weight: 700 !important; margin: 0; }
    
    /* Pure CSS Molecular Kinetic Simulation Nodes (100% Streamlit Cloud Safe) */
    .molecule-stream-1, .dna-fragment-2 {
        position: absolute; background: rgba(16, 185, 129, 0.4); border-radius: 50%;
    }
    .molecule-stream-1 {
        width: 16px; height: 14px; top: 35%; left: -5%;
        animation: streamWave 7s ease-in-out infinite; box-shadow: 0 0 12px #10b981;
    }
    .dna-fragment-2 {
        width: 10px; height: 10px; top: 60%; left: -8%;
        animation: streamWave 5s ease-in-out infinite 2s; box-shadow: 0 0 12px #38bdf8;
    }
    @keyframes streamWave {
        0% { left: -5%; transform: translateY(0px) scale(1); }
        50% { transform: translateY(-20px) scale(1.3); background: #38bdf8; }
        100% { left: 105%; transform: translateY(10px) scale(1); }
    }
    
    /* Advanced Medical Diagnostic Cards */
    .med-card {
        background-color: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03);
    }
    .med-card-header {
        font-size: 1.1rem; font-weight: 700; padding: 0.5rem 1rem; border-radius: 6px; color: white !important; margin-bottom: 1rem;
    }
    .guideline-tag {
        background-color: #ecfdf5; border: 1px solid #10b981; color: #065f46 !important;
        padding: 4px 10px; border-radius: 4px; font-weight: 600; font-size: 12px; display: inline-block; margin-top: 5px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="clinical-banner">
        <div class="molecule-stream-1"></div>
        <div class="dna-fragment-2"></div>
        <h2>🧬 Next-Gen RWE Systems Pharmacology & Intelligence Architecture</h2>
        <p style='color: #a7f3d0; margin: 6px 0 0 0; font-size:14px;'>Lead Innovator & Clinical Architect: Dr. Mayank Virmani | PharmD, PV Scientist Portfolio</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📋 PGx, Stratification & ADME")
    age = st.slider("Patient Age (Years)", 18, 90, 52)
    weight = st.slider("Patient Weight (kg)", 40, 120, 70)
    
    menopausal_status = st.selectbox("Menopausal Status Profiling", [
        "Pre-Menopausal (Intact Ovarian Estrogen Feedback Axis)",
        "Peri-Menopausal (Fluctuating Gonadotropin Loops)",
        "Post-Menopausal (Peripheral Adipose Estrogen Conversion Window)"
    ])
    
    serum_creatinine = st.number_input("Serum Creatinine (mg/dL) [Nephron Marker]", min_value=0.3, max_value=10.0, value=0.9, step=0.1)
    
    cyp2d6_genotype = st.selectbox("CYP2D6 Genomic Allelic Profile (CPIC Focus)", [
        "*1/*1 (Normal Metabolizer - Default Activity Score: 2.0)", 
        "*1/*10 (Intermediate Metabolizer - Decreased Conversion Kinetics)", 
        "*4/*4 (Null Function - Poor Metabolizer - Activity Score: 0.0)", 
        "*1xN/*1 (Ultra-rapid Metabolizer - Accelerated Clearance/Saturation)"
    ])
    er_expression = st.radio("ERα Nuclear Receptor Expression Status", ["Positive", "Negative"], horizontal=True)

with col2:
    st.markdown("### 💊 Concomitant Multi-Pathway DDI")
    psych_inhibitor = st.selectbox("CYP2D6 Mechanism-Based Suicidal Inhibitors", [
        "None", "Paroxetine / Fluoxetine (Irreversible Phenoconversion Induced)", "Amiodarone (Moderate Competitive Inhibition)"
    ])
    thyroid_axis = st.selectbox("Thyroid Axis Concomitant Therapy", ["None", "Levothyroxine (TBG Competition Hazard)"])
    metabolic_agent = st.selectbox("Metabolic / Glycemic Co-medication", ["None", "Metformin (OCT1 Substrate Interaction)"])
    cv_agent = st.selectbox("Antihypertensive Regimen", ["None", "Metoprolol (Competitive CYP2D6 Affinity)"])

with col3:
    st.markdown("### 📊 Real-World Biomarkers & Morbidities")
    adherence = st.slider("Medication Adherence (MEMS Smart-Cap Telemetry %)", 10, 100, 95) / 100.0
    days_on_therapy = st.number_input("Days Since Regimen Initiation (Steady-State Windows)", min_value=1, max_value=365, value=45)
    
    # 🌟 NEW UPGRADE: Expanded LFT inputs up to 2000 U/L to capture severe dynamic acute hepatitis / DILI bounds
    serum_ast = st.number_input("Serum AST Level (U/L) [Extended Dynamic Range]", min_value=5, max_value=2000, value=30, step=5)
    serum_alt = st.number_input("Serum ALT Level (U/L) [Extended Dynamic Range]", min_value=5, max_value=2000, value=35, step=5)
    serum_tg = st.number_input("Serum Triglycerides (mg/dL) [Lipid Biomarker]", min_value=50, max_value=800, value=150)
    
    prior_morbidity = st.multiselect("Prior Chronic Pathological Architecture", ["Deep Vein Thrombosis (DVT)", "Fatty Liver (NAFLD)", "Retinopathy"])

# --- CORE CLINICAL PHARMACOLOGY COMPUTATION ENGINE ---
cr_cl = round(((140 - age) * weight) / (72 * serum_creatinine) * 0.85, 1)

if "*4/*4" in cyp2d6_genotype: base_metabolite = 8.8
elif "*1/*1" in cyp2d6_genotype: base_metabolite = 22.3
elif "*1/*10" in cyp2d6_genotype: base_metabolite = 14.0
else: base_metabolite = 30.5

# DDI Modifiers
if "Paroxetine" in psych_inhibitor: base_metabolite *= 0.25 
elif "Amiodarone" in psych_inhibitor: base_metabolite *= 0.60
if "Metoprolol" in cv_agent: base_metabolite *= 0.85

# Stratified LFT Evaluation with Extended Limits
if serum_ast >= 500 or serum_alt >= 500:
    liver_stress = "Fulminant Hepatotoxicity"
    base_metabolite *= 0.40
elif serum_ast >= 150 or serum_alt >= 150:
    liver_stress = "Severe"
    base_metabolite *= 0.75
elif serum_ast >= 50 or serum_alt >= 50:
    liver_stress = "Moderate"
    base_metabolite *= 0.90
else:
    liver_stress = "Normal"

if serum_tg >= 250: base_metabolite *= 0.90

calculated_endoxifen = round(base_metabolite * adherence * (1 - np.exp(-0.024 * days_on_therapy)), 1)
t_half = 14 if cr_cl >= 60 else 24 if cr_cl >= 30 else 48

base_survival = 0.95 if "Pre" in menopausal_status else 0.88 if "Peri" in menopausal_status else 0.82
if er_expression == "Negative": base_survival *= 0.60
survival_percentage = round(base_survival * 100, 1)

# 🌟 NEW UPGRADE: Dynamic Dosing Regimen mapped to CPIC & NCCN Guidelines
if "Negative" in er_expression:
    suggested_regimen = "Terminate Endocrine Regimen Immediately"
    regimen_timeline = "Structural absence of ERa receptor targets. Route to chemotherapy paths."
    guideline_source = "NCCN 2026 Adjuvant Breast Cancer Staging Protocol"
    dose_color = "red"
elif liver_stress == "Fulminant Hepatotoxicity" or serum_tg >= 500:
    suggested_regimen = "Emergency Suspension / Halt Therapy"
    regimen_timeline = "Fulminant DILI matrix or hypertriglyceridemia-pancreatitis crisis risk. Discontinue SERM."
    guideline_source = "FDA Post-Marketing Pharmacovigilance Safety Mandate"
    dose_color = "red"
elif "Post-Menopausal" in menopausal_status and ("*4/*4" in cyp2d6_genotype or "Paroxetine" in psych_inhibitor):
    suggested_regimen = "Switch to Aromatase Inhibitors (Anastrozole 1mg/day)"
    regimen_timeline = "Biotransformation blocked by non-functional alleles or permanent phenoconversion."
    guideline_source = "CPIC 2026 Updates / NCCN Endocrine Preference Consensus"
    dose_color = "red"
elif calculated_endoxifen < 15.0 and adherence >= 0.80:
    suggested_dose_mg = 40 if liver_stress == "Normal" else 20
    suggested_regimen = f"Escalate Tamoxifen Regimen to {suggested_dose_mg} mg/day"
    regimen_timeline = "Sub-therapeutic exposure window. Maintain 40mg for 4-6 weeks to reach steady-state, then re-check TDM."
    guideline_source = "ASCO / International Tamoxifen Consensus Guideline"
    dose_color = "orange"
elif liver_stress == "Severe":
    suggested_regimen = "De-escalate Tamoxifen to 10 mg/day"
    regimen_timeline = "Restrict parameters to ease hepatic functional load until transaminases normalize below 1.5x ULN."
    guideline_source = "NCCN Supportive Organ Preservation Framework"
    dose_color = "orange"
else:
    suggested_regimen = "Maintain Standard 20 mg/day Regimen"
    regimen_timeline = "Optimal target metabolic exposure met. Continue standard adjuvant 5-year window tracking."
    guideline_source = "CPIC / NCCN Standard Adjuvant Guidelines"
    dose_color = "green"

st.write("---")
st.header("🤖 RWE Systems Pharmacology Translation Engine")

out_col1, out_col2 = st.columns(2)

with out_col1:
    st.markdown("### 📈 Pharmacokinetic & Dosing Analytics Core")
    
    # Render Dynamic Dosing Decision Panel with Guidelines Tag
    st.markdown(f"""
    <div style='background-color: white; padding: 1.5rem; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 15px;'>
        <p style='margin: 0; font-weight: 600; color: #475569;'>🎯 ALGORITHMIC DOSING DECISION MATRIX:</p>
        <h2 style='margin: 5px 0 0 0; color: {dose_color} !important; font-weight: 800; font-size:22px;'>{suggested_regimen}</h2>
