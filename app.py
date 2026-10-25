# ============================================================
# OncoPGx | Tamoxifen Clinical Decision Support Research Prototype
# Research use only — NOT for autonomous clinical decisions.
# ============================================================

import streamlit as st
import sqlite3
import json
import html
from datetime import datetime, date
from pathlib import Path

# ----------------------- APP CONFIG --------------------------

st.set_page_config(
    page_title="OncoPGx | Tamoxifen CDSS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

APP_NAME = "OncoPGx"
DB_PATH = Path("oncopgx_research.db")

# ----------------------- DESIGN ------------------------------

st.markdown(
    """
    <style>
    .stApp {
        background:
          radial-gradient(circle at 10% 10%, rgba(27,145,180,.13), transparent 30%),
          radial-gradient(circle at 90% 20%, rgba(38,180,160,.12), transparent 25%),
          linear-gradient(135deg, #f4f8fc 0%, #edf5f8 50%, #f5f8fc 100%);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #102b46 0%, #164d65 100%);
    }

    [data-testid="stSidebar"] * {
        color: #f4fbff;
    }

    .hero {
        padding: 28px;
        border-radius: 22px;
        color: white;
        background: linear-gradient(115deg, #102b46 0%, #126782 58%, #14a89e 100%);
        box-shadow: 0 12px 32px rgba(16,43,70,.18);
        margin-bottom: 20px;
    }

    .hero h1 {
        color: white;
        font-size: 2.25rem;
        margin-bottom: 5px;
    }

    .hero p {
        color: #e2f8ff;
        margin-bottom: 0;
    }

    .eyebrow {
        font-size: .78rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: #bceef0;
        font-weight: 700;
    }

    .panel {
        padding: 18px;
        border-radius: 16px;
        border: 1px solid #dce8ef;
        background: rgba(255,255,255,.88);
        box-shadow: 0 5px 18px rgba(20,55,75,.055);
        margin-bottom: 12px;
    }

    .metric-card {
        background: white;
        border: 1px solid #dbe8ef;
        border-radius: 15px;
        padding: 17px;
        min-height: 105px;
    }

    .metric-label {
        color: #60798a;
        font-size: .85rem;
        margin-bottom: 5px;
    }

    .metric-value {
        color: #103b55;
        font-size: 1.55rem;
        font-weight: 750;
    }

    .small-note {
        color: #617786;
        font-size: .84rem;
    }

    .tag {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 999px;
        background: #e1f5f4;
        color: #087c78;
        font-size: .78rem;
        font-weight: 700;
        margin: 2px;
    }

    div[data-testid="stTabs"] button {
        font-weight: 650;
    }

    div.stButton > button {
        border-radius: 10px;
        font-weight: 650;
        min-height: 2.7rem;
    }

    .disclaimer {
        border-left: 5px solid #d59a27;
        padding: 12px 16px;
        background: #fff8e8;
        color: #604814;
        border-radius: 8px;
        margin: 12px 0;
    }

    .dna {
        font-size: 2.2rem;
        margin-right: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------- DATABASE ---------------------------

def init_db():
    """Create local research database if it does not exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patient_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_time TEXT NOT NULL,
                patient_code TEXT NOT NULL,
                record_json TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS adverse_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_time TEXT NOT NULL,
                patient_code TEXT NOT NULL,
                event_name TEXT NOT NULL,
                severity TEXT NOT NULL,
                notes TEXT
            )
        """)

        conn.commit()


init_db()

# ----------------------- HELPERS -----------------------------

def metric_card(label, value, caption=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{html.escape(str(label))}</div>
            <div class="metric-value">{html.escape(str(value))}</div>
            <div class="small-note">{html.escape(str(caption))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def safe_float(value):
    try:
        if value is None or str(value).strip() == "":
            return None
        result = float(value)
        return result
    except (ValueError, TypeError):
        return None


def calculate_bmi(weight_kg, height_cm):
    if weight_kg and height_cm and height_cm > 0:
        height_m = height_cm / 100
        return round(weight_kg / (height_m ** 2), 1)
    return None


def classify_cyp2d6_activity(score):
    """
    Simplified CYP2D6 activity-score interpretation.
    Requires correct allele function, copy number and phasing
    for a real clinical interpretation.
    """
    if score is None:
        return "Unknown", "Insufficient information"

    if score < 0:
        return "Unknown", "Invalid activity score"

    if score == 0:
        return "Poor metabolizer", (
            "Reduced CYP2D6 function. Review the CPIC guideline "
            "and clinical context with an oncology clinician."
        )

    if score < 1.25:
        return "Intermediate metabolizer", (
            "Reduced CYP2D6 function may lower endoxifen exposure. "
            "Review guideline-based endocrine options with the care team."
        )

    if score <= 2.25:
        return "Normal metabolizer", (
            "Expected normal CYP2D6 function, subject to genotype "
            "quality and drug-interaction review."
        )

    return "Ultrarapid metabolizer", (
        "Higher CYP2D6 activity score. Do not infer that a higher "
        "tamoxifen dose is needed from this result alone."
    )


def check_cyp2d6_inhibitors(medication_text):
    """
    A small keyword screen for research demonstration only.
    This is NOT a comprehensive interaction checker.
    """
    text = (medication_text or "").lower()

    inhibitors = {
        "paroxetine": "Strong CYP2D6 inhibitor",
        "fluoxetine": "Strong CYP2D6 inhibitor",
        "bupropion": "Strong CYP2D6 inhibitor",
        "quinidine": "Strong CYP2D6 inhibitor",
        "duloxetine": "Moderate CYP2D6 inhibitor",
        "terbinafine": "CYP2D6 inhibition concern"
    }

    found = []
    for drug, description in inhibitors.items():
        if drug in text:
            found.append((drug.title(), description))

    return found


def make_report(data):
    lines = [
        "# OncoPGx — Tamoxifen Research Summary",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "> Research-use-only summary. Not a prescription or a validated clinical prediction.",
        "",
        "## Patient / Research Record",
        f"- Record code: {data.get('patient_code', 'Not entered')}",
        f"- Age: {data.get('age', 'Not entered')}",
        f"- Sex: {data.get('sex', 'Not entered')}",
        f"- Indication: {data.get('indication', 'Not entered')}",
        f"- Menopausal status: {data.get('menopausal_status', 'Not entered')}",
        "",
        "## Pharmacogenomics",
        f"- CYP2D6 diplotype: {data.get('diplotype', 'Not entered')}",
        f"- Activity score: {data.get('activity_score', 'Not entered')}",
        f"- Phenotype: {data.get('phenotype', 'Unknown')}",
        "",
        "## Treatment Context",
        f"- Tamoxifen dose recorded: {data.get('tamoxifen_dose', 'Not entered')}",
        f"- Other medications: {data.get('medications', 'Not entered')}",
        f"- Symptoms / toxicity: {data.get('symptoms', 'Not entered')}",
        "",
        "## Laboratory Context",
        f"- ALT: {data.get('alt', 'Not entered')}",
        f"- AST: {data.get('ast', 'Not entered')}",
        f"- Bilirubin: {data.get('bilirubin', 'Not entered')}",
        f"- Creatinine: {data.get('creatinine', 'Not entered')}",
        "",
        "## Clinical Review",
        data.get("clinical_review", "No review note entered."),
        "",
        "## Limitations",
        "- This prototype does not predict toxicity probability.",
        "- CYP2D6 phenotype interpretation depends on the assay and allele translation.",
        "- Drug interaction screening is incomplete.",
        "- Treatment choice and dosing require qualified clinical review.",
        "- Validate any model using appropriate clinical data before clinical use.",
    ]
    return "\n".join(lines)


def save_patient_record(data):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO patient_records
            (record_time, patient_code, record_json)
            VALUES (?, ?, ?)
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                data.get("patient_code", "UNSPECIFIED"),
                json.dumps(data, ensure_ascii=False)
            )
        )
        conn.commit()


# ----------------------- SESSION STATE -----------------------

defaults = {
    "patient_code": "PGX-001",
    "age": 50,
    "sex": "Female",
    "indication": "ER-positive breast cancer",
    "menopausal_status": "Unknown",
    "diplotype": "*1/*1",
    "activity_score": 2.0,
    "tamoxifen_dose": 20.0,
    "medications": "",
    "symptoms": "",
    "clinical_review": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ----------------------- SIDEBAR -----------------------------

with st.sidebar:
    st.markdown("# 🧬 OncoPGx")
    st.markdown("**Precision Oncology Research Lab**")
    st.markdown("---")

    st.markdown("### Research module")
    st.caption("Tamoxifen · CYP2D6 · Safety · CDSS")

    st.markdown("---")
    st.markdown("### Important")
    st.warning(
        "Research prototype only. Do not use it to independently "
        "start, stop or change a patient's medication."
    )

    st.markdown("---")
    st.caption("Version 2.0 · Research prototype")


# ----------------------- HERO HEADER -------------------------

st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">PRECISION ONCOLOGY • PHARMACOGENOMICS</div>
        <h1>🧬 OncoPGx</h1>
        <p>Tamoxifen Clinical Decision Support & Research Platform</p>
        <p>Genotype interpretation · Medication review · Safety monitoring · Research workflow</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="disclaimer">
    <b>Research-use-only notice:</b> This prototype is not a validated
    medical device. It does not make autonomous treatment decisions,
    prescribe medication, or calculate an individual's probability of
    toxicity. Every interpretation must be reviewed by a qualified
    oncology clinician or clinical pharmacologist.
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------------- NAVIGATION --------------------------

tabs = st.tabs([
    "👤 Patient Profile",
    "🧬 PGx & Labs",
    "💊 Therapy Guidance",
    "🛡️ Safety & PV",
    "📊 Research Validation",
    "📄 Tumor Board Report",
    "🗂️ Records"
])

# ======================= TAB 1 ===============================

with tabs[0]:
    st.subheader("Patient / Research Profile")
    st.write(
        "Use a coded identifier rather than a patient's name or other "
        "directly identifying information."
    )

    c1, c2 = st.columns(2)

    with c1:
        st.text_input("Research patient code", key="patient_code")
        st.number_input("Age (years)", 18, 110, key="age")
        st.selectbox(
            "Sex",
            ["Female", "Male", "Other / not recorded"],
            key="sex"
        )
        st.selectbox(
            "Menopausal status",
            ["Unknown", "Premenopausal", "Perimenopausal", "Postmenopausal"],
            key="menopausal_status"
        )

    with c2:
        st.selectbox(
            "Clinical indication",
            [
                "ER-positive breast cancer",
                "Risk reduction",
                "Other / research scenario"
            ],
            key="indication"
        )

        st.selectbox(
            "Treatment setting",
            [
                "Adjuvant",
                "Neoadjuvant",
                "Metastatic",
                "Risk reduction",
                "Not recorded"
            ],
            key="treatment_setting",
        ) if "treatment_setting" not in st.session_state else st.selectbox(
            "Treatment setting",
            ["Adjuvant", "Neoadjuvant", "Metastatic",
             "Risk reduction", "Not recorded"],
            key="treatment_setting"
        )

        st.text_input(
            "Study / cohort code (optional)",
            key="study_code"
        )

    weight = st.number_input(
        "Weight (kg)", min_value=0.0, max_value=350.0,
        value=float(st.session_state.get("weight", 65.0)), step=0.5
    )
    height = st.number_input(
        "Height (cm)", min_value=0.0, max_value=250.0,
        value=float(st.session_state.get("height", 160.0)), step=0.5
    )

    bmi = calculate_bmi(weight, height)

    a, b, c = st.columns(3)
    with a:
        metric_card("Patient code", st.session_state.patient_code)
    with b:
        metric_card("Age", f"{st.session_state.age} years")
    with c:
        metric_card("BMI", f"{bmi}" if bmi else "Not calculated",
                    "Descriptive measure only")

    st.caption(
        "BMI is included for research context; it is not used here "
        "to select or calculate a tamoxifen dose."
    )

# ======================= TAB 2 ===============================

with tabs[1]:
    st.subheader("CYP2D6 Pharmacogenomics")

    st.info(
        "Select an activity score only if a validated genotype-to-"
        "activity translation is available. The dropdown below is a "
        "simplified research input, not a genotype caller."
    )

    st.text_input("CYP2D6 diplotype (as reported by laboratory)", key="diplotype")

    st.selectbox(
        "CYP2D6 activity score",
        options=[0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0],
        key="activity_score"
    )

    phenotype, interpretation = classify_cyp2d6_activity(
        float(st.session_state.activity_score)
    )

    p1, p2 = st.columns(2)
    with p1:
        metric_card("Interpreted phenotype", phenotype)
    with p2:
        metric_card("Activity score", st.session_state.activity_score)

    st.markdown("#### Interpretation note")
    st.write(interpretation)

    st.markdown("---")
    st.subheader("Laboratory context")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        alt = st.number_input("ALT (U/L)", min_value=0.0, value=25.0, step=1.0)
    with c2:
        ast = st.number_input("AST (U/L)", min_value=0.0, value=24.0, step=1.0)
    with c3:
        bilirubin = st.number_input(
            "Total bilirubin (mg/dL)", min_value=0.0, value=0.8, step=0.1
        )
    with c4:
        creatinine = st.number_input(
            "Creatinine (mg/dL)", min_value=0.0, value=0.9, step=0.1
        )

    st.caption(
        "Enter results from the clinical record. This prototype does not "
        "automatically label these results as normal or abnormal because "
        "reference ranges vary by laboratory and clinical context."
    )

    st.markdown("#### Other relevant research inputs")

    c1, c2 = st.columns(2)
    with c1:
        adherence = st.selectbox(
            "Reported adherence",
            ["Not assessed", "Good", "Intermittent", "Poor", "Unknown"]
        )
    with c2:
        endoxifen = st.number_input(
            "Endoxifen concentration (optional; ng/mL)",
            min_value=0.0,
            value=0.0,
            step=0.1
        )

    if endoxifen == 0:
        st.caption("Endoxifen value left at 0: treated as not entered in this prototype.")

# ======================= TAB 3 ===============================

with tabs[2]:
    st.subheader("Tamoxifen Therapy Context")

    st.write(
        "Tamoxifen is commonly prescribed at 20 mg once daily in relevant "
        "breast-cancer settings. The correct regimen depends on the indication, "
        "patient context and local guideline. This page does not prescribe."
    )

    st.number_input(
        "Current recorded tamoxifen dose (mg/day)",
        min_value=0.0,
        max_value=100.0,
        step=5.0,
        key="tamoxifen_dose"
    )

    st.text_area(
        "Current medications (enter generic names, separated by commas)",
        key="medications",
        height=100,
        placeholder="Example: medicine A, medicine B"
    )

    inhibitors = check_cyp2d6_inhibitors(st.session_state.medications)

    st.markdown("#### Interaction screening")

    if inhibitors:
        st.error(
            "Potential CYP2D6 inhibitor name(s) detected. This is a "
            "keyword screen, not a comprehensive interaction check."
        )
        for drug, description in inhibitors:
            st.markdown(f"- **{drug}** — {description}")

        st.warning(
            "Ask the prescribing clinician or pharmacist to review whether "
            "an alternative medication is appropriate. Do not stop a medicine "
            "without clinical advice."
        )
    else:
        st.success(
            "No medicines from this prototype's small keyword list were detected. "
            "This does not establish that the medication list is interaction-free."
        )

    st.markdown("#### Guideline-informed discussion prompts")

    if phenotype in ["Poor metabolizer", "Intermediate metabolizer"]:
        st.warning(
            "The interpreted CYP2D6 phenotype may be associated with reduced "
            "endoxifen formation. Discuss the applicable CPIC guidance and "
            "available endocrine-treatment options with the oncology team."
        )
        st.markdown(
            "- Confirm the laboratory result and allele translation.\n"
            "- Review CYP2D6-inhibiting co-medications.\n"
            "- Consider menopausal status and the full oncology treatment plan.\n"
            "- Any endocrine-treatment change or dose adjustment requires clinician review."
        )
    elif phenotype in ["Normal metabolizer", "Ultrarapid metabolizer"]:
        st.info(
            "Do not increase the dose solely because of this phenotype. "
            "Review the full clinical picture, adherence, interactions and "
            "the applicable guideline."
        )
    else:
        st.info("A reliable phenotype is not available for this record.")

    st.markdown(
        """
        **Clinical guideline reference:**  
        CPIC guideline for CYP2D6 and tamoxifen therapy:  
        https://cpicpgx.org/guidelines/guideline-for-tamoxifen-and-cyp2d6/
        """
    )

    st.caption(
        "This screen does not determine whether tamoxifen is appropriate, "
        "does not calculate an individualized dose, and does not replace "
        "the oncology team's decision."
    )

# ======================= TAB 4 ===============================

with tabs[3]:
    st.subheader("Safety Monitoring & Pharmacovigilance")

    st.text_area(
        "Current symptoms / suspected adverse events",
        key="symptoms",
        height=110,
        placeholder="Describe symptoms, onset, duration and relevant context."
    )

    st.markdown("#### Record a suspected adverse event")

    with st.form("adverse_event_form"):
        event_name = st.text_input(
            "Event / symptom",
            placeholder="e.g. hot flashes, leg swelling, abnormal bleeding"
        )

        severity = st.selectbox(
            "Reported severity",
            ["Mild", "Moderate", "Severe", "Unknown"]
        )

        event_notes = st.text_area(
            "Notes",
            placeholder="Onset, duration, suspected relationship, action taken"
        )

        submitted = st.form_submit_button("Save adverse-event entry")

        if submitted:
            if not event_name.strip():
                st.error("Enter an event name before saving.")
            else:
                with sqlite3.connect(DB_PATH) as conn:
                    conn.execute(
                        """
                        INSERT INTO adverse_events
                        (event_time, patient_code, event_name, severity, notes)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            datetime.now().isoformat(timespec="seconds"),
                            st.session_state.patient_code,
                            event_name.strip(),
                            severity,
                            event_notes.strip()
                        )
                    )
                    conn.commit()

                st.success("Adverse-event entry saved in the local research database.")

    st.markdown("---")
    st.markdown("#### Safety reminders")

    st.warning(
        "New or severe symptoms require clinical assessment. This application "
        "cannot determine causality or replace an adverse-event assessment."
    )

    st.markdown(
        """
        Examples of symptoms that should not be ignored include:
        - New unilateral leg swelling or pain, or sudden shortness of breath.
        - New or unusual vaginal bleeding.
        - Severe or rapidly worsening symptoms.

        Seek urgent medical care for potentially serious symptoms. This list is
        not exhaustive and is not a diagnostic tool.
        """
    )

