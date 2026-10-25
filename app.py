
import streamlit as st
import pandas as pd
import json
from datetime import datetime

st.set_page_config(
    page_title="OncoPGx | Tamoxifen CDSS",
    page_icon="🧬",
    layout="wide"
)

# -------------------- STYLE --------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#f3f8fc,#edf6f7);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#102d48,#12677a);
}
[data-testid="stSidebar"] * { color: white; }
.hero {
    padding: 28px;
    border-radius: 20px;
    color: white;
    background: linear-gradient(110deg,#102d48,#12677a,#12a99b);
    margin-bottom: 20px;
}
.hero h1 { color: white; font-size: 2.3rem; }
.hero p { color: #e2f8ff; }
.card {
    background: white;
    border: 1px solid #d8e7ed;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 10px;
}
.warning {
    padding: 14px;
    border-radius: 10px;
    background: #fff5dc;
    border-left: 5px solid #d99b25;
}
.small { color: #597386; font-size: .85rem; }
</style>
""", unsafe_allow_html=True)

# -------------------- LOGIC --------------------
def classify_tamoxifen_as(score, allele_context):
    """
    Simplified CPIC 2018 tamoxifen-specific interpretation.
    A clinical laboratory's validated phenotype takes precedence.
    """
    if score is None:
        return "Unknown", "Activity score not available."

    if score == 0:
        return "Poor metabolizer", (
            "Reduced endoxifen formation is expected. "
            "Review guideline-based endocrine options with the oncology team."
        )

    if score == 0.5:
        return "Intermediate metabolizer", (
            "Reduced CYP2D6 function may reduce endoxifen formation. "
            "Review guideline recommendations and clinical context."
        )

    if score == 1.0:
        if allele_context == "CYP2D6*10 present":
            return "Intermediate metabolizer consideration", (
                "CPIC provides a moderate recommendation for relevant *10 "
                "genotypes. Confirm the exact diplotype and laboratory report."
            )
        if allele_context == "CYP2D6*10 absent":
            return "Normal / intermediate: context-dependent", (
                "CPIC 2018 describes lower endoxifen concentrations at AS 1.0, "
                "but recommendation strength depends on allele context. "
                "Do not make an automatic treatment decision."
            )
        return "Indeterminate without allele context", (
            "Activity score 1.0 requires diplotype/allele review. "
            "Do not automatically label this result normal or intermediate."
        )

    if score in (1.5, 2.0):
        return "Normal metabolizer", (
            "CPIC 2018 associates these scores with expected therapeutic "
            "endoxifen concentrations. Avoid moderate and strong CYP2D6 "
            "inhibitors where clinically feasible."
        )

    if score > 2.0:
        return "Ultrarapid metabolizer", (
            "CPIC 2018 associates scores above 2.0 with expected therapeutic "
            "endoxifen concentrations. Do not increase the dose solely "
            "because of this result."
        )

    return "Needs laboratory interpretation", (
        "This simplified application does not assign a definitive phenotype "
        "for this score. Consult the validated genotype-to-phenotype report."
    )


def screen_interactions(text):
    # Illustrative keyword screen only; not a complete drug database.
    groups = {
        "Strong CYP2D6 inhibitor": [
            "paroxetine", "fluoxetine", "bupropion", "quinidine"
        ],
        "Potential CYP2D6 inhibition concern": [
            "duloxetine", "terbinafine"
        ]
    }
    found = []
    lower = (text or "").lower()
    for category, drugs in groups.items():
        for drug in drugs:
            if drug in lower:
                found.append((drug.title(), category))
    return found


# -------------------- HEADER --------------------
st.markdown("""
<div class="hero">
  <div style="letter-spacing:2px;font-size:.8rem">
  PRECISION ONCOLOGY • PHARMACOGENOMICS
  </div>
  <h1>🧬 OncoPGx</h1>
  <p>Tamoxifen Clinical Decision Support Research Prototype</p>
  <p>CYP2D6 interpretation · Medication review · Safety · Research reporting</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="warning">
<b>Research-use only.</b> This prototype is not a validated medical device,
does not predict individual toxicity risk, and must not be used to independently
start, stop, or adjust treatment. Clinical decisions require qualified review.
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("# 🧬 OncoPGx")
    st.markdown("**Tamoxifen Research Workspace**")
    st.divider()
    st.caption("Prototype version 3")
    st.warning("Use synthetic/demo data only in this public demo.")

# -------------------- TABS --------------------
tabs = st.tabs([
    "Patient Profile",
    "CYP2D6 & Labs",
    "Therapy Review",
    "Safety & PV",
    "Research Plan",
    "Report"
])

# -------------------- TAB 1 --------------------
with tabs[0]:
    st.subheader("Patient / Study Profile")
    st.caption("Use a coded ID, not a name or other direct identifier.")

    c1, c2 = st.columns(2)
    with c1:
        patient_id = st.text_input("Research ID", "DEMO-001")
        age = st.number_input("Age (years)", 18, 110, 50)
        menopausal = st.selectbox(
            "Menopausal status",
            ["Unknown", "Premenopausal", "Postmenopausal"]
        )
    with c2:
        indication = st.selectbox(
            "Indication",
            ["ER-positive breast cancer", "Risk reduction", "Other / not specified"]
        )
        setting = st.selectbox(
            "Treatment setting",
            ["Adjuvant", "Neoadjuvant", "Metastatic", "Risk reduction", "Unknown"]
        )
        study_id = st.text_input("Study code (optional)", "DEMO-STUDY")

    st.info(
        "Demo record only. Do not enter identifiable patient information "
        "or confidential clinical data into a public GitHub-hosted app."
    )

# -------------------- TAB 2 --------------------
with tabs[1]:
    st.subheader("CYP2D6 Pharmacogenomics")

    diplotype = st.text_input("Reported CYP2D6 diplotype", "*1/*1")
    score = st.selectbox(
        "Activity score from validated laboratory interpretation",
        [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0]
    )
    allele_context = st.selectbox(
        "For activity score 1.0: *10 allele context",
        [
            "Not applicable",
            "Unknown / not reported",
            "CYP2D6*10 present",
            "CYP2D6*10 absent"
        ]
    )

    if score != 1.0:
        allele_context_for_logic = "Not applicable"
    else:
        allele_context_for_logic = allele_context

    phenotype, interpretation = classify_tamoxifen_as(
        float(score), allele_context_for_logic
    )

    c1, c2 = st.columns(2)
    with c1:
        st.metric("Activity score", score)
    with c2:
        st.metric("Interpretation", phenotype)

    st.markdown("#### Interpretation")
    st.write(interpretation)

    st.caption(
        "The score must come from a validated genotype interpretation. "
        "This app does not infer allele function, copy number, or phase from "
        "the diplotype text. CYP2D6 phenotype thresholds may vary by guideline "
        "and laboratory; tamoxifen-specific guidance is used here."
    )

    st.divider()
    st.subheader("Laboratory context")
    a, b, c, d = st.columns(4)
    with a:
        alt = st.number_input("ALT (U/L)", min_value=0.0, value=25.0)
    with b:
        ast = st.number_input("AST (U/L)", min_value=0.0, value=24.0)
    with c:
        bilirubin = st.number_input(
            "Bilirubin (mg/dL)", min_value=0.0, value=0.8
        )
    with d:
        creatinine = st.number_input(
            "Creatinine (mg/dL)", min_value=0.0, value=0.9
        )

    st.caption(
        "Values are recorded as entered; no normal/abnormal classification "
        "is applied because laboratory reference ranges vary."
    )

# -------------------- TAB 3 --------------------
with tabs[2]:
    st.subheader("Tamoxifen Therapy Review")

    st.markdown("""
    **Reference context:** Tamoxifen 20 mg/day is the standard dose described
    in the CPIC 2018 guideline for relevant settings. This is reference
    information, not an individualized prescription.
    """)

    current_dose = st.number_input(
        "Recorded current dose (mg/day)",
        min_value=0.0, max_value=100.0, value=20.0, step=5.0
    )

    medications = st.text_area(
        "Current medications (generic names)",
        placeholder="Enter medication names separated by commas"
    )

    findings = screen_interactions(medications)
    st.markdown("#### Interaction screen")

    if findings:
        st.error("Potential CYP2D6 inhibitor keyword detected.")
        for drug, category in findings:
            st.write(f"- **{drug}** — {category}")
        st.warning(
            "Ask the treating clinician/pharmacist to review alternatives "
            "where appropriate. Do not stop or switch medication independently."
        )
    else:
        st.info(
            "No listed keywords detected. This does not mean the medication "
            "list is free of interactions."
        )

    st.markdown("#### Guideline discussion prompt")
    if phenotype in [
        "Poor metabolizer",
        "Intermediate metabolizer",
        "Intermediate metabolizer consideration"
    ]:
        st.warning(
            "Discuss the applicable CPIC recommendation and alternative "
            "endocrine options with the oncology team. Choice depends on "
            "menopausal status, contraindications, and the complete clinical picture."
        )
    elif score == 1.0:
        st.warning(
            "Activity score 1.0 needs allele-specific interpretation. "
            "This prototype does not make an automatic treatment recommendation."
        )
    else:
        st.info(
            "Confirm the laboratory result, co-medications, adherence, "
            "and clinical context. Do not change the dose based on this screen alone."
        )

    st.markdown(
        "[Open CPIC CYP2D6–tamoxifen guideline]"
        "(https://pmc.ncbi.nlm.nih.gov/articles/5931215/)"
    )

# -------------------- TAB 4 --------------------
with tabs[3]:
    st.subheader("Safety Monitoring & Pharmacovigilance")

    symptoms = st.text_area(
        "Symptoms / suspected adverse events",
        placeholder="Describe onset, duration, severity and relevant context"
    )

    event_name = st.text_input("Event name for demo log")
    severity = st.selectbox(
        "Reported severity",
        ["Unknown", "Mild", "Moderate", "Severe"]
    )
    event_notes = st.text_area("Event notes")

    if st.button("Prepare adverse-event entry"):
        if not event_name.strip():
            st.error("Enter an event name first.")
        else:
            event = {
                "patient_id": patient_id,
                "event": event_name,
                "severity": severity,
                "notes": event_notes,
                "created_at": datetime.now().isoformat(timespec="seconds")
            }
            st.session_state["event_preview"] = event

    if "event_preview" in st.session_state:
        st.json(st.session_state["event_preview"])
        st.download_button(
            "Download event entry (JSON)",
            data=json.dumps(st.session_state["event_preview"], indent=2),
            file_name="oncopgx_event_entry.json",
            mime="application/json"
        )

    st.warning(
        "This version prepares a downloadable event entry but does not submit "
        "it to a pharmacovigilance authority or provide a validated causality assessment."
    )

    st.markdown("""
    New or severe symptoms require appropriate clinical assessment. For
    potentially serious symptoms, seek urgent medical care. This application
    is not an emergency triage system.
    """)

# -------------------- TAB 5 --------------------
with tabs[4]:
    st.subheader("Research Validation Plan")
    st.write(
        "This is a planning checklist, not a trained or validated toxicity model."
    )

    title = st.text_input(
        "Proposed study title",
        "CYP2D6 and tamoxifen-related outcomes in breast cancer"
    )
    design = st.selectbox(
        "Study design",
        [
            "Retrospective cohort",
            "Prospective observational study",
            "External validation",
            "Pilot feasibility study"
        ]
    )
    endpoint = st.selectbox(
        "Primary endpoint",
        [
            "Grade 3 or higher toxicity",
            "Any-grade adverse event",
            "Treatment discontinuation",
            "Endoxifen concentration",
            "Adherence"
        ]
    )
    dataset = st.selectbox(
        "Data availability",
        [
            "No patient-level dataset",
            "Published aggregate data only",
            "De-identified individual-level data available",
            "Prospective data collection planned"
        ]
    )
    n = st.number_input(
        "Estimated sample size", min_value=0, max_value=1000000, value=0
    )

    predictors = st.multiselect(
        "Candidate variables",
        [
            "Age", "CYP2D6 diplotype/activity score",
            "CYP2D6 inhibitor exposure", "Tamoxifen dose",
            "Adherence", "Endoxifen concentration",
            "Treatment duration", "Liver function",
            "Comorbidities", "Concomitant medicines"
        ],
        default=["Age", "CYP2D6 diplotype/activity score",
                 "CYP2D6 inhibitor exposure", "Adherence"]
    )

    checks = {
        "Ethics approval or waiver addressed":
            st.checkbox("Ethics approval / waiver addressed"),
        "Privacy and de-identification plan":
            st.checkbox("Privacy and de-identification plan"),
        "Endpoint defined in advance":
            st.checkbox("Endpoint defined in advance"),
        "Missing-data plan":
            st.checkbox("Missing-data plan"),
        "Data leakage prevention":
            st.checkbox("Data leakage prevention"),
        "External validation plan":
            st.checkbox("External validation plan"),
        "Calibration and clinical utility":
            st.checkbox("Calibration and clinical utility plan")
    }

    completed = sum(checks.values())
    st.progress(completed / len(checks))
    st.write(f"Checklist: {completed}/{len(checks)} completed.")

    plan = {
        "study_title": title,
        "design": design,
        "endpoint": endpoint,
        "dataset_status": dataset,
        "estimated_sample_size": n,
        "candidate_predictors": predictors,
        "checklist": checks,
        "generated_at": datetime.now().isoformat(timespec="seconds")
    }

    st.download_button(
        "Download research plan",
        data=json.dumps(plan, indent=2),
        file_name="oncopgx_research_plan.json",
        mime="application/json"
    )

    st.markdown("""
    **Suggested validation sequence**
    1. Predefine endpoint, eligibility criteria and time horizon.
    2. Audit data quality and missingness.
    3. Establish a transparent baseline model.
    4. Prevent patient-level leakage between training and test sets.
    5. Evaluate discrimination, calibration and clinically relevant errors.
    6. Seek independent validation before considering clinical use.
    """)

# -------------------- TAB 6 --------------------
with tabs[5]:
    st.subheader("Research Summary Report")

    clinical_note = st.text_area(
        "Reviewer note",
        placeholder="Record interpretation, uncertainty and follow-up actions"
    )

    report = {
        "application": "OncoPGx Tamoxifen CDSS Research Prototype",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "patient_code": patient_id,
        "age": age,
        "indication": indication,
        "treatment_setting": setting,
        "menopausal_status": menopausal,
        "study_code": study_id,
        "CYP2D6_diplotype_as_entered": diplotype,
        "CYP2D6_activity_score": score,
        "CYP2D6_interpretation": phenotype,
        "interpretation_note": interpretation,
        "recorded_tamoxifen_dose_mg_day": current_dose,
        "medications_as_entered": medications,
        "symptoms": symptoms,
        "laboratory_values": {
            "ALT_U_L": alt,
            "AST_U_L": ast,
            "bilirubin_mg_dL": bilirubin,
            "creatinine_mg_dL": creatinine
        },
        "reviewer_note": clinical_note,
        "limitations": [
            "Research use only",
            "Not a toxicity prediction model",
            "Interaction screen is incomplete",
            "No autonomous prescribing",
            "Phenotype must be confirmed from validated laboratory interpretation"
        ]
    }

    st.markdown("#### Preview")
    st.json(report)

    st.download_button(
        "Download report (JSON)",
        data=json.dumps(report, indent=2),
        file_name=f"OncoPGx_{patient_id or 'demo'}_report.json",
        mime="application/json"
    )

    lines = [
        "# OncoPGx Tamoxifen Research Summary",
        "",
        f"Generated: {report['generated_at']}",
        f"Patient code: {patient_id}",
        f"Age: {age}",
        f"Indication: {indication}",
        f"Treatment setting: {setting}",
        f"Menopausal status: {menopausal}",
        "",
        "## CYP2D6",
        f"Diplotype entered: {diplotype}",
        f"Activity score: {score}",
        f"Interpretation: {phenotype}",
        interpretation,
        "",
        "## Treatment context",
        f"Recorded tamoxifen dose: {current_dose} mg/day",
        f"Medication list: {medications}",
        "",
        "## Safety",
        f"Symptoms: {symptoms}",
        "",
        "## Reviewer note",
        clinical_note,
        "",
        "## Limitations",
        *[f"- {item}" for item in report["limitations"]],
        "",
        "Guideline: https://pmc.ncbi.nlm.nih.gov/articles/5931215/"
    ]

    st.download_button(
        "Download report (Markdown)",
        data="\n".join(lines),
        file_name=f"OncoPGx_{patient_id or 'demo'}_report.md",
        mime="text/markdown"
    )

st.divider()
st.caption(
    "OncoPGx · Research prototype · Clinical review required · "
    "No individual toxicity probability is calculated."
)
