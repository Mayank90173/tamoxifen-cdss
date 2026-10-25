
from __future__ import annotations

import json
from datetime import datetime
from io import BytesIO

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# OncoPGx: Tamoxifen Clinical Decision Support Research Prototype
# Educational/research use only — not clinically validated.
# ============================================================

st.set_page_config(
    page_title="OncoPGx | Tamoxifen Research CDSS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_TITLE = "OncoPGx — Oncology Pharmacogenomics Research Prototype"
APP_AUTHOR = "Dr. Mayank Virmani, PharmD"

st.markdown(
    """
    <style>
    .stApp { background-color: #0b1020; color: #edf2ff; }
    [data-testid="stSidebar"] { background-color: #111a30; }
    [data-testid="stMetric"] {
        background: #141f38;
        border: 1px solid #263757;
        padding: 14px;
        border-radius: 12px;
    }
    .hero {
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #2d4267;
        background: linear-gradient(120deg, #142746, #17203a);
        margin-bottom: 16px;
    }
    .muted { color: #aebdd8; font-size: 0.9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="hero">
        <h1>🧬 {APP_TITLE}</h1>
        <p>Pharmacogenomics • Medication Safety • Renal Function • Research Analytics</p>
        <p class="muted">{APP_AUTHOR}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.warning(
    "RESEARCH / EDUCATIONAL USE ONLY. This prototype is not clinically "
    "validated and must not be used to select treatment, adjust doses, or "
    "make patient-care decisions. Confirm all medication and guideline "
    "information with qualified clinicians and authoritative references."
)


# ----------------------------- Constants -----------------------------

DRUGS = [
    "Tamoxifen",
    "Anastrozole",
    "Letrozole",
    "Exemestane",
    "Fulvestrant",
    "Other",
]

CONMED_OPTIONS = [
    "None selected",
    "Paroxetine",
    "Fluoxetine",
    "Bupropion",
    "Quinidine",
    "Duloxetine",
    "Escitalopram",
    "Citalopram",
    "Sertraline",
    "Venlafaxine",
    "Amitriptyline",
    "Clopidogrel",
    "Warfarin",
    "Apixaban",
    "Rivaroxaban",
    "Omeprazole",
    "Pantoprazole",
    "Metoprolol",
    "Carbamazepine",
    "Phenytoin",
    "Rifampin",
    "Other",
]

CYP2D6_PHENOTYPES = [
    "Unknown / not tested",
    "Poor metabolizer",
    "Intermediate metabolizer",
    "Normal metabolizer",
    "Ultrarapid metabolizer",
]

CYP2D6_GENOTYPES = [
    "Unknown / not tested",
    "*1/*1",
    "*1/*4",
    "*4/*4",
    "*1/*10",
    "*10/*10",
    "*1/*5",
    "*5/*4",
    "Other / complex genotype",
]

GENOTYPE_SOURCES = [
    "Not available",
    "Clinical laboratory report",
    "Research laboratory",
    "Published dataset",
    "Manually entered / unverified",
]

# This is a deliberately limited educational screening list, not a
# complete interaction database. Verify medicines and evidence clinically.
CYP2D6_INHIBITOR_SCREEN = {
    "Paroxetine": "Strong CYP2D6 inhibitor; may reduce tamoxifen activation.",
    "Fluoxetine": "Strong CYP2D6 inhibitor; may reduce tamoxifen activation.",
    "Bupropion": "Strong CYP2D6 inhibitor; may reduce tamoxifen activation.",
    "Quinidine": "Strong CYP2D6 inhibitor; may reduce tamoxifen activation.",
    "Duloxetine": "CYP2D6 inhibition may be clinically relevant.",
    "Escitalopram": "Generally less CYP2D6 inhibition than strong inhibitors; verify context.",
    "Citalopram": "Generally less CYP2D6 inhibition than strong inhibitors; verify context.",
    "Sertraline": "CYP2D6 inhibition varies with dose and context.",
    "Venlafaxine": "Generally has less CYP2D6 inhibition than strong inhibitors.",
    "Amitriptyline": "CYP2D6 substrate; interaction and clinical context need review.",
}

GENERAL_SAFETY_NOTES = {
    "Paroxetine",
    "Fluoxetine",
    "Bupropion",
    "Quinidine",
}


# ----------------------------- Functions -----------------------------

def safe_float(value, default=0.0):
    """Convert a value to float without crashing on blank input."""
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def cockcroft_gault_crcl(age, weight_kg, serum_creatinine, sex):
    """
    Estimate creatinine clearance (mL/min) with Cockcroft–Gault.

    This implementation uses the conventional sex coefficient.
    It is an estimate, not a diagnosis or dosing instruction.
    """
    if age <= 0 or weight_kg <= 0 or serum_creatinine <= 0:
        return None

    result = ((140 - age) * weight_kg) / (72 * serum_creatinine)

    if sex == "Female":
        result *= 0.85

    return max(result, 0.0)


def ckd_epi_2021_egfr(age, serum_creatinine, sex):
    """
    Estimate eGFR using the 2021 CKD-EPI creatinine equation,
    without a race coefficient.

    Returns mL/min/1.73 m².
    """
    if age <= 0 or serum_creatinine <= 0:
        return None

    female = sex == "Female"
    kappa = 0.7 if female else 0.9
    alpha = -0.241 if female else -0.302
    sex_coefficient = 1.012 if female else 1.0

    scr_over_k = serum_creatinine / kappa

    result = (
        142
        * min(scr_over_k, 1) ** alpha
        * max(scr_over_k, 1) ** (-1.200)
        * (0.9938**age)
        * sex_coefficient
    )

    return max(result, 0.0)


def format_number(value, digits=1):
    if value is None:
        return "Not calculated"
    return f"{value:.{digits}f}"


def build_conmed_screen(selected_medicines, primary_drug):
    rows = []

    if primary_drug != "Tamoxifen":
        return pd.DataFrame(
            columns=["Medicine", "Screening observation", "Status"]
        )

    for medicine in selected_medicines:
        if medicine == "None selected":
            continue

        if medicine in CYP2D6_INHIBITOR_SCREEN:
            observation = CYP2D6_INHIBITOR_SCREEN[medicine]
            status = (
                "Review CYP2D6 interaction"
                if medicine in GENERAL_SAFETY_NOTES
                else "Review medication context"
            )
        elif medicine == "Rifampin":
            observation = (
                "Potential enzyme induction and interaction concerns; "
                "verify with an authoritative interaction resource."
            )
            status = "Clinical verification required"
        elif medicine == "Other":
            observation = (
                "Medicine name not specified; no interaction assessment possible."
            )
            status = "Insufficient information"
        else:
            observation = (
                "No automated interpretation supplied by this limited prototype. "
                "This does not mean the medicine has no interaction."
            )
            status = "Manual review required"

        rows.append(
            {
                "Medicine": medicine,
                "Screening observation": observation,
                "Status": status,
            }
        )

    return pd.DataFrame(
        rows,
        columns=["Medicine", "Screening observation", "Status"],
    )


def build_report(data):
    """Build a plain-text research summary for download."""
    lines = [
        APP_TITLE,
        f"App label: {APP_AUTHOR}",
        f"Generated: {datetime.now().astimezone().isoformat(timespec='seconds')}",
        "",
        "IMPORTANT DISCLAIMER",
        "Research/educational prototype only. Not clinically validated.",
        "Not for treatment selection, dosing, diagnosis, or patient-care decisions.",
        "",
        "PATIENT / CASE INFORMATION",
    ]

    for key, value in data["case"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "PHARMACOGENOMICS"])

    for key, value in data["pgx"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "RENAL FUNCTION ESTIMATES"])

    for key, value in data["renal"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "SAFETY / LAB DATA"])

    for key, value in data["safety"].items():
        lines.append(f"{key}: {value}")

    lines.extend(["", "CONCOMITANT MEDICATIONS"])

    if data["conmeds"]:
        for row in data["conmeds"]:
            lines.append(
                f"- {row['Medicine']}: {row['Screening observation']} "
                f"[{row['Status']}]"
            )
    else:
        lines.append("No concomitant medicines entered.")

    lines.extend(
        [
            "",
            "INTERPRETATION LIMITATIONS",
            "- CYP2D6 phenotype and genotype are entered independently.",
            "- The app does not infer phenotype from genotype.",
            "- No personalized toxicity probability is calculated.",
            "- No endoxifen concentration is predicted.",
            "- No individualized treatment or dose recommendation is generated.",
            "- Medication screening is limited and not exhaustive.",
            "- CrCl and eGFR are different estimates and are not interchangeable.",
            "- Laboratory values require clinical context and reference ranges.",
            "",
            "REFERENCES FOR VERIFICATION",
            "CPIC tamoxifen guideline: "
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC5931215/",
            "CPIC guidelines: https://cpicpgx.org/guidelines/",
            "NCCN guidelines: https://www.nccn.org/guidelines/category_1",
            "NIDDK eGFR resources: https://www.niddk.nih.gov/health-information/"
            "professional-topics/kidney-disease/laboratory-evaluation/glomerular-filtration-rate",
        ]
    )

    return "\n".join(lines)


def metric_or_na(label, value, suffix=""):
    if value is None:
        st.metric(label, "N/A")
    else:
        st.metric(label, f"{value:.1f}{suffix}")


# ----------------------------- Sidebar -----------------------------

st.sidebar.title("⚙️ Research workspace")
st.sidebar.caption("Prototype configuration")

primary_drug = st.sidebar.selectbox(
    "Primary oncology medicine",
    DRUGS,
    index=0,
)

case_id = st.sidebar.text_input(
    "Research case ID",
    value="CASE-001",
    help="Use a pseudonymous research ID. Avoid names or identifying details.",
)

data_mode = st.sidebar.radio(
    "Data type",
    ["Synthetic / demonstration", "De-identified research data"],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Navigation")
st.sidebar.caption(
    "Use the tabs across the main workspace to enter data, "
    "review screening output, inspect graphs, and export a report."
)

st.sidebar.markdown("---")
st.sidebar.caption("Clinical use is not supported by this prototype.")


# ----------------------------- Tabs -----------------------------

tabs = st.tabs(
    [
        "📋 Patient & Renal",
        "🧬 PGx",
        "💊 Medication Review",
        "🧪 Safety & Labs",
        "📈 Live Graphs",
        "📄 Clinical Report",
        "📚 Evidence",
    ]
)


# ----------------------------- Patient & Renal -----------------------------

with tabs[0]:
    st.subheader("Patient / research case characteristics")
    st.caption(
        "Enter synthetic or appropriately de-identified data. "
        "Do not enter names, addresses, hospital numbers, or other identifiers."
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        age = st.number_input(
            "Age (years)",
            min_value=18,
            max_value=120,
            value=55,
            step=1,
        )

    with c2:
        sex = st.selectbox(
            "Sex used for equation",
            ["Female", "Male"],
            index=0,
            help=(
                "These equations use sex-specific coefficients. "
                "For clinical interpretation, follow the appropriate "
                "validated local workflow."
            ),
        )

    with c3:
        weight_kg = st.number_input(
            "Weight (kg)",
            min_value=1.0,
            max_value=350.0,
            value=65.0,
            step=0.5,
        )

    c4, c5, c6 = st.columns(3)

    with c4:
        serum_creatinine = st.number_input(
            "Serum creatinine (mg/dL)",
            min_value=0.1,
            max_value=30.0,
            value=0.9,
            step=0.1,
            format="%.2f",
        )

    with c5:
        height_cm = st.number_input(
            "Height (cm)",
            min_value=50.0,
            max_value=250.0,
            value=160.0,
            step=0.5,
        )

    with c6:
        menopausal_status = st.selectbox(
            "Menopausal status",
            [
                "Not entered",
                "Premenopausal",
                "Perimenopausal",
                "Postmenopausal",
                "Unknown",
            ],
        )

    c7, c8, c9 = st.columns(3)

    with c7:
        cancer_stage = st.selectbox(
            "Cancer stage",
            ["Not entered", "Stage I", "Stage II", "Stage III", "Stage IV", "Unknown"],
        )

    with c8:
        receptor_status = st.selectbox(
            "Hormone receptor status",
            [
                "Not entered",
                "ER-positive",
                "ER-negative",
                "PR-positive",
                "PR-negative",
                "Mixed / other",
                "Unknown",
            ],
        )

    with c9:
        treatment_setting = st.selectbox(
            "Treatment setting",
            [
                "Not entered",
                "Adjuvant",
                "Neoadjuvant",
                "Metastatic",
                "Other / unknown",
            ],
        )

    st.markdown("### Automatically calculated estimates")

    crcl = cockcroft_gault_crcl(
        age=age,
        weight_kg=weight_kg,
        serum_creatinine=serum_creatinine,
        sex=sex,
    )

    egfr = ckd_epi_2021_egfr(
        age=age,
        serum_creatinine=serum_creatinine,
        sex=sex,
    )

    r1, r2, r3 = st.columns(3)

    with r1:
        metric_or_na("Cockcroft–Gault CrCl", crcl, " mL/min")

    with r2:
        metric_or_na("2021 CKD-EPI eGFR", egfr, " mL/min/1.73 m²")

    with r3:
        bmi = weight_kg / ((height_cm / 100) ** 2) if height_cm > 0 else None
        metric_or_na("BMI", bmi, " kg/m²")

    st.info(
        "CrCl and eGFR are different estimates. They are not interchangeable. "
        "The appropriate estimate depends on the clinical context and the "
        "specific medicine or guideline. These calculations are not treatment "
        "recommendations."
    )


# ----------------------------- PGx -----------------------------

with tabs[1]:
    st.subheader("CYP2D6 pharmacogenomics")
    st.write(
        "Tamoxifen is metabolized through pathways including CYP2D6-mediated "
        "formation of active metabolites. CYP2D6 results may be relevant to "
        "tamoxifen pharmacogenomic research."
    )

    p1, p2 = st.columns(2)

    with p1:
        cyp2d6_phenotype = st.selectbox(
            "Reported CYP2D6 phenotype",
            CYP2D6_PHENOTYPES,
            index=0,
        )

    with p2:
        cyp2d6_genotype = st.selectbox(
            "Reported CYP2D6 genotype / diplotype",
            CYP2D6_GENOTYPES,
            index=0,
        )

    p3, p4 = st.columns(2)

    with p3:
        genotype_source = st.selectbox(
            "Source of PGx result",
            GENOTYPE_SOURCES,
            index=0,
        )

    with p4:
        activity_score = st.selectbox(
            "Reported activity score",
            [
                "Not available",
                "0",
                "0.25",
                "0.5",
                "0.75",
                "1.0",
                "1.25",
                "1.5",
                "2.0",
                "Other / not entered",
            ],
        )

    cyp2d6_notes = st.text_area(
        "PGx notes",
        placeholder=(
            "Optional: assay details, allele calls, copy-number findings, "
            "or notes from a published dataset."
        ),
        height=100,
    )

    st.markdown("### Research interpretation boundaries")

    if primary_drug == "Tamoxifen":
        st.info(
            "The reported phenotype, genotype, and activity score are shown "
            "as entered. The app does not independently verify the assay, "
            "infer a phenotype from a diplotype, predict endoxifen levels, "
            "or recommend changing treatment."
        )
    else:
        st.info(
            "CYP2D6 information can be recorded for research, but this "
            "prototype does not provide drug-specific PGx guidance for "
            "the selected non-tamoxifen medicine."
        )

    st.markdown("#### Research questions to investigate")
    st.markdown(
        """
        - How are CYP2D6 phenotype and genotype reported in the source study?
        - Was allele calling and copy-number variation assessed?
        - How was adherence to tamoxifen evaluated?
        - Were concomitant CYP2D6 inhibitors documented?
        - What outcome was studied: recurrence, survival, endoxifen exposure,
          adverse events, or another endpoint?
        - Was the result replicated in an independent cohort?
        """
    )


# ----------------------------- Medication Review -----------------------------

with tabs[2]:
    st.subheader("Concomitant medication screening")

    selected_conmeds = st.multiselect(
        "Select concomitant medicines",
        options=CONMED_OPTIONS,
        default=["None selected"],
        help=(
            "This is a limited educational screening list. "
            "It is not a complete interaction database."
        ),
    )

    if "None selected" in selected_conmeds and len(selected_conmeds) > 1:
        selected_conmeds = [
            medicine for medicine in selected_conmeds
            if medicine != "None selected"
        ]

    conmed_df = build_conmed_screen(
        selected_medicines=selected_conmeds,
        primary_drug=primary_drug,
    )

    if primary_drug == "Tamoxifen":
        st.markdown("#### CYP2D6 and tamoxifen")
        st.write(
            "Strong CYP2D6 inhibitors may reduce conversion of tamoxifen "
            "to active metabolites. The clinical relevance depends on the "
            "medicine, dose, patient context, and current evidence."
        )
    else:
        st.info(
            "The CYP2D6 interaction screen in this prototype is specific "
            "to tamoxifen. It is not applied to the selected medicine."
        )

    if conmed_df.empty:
        st.info("No medicines requiring a displayed screening row were entered.")
    else:
        st.dataframe(
            conmed_df,
            use_container_width=True,
            hide_index=True,
        )

    st.warning(
        "An absent alert does not establish that a combination is safe. "
        "This prototype does not check every drug, dose, supplement, "
        "interaction pathway, or updated prescribing recommendation."
    )

    st.markdown("### Medication reconciliation notes")
    medication_notes = st.text_area(
        "Additional medication notes",
        placeholder=(
            "Optional: dose, route, duration, supplements, adherence, "
            "or details requiring verification."
        ),
        height=100,
    )


# ----------------------------- Safety & Labs -----------------------------

with tabs[3]:
    st.subheader("Safety and laboratory data")
    st.caption(
        "These fields record observations. They do not diagnose toxicity "
        "or generate a validated risk score."
    )

    s1, s2, s3 = st.columns(3)

    with s1:
        ast = st.number_input(
            "AST (U/L)",
            min_value=0.0,
            max_value=10000.0,
            value=25.0,
            step=1.0,
        )

    with s2:
        alt = st.number_input(
            "ALT (U/L)",
            min_value=0.0,
            max_value=10000.0,
            value=25.0,
            step=1.0,
        )

    with s3:
        bilirubin = st.number_input(
            "Total bilirubin (mg/dL)",
            min_value=0.0,
            max_value=100.0,
            value=0.8,
            step=0.1,
        )

    s4, s5, s6 = st.columns(3)

    with s4:
        platelets = st.number_input(
            "Platelets (×10⁹/L)",
            min_value=0.0,
            max_value=3000.0,
            value=250.0,
            step=5.0,
        )

    with s5:
        hemoglobin = st.number_input(
            "Hemoglobin (g/dL)",
            min_value=0.0,
            max_value=30.0,
            value=12.5,
            step=0.1,
        )

    with s6:
        blood_pressure_systolic = st.number_input(
            "Systolic BP (mmHg)",
            min_value=0,
            max_value=300,
            value=120,
            step=1,
        )

    st.markdown("### Relevant history / observations")

    h1, h2 = st.columns(2)

    with h1:
        dvt_history = st.selectbox(
            "History of DVT / pulmonary embolism",
            ["Not entered", "No", "Yes", "Unknown"],
        )

        liver_history = st.selectbox(
            "History of liver disease",
            ["Not entered", "No", "Yes", "Unknown"],
        )

    with h2:
        uterine_history = st.selectbox(
            "Relevant uterine / endometrial history",
            ["Not entered", "No", "Yes", "Unknown", "Not applicable"],
        )

        adverse_event_history = st.selectbox(
            "Prior treatment-related adverse event",
            ["Not entered", "No", "Yes", "Unknown"],
        )

    adverse_event_notes = st.text_area(
        "Adverse event / toxicity notes",
        placeholder=(
            "Optional: event description, date, severity as reported, "
            "management, and source. Do not enter identifying information."
        ),
        height=100,
    )

    st.info(
        "Tamoxifen has clinically important risks and precautions, including "
        "venous thromboembolic and endometrial risks in relevant settings. "
        "This app does not assess an individual's absolute risk. Interpret "
        "laboratory results using validated local reference ranges and "
        "appropriate clinical evaluation."
    )


# ----------------------------- Live Graphs -----------------------------

with tabs[4]:
    st.subheader("Live research visualizations")

    graph_values = pd.DataFrame(
        {
            "Measurement": [
                "AST",
                "ALT",
                "Total bilirubin",
                "Platelets",
                "Hemoglobin",
            ],
            "Entered value": [
                ast,
                alt,
                bilirubin,
                platelets,
                hemoglobin,
            ],
            "Unit": [
                "U/L",
                "U/L",
                "mg/dL",
                "×10⁹/L",
                "g/dL",
            ],
        }
    )

    st.markdown("#### Entered laboratory values")
    fig_labs = px.bar(
        graph_values,
        x="Measurement",
        y="Entered value",
        hover_data=["Unit"],
        title="Entered values (different units; not directly comparable)",
    )
    fig_labs.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_labs, use_container_width=True)

    st.caption(
        "The graph displays entered values, not normal ranges or toxicity grades. "
        "Because units differ, bar heights must not be compared across tests."
    )

    renal_df = pd.DataFrame(
        {
            "Estimate": ["Cockcroft–Gault CrCl", "CKD-EPI 2021 eGFR"],
            "Value": [
                crcl if crcl is not None else 0,
                egfr if egfr is not None else 0,
            ],
            "Unit": ["mL/min", "mL/min/1.73 m²"],
        }
    )

    st.markdown("#### Renal function estimates")
    fig_renal = go.Figure()

    for _, row in renal_df.iterrows():
        fig_renal.add_trace(
            go.Bar(
                x=[row["Estimate"]],
                y=[row["Value"]],
                name=row["Estimate"],
                text=[f"{row['Value']:.1f}" if row["Value"] > 0 else "N/A"],
                textposition="outside",
                hovertemplate=(
                    "%{x}<br>Value: %{y:.1f}<br>"
                    + row["Unit"]
                    + "<extra></extra>"
                ),
            )
        )

    fig_renal.update_layout(
        title="Calculated renal estimates (different units)",
        template="plotly_dark",
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_renal, use_container_width=True)

    st.caption(
        "The two estimates use different units and equations. "
        "This visualization is descriptive and should not be used to compare "
        "their magnitudes as though they were the same measurement."
    )

    st.markdown("#### CYP2D6 data entered")
    pgx_graph_df = pd.DataFrame(
        {
            "Field": ["Phenotype", "Genotype"],
            "Value": [cyp2d6_phenotype, cyp2d6_genotype],
        }
    )

    fig_pgx = px.bar(
        pgx_graph_df,
        x="Field",
        y=[1, 1],
        color="Value",
        title="Entered PGx categories (categorical display only)",
    )
    fig_pgx.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
    )
    st.plotly_chart(fig_pgx, use_container_width=True)

    st.caption(
        "This chart shows selected categories only. It does not calculate "
        "metabolizer phenotype, enzyme activity, endoxifen concentration, "
        "or toxicity probability."
    )

    if not conmed_df.empty:
        st.markdown("#### Medication screening categories")
        counts_df = (
            conmed_df["Status"]
            .value_counts()
            .rename_axis("Screening status")
            .reset_index(name="Count")
        )
        fig_conmed = px.bar(
            counts_df,
            x="Screening status",
            y="Count",
            title="Number of medicines in each screening category",
        )
        fig_conmed.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_conmed, use_container_width=True)


# ----------------------------- Clinical Report -----------------------------

with tabs[5]:
    st.subheader("Research case report")
    st.write(
        "Generate a downloadable snapshot of the current form. "
        "Review the output before using it in a poster or research workflow."
    )

    report_data = {
        "case": {
            "Research case ID": case_id,
            "Data type": data_mode,
            "Primary oncology medicine": primary_drug,
            "Age (years)": age,
            "Sex used for equation": sex,
            "Weight (kg)": weight_kg,
            "Height (cm)": height_cm,
            "BMI (kg/m²)": format_number(bmi),
            "Menopausal status": menopausal_status,
            "Cancer stage": cancer_stage,
            "Hormone receptor status": receptor_status,
            "Treatment setting": treatment_setting,
        },
        "pgx": {
            "Reported CYP2D6 phenotype": cyp2d6_phenotype,
            "Reported CYP2D6 genotype": cyp2d6_genotype,
            "Reported activity score": activity_score,
            "PGx result source": genotype_source,
            "PGx notes": cyp2d6_notes or "Not entered",
        },
        "renal": {
            "Serum creatinine (mg/dL)": serum_creatinine,
            "Cockcroft–Gault CrCl (mL/min)": format_number(crcl),
            "2021 CKD-EPI eGFR (mL/min/1.73 m²)": format_number(egfr),
        },
        "safety": {
            "AST (U/L)": ast,
            "ALT (U/L)": alt,
            "Total bilirubin (mg/dL)": bilirubin,
            "Platelets (×10⁹/L)": platelets,
            "Hemoglobin (g/dL)": hemoglobin,
            "Systolic BP (mmHg)": blood_pressure_systolic,
            "DVT / pulmonary embolism history": dvt_history,
            "Liver disease history": liver_history,
            "Uterine / endometrial history": uterine_history,
            "Prior adverse event": adverse_event_history,
            "Adverse event notes": adverse_event_notes or "Not entered",
        },
        "conmeds": conmed_df.to_dict(orient="records"),
    }

    report_text = build_report(report_data)

    st.text_area(
        "Report preview",
        value=report_text,
        height=400,
    )

    st.download_button(
        label="⬇️ Download research report (.txt)",
        data=report_text,
        file_name=f"{case_id}_research_report.txt",
        mime="text/plain",
        use_container_width=True,
    )

    json_text = json.dumps(report_data, indent=2, ensure_ascii=False)

    st.download_button(
        label="⬇️ Download structured data (.json)",
        data=json_text,
        file_name=f"{case_id}_research_data.json",
        mime="application/json",
        use_container_width=True,
    )

    csv_bytes = pd.DataFrame(
        [
            {"Section": section, "Field": field, "Value": str(value)}
            for section, section_data in report_data.items()
            if isinstance(section_data, dict)
            and section != "conmeds"
            for field, value in section_data.items()
        ]
    ).to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download case variables (.csv)",
        data=csv_bytes,
        file_name=f"{case_id}_case_variables.csv",
        mime="text/csv",
        use_container_width=True,
    )

    if st.button("Prepare report preview again", use_container_width=True):
        st.success(
            "The preview reflects the current entries. "
            "Use the download buttons above to save it."
        )


# ----------------------------- Evidence -----------------------------

with tabs[6]:
    st.subheader("Evidence and documentation")

    st.markdown(
        """
        ### Core references

        1. **CPIC guideline for CYP2D6 and tamoxifen therapy**
           - https://pmc.ncbi.nlm.nih.gov/articles/PMC5931215/

        2. **Clinical Pharmacogenetics Implementation Consortium (CPIC)**
           - https://cpicpgx.org/guidelines/

        3. **National Comprehensive Cancer Network (NCCN)**
           - https://www.nccn.org/guidelines/category_1

        4. **NIDDK: Estimated glomerular filtration rate**
           - https://www.niddk.nih.gov/health-information/professional-topics/
             kidney-disease/laboratory-evaluation/glomerular-filtration-rate
        """
    )

    st.markdown("### Evidence extraction template")

    evidence_df = pd.DataFrame(
        [
            {
                "Evidence field": "Study / guideline",
                "Entry": "",
            },
            {
                "Evidence field": "Publication year",
                "Entry": "",
            },
            {
                "Evidence field": "Study design",
                "Entry": "",
            },
            {
                "Evidence field": "Population / sample size",
                "Entry": "",
            },
            {
                "Evidence field": "CYP2D6 assay / phenotype method",
                "Entry": "",
            },
            {
                "Evidence field": "Tamoxifen exposure / adherence",
                "Entry": "",
            },
            {
                "Evidence field": "Outcome measured",
                "Entry": "",
            },
            {
                "Evidence field": "Effect estimate and uncertainty",
                "Entry": "",
            },
            {
                "Evidence field": "Limitations",
                "Entry": "",
            },
        ]
    )

    edited_evidence_df = st.data_editor(
        evidence_df,
        use_container_width=True,
        hide_index=True,
        disabled=["Evidence field"],
        num_rows="fixed",
        key="evidence_table",
    )

    evidence_csv = edited_evidence_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download evidence extraction table (.csv)",
        data=evidence_csv,
        file_name="tamoxifen_pgx_evidence_extraction.csv",
        mime="text/csv",
    )

    st.markdown("### Prototype scope and limitations")
    st.markdown(
        """
        - This app is a research demonstration, not a medical device.
        - No clinical outcome model has been trained or validated here.
        - No toxicity risk percentage or survival prediction is produced.
        - No dose selection, treatment recommendation, or medication change
          is generated.
        - The medication list and interaction observations are not exhaustive.
        - Genotype, phenotype, and activity score are independent user inputs;
          the app does not reconcile or validate them.
        - Renal equations provide estimates and have limitations.
        - No patient data are intentionally sent to an external API by this code,
          but hosting platforms and browser sessions have their own security
          and data-handling considerations. Do not enter identifiable data.
        """
    )


# ----------------------------- Footer -----------------------------

st.markdown("---")
st.caption(
    f"{APP_TITLE} | {APP_AUTHOR} | "
    "Educational research prototype — clinical validation pending."
)
