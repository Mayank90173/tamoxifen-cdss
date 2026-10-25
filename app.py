import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ─── INTERFACE CONFIGURATION & SWISS DARK HUD SURGICAL THEME ──────────────────
st.set_page_config(
    page_title="OncoPGx Core Platform v5.0",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background-color: #02040a; color: #e2e8f0; }
    h1, h2, h3, h4, p, span, label, div { font-family: 'Inter', system-ui, sans-serif; }
    
    .innovation-banner {
        background: linear-gradient(135deg, #012022 0%, #030712 60%, #150c33 100%);
        border-radius: 16px; padding: 2rem; position: relative;
        border: 1px solid rgba(16, 185, 129, 0.4);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.8); margin-bottom: 2rem;
    }
    .hud-header {
        border-left: 4px solid #00f2fe; padding-left: 12px; margin-top: 1.8rem; margin-bottom: 1.2rem;
        font-weight: 700; color: #ffffff; font-size: 19px; letter-spacing: -0.5px;
    }
    .metric-panel {
        background: rgba(15, 23, 42, 0.95); border: 1px solid rgba(0, 242, 254, 0.25);
        border-radius: 12px; padding: 1.2rem; text-align: center;
        box-shadow: 0 4px 25px rgba(0,0,0,0.7);
    }
    .metric-val { font-size: 26px; font-weight: 900; color: #00f2fe; margin: 4px 0; font-family: monospace; }
    .metric-lbl { font-size: 11px; text-transform: uppercase; color: #94a3b8; letter-spacing: 1px; font-weight: 600; }
    
    .directive-card {
        background: rgba(15, 23, 42, 0.6); padding: 1.8rem; border-radius: 14px; 
        border: 1px solid rgba(255,255,255,0.08); margin-top: 1rem; line-height: 1.6;
    }
    .report-block {
        background: #ffffff; color: #1e293b; padding: 2.5rem; border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5); font-family: 'Courier New', Courier, monospace;
        border-top: 10px solid #0f172a; margin-top: 1.5rem;
    }
    .system-badge { font-size: 10px; font-family: monospace; text-transform: uppercase; letter-spacing: 2px; color: #00f2fe; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="innovation-banner">
        <span class="system-badge">✦ TRANSLATIONAL ECOSPEED // PHARMACOGENOMIC SIMULATOR v5.0</span>
        <h1 style='color: #ffffff !important; margin: 5px 0 0 0; font-size:32px; font-weight:800; letter-spacing:-0.5px;'>🧬 OncoPGx India v5.0: Full-Fledged Precision Oncology Architecture</h1>
        <p style='color: #94a3b8 !important; margin: 5px 0 0 0; font-size:13px; font-family: monospace;'>
            Integrated Real-Time PK Graph • Multi-Guideline Ingestion (CPIC/ASCO/ESMO) • Independent Investigator Framework: Mayank Virmani
        </p>
    </div>
""", unsafe_allow_html=True)

# ─── HIGH-DENSITY INPUT REGISTRATION GRID (TWO COLUMN WORKSPACE) ──────────────
col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown("<div class='hud-header'>📋 1. Patient Demographics & Organ Status</div>", unsafe_allow_html=True)
    pt_id = st.text_input("Patient Global System Identifier Hash", "IND-MOHALI-2026-X99")
    age = st.slider("Chronological Age Axis (Years)", 18, 95, 48)
    weight = st.slider("Total Body Mass Parameter (kg)", 40, 140, 65)
    gender = st.radio("Biological Configuration Core", ["Female", "Male"], horizontal=True)
    creatinine = st.number_input("Serum Creatinine Clear Baseline (mg/dL)", min_value=0.3, max_value=8.0, value=0.85, step=0.05)
    menopausal_status = st.selectbox("Menopausal Physiological Axis", ["Premenopausal Status", "Postmenopausal Status"])
    
    st.markdown("<div class='hud-header'>🧬 2. Multi-Omic & Tumor Pathology Parameters</div>", unsafe_allow_html=True)
    cyp2d6_pheno = st.selectbox("CYP2D6 Functional Phenotype (CPIC Core Mapping)", [
        "Normal Metabolizer (NM) [e.g., *1/*1, *1/*2 Baseline]",
        "Intermediate Metabolizer (IM) [High Prevalence South Asian *10 Axis]",
        "Poor Metabolizer (PM) [Null Alleles *4/*4, *5/*5 Total Loss]",
        "Ultra-rapid Metabolizer (UM) [Duplicated Functional Shunts]"
    ])
    er_status = st.radio("Nuclear Estrogen Receptor Expression (ERα)", ["Positive Expression Status", "Negative Expression Status"], horizontal=True)
    nodal_status = st.selectbox("Lymph Node Pathological Involvement", ["Node-Negative (Low Core Risk)", "Node-Positive (High Risk / Extended Recurrence Matrix)"])
    tumor_size = st.slider("Primary Tumor Diameter Dimensions (mm)", 1, 100, 25)

    st.markdown("<div class='hud-header'>💊 3. Integrated Xenobiotic Interferences (Concomitant DDIs)</div>", unsafe_allow_html=True)
    cyp2d6_inhib = st.selectbox("Co-administered Serotonergic Modulators (SSRI Core)", [
        "None / Sub-clinical Profile (e.g., Venlafaxine, Citalopram Verified Safe)",
        "Paroxetine / Fluoxetine [STRONG Competitive Irreversible Capture Matrix]",
        "Sertraline / Duloxetine [MODERATE High-Affinity Pathway Saturation]"
    ])
    cyp3a4_mod = st.selectbox("Parallel CYP3A4 Enzyme Interferences", [
        "None / Baseline Cellular Clearance",
        "Rifampicin [STRONG Trans-Activation Inducer - Accelerated Drug Loss]",
        "Ketoconazole [STRONG Metabolic Clearance Suppression Matrix]"
    ])
    
    compliance = st.slider("Patient Adherence Index Verification (MEMS %)", 10, 100, 100) / 100.0

# ─── REAL-TIME QUANTITATIVE SYSTEMS PHARMACOLOGY LOGIC ENGINE ─────────────────
# 1. Kidney Function Metrics (Cockcroft-Gault Equation)
g_mult = 0.85 if gender == "Female" else 1.0
computed_crcl = round(((140 - age) * weight) / (72 * creatinine) * g_mult, 1)

# Clearance rate constant calculation based on renal performance values
k_e_base = 0.022 if computed_crcl >= 60 else 0.040 if computed_crcl >= 30 else 0.065

# 2. Hepatic Metabolic Flux Processing (Aligned with Hwang et al. 13,001 Patient Cohort)
if "Poor" in cyp2d6_pheno:
    metabolic_velocity = 8.8
elif "Intermediate" in cyp2d6_pheno:
    metabolic_velocity = 14.2 # South Asian intermediate signature marker
elif "Ultra-rapid" in cyp2d6_pheno:
    metabolic_velocity = 31.8
else:
    metabolic_velocity = 22.3 

# 3. Phenoconversion & Secondary Drug Interactions Loop
is_phenoconverted = False
if "Paroxetine" in cyp2d6_inhib:
    metabolic_velocity = 8.8 
    is_phenoconverted = True
elif "Sertraline" in cyp2d6_inhib:
    metabolic_velocity *= 0.62

if "Rifampicin" in cyp3a4_mod:
    metabolic_velocity *= 0.48 
elif "Ketoconazole" in cyp3a4_mod:
    metabolic_velocity *= 1.20

final_predicted_steady_state = round(metabolic_velocity * compliance, 2)

# 4. Multi-Guideline Adaptive Clinical Decision Engine (CPIC v2.0 / ASCO / ESMO)
guideline_tags = []
primary_recommendation = ""
alternative_options = ""
duration_protocol = ""
dosage_regimen = ""

if "Negative" in er_status:
    primary_recommendation = "DISCONTINUE ENDOCRINE THERAPY TRAJECTORY"
    dosage_regimen = "0.0 mg Oral Daily"
    alternative_options = "Cytotoxic Chemotherapy (Anthracyclines/Taxanes) + Targeted Biologics based on HER2/PD-L1 Status."
    duration_protocol = "Immediate Termination of Endocrine Modeling"
    guideline_tags = ["ASCO 2024 Criteria", "ESMO Endocrine Guidelines Section 4.1"]
else:
    is_high_risk = "Node-Positive" in nodal_status or tumor_size > 50
    base_duration = "5 Years Standard Adjuvant Protocol" if not is_high_risk else "Extended 10 Years Protocol (ATLAS & aTTOM Clinical Trials Alignment)"
    
    if "Premenopausal" in menopausal_status:
        if "Poor" in cyp2d6_pheno or is_phenoconverted:
            primary_recommendation = "Ovarian Function Suppression (OFS) + Aromatase Inhibitor (AI) Class Rotation"
            dosage_regimen = "Letrozole 2.5 mg Oral QD + Goserelin (LHRH Agonist) 3.6 mg Subcutaneous Depot Every 28 Days"
            alternative_options = "Tamoxifen Dose Escalation to 40 mg QD (Split as 20mg BID) if AI is clinically contraindicated due to bone pathology."
            duration_protocol = f"{base_duration} (OFS duration strictly maintained for minimum 5 years)."
            guideline_tags = ["CPIC 2023 Tamoxifen Update", "ASCO/SOFT/TEXT Trial Clinical Guidelines"]
        elif "Intermediate" in cyp2d6_pheno:
            primary_recommendation = "Tamoxifen Standard Protocol with Preemptive Serum TDM Monitoring Matrix"
            dosage_regimen = "Tamoxifen Malate 20 mg Oral QD"
            alternative_options = "Dose-Escalation to 40 mg Oral QD (Split 20mg BID) if subsequent 90-day TDM tracking reflects values <5.97 ng/mL."
            duration_protocol = base_duration
            guideline_tags = ["CPIC 2023 Guideline Axis", "DPWG (Dutch Pharmacogenetics Working Group) Consensus"]
        else:
            primary_recommendation = "Standard Adjuvant Tamoxifen Monotherapy Corridor Approved"
            dosage_regimen = "Tamoxifen Malate 20 mg Oral QD"
            alternative_options = "Add OFS (Goserelin Depot) if dynamic staging drops or nodal recurrence markers scale up."
            duration_protocol = base_duration
            guideline_tags = ["ASCO Endocrine Mandate", "ESMO Core Biomarker Matrix"]
            
    else: # Postmenopausal Settings
        if "Poor" in cyp2d6_pheno or is_phenoconverted or is_high_risk:
            primary_recommendation = "Primary Aromatase Inhibitor (AI) Monotherapy Deployment"
            dosage_regimen = "Letrozole 2.5 mg Oral QD OR Anastrozole 1 mg Oral QD"
            alternative_options = "Exemestane (Steroidal AI) 25 mg Oral QD if arthralgia or muscular hypersensitivity profile triggers on letrozole."
            duration_protocol = "5 Years Standard AI. If Node-Positive, execute sequential switch: 5 Years AI followed by 5 Years Tamoxifen (Total 10 Years Profile)."
            guideline_tags = ["ASCO Postmenopausal Consensus", "ESMO Early Breast Cancer Guidelines"]
        else:
            primary_recommendation = "Aromatase Inhibitor Primary Corridor Approved"
            dosage_regimen = "Anastrozole 1 mg Oral QD"
