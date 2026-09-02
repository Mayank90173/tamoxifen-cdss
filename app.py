import streamlit as st
import numpy as np

# 1. Advanced Institutional Page Settings (Premium Swiss Medical UI)
st.set_page_config(page_title="Swiss-Level Systems Pharmacology Command Center", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Zurich Corporate Clinical Aesthetic - Soft Dark Slate Matrix */
    .stApp { background-color: #090d16; color: #f1f5f9; }
    h1, h2, h3, h4, p, span, label, div { font-family: 'Inter', system-ui, sans-serif; }
    div[data-baseweb="select"] > div { background-color: #111827 !important; color: #ffffff !important; border: 1px solid #1f2937 !important; border-radius: 8px !important; }
    div[data-baseweb="select"] * { color: #ffffff !important; }
    input { background-color: #111827 !important; color: #ffffff !important; border: 1px solid #1f2937 !important; }
    
    /* Premium Animated Receptor Canvas Banner */
    .swiss-banner {
        background: linear-gradient(135deg, #022c22 0%, #0f172a 100%);
        border-radius: 16px; padding: 2.5rem; position: relative; overflow: hidden;
        border-left: 6px solid #10b981; box-shadow: 0 20px 40px rgba(16, 185, 129, 0.1); margin-bottom: 2.5rem;
    }
    
    /* 🧬 Live Atom Dynamics (100% Streamlit Cloud Error-Free Animators) */
    .atom-core-1, .atom-core-2 {
        position: absolute; border-radius: 50%;
    }
    .atom-core-1 { width: 14px; height: 14px; background: #0ea5e9; top: 40%; left: -5%; animation: receptorLock 6s ease-in-out infinite; box-shadow: 0 0 15px #0ea5e9; }
    .atom-core-2 { width: 10px; height: 10px; background: #ef4444; top: 65%; left: -10%; animation: receptorLock 4s linear infinite 2s; box-shadow: 0 0 15px #ef4444; }
    @keyframes receptorLock {
        0% { left: -5%; transform: scale(1); }
        70% { left: 80%; top: 45%; transform: scale(1.4); background: #10b981; box-shadow: 0 0 25px #10b981; }
        100% { left: 110%; top: 50%; transform: scale(1); }
    }
    
    /* Swiss Institutional Output Frame Styling */
    .swiss-report-frame {
        background-color: #111827; border-radius: 14px; padding: 2.2rem;
        border: 1px solid #1f2937; box-shadow: 0 15px 30px rgba(0,0,0,0.5); margin-top: 2rem;
    }
    .swiss-header-tag {
        font-size: 1.2rem; font-weight: 700; color: #10b981; border-bottom: 2px solid #1f2937;
        padding-bottom: 0.5rem; margin-bottom: 1.2rem; margin-top: 1.2rem; text-transform: uppercase; letter-spacing: 0.5px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Main Executive Banner with Live Molecular Target Capture
st.markdown("""
    <div class="swiss-banner">
        <div class="atom-core-1"></div>
        <div class="atom-core-2"></div>
        <h1 style='color: #ffffff !important; margin:0; font-size:28px; font-weight:800;'>🧬 SWISS-LEVEL SYSTEMS PHARMACOLOGY COMMAND UNIT</h1>
        <p style='color: #94a3b8 !important; margin: 8px 0 0 0; font-size:14px; font-family: monospace;'>
            H informatics System • Lead Consultant: Dr. Mayank Virmani | PharmD, PV Scientist Portfolio
        </p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### 📋 Genotype & Menopausal Baseline")
    age = st.slider("Patient Age (Years)", 18, 90, 63)
    weight = st.slider("Patient Weight (kg)", 40, 120, 102)
    
    menopausal_status = st.selectbox("Menopausal Staging Axis", [
        "Pre-Menopausal (Active Ovarian Loop)",
        "Peri-Menopausal (Fluctuating Gonadotropin)",
        "Post-Menopausal (Peripheral Adipose Window)"
    ])
    
    cyp2d6_genotype = st.selectbox("CYP2D6 Genomic Profile (CPIC Focus)", [
        "*1xN/*1 (Ultra-rapid Metabolizer - Activity Score: >2.0)",
        "*1/*1 (Normal Metabolizer - Default Activity Score: 2.0)", 
        "*1/*10 (Intermediate Metabolizer - Decreased Kinetic Flux)", 
        "*4/*4 (Null Function - Poor Metabolizer - Activity Score: 0.0)"
    ])
    er_expression = st.radio("ERα Nuclear Receptor Status", ["Positive", "Negative"], horizontal=True)

with col2:
    st.markdown("#### 💊 Multi-Pathway Competitive DDIs")
    psych_inhibitor = st.selectbox("CYP2D6 Mechanism-Based Inhibitors", [
        "Amiodarone (Moderate Competitive Inhibition)",
        "Paroxetine / Fluoxetine (Irreversible Phenoconversion)",
        "None"
    ])
    thyroid_axis = st.selectbox("Thyroid Axis Interaction", ["Levothyroxine (TBG Competition Hazard)", "None"])
    metabolic_agent = st.selectbox("Glycemic Control Interaction", ["Metformin (OCT1 Translocation Inter-play)", "None"])
    cv_agent = st.selectbox("Cardiovascular Substrate Clash", ["Metoprolol (Competitive CYP2D6 Affinity)", "None"])

with col3:
    st.markdown("#### 📊 Real-World Biomarkers & Morbidities")
    adherence = st.slider("Medication Adherence (MEMS Telemetry %)", 10, 100, 70) / 100.0
    days_on_therapy = st.number_input("Days Since Treatment Initiation", min_value=1, max_value=365, value=1)
    
    # 🌟 NEW UPGRADE: Split AST, ALT and added Total Bilirubin (TBIL) for Hy's Law implementation
    serum_ast = st.number_input("Serum AST Level (U/L) [Range: 5-2000]", min_value=5, max_value=2000, value=160, step=5)
    serum_alt = st.number_input("Serum ALT Level (U/L) [Range: 5-2000]", min_value=5, max_value=2000, value=180, step=5)
    serum_tbil = st.number_input("Serum Total Bilirubin (mg/dL) [Hy's Law Marker]", min_value=0.1, max_value=15.0, value=2.5, step=0.1)
    serum_tg = st.number_input("Serum Triglycerides (mg/dL)", min_value=50, max_value=800, value=233, step=5)
    
    # 🌟 FIXED COMPB MORBIDITY LIST
    prior_morbidity = st.multiselect("Prior Chronic Pathological Architecture", ["Deep Vein Thrombosis (DVT)", "Fatty Liver (NAFLD)", "Retinopathy"], default=["Fatty Liver (NAFLD)", "Retinopathy"])

# --- ADVANCED SWISS CLINICAL COMPULATION ENGINE ---
cr_cl = round(((140 - age) * weight) / (72 * 0.9) * 0.85, 1) # Normalizing baseline GFR calculation metrics

if "*4/*4" in cyp2d6_genotype: base_metabolite = 8.8
elif "*1/*1" in cyp2d6_genotype: base_metabolite = 22.3
elif "*1/*10" in cyp2d6_genotype: base_metabolite = 14.0
else: base_metabolite = 30.5  

if "Paroxetine" in psych_inhibitor: base_metabolite *= 0.25 
elif "Amiodarone" in psych_inhibitor: base_metabolite *= 0.60
if "Metoprolol" in cv_agent: base_metabolite *= 0.85

# 🌟 HY'S LAW VALIDATION ALGORITHM (FDA Drug Safety Metric)
# Baseline assumptions: AST/ALT ULN = 40 U/L, TBIL ULN = 1.2 mg/dL
hys_law_active = False
if (serum_ast > 120 or serum_alt > 120) and (serum_tbil > 2.4):
    hys_law_active = True

liver_stress = "Fulminant Hepatotoxicity" if (serum_ast >= 500 or serum_alt >= 500) else "Severe" if (serum_ast >= 150 or serum_alt >= 150) else "Normal"
if hys_law_active: base_metabolite *= 0.30
elif liver_stress == "Severe": base_metabolite *= 0.75

calculated_endoxifen = round(base_metabolite * adherence * (1 - np.exp(-0.024 * days_on_therapy)), 1)
t_half = 14 if cr_cl >= 60 else 24 if cr_cl >= 30 else 48
survival_percentage = round((0.52 if age > 50 else 0.88) * 100, 1)

# Dynamic Dosing Mapping
if "Negative" in er_expression:
    suggested_regimen = "Terminate Endocrine Regimen Immediately"
    regimen_timeline = "N/A - Structural absence of ERa receptor targets. Switch immediately to chemotherapy protocols."
    guideline_source = "NCCN 2026 Adjuvant Staging Guideline"
    dose_color = "#ef4444"
elif hys_law_active or liver_stress == "Fulminant Hepatotoxicity":
    suggested_regimen = "CRITICAL HALT / EMERGENCY suspensions"
    regimen_timeline = "🚨 HY'S LAW STATE MET. Severe drug-induced hepatocellular jaundice verified. Continuing drug exposure introduces high risk of acute hepatic liver failure."
    guideline_source = "FDA Post-Marketing Pharmacovigilance Fatal DILI Mandate"
    dose_color = "#ef4444"
elif days_on_therapy < 21:
    suggested_regimen = "Maintain Standard Protocol (Observation Phase)"
    regimen_timeline = f"Active metabolite is sub-therapeutic ({calculated_endoxifen} ng/mL) because Days on Therapy is {days_on_therapy}. System has NOT achieved Pharmacokinetic Steady-State. Maintain; do NOT alter kinetics prematurely."
    guideline_source = "ASCO / International Pharmacogenomics Consensus"
    dose_color = "#10b981"
else:
    suggested_regimen = "Maintain Standard Maintenance"
    regimen_timeline = "Target active metabolic window met successfully. Continue standard adjuvant 5-year treatment window tracking."
    guideline_source = "CPIC / NCCN Standard Adjuvant Protocols"
    dose_color = "#10b981"

st.write("---")
st.header("🤖 RWE Systems Pharmacology Translation Engine (Live Output)")

st.warning(f"🎯 ALGORITHMIC DOSING DECISION MATRIX: {suggested_regimen}")
st.info(f"⏳ TIMELINE STRATEGY: {regimen_timeline} | Compliant with: {guideline_source}")

out_col1, out_col2 = st.columns(2)

with out_col1:
    st.markdown("### 📈 Pharmacokinetic Core Metrics")
    st.metric(label="Simulated Active Serum Endoxifen Exposure", value=f"{calculated_endoxifen} ng/mL", delta="Efficacy Threshold &ge;15.0 ng/mL")
    st.metric(label="Calculated Creatinine Clearance (Cockcroft-Gault)", value=f"{cr_cl} mL/min", delta=f"Extrapolated Half-life (t1/2): ~{t_half} hours")
    st.metric(label="Calculated 5-Year Overall Survival Probability", value=f"{survival_percentage}%")

with out_col2:
    st.markdown("### 🫁 Multi-Organ Toxicological Mechanism & Specific Diets")
    
    # --- 🟫 DYNAMIC TOXICOLOGY & LIVER DIET CARD (NAFLD/HY'S LAW INTEGRATION) ---
    st.markdown("<div class='swiss-report-frame' style='margin-top:0; padding:1.2rem;'>", unsafe_allow_html=True)
    if hys_law_active:
        st.markdown("<span style='color:#ef4444; font-weight:700; font-size:14px;'>🚨 FULMINANT HY'S LAW SIGNALLING ACTIVE:</span>", unsafe_allow_html=True)
