import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ─── INTERFACE CONFIGURATION & HIGH-FIDELITY Presentation Theme ──────────────
st.set_page_config(
    page_title="OncoPGx Core Platform v5.6",
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
    .sop-ledger-block {
        background: rgba(30, 41, 59, 0.5); border-left: 4px solid #fbbf24;
        padding: 1rem; border-radius: 0 12px 12px 0; margin-top: 0.8rem;
    }
    .system-badge { font-size: 10px; font-family: monospace; text-transform: uppercase; letter-spacing: 2px; color: #00f2fe; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="innovation-banner">
        <span class="system-badge">✦ TRANSLATIONAL ECOSPEED // ESTIC 2026 PLATFORM PROTOTYPE</span>
        <h1 style='color: #ffffff !important; margin: 5px 0 0 0; font-size:32px; font-weight:800; letter-spacing:-0.5px;'>🧬 OncoPGx India v5.6: Full-Fledged Precision Oncology Architecture</h1>
        <p style='color: #94a3b8 !important; margin: 5px 0 0 0; font-size:13px; font-family: monospace;'>
            Integrated Real-Time PK Graph • Multi-Guideline Ingestion (CPIC/ASCO/ESMO) • Independent Investigator Framework: Mayank Virmani
        </p>
    </div>
""", unsafe_allow_html=True)

# ─── HIGH-DENSITY INPUT REGISTRATION GRID (TWO COLUMN WORKSPACE) ──────────────
col1, col2 = st.columns([1, 1.2])

with col1:
    st.markdown("<div class='hud-header'>📋 1. Patient Biometrics & Organ Status</div>", unsafe_allow_html=True)
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
g_mult = 0.85 if gender == "Female" else 1.0
computed_crcl = round(((140 - age) * weight) / (72 * creatinine) * g_mult, 1)
k_e_base = 0.022 if computed_crcl >= 60 else 0.040 if computed_crcl >= 30 else 0.065

if "Poor" in cyp2d6_pheno:
    metabolic_velocity = 8.8
elif "Intermediate" in cyp2d6_pheno:
    metabolic_velocity = 14.2 
elif "Ultra-rapid" in cyp2d6_pheno:
    metabolic_velocity = 31.8
else:
    metabolic_velocity = 22.3 

is_phenoconverted = False
if "Paroxetine" in cyp2d6_inhib:
    metabolic_velocity = 6.2  
    is_phenoconverted = True
elif "Sertraline" in cyp2d6_inhib:
    metabolic_velocity *= 0.55

if "Rifampicin" in cyp3a4_mod:
    metabolic_velocity *= 0.45 
elif "Ketoconazole" in cyp3a4_mod:
    metabolic_velocity *= 1.25

final_predicted_steady_state = round(metabolic_velocity * compliance, 2)

# ─── REAL-TIME CLINICAL MATRIX RESOLUTION ENGINE ─────────────────────────────
guideline_text = "ASCO Endocrine Mandate, ESMO Core Biomarker Matrix"
primary_recommendation = ""
alternative_options = ""
duration_protocol = ""
regimen_specification = ""

sop_status = "NOMINAL PIPELINE"
sop_rationale = "Patient exhibits balanced genomic clearance parameters. Standard clinical track approved."

if "Negative" in er_status:
    primary_recommendation = "❌ DISCONTINUE ENDOCRINE THERAPY TRAJECTORY"
    regimen_specification = "Discontinue Endocrine Intervention Protocol"
    alternative_options = "Cytotoxic Chemotherapy (Anthracyclines/Taxanes) + Targeted Biologics based on HER2/PD-L1 Status."
    duration_protocol = "Immediate Termination of Endocrine Modeling"
    guideline_text = "ASCO 2024 Criteria, ESMO Endocrine Guidelines Section 4.1"
    sop_status = "CRITICAL PATH OVERRIDE"
    sop_rationale = "ER-negative expression voids biomarker targets; standard endocrine pathways are cancelled."
else:
    is_high_risk = "Node-Positive" in nodal_status or tumor_size > 50
    base_duration = "5 Years Adjuvant Protocol" if not is_high_risk else "Extended 10 Years Protocol (ATLAS & aTTOM Trials)"
    
    if is_high_risk:
        sop_status = "TIMELINE EXTENSION INTERVENTION"
        sop_rationale = "High tumor load or nodal matrix involvement requires transition to 10 years framework based on ATLAS trial guidelines."

    if "Premenopausal Status" in menopausal_status:
        if "Poor" in cyp2d6_pheno or is_phenoconverted:
            primary_recommendation = "🔄 Ovarian Function Suppression (OFS) + Aromatase Inhibitor (AI) Class Rotation"
            regimen_specification = "Letrozole 2.5 mg Oral QD + Goserelin (LHRH Agonist) 3.6 mg SC Depot Every 28 Days"
            alternative_options = "Tamoxifen Protocol Adjustment to 40mg Daily if AI is contraindicated due to osteoporosis."
            duration_protocol = f"{base_duration} (OFS strictly maintained for minimum 5 years)."
            guideline_text = "CPIC 2023 Tamoxifen Update, ASCO/SOFT/TEXT Trial Clinical Guidelines"
            sop_status = "DRUG CLASS VARIATION ROUTING"
            sop_rationale = "Active Endoxifen concentration falls below the 16 nM floor due to poor metabolizer profile or drug interaction. Overriding standard Tamoxifen."
        elif "Intermediate" in cyp2d6_pheno:
            primary_recommendation = "⚠️ Tamoxifen Standard Protocol + Accelerated Serum TDM Monitoring Matrix"
            regimen_specification = "Tamoxifen Malate 20 mg Oral QD"
            alternative_options = "Dose-Escalation to 40 mg Oral QD (Split 20mg BID) if subsequent 90-day TDM reflects values < 16 nM."
            duration_protocol = base_duration
            guideline_text = "CPIC 2023 Guideline Axis, DPWG Consensus Guidelines"
            sop_status = "CONTINGENT TDM MODIFICATION"
            sop_rationale = "Borderline clearance via South Asian *10 Intermediate Metabolizer trait. Action triggers for dynamic titration based on TDM."
        else:
            primary_recommendation = "Standard Adjuvant Tamoxifen Monotherapy Corridor Approved"
            regimen_specification = "Tamoxifen Malate 20 mg Oral QD"
            alternative_options = "Add OFS (Goserelin Depot) if dynamic staging drops or nodal recurrence markers scale up."
            duration_protocol = base_duration
            guideline_text = "ASCO Endocrine Mandate, ESMO Core Biomarker Matrix"
            
    else: # Postmenopausal Settings
        if "Poor" in cyp2d6_pheno or is_phenoconverted:
            primary_recommendation = "🎯 Primary Aromatase Inhibitor (AI) Monotherapy Deployment"
            regimen_specification = "Letrozole 2.5 mg Oral QD OR Anastrozole 1 mg Oral QD"
