
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import date
from io import StringIO

# =========================================================
# OncoPGx-CDDS | Tamoxifen Clinical Decision Support Demo
# Research prototype — not for autonomous clinical decisions
# =========================================================

st.set_page_config(
    page_title="OncoPGx-CDDS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------- DESIGN -------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #07111f 0%, #101b35 55%, #20123b 100%);
    color: #edf4ff;
}
[data-testid="stSidebar"] {
    background: #0a1325;
    border-right: 1px solid #26385d;
}
h1, h2, h3 { color: #e8f1ff !important; }
p, label, .stMarkdown { color: #d8e4f7; }
.hero {
    padding: 26px;
    border-radius: 20px;
    background: linear-gradient(120deg, #102b52, #33205c);
    border: 1px solid #4767a5;
    margin-bottom: 18px;
}
.panel {
    background: rgba(20, 34, 62, 0.85);
    border: 1px solid #30466d;
    border-radius: 16px;
    padding: 18px;
    margin: 8px 0;
}
.small-note { color: #aebfdb; font-size: 0.88rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>🧬 OncoPGx-CDDS</h1>
  <h3>Tamoxifen Clinical Pharmacology & Pharmacogenomics Decision Support</h3>
  <p>Integrated research prototype • PGx • Drug interactions • PK/PD • Safety • Clinician report</p>
</div>
""", unsafe_allow_html=True)

st.warning(
    "RESEARCH DEMO ONLY — Not a validated clinical prediction model. "
    "Do not use this prototype to prescribe, change, or discontinue treatment. "
    "Clinical decisions require an oncology team's review."
)

# ------------------------- SIDEBAR -------------------------
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio(
    "Open module",
    [
        "Overview",
        "Patient & Clinical Data",
        "Pharmacogenomics",
        "Drug Interactions",
        "PK/PD & AUC",
        "Toxicity & Safety",
        "Doctor Report"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Prototype v1.0 • Tamoxifen research workflow")
st.sidebar.caption("Future integration: authorized EHR, lab and genomic-report interfaces.")

# ------------------------- SESSION DEFAULTS -------------------------
defaults = {
    "patient_id": "DEMO-001",
    "patient_age": 52,
    "patient_sex": "Female",
    "weight": 65.0,
    "height": 160.0,
    "menopause": "Postmenopausal",
    "indication": "Adjuvant breast cancer",
    "er_status": "Positive",
    "her2_status": "Unknown",
    "treatment_status": "Currently taking tamoxifen",
    "dose": 20,
    "duration": "1–5 years",
    "genotype": "*1/*1",
    "phenotype": "Normal metabolizer",
    "activity_score": "1.5–2.0",
    "creatinine": 0.9,
    "alt": 25.0,
    "ast": 24.0,
    "bilirubin": 0.7,
    "adherence": "Good",
    "symptoms": [],
    "severity": 0,
    "pk_mode": "Illustrative demo data"
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Shared report facts
report = {
    "Prototype": "OncoPGx-CDDS v1.0",
    "Assessment date": str(date.today()),
    "Patient/demo ID": st.session_state.patient_id,
}

# ------------------------- OVERVIEW -------------------------
if page == "Overview":
    st.subheader("Research dashboard")
    a, b, c = st.columns(3)
    a.metric("Core modules", "6")
    b.metric("PK/PD", "AUC + Cmax + Tmax")
    c.metric("Output", "Doctor-facing report")

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### Workflow")
    st.markdown("""
    1. Enter demo patient and clinical information.
    2. Review CYP2D6 genotype/phenotype and relevant medicines.
    3. Enter measured concentration-time data or load clearly labelled demo values.
    4. Review safety flags and guideline-based considerations.
    5. Export a report for clinician review.
    """)
    st.markdown("</div>", unsafe_allow_html=True)

    st.info(
        "Automation roadmap: authorized EHR/FHIR connection, laboratory and "
        "genomic-report ingestion, source verification, human review and audit trail. "
        "These integrations are not connected in this demo."
    )

# ------------------------- PATIENT & CLINICAL DATA -------------------------
elif page == "Patient & Clinical Data":
    st.subheader("👤 Patient and clinical profile")
    st.caption("Use fictional/demo data for presentations. Avoid identifiable patient information.")

    with st.form("patient_form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            pid = st.text_input("Demo patient ID", value=st.session_state.patient_id)
            age = st.number_input("Age (years)", 18, 110, int(st.session_state.patient_age))
            sex = st.selectbox("Sex used for calculation", ["Female", "Male"])
        with c2:
            weight = st.number_input("Weight (kg)", 20.0, 250.0, float(st.session_state.weight))
            height = st.number_input("Height (cm)", 100.0, 230.0, float(st.session_state.height))
            menopause = st.selectbox(
                "Menopause status",
                ["Premenopausal", "Postmenopausal", "Perimenopausal", "Unknown"]
            )
        with c3:
            indication = st.selectbox(
                "Treatment indication",
                [
                    "Adjuvant breast cancer",
                    "Metastatic breast cancer",
                    "DCIS",
                    "Risk reduction",
                    "Other / unknown"
                ]
            )
            er = st.selectbox("Estrogen receptor (ER)", ["Positive", "Negative", "Unknown"])
            her2 = st.selectbox("HER2 status", ["Positive", "Negative", "Unknown"])

        treatment_status = st.selectbox(
            "Treatment status",
            ["Considering treatment", "Currently taking tamoxifen", "Treatment completed"]
        )
        dose = st.selectbox("Current recorded tamoxifen dose (mg/day)", [0, 10, 20, 30, 40])
        duration = st.selectbox(
            "Treatment duration",
            ["Not started", "<1 year", "1–5 years", ">5 years", "Unknown"]
        )
        adherence = st.selectbox("Reported adherence", ["Good", "Variable", "Poor", "Unknown"])

        submitted = st.form_submit_button("Save clinical profile", type="primary")

    if submitted:
        st.session_state.patient_id = pid.strip() or "DEMO-001"
        st.session_state.patient_age = age
        st.session_state.patient_sex = sex
        st.session_state.weight = weight
        st.session_state.height = height
        st.session_state.menopause = menopause
        st.session_state.indication = indication
        st.session_state.er_status = er
        st.session_state.her2_status = her2
        st.session_state.treatment_status = treatment_status
        st.session_state.dose = dose
        st.session_state.duration = duration
        st.session_state.adherence = adherence
        st.success("Profile saved for this session.")

    st.markdown("### Laboratory data")
    l1, l2, l3, l4 = st.columns(4)
    creatinine = l1.number_input("Serum creatinine (mg/dL)", 0.1, 15.0, float(st.session_state.creatinine), 0.1)
    alt = l2.number_input("ALT (U/L)", 0.0, 5000.0, float(st.session_state.alt))
    ast = l3.number_input("AST (U/L)", 0.0, 5000.0, float(st.session_state.ast))
    bilirubin = l4.number_input("Total bilirubin (mg/dL)", 0.0, 100.0, float(st.session_state.bilirubin), 0.1)

    if st.button("Save laboratory values"):
        st.session_state.creatinine = creatinine
        st.session_state.alt = alt
        st.session_state.ast = ast
        st.session_state.bilirubin = bilirubin
        st.success("Laboratory values saved.")

    age = int(st.session_state.patient_age)
    sex = st.session_state.patient_sex
    weight = float(st.session_state.weight)
    creatinine = float(st.session_state.creatinine)

    # Cockcroft–Gault CrCl estimate; not a tamoxifen dosing algorithm.
    sex_factor = 0.85 if sex == "Female" else 1.0
    crcl = ((140 - age) * weight * sex_factor) / (72 * creatinine)

    # CKD-EPI 2021 creatinine equation (adult estimate).
    scr = creatinine
    female = sex == "Female"
    k = 0.7 if female else 0.9
    alpha = -0.241 if female else -0.302
    sex_factor_egfr = 1.012 if female else 1.0
    egfr = (
        142
        * min(scr / k, 1) ** alpha
        * max(scr / k, 1) ** -1.200
        * 0.9938 ** age
        * sex_factor_egfr
    )

    st.markdown("### Calculated values")
    m1, m2 = st.columns(2)
    m1.metric("Estimated CrCl", f"{crcl:.1f} mL/min")
    m2.metric("Estimated eGFR", f"{egfr:.1f} mL/min/1.73 m²")
    st.caption(
        "These are estimates, depend on data quality and clinical context, and are "
        "not tamoxifen-specific dose calculators. Review with a clinician."
    )

# ------------------------- PHARMACOGENOMICS -------------------------
elif page == "Pharmacogenomics":
    st.subheader("🧬 CYP2D6 pharmacogenomics")

    genotype_options = [
        "*1/*1", "*1/*2", "*1/*4", "*1/*10", "*1/*41",
        "*4/*4", "*4/*10", "*10/*10", "*5/*5",
        "Other / report not available"
    ]
    genotype = st.selectbox(
        "CYP2D6 diplotype (from a validated report)",
        genotype_options,
        index=genotype_options.index(st.session_state.genotype)
        if st.session_state.genotype in genotype_options else 0
    )
    phenotype = st.selectbox(
        "Laboratory-reported phenotype",
        [
            "Ultrarapid metabolizer",
            "Normal metabolizer",
            "Intermediate metabolizer",
            "Poor metabolizer",
            "Indeterminate / unknown"
        ],
        index=[
            "Ultrarapid metabolizer",
            "Normal metabolizer",
            "Intermediate metabolizer",
            "Poor metabolizer",
            "Indeterminate / unknown"
        ].index(st.session_state.phenotype)
        if st.session_state.phenotype in [
            "Ultrarapid metabolizer", "Normal metabolizer",
            "Intermediate metabolizer", "Poor metabolizer",
            "Indeterminate / unknown"
        ] else 1
    )
    activity_score = st.selectbox(
        "Activity score (as reported by lab)",
        ["0", "0.25", "0.5", "1.0", "1.25", "1.5–2.0", ">2.0", "Unknown"]
    )

    st.session_state.genotype = genotype
    st.session_state.phenotype = phenotype
    st.session_state.activity_score = activity_score

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### Mechanistic interpretation")
    st.write(
        "Tamoxifen is metabolized through several pathways. CYP2D6 contributes "
        "to formation of endoxifen, an active metabolite. Reduced CYP2D6 activity "
        "or CYP2D6 inhibition may lower endoxifen exposure."
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if phenotype == "Poor metabolizer":
        st.error(
            "CPIC consideration: discuss alternative endocrine therapy with the "
            "oncology team. If alternatives are contraindicated, 40 mg/day has been "
            "discussed in guidance as a clinician-supervised option; it does not "
            "necessarily normalize endoxifen exposure."
        )
    elif phenotype == "Intermediate metabolizer":
        st.warning(
            "CPIC consideration: review menopausal status, allele/activity score "
            "and interacting medicines. Alternative endocrine therapy may be "
            "considered; any dose change requires oncology review."
        )
    elif phenotype in ["Normal metabolizer", "Ultrarapid metabolizer"]:
        st.success(
            "CPIC guidance generally supports standard-of-care dosing (commonly "
            "20 mg/day) and avoiding moderate/strong CYP2D6 inhibitors."
        )
    else:
        st.info("No genotype-based interpretation until a valid result is available.")

    st.caption("Genotype-to-phenotype translation can vary by allele and laboratory. Verify the original report.")

# ------------------------- DRUG INTERACTIONS -------------------------
elif page == "Drug Interactions":
    st.subheader("💊 CYP2D6 interaction screening")
    st.write("Select medicines present on the medication list. This is a screening aid, not a complete interaction checker.")

    medication_list = [
        "Fluoxetine",
        "Paroxetine",
        "Bupropion",
        "Quinidine",
        "Duloxetine",
        "Mirabegron",
        "Sertraline",
        "Citalopram",
        "Escitalopram",
        "Other / not listed"
    ]
    selected_meds = st.multiselect(     "Current medicines",     medication_list,     key="selected_meds" )

    interaction_info = {
        "Fluoxetine": ("Strong CYP2D6 inhibition", "May reduce endoxifen formation; clinician/pharmacist should review alternatives."),
        "Paroxetine": ("Strong CYP2D6 inhibition", "May reduce endoxifen formation; clinician/pharmacist should review alternatives."),
        "Bupropion": ("Strong CYP2D6 inhibition", "May reduce endoxifen formation; review indication and alternatives."),
        "Quinidine": ("Strong CYP2D6 inhibition", "May reduce endoxifen formation; review with prescriber."),
        "Duloxetine": ("Moderate CYP2D6 inhibition", "Potential to reduce endoxifen formation; review full medication list."),
        "Mirabegron": ("Moderate CYP2D6 inhibition", "Potential interaction; verify dose, indication and alternatives."),
        "Sertraline": ("Variable / weaker inhibition than fluoxetine or paroxetine", "Review overall regimen and clinical context."),
        "Citalopram": ("Generally weaker CYP2D6 inhibition", "Review with pharmacist; do not stop antidepressants abruptly."),
        "Escitalopram": ("Generally weaker CYP2D6 inhibition", "Review with pharmacist; do not stop antidepressants abruptly."),
        "Other / not listed": ("Not assessed", "Run a comprehensive interaction check using a validated clinical resource.")
    }

    if selected_meds:
        for med in selected_meds:
            level, action = interaction_info[med]
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown(f"**{med}** — {level}")
            st.write(action)
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("No medicines selected. This does not confirm absence of interactions.")

    if selected_meds and st.session_state.phenotype in [
        "Poor metabolizer", "Intermediate metabolizer"
    ]:
        st.warning(
            "Combined concern: reduced CYP2D6 activity plus a CYP2D6-inhibiting medicine "
            "warrants clinician/pharmacist review."
        )

    st.caption("Interaction strength can vary by dose and source. Confirm with an authoritative interaction database.")

# ------------------------- PK/PD & AUC -------------------------
elif page == "PK/PD & AUC":
    st.subheader("📈 Tamoxifen / Endoxifen PK/PD explorer")
    st.write(
        "Enter actual concentration-time observations for an observed AUC calculation, "
        "or load labelled illustrative data for a presentation demo."
    )

    analyte = st.selectbox("Analyte", ["Endoxifen", "Tamoxifen", "Other (specify in notes)"])
    unit = st.selectbox("Concentration unit", ["ng/mL", "µg/L", "Other / specify in notes"])
    mode = st.radio(
        "Data source",
        ["Illustrative demo data", "Enter measured concentration-time data"],
        horizontal=True
    )

    if mode == "Illustrative demo data":
        pk_df = pd.DataFrame({
            "Time (hours)": [0, 2, 4, 8, 12, 24],
            "Concentration": [0.0, 2.1, 3.8, 3.2, 2.6, 1.4]
        })
        st.warning(
            "These are invented illustrative values for demonstrating the graph and calculation. "
            "They are not patient measurements, reference ranges or a validated PK simulation."
        )
    else:
        st.caption("Use actual laboratory values and correct sampling times. Remove blank rows before calculation.")
        pk_df = st.data_editor(
            pd.DataFrame({
                "Time (hours)": [0.0, 2.0, 4.0],
                "Concentration": [None, None, None]
            }),
            num_rows="dynamic",
            use_container_width=True,
            key="pk_data_editor"
        )

    notes = st.text_input("Sampling / dose / report notes (optional)")
    df = pk_df.copy()
    df["Time (hours)"] = pd.to_numeric(df["Time (hours)"], errors="coerce")
    df["Concentration"] = pd.to_numeric(df["Concentration"], errors="coerce")
    df = df.dropna().sort_values("Time (hours)").reset_index(drop=True)

    if len(df) >= 2:
        times = df["Time (hours)"].to_numpy(dtype=float)
        conc = df["Concentration"].to_numpy(dtype=float)
        valid = (
            np.all(times >= 0)
            and np.all(conc >= 0)
            and np.all(np.diff(times) > 0)
        )

        if valid:
            # Trapezoidal observed AUC over the entered sampling interval.
            auc = float(np.sum(     (conc[:-1] + conc[1:]) * 0.5 * np.diff(times) ))
            cmax = float(np.max(conc))
            tmax = float(times[np.argmax(conc)])
            tmin, tmax_interval = float(times.min()), float(times.max())

            k1, k2, k3 = st.columns(3)
            k1.metric(f"AUC ({unit}·h)", f"{auc:.3f}")
            k2.metric(f"Cmax ({unit})", f"{cmax:.3f}")
            k3.metric("Tmax (hours)", f"{tmax:.2f}")

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=times, y=conc,
                mode="lines+markers",
                name="Concentration",
                fill="tozeroy",
                line=dict(width=3)
            ))
            fig.update_layout(
                title=f"{analyte}: concentration vs time",
                xaxis_title="Time (hours)",
                yaxis_title=f"Concentration ({unit})",
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(10,18,35,0.75)",
                height=430
            )
            st.plotly_chart(fig, use_container_width=True)

            st.info(
                f"Observed interval: {tmin:g}–{tmax_interval:g} hours. "
                "This is AUC over the entered observations only, not automatically AUC over 24 hours, "
                "AUC to infinity, steady-state exposure or a therapeutic target."
            )

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇️ Download PK/PD data (CSV)",
                data=csv,
                file_name="oncopgx_pkpd_data.csv",
                mime="text/csv"
            )
            st.markdown("#### Interpretation limits")
            st.write(
                "The graph describes the supplied data. It does not predict endoxifen concentration "
                "from genotype, infer drug exposure from dose alone, or calculate an individualized dose. "
                "A validated PK model requires appropriate sampling, assay details, dose timing, "
                "adherence and external validation."
            )
        else:
            st.error("Check data: times must be unique, non-negative and strictly increasing; concentrations must be non-negative.")
    else:
        st.info("Enter at least two complete time-concentration observations to calculate AUC.")

    st.caption("AUC is calculated by the trapezoidal rule using the concentration units and times entered.")

# ------------------------- TOXICITY & SAFETY -------------------------
elif page == "Toxicity & Safety":
    st.subheader("🩺 Toxicity and safety review")
    st.write("This module records reported symptoms and clinical flags. It is not a trained or validated toxicity predictor.")

    symptoms = st.multiselect(
        "Reported symptoms",
        [
            "Hot flashes",
            "Fatigue",
            "Nausea",
            "Mood changes",
            "Joint or muscle pain",
            "Abnormal vaginal bleeding",
            "Leg swelling or pain",
            "Shortness of breath",
            "Chest pain",
            "Visual changes",
            "Other"
        ],
        default=st.session_state.symptoms
    )
    severity = st.slider("Overall reported symptom severity (0–10)", 0, 10, int(st.session_state.severity))
    liver_concern = st.checkbox("Known liver disease or clinician-identified liver concern")
    clot_history = st.checkbox("History of venous thromboembolism / blood clot")
    pregnancy_concern = st.checkbox("Pregnancy possible or pregnancy status uncertain")

    st.session_state.symptoms = symptoms
    st.session_state.severity = severity

    if any(s in symptoms for s in ["Chest pain", "Shortness of breath", "Leg swelling or pain"]):
        st.error(
            "Urgent safety flag: these symptoms may indicate a serious condition such as a blood clot. "
            "Seek urgent medical assessment; do not rely on this demo."
        )
    if "Abnormal vaginal bleeding" in symptoms:
        st.warning("Prompt clinician assessment is important for abnormal vaginal bleeding.")
    if liver_concern or clot_history or pregnancy_concern:
        st.warning("Relevant safety history selected: review with the treating oncology team.")
    if severity >= 7:
        st.warning("High reported symptom burden: prompt clinical review is appropriate.")
    elif severity >= 4:
        st.info("Moderate reported symptom burden: document and review with the care team.")
    else:
        st.success("No high symptom-severity threshold reached in this self-reported screen.")

    st.caption(
        "Flags are rule-based prompts, not probabilities, diagnostic outputs or a validated toxicity score. "
        "Clinical evaluation and local emergency guidance take precedence."
    )

# ------------------------- DOCTOR REPORT -------------------------
elif page == "Doctor Report":
    st.subheader("📄 Clinician-facing summary")
    st.write("Review the generated summary before using it. This is a demo report, not a medical record.")

    pid = st.session_state.patient_id
    phenotype = st.session_state.phenotype
    genotype = st.session_state.genotype
    age = st.session_state.patient_age
    sex = st.session_state.patient_sex
    dose = st.session_state.dose
    indication = st.session_state.indication
    menopause = st.session_state.menopause
    adherence = st.session_state.adherence
    creatinine = st.session_state.creatinine
    alt = st.session_state.alt
    ast = st.session_state.ast
    bilirubin = st.session_state.bilirubin
    symptoms = st.session_state.symptoms
    severity = st.session_state.severity

    if phenotype in ["Normal metabolizer", "Ultrarapid metabolizer"]:
        pgx_summary = (
            "CPIC guidance generally supports standard-of-care tamoxifen dosing "
            "(commonly 20 mg/day); review CYP2D6 inhibitors."
        )
    elif phenotype == "Intermediate metabolizer":
        pgx_summary = (
            "Review allele/activity score, menopausal status and interacting medicines. "
            "Discuss endocrine alternatives with oncology; any dose change requires clinician review."
        )
    elif phenotype == "Poor metabolizer":
        pgx_summary = (
            "CPIC recommends discussing alternative endocrine therapy with oncology. "
            "40 mg/day may be considered only in selected circumstances under clinician supervision "
            "when an aromatase inhibitor is contraindicated; exposure may remain lower than in normal metabolizers."
        )
    else:
        pgx_summary = "Phenotype unknown/indeterminate: no genotype-based recommendation generated."
        
    # -------- EVIDENCE-BASED TREATMENT DECISION SUPPORT --------

    st.markdown("## 🧠 Treatment Recommendation Engine")
    st.caption(
        "Rule-based research prototype. Outputs are options for clinician review, "
        "not autonomous prescriptions."
    )

    phenotype = st.session_state.get("phenotype", "Indeterminate / unknown")
    menopause = st.session_state.get("menopause", "Unknown")
    indication = st.session_state.get("indication", "Other / unknown")
    er_status = st.session_state.get("er_status", "Unknown")
    current_dose = int(st.session_state.get("dose", 0))
    adherence = st.session_state.get("adherence", "Unknown")
    symptoms = st.session_state.get("symptoms", [])

    # These medicines must be reviewed by the treating clinician/pharmacist.
    inhibitor_meds = [
        "Fluoxetine", "Paroxetine", "Bupropion", "Quinidine",
        "Duloxetine", "Mirabegron"
    ]

    # If the user has visited the interaction page in this session,
    # its selection can be used here after adding the widget key shown below.
    selected_meds = st.session_state.get("selected_meds", [])
    relevant_meds = [m for m in selected_meds if m in inhibitor_meds]

    recommendations = []
    modifications = []
    missing_info = []
    evidence = []

    # 1. Check whether endocrine therapy suitability can be assessed.
    if er_status == "Negative":
        recommendations.append(
            "The entered ER-negative status does not establish an indication "
            "for endocrine treatment. Verify pathology and treatment plan."
        )
        missing_info.append("Confirm ER/pathology report and oncology treatment indication.")

    elif er_status == "Unknown":
        recommendations.append(
            "Do not select an endocrine regimen until hormone-receptor status is verified."
        )
        missing_info.append("ER status / pathology confirmation")

    elif indication == "Metastatic breast cancer":
        recommendations.append(
            "Review the complete metastatic treatment history, disease status, "
            "prior endocrine/CDK4/6-targeted therapy where relevant, and treatment goals "
            "before choosing an endocrine regimen."
        )
        missing_info.append(
            "Prior systemic therapies, disease status, contraindications and current oncology plan"
        )

    elif indication in ["Adjuvant breast cancer", "DCIS", "Risk reduction"]:
        if phenotype in ["Normal metabolizer", "Ultrarapid metabolizer"]:
            recommendations.append(
                "CPIC CYP2D6 guidance: standard-of-care tamoxifen dosing, commonly "
                "20 mg/day, is supported for this phenotype. This does not establish "
                "that tamoxifen is the best overall endocrine regimen for this patient."
            )
            evidence.append("CPIC CYP2D6–tamoxifen guideline, 2018")

        elif phenotype == "Intermediate metabolizer":
            recommendations.append(
                "Discuss the overall endocrine-treatment options with oncology. "
                "For eligible patients, an aromatase inhibitor may be considered; "
                "if premenopausal, ovarian function suppression may be needed."
            )
            modifications.append(
                "Review CYP2D6 allele/activity score and all CYP2D6-inhibiting medicines."
            )
            evidence.append("CPIC CYP2D6–tamoxifen guideline, 2018")

        elif phenotype == "Poor metabolizer":
            recommendations.append(
                "CPIC recommends discussing alternative endocrine therapy: an aromatase "
                "inhibitor for postmenopausal patients, or an aromatase inhibitor with "
                "ovarian function suppression for premenopausal patients, where clinically appropriate."
            )
            modifications.append(
                "If an aromatase inhibitor is contraindicated, the oncology team may consider "
                "tamoxifen 40 mg/day in selected circumstances. This is not an automatic dose change."
            )
            evidence.append("CPIC CYP2D6–tamoxifen guideline, 2018")

        else:
            recommendations.append(
                "CYP2D6 phenotype is unknown. Do not generate a genotype-based treatment preference "
                "until the laboratory result is verified."
            )
            missing_info.append("Validated CYP2D6 genotype and phenotype report")

    # 2. Menopause-related considerations.
    if menopause == "Unknown":
        missing_info.append("Menopausal status")
    elif menopause == "Premenopausal" and phenotype in [
        "Poor metabolizer", "Intermediate metabolizer"
    ]:
        modifications.append(
            "If considering an aromatase inhibitor, assess whether ovarian function suppression "
            "is appropriate; an aromatase inhibitor alone is not suitable for every premenopausal patient."
        )

    # 3. Interaction and adherence flags.
    if relevant_meds:
        modifications.append(
            "Potential CYP2D6 interaction flagged for: "
            + ", ".join(relevant_meds)
            + ". Ask the prescriber/pharmacist to assess alternatives. Do not stop these medicines abruptly."
        )

    if adherence in ["Variable", "Poor"]:
        modifications.append(
            "Review adherence, missed doses, tolerability and barriers before interpreting treatment response."
        )

    # 4. Safety flags — prompt assessment, not a toxicity prediction.
    urgent_symptoms = [
        s for s in symptoms
        if s in ["Chest pain", "Shortness of breath", "Leg swelling or pain"]
    ]
    if urgent_symptoms:
        modifications.append(
            "URGENT symptom flag: " + ", ".join(urgent_symptoms)
            + ". Prompt urgent clinical assessment is needed."
        )

    if current_dose == 0:
        modifications.append(
            "No current daily dose recorded. Confirm whether treatment has started and verify the prescription."
        )
    elif current_dose not in [10, 20, 30, 40]:
        modifications.append(
            "Verify the recorded dose against the original prescription."
        )

    # 5. Display structured output.
    st.markdown("### Preferred clinical pathway to discuss")
    for item in recommendations:
        st.info(item)

    st.markdown("### Treatment modification / review flags")
    if modifications:
        for item in modifications:
            st.warning(item)
    else:
        st.success(
            "No modification flag was triggered by the currently entered fields. "
            "This does not prove that the regimen is optimal or safe."
        )

    st.markdown("### Missing information")
    if missing_info:
        for item in sorted(set(missing_info)):
            st.write("- " + item)
    else:
        st.write(
            "No additional missing item was detected by these limited rules. "
            "The complete oncology assessment is still required."
        )

    st.markdown("### Evidence basis")
    if evidence:
        st.write("Guideline used: " + "; ".join(sorted(set(evidence))))
        st.markdown(
            "[Open CPIC tamoxifen guideline](https://pmc.ncbi.nlm.nih.gov/articles/5931215/)"
        )
    else:
        st.write(
            "No genotype-specific recommendation was selected. Verify the indication "
            "and consult current oncology guidance."
        )

    st.caption(
        "This engine does not rank all cancer regimens, estimate recurrence benefit, "
        "or validate an individualized dose. ER status, stage, recurrence risk, prior treatment, "
        "contraindications, patient preferences and current local guidance can change the decision."
    )

    report_text = f"""
# OncoPGx-CDDS — Clinician Review Report

**Report date:** {date.today()}
**Patient/demo ID:** {pid}
**System status:** Research prototype; not validated for clinical decision-making

## 1. Clinical profile
- Age: {age}
- Sex used for calculations: {sex}
- Menopause status: {menopause}
- Indication: {indication}
- Recorded tamoxifen dose: {dose} mg/day
- Reported adherence: {adherence}

## 2. Pharmacogenomics
- CYP2D6 diplotype entered: {genotype}
- Reported phenotype entered: {phenotype}
- Guideline consideration: {pgx_summary}

## 3. Laboratory values entered
- Serum creatinine: {creatinine} mg/dL
- ALT: {alt} U/L
- AST: {ast} U/L
- Total bilirubin: {bilirubin} mg/dL

## 4. Symptoms entered
- Symptoms: {", ".join(symptoms) if symptoms else "None selected"}
- Overall self-reported severity: {severity}/10

## 5. Clinical review checklist
- Confirm the original CYP2D6 laboratory report and allele interpretation.
- Review all prescribed, OTC and herbal medicines for interactions.
- Confirm indication, menopausal status, adherence and treatment history.
- Review relevant symptoms, laboratory data and contraindications.
- Verify current local prescribing information and oncology guidance.
- Do not change the prescribed dose based on this prototype alone.

## 6. PK/PD
PK/PD values are calculated in the separate PK/PD module from the selected data set.
Illustrative values are not patient measurements. No individual exposure or dose prediction is generated by this report.

## 7. Limitations
This prototype uses user-entered data and rule-based flags. It is not connected to an EHR, does not validate laboratory/genomic reports, and is not a trained or externally validated toxicity prediction model. All decisions require qualified clinical review.

## References
- CPIC Guideline for CYP2D6 and Tamoxifen Therapy (2018):
  https://pmc.ncbi.nlm.nih.gov/articles/5931215/
- FDA tamoxifen product labeling:
  https://www.accessdata.fda.gov/drugsatfda_docs/label/2018/021807s005lbl.pdf
"""
    st.markdown(report_text)
    st.download_button(
        "⬇️ Download clinician report (Markdown)",
        data=report_text,
        file_name=f"OncoPGx_report_{pid}.md",
        mime="text/markdown"
    )

st.markdown("---")
st.caption(
    "OncoPGx-CDDS is a research prototype. No real-time EHR connection, "
    "validated predictive model, or autonomous prescribing functionality is enabled."
)
