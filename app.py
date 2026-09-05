import streamlit as st
import numpy as np
import pandas as pd
import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Premium Institutional Page & Swiss UI Setup
st.set_page_config(
    page_title="Zurich Translational Systems Pharmacology Command Center", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# High-Tech Cybernetic Medical Aesthetic & Morphing Organ Canvas Elements
st.markdown("""
    <style>
    .stApp { background-color: #060913; color: #f8fafc; }
    h1, h2, h3, h4, p, span, label, div { font-family: 'Inter', system-ui, sans-serif; }
    
    .swiss-premium-banner {
        background: linear-gradient(135deg, #022c22 0%, #0b1329 50%, #1e1b4b 100%);
        border-radius: 20px; padding: 3rem 2.5rem; position: relative; overflow: hidden;
        border: 1px solid rgba(16, 185, 129, 0.2);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); margin-bottom: 2.5rem;
    }
    
    .biomatrix-dna {
        position: absolute; width: 4px; height: 120px; background: linear-gradient(to bottom, #10b981, transparent);
        right: 8%; top: 10%; opacity: 0.4; animation: dnaPulse 3s ease-in-out infinite alternate;
    }
    .biomatrix-kidney {
        position: absolute; width: 30px; height: 45px; border: 2px dashed #0ea5e9; border-radius: 40% 60% 60% 40% / 40% 40% 60% 60%;
        right: 15%; top: 35%; opacity: 0.25; animation: organFilter 5s linear infinite;
    }
    .biomatrix-liver {
        position: absolute; width: 55px; height: 35px; border: 2px dashed #f43f5e; border-radius: 70% 30% 50% 50% / 60% 40% 60% 40%;
        right: 4%; top: 50%; opacity: 0.25; animation: liverMetabolize 4s ease-in-out infinite alternate;
    }
    
    @keyframes dnaPulse { 0% { transform: scaleY(0.8) translateY(0px); opacity: 0.2; } 100% { transform: scaleY(1.2) translateY(10px); opacity: 0.6; } }
    @keyframes organFilter { 0% { transform: rotate(0deg) scale(1); border-color: #0ea5e9; } 50% { transform: rotate(5deg) scale(1.08); border-color: #38bdf8; } 100% { transform: rotate(0deg) scale(1); border-color: #0ea5e9; } }
    @keyframes liverMetabolize { 0% { transform: skewX(-5deg) scale(0.95); filter: drop-shadow(0 0 2px #f43f5e); } 100% { transform: skewX(5deg) scale(1.05); filter: drop-shadow(0 0 12px #f43f5e); } }
    
    .swiss-card {
        background: rgba(17, 24, 39, 0.7); border-radius: 16px; padding: 2rem;
        border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 2rem;
    }
    .system-status { font-size: 11px; font-family: monospace; text-transform: uppercase; letter-spacing: 1px; color: #64748b; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="swiss-premium-banner">
        <div class="biomatrix-dna"></div>
        <div class="biomatrix-kidney"></div>
        <div class="biomatrix-liver"></div>
        <span class="system-status">✦ SWISS CLINICAL PHARMACOGENOMICS MATRIX // LEVEL 4 AUDIT</span>
        <h1 style='color: #ffffff !important; margin: 5px 0 0 0; font-size:32px; font-weight:800; letter-spacing:-0.5px;'>🧬 TRANSLATIONAL SYSTEMS PHARMACOLOGY PLATFORM</h1>
        <p style='color: #94a3b8 !important; margin: 8px 0 0 0; font-size:14px; font-family: monospace;'>
            H-Informatics Engine • Portfolio: Dr. Mayank Virmani | Lead Consultant PharmD & PV Scientist
        </p>
    </div>
""", unsafe_allow_html=True)

if 'patient_ledger' not in st.session_state:
    st.session_state.patient_ledger = []

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📋 1. Patient Demographics & Genotype")
    pt_id = st.text_input("Unique Patient System Hash ID", "ZRH-2026-9843X")
    age = st.slider("Patient Chronological Age", 18, 100, 64)
    weight = st.slider("Total Mass Target (kg)", 35, 150, 82)
    gender = st.radio("Biological Configuration", ["Female (0.85 CrCl Skew)", "Male"], horizontal=True)
    
    cyp2d6_profile = st.selectbox("CYP2D6 Genomic Architecture (CPIC Tier-1)", [
        "*1xN/*1 (Ultra-rapid Metabolizer - Functional Activity Score: >2.0)",
        "*1/*1 (Normal Metabolizer - Baseline Metabolic Velocity)", 
        "*1/*10 (Intermediate Metabolizer - Impaired Flux Spectrum)", 
        "*4/*4 (Null Allele - Poor Metabolizer - Total Phenoconversion)"
    ])
    er_status = st.radio("Estrogen Receptor Nuclear Expression (ERα)", ["Positive Status", "Negative Status"], horizontal=True)

with col2:
    st.markdown("### 💊 2. Multi-Pathway Xenobiotic DDI Grid")
    cyp2d6_inhibitor = st.selectbox("CYP2D6 Potent Core Inhibitors", [
        "None / Sub-clinical",
        "Paroxetine / Fluoxetine (Irreversible Structural Invalidation)",
        "Bupropion / Quinidine (High Affinity Competitive Capture)",
        "Sertraline / Duloxetine (Moderate Pathway Saturation)"
    ])
    cyp3a4_modulator = st.selectbox("Secondary CYP3A4 Pathway Competitors", [
        "None / Normal Turnover",
        "Rifampicin (Extreme CYP3A4 Enzyme Induction Hazard)",
        "Ketoconazole / Clarithromycin (Severe Clearance Suppression Matrix)",
        "St. John's Wort (Unregulated Botanical Induction)"
    ])
    pgp_pump = st.selectbox("P-Glycoprotein (P-gp / ABCB1) Efflux Status", [
        "Standard Efflux",
        "Verapamil / Amiodarone (P-gp Efflux Blockade)"
    ])

with col3:
    st.markdown("### 📊 3. End-Organ Pathological Load")
    creatinine = st.number_input("Serum Creatinine Clear Marker (mg/dL)", min_value=0.2, max_value=12.0, value=1.40, step=0.05)
    serum_ast = st.number_input("Hepatic Transaminase AST (U/L)", min_value=5, max_value=3000, value=145, step=5)
    serum_alt = st.number_input("Hepatic Transaminase ALT (U/L)", min_value=5, max_value=3000, value=165, step=5)
    total_bilirubin = st.number_input("Total Bilirubin Mass Fraction (mg/dL)", min_value=0.1, max_value=20.0, value=2.6, step=0.1)
    
    comorbidities = st.multiselect("Active Pathological Architectural Overlays", [
        "Deep Vein Thrombosis (DVT Cluster Risk)",
        "Endometrial Hyperplasia Hyper-proliferation",
        "Non-Alcoholic Fatty Liver Disease (NAFLD - Severe Met-Impairment)",
        "Severe Retinopathy & Macular Degradation"
    ], default=["Non-Alcoholic Fatty Liver Disease (NAFLD - Severe Met-Impairment)"])
    
    compliance = st.slider("Adherence Control (MEMS Smart-Cap %)", 10, 100, 85) / 100.0
    days_on_therapy = st.number_input("Duration Cycle Status (Days Active)", min_value=1, max_value=730, value=24)

# --- PHARMACOLOGY KINETIC ENGINE ---
gender_multiplier = 0.85 if "Female" in gender else 1.0
calculated_crcl = round(((140 - age) * weight) / (72 * creatinine) * gender_multiplier, 1)

if "*4/*4" in cyp2d6_profile: base_flux = 7.2
elif "*1/*10" in cyp2d6_profile: base_flux = 13.8
elif "*1/*1" in cyp2d6_profile: base_flux = 24.5
else: base_flux = 34.0  

if "Paroxetine" in cyp2d6_inhibitor: base_flux *= 0.15 
elif "Bupropion" in cyp2d6_inhibitor: base_flux *= 0.30
elif "Sertraline" in cyp2d6_inhibitor: base_flux *= 0.65

if "Rifampicin" in cyp3a4_modulator: base_flux *= 0.45 
elif "Ketoconazole" in cyp3a4_modulator: base_flux *= 1.25 

if "Non-Alcoholic Fatty Liver Disease" in comorbidities: base_flux *= 0.80

hys_law_triggered = (serum_ast > 120 or serum_alt > 120) and (total_bilirubin > 2.0)
if hys_law_triggered: base_flux *= 0.35

calculated_endoxifen = round(base_flux * compliance * (1 - np.exp(-0.028 * days_on_therapy)), 2)

# --- DYNAMIC DIETARY ENGINE ---
dietary_matrix = []
fluid_target = max(1.5, round((weight * 30) / 1000, 1))

if "Deep Vein Thrombosis" in comorbidities:
    dietary_matrix.append("• **Vascular Integrity Focus**: Absolute exclusion of high-dose isolated Vitamin K supplements; strictly regulate uniform intake of leafy greens.")
if "Non-Alcoholic Fatty Liver Disease" in comorbidities:
    dietary_matrix.append("• **Hepatocyte Repair Diet Plan**: Restrict high-fructose corn syrups and processed simple sugars entirely to prevent worsening hepatic steatosis.")
if calculated_crcl < 45:
    dietary_matrix.append(f"• **Renal Protection Protocol**: Limit protein volume to 0.8g/kg. Ensure precise calculated daily fluid limit of **{fluid_target} Litres**.")
else:
    dietary_matrix.append(f"• **Standard Clearance Hydration Plan**: Maintain a systemic fluid loading target of **{fluid_target} Litres** daily.")

if not dietary_matrix:
    dietary_matrix.append("• **Metabolic Maintenance Optimization**: Balanced Mediterranean profile containing cold-pressed olive oils.")

final_diet_compiled = "\n\n".join(dietary_matrix)

# --- DIRECTIVE MATRIX ---
if "Negative Status" in er_status:
    clinical_directive = "TERMINATE ENDOCRINE SYSTEM PROTOCOL IMMEDIATELY"
    directive_notes = "Target ERα receptor architecture is entirely absent. Tamoxifen lacks biological binding efficacy."
    ui_status_color = "#ef4444"
elif hys_law_triggered or "Deep Vein Thrombosis (DVT Cluster Risk)" in comorbidities:
    clinical_directive = "CRITICAL MEDICAL SUSPENSION ORDERED"
    directive_notes = "🚨 IMMEDIATE SUSPENSION WARRANTED. Either active Hy's Law drug-induced liver injury has been identified or a critical DVT threat profile exists."
    ui_status_color = "#ef4444"
elif calculated_endoxifen < 5.97:
    clinical_directive = "SUB-THERAPEUTIC PHARMACOKINETIC SPECTRUM DETECTED"
    directive_notes = f"Current concentration profile ({calculated_endoxifen} ng/mL) falls below the critical therapeutic benchmark of 5.97 ng/mL."
    ui_status_color = "#f59e0b"
else:
    clinical_directive = "OPTIMAL STABLE MAINTAINED MAINTENANCE"
    directive_notes = f"Steady-state active concentration target successfully stabilized ({calculated_endoxifen} ng/mL)."
    ui_status_color = "#10b981"

# --- FIXED REPORTLAB PDF GENERATION ENGINE ---
def generate_pdf_payload():
    import io
    pdf_buffer = io.BytesIO()
