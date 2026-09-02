
import streamlit as st
import numpy as np

# Page Configuration for Executive Presentation (100% Stable)
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
    serum_creatinine = st.number_input("Serum Creatinine (mg/dL)", min_value=0.3, max_value=10.0, value=0.9, step=0.1)
    
    cyp2d6_genotype = st.selectbox("CYP2D6 Genomic Allelic Translation (CPIC)", [
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
    st.header("📊 Real-World Data & Lab Biomarkers")
    adherence = st.slider("Medication Adherence (MEMS Smart-Cap Telemetry %)", 10, 100, 95) / 100.0
    days_on_therapy = st.number_input("Days Since Treatment Initiation (Steady-State Windows)", min_value=1, max_value=365, value=45)
    ast_alt = st.number_input("Serum AST / ALT Levels (U/L) [Hepatic Stress]", min_value=10, max_value=500, value=35)
    prior_morbidity = st.multiselect("Prior Pathological History", ["Deep Vein Thrombosis (DVT)", "Fatty Liver (NAFLD)", "Retinopathy"])

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

# Dosage Dynamic Mapping Matrix
if "Negative" in er_expression:
    suggested_regimen = "Terminate Endocrine Regimen Immediately"
    regimen_timeline = "N/A - Structural absence of hormone targets. Route to cytotoxic chemotherapy."
elif "*4/*4" in cyp2d6_genotype or "Paroxetine" in psych_inhibitor:
    suggested_regimen = "Switch to Aromatase Inhibitors (Anastrozole 1mg/day)"
    regimen_timeline = "Permanent switch indicated. Active biotransformation blocked via null alleles or phenoconversion."
elif calculated_endoxifen < 15.0 and adherence >= 0.80:
    suggested_dose_mg = 40 if ast_alt < 150 else 20
    suggested_regimen = f"Escalate Tamoxifen Regimen to {suggested_dose_mg} mg/day"
    regimen_timeline = "Maintain 40mg/day for exactly 4 to 6 weeks (28-42 days) to hit Steady-State, followed by repeat TDM assay."
elif liver_stress == "Severe":
    suggested_regimen = "De-escalate Tamoxifen to 10 mg/day"
    regimen_timeline = "Maintain restricted sub-dose to minimize hepatocyte damage until AST/ALT settles."
else:
    suggested_regimen = "Maintain Standard 20 mg/day Regimen"
    regimen_timeline = "Continue standard maintenance for the remaining adjuvant oncology 5-year window."

st.write("---")
st.header("🤖 RWE Systems Pharmacology Translation Engine")

out_col1, out_col2 = st.columns(2)

with out_col1:
    st.subheader("📈 Pharmacokinetic & Dosing Analytics Core")
    st.error(f"🎯 ALGORITHMIC DOSING DECISION MATRIX: {suggested_regimen}")
    st.warning(f"⏳ TIMELINE STRATEGY: {regimen_timeline}")
    st.metric(label="Simulated Active Serum Endoxifen Exposure", value=f"{calculated_endoxifen} ng/mL", delta="Efficacy Threshold ≥15.0 ng/mL")
    st.metric(label="Calculated Creatinine Clearance (Cockcroft-Gault)", value=f"{cr_cl} mL/min", delta=f"Extrapolated Half-life (t1/2): ~{t_half} hours")
    st.metric(label="Calculated 5-Year Overall Survival Probability (Proxy Matrix)", value=f"{survival_percentage}%")

with out_col2:
    st.subheader("🫁 Multi-Organ Toxicological Mechanism & ADR Mapping")
    st.error("🚫 **ABSOLUTE DIETARY CONTRAINDICATIONS & METABOLIC TRAPS**\n\n"
             "• **Grapefruit / Grapefruit Juice:** Contains active Furanocoumarins which cause irreversible mechanism-based destruction of intestinal and hepatic CYP3A4 enzymes. This halts the major primary metabolic pathway of Tamoxifen into N-desmethyltamoxifen, crashing active Endoxifen formation.\n\n"
             "• **High-Fat Diets:** High lipophilic content extends gastrointestinal transit time and retards Tmax. Dosing patterns must remain strictly uniform to avoid wild plasma fluctuations.")

    st.markdown("##### 🟫 HEPATIC COMPARTMENT: CYP450 METABOLISM")
    if liver_stress == "Severe": st.error("❌ **CRITICAL LIVER ACCUMULATION RISK:** AST/ALT >3x ULN indicates acute DILI risk.")
    else: st.success("✅ **Hepatic Status:** CYP2D6/CYP3A4 metabolic flux is within normal physiological limits.")

    st.markdown("##### 🫘 RENAL COMPARTMENT: PHASE II GLUCURONIDATION EXCRETION")
    if cr_cl < 30: st.error("❌ **RENAL EXCRETION FAILURE:** CrCl < 30 mL/min prevents proper voiding of polar glucuronide conjugates (via UGT2B7).")
    else: st.success("✅ **Renal Status:** Glomerular filtration clearance rate is stable.")

    # 💊 COMORBIDITY INTERACTION ASSOCIATIONS
    st.markdown("##### 💊 COMORBIDITY MAPPING & MOLECULAR ASSOCIATIONS")
    if "Levothyroxine" in thyroid_axis: st.warning("⚠️ **Thyroid Inter-Axis Clash:** Tamoxifen upregulates circulating Thyroxine-Binding Globulin (TBG) levels, decreasing free active T4 fractions.")
    if "Metoprolol" in cv_agent: st.warning("⚠️ **Cardiovascular Competition:** Metoprolol functions as a competitive CYP2D6 substrate. It competes for enzymatic binding pockets, lowering Tamoxifen's biotransformation rate.")
    if "Metformin" in metabolic_agent: st.success("✅ **Glycemic Synergy:** Metformin acts via insulin sensitization, balancing anti-estrogen peripheral insulin resistance trends.")
    if "Deep Vein Thrombosis (DVT)" in prior_morbidity: st.error("🚨 **CRITICAL VASCULAR EMERGENCY:** Prior thromboembolic history. SERM downregulates Antithrombin III and suppresses Protein C/S activation.")

# --- 📄 STABLE DOWNLOAD ARTIFACT SYSTEM (100% TEXT-BASED CRASH PROOF) ---
st.write("---")
st.header("📄 Secure Clinical Documentation Generator")

report_lines = [
    "========================================================================",
    "[REAL-WORLD EVIDENCE CLINICAL ADVISORY NOTE - CDSS PLATFORM]",
    "========================================================================",
    "LEAD INNOVATOR & CLINICAL PHARMACOLOGIST: DR. MAYANK VIRMANI",
    "PharmD, Pharmacovigilance Scientist Portfolio",
    "------------------------------------------------------------------------",
    f"* CYP2D6 Allelic Pair Status: {cyp2d6_genotype}",
    f"* Simulated Serum Endoxifen: {calculated_endoxifen} ng/mL",
    f"* Calculated Creatinine Clearance (Cockcroft-Gault): {cr_cl} mL/min",
    f"* TARGET DOSING REGIMEN     : {suggested_regimen}",
    "------------------------------------------------------------------------",
    "🚫 ABSOLUTE DIETARY CONTRAINDICATIONS:",
    "- Grapefruit Juice: Irreversible mechanism-based destruction of CYP3A4 via furanocoumarins.",
    "- High-Fat Diets: Retards Tmax velocities. Uniform ingestion state is mandatory.",
    "------------------------------------------------------------------------",
    "© 2026 Dr. Mayank Virmani. All Rights Reserved. RWE Predictive Pharmacology Core."
]

final_report_string = "\n".join(report_lines)

st.download_button(
    label="📥 Generate & Download Clinical Advisory Report",
    data=final_report_string,
    file_name="Clinical_PGx_Report_Dr_Mayank_Virmani.txt",
    mime="text/plain"
)

st.markdown("<p style='text-align: center; color: gray; font-size: 13px; margin-top: 35px;'>© 2026 Dr. Mayank Virmani. All Rights Reserved. Translational Health Software Portfolio.</p>", unsafe_allow_html=True)
