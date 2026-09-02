import streamlit as st
import numpy as np

# Page Configuration for Executive Presentation (100% Stable Layout)
st.set_page_config(page_title="RWD-PGx Endocrine Stewardship Framework", layout="wide")

st.title("🧬 Systems Pharmacology & Pharmacovigilance CDSS Platform")
st.caption("Lead Innovator & Clinical Pharmacologist: Dr. Mayank Virmani | PharmD, PV Scientist Portfolio")
st.write("---")

st.info("⚗️ SYSTEM ARCHITECTURE STATUS: [Phase I-IV ADME Modeling Engine Active | Structural Interaction Tracker Online]")

col1, col2, col3 = st.columns(3)

with col1:
    st.header("🧬 PGx & Transmembrane ADME Inputs")
    age = st.slider("Patient Age (Years)", 18, 90, 52)
    weight = st.slider("Patient Weight (kg)", 40, 120, 70)
    
    menopausal_status = st.selectbox("Menopausal Status Profiling", [
        "Pre-Menopausal (Intact Ovarian Estrogen Feedback Axis)",
        "Peri-Menopausal (Fluctuating Gonadotropin Loops)",
        "Post-Menopausal (Peripheral Adipose Estrogen Conversion Window)"
    ])
    
    serum_creatinine = st.number_input("Serum Creatinine (mg/dL) [Nephron Marker]", min_value=0.3, max_value=10.0, value=0.9, step=0.1)
    
    cyp2d6_genotype = st.selectbox("CYP2D6 Genomic Allelic Translation (CPIC Focus)", [
        "*1/*1 (Normal Metabolizer - Default Activity Score: 2.0)", 
        "*1/*10 (Intermediate Metabolizer - Decreased Conversion Kinetics)", 
        "*4/*4 (Null Function - Poor Metabolizer - Activity Score: 0.0)", 
        "*1xN/*1 (Ultra-rapid Metabolizer - Accelerated Clearance/Saturation)"
    ])
    er_expression = st.radio("ERα Nuclear Receptor Expression Status", ["Positive", "Negative"], horizontal=True)

with col2:
    st.header("💊 Pharmacokinetic DDI Pathways")
    psych_inhibitor = st.selectbox("CYP2D6 Mechanism-Based Suicidal Inhibitors", [
        "None", "Paroxetine / Fluoxetine (Irreversible Phenoconversion Induced)", "Amiodarone (Moderate Competitive Inhibition)"
    ])
    thyroid_axis = st.selectbox("Thyroid Axis Concomitant Interaction", ["None", "Levothyroxine (TBG Competition Hazard)"])
    metabolic_agent = st.selectbox("Metabolic / Glycemic Co-medication", ["None", "Metformin (OCT1 Substrate Interaction)"])
    cv_agent = st.selectbox("Antihypertensive Regimen", ["None", "Metoprolol (CYP2D6 Substrate Competition)"])

with col3:
    st.header("📊 Real-World Evidence & Lab Biomarkers")
    adherence = st.slider("Medication Adherence (MEMS Smart-Cap Telemetry %)", 10, 100, 95) / 100.0
    days_on_therapy = st.number_input("Days Since Treatment Initiation (Steady-State Windows)", min_value=1, max_value=365, value=45)
    
    serum_ast = st.number_input("Serum AST Level (U/L) [Extended Range]", min_value=5, max_value=2000, value=30, step=5)
    serum_alt = st.number_input("Serum ALT Level (U/L) [Extended Range]", min_value=5, max_value=2000, value=35, step=5)
    serum_tg = st.number_input("Serum Triglycerides (mg/dL) [Lipid Biomarker]", min_value=50, max_value=800, value=150)
    
    prior_morbidity = st.multiselect("Prior Pathological History", ["Deep Vein Thrombosis (DVT)", "Fatty Liver (NAFLD)", "Retinopathy"])

# --- CORE CLINICAL PHARMACOLOGY COMPUTATION ENGINE ---
cr_cl = round(((140 - age) * weight) / (72 * serum_creatinine) * 0.85, 1)

