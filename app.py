import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date
import json

# Page Config
st.set_page_config(page_title="OncoPGx | Clinically-Grounded Decision Support", page_icon="🧬", layout="wide")

# Theme styling matching clinical dark-mode dashboard
st.markdown("""
<style>
.stApp{background:#07111f;color:#eef5ff}
[data-testid="stSidebar"]{background:#0b1b2c}
[data-testid="stMetric"]{background:#102238;border:1px solid #29435d;padding:12px;border-radius:12px}
.report-box{background-color:#112240; border-radius:8px; padding:20px; border:1px dashed #64ffda; margin-top:20px;}
</style>""", unsafe_allow_html=True)

st.title("🧬 OncoPGx: Advanced Breast Cancer Pharmacology & Pharmacogenomics Dashboard")
st.caption("Evidence-Based Decision Support System • Integrated PK/PD Model, Pharmacovigilance, and Renal Clearance Matrix")

# Core Clinical Warnings & Disclaimers
st.error("⚠️ **CLINICAL EVIDENCE DISCLAIMER:** This system is an educational and research prototype. It does not automatically prescribe medication or select a globally 'best' drug. Dosage adjustments and treatment decisions must always be guided by complete clinical evidence, official oncology guidelines (NCCN/ASCO/CPIC), and direct oversight of a qualified oncologist.")

# ----------------- SESSION STATE FOR PERSISTENT PHARMACOVIGILANCE -----------------
if 'pv_database' not in st.session_state:
    st.session_state.pv_database = pd.DataFrame(columns=[
        "Date", "Patient ID", "Cancer Type", "Stage", "Drug", "Dose (mg)", "Adverse Reaction", "Seriousness"
    ])

# ----------------- DATA DICTIONARIES & SCHEMAS -----------------
INTERACTIONS = {
    "None": ("No known interactions selected.", "Low risk", "NORMAL"),
    "Paroxetine": ("Strong CYP2D6 inhibitor. Can markedly reduce tamoxifen activation to active Endoxifen.", "High Priority Review", "CRITICAL"),
    "Fluoxetine": ("Strong CYP2D6 inhibitor. Long half-life interaction risks that can persist.", "High Priority Review", "CRITICAL"),
    "Bupropion": ("Strong CYP2D6 inhibitor. Decreases formation of active endoxifen.", "High Priority Review", "CRITICAL"),
    "Duloxetine": ("Moderate CYP2D6 inhibitor. May decrease active metabolite plasma concentrations.", "Review Context", "WARNING"),
    "Sertraline": ("Mild-to-moderate CYP2D6 inhibitor. Sub-type dependent interaction risk.", "Review Context", "WARNING"),
    "Rifampicin": ("Strong CYP3A4 inducer. Significantly decreases overall tamoxifen exposure.", "High Priority Review", "CRITICAL"),
}

PGX_SUBTYPES = {
    "Normal Metabolizer (NM)": {"score": 2.0, "guideline": "Standard clinical dosage recommended (e.g., Tamoxifen 20mg/day). Avoid potent CYP2D6 inhibitors."},
    "Intermediate Metabolizer (IM)": {"score": 1.0, "guideline": "Consider alternative endocrine therapy or monitor endoxifen concentrations. Strictly avoid CYP2D6 inhibitors."},
    "Poor Metabolizer (PM)": {"score": 0.0, "guideline": "High risk of therapeutic failure with standard Tamoxifen. Strong recommendation to consider Aromatase Inhibitors if postmenopausal, or alternative management."},
    "Ultrarapid Metabolizer (UM)": {"score": 3.0, "guideline": "Standard Tamoxifen usage can cause rapid metabolite formation. Monitor closely for toxicities."}
}

