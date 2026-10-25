
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import base64
from pathlib import Path
from datetime import date

st.set_page_config(
    page_title="OncoPGx-CDDS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------ VISUAL DESIGN ------------------
st.markdown("""
<style>
.stApp {
    background:
      radial-gradient(ellipse at 10% 0%, #182b70 0%, transparent 42%),
      radial-gradient(ellipse at 90% 30%, #18205d 0%, transparent 40%),
      linear-gradient(135deg,#030b20 0%,#071b3c 55%,#06112b 100%);
    color:#edf5ff;
}
[data-testid="stHeader"] {background:rgba(0,0,0,0);}
[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#081a42,#071129);
    border-right:1px solid #204a8d;
}
h1,h2,h3 {color:#e8f1ff !important;}
p,label,span {color:#d6e5ff;}
div[data-testid="stMetric"] {
    background:linear-gradient(135deg,rgba(21,62,123,.75),rgba(13,27,64,.9));
    border:1px solid #285a9e;
    padding:16px;border-radius:15px;
}
div[data-testid="stForm"], div[data-testid="stExpander"] {
    border:1px solid #224c83;border-radius:14px;
}
.stButton > button, .stDownloadButton > button {
    background:linear-gradient(90deg,#087ee8,#7147f5);
    color:white;border:0;border-radius:10px;
    font-weight:600;min-height:42px;
}
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div {
    background:#102a50;border-color:#2d5c95;border-radius:9px;
}
.hero {
    border:1px solid #2c579b;
    border-radius:20px;padding:28px;
    background:
      radial-gradient(ellipse at 85% 50%,rgba(0,190,255,.24),transparent 42%),
      linear-gradient(110deg,rgba(9,32,78,.97),rgba(12,46,100,.75));
    margin:8px 0 20px 0;
}
.hero-sub {color:#9adfff;font-size:16px;}
.tag {
    display:inline-block;border:1px solid #3b75bd;
    border-radius:20px;padding:5px 11px;
    margin:4px;color:#c8e8ff;background:#102a50;
}
.small-note {color:#a8c8ed;font-size:13px;}
</style>
""", unsafe_allow_html=True)

# Optional local DNA image: save a DNA image as dna.png beside app.py.
# If absent, the gradient theme remains.
dna_file = Path(__file__).parent / "dna.png"
if dna_file.exists():
    encoded = base64.b64encode(dna_file.read_bytes()).decode()
    st.markdown(f"""
    <style>
    .hero {{
      background-image:linear-gradient(90deg,rgba(5,20,52,.98),
      rgba(5,25,65,.78),rgba(5,25,65,.35)),
      url("data:image/png;base64,{encoded}");
      background-size:cover;background-position:center;
    }}
    </style>
    """, unsafe_allow_html=True)

# ------------------ HELPERS ------------------
def safe_num(x):
    try:
        return float(x) if x is not None else 0.0
    except (ValueError, TypeError):
        return 0.0

def ckdepi_2021(scr, age, sex):
    """2021 CKD-EPI creatinine equation; eGFR mL/min/1.73m²."""
    if scr <= 0 or age <= 0:
        return None
    female = sex == "Female"
    k = 0.7 if female else 0.9
    alpha = -0.241 if female else -0.302
    value = 142 * min(scr / k, 1) ** alpha
    value *= max(scr / k, 1) ** (-1.200)
    value *= 0.9938 ** age
    if female:
        value *= 1.012
    return value

def cockcroft_gault(scr, age, weight, sex):
    """Cockcroft-Gault estimated CrCl in mL/min."""
    if scr <= 0 or age <= 0 or weight <= 0:
        return None
    result = ((140 - age) * weight) / (72 * scr)
    if sex == "Female":
        result *= 0.85
    return result

def fmt(value, digits=1):
    return "Not calculable — check required inputs" if value is None else f"{value:.{digits}f}"

# ------------------ HEADER ------------------
st.markdown("""
<div class="hero">
  <div style="font-size:36px;font-weight:800;color:#ffffff">
    🧬 OncoPGx-CDDS
  </div>
  <div style="font-size:19px;font-weight:600;color:#b8d9ff">
    Tamoxifen Clinical Pharmacology & Pharmacogenomics
  </div>
  <div class="hero-sub">
    Personalized assessment · Evidence-aware · Research decision support
  </div>
  <br>
  <span class="tag">CYP2D6 PGx</span>
  <span class="tag">Clinical Pharmacology</span>
  <span class="tag">PK/PD & Exposure</span>
  <span class="tag">Toxicity Monitoring</span>
</div>
""", unsafe_allow_html=True)

st.warning(
    "RESEARCH PROTOTYPE — NOT FOR AUTONOMOUS CLINICAL DECISIONS. "
    "Do not start, stop, switch or change treatment using this app alone. "
    "The treating oncology team must review all treatment decisions."
)

# ------------------ NAVIGATION ------------------
pages = [
    "Patient Profile",
    "Pharmacogenomics",
    "Clinical Pharmacology",
    "Interactions",
    "PK/PD & Exposure",
    "Toxicity & Safety",
    "Report",
]
page = st.sidebar.radio("🧭 WORKBENCH", pages)
st.sidebar.markdown("---")
st.sidebar.caption("Research prototype • Verify inputs and evidence.")

# ------------------ PATIENT INPUTS ------------------
st.header("👤 Patient & Genomic Information")

c1, c2, c3 = st.columns(3)
with c1:
    patient_id = st.text_input("Research patient ID", "P001")
    age = st.number_input("Age (years)", 18, 110, 50)
    sex = st.selectbox("Sex used for equations", ["Female", "Male"])
with c2:
    weight = st.number_input("Weight (kg)", 0.0, 350.0, 65.0, 0.5)
    height = st.number_input("Height (cm, optional)", 0.0, 250.0, 0.0, 0.5)
    menopause = st.selectbox(
        "Menopausal status",
        ["Unknown", "Premenopausal", "Perimenopausal", "Postmenopausal"]
    )
with c3:
    stage = st.selectbox(
        "Cancer context",
        ["Not specified", "DCIS / Stage 0", "Stage I", "Stage II",
         "Stage III", "Stage IV / metastatic", "Risk reduction"]
    )
    receptor = st.selectbox(
        "Hormone receptor status",
        ["Unknown", "ER-positive", "ER/PR-positive",
         "PR-positive only / other", "Hormone receptor-negative"]
    )
    treatment_status = st.selectbox(
        "Tamoxifen status",
        ["Not started", "Currently taking", "Previously taken",
         "Held by clinical team", "Unknown"]
    )

st.subheader("🧪 Renal function — automatic calculations")
r1, r2, r3 = st.columns(3)
with r1:
    scr = st.number_input(
        "Serum creatinine (mg/dL)", 0.0, 30.0, 0.0, 0.1,
        help="Enter a measured value. Keep 0 if unavailable."
    )
with r2:
    lab_egfr = st.number_input(
        "Reported eGFR (optional)", 0.0, 200.0, 0.0, 0.1
    )
with r3:
    lab_date = st.date_input("Lab date", value=None)

egfr = ckdepi_2021(scr, age, sex)
crcl = cockcroft_gault(scr, age, weight, sex)

m1, m2, m3 = st.columns(3)
m1.metric("Calculated eGFR", fmt(egfr), "mL/min/1.73 m²")
m2.metric("Calculated CrCl", fmt(crcl), "mL/min")
m3.metric(
    "Reported eGFR",
    fmt(lab_egfr) if lab_egfr > 0 else "Not entered",
    "mL/min/1.73 m²"
)

st.caption(
    "Equations: 2021 CKD-EPI creatinine eGFR and Cockcroft–Gault CrCl. "
    "These are estimates, not diagnoses. Verify units, sex input, weight "
    "choice, clinical context and laboratory results. They do not directly "
    "calculate a tamoxifen dose."
)

# ------------------ PGX ------------------
st.header("🧬 CYP2D6 Pharmacogenomics")

genotypes = [
    "Unknown / not tested",
    "*1/*1",
    "*1/*2",
    "*1/*4",
    "*1/*5",
    "*1/*10",
    "*1/*41",
    "*2/*2",
    "*2/*4",
    "*2/*10",
    "*2/*41",
    "*4/*4",
    "*4/*5",
    "*4/*10",
    "*4/*41",
    "*5/*5",
    "*10/*10",
    "*10/*41",
    "*41/*41",
    "*1xN/*1",
    "*1xN/*4",
    "Other / complex diplotype",
    "Lab result not interpretable",
]
phenotypes = [
    "Unknown / not tested",
    "Poor metabolizer",
    "Intermediate metabolizer",
    "Normal metabolizer",
    "Rapid metabolizer",
    "Ultrarapid metabolizer",
    "Laboratory has not assigned phenotype",
]

g1, g2, g3 = st.columns(3)
with g1:
    genotype = st.selectbox("CYP2D6 genotype / diplotype", genotypes)
with g2:
    phenotype = st.selectbox("Reported CYP2D6 phenotype", phenotypes)
with g3:
    pgx_source = st.selectbox(
        "Test source",
        ["Not tested", "Clinical laboratory", "Research laboratory", "Published dataset"]
    )
pgx_notes = st.text_area(
    "PGx interpretation / allele notes",
    placeholder="Copy the laboratory interpretation and limitations, if available."
)
st.info(
    "The diplotype list is a selection aid, not a complete allele database. "
    "Copy-number changes, structural variants, allele function and test "
    "limitations require laboratory interpretation. Do not infer phenotype "
    "from the dropdown alone."
)

# ------------------ CLINICAL PHARMACOLOGY ------------------
st.header("💊 Clinical Pharmacology")

dose_reference = st.selectbox(
    "Tamoxifen regimen reference",
    [
        "Not selected",
        "20 mg/day — common reference regimen; verify indication and guideline",
        "Other regimen — enter verified source",
    ]
)
dose_other = st.text_input(
    "Other regimen / duration / source (optional)",
    placeholder="Enter a verified guideline or prescription reference"
)
indication = st.selectbox(
    "Treatment indication",
    [
        "Not specified",
        "Adjuvant endocrine therapy",
        "Metastatic breast cancer",
        "DCIS",
        "Risk reduction / prevention",
        "Other — verify with oncology team",
    ]
)
duration = st.text_input(
    "Documented intended duration",
    placeholder="Enter clinician-recorded duration or guideline source"
)
current_dose = st.selectbox(
    "Current prescribed dose (record only)",
    ["Unknown", "5 mg/day", "10 mg/day", "20 mg/day", "Other — verify prescription"]
)
adherence = st.selectbox(
    "Adherence status",
    ["Unknown", "No reported difficulty", "Missed doses reported", "Needs review"]
)
clinical_notes = st.text_area(
    "Clinical pharmacology notes",
    placeholder="Indication, treatment history, prior endocrine therapy, clinical rationale"
)

st.info(
    "The app records guideline references but does not prescribe a dose. "
    "A dose increase, dose reduction or alternative endocrine regimen must "
    "not be generated from genotype or renal estimates alone. Confirm the "
    "current guideline and product label for the specific indication."
)

# ------------------ INTERACTIONS ------------------
st.header("🔗 Drug Interaction Screening")

inhibitors = {
    "Fluoxetine": ("Strong CYP2D6 inhibitor", "May reduce CYP2D6-mediated endoxifen formation."),
    "Paroxetine": ("Strong CYP2D6 inhibitor", "May reduce CYP2D6-mediated endoxifen formation."),
    "Bupropion": ("Strong CYP2D6 inhibitor", "May reduce CYP2D6-mediated endoxifen formation."),
    "Quinidine": ("Strong CYP2D6 inhibitor", "May reduce CYP2D6-mediated endoxifen formation."),
    "Duloxetine": ("Moderate CYP2D6 inhibitor", "May reduce CYP2D6 activity; review dose and alternatives."),
    "Mirabegron": ("Moderate CYP2D6 inhibitor", "May inhibit CYP2D6; verify clinical relevance."),
    "Sertraline": ("Potential CYP2D6 inhibition", "Effect can vary with dose and patient factors."),
    "Citalopram": ("Generally weaker CYP2D6 inhibition", "Review full medication list and clinical context."),
    "Escitalopram": ("Generally weaker CYP2D6 inhibition", "Review full medication list and clinical context."),
}
selected_meds = st.multiselect(
    "Select medicines to screen",
    list(inhibitors.keys())
)
other_meds = st.text_area(
    "Other medicines / supplements",
    placeholder="Medicine name, dose, frequency"
)

if selected_meds:
    int_df = pd.DataFrame([
        {
            "Medicine": med,
            "Interaction screen": inhibitors[med][0],
            "Mechanism / potential relevance": inhibitors[med][1],
        }
        for med in selected_meds
    ])
    st.dataframe(int_df, use_container_width=True, hide_index=True)
    st.warning(
        "Potential interaction flag only. A clinician/pharmacist should "
        "review the medicine, indication and safe alternatives. Do not "
        "stop antidepressants or other medicines independently."
    )
else:
    st.write("Select medicines to populate the interaction screen.")

interaction_plan = st.text_area(
    "Clinician review / interaction management plan",
    placeholder="Record the prescriber's assessment and agreed plan."
)

# ------------------ PK / PD ------------------
st.header("📈 PK/PD & Exposure Research")

st.write(
    "Use measured concentration-time data or a documented, validated model. "
    "This app does not infer individual concentration from genotype alone."
)
exposure_type = st.radio(
    "Data source",
    ["Measured concentration-time data", "No measured data available"]
)
auc = None
pk_df = pd.DataFrame(columns=["Time (hours)", "Concentration (ng/mL)"])

if exposure_type == "Measured concentration-time data":
    st.caption(
        "Enter one row per measured time point. Use the same analyte, "
        "consistent units and appropriate sampling times."
    )
    pk_df = st.data_editor(
        pd.DataFrame({
            "Time (hours)": [0.0, 2.0, 4.0, 8.0, 12.0, 24.0],
            "Concentration (ng/mL)": [None, None, None, None, None, None],
        }),
        num_rows="dynamic",
        use_container_width=True,
        key="pk_editor",
    )
    valid = pk_df.dropna().copy()
    if len(valid) >= 2:
        valid = valid.sort_values("Time (hours)")
        if (
            (valid["Time (hours)"] >= 0).all()
            and (valid["Concentration (ng/mL)"] >= 0).all()
            and valid["Time (hours)"].is_unique
        ):
            auc = float(np.trapezoid(
                valid["Concentration (ng/mL)"],
                valid["Time (hours)"]
            ))
            st.metric("Observed-data AUC (trapezoidal)", f"{auc:.2f}", "ng·h/mL")
            fig = px.line(
                valid, x="Time (hours)", y="Concentration (ng/mL)",
                markers=True, title="Entered concentration-time profile"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption(
                "This is AUC over the entered observation window, not "
                "automatically AUC to infinity or a validated prediction. "
                "Units and sampling design matter."
            )
        else:
            st.error("Check time points: use non-negative, unique time values and non-negative concentrations.")
    else:
        st.info("Enter at least two valid measured time-concentration pairs to calculate observed-data AUC.")

model_status = st.selectbox(
    "Prediction model status",
    [
        "No validated individual PK model configured",
        "External model available — not implemented in this prototype",
    ]
)
st.caption(
    "No synthetic concentration curve is presented as a real patient prediction. "
    "Population PK prediction requires a specified model, parameters, dosing "
    "history and validation for the intended population."
)

# ------------------ TOXICITY ------------------
st.header("🛡️ Toxicity & Safety")

risk_factors = st.multiselect(
    "Relevant clinical risk factors",
    [
        "History of DVT / pulmonary embolism",
        "Liver disease",
        "Abnormal uterine bleeding / endometrial concern",
        "History of stroke",
        "Immobility",
        "Cardiovascular risk factors",
        "Pregnancy-related concern",
        "Adherence difficulty",
        "Other significant comorbidity",
    ]
)
symptoms = [
    "Hot flashes", "Fatigue", "Nausea", "Mood changes",
    "Joint / muscle symptoms", "Vaginal symptoms",
    "Abnormal uterine bleeding", "Leg swelling or pain",
    "Chest pain / shortness of breath", "Visual symptoms",
]
symptom_values = {}
for symptom in symptoms:
    symptom_values[symptom] = st.select_slider(
        symptom,
        options=["Not reported", "Mild", "Moderate", "Severe"],
        value="Not reported",
        key=f"tox_{symptom}",
    )

toxicity_notes = st.text_area("Toxicity notes / onset / duration / impact")
active_symptoms = {
    k: v for k, v in symptom_values.items() if v != "Not reported"
}
if active_symptoms:
    tdf = pd.DataFrame(
        [{"Symptom": k, "Reported severity": v} for k, v in active_symptoms.items()]
    )
    fig = px.bar(
        tdf, x="Symptom", y="Reported severity", color="Reported severity",
        title="Patient-reported symptom severity"
    )
    fig.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)

st.error(
    "New chest pain, sudden breathlessness, one-sided leg swelling/pain, "
    "stroke-like symptoms or severe bleeding require urgent medical assessment. "
    "Do not wait for an app result."
)

# ------------------ REPORT ------------------
st.header("📄 Research Report")

review_status = st.selectbox(
    "Review status",
    ["Not reviewed", "Pending oncology review", "Reviewed by treating team"]
)
review_notes = st.text_area("Reviewer notes / follow-up plan")
alternatives = st.multiselect(
    "Options for oncology-team discussion",
    [
        "Review indication and guideline",
        "Review interacting medicines with prescriber/pharmacist",
        "Review adherence and tolerability",
        "Discuss alternative endocrine therapy",
        "Review menopausal / ovarian function status",
        "Specialist PGx consultation",
        "Consider drug-level monitoring if clinically appropriate",
    ]
)

report = f"""# OncoPGx-CDDS Research Report

**Prototype disclaimer:** Not for autonomous clinical decisions. Treating-team review required.

## Patient
- Research ID: {patient_id}
- Age: {age}
- Sex used for equations: {sex}
- Weight: {weight} kg
- Menopausal status: {menopause}
- Cancer context: {stage}
- Receptor status: {receptor}
- Tamoxifen status: {treatment_status}

## Renal estimates
- Serum creatinine: {scr} mg/dL
- Calculated 2021 CKD-EPI eGFR: {fmt(egfr)} mL/min/1.73 m²
- Calculated Cockcroft-Gault CrCl: {fmt(crcl)} mL/min
- Reported eGFR: {lab_egfr if lab_egfr > 0 else 'Not entered'}
- Lab date: {lab_date}

## Pharmacogenomics
- CYP2D6 diplotype: {genotype}
- Reported phenotype: {phenotype}
- Test source: {pgx_source}
- Notes: {pgx_notes}

## Clinical pharmacology
- Indication: {indication}
- Regimen reference: {dose_reference}
- Other regimen/source: {dose_other}
- Current prescribed dose (recorded): {current_dose}
- Duration: {duration}
- Adherence: {adherence}
- Clinical notes: {clinical_notes}

## Interaction screen
- Selected medicines: {', '.join(selected_meds) if selected_meds else 'None selected'}
- Other medicines: {other_meds}
- Review plan: {interaction_plan}

## PK/PD
- Data source: {exposure_type}
- Observed-data AUC: {auc if auc is not None else 'Not calculated'}
- Prediction model status: {model_status}

## Toxicity
- Risk factors: {', '.join(risk_factors) if risk_factors else 'None selected'}
- Symptoms: {active_symptoms if active_symptoms else 'None reported'}
- Notes: {toxicity_notes}

## Review
- Status: {review_status}
- Notes: {review_notes}
- Options for discussion: {', '.join(alternatives) if alternatives else 'None selected'}

## Limitations
- This report reflects manually entered information.
- Renal estimates are not diagnoses and do not directly determine tamoxifen dose.
- Interaction flags are screening prompts, not proof of clinical harm.
- No patient-specific PK concentration prediction is generated by this prototype.
- Final clinical interpretation and treatment decisions require the oncology team.

## References
- CPIC CYP2D6 and tamoxifen guideline: https://pmc.ncbi.nlm.nih.gov/articles/5931215/
- NCI hormone therapy: https://www.cancer.gov/types/breast/treatment/hormone-therapy
- FDA tamoxifen label: https://www.accessdata.fda.gov/drugsatfda_docs/label/2018/021807s005lbl.pdf
"""

st.download_button(
    "⬇️ Download research report",
    data=report,
    file_name=f"OncoPGx_{patient_id or 'patient'}_report.md",
    mime="text/markdown",
    use_container_width=True,
)
with st.expander("Preview report"):
    st.markdown(report)

st.markdown("---")
st.caption(
    "OncoPGx-CDDS | Research prototype. Use synthetic or properly "
    "de-identified data for demonstrations. Validate calculations and "
    "clinical content before research or clinical use."
)