if "*4/*4" in cyp2d6_genotype: base_metabolite = 8.8
elif "*1/*1" in cyp2d6_genotype: base_metabolite = 22.3
elif "*1/*10" in cyp2d6_genotype: base_metabolite = 14.0
else: base_metabolite = 30.5

# DDI and Phenoconversion Math Matrices
if "Paroxetine" in psych_inhibitor: base_metabolite *= 0.25 
elif "Amiodarone" in psych_inhibitor: base_metabolite *= 0.60
if "Metoprolol" in cv_agent: base_metabolite *= 0.85

if serum_ast >= 500 or serum_alt >= 500:
    liver_stress = "Fulminant Hepatotoxicity"
    base_metabolite *= 0.40
elif serum_ast >= 150 or serum_alt >= 150:
    liver_stress = "Severe"
    base_metabolite *= 0.75
else:
    liver_stress = "Normal"

if serum_tg >= 250: base_metabolite *= 0.90
calculated_endoxifen = round(base_metabolite * adherence * (1 - np.exp(-0.024 * days_on_therapy)), 1)
t_half = 14 if cr_cl >= 60 else 24 if cr_cl >= 30 else 48

base_survival = 0.95 if "Pre" in menopausal_status else 0.88 if "Peri" in menopausal_status else 0.82
if er_expression == "Negative": base_survival *= 0.60
survival_percentage = round(base_survival * 100, 1)

# Dosage Dynamic Mapping Matrix
if "Negative" in er_expression:
    suggested_regimen = "Terminate Endocrine Regimen Immediately"
    regimen_timeline = "N/A - Structural absence of hormone targets. Route to cytotoxic chemotherapy."
    guideline_source = "NCCN 2026 Guidelines"
    dose_color = "red"
elif liver_stress == "Fulminant Hepatotoxicity" or serum_tg >= 500:
    suggested_regimen = "Emergency Suspension / Halt Therapy"
    regimen_timeline = "Fulminant DILI matrix or pancreatic risk. Discontinue SERM track."
    guideline_source = "FDA Post-Marketing Pharmacovigilance Mandate"
    dose_color = "red"
elif "Post-Menopausal" in menopausal_status and ("*4/*4" in cyp2d6_genotype or "Paroxetine" in psych_inhibitor):
    suggested_regimen = "Switch to Aromatase Inhibitors (Anastrozole 1mg/day)"
    regimen_timeline = "Biotransformation blocked by non-functional alleles or permanent phenoconversion."
    guideline_source = "CPIC / NCCN Guidelines Consensus"
    dose_color = "red"
elif calculated_endoxifen < 15.0 and adherence >= 0.80:
    suggested_dose_mg = 40 if liver_stress == "Normal" else 20
    suggested_regimen = f"Escalate Tamoxifen Regimen to {suggested_dose_mg} mg/day"
    regimen_timeline = "Sub-therapeutic exposure window. Maintain 40mg for 4-6 weeks to reach steady-state, then re-check TDM."
    guideline_source = "ASCO / International Tamoxifen Consensus"
    dose_color = "orange"
elif liver_stress == "Severe":
    suggested_regimen = "De-escalate Tamoxifen to 10 mg/day"
    regimen_timeline = "Restrict parameters to ease hepatic functional load until transaminases normalize below 1.5x ULN."
    guideline_source = "NCCN Supportive Organ Preservation Framework"
    dose_color = "orange"
else:
    suggested_regimen = "Maintain Standard 20 mg/day Regimen"
    regimen_timeline = "Optimal target metabolic exposure met. Continue standard adjuvant 5-year treatment window tracking."
    guideline_source = "CPIC / NCCN Adjuvant Guidelines"
    dose_color = "green"

st.write("---")
st.header("🤖 RWE Systems Pharmacology Translation Engine")

out_col1, out_col2 = st.columns(2)

