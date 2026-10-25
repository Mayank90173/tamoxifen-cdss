
# ============================================================
# OncoPGx | Tamoxifen Clinical Decision Support Prototype
# Dr. Mayank Virmani, PharmD
# Educational use only | Clinical validation pending
#
# Install:
# pip install streamlit pandas plotly
#
# Run:
# streamlit run app.py
#
# IMPORTANT:
# This is NOT a validated clinical prediction model.
# It does not calculate personalized toxicity probabilities.
# Outputs are clinician-review prompts, not prescriptions.
# Data is stored in the current Streamlit session only.
# Do not enter identifiable real-patient information.
# ============================================================

from datetime import date, datetime
import json
import math

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


APP_NAME = "OncoPGx"
AUTHOR = "Dr. Mayank Virmani, PharmD"

DISCLAIMER = (
    "EDUCATIONAL USE ONLY — CLINICAL VALIDATION PENDING. "
    "This prototype has not been validated for clinical decision-making. "
    "It does not replace oncology assessment, approved prescribing information, "
    "institutional protocols, or professional clinical judgement."
)

REFERENCES = [
    {
        "id": "R1",
        "title": "CPIC Guideline for CYP2D6 and Tamoxifen Therapy",
        "detail": "Goetz MP et al. Clinical Pharmacology & Therapeutics. 2018;103:770–777.",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC5931215/",
        "use": "CYP2D6 phenotype interpretation and genotype-informed tamoxifen considerations.",
    },
    {
        "id": "R2",
        "title": "NCCN Clinical Practice Guidelines in Oncology",
        "detail": "Breast Cancer guideline; verify the current version.",
        "url": "https://www.nccn.org/guidelines/category_1",
        "use": "Endocrine treatment options and oncology treatment context.",
    },
    {
        "id": "R3",
        "title": "CPIC guideline resources",
        "detail": "Clinical Pharmacogenetics Implementation Consortium.",
        "url": "https://cpicpgx.org/guidelines/",
        "use": "Guideline updates and pharmacogenetic implementation resources.",
    },
    {
        "id": "R4",
        "title": "Tamoxifen prescribing information",
        "detail": "U.S. National Library of Medicine, DailyMed.",
        "url": "https://dailymed.nlm.nih.gov/dailymed/search.cfm?query=tamoxifen",
        "use": "Medicine-label warnings, precautions and adverse effects.",
    },
    {
        "id": "R5",
        "title": "Aromatase inhibitor prescribing information",
        "detail": "DailyMed medicine-specific labels.",
        "url": "https://dailymed.nlm.nih.gov/dailymed/search.cfm?query=anastrozole",
        "use": "Verify safety and monitoring for the particular alternative medicine.",
    },
    {
        "id": "R6",
        "title": "CPIC pharmacogenetic resources",
        "detail": "CYP2D6 allele function and genotype-to-phenotype interpretation.",
        "url": "https://cpicpgx.org/",
        "use": "Allele function, phenotype translation and interpretation limitations.",
    },
]

CYP2D6_INHIBITORS = [
    "paroxetine",
    "fluoxetine",
    "bupropion",
    "quinidine",
    "duloxetine",
    "terbinafine",
    "cinacalcet",
]

OTHER_INTERACTION_TERMS = [
    "sertraline",
    "escitalopram",
    "citalopram",
    "mirabegron",
    "diphenhydramine",
    "amiodarone",
]


# -------------------- App configuration --------------------