# ======================= TAB 5 ===============================

with tabs[4]:
    st.subheader("Research Validation Workspace")

    st.write(
        "This section helps plan a future clinical research study. "
        "It does not claim that a toxicity prediction model has been trained "
        "or clinically validated."
    )

    st.markdown("#### Define the proposed study")

    study_title = st.text_input(
        "Proposed study title",
        value="CYP2D6 and tamoxifen-related outcomes in breast cancer"
    )

    outcome = st.selectbox(
        "Primary endpoint",
        [
            "Any-grade adverse event",
            "Grade 3 or higher toxicity",
            "Treatment discontinuation",
            "Endoxifen concentration",
            "Adherence",
            "Other / exploratory"
        ]
    )

    design = st.selectbox(
        "Study design",
        [
            "Retrospective cohort",
            "Prospective observational cohort",
            "External validation",
            "Pilot feasibility study"
        ]
    )

    data_status = st.selectbox(
        "Dataset status",
        [
            "No dataset yet",
            "Published aggregate data only",
            "De-identified individual-level dataset available",
            "Prospective recruitment planned"
        ]
    )

    sample_size = st.number_input(
        "Estimated sample size",
        min_value=0,
        max_value=1000000,
        value=0,
        step=10
    )

    st.markdown("#### Proposed candidate predictors")

    predictors = st.multiselect(
        "Select candidate variables",
        [
            "Age",
            "Menopausal status",
            "CYP2D6 genotype / activity score",
            "CYP2D6-inhibiting co-medications",
            "Tamoxifen dose",
            "Adherence",
            "Endoxifen concentration",
            "Liver function",
            "Renal function",
            "Comorbidities",
            "Concomitant medicines",
            "Treatment duration",
            "Baseline toxicity history"
        ],
        default=[
            "Age",
            "CYP2D6 genotype / activity score",
            "CYP2D6-inhibiting co-medications",
            "Tamoxifen dose",
            "Adherence"
        ]
    )

    st.markdown("#### Validation checklist")

    c1, c2 = st.columns(2)

    with c1:
        ethics = st.checkbox("Ethics approval / waiver addressed")
        privacy = st.checkbox("Data de-identification and access controls addressed")
        outcome_definition = st.checkbox("Outcome definition specified in advance")
        missingness = st.checkbox("Missing-data plan specified")

    with c2:
        leakage = st.checkbox("Data leakage prevention plan specified")
        external = st.checkbox("External validation cohort planned")
        calibration = st.checkbox("Calibration assessment planned")
        clinical_utility = st.checkbox("Clinical utility assessment planned")

    checklist = {
        "Ethics": ethics,
        "Privacy": privacy,
        "Outcome definition": outcome_definition,
        "Missing-data plan": missingness,
        "Leakage prevention": leakage,
        "External validation": external,
        "Calibration": calibration,
        "Clinical utility": clinical_utility
    }

    completed = sum(checklist.values())
    st.progress(completed / len(checklist))
    st.write(f"Research-readiness checklist: **{completed}/{len(checklist)}** items checked.")

    if completed < len(checklist):
        st.caption("Unchecked items represent tasks to address; they are not necessarily mandatory in identical form for every study.")

    study_plan = {
        "study_title": study_title,
        "design": design,
        "primary_endpoint": outcome,
        "dataset_status": data_status,
        "estimated_sample_size": sample_size,
        "candidate_predictors": predictors,
        "validation_checklist": checklist,
        "created_at": datetime.now().isoformat(timespec="seconds")
    }

    st.download_button(
        "Download research plan (JSON)",
        data=json.dumps(study_plan, indent=2),
        file_name="oncopgx_research_plan.json",
        mime="application/json"
    )

    st.markdown("#### Recommended modelling sequence")

    st.markdown(
        """
        1. Define the outcome and the time window before examining results.
        2. Establish a reproducible data dictionary and quality-control plan.
        3. Start with descriptive statistics and a clinically interpretable baseline model.
        4. Separate training and evaluation data at the patient level.
        5. Evaluate discrimination, calibration and clinically relevant errors.
        6. Use internal resampling and, where feasible, an independent external cohort.
        7. Assess clinical utility before considering prospective implementation.
        """
    )

    st.caption(
        "No model training, risk score or toxicity probability is generated by this tab."
    )