with out_col1:
    st.subheader("📈 Pharmacokinetic & Dosing Analytics Core")
    st.error(f"🎯 ALGORITHMIC DOSING DECISION MATRIX: {suggested_regimen}")
    st.warning(f"⏳ TIMELINE STRATEGY: {regimen_timeline}")
    st.info(f"📜 Compliant with: {guideline_source}")
    st.metric(label="Simulated Active Serum Endoxifen Exposure", value=f"{calculated_endoxifen} ng/mL", delta="Efficacy Threshold ≥15.0 ng/mL")
    st.metric(label="Calculated Creatinine Clearance (Cockcroft-Gault)", value=f"{cr_cl} mL/min", delta=f"Extrapolated Half-life (t1/2): ~{t_half} hours")
    st.metric(label="Calculated 5-Year Overall Survival Probability (Proxy Matrix)", value=f"{survival_percentage}%")

with out_col2:
    st.subheader("🫁 Multi-Organ Toxicological Mechanism & ADR Mapping")
    
    st.error("🚫 **ABSOLUTE DIETARY CONTRAINDICATIONS & METABOLIC TRAPS**\n\n"
             "• **Grapefruit / Grapefruit Juice:** Contains active Furanocoumarins which cause irreversible mechanism-based destruction of intestinal and hepatic CYP3A4 enzymes. This halts the major primary metabolic pathway of Tamoxifen into N-desmethyltamoxifen, crashing active Endoxifen formation.\n\n"
             "• **High-Fat Diets:** High lipophilic content extends gastrointestinal transit time and retards Tmax. Dosing patterns must remain strictly uniform to avoid wild plasma fluctuations.")

    if serum_tg >= 250 or "Fatty Liver (NAFLD)" in prior_morbidity:
        st.warning(f"⚠️ **Lipid Overload Protocol Active (TG: {serum_tg} mg/dL):** Tamoxifen suppresses fat beta-oxidation. Avoid simple sugars, alcohol, and refined fats.")

    st.markdown(f"##### 🟫 HEPATIC COMPARTMENT (AST: {serum_ast} | ALT: {serum_alt})")
    if liver_stress == "Fulminant Hepatotoxicity" or liver_stress == "Severe":
        st.error("❌ **CRITICAL LIVER ACCUMULATION RISK:** Severe hepatocyte stress locks parent drug bio-activation, dropping metabolite exposure fields.")
    else:
        st.success("✅ **Hepatic Status:** CYP2D6/CYP3A4 metabolic flux is within normal physiological limits.")

    st.markdown("##### 🫘 RENAL COMPARTMENT: PHASE II GLUCURONIDATION EXCRETION")
    if cr_cl < 30:
        st.error("❌ **RENAL EXCRETION FAILURE:** CrCl < 30 mL/min prevents proper voiding of polar glucuronide conjugates (via UGT2B7). High system tissue accumulation toxicity danger.")
    else:
        st.success("✅ **Renal Status:** Glomerular filtration clearance rate is stable.")

    # 💊 COMORBIDITY INTERACTION ASSOCIATIONS
    if "Levothyroxine" in thyroid_axis or "Metoprolol" in cv_agent or "Metformin" in metabolic_agent or "Deep Vein Thrombosis (DVT)" in prior_morbidity or "Pre" in menopausal_status:
        st.markdown("##### 💊 SYSTEMIC PHYSIOLOGICAL CROSS-TALK LOG")
        if "Pre-Menopausal" in menopausal_status: st.write("ℹ️ **Pre-Menopausal Axis:** Tamoxifen blocks ER in the pituitary, inducing a compensatory surge in GnRH/estradiol.")
        if "Levothyroxine" in thyroid_axis: st.write("⚠️ **Thyroid Inter-Axis Clash:** Tamoxifen upregulates TBG levels, decreasing free active T4 fractions.")
        if "Metoprolol" in cv_agent: st.write("⚠️ **Metoprolol DDI:** Competitive CYP2D6 substrate, lowering Tamoxifen's biotransformation rate.")
        if "Metformin" in metabolic_agent: st.write("✅ **Glycemic Synergy:** Metformin normalizes systemic insulin sensitivities.")