# ----------------- SIDEBAR: PATIENT DEMOGRAPHICS & CLINICAL ENTRY -----------------
st.sidebar.header("📋 Patient Demographics & Profile")
patient_id = st.sidebar.text_input("Patient Reference/ID", "PT-2026-89B")
age = st.sidebar.number_input("Age (Years)", min_value=18, max_value=100, value=54)
weight = st.sidebar.number_input("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0)
serum_creatinine = st.sidebar.number_input("Serum Creatinine (mg/dL)", min_value=0.3, max_value=10.0, value=0.9, step=0.1)
gender = st.sidebar.selectbox("Biological Sex", ["Female", "Male"])
menopause_status = st.sidebar.selectbox("Menopausal Status", ["Pre-menopausal", "Post-menopausal", "Perimenopausal"])

st.sidebar.header("🧬 Tumor Characteristics & Pathology")
cancer_type = st.sidebar.selectbox("Cancer Classification", ["Invasive Ductal Carcinoma (IDC)", "Invasive Lobular Carcinoma (ILC)", "Ductal Carcinoma In Situ (DCIS)"])
cancer_stage = st.sidebar.selectbox("Clinical Stage", ["Stage I", "Stage II", "Stage III", "Stage IV"])
er_status = st.sidebar.selectbox("Estrogen Receptor (ER)", ["Positive", "Negative"])
pr_status = st.sidebar.selectbox("Progesterone Receptor (PR)", ["Positive", "Negative"])
her2_status = st.sidebar.selectbox("HER2 Status", ["Negative", "Positive (Overexpressed)"])

st.sidebar.header("💊 Pharmacogenomics & Meds")
pgx_phenotype = st.sidebar.selectbox("CYP2D6 Genotype Phenotype", list(PGX_SUBTYPES.keys()))
co_medications = st.sidebar.multiselect("Current Co-medications Screen", list(INTERACTIONS.keys()), default=["None"])

# ----------------- CLINICAL CORE CALCULATIONS -----------------

# 1. Kidney Metrics: Cockcroft-Gault CrCl
def calculate_cockcroft_gault(age, weight, scr, sex):
    # Assumption: Actual Body Weight utilized. Direct calculation unadjusted for ideal weight unless specified.
    constant = 85 if sex == "Female" else 72
    crcl = ((140 - age) * weight) / (constant * scr)
    return round(crcl, 2)

# 2. Kidney Metrics: CKD-EPI eGFR (2021 Refined Equation without race parameter)
def calculate_ckd_epi(age, scr, sex):
    # Standard 2021 CKD-EPI equations mapping
    if sex == "Female":
        kappa = 0.7
        alpha = -0.241
        gender_mod = 1.012
    else:
        kappa = 0.9
        alpha = -0.302
        gender_mod = 1.0

    min_term = min(scr / kappa, 1) ** alpha
    max_term = max(scr / kappa, 1) ** -1.200
    age_term = 0.9938 ** age
    egfr = 142 * min_term * max_term * age_term * gender_mod
    return round(egfr, 2)

crcl_val = calculate_cockcroft_gault(age, weight, serum_creatinine, gender)
egfr_val = calculate_ckd_epi(age, serum_creatinine, gender)

# 3. Liver Function Test Mock Profile for baseline checking
st.sidebar.header("🧪 Liver Function Panel")
ast_val = st.sidebar.number_input("AST (U/L)", value=25)
alt_val = st.sidebar.number_input("ALT (U/L)", value=30)
bilirubin_val = st.sidebar.number_input("Total Bilirubin (mg/dL)", value=0.8)

# ----------------- MAIN DASHBOARD TABS -----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Core Diagnostics & Renal Matrix",
    "💊 Guideline Engine & Treatment Matrix",
    "📈 PK Core & Endoxifen Simulation",
    "🛡️ Live Pharmacovigilance Hub",
    "📋 Case Report Generator"
])

# ----- TAB 1: CORE DIAGNOSTICS & RENAL MATRIX -----
with tab1:
    st.subheader("📋 Unified Patient Status Panel & Renal Clearance Contrast Matrix")
    
    # Summary Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Patient ID & Gender", f"{patient_id} ({gender})")
    m2.metric("Tumor Subtype Matrix", f"ER+/PR+/HER2-" if er_status=="Positive" and her2_status=="Negative" else f"ER:{er_status}/HER2:{her2_status}")
    m3.metric("Cockcroft-Gault CrCl", f"{crcl_val} mL/min")
    m4.metric("CKD-EPI eGFR", f"{egfr_val} mL/min/1.73m²")

    st.markdown("### 🧪 Renal Function Comparison Matrix")
    # Explanatory data presentation for safety compliance
    renal_data = {
        "Metric & Methodology": ["Cockcroft-Gault CrCl", "CKD-EPI eGFR (2021)"],
        "Calculated Value": [f"{crcl_val} mL/min", f"{egfr_val} mL/min/1.73m²"],
        "Primary Clinical Application": ["Used primarily for baseline renal drug dosage adjustments (FDA Labeling).", "Used for chronic kidney disease staging and overall classification."],
        "Key Biological Assumptions": ["Highly dependent on actual total body weight; can overestimate clearance in obese profiles.", "Normalized to standardized body surface area (1.73m²); independent of patient weight tracking."]
    }
    st.table(pd.DataFrame(renal_data))

    st.markdown("### 💾 Liver Function Baseline Verification")
    l1, l2, l3 = st.columns(3)
    l1.metric("AST Status", f"{ast_val} U/L", delta="Normal" if ast_val < 40 else "Elevated Check Pathology")
    l2.metric("ALT Status", f"{alt_val} U/L", delta="Normal" if alt_val < 45 else "Elevated Check Pathology")
    l3.metric("Total Bilirubin", f"{bilirubin_val} mg/dL", delta="Normal" if bilirubin_val <= 1.2 else "Hyperbilirubinemia Warning")

# ----- TAB 2: GUIDELINE ENGINE & TREATMENT MATRIX -----
with tab2:
    st.subheader("🛠️ Evidence-Based Treatment Option Matrix (Ranked by Guideline Alignment)")
    
    # Drug Interaction Screening
    st.markdown("### ⚡ Real-Time Drug Interaction Screening Ledger")
    highest_severity = "NORMAL"
    for med in co_medications:
        if med != "None":
            details = INTERACTIONS[med]
            if details[2] == "CRITICAL":
                st.error(f"🔴 **Critical Action Prompt [{med}]:** {details[0]} | *Risk Status:* {details[1]}")
                highest_severity = "CRITICAL"
            elif details[2] == "WARNING":
                st.warning(f"🟡 **Review Advisory [{med}]:** {details[0]} | *Risk Status:* {details[1]}")
                if highest_severity != "CRITICAL": highest_severity = "WARNING"
    if "None" in co_medications or len(co_medications) == 0:
        st.success("🟢 No heavy CYP2D6 processing inhibitors or interaction flags selected in baseline profile setup.")

    # Treatment Matrix Engine Logic
    st.markdown("### 📋 Multi-Factor Treatment Options Suitability Matrix")
    st.info("The ranking below represents structural mapping to NCCN/CPIC options framework based on your profile selection. Final strategy requires comprehensive bedside verification.")

    options = []
    # Logic matrix dependent on staging, hormone, and menopausal profiles
    if er_status == "Positive":
        if menopause_status == "Post-menopausal":