# ======================= TAB 6 ===============================

with tabs[5]:
    st.subheader("Tumor Board / Research Report")

    st.text_area(
        "Clinical review note",
        key="clinical_review",
        placeholder=(
            "Document the clinician's interpretation, uncertainties, "
            "and follow-up plan. Do not enter unnecessary identifiers."
        ),
        height=120
    )

    current_phenotype, current_interpretation = classify_cyp2d6_activity(
        float(st.session_state.activity_score)
    )

    record = {
        "patient_code": st.session_state.patient_code,
        "age": st.session_state.age,
        "sex": st.session_state.sex,
        "indication": st.session_state.indication,
        "menopausal_status": st.session_state.menopausal_status,
        "treatment_setting": st.session_state.get("treatment_setting", "Not recorded"),
        "diplotype": st.session_state.diplotype,
        "activity_score": st.session_state.activity_score,
        "phenotype": current_phenotype,
        "phenotype_interpretation": current_interpretation,
        "tamoxifen_dose": st.session_state.tamoxifen_dose,
        "medications": st.session_state.medications,
        "symptoms": st.session_state.symptoms,
        "alt": alt,
        "ast": ast,
        "bilirubin": bilirubin,
        "creatinine": creatinine,
        "adherence": adherence,
        "endoxifen": endoxifen if endoxifen > 0 else "Not entered",
        "clinical_review": st.session_state.clinical_review,
        "report_generated": datetime.now().isoformat(timespec="seconds")
    }

    r1, r2, r3 = st.columns(3)

    with r1:
        metric_card("CYP2D6 phenotype", current_phenotype)

    with r2:
        metric_card("Recorded dose", f"{st.session_state.tamoxifen_dose:g} mg/day")

    with r3:
        metric_card("Adherence", adherence)

    st.markdown("#### Report preview")
    st.markdown(make_report(record))

    st.download_button(
        "⬇️ Download research summary (Markdown)",
        data=make_report(record),
        file_name=f"OncoPGx_{st.session_state.patient_code}_summary.md",
        mime="text/markdown"
    )

    st.download_button(
        "⬇️ Download structured record (JSON)",
        data=json.dumps(record, indent=2, default=str),
        file_name=f"OncoPGx_{st.session_state.patient_code}_record.json",
        mime="application/json"
    )

    if st.button("💾 Save patient snapshot to local database"):
        save_patient_record(record)
        st.success("Snapshot saved locally. Avoid storing identifiable patient data.")