st.set_page_config(
    page_title="OncoPGx | Tamoxifen CDSS",
    page_icon="🧬",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url(
      'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .stApp {
        background:
        radial-gradient(circle at 90% 0%, #d8f4f1 0%, transparent 28%),
        radial-gradient(circle at 0% 20%, #e4edff 0%, transparent 28%),
        #f5f8fc;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    h1, h2, h3 {
        font-family: 'Manrope', sans-serif !important;
    }

    .hero {
        background: linear-gradient(120deg, #10243e, #15536b, #087e8b);
        color: white;
        padding: 1.7rem;
        border-radius: 22px;
        margin-bottom: 1rem;
        box-shadow: 0 12px 30px #10243e22;
    }

    .hero h1 { color: white !important; margin-bottom: .2rem; }
    .hero p { color: #d8f4f8; margin-bottom: .2rem; }

    .warning-box {
        background: #fff7e6;
        color: #754b00;
        border: 1px solid #f1cd82;
        padding: .9rem 1rem;
        border-radius: 12px;
        margin: .6rem 0 1rem 0;
        font-size: .87rem;
    }

    .panel {
        background: #ffffffdf;
        border: 1px solid #dce7f2;
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: .8rem;
    }

    .muted {
        color: #63758b;
        font-size: .85rem;
    }

    a { color: #087e8b !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------- Session storage --------------------

DEFAULTS = {
    "patient": {},
    "labs": [],
    "medications": [],
    "adverse_events": [],
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def safe_float(value):
    try:
        if value is None or value == "":
            return None
        value = float(value)
        return value if math.isfinite(value) else None
    except (ValueError, TypeError):
        return None


def display(value):
    if value is None or value == "":
        return "Not recorded"
    return str(value)


def add_reference(ref_id):
    ref = next(
        (r for r in REFERENCES if r["id"] == ref_id),
        None,
    )
    if ref:
        st.markdown(
            f"[{ref['id']}: {ref['title']}]({ref['url']})"
        )


def get_pgx_interpretation(score, allele_context):
    if score is None:
        return (
            "Not entered",
            "Enter the laboratory-reported activity score if available.",
        )

    if score == 0:
        return (
            "Poor metabolizer",
            "CYP2D6 function is absent or very low according to "
            "the score supplied. Discuss the laboratory result and "
            "endocrine treatment options with the treating oncologist.",
        )

    if 0 < score < 1:
        return (
            "Reduced activity; generally intermediate range",
            "Reduced CYP2D6 activity may reduce endoxifen exposure. "
            "Confirm phenotype from the validated laboratory report "
            "and review treatment options with oncology.",
        )

    if score == 1:
        if allele_context == "*10 present":
            return (
                "Activity score 1.0 — *10-specific review",
                "The presence of *10 may affect tamoxifen-specific "
                "interpretation. Confirm the diplotype, allele-function "
                "translation and current guideline.",
            )

        if allele_context == "*10 absent":
            return (
                "Activity score 1.0 — verify allele translation",
                "Do not assign a final phenotype from score alone. "
                "Confirm the diplotype and the laboratory's validated "
                "phenotype interpretation.",
            )

        return (
            "Activity score 1.0 — indeterminate",
            "Allele-specific interpretation is needed. Confirm the "
            "diplotype and laboratory phenotype before applying "
            "a genotype-guided recommendation.",
        )

    if 1 < score < 1.5:
        return (
            "Intermediate range — verify laboratory interpretation",
            "Review allele function, copy number, assay coverage and "
            "the validated laboratory phenotype assignment.",
        )

    if 1.5 <= score <= 2:
        return (
            "Usually consistent with normal metabolism",
            "This score commonly falls in the normal-metabolizer range. "
            "Confirm the actual laboratory phenotype, medications and "
            "current clinical guidance.",
        )

    if score > 2:
        return (
            "Increased activity — confirm phenotype",
            "Check the laboratory's genotype-to-phenotype translation "
            "and copy-number result. Do not increase the tamoxifen dose "
            "automatically from this score.",
        )

    return (
        "Needs laboratory review",
        "Use the validated clinical laboratory interpretation.",
    )


def screen_interactions(medicine_names):
    combined = " ".join(medicine_names).lower()
    results = []

    for medicine in CYP2D6_INHIBITORS:
        if medicine in combined:
            results.append({
                "Medicine keyword": medicine.title(),
                "Signal": "Potential CYP2D6 inhibition",
                "Suggested action": (
                    "Verify the interaction and discuss suitable "
                    "alternatives with the prescriber/pharmacist."
                ),
            })

    for medicine in OTHER_INTERACTION_TERMS:
        if medicine in combined:
            results.append({
                "Medicine keyword": medicine.title(),
                "Signal": "Potential interaction; verify strength",
                "Suggested action": (
                    "Check a current interaction resource and "
                    "the medicine-specific label."
                ),
            })

    return results


def renal_interpretation(egfr, crcl):
    notes = []

    if egfr is not None:
        if egfr < 15:
            notes.append("eGFR below 15 mL/min/1.73 m²")
        elif egfr < 30:
            notes.append("eGFR below 30 mL/min/1.73 m²")
        elif egfr < 60:
            notes.append("eGFR below 60 mL/min/1.73 m²")
        else:
            notes.append("eGFR 60 mL/min/1.73 m² or above")

    if crcl is not None:
        if crcl < 30:
            notes.append("CrCl below 30 mL/min")
        elif crcl < 60:
            notes.append("CrCl below 60 mL/min")
        else:
            notes.append("CrCl 60 mL/min or above")

    if not notes:
        return "Not assessed"

    return "; ".join(notes)


def therapy_options(patient):
    menopause = patient.get("menopause", "Unknown")
    cyp = patient.get("pgx_label", "")
    stage = patient.get("stage", "")
    contraindications = patient.get("contraindications", [])

    options = []

    if menopause == "Postmenopausal":
        options.append({
            "Option": "Aromatase inhibitor strategy",
            "Clinical position": "Discuss as a guideline-supported option",
            "Rationale": (
                "For many postmenopausal patients with hormone-receptor-positive "
                "breast cancer, an aromatase inhibitor is an endocrine option. "
                "The choice depends on recurrence risk, previous treatment, "
                "bone health, tolerability and contraindications."
            ),
        })

        options.append({
            "Option": "Tamoxifen",
            "Clinical position": "May be appropriate in selected contexts",
            "Rationale": (
                "Consider prior treatment, tolerability, contraindications, "
                "patient preference, concomitant medicines and relevant PGx "
                "information."
            ),
        })

    elif menopause == "Premenopausal":
        options.append({
            "Option": "Tamoxifen",
            "Clinical position": "Common endocrine option to discuss",
            "Rationale": (
                "May be an option for many premenopausal patients. "
                "The appropriate strategy depends on disease risk, "
                "treatment intent, ovarian status and contraindications."
            ),
        })

        options.append({
            "Option": "Aromatase inhibitor plus ovarian suppression",
            "Clinical position": "Consider in selected patients",
            "Rationale": (
                "An aromatase inhibitor should not be used alone when "
                "ovarian function remains active. Ovarian suppression "
                "and specialist oversight are required."
            ),
        })

    elif menopause == "Perimenopausal / uncertain":
        options.append({
            "Option": "Confirm menopausal/ovarian status",
            "Clinical position": "Resolve before comparing AI-only therapy",
            "Rationale": (
                "Menopausal status affects endocrine treatment selection. "
                "Do not assume an aromatase inhibitor alone is suitable."
            ),
        })

    else:
        options.append({
            "Option": "Clarify menopausal/ovarian status",
            "Clinical position": "Insufficient information",
            "Rationale": (
                "A responsible comparison of endocrine options requires "
                "appropriate assessment of menopausal/ovarian status."
            ),
        })

    if "Poor metabolizer" in cyp or "Reduced activity" in cyp:
        options.append({
            "Option": "PGx-informed oncology review",
            "Clinical position": "Review CYP2D6 findings",
            "Rationale": (
                "CPIC provides genotype-informed recommendations for "
                "reduced CYP2D6 function. Routine CYP2D6 testing positions "
                "can differ between pharmacogenetic and oncology guidelines. "
                "Use the complete clinical context and local guidance."
            ),
        })

    if patient.get("prior_ai") == "AI intolerance / contraindication":
        options.append({
            "Option": "Review alternative endocrine strategies",
            "Clinical position": "Individualized decision",
            "Rationale": (
                "Document the reason for previous intolerance or "
                "contraindication and review options with oncology."
            ),
        })

    if contraindications:
        options.append({
            "Option": "Resolve safety history",
            "Clinical position": "Clinician review required",
            "Rationale": (
                "History entered: " + ", ".join(contraindications) +
                ". These are review flags, not an automated diagnosis "
                "or definitive contraindication determination."
            ),
        })

    if stage == "Metastatic / advanced":
        options.append({
            "Option": "Advanced breast cancer treatment pathway",
            "Clinical position": "Specialist decision essential",
            "Rationale": (
                "Selection depends on tumour biology, prior endocrine "
                "therapy, biomarkers, disease tempo, comorbidities and "
                "current guidelines. This prototype cannot rank all "
                "advanced-disease regimens."
            ),
        })

    return options


def build_report():
    patient = st.session_state["patient"]
    labs = st.session_state["labs"]
    meds = st.session_state["medications"]
    adverse_events = st.session_state["adverse_events"]

    lines = [
        "# OncoPGx Clinical Decision-Support Summary",
        "",
        f"**Prepared by:** {AUTHOR}",
        f"**Report date:** {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}",
        "",
        f"> **{DISCLAIMER}**",
        "",
        "## Patient and oncology context",
    ]

    fields = [
        ("Study code", "patient_code"),
        ("Age", "age"),
        ("Diagnosis", "diagnosis"),
        ("Disease context", "stage"),
        ("ER", "er"),
        ("PR", "pr"),
        ("HER2", "her2"),
        ("Menopausal status", "menopause"),
        ("Current endocrine therapy", "current_therapy"),
        ("Previous AI experience", "prior_ai"),
        ("BMI", "bmi"),
        ("Comorbidities", "comorbidities"),
        ("Safety history", "contraindications"),
    ]

    for label, key in fields:
        lines.append(f"- **{label}:** {display(patient.get(key))}")

    lines.extend(["", "## CYP2D6 pharmacogenomics"])

    for label, key in [
        ("Diplotype", "diplotype"),
        ("Laboratory phenotype", "lab_phenotype"),
        ("Activity score", "activity_score"),
        ("Interpretation", "pgx_label"),
        ("Interpretive note", "pgx_note"),
        ("Genotyping/report context", "genotype_method"),
    ]:
        lines.append(f"- **{label}:** {display(patient.get(key))}")

    lines.extend(["", "## Renal and hepatic context"])

    for label, key in [
        ("Creatinine (mg/dL)", "creatinine"),
        ("eGFR (mL/min/1.73 m²)", "egfr"),
        ("CrCl (mL/min)", "crcl"),
        ("ALT (U/L)", "alt"),
        ("AST (U/L)", "ast"),
        ("Bilirubin (mg/dL)", "bilirubin"),
    ]:
        lines.append(f"- **{label}:** {display(patient.get(key))}")

    lines.extend(["", "## Medication review"])

    if meds:
        for med in meds:
            lines.append(f"- {med['name']}: {med.get('notes', '')}")
    else:
        lines.append("- No concomitant medicines entered.")

    signals = screen_interactions([m["name"] for m in meds])

    if signals:
        lines.append("")
        lines.append("Potential interaction keyword signals:")
        for signal in signals:
            lines.append(
                f"- {signal['Medicine keyword']}: {signal['Signal']}. "
                f"{signal['Suggested action']}"
            )
    else:
        lines.append(
            "- No listed keyword matched. This does not prove that "
            "the medicine list is interaction-free."
        )

    lines.extend(["", "## Serial laboratory data"])

    if labs:
        for lab in labs:
            lines.append(
                f"- {lab['date']} | {lab['analyte']}: "
                f"{lab['value']} {lab['unit']} | "
                f"Flag: {lab.get('flag', 'Not assessed')}"
            )
    else:
        lines.append("- No serial laboratory results entered.")

    lines.extend(["", "## Adverse-event log"])

    if adverse_events:
        for event in adverse_events:
            lines.append(
                f"- {event['event']} | Onset: {event['onset']} | "
                f"Severity: {event['severity']} | "
                f"Seriousness: {event['seriousness']} | "
                f"Action/outcome: {event['action']} | "
                f"Notes: {event['notes']}"
            )
    else:
        lines.append("- No adverse-event entries.")

    lines.extend([
        "",
        "## Therapy discussion",
        "Options are discussion prompts, not a prescription.",
    ])

    for option in therapy_options(patient):
        lines.append(
            f"- **{option['Option']}** — {option['Clinical position']}. "
            f"{option['Rationale']}"
        )

    lines.extend([
        "",
        "## Interpretation and limitations",
        "- No validated personalized toxicity probability was calculated.",
        "- No treatment recommendation has been clinically validated by this prototype.",
        "- CYP2D6 interpretation must be confirmed using the validated laboratory report.",
        "- Medication screening uses keyword matching and may miss interactions.",
        "- Renal measures are contextual; do not infer tamoxifen dose adjustment from eGFR/CrCl alone.",
        "- Therapy choice depends on disease biology, treatment intent, menopausal status, prior therapy, contraindications and patient preferences.",
        "- All outputs require qualified oncology review.",
        "",
        "## References",
    ])

    for ref in REFERENCES:
        lines.append(
            f"- [{ref['id']}] {ref['title']}. {ref['detail']} "
            f"{ref['url']} — {ref['use']}"
        )

    lines.extend([
        "",
        "---",
        f"Prepared with {APP_NAME}. {DISCLAIMER}",
    ])

    return "\n".join(lines)


# -------------------- Header and navigation --------------------

st.markdown(
    f"""
    <div class="hero">
      <div style="font-size:.75rem;letter-spacing:.15em;color:#a5f3fc">
        PRECISION ONCOLOGY • PHARMACOGENOMICS • SAFETY
      </div>
      <h1>🧬 {APP_NAME}</h1>
      <p>Tamoxifen Pharmacogenomics & Clinical Decision Support</p>
      <p><b>{AUTHOR}</b> | Educational research prototype</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="warning-box">⚠️ {DISCLAIMER}</div>',
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "Clinical Overview",
    "Patient Profile",
    "CYP2D6 & Interactions",
    "Renal / Labs / Graphs",
    "Toxicity & Safety",
    "Therapy Review",
    "Clinical Report",
    "Evidence Library",
])


# ============================================================
# 1. CLINICAL OVERVIEW
# ============================================================

with tabs[0]:
    patient = st.session_state["patient"]

    st.subheader("Clinical snapshot")

    a, b, c, d = st.columns(4)

    a.metric("Patient code", patient.get("patient_code", "DEMO-001"))
    b.metric("Menopausal status", patient.get("menopause", "Not entered"))
    c.metric("CYP2D6", patient.get("pgx_label", "Not entered"))
    d.metric("Lab data points", len(st.session_state["labs"]))

    st.markdown("### Workflow")

    st.markdown(
        """
        <div class="panel">
        <b>01</b> Patient profile & disease context
        &nbsp; → &nbsp; <b>02</b> CYP2D6 & interactions
        &nbsp; → &nbsp; <b>03</b> Renal/lab monitoring
        &nbsp; → &nbsp; <b>04</b> Safety review
        &nbsp; → &nbsp; <b>05</b> Therapy discussion & report
        </div>
        """,
        unsafe_allow_html=True,
    )

    checklist = {
        "Patient context recorded": bool(patient.get("diagnosis")),
        "Menopausal status recorded": bool(
            patient.get("menopause")
            and patient.get("menopause") != "Unknown / not documented"
        ),
        "CYP2D6 result recorded": bool(
            patient.get("diplotype") or patient.get("activity_score") is not None
        ),
        "Medication list reviewed": bool(st.session_state["medications"]),
        "Renal/liver context entered": any(
            patient.get(k) is not None
            for k in ["egfr", "crcl", "alt", "ast", "bilirubin"]
        ),
    }

    st.markdown("### Completeness checklist")

    for label, completed in checklist.items():
        st.write(("✅" if completed else "⬜") + " " + label)

    st.warning(
        "This application organizes clinical information. It does not "
        "produce validated toxicity predictions or independently choose "
        "an endocrine regimen."
    )


# ============================================================
# 2. PATIENT PROFILE
# ============================================================

with tabs[1]:
    st.subheader("Patient profile and oncology context")
    st.caption("Use a fictional or coded profile for demonstration.")

    p = st.session_state["patient"]

    with st.form("profile_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            patient_code = st.text_input(
                "Patient / study code",
                value=p.get("patient_code", "DEMO-001"),
            )
            age = st.number_input(
                "Age (years)", 18, 110,
                int(p.get("age") or 55),
            )
            menopause = st.selectbox(
                "Menopausal / ovarian status",
                [
                    "Premenopausal",
                    "Perimenopausal / uncertain",
                    "Postmenopausal",
                    "Unknown / not documented",
                ],
                index=[
                    "Premenopausal",
                    "Perimenopausal / uncertain",
                    "Postmenopausal",
                    "Unknown / not documented",
                ].index(p.get("menopause", "Unknown / not documented")),
            )

        with col2:
            diagnosis = st.selectbox(
                "Diagnosis",
                [
                    "Hormone receptor-positive breast cancer",
                    "Other / not specified",
                ],
                index=[
                    "Hormone receptor-positive breast cancer",
                    "Other / not specified",
                ].index(p.get("diagnosis", "Hormone receptor-positive breast cancer")),
            )

            stage = st.selectbox(
                "Disease context",
                [
                    "Early / adjuvant",
                    "Neoadjuvant",
                    "Metastatic / advanced",
                    "Prevention / risk reduction",
                    "Not documented",
                ],
                index=[
                    "Early / adjuvant",
                    "Neoadjuvant",
                    "Metastatic / advanced",
                    "Prevention / risk reduction",
                    "Not documented",
                ].index(p.get("stage", "Early / adjuvant")),
            )

            er = st.selectbox(
                "ER status",
                ["Positive", "Negative", "Unknown"],
                index=["Positive", "Negative", "Unknown"].index(
                    p.get("er", "Unknown")
                ),
            )

            pr = st.selectbox(
                "PR status",
                ["Positive", "Negative", "Unknown"],
                index=["Positive", "Negative", "Unknown"].index(
                    p.get("pr", "Unknown")
                ),
            )

        with col3:
            her2 = st.selectbox(
                "HER2 status",
                ["Positive", "Negative", "Unknown"],
                index=["Positive", "Negative", "Unknown"].index(
                    p.get("her2", "Unknown")
                ),
            )

            current_therapy = st.selectbox(
                "Current endocrine therapy",
                [
                    "Tamoxifen",
                    "Aromatase inhibitor",
                    "AI + ovarian suppression",
                    "Other",
                    "Not started / unknown",
                ],
                index=[
                    "Tamoxifen",
                    "Aromatase inhibitor",
                    "AI + ovarian suppression",
                    "Other",
                    "Not started / unknown",
                ].index(p.get("current_therapy", "Not started / unknown")),
            )

            prior_ai = st.selectbox(
                "Prior AI experience",
                [
                    "No prior AI",
                    "AI tolerated",
                    "AI intolerance / contraindication",
                    "Unknown",
                ],
                index=[
                    "No prior AI",
                    "AI tolerated",
                    "AI intolerance / contraindication",
                    "Unknown",
                ].index(p.get("prior_ai", "Unknown")),
            )

            bmi = st.number_input(
                "BMI (kg/m²)",
                min_value=10.0,
                max_value=90.0,
                value=float(p.get("bmi") or 25.0),
                step=0.1,
            )

        comorbidities = st.text_area(
            "Comorbidities / relevant history",
            value=p.get("comorbidities", ""),
            placeholder="e.g., hypertension, diabetes, osteoporosis",
        )

        safety_choices = [
            "Prior venous thromboembolism (VTE)",
            "Known thrombophilia",
            "History of stroke",
            "Abnormal uterine bleeding / endometrial concern",
            "Severe liver disease",
            "Pregnancy / pregnancy possibility",
            "Other clinically important concern",
        ]

        contraindications = st.multiselect(
            "Safety history requiring clinician review",
            safety_choices,
            default=[
                x for x in p.get("contraindications", [])
                if x in safety_choices
            ],
        )

        save_profile = st.form_submit_button(
            "Save patient profile",
            type="primary",
            use_container_width=True,
        )

    if save_profile:
        p.update({
            "patient_code": patient_code.strip() or "DEMO-001",
            "age": age,
            "menopause": menopause,
            "diagnosis": diagnosis,
            "stage": stage,
            "er": er,
            "pr": pr,
            "her2": her2,
            "current_therapy": current_therapy,
            "prior_ai": prior_ai,
            "bmi": bmi,
            "comorbidities": comorbidities.strip(),
            "contraindications": contraindications,
        })

        st.session_state["patient"] = p
        st.success("Patient profile saved in this session.")

    with st.expander("View saved profile"):
        st.json(st.session_state["patient"])


# ============================================================
# 3. CYP2D6 & INTERACTIONS
# ============================================================

with tabs[2]:
    st.subheader("CYP2D6 pharmacogenomics")

    st.info(
        "Enter the validated laboratory report. This tool does not "
        "analyse raw DNA, call variants or infer CYP2D6 copy number."
    )

    p = st.session_state["patient"]

    with st.form("pgx_form"):
        col1, col2 = st.columns(2)

        with col1:
            diplotype = st.text_input(
                "Laboratory-reported diplotype",
                value=p.get("diplotype", ""),
                placeholder="Enter the report's star-allele result",
            )

            lab_phenotype = st.selectbox(
                "Laboratory-reported phenotype",
                [
                    "Not entered",
                    "Poor metabolizer",
                    "Intermediate metabolizer",
                    "Normal metabolizer",
                    "Ultrarapid metabolizer",
                    "Indeterminate / other",
                ],
                index=[
                    "Not entered",
                    "Poor metabolizer",
                    "Intermediate metabolizer",
                    "Normal metabolizer",
                    "Ultrarapid metabolizer",
                    "Indeterminate / other",
                ].index(p.get("lab_phenotype", "Not entered")),
            )

            score_available = st.checkbox(
                "Activity score available",
                value=p.get("activity_score") is not None,
            )

            score = st.number_input(
                "Activity score",
                min_value=0.0,
                max_value=5.0,
                value=float(
                    p.get("activity_score")
                    if p.get("activity_score") is not None
                    else 1.5
                ),
                step=0.25,
                disabled=not score_available,
            )

        with col2:
            allele_context = st.selectbox(
                "For activity score 1.0: *10 context",
                [
                    "Unknown / not reviewed",
                    "*10 present",
                    "*10 absent",
                    "Not applicable",
                ],
                index=[
                    "Unknown / not reviewed",
                    "*10 present",
                    "*10 absent",
                    "Not applicable",
                ].index(p.get("allele_context", "Unknown / not reviewed")),
            )

            genotype_method = st.selectbox(
                "Testing context",
                [
                    "Clinical laboratory report",
                    "Research assay",
                    "Not known",
                ],
                index=[
                    "Clinical laboratory report",
                    "Research assay",
                    "Not known",
                ].index(p.get("genotype_method", "Not known")),
            )

            cyp_notes = st.text_area(
                "Laboratory notes / copy-number information",
                value=p.get("cyp_notes", ""),
            )

        save_pgx = st.form_submit_button(
            "Interpret and save PGx",
            type="primary",
            use_container_width=True,
        )

    if save_pgx:
        score_value = float(score) if score_available else None
        label, note = get_pgx_interpretation(
            score_value, allele_context
        )

        p.update({
            "diplotype": diplotype.strip(),
            "lab_phenotype": lab_phenotype,
            "activity_score": score_value,
            "allele_context": allele_context,
            "genotype_method": genotype_method,
            "cyp_notes": cyp_notes.strip(),
            "pgx_label": label,
            "pgx_note": note,
        })

        st.session_state["patient"] = p
        st.success("PGx details saved.")

    if p.get("pgx_label"):
        st.markdown("### Current interpretation")
        st.subheader(p["pgx_label"])
        st.write(p.get("pgx_note", ""))

        if p.get("lab_phenotype") not in (None, "", "Not entered"):
            st.write(
                "**Laboratory phenotype:**",
                p["lab_phenotype"],
            )

        st.warning(
            "If the laboratory phenotype conflicts with the score-based "
            "interpretation, verify the report and allele translation. "
            "Do not automatically resolve discrepancies."
        )

    add_reference("R1")
    add_reference("R6")

    st.markdown("---")
    st.subheader("Concomitant medication list")

    with st.form("medicine_form", clear_on_submit=True):
        medicine_name = st.text_input(
            "Generic medicine name",
            placeholder="e.g., paroxetine",
        )
        medicine_notes = st.text_input(
            "Dose / indication / notes (optional)"
        )
        add_medicine = st.form_submit_button("Add medicine")

    if add_medicine:
        if medicine_name.strip():
            st.session_state["medications"].append({
                "name": medicine_name.strip(),
                "notes": medicine_notes.strip(),
            })
            st.success("Medicine added.")
        else:
            st.error("Enter a medicine name.")

    meds = st.session_state["medications"]

    if meds:
        st.dataframe(
            pd.DataFrame(meds),
            use_container_width=True,
            hide_index=True,
        )

        if st.button("Clear medication list"):
            st.session_state["medications"] = []
            st.rerun()

    interaction_results = screen_interactions(
        [m["name"] for m in meds]
    )

    st.markdown("### Interaction screen")

    if interaction_results:
        st.warning(
            "Potential CYP2D6 interaction keywords were found. "
            "This is not a complete drug-interaction checker."
        )
        st.dataframe(
            pd.DataFrame(interaction_results),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(
            "No listed keyword matched. This does not prove the "
            "medication list is interaction-free."
        )

    st.caption(
        "Check all medicines using a current interaction resource "
        "and the relevant prescribing information."
    )


# ============================================================
# 4. RENAL FUNCTION, LABS & LIVE GRAPHS
# ============================================================

with tabs[3]:
    st.subheader("Renal function and laboratory monitoring")
    st.caption(
        "Graphs use actual values entered into this session. "
        "The app does not generate synthetic patient results."
    )

    p = st.session_state["patient"]

    with st.form("renal_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            creatinine = st.number_input(
                "Serum creatinine (mg/dL)",
                min_value=0.0,
                max_value=30.0,
                value=float(p.get("creatinine") or 0.0),
                step=0.1,
            )

            egfr = st.number_input(
                "eGFR (mL/min/1.73 m²)",
                min_value=0.0,
                max_value=250.0,
                value=float(p.get("egfr") or 0.0),
                step=1.0,
            )

            crcl = st.number_input(
                "Creatinine clearance (mL/min)",
                min_value=0.0,
                max_value=250.0,
                value=float(p.get("crcl") or 0.0),
                step=1.0,
                help="Enter a clinician-calculated or laboratory-reported value.",
            )

        with col2:
            alt = st.number_input(
                "ALT (U/L)", 0.0, 10000.0,
                float(p.get("alt") or 0.0), step=1.0,
            )

            ast = st.number_input(
                "AST (U/L)", 0.0, 10000.0,
                float(p.get("ast") or 0.0), step=1.0,
            )

            bilirubin = st.number_input(
                "Total bilirubin (mg/dL)", 0.0, 100.0,
                float(p.get("bilirubin") or 0.0), step=0.1,
            )

        with col3:
            lab_date = st.date_input(
                "Current lab date", value=date.today()
            )
            lab_comment = st.text_area("Lab notes / context")

        save_renal = st.form_submit_button(
            "Save renal and liver context",
            type="primary",
            use_container_width=True,
        )

    if save_renal:
        p.update({
            "creatinine": creatinine if creatinine > 0 else None,
            "egfr": egfr if egfr > 0 else None,
            "crcl": crcl if crcl > 0 else None,
            "alt": alt if alt > 0 else None,
            "ast": ast if ast > 0 else None,
            "bilirubin": bilirubin if bilirubin > 0 else None,
            "latest_lab_date": str(lab_date),
            "lab_comment": lab_comment.strip(),
        })
        st.session_state["patient"] = p
        st.success("Renal and liver context saved.")

    renal_text = renal_interpretation(
        safe_float(p.get("egfr")),
        safe_float(p.get("crcl")),
    )

    st.markdown("### Renal context")

    if renal_text == "Not assessed":
        st.info("Renal function has not been entered.")
    else:
        st.write(renal_text)

    st.warning(
        "eGFR and CrCl are included for overall clinical context. "
        "Do not use these values alone to adjust tamoxifen dose. "
        "Review the relevant drug label and clinical context."
    )

    st.markdown("---")
    st.subheader("Add serial laboratory data")

    with st.form("serial_lab_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            sample_date = st.date_input(
                "Sample date", value=date.today()
            )

            analyte = st.selectbox(
                "Analyte",
                [
                    "Creatinine",
                    "eGFR",
                    "CrCl",
                    "ALT",
                    "AST",
                    "Total bilirubin",
                    "Platelets",
                    "Hemoglobin",
                    "Other",
                ],
            )

        with col2:
            value = st.number_input(
                "Result value",
                min_value=0.0,
                max_value=100000.0,
                value=0.0,
                step=0.1,
            )

            default_units = {
                "Creatinine": "mg/dL",
                "eGFR": "mL/min/1.73 m²",
                "CrCl": "mL/min",
                "ALT": "U/L",
                "AST": "U/L",
                "Total bilirubin": "mg/dL",
                "Platelets": "10^9/L",
                "Hemoglobin": "g/dL",
            }

            unit = st.text_input(
                "Units",
                value=default_units.get(analyte, ""),
            )

        with col3:
            low = st.number_input(
                "Reference lower bound (optional)",
                min_value=0.0,
                value=0.0,
                step=0.1,
            )

            high = st.number_input(
                "Reference upper bound (optional)",
                min_value=0.0,
                value=0.0,
                step=0.1,
            )

        notes = st.text_input("Notes (optional)")
        add_lab = st.form_submit_button("Add lab point")

    if add_lab:
        flag = "Not assessed"

        if high > 0 and value > high:
            flag = "Above entered reference interval"
        elif low > 0 and value < low:
            flag = "Below entered reference interval"

        st.session_state["labs"].append({
            "date": str(sample_date),
            "analyte": analyte,
            "value": float(value),
            "unit": unit,
            "reference_low": low if low > 0 else None,
            "reference_high": high if high > 0 else None,
            "flag": flag,
            "notes": notes.strip(),
        })

        st.success("Lab point added.")

    labs = st.session_state["labs"]

    if labs:
        df = pd.DataFrame(labs)

        st.markdown("### Recorded laboratory data")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

        chosen_analyte = st.selectbox(
            "Select analyte for live graph",
            sorted(df["analyte"].unique()),
        )

        graph_df = df[
            df["analyte"] == chosen_analyte
        ].copy()

        graph_df["date"] = pd.to_datetime(
            graph_df["date"], errors="coerce"
        )

        graph_df = graph_df.sort_values("date")

        fig = px.line(
            graph_df,
            x="date",
            y="value",
            markers=True,
            title=f"{chosen_analyte}: entered results over time",
            hover_data=["unit", "flag", "notes"],
        )

        fig.update_layout(
            template="plotly_white",
            height=380,
            xaxis_title="Sample date",
            yaxis_title="Entered value",
        )

        st.plotly_chart(fig, use_container_width=True)

        last = graph_df.iloc[-1]

        if (
            pd.notna(last.get("reference_low"))
            and pd.notna(last.get("reference_high"))
        ):
            fig2 = go.Figure()

            fig2.add_trace(
                go.Scatter(
                    x=graph_df["date"],
                    y=graph_df["value"],
                    mode="lines+markers",
                    name=chosen_analyte,
                )
            )

            fig2.add_hrect(
                y0=float(last["reference_low"]),
                y1=float(last["reference_high"]),
                opacity=0.16,
                line_width=0,
                annotation_text="Entered reference interval",
            )

            fig2.update_layout(
                template="plotly_white",
                height=320,
                title="Trend with user-entered reference interval",
            )

            st.plotly_chart(fig2, use_container_width=True)

        st.download_button(
            "Download laboratory data CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="OncoPGx_laboratory_data.csv",
            mime="text/csv",
        )

        if st.button("Clear serial laboratory data"):
            st.session_state["labs"] = []
            st.rerun()

    else:
        st.info(
            "Add serial lab results to create live graphs. "
            "No fake patient values are supplied."
        )

    st.caption(
        "Reference ranges vary between laboratories. Flags use only "
        "the boundaries entered by the user and are not clinical diagnoses."
    )


# ============================================================
# 5. TOXICITY & SAFETY
# ============================================================

with tabs[4]:
    st.subheader("Toxicity and safety monitoring")

    st.warning(
        "No validated toxicity-prediction model is implemented. "
        "This module organizes safety review and does not calculate "
        "personalized toxicity probabilities."
    )

    safety_topics = {
        "Venous thromboembolism": (
            "Review previous DVT/PE, thrombophilia, immobility, recent "
            "surgery and relevant symptoms. Sudden breathlessness, chest "
            "pain or unilateral leg swelling may require urgent assessment."
        ),
        "Uterine / endometrial symptoms": (
            "Document abnormal uterine bleeding in patients for whom "
            "this is relevant and arrange appropriate clinical evaluation. "
            "Do not dismiss unexplained bleeding."
        ),
        "Liver context": (
            "Review relevant liver history and laboratory results when "
            "clinically indicated. Interpret results against local ranges "
            "and the overall clinical picture."
        ),
        "Ocular symptoms": (
            "Document new visual symptoms and arrange appropriate clinical "
            "assessment."
        ),
        "Drug interactions": (
            "Review the full medication list and CYP2D6 inhibitors with a "
            "qualified pharmacist or prescriber."
        ),
        "Adherence and tolerability": (
            "Ask about symptoms, missed doses, barriers and patient "
            "preferences. Do not infer adherence from a PGx result."
        ),
    }

    for title, detail in safety_topics.items():
        with st.expander(title):
            st.write(detail)

    p = st.session_state["patient"]
    flags = p.get("contraindications", [])

    if flags:
        st.markdown("### Patient-entered safety flags")
        for flag in flags:
            st.error(flag)
        st.caption(
            "These are review prompts, not definitive contraindication "
            "adjudications."
        )
    else:
        st.info(
            "No safety-history flags entered. Missing information "
            "does not establish absence of risk."
        )

    st.markdown("---")
    st.subheader("Adverse-event documentation")

    with st.form("ae_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            event = st.selectbox(
                "Event",
                [
                    "Hot flashes / vasomotor symptoms",
                    "Nausea / gastrointestinal symptoms",
                    "Abnormal uterine bleeding",
                    "Suspected thromboembolic event",
                    "Liver test abnormality",
                    "Visual symptom",
                    "Other",
                ],
            )
            onset = st.date_input("Onset date", value=date.today())

        with col2:
            severity = st.selectbox(
                "Severity",
                ["Not assessed", "Mild", "Moderate", "Severe"],
            )
            seriousness = st.selectbox(
                "Seriousness",
                [
                    "Not assessed",
                    "Non-serious",
                    "Potentially serious",
                    "Serious — urgent assessment required",
                ],
            )

        with col3:
            action = st.selectbox(
                "Action / outcome",
                [
                    "Not recorded",
                    "No change documented",
                    "Symptomatic treatment",
                    "Treatment changed by clinician",
                    "Urgent referral / emergency care",
                    "Resolved",
                    "Ongoing",
                ],
            )

        ae_notes = st.text_area(
            "Description, suspected medicine, action and outcome"
        )

        submit_ae = st.form_submit_button(
            "Save adverse-event entry",
            type="primary",
        )

    if submit_ae:
        st.session_state["adverse_events"].append({
            "event": event,
            "onset": str(onset),
            "severity": severity,
            "seriousness": seriousness,
            "action": action,
            "notes": ae_notes.strip(),
        })

        st.success("Adverse-event entry saved in this session.")

        if (
            event == "Suspected thromboembolic event"
            or seriousness.startswith("Serious")
        ):
            st.error(
                "Urgent clinical assessment may be required. Follow "
                "local emergency procedures. This app is not an emergency service."
            )

    if st.session_state["adverse_events"]:
        ae_df = pd.DataFrame(st.session_state["adverse_events"])

        st.dataframe(
            ae_df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download adverse-event log CSV",
            ae_df.to_csv(index=False).encode("utf-8"),
            file_name="OncoPGx_adverse_events.csv",
            mime="text/csv",
        )

    add_reference("R4")


# ============================================================
# 6. THERAPY / REGIMEN REVIEW
# ============================================================

with tabs[5]:
    st.subheader("Therapy and endocrine-regimen review")

    st.caption(
        "The output below is a transparent clinical discussion aid, "
        "not an autonomous treatment recommendation."
    )

    p = st.session_state["patient"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Disease context", p.get("stage", "Not entered"))
    col2.metric("Menopausal status", p.get("menopause", "Not entered"))
    col3.metric("Current therapy", p.get("current_therapy", "Not entered"))
    col4.metric("CYP2D6", p.get("pgx_label", "Not entered"))

    if p.get("er") == "Negative":
        st.error(
            "ER is recorded as negative. Verify the pathology and treatment "
            "indication before applying the usual hormone-receptor-positive "
            "endocrine therapy pathway."
        )

    if p.get("menopause") in (
        None,
        "",
        "Unknown / not documented",
    ):
        st.warning(
            "Menopausal/ovarian status is unknown. The app cannot responsibly "
            "compare AI-only therapy with strategies that require ovarian suppression."
        )

    options = therapy_options(p)

    st.markdown("### Options for clinician discussion")

    for option in options:
        with st.expander(
            f"{option['Option']} — {option['Clinical position']}",
            expanded=True,
        ):
            st.write(option["Rationale"])

    st.markdown("### Review before final regimen selection")

    review_items = [
        "Confirm pathology and ER/PR/HER2 status.",
        "Confirm disease stage and treatment intent.",
        "Review recurrence risk and previous endocrine treatment.",
        "Confirm menopausal/ovarian status.",
        "Review contraindications, VTE history and relevant symptoms.",
        "Review bone health when considering an aromatase inhibitor.",
        "Reconcile medicines and check interactions.",
        "Verify CYP2D6 result against the validated laboratory report.",
        "Discuss tolerability, adherence, patient preference and follow-up.",
    ]

    for i, item in enumerate(review_items):
        st.checkbox(item, key=f"review_check_{i}")

    st.markdown("### How to interpret the recommendation")

    st.info(
        "For a postmenopausal patient, an aromatase inhibitor may be an "
        "appropriate endocrine option to discuss. For a premenopausal patient, "
        "tamoxifen and, in selected cases, an aromatase inhibitor with ovarian "
        "suppression may be options. This does not establish which is best "
        "for a particular patient."
    )

    st.warning(
        "CPIC provides CYP2D6 genotype-informed guidance when results are "
        "available. This should not be confused with a recommendation that "
        "all oncology patients undergo routine CYP2D6 testing. Verify the "
        "current oncology guideline, institutional protocol and complete "
        "patient context."
    )

    add_reference("R1")
    add_reference("R2")
    add_reference("R3")
    add_reference("R5")


# ============================================================
# 7. PROFESSIONAL CLINICAL REPORT
# ============================================================

with tabs[6]:
    st.subheader("Evidence-linked clinical summary")

    st.caption(
        "The report uses information entered in this session. It is not "
        "a validated clinical recommendation or signed clinical record."
    )

    report_text = build_report()

    st.markdown(f"**{APP_NAME}**")
    st.markdown(f"**Prepared by:** {AUTHOR}")
    st.markdown(
        f"**Generated:** {datetime.now().astimezone().strftime('%d %b %Y, %H:%M %Z')}"
    )

    st.warning(DISCLAIMER)

    with st.expander("Preview full report", expanded=True):
        st.markdown(report_text)

    code = str(
        st.session_state["patient"].get("patient_code", "DEMO-001")
    )
    safe_code = "".join(
        c if c.isalnum() or c in "-_" else "_"
        for c in code
    )

    st.download_button(
        "Download clinical report (Markdown)",
        data=report_text.encode("utf-8"),
        file_name=f"OncoPGx_{safe_code}_report.md",
        mime="text/markdown",
        type="primary",
        use_container_width=True,
    )

    structured_data = {
        "author": AUTHOR,
        "generated_at": datetime.now().astimezone().isoformat(),
        "disclaimer": DISCLAIMER,
        "patient": st.session_state["patient"],
        "labs": st.session_state["labs"],
        "medications": st.session_state["medications"],
        "adverse_events": st.session_state["adverse_events"],
        "references": REFERENCES,
    }

    st.download_button(
        "Download structured report (JSON)",
        data=json.dumps(
            structured_data,
            indent=2,
            ensure_ascii=False,
            default=str,
        ).encode("utf-8"),
        file_name=f"OncoPGx_{safe_code}_report.json",
        mime="application/json",
        use_container_width=True,
    )

    st.caption(
        "For a presentation, open the report preview and use your browser's "
        "Print → Save as PDF option. Review the content before sharing."
    )


# ============================================================
# 8. EVIDENCE LIBRARY
# ============================================================

with tabs[7]:
    st.subheader("Evidence library")

    st.write(
        "These sources provide guideline and prescribing-information context. "
        "Check the latest version before any clinical application."
    )

    for ref in REFERENCES:
        with st.container():
            st.markdown(
                f"**[{ref['id']}] {ref['title']}**"
            )
            st.write(ref["detail"])
            st.write(ref["use"])
            st.markdown(f"[Open source]({ref['url']})")
            st.divider()

    st.markdown("### Evidence interpretation")

    st.markdown(
        """
        **CYP2D6 and endoxifen:** CYP2D6 contributes to formation of
        endoxifen, an active tamoxifen metabolite. A genotype result is
        not a direct measurement of endoxifen concentration or cancer outcome.

        **Genotype interpretation:** allele function, diplotype, copy number,
        assay coverage and the laboratory's validated translation can affect
        phenotype assignment.

        **Toxicity:** the prototype records safety factors and adverse events.
        It does not contain a validated model for predicting an individual's
        probability of toxicity.

        **Renal function:** eGFR and creatinine clearance document overall
        clinical context. They should not independently determine tamoxifen
        dose changes.

        **Therapy choice:** disease stage, receptor status, menopausal/ovarian
        status, prior therapy, contraindications, tolerability and patient
        preferences must be considered by the treating team.

        **Guidelines:** CPIC pharmacogenetic guidance and oncology guidelines
        may address different questions. Check the current versions and local
        institutional recommendations.
        """
    )

    refs_text = "\n\n".join(
        f"[{r['id']}] {r['title']}\n{r['detail']}\n"
        f"{r['url']}\n{r['use']}"
        for r in REFERENCES
    )

    st.download_button(
        "Download reference list",
        data=refs_text.encode("utf-8"),
        file_name="OncoPGx_references.txt",
        mime="text/plain",
    )


# -------------------- Footer --------------------

st.divider()

st.markdown(
    f"""
    <div style="text-align:center;color:#64748b;font-size:.83rem;padding:.5rem">
    <b>{APP_NAME}</b> · {AUTHOR}<br>
    Educational research prototype · Clinical validation pending<br>
    Not for autonomous clinical decisions
    </div>
    """,
    unsafe_allow_html=True,
)
