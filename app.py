
from datetime import date, datetime
from io import StringIO
import math

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# ONCOPGX INDIA — T A M O X I F E N  R E S E A R C H  E X P L O R E R
# Research / educational prototype — NOT a clinical decision tool
# ============================================================

st.set_page_config(
    page_title="OncoPGx India | Tamoxifen Explorer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.2rem; padding-bottom: 2rem;}
    .hero {
        padding: 1.25rem 1.5rem;
        border: 1px solid rgba(128,128,128,.3);
        border-radius: 14px;
        margin-bottom: 1rem;
    }
    .muted {opacity: .75; font-size: .9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧬 OncoPGx India")
st.subheader("Tamoxifen pharmacogenomics & safety research explorer")

st.markdown(
    """
    <div class="hero">
    <b>Research prototype</b><br>
    Integrates recorded clinical/laboratory data, pharmacogenomic context,
    medication screening and transparent exploratory visualisations.
    It does not calculate a validated endoxifen prediction or recommend
    an individual patient's treatment or dose.
    </div>
    """,
    unsafe_allow_html=True,
)

st.warning(
    "Use fictional data for demonstrations. This application is not validated "
    "for clinical care. Do not upload identifiable patient information to a demo deployment."
)


# ------------------------- HELPERS -------------------------

def safe_float(value, default=np.nan):
    try:
        result = float(value)
        return result if np.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def fmt(value, digits=1):
    if pd.isna(value):
        return "Not available"
    return f"{value:.{digits}f}"


def cockcroft_gault(age, weight_kg, creatinine_mg_dl, sex_factor):
    """CrCl estimate in mL/min; clinical interpretation is required."""
    if (
        age <= 0
        or weight_kg <= 0
        or creatinine_mg_dl <= 0
    ):
        return np.nan

    result = ((140 - age) * weight_kg) / (72 * creatinine_mg_dl)
    return result * sex_factor


def ckd_epi_2021_creatinine(age, scr, sex):
    """
    CKD-EPI 2021 creatinine equation, eGFR in mL/min/1.73 m².
    Uses the equation's sex-specific coefficients; not a diagnosis.
    """
    if age <= 0 or scr <= 0:
        return np.nan

    if sex == "Female":
        k = 0.7
        alpha = -0.241
        sex_factor = 1.012
    else:
        k = 0.9
        alpha = -0.302
        sex_factor = 1.0

    return (
        142
        * min(scr / k, 1) ** alpha
        * max(scr / k, 1) ** (-1.200)
        * (0.9938 ** age)
        * sex_factor
    )


def numeric_status(value, upper, lower=None):
    if pd.isna(value):
        return "Not entered"
    if lower is not None and value < lower:
        return "Below configured reference"
    if value > upper:
        return "Above configured reference"
    return "Within configured reference"


def build_report(data, renal, liver_flags, interaction_rows):
    lines = [
        "ONCOPGX INDIA — TAMOXIFEN RESEARCH SCENARIO",
        "=" * 55,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Scenario ID: {data['scenario_id']}",
        "",
        "IMPORTANT",
        "This is a research/educational summary, not a diagnosis or prescription.",
        "No validated endoxifen concentration or individual risk prediction is generated.",
        "",
        "CANCER PROFILE",
        f"Intent: {data['intent']}",
        f"Histology: {data['histology']}",
        f"Stage: {data['stage']}",
        f"Metastasis: {data['metastasis']}",
        f"Tumour size (cm): {data['tumour_size']}",
        f"Nodes: {data['nodes']}",
        f"Grade: {data['grade']}",
        f"ER / PR / HER2: {data['er']} / {data['pr']} / {data['her2']}",
        "",
        "PHARMACOGENOMICS",
        f"CYP2D6 phenotype entered: {data['phenotype']}",
        f"Diplotype entered: {data['diplotype']}",
        f"Activity score entered: {data['activity_score']}",
        "",
        "RENAL ESTIMATES",
        f"Cockcroft-Gault CrCl (mL/min): {fmt(renal['crcl'])}",
        f"CKD-EPI 2021 eGFR (mL/min/1.73m²): {fmt(renal['egfr'])}",
        "These equations are not interchangeable and do not independently determine a dose.",
        "",
        "RECORDED LABORATORY VALUES",
        f"ALT: {data['alt']}",
        f"AST: {data['ast']}",
        f"Total bilirubin: {data['bilirubin']}",
        f"Albumin: {data['albumin']}",
        f"INR: {data['inr']}",
        "",
        "MEDICATION SCREEN",
    ]

    if interaction_rows:
        for row in interaction_rows:
            lines.append(f"- {row['Medication']}: {row['Screening note']}")
    else:
        lines.append("- No entered medication matched the built-in screening list.")

    lines += [
        "",
        "LABORATORY FLAGS",
        *[f"- {flag}" for flag in liver_flags],
        "",
        "MEASURED END OXIFEN",
        f"Recorded measured value: {data['measured_endoxifen']}",
        f"Unit entered: {data['endoxifen_unit']}",
        f"Collection date: {data['endoxifen_date']}",
        "The app does not infer or convert a measured value into a treatment decision.",
        "",
        "REFERENCES",
        "CPIC CYP2D6 and tamoxifen guideline: https://pmc.ncbi.nlm.nih.gov/articles/5931215/",
        "CPIC CYP2D6 gene resource: https://cpicpgx.org/gene/CYP2D6/",
        "CKD-EPI 2021 equation: https://doi.org/10.1056/NEJMoa2102953",
        "Indian genomic variation study (PMID 38426301): https://pubmed.ncbi.nlm.nih.gov/38426301/",
    ]
    return "\n".join(lines)


# ------------------------- SIDEBAR -------------------------

st.sidebar.title("Scenario setup")
st.sidebar.caption("Enter fictional or appropriately de-identified research data.")

scenario_id = st.sidebar.text_input("Scenario ID", "DEMO-001")
demo_mode = st.sidebar.checkbox("Label this as demo data", value=True)

intent = st.sidebar.selectbox(
    "Clinical context",
    [
        "Adjuvant treatment",
        "Risk reduction",
        "DCIS",
        "Metastatic disease",
        "Research-only scenario",
    ],
)

histology = st.sidebar.selectbox(
    "Histology",
    [
        "Invasive ductal carcinoma",
        "Invasive lobular carcinoma",
        "DCIS",
        "Other / not specified",
    ],
)

stage = st.sidebar.selectbox(
    "Recorded stage",
    ["0", "I", "II", "III", "IV", "Unknown / not recorded"],
)

metastasis = st.sidebar.selectbox(
    "Distant metastasis",
    ["Not recorded", "No", "Yes"],
)

tumour_size = st.sidebar.number_input(
    "Tumour size (cm)", min_value=0.0, max_value=30.0, value=0.0, step=0.1
)

nodes = st.sidebar.selectbox(
    "Regional lymph nodes",
    ["Unknown", "Negative", "Positive"],
)

grade = st.sidebar.selectbox("Tumour grade", ["Unknown", "1", "2", "3"])

st.sidebar.markdown("### Receptor status")
er = st.sidebar.selectbox("ER", ["Positive", "Negative", "Unknown"])
pr = st.sidebar.selectbox("PR", ["Positive", "Negative", "Unknown"])
her2 = st.sidebar.selectbox("HER2", ["Positive", "Negative", "Equivocal", "Unknown"])

st.sidebar.markdown("### Demographics")
age = st.sidebar.number_input("Age (years)", min_value=18, max_value=110, value=55)
sex = st.sidebar.selectbox("Sex coefficient for equations", ["Female", "Male"])
weight = st.sidebar.number_input("Weight (kg)", min_value=1.0, max_value=350.0, value=65.0)
scr = st.sidebar.number_input(
    "Serum creatinine (mg/dL)", min_value=0.1, max_value=30.0, value=1.0, step=0.1
)

st.sidebar.markdown("### CYP2D6")
phenotype = st.sidebar.selectbox(
    "Recorded CYP2D6 phenotype",
    [
        "Unknown / not tested",
        "Poor metabolizer",
        "Intermediate metabolizer",
        "Normal metabolizer",
        "Ultrarapid metabolizer",
        "Other / laboratory interpretation",
    ],
)
diplotype = st.sidebar.text_input("CYP2D6 diplotype (optional)", placeholder="e.g. lab-reported result")
activity_score = st.sidebar.text_input("Activity score (optional)", placeholder="Use laboratory report")

st.sidebar.markdown("### Medication list")
medication_options = [
    "Paroxetine",
    "Fluoxetine",
    "Bupropion",
    "Quinidine",
    "Terbinafine",
    "Duloxetine",
    "Sertraline",
    "Escitalopram",
    "Citalopram",
    "Rifampicin / rifampin",
    "Carbamazepine",
    "Phenytoin",
    "Warfarin",
    "Anastrozole",
    "Letrozole",
    "Exemestane",
    "Other / not listed",
    "None recorded",
]
medications = st.sidebar.multiselect("Current / recent medications", medication_options)

st.sidebar.markdown("### Recorded laboratory results")
alt = st.sidebar.number_input("ALT (U/L)", min_value=0.0, max_value=50000.0, value=25.0)
ast = st.sidebar.number_input("AST (U/L)", min_value=0.0, max_value=50000.0, value=25.0)
bilirubin = st.sidebar.number_input(
    "Total bilirubin (mg/dL)", min_value=0.0, max_value=100.0, value=1.0, step=0.1
)
albumin = st.sidebar.number_input(
    "Albumin (g/dL)", min_value=0.0, max_value=10.0, value=4.0, step=0.1
)
inr = st.sidebar.number_input("INR", min_value=0.0, max_value=20.0, value=1.0, step=0.1)

st.sidebar.markdown("### Measured endoxifen (optional)")
measured_endoxifen = st.sidebar.text_input(
    "Measured result (enter as reported)", placeholder="Leave blank if unavailable"
)
endoxifen_unit = st.sidebar.selectbox(
    "Reported unit", ["ng/mL", "nM", "Other / not recorded"]
)
endoxifen_date = st.sidebar.date_input("Sample collection date", value=date.today())

adherence = st.sidebar.selectbox(
    "Adherence (reported)", ["Unknown", "Consistent", "Some missed doses", "Frequent missed doses"]
)

st.sidebar.caption(
    "The app does not assume a CYP2D6 allele frequency for Indian populations "
    "and does not infer phenotype from ancestry."
)


# ------------------------- COMPUTATION -------------------------

sex_factor = 0.85 if sex == "Female" else 1.0
crcl = cockcroft_gault(age, weight, scr, sex_factor)
egfr = ckd_epi_2021_creatinine(age, scr, sex)

renal = {"crcl": crcl, "egfr": egfr}

data = {
    "scenario_id": scenario_id,
    "intent": intent,
    "histology": histology,
    "stage": stage,
    "metastasis": metastasis,
    "tumour_size": tumour_size,
    "nodes": nodes,
    "grade": grade,
    "er": er,
    "pr": pr,
    "her2": her2,
    "phenotype": phenotype,
    "diplotype": diplotype or "Not entered",
    "activity_score": activity_score or "Not entered",
    "alt": alt,
    "ast": ast,
    "bilirubin": bilirubin,
    "albumin": albumin,
    "inr": inr,
    "measured_endoxifen": measured_endoxifen or "Not entered",
    "endoxifen_unit": endoxifen_unit,
    "endoxifen_date": str(endoxifen_date),
}

# Medication screening is a review prompt, not a clinical decision.
strong_cyp2d6_inhibitors = {
    "Paroxetine": "Strong CYP2D6 inhibition; may reduce formation of endoxifen.",
    "Fluoxetine": "Strong CYP2D6 inhibition; may reduce formation of endoxifen.",
    "Bupropion": "Strong CYP2D6 inhibition; may reduce formation of endoxifen.",
    "Quinidine": "Strong CYP2D6 inhibition; may reduce formation of endoxifen.",
    "Terbinafine": "Can inhibit CYP2D6; review the medication context.",
    "Duloxetine": "CYP2D6 inhibition potential; review the medication context.",
    "Sertraline": "CYP2D6 inhibition varies; review dose and clinical context.",
}

inducers = {
    "Rifampicin / rifampin": "Enzyme induction may alter tamoxifen exposure; assess with a pharmacist/clinician.",
    "Carbamazepine": "Enzyme induction may alter drug exposure; review with a clinician.",
    "Phenytoin": "Enzyme induction may alter drug exposure; review with a clinician.",
}

interaction_rows = []
for medication in medications:
    if medication in strong_cyp2d6_inhibitors:
        interaction_rows.append(
            {"Medication": medication, "Screening note": strong_cyp2d6_inhibitors[medication]}
        )
    elif medication in inducers:
        interaction_rows.append(
            {"Medication": medication, "Screening note": inducers[medication]}
        )
    elif medication == "Warfarin":
        interaction_rows.append(
            {
                "Medication": medication,
                "Screening note": "Potential clinically important interaction; review anticoagulation and monitoring with the treating team.",
            }
        )
    elif medication in ["Anastrozole", "Letrozole", "Exemestane"]:
        interaction_rows.append(
            {
                "Medication": medication,
                "Screening note": "Endocrine therapy context. Do not combine, stop or switch treatment based on this screen.",
            }
        )
    elif medication == "Other / not listed":
        interaction_rows.append(
            {
                "Medication": medication,
                "Screening note": "Not evaluated by the built-in medication list; check a current interaction reference.",
            }
        )

liver_flags = []
# These are configurable screening prompts, not universal diagnostic cutoffs.
if alt > 40:
    liver_flags.append("ALT exceeds the app's illustrative 40 U/L screening threshold.")
if ast > 40:
    liver_flags.append("AST exceeds the app's illustrative 40 U/L screening threshold.")
if bilirubin > 1.2:
    liver_flags.append("Bilirubin exceeds the app's illustrative 1.2 mg/dL screening threshold.")
if albumin < 3.5:
    liver_flags.append("Albumin is below the app's illustrative 3.5 g/dL screening threshold.")
if inr > 1.2:
    liver_flags.append("INR exceeds the app's illustrative 1.2 screening threshold.")
if not liver_flags:
    liver_flags.append("No entered value crossed the app's illustrative screening thresholds.")

if demo_mode:
    st.info("Demo mode is ON: this scenario should be treated as fictional.")
else:
    st.info("Demo mode is OFF. Ensure you have appropriate permission and data governance before entering real data.")


# ------------------------- NAVIGATION -------------------------

tabs = st.tabs(
    [
        "📊 Dashboard",
        "🧬 PGx & PK",
        "🎗️ Cancer profile",
        "💊 Interactions",
        "🩺 Kidney & liver",
        "📝 Pharmacovigilance",
        "📄 Report & evidence",
    ]
)


# ------------------------- TAB 1: DASHBOARD -------------------------

with tabs[0]:
    st.header("Scenario dashboard")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Age", f"{age} years")
    c2.metric("CYP2D6 phenotype", phenotype.split(" / ")[0])
    c3.metric("CrCl estimate", f"{fmt(crcl)} mL/min")
    c4.metric("eGFR estimate", f"{fmt(egfr)} mL/min/1.73m²")

    st.caption(
        "Renal values are equation-derived estimates. They are not tamoxifen exposure "
        "predictions and must not be used alone to select a treatment or dose."
    )

    left, right = st.columns(2)

    with left:
        st.subheader("Recorded cancer characteristics")
        cancer_summary = pd.DataFrame(
            {
                "Field": [
                    "Intent",
                    "Histology",
                    "Stage",
                    "Metastasis",
                    "Tumour size (cm)",
                    "Nodes",
                    "Grade",
                    "ER",
                    "PR",
                    "HER2",
                ],
                "Recorded value": [
                    intent,
                    histology,
                    stage,
                    metastasis,
                    tumour_size,
                    nodes,
                    grade,
                    er,
                    pr,
                    her2,
                ],
            }
        )
        st.dataframe(cancer_summary, hide_index=True, use_container_width=True)

    with right:
        st.subheader("Recorded lab values")
        labs = pd.DataFrame(
            {
                "Lab": ["ALT", "AST", "Bilirubin", "Albumin", "INR"],
                "Value": [alt, ast, bilirubin, albumin, inr],
                "Unit": ["U/L", "U/L", "mg/dL", "g/dL", "ratio"],
            }
        )
        fig_labs = px.bar(labs, x="Lab", y="Value", color="Lab", title="Entered laboratory values")
        fig_labs.update_layout(showlegend=False)
        st.plotly_chart(fig_labs, use_container_width=True)

    st.subheader("Renal equation comparison")
    renal_chart = pd.DataFrame(
        {
            "Measure": ["Cockcroft–Gault CrCl", "CKD-EPI 2021 eGFR"],
            "Value": [crcl, egfr],
            "Unit": ["mL/min", "mL/min/1.73m²"],
        }
    )
    st.dataframe(renal_chart, hide_index=True, use_container_width=True)

    st.caption(
        "These renal measures use different equations and units; the chart is descriptive, "
        "not a head-to-head measure of treatment safety."
    )


# ------------------------- TAB 2: PGx & PK -------------------------

with tabs[1]:
    st.header("CYP2D6 pharmacogenomics & tamoxifen context")

    st.markdown("### Recorded genotype / phenotype")
    pgx = pd.DataFrame(
        [
            ["Phenotype", phenotype],
            ["Diplotype", diplotype or "Not entered"],
            ["Activity score", activity_score or "Not entered"],
        ],
        columns=["Field", "Entered value"],
    )
    st.dataframe(pgx, hide_index=True, use_container_width=True)

    if phenotype == "Unknown / not tested":
        st.info(
            "No CYP2D6 result was entered. The app will not infer a genotype or phenotype "
            "from ethnicity, geography or other demographic data."
        )
    elif phenotype == "Poor metabolizer":
        st.warning(
            "CPIC guidance describes lower endoxifen exposure in CYP2D6 poor metabolizers. "
            "This is context for a clinician/pharmacist review, not an automatic treatment recommendation."
        )
    elif phenotype == "Intermediate metabolizer":
        st.warning(
            "Intermediate metabolizer status can be associated with altered endoxifen exposure. "
            "Interpret the laboratory result using current guidance and the patient's full context."
        )
    else:
        st.info(
            "Phenotype has been recorded as entered. A phenotype label alone does not establish "
            "the patient's endoxifen concentration or clinical outcome."
        )

    st.markdown("### Measured value versus model estimate")
    st.write(
        "**Measured endoxifen:** entered by the user only, with the unit and sample date. "
        "No value is generated when a result is missing."
    )
    if measured_endoxifen.strip():
        st.success(
            f"Recorded result: {measured_endoxifen} {endoxifen_unit} "
            f"(sample date: {endoxifen_date})."
        )
    else:
        st.info("No measured endoxifen result entered.")

    st.write(
        "**Model-estimated endoxifen:** unavailable. No validated predictive model or "
        "calibrated patient-level dataset is configured in this application."
    )

    st.markdown("### Conceptual pharmacokinetic pathway")
    pathway = pd.DataFrame(
        {
            "Step": [
                "Tamoxifen administered",
                "CYP-mediated metabolism",
                "Endoxifen formed",
                "Measured concentration",
                "Clinical interpretation",
            ],
            "Status": [
                "Drug regimen not modelled",
                "Affected by genotype and interactions",
                "Not numerically predicted",
                "Optional laboratory input",
                "Requires clinical context",
            ],
        }
    )
    st.dataframe(pathway, hide_index=True, use_container_width=True)

    st.caption(
        "The app deliberately does not convert CYP2D6 phenotype into a fabricated ng/mL "
        "value, risk percentage or dosing suggestion."
    )


# ------------------------- TAB 3: CANCER PROFILE -------------------------

with tabs[2]:
    st.header("Cancer profile")

    profile = {
        "Intent": intent,
        "Histology": histology,
        "Stage": stage,
        "Distant metastasis": metastasis,
        "Tumour size (cm)": tumour_size,
        "Nodes": nodes,
        "Grade": grade,
        "ER": er,
        "PR": pr,
        "HER2": her2,
    }

    st.dataframe(
        pd.DataFrame(list(profile.items()), columns=["Feature", "Recorded value"]),
        hide_index=True,
        use_container_width=True,
    )

    if er == "Negative":
        st.warning(
            "ER is recorded as negative. Confirm pathology and the clinical indication "
            "for tamoxifen with the treating oncology team; this app does not decide eligibility."
        )
    elif er == "Unknown":
        st.info("ER status is unknown. Verify the pathology report before interpreting endocrine therapy context.")
    else:
        st.info("ER is recorded as positive. This is not, by itself, a treatment recommendation.")

    st.caption(
        "Stage, receptor status and tumour characteristics are descriptive inputs. "
        "The app does not calculate recurrence risk, survival, or treatment benefit."
    )


# ------------------------- TAB 4: INTERACTIONS -------------------------

with tabs[3]:
    st.header("Medication interaction screening")

    if interaction_rows:
        interaction_df = pd.DataFrame(interaction_rows)
        st.dataframe(interaction_df, hide_index=True, use_container_width=True)
        csv_interactions = interaction_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download interaction screen CSV",
            data=csv_interactions,
            file_name=f"{scenario_id}_interactions.csv",
            mime="text/csv",
        )
    else:
        st.info("No listed medication generated a built-in screening note.")
        st.write("Selected medications:", ", ".join(medications) if medications else "None entered")

    st.markdown("### How to interpret the screen")
    st.markdown(
        """
        - CYP2D6 inhibitors may reduce endoxifen formation.
        - Enzyme inducers may alter drug exposure; the effect should be reviewed using a
          current drug-interaction resource.
        - The presence of a medicine in this list does not prove a clinically significant
          interaction in an individual.
        - Do not stop, substitute or change a prescribed medicine based on this screen.
        """
    )

    st.markdown(
        "[CPIC CYP2D6 guideline](https://pmc.ncbi.nlm.nih.gov/articles/5931215/) · "
        "[CPIC CYP2D6 resource](https://cpicpgx.org/gene/CYP2D6/)"
    )


# ------------------------- TAB 5: KIDNEY & LIVER -------------------------

with tabs[4]:
    st.header("Kidney and liver monitoring context")

    a, b = st.columns(2)

    with a:
        st.subheader("Kidney equations")
        st.metric("Cockcroft–Gault CrCl", f"{fmt(crcl)} mL/min")
        st.metric("CKD-EPI 2021 eGFR", f"{fmt(egfr)} mL/min/1.73m²")
        st.write(
            "CrCl and eGFR are different estimates. Interpretation depends on the clinical "
            "setting, body composition, trends, and the purpose for which the equation is used."
        )

    with b:
        st.subheader("Liver laboratory screening")
        liver_df = pd.DataFrame(
            {
                "Test": ["ALT", "AST", "Total bilirubin", "Albumin", "INR"],
                "Entered result": [alt, ast, bilirubin, albumin, inr],
                "Illustrative screen": [
                    numeric_status(alt, 40),
                    numeric_status(ast, 40),
                    numeric_status(bilirubin, 1.2),
                    numeric_status(albumin, 10, 3.5),
                    numeric_status(inr, 1.2),
                ],
            }
        )
        st.dataframe(liver_df, hide_index=True, use_container_width=True)

    st.markdown("### Review prompts")
    for flag in liver_flags:
        st.write(f"- {flag}")

    st.caption(
        "The laboratory thresholds shown here are illustrative software flags, not universal "
        "reference ranges or diagnostic criteria. Interpret results against the reporting "
        "laboratory's reference interval, symptoms, history and clinician assessment. "
        "This app does not calculate Child–Pugh class or diagnose liver disease."
    )


# ------------------------- TAB 6: PHARMACOVIGILANCE -------------------------

with tabs[5]:
    st.header("Pharmacovigilance case register")
    st.write(
        "Add a de-identified safety report for this session. This register is held only in "
        "Streamlit session state and is not a secure, persistent pharmacovigilance database."
    )

    if "pv_cases" not in st.session_state:
        st.session_state.pv_cases = []

    with st.form("pv_form", clear_on_submit=True):
        pv_id = st.text_input("Case reference", placeholder="e.g. PV-DEMO-001")
        suspected_drug = st.text_input("Suspected drug", value="Tamoxifen")
        event_term = st.text_input("Adverse event / reaction term")
        onset_date = st.date_input("Event onset date", value=date.today())
        seriousness = st.selectbox(
            "Seriousness (reported)",
            ["Not assessed", "Non-serious", "Serious"],
        )
        outcome = st.selectbox(
            "Outcome (reported)",
            [
                "Unknown",
                "Recovered",
                "Recovering",
                "Not recovered",
                "Recovered with sequelae",
                "Fatal",
            ],
        )
        reporter_notes = st.text_area(
            "De-identified narrative",
            placeholder="Enter only information suitable for this demo register.",
        )
        submit_pv = st.form_submit_button("Add case to this session")

    if submit_pv:
        if not pv_id.strip() or not event_term.strip():
            st.error("Enter both a case reference and an adverse event term.")
        else:
            st.session_state.pv_cases.append(
                {
                    "Case reference": pv_id.strip(),
                    "Scenario ID": scenario_id,
                    "Suspected drug": suspected_drug.strip(),
                    "Event term": event_term.strip(),
                    "Onset date": str(onset_date),
                    "Seriousness": seriousness,
                    "Outcome": outcome,
                    "Narrative": reporter_notes.strip(),
                    "Created at": datetime.now().isoformat(timespec="minutes"),
                }
            )
            st.success("Case added to the current session.")

    if st.session_state.pv_cases:
        pv_df = pd.DataFrame(st.session_state.pv_cases)
        st.dataframe(pv_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download PV register CSV",
            data=pv_df.to_csv(index=False).encode("utf-8"),
            file_name="oncopgx_pv_register.csv",
            mime="text/csv",
        )

        if st.button("Clear session PV register"):
            st.session_state.pv_cases = []
            st.rerun()
    else:
        st.info("No pharmacovigilance cases recorded in this session.")

    st.warning(
        "This feature does not submit a report to a regulator, hospital or safety database. "
        "Follow applicable institutional and regulatory reporting procedures."
    )


# ------------------------- TAB 7: REPORT & EVIDENCE -------------------------

with tabs[6]:
    st.header("Export report & evidence")

    report_text = build_report(data, renal, liver_flags, interaction_rows)

    st.download_button(
        "📄 Download scenario report (TXT)",
        data=report_text,
        file_name=f"{scenario_id}_oncopgx_report.txt",
        mime="text/plain",
        use_container_width=True,
    )

    scenario_df = pd.DataFrame(
        [{"Field": key, "Value": str(value)} for key, value in data.items()]
    )
    st.download_button(
        "⬇️ Download scenario data (CSV)",
        data=scenario_df.to_csv(index=False).encode("utf-8"),
        file_name=f"{scenario_id}_scenario.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.subheader("Report preview")
    st.text_area("Generated report", value=report_text, height=380)

    st.subheader("Evidence and references")

    st.markdown(
        """
        1. **CPIC CYP2D6–tamoxifen guideline (2018)**  
           [Read guideline](https://pmc.ncbi.nlm.nih.gov/articles/5931215/)  
           Describes CYP2D6-related endoxifen exposure and genotype-informed guidance.
           Clinical outcome evidence and individual treatment decisions require context.

        2. **CPIC CYP2D6 gene resource**  
           [Read resource](https://cpicpgx.org/gene/CYP2D6/)  
           Pharmacogenetic information and guideline resources.

        3. **CKD-EPI 2021 creatinine equation**  
           [Read publication](https://doi.org/10.1056/NEJMoa2102953)  
           Equation reference for eGFR; not a tamoxifen dosing algorithm.

        4. **Indian genomic variation study (PMID 38426301)**  
           [Read PubMed record](https://pubmed.ncbi.nlm.nih.gov/38426301/)  
           Supports the importance of population-level genomic diversity and cautions
           against assuming one CYP2D6 allele distribution for all Indian populations.
        """
    )

    st.subheader("Model limitations")
    st.markdown(
        """
        - No externally validated endoxifen prediction model is implemented.
        - No recurrence, toxicity probability, survival or dose-response prediction is generated.
        - CYP2D6 phenotype is recorded from the user/lab and is not inferred.
        - Medication screening is a limited rule-based aid, not a comprehensive interaction checker.
        - Kidney and liver outputs are equation-derived values and illustrative laboratory flags.
        - Data entered in this app are not automatically saved to a secure clinical database.
        - Before research or clinical deployment, add validation, versioning, audit trails,
          access controls, consent/data-governance processes and appropriate clinical review.
        """
    )


# ------------------------- FOOTER -------------------------

st.divider()
st.caption(
    "OncoPGx India • Research prototype • No patient-specific dose or treatment decisions. "
    "Verify laboratory units, equations, clinical context and references before use."
)
