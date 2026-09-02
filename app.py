import streamlit as st
import numpy as np

# 1. Page Configuration for Ultra-Premium Medical Workspace
st.set_page_config(page_title="RWD-PGx Advanced Systems Oncology Core", layout="wide", initial_sidebar_state="collapsed")

# Advanced Styling with Soft Clinical Slate Theme & Live Molecular Fragment Streams
st.markdown("""
    <style>
    .stApp { background-color: #f1f5f9; color: #0f172a; }
    h1, h2, h3, h4, p, span, label { color: #1e293b !important; }
    div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #0f172a !important; border: 1px solid #cbd5e1 !important; }
    div[role="radiogroup"] label { color: #0f172a !important; }
    
    .clinical-banner {
        background: linear-gradient(135deg, #0f172a 0%, #115e59 100%);
        border-radius: 14px; padding: 2.5rem; color: #f8fafc; margin-bottom: 2rem;
        box-shadow: 0 10px 25px rgba(17, 94, 89, 0.15);
        position: relative; overflow: hidden;
    }
    .clinical-banner h2 { color: #ffffff !important; font-weight: 700 !important; margin: 0; }
    
    .molecule-stream-1, .dna-fragment-2 {
        position: absolute; background: rgba(56, 189, 248, 0.4); border-radius: 50%;
    }
    .molecule-stream-1 {
        width: 16px; height: 14px; top: 30%; left: -5%;
        animation: streamWave 8s ease-in-out infinite; box-shadow: 0 0 12px #38bdf8;
    }
    .dna-fragment-2 {
        width: 10px; height: 10px; top: 65%; left: -8%;
        animation: streamWave 5s ease-in-out infinite 2.5s; box-shadow: 0 0 12px #22c55e;
    }
    @keyframes streamWave {
        0% { left: -5%; transform: translateY(0px) scale(1); }
        50% { transform: translateY(-25px) scale(1.3); background: #22c55e; }
        100% { left: 105%; transform: translateY(10px) scale(1); }
    }
    
    .med-card {
        background-color: white; border-radius: 12px; padding: 1.5rem; border: 1px solid #cbd5e1;
        margin-bottom: 1.5rem; box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .med-card-header {
        font-size: 1.1rem; font-weight: 700; padding: 0.5rem 1rem; border-radius: 6px; color: white !important; margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="clinical-banner">
        <div class="molecule-stream-1"></div>
        <div class="dna-fragment-2"></div>
        <h2>🧬 Next-Gen RWE Systems Pharmacology & Intelligence Architecture</h2>
        <p style='color: #94a3b8; margin: 6px 0 0 0; font-size:14px;'>Active Stream Simulation: [E-Endoxifen C26H29NO Diffusion Steady-State Equilibrium Vector Loaded]</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📋 PGx & Transmembrane ADME")
    age = st.slider("Patient Age (Years)", 18, 90, 52)
    weight = st.slider("Patient Weight (kg)", 40, 120, 70)
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
    metabolic_agent = st.selectbox("Metabolic / Glycemic Co-medication", ["None", "Metformin (OCT1 Translocation Inter-play)"])
    cv_agent = st.selectbox("Antihypertensive Regimen", ["None", "Metoprolol (Competitive CYP2D6 Affinity)"])

with col3:
    st.markdown("### 📊 Real-World Data & Lab Biomarkers")
    adherence = st.slider("Medication Adherence (MEMS Smart-Cap Telemetry %)", 10, 100, 95) / 100.0
    days_on_therapy = st.number_input("Days Since Treatment Initiation (Steady-State Windows)", min_value=1, max_value=365, value=45)
    ast_alt = st.number_input("Serum AST / ALT Levels (U/L) [Hepatocyte Stress]", min_value=10, max_value=500, value=35)
    prior_morbidity = st.multiselect("Prior Chronic Pathological Architecture", ["Deep Vein Thrombosis (DVT)", "Fatty Liver (NAFLD)", "Retinopathy"])

# --- CORE CLINICAL PHARMACOLOGY COMPUTATION ENGINE ---
cr_cl = round(((140 - age) * weight) / (72 * serum_creatinine) * 0.85, 1)

if "*4/*4" in cyp2d6_genotype: base_metabolite = 8.8
elif "*1/*1" in cyp2d6_genotype: base_metabolite = 22.3
elif "*1/*10" in cyp2d6_genotype: base_metabolite = 14.0
else: base_metabolite = 30.5

if "Paroxetine" in psych_inhibitor: base_metabolite *= 0.25 
elif "Amiodarone" in psych_inhibitor: base_metabolite *= 0.60
if "Metoprolol" in cv_agent: base_metabolite *= 0.85

liver_stress = "Severe" if ast_alt >= 150 else "Moderate" if ast_alt >= 50 else "Normal"
if liver_stress == "Severe": base_metabolite *= 0.75

calculated_endoxifen = round(base_metabolite * adherence * (1 - np.exp(-0.024 * days_on_therapy)), 1)
t_half = 14 if cr_cl >= 60 else 24 if cr_cl >= 30 else 48
base_survival = 0.52 if age > 50 else 0.88
survival_percentage = round(base_survival * 100, 1)

# Dynamic Dosing Logic
if "Negative" in er_expression:
    suggested_regimen = "Terminate Endocrine Regimen Immediately"
    regimen_timeline = "N/A - Structural absence of hormone targets. Route to cytotoxic systemic chemotherapy."
    dose_color = "red"
elif "*4/*4" in cyp2d6_genotype or "Paroxetine" in psych_inhibitor:
    suggested_regimen = "Switch to Aromatase Inhibitors (Anastrozole 1mg/day)"
    regimen_timeline = "Permanent switch. Active biotransformation blocked via null alleles or irreversible phenoconversion."
    dose_color = "red"
elif calculated_endoxifen < 15.0 and adherence >= 0.80:
    suggested_dose_mg = 40 if ast_alt < 150 else 20
    suggested_regimen = f"Escalate Tamoxifen Regimen to {suggested_dose_mg} mg/day"
    regimen_timeline = "Maintain 40mg/day for exactly 4 to 6 weeks (28-42 days) to hit Steady-State PK, followed by repeat TDM assay."
    dose_color = "orange"
elif liver_stress == "Severe":
    suggested_regimen = "De-escalate Tamoxifen to 10 mg/day"
    regimen_timeline = "Maintain restricted sub-dose to minimize hepatocyte damage until AST/ALT settles below 1.5x ULN."
    dose_color = "orange"
else:
    suggested_regimen = "Maintain Standard 20 mg/day Regimen"
    regimen_timeline = "Continue standard maintenance for the remaining adjuvant oncology 5-year treatment window."
    dose_color = "green"

st.write("---")
st.markdown("## 🤖 RWE Systems Pharmacology Translation Engine")

out_col1, out_col2 = st.columns(2)

with out_col1:
    st.markdown("### 📈 Pharmacokinetic & Dosing Analytics Core")
    st.error(f"🎯 ALGORITHMIC DOSING DECISION MATRIX: {suggested_regimen}")
    st.warning(f"⏳ TIMELINE STRATEGY: {regimen_timeline}")
    st.metric(label="Simulated Active Serum Endoxifen Exposure", value=f"{calculated_endoxifen} ng/mL", delta="Efficacy Threshold ≥15.0 ng/mL")
    st.metric(label="Calculated Creatinine Clearance (Cockcroft-Gault)", value=f"{cr_cl} mL/min", delta=f"Extrapolated Half-life (t1/2): ~{t_half} hours")
    st.metric(label="Calculated 5-Year Overall Survival Probability (Proxy Matrix)", value=f"{survival_percentage}%")

with out_col2:
    st.markdown("### 🫁 Multi-Organ Toxicological Mechanism & Condition-Specific Diets")
    
    st.markdown("<div class='med-card'>", unsafe_allow_html=True)
    st.markdown("<div class='med-card-header' style='background-color: #0f172a;'>🥦 CONDITION-SPECIFIC DIETARY EXCLUSIONS & CONTRAINDICATIONS</div>", unsafe_allow_html=True)
    
    st.error("🚫 **Universal Restriction:** Avoid **Grapefruit Juice** completely. Furanocoumarins cause irreversible mechanism-based suicide inhibition of intestinal/hepatic **CYP3A4**, crashing active transformation cascades.")
    
    if "Fatty Liver (NAFLD)" in prior_morbidity or liver_stress == "Severe":
        st.warning("🥑 **NAFLD Hepatic Intervention Diet Active:** SERMs aggravate hepatic lipid accumulation. **Contraindicated:** High-fructose corn syrups and ultra-processed saturated trans-fats. **Advised:** High choline-rich inputs and Omega-3 polyunsaturated fatty acids to mitigate steatotic progression parameters.")
    elif "*4/*4" in cyp2d6_genotype or "Paroxetine" in psych_inhibitor:
        st.warning("🌱 **Phytoestrogen Restricted Diet Active:** Genetically locked Poor Metabolizers have low baseline Endoxifen. **Contraindicated:** Unmonitored soy concentrates, tofu, and flaxseed. Massive phytoestrogen amounts can competitively displace sub-therapeutic Endoxifen molecules from remaining nuclear ERα spots, causing clinical therapy failure.")
    elif cr_cl < 30:
        st.warning("🍊 **Renal Glucuronide Excretion Diet Active:** Severe clearance delays detected. **Contraindicated:** High sodium and unmitigated high protein loads that aggravate glomerular hyperfiltration stress matrices.")
    else:
        st.success("✅ **Standard Metabolic Diet Active:** Balance caloric intake; maintain uniform fat schedules to secure static GI transit times and prevent erratic **Tmax** shifts.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='med-card'>", unsafe_allow_html=True)
    if liver_stress == "Severe":
        st.markdown("<div class='med-card-header' style='background-color: #b91c1c;'>🟫 HEPATIC STATUS: SEVERE OVERLOAD (DILI RISK)</div>", unsafe_allow_html=True)