# ======================= TAB 7 ===============================

with tabs[6]:
    st.subheader("Local Research Records")

    st.caption(
        "Records are stored in a local SQLite database beside the app. "
        "For hosted deployments, persistence and privacy depend on the hosting setup."
    )

    try:
        with sqlite3.connect(DB_PATH) as conn:
            patient_df = __import__("pandas").read_sql_query(
                """
                SELECT id, record_time, patient_code, record_json
                FROM patient_records
                ORDER BY id DESC
                LIMIT 200
                """,
                conn
            )

            event_df = __import__("pandas").read_sql_query(
                """
                SELECT id, event_time, patient_code, event_name, severity, notes
                FROM adverse_events
                ORDER BY id DESC
                LIMIT 200
                """,
                conn
            )

        st.markdown("#### Saved patient snapshots")
        if patient_df.empty:
            st.info("No patient snapshots have been saved yet.")
        else:
            display_df = patient_df.drop(columns=["record_json"])
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            selected_id = st.selectbox(
                "Select snapshot ID to inspect",
                patient_df["id"].tolist()
            )

            selected_row = patient_df[patient_df["id"] == selected_id].iloc[0]
            try:
                parsed = json.loads(selected_row["record_json"])
                st.json(parsed)
            except (json.JSONDecodeError, TypeError):
                st.warning("Could not parse this saved record.")

        st.markdown("---")
        st.markdown("#### Adverse-event log")

        if event_df.empty:
            st.info("No adverse-event entries recorded.")
        else:
            st.dataframe(event_df, use_container_width=True, hide_index=True)

            st.download_button(
                "Download adverse-event log (CSV)",
                data=event_df.to_csv(index=False),
                file_name="oncopgx_adverse_events.csv",
                mime="text/csv"
            )

    except Exception as exc:
        st.error(f"Could not read local records: {exc}")

# ----------------------- FOOTER ------------------------------

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; padding:14px; color:#557080;">
        <b>🧬 OncoPGx</b> · Tamoxifen Pharmacogenomics Research Prototype<br>
        <span style="font-size:.82rem;">
        Research support only · Not a substitute for clinical judgment ·
        Validate before any clinical deployment
        </span>
    </div>
    """,
    unsafe_allow_html=True
)
