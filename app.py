import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import io
import math
from datetime import datetime, date
from pathlib import Path

# Local persistence. On hosted platforms, local files may be ephemeral.
DATA_DIR = Path("oncopgx_data")
DATA_DIR.mkdir(exist_ok=True)
PV_DB = DATA_DIR / "pv_registry.csv"
TDM_DB = DATA_DIR / "tdm_measurements.csv"

def read_local_csv(path, columns):
    """Read a local research CSV safely; return an empty table if absent/unreadable."""
    try:
        if path.exists():
            df = pd.read_csv(path)
            for col in columns:
                if col not in df.columns:
                    df[col] = ""
            return df[columns]
    except Exception:
        pass
    return pd.DataFrame(columns=columns)

def append_local_row(path, columns, row):
    """Append one row to a local CSV research log."""
    df = read_local_csv(path, columns)
    df = pd.concat([df, pd.DataFrame([{c: row.get(c, "") for c in columns}])], ignore_index=True)
    df.to_csv(path, index=False)
    return df

st.set_page_config(
    page_title="OncoPGx | Precision Oncology",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------- THEME --------------------

st.markdown("""
<style>
.stApp {
    background:
      radial-gradient(ellipse at 80% 0%, #102b59 0%, transparent 38%),
      radial-gradient(ellipse at 0% 80%, #101b45 0%, transparent 35%),
      #06101f;
    color: #edf5ff;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#09172d,#06101f);
    border-right: 1px solid #1b4266;
}
h1,h2,h3 { color: #e5f5ff !important; }
p, label, li { color: #c6d8f2; }
[data-testid="stMetric"] {
    background: linear-gradient(135deg,#102747,#0b1830);
    border: 1px solid #23527b;
    padding: 15px;
    border-radius: 13px;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    border-color: #20496c;
    border-radius: 14px;
}
.stButton > button {
    background: linear-gradient(90deg,#087ee1,#7857ff);
    color: white;
    border: 0;
    border-radius: 9px;
}
div[data-baseweb="select"] > div {
    background-color: #0b1c35;
}
hr { border-color: #214264; }
.hero {
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #22618b;
    background: linear-gradient(115deg,#0b2344,#102253,#161640);
}
.small { color: #83b8e8; font-size: 13px; }
.warning {
    padding: 12px;
    border: 1px solid #d84b75;
    border-radius: 10px;
    background: #29152a;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div style="font-size:14px;color:#55dfff;letter-spacing:3px">
    PRECISION ONCOLOGY • PHARMACOGENOMICS
  </div>
  <h1 style="font-size:38px;margin:8px 0">
    🧬 OncoPGx
  </h1>
  <h3 style="font-weight:400">
    Tamoxifen Safe-Use Explorer
  </h3>
  <p>
    Mechanistic pharmacology · PGx · Drug interactions ·
    Safety screening · Clinical evidence
  </p>
</div>
""", unsafe_allow_html=True)

st.error(
    "RESEARCH / EDUCATION PROTOTYPE ONLY. "
    "Not validated for clinical use. No individual toxicity probability "
    "is calculated. Never start, stop, or change a medicine based on this app."
)

# -------------------- KNOWLEDGE BASE --------------------

PHENOTYPES = {
    "Not tested / unknown": {
        "activity": "Unknown",
        "summary": "Do not infer genotype from symptoms or ancestry.",
        "approach": "Use the existing clinical plan; testing decisions follow local guidance.",
    },
    "Normal metabolizer": {
        "activity": "Expected normal activity",
        "summary": "Expected CYP2D6 activity is within the normal range.",
        "approach": "Standard treatment may be appropriate if clinically indicated.",
    },
    "Intermediate metabolizer": {
        "activity": "Reduced activity",
        "summary": "CYP2D6 activity is expected to be reduced.",
        "approach": "Review the actual genotype/activity score and clinical context.",
    },
    "Poor metabolizer": {
        "activity": "Little or no activity",
        "summary": "CYP2D6-mediated endoxifen formation may be reduced.",
        "approach": "Discuss endocrine alternatives with the oncology team.",
    },
    "Ultrarapid metabolizer": {
        "activity": "Higher-than-normal activity",
        "summary": "Predicted activity is higher than the normal range.",
        "approach": "Do not increase or reduce treatment solely from this label.",
    },
}

INTERACTIONS = {
    "Paroxetine": (
        "Strong CYP2D6 inhibitor",
        "May reduce endoxifen formation",
        "High-priority medication review",
    ),
    "Fluoxetine": (
        "Strong CYP2D6 inhibitor",
        "May reduce endoxifen formation; effects can persist",
        "High-priority medication review",
    ),
    "Bupropion": (
        "Strong CYP2D6 inhibitor",
        "May reduce CYP2D6 activity",
        "High-priority medication review",
    ),
    "Duloxetine": (
        "Moderate CYP2D6 inhibitor",
        "May affect CYP2D6 activity",
        "Review clinical context",
    ),
    "Terbinafine": (
        "CYP2D6 inhibitor",
        "May inhibit tamoxifen activation",
        "Review indication and alternatives",
    ),
    "Sertraline": (
        "CYP2D6 inhibition varies",
        "Effect depends on context and dose",
        "Review the complete medication list",
    ),
    "Rifampicin / rifampin": (
        "Strong CYP3A4 inducer",
        "May reduce tamoxifen exposure",
        "Prompt prescriber/pharmacist review",
    ),
    "Carbamazepine": (
        "Enzyme inducer",
        "May alter drug exposure",
        "Verify with a current interaction resource",
    ),
    "Phenytoin": (
        "Enzyme inducer",
        "May alter drug exposure",
        "Verify with a current interaction resource",
    ),
    "Warfarin": (
        "Anticoagulant interaction",
        "May increase anticoagulant effect and bleeding risk",
        "Review anticoagulation monitoring",
    ),
    "Anastrozole": (
        "Endocrine regimen overlap",
        "Concurrent use is not routine in standard adjuvant treatment",
        "Confirm intended regimen with oncology",
    ),
    "Letrozole": (
        "Endocrine regimen overlap",
        "Concurrent use requires regimen-specific justification",
        "Confirm intended regimen with oncology",
    ),
}

PATHWAYS = {
    "CYP2D6 → Endoxifen formation": {
        "steps": [
            "Tamoxifen",
            "N-desmethyl-tamoxifen",
            "Endoxifen",
        ],
        "description": (
            "CYP2D6 contributes to formation of endoxifen, an active "
            "tamoxifen metabolite. Genotype and CYP2D6-inhibiting medicines "
            "can influence endoxifen exposure."
        ),
        "takeaway": "Genetic activity and inhibitors can affect metabolism.",
    },
    "Estrogen receptor pharmacology": {
        "steps": [
            "Tamoxifen",
            "Active metabolites",
            "Estrogen receptor",
            "Tissue-dependent effects",
        ],
        "description": (
            "Tamoxifen is a selective estrogen receptor modulator (SERM). "
            "Its receptor effects vary by tissue and biological context."
        ),
        "takeaway": "Receptor effects depend on tissue and clinical setting.",
    },
    "CYP3A4 and drug metabolism": {
        "steps": [
            "Tamoxifen",
            "Metabolic pathways",
            "Active metabolites",
        ],
        "description": (
            "Several enzymes contribute to tamoxifen metabolism. Strong "
            "enzyme inducers or inhibitors can change exposure; the effect "
            "must be checked against current product information."
        ),
        "takeaway": "Metabolic pathways are interconnected, not a single-enzyme switch.",
    },
    "Drug interaction pathway": {
        "steps": [
            "Co-medication",
            "Enzyme effect",
            "Altered exposure",
            "Clinical review",
        ],
        "description": (
            "Co-medications can affect metabolism, bleeding risk, or endocrine "
            "regimen compatibility. A screening flag is not proof of harm."
        ),
        "takeaway": "Review the full medicine list before clinical decisions.",
    },
    "Endocrine treatment alternatives": {
        "steps": [
            "Clinical context",
            "Menopausal status",
            "Endocrine options",
            "Oncology review",
        ],
        "description": (
            "Depending on the cancer setting and menopausal status, the "
            "oncology team may consider an aromatase inhibitor, ovarian "
            "function suppression, or another endocrine strategy."
        ),
        "takeaway": "Alternatives depend on indication and patient-specific factors.",
    },
}

# ================= PATIENT PROFILE MODULE =================

st.sidebar.markdown("---")
st.sidebar.markdown("## 👤 Patient Profile")

with st.sidebar.form("patient_profile_form"):
    patient_id = st.text_input(
        "Demo Patient ID",
        value="DEMO-001",
        help="Use a fictional ID. Do not enter patient-identifying information."
    )

    age = st.number_input(
        "Age (years)",
        min_value=18,
        max_value=110,
        value=52
    )

    menopausal_status = st.selectbox(
        "Menopausal status",
        [
            "Unknown",
            "Premenopausal",
            "Postmenopausal",
            "Perimenopausal / uncertain"
        ]
    )

    cancer_stage = st.selectbox(
        "Cancer stage",
        [
            "Unknown",
            "Stage 0 / DCIS",
            "Stage I",
            "Stage II",
            "Stage III",
            "Stage IV / metastatic"
        ]
    )

    er_status = st.selectbox(
        "Estrogen receptor (ER)",
        ["Positive", "Negative", "Unknown"]
    )

    pr_status = st.selectbox(
        "Progesterone receptor (PR)",
        ["Positive", "Negative", "Unknown"]
    )

    her2_status = st.selectbox(
        "HER2 status",
        ["Positive", "Negative", "Unknown"]
    )

    treatment_setting = st.selectbox(
        "Treatment setting",
        [
            "Adjuvant",
            "Metastatic",
            "Risk reduction / DCIS",
            "Other / unknown"
        ]
    )

    prescribed_dose = st.selectbox(
        "Currently prescribed tamoxifen dose",
        ["Unknown", "10 mg/day", "20 mg/day", "40 mg/day", "Other"]
    )

    cyp2d6 = st.selectbox(
        "CYP2D6 phenotype",
        [
            "Not tested / unknown",
            "Normal metabolizer",
            "Intermediate metabolizer",
            "Poor metabolizer",
            "Ultrarapid metabolizer"
        ]
    )

    bmi = st.number_input(
        "BMI (kg/m²)",
        min_value=10.0,
        max_value=80.0,
        value=25.0,
        step=0.5
    )

    liver_status = st.selectbox(
        "Liver function",
        ["Unknown", "No known impairment", "Impairment reported"]
    )

    vte_history = st.selectbox(
        "Previous venous thromboembolism (VTE)",
        ["Unknown", "No known history", "History reported"]
    )

    adherence = st.selectbox(
        "Medication adherence",
        ["Unknown", "Reported good", "Missed doses reported"]
    )

    endoxifen = st.text_input(
        "Measured endoxifen level (optional)",
        placeholder="Enter value only if measured"
    )

    medications = st.text_area(
        "Current medicines",
        placeholder="Enter generic medicine names separated by commas"
    )

    symptoms = st.multiselect(
        "Symptoms / adverse events",
        [
            "Hot flashes",
            "Abnormal vaginal bleeding",
            "Leg swelling or pain",
            "Chest pain or sudden breathlessness",
            "Jaundice or dark urine",
            "Other / none reported"
        ]
    )

    save_profile = st.form_submit_button(
        "Save Patient Profile",
        use_container_width=True
    )

if save_profile:
    st.session_state["patient_profile"] = {
        "Patient ID": patient_id.strip() or "DEMO-001",
        "Age": age,
        "Menopausal status": menopausal_status,
        "Cancer stage": cancer_stage,
        "ER status": er_status,
        "PR status": pr_status,
        "HER2 status": her2_status,
        "Treatment setting": treatment_setting,
        "Prescribed dose": prescribed_dose,
        "CYP2D6 phenotype": cyp2d6,
        "BMI": bmi,
        "Liver function": liver_status,
        "VTE history": vte_history,
        "Adherence": adherence,
        "Endoxifen level": endoxifen.strip() or "Not available",
        "Current medicines": medications.strip() or "Not entered",
        "Symptoms": symptoms
    }

    st.sidebar.success("Profile saved for this session.")

# ================= PATIENT SUMMARY =================

profile = st.session_state.get("patient_profile")

if profile:
    st.markdown("---")
    st.subheader("👤 Active Patient Scenario")

    st.caption(
        "Fictional research scenario — not a validated clinical assessment."
    )

    # Surface receptor-status context early so an ER-negative scenario is not
    # accidentally interpreted as a tamoxifen dosing scenario.
    if profile.get("ER status") == "Negative":
        st.error(
            "INITIAL CHECK — ER-negative scenario: tamoxifen is not routine "
            "endocrine treatment for confirmed ER-negative breast cancer. "
            "Review complete pathology (including any ER/PR discordance), HER2, "
            "stage and the oncology plan before discussing endocrine medicines."
        )
    elif profile.get("ER status") == "Unknown":
        st.warning(
            "INITIAL CHECK — ER status is unknown. Confirm tumour receptor status "
            "before interpreting tamoxifen or aromatase-inhibitor options."
        )
    elif profile.get("ER status") == "Positive":
        st.info(
            "INITIAL CHECK — ER-positive scenario: endocrine therapy may be relevant, "
            "but selection depends on stage, menopausal status and the oncology plan."
        )

    st.markdown(
        f"### Patient: {profile['Patient ID']}"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Age", f"{profile['Age']} years")
    c2.metric("CYP2D6", profile["CYP2D6 phenotype"])
    c3.metric("Prescribed dose", profile["Prescribed dose"])
    c4.metric("BMI", f"{profile['BMI']:.1f}")

    with st.expander("View complete clinical profile"):
        st.dataframe(
            pd.DataFrame(
                [
                    {"Parameter": key, "Value": value}
                    for key, value in profile.items()
                ]
            ),
            use_container_width=True,
            hide_index=True
        )

    flags = []

    if profile["CYP2D6 phenotype"] == "Poor metabolizer":
        flags.append(
            "Review CYP2D6 interpretation and endocrine options with oncology."
        )

    if profile["Liver function"] == "Impairment reported":
        flags.append(
            "Liver impairment reported: clinician review may be appropriate."
        )

    if profile["VTE history"] == "History reported":
        flags.append(
            "Previous VTE reported: review thromboembolic risk with the care team."
        )

    if profile["Adherence"] == "Missed doses reported":
        flags.append(
            "Adherence concern: discuss barriers with the care team."
        )

    if profile["Symptoms"]:
        for symptom in profile["Symptoms"]:
            if symptom == "Chest pain or sudden breathlessness":
                flags.append(
                    "URGENT: chest pain or sudden breathlessness requires emergency assessment."
                )
            elif symptom == "Leg swelling or pain":
                flags.append(
                    "New leg swelling or pain needs urgent assessment for possible VTE."
                )
            elif symptom == "Abnormal vaginal bleeding":
                flags.append(
                    "Abnormal vaginal bleeding requires clinical assessment."
                )
            elif symptom == "Jaundice or dark urine":
                flags.append(
                    "Jaundice or dark urine requires prompt clinical assessment."
                )
            elif symptom not in ("Other / none reported",):
                flags.append(
                    f"Reported symptom: {symptom}. Review severity and context."
                )

    if flags:
        st.markdown("### ⚠️ Review prompts")
        for flag in flags:
            st.warning(flag)
    else:
        st.info(
            "No review prompts triggered by the fields entered. "
            "This does not establish that treatment is safe."
        )


# -------------------- SIDEBAR --------------------

st.sidebar.markdown("## 🧬 OncoPGx")
st.sidebar.caption("Precision oncology workspace")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Overview",
        "Mechanism Explorer",
        "CYP2D6 Pharmacogenomics",
        "Drug Interaction Checker",
        "Dosage Decision Support",
        "Toxicity Screening",
        "Pharmacovigilance",
        "Renal & Hepatic Labs",
        "Endoxifen TDM",
        "PK/AUC Sandbox",
        "PV Registry & Reports",
        "Guidelines & Evidence",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Research prototype**\n\n"
    "No validated clinical prediction model is embedded. "
    "Use fictional scenarios only; do not enter identifiable patient data."
)

# -------------------- OVERVIEW --------------------

if page == "Overview":
    st.subheader("Precision oncology workspace")
    st.write(
        "Explore tamoxifen pharmacology, CYP2D6-related variability, "
        "drug interactions, and treatment safety considerations."
    )

    a, b, c, d = st.columns(4)
    a.metric("Mechanistic pathways", len(PATHWAYS))
    b.metric("Interaction entries", len(INTERACTIONS))
    c.metric("PGx phenotypes", len(PHENOTYPES))
    d.metric("Prediction model", "Not validated")

    st.markdown("### Research modules")
    cards = [
        ("🧬", "Mechanism Explorer", "Explore metabolic and receptor pathways."),
        ("🧪", "Pharmacogenomics", "Interpret a reported CYP2D6 phenotype."),
        ("💊", "Interaction Checker", "Screen selected co-medications."),
        ("🛡️", "Toxicity Screening", "Review safety factors without inventing probabilities."),
    ]
    cols = st.columns(2)
    for i, (emoji, title, desc) in enumerate(cards):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"### {emoji} {title}")
                st.write(desc)

    st.info(
        "Suggested demonstration: choose a pathway, change the CYP2D6 "
        "scenario, select an interacting medicine, and inspect the "
        "transparent safety flags."
    )

# -------------------- MECHANISM EXPLORER --------------------

elif page == "Mechanism Explorer":
    st.subheader("Interactive mechanism explorer")
    choice = st.selectbox("Select a pathway", list(PATHWAYS.keys()))
    pathway = PATHWAYS[choice]

    st.write(pathway["description"])

    fig = go.Figure()
    n = len(pathway["steps"])
    xs = [i / max(n - 1, 1) for i in range(n)]
    colors = ["#126de5", "#00bfa6", "#7657ff", "#e34e9a"]

    for i, (x, label) in enumerate(zip(xs, pathway["steps"])):
        fig.add_trace(go.Scatter(
            x=[x], y=[0],
            mode="markers+text",
            text=[label],
            textposition="bottom center",
            marker=dict(
                size=38,
                color=colors[i % len(colors)],
                line=dict(color="#bcecff", width=1.5),
            ),
            hovertemplate="%{text}<extra></extra>",
            showlegend=False,
        ))
        if i < n - 1:
            fig.add_annotation(
                x=xs[i + 1] - 0.08,
                y=0,
                ax=xs[i] + 0.08,
                ay=0,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                text="",
                showarrow=True,
                arrowhead=3,
                arrowwidth=2,
                arrowcolor="#38d9ff",
            )

    fig.update_layout(
        template="plotly_dark",
        height=310,
        margin=dict(l=30, r=30, t=35, b=90),
        xaxis=dict(visible=False, range=[-0.12, 1.12]),
        yaxis=dict(visible=False, range=[-0.6, 0.6]),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig, use_container_width=True)
    st.success(pathway["takeaway"])

    with st.expander("Scientific interpretation and limitations"):
        st.write(
            "This is a conceptual pathway illustration. It does not "
            "calculate enzyme activity, measured endoxifen concentration, "
            "treatment efficacy, or individual toxicity probability."
        )

# -------------------- PHARMACOGENOMICS --------------------

elif page == "CYP2D6 Pharmacogenomics":
    st.subheader("CYP2D6 phenotype explorer")
    st.markdown("### CYP2D6 genotype examples")

    GENOTYPE_EXAMPLES = {
        "*1/*1": {
            "activity_score": "2.0",
            "phenotype": "Normal metabolizer",
            "interpretation": (
                "Two normal-function alleles in this illustrative example."
            ),
        },
        "*1/*10": {
            "activity_score": "1.25",
            "phenotype": "Normal metabolizer",
            "interpretation": (
                "One normal-function allele and one decreased-function "
                "allele. Confirm the laboratory's allele assignment."
            ),
        },
        "*4/*10": {
            "activity_score": "0.25",
            "phenotype": "Intermediate metabolizer",
            "interpretation": (
                "One no-function allele and one decreased-function allele."
            ),
        },
        "*10/*10": {
            "activity_score": "0.5",
            "phenotype": "Intermediate metabolizer",
            "interpretation": (
                "Two decreased-function *10 alleles; verify the laboratory "
                "star-allele calls and activity-score method."
            ),
        },
        "*1/*4": {
            "activity_score": "1.0",
            "phenotype": "Intermediate metabolizer (guideline-specific interpretation)",
            "interpretation": (
                "One normal-function and one no-function allele. An activity "
                "score of 1.0 can require allele- and guideline-specific interpretation."
            ),
        },
        "*4/*4": {
            "activity_score": "0",
            "phenotype": "Poor metabolizer",
            "interpretation": (
                "Two no-function alleles in this illustrative example."
            ),
        },
    }

    selected_genotype = st.selectbox(
        "Select an illustrative CYP2D6 genotype",
        list(GENOTYPE_EXAMPLES.keys()),
        key="cyp2d6_genotype_examples",
    )

    genotype_info = GENOTYPE_EXAMPLES[selected_genotype]

    g1, g2 = st.columns(2)
    g1.metric(
        "Illustrative activity score",
        genotype_info["activity_score"],
    )
    g2.metric(
        "Illustrative phenotype",
        genotype_info["phenotype"],
    )

    st.info(genotype_info["interpretation"])

    st.caption(
        "Educational examples only. Activity scores and phenotype labels can "
        "depend on the allele-function table and guideline version. Confirm allele "
        "function, copy-number/hybrid variation, activity score and phenotype using "
        "the actual laboratory report and applicable clinical guidance. "
        "Do not infer a person's genotype from ancestry."
    )

    phenotype = st.selectbox(
        "Select reported phenotype",
        list(PHENOTYPES.keys()),
    )
    data = PHENOTYPES[phenotype]

    a, b = st.columns(2)
    a.metric("Expected activity", data["activity"])
    b.metric("Selected scenario", phenotype)

    st.markdown("### Interpretation")
    st.write(data["summary"])
    st.info(data["approach"])

    st.markdown("### Phenotype comparison")
    table = pd.DataFrame([
        {
            "Phenotype": name,
            "Expected activity": values["activity"],
            "Interpretation": values["summary"],
        }
        for name, values in PHENOTYPES.items()
    ])
    st.dataframe(table, use_container_width=True, hide_index=True)

    st.caption(
        "CPIC guidance and oncology guidelines have different scopes. "
        "CYP2D6 testing is not universally recommended to choose adjuvant "
        "endocrine therapy. Confirm current local guidance and the actual "
        "laboratory report before clinical interpretation."
    )

# -------------------- INTERACTION CHECKER --------------------

elif page == "Drug Interaction Checker":
    st.subheader("Drug–drug interaction screening")

    medicines = st.multiselect(
        "Select co-medications in a fictional scenario",
        list(INTERACTIONS.keys()),
    )
    search = st.text_input("Filter displayed medicines", "").strip().lower()

    if medicines:
        rows = []
        for med in medicines:
            group, effect, action = INTERACTIONS[med]
            rows.append({
                "Medicine": med,
                "Interaction group": group,
                "Potential concern": effect,
                "Review prompt": action,
            })

        df = pd.DataFrame(rows)
        if search:
            df = df[
                df.astype(str).apply(
                    lambda col: col.str.lower().str.contains(search)
                ).any(axis=1)
            ]

        st.dataframe(df, use_container_width=True, hide_index=True)
        st.metric("Selected review flags", len(medicines))
        st.warning(
            "These are screening prompts, not confirmed patient-specific "
            "interactions. Verify against current product information and "
            "a clinical pharmacist/prescriber."
        )
    else:
        st.info("Select one or more medicines to see interaction details.")

    st.caption(
        "The list is not exhaustive. A medicine absent from this list "
        "cannot be assumed safe or interaction-free."
    )

# -------------------- DOSAGE DECISION SUPPORT --------------------

elif page == "Dosage Decision Support":
    st.subheader("Dose reference and clinical decision support")

    st.info(
        "Reference information only. This module does not prescribe, "
        "calculate a personalised dose, or recommend unsupervised dose changes."
    )

    setting = st.selectbox(
        "Clinical context",
        [
            "Adjuvant treatment",
            "Metastatic disease",
            "Risk reduction / DCIS",
            "Other / not specified",
        ],
    )
    menopause = st.selectbox(
        "Menopausal status",
        ["Unknown", "Premenopausal", "Postmenopausal", "Uncertain"],
    )
    er_status_dose = st.selectbox(
        "Estrogen receptor (ER) status",
        ["Positive", "Negative", "Unknown / discordant"],
        help="Endocrine therapy decisions depend on confirmed tumour receptor status.",
    )
    pr_status_dose = st.selectbox(
        "Progesterone receptor (PR) status",
        ["Positive", "Negative", "Unknown"],
        help="An ER-negative / PR-positive result is uncommon and may warrant pathology review.",
    )
    phenotype = st.selectbox(
        "CYP2D6 phenotype",
        list(PHENOTYPES.keys()),
        key="dose_phenotype",
    )
    ai_status = st.selectbox(
        "Aromatase inhibitor suitability",
        [
            "Not assessed",
            "May be considered by oncology team",
            "Contraindicated or not tolerated (clinician-confirmed)",
        ],
    )
    inhibitor = st.selectbox(
        "Strong CYP2D6 inhibitor present?",
        ["Unknown", "No", "Yes"],
    )

    st.markdown("### Standard reference")
    st.metric("Common adult adjuvant reference (when endocrine therapy is indicated)", "Tamoxifen 20 mg/day")
    st.caption(
        "This is a reference dose, not a personalised recommendation. The "
        "appropriate regimen depends on confirmed hormone-receptor status, "
        "stage/setting, menopausal status, product labeling and the oncology plan."
    )

    st.markdown("### Initial receptor-status check")
    if er_status_dose == "Negative":
        if pr_status_dose == "Positive":
            st.error(
                "ER-negative / PR-positive result: tamoxifen should not be "
                "assumed effective. This uncommon/discordant pattern warrants "
                "pathology review and confirmation of ER/PR testing before an "
                "endocrine-treatment decision. Do not auto-select tamoxifen or an AI."
            )
        else:
            st.error(
                "ER-negative tumour: tamoxifen and aromatase inhibitors are not "
                "routine endocrine treatment for a confirmed ER-negative cancer. "
                "Treatment should be guided by the full pathology (including HER2), "
                "stage and oncology team; do not recommend tamoxifen 20 or 40 mg "
                "on the basis of CYP2D6 alone."
            )
    elif er_status_dose == "Unknown / discordant":
        st.warning(
            "ER status is unknown/discordant: no endocrine drug or dose should "
            "be inferred. Confirm the pathology report and receptor results first."
        )
    else:
        st.success(
            "ER-positive scenario: endocrine therapy may be relevant. Compare "
            "options using menopausal status, clinical setting, contraindications "
            "and the complete oncology plan."
        )

    st.markdown("### Context-aware discussion output")
    if er_status_dose != "Positive":
        st.info(
            "No tamoxifen dose recommendation is generated because ER positivity "
            "has not been confirmed. The 20 mg/day reference above is not a "
            "recommendation for this scenario."
        )
    elif phenotype in ("Poor metabolizer", "Intermediate metabolizer"):
        if menopause == "Postmenopausal":
            st.warning(
                "Reduced CYP2D6 activity scenario: discuss an aromatase inhibitor "
                "as an alternative with oncology, if clinically suitable. If an AI "
                "is contraindicated or not tolerated, tamoxifen 40 mg/day may be "
                "considered by the prescriber in selected cases; it does not "
                "guarantee normal endoxifen exposure."
            )
        elif menopause == "Premenopausal":
            st.warning(
                "Reduced CYP2D6 activity scenario: discuss an aromatase inhibitor "
                "PLUS ovarian function suppression with oncology if appropriate. "
                "If this approach is unsuitable, the prescriber may consider other "
                "options; tamoxifen 40 mg/day is not an automatic first choice."
            )
        else:
            st.warning(
                "Reduced CYP2D6 activity scenario: first clarify menopausal status "
                "and review interacting medicines. An AI alone is not an appropriate "
                "default for a premenopausal patient; ovarian function suppression "
                "may be required if an AI strategy is chosen."
            )
    else:
        st.info(
            "For normal/ultrarapid or unknown CYP2D6 phenotype, do not escalate "
            "tamoxifen solely from the phenotype label. If tamoxifen is the chosen "
            "treatment for confirmed ER-positive disease, 20 mg/day is the common "
            "reference dose; verify the complete clinical plan and interactions."
        )

    st.markdown("### Factors for clinician review")
    review_items = []
    if phenotype == "Poor metabolizer":
        review_items.append(
            "Review endocrine alternatives; CPIC discusses alternatives "
            "in appropriate clinical contexts."
        )
    elif phenotype == "Intermediate metabolizer":
        review_items.append(
            "Confirm the genotype/activity score and review current guidance."
        )
    elif phenotype == "Not tested / unknown":
        review_items.append(
            "Phenotype is unknown; do not infer it from symptoms or ancestry."
        )

    if inhibitor == "Yes":
        review_items.append(
            "Review the interacting medicine and possible alternatives "
            "without stopping it independently."
        )
    elif inhibitor == "Unknown":
        review_items.append(
            "Medication interaction status is unknown."
        )

    if menopause == "Unknown" or menopause == "Uncertain":
        review_items.append(
            "Clarify menopausal status before evaluating endocrine options."
        )

    if ai_status == "Contraindicated or not tolerated (clinician-confirmed)":
        review_items.append(
            "Discuss suitable options with the oncology team; do not "
            "automatically escalate tamoxifen dosage."
        )

    if setting == "Other / not specified":
        review_items.append(
            "Confirm the exact treatment indication and intended regimen."
        )

    if review_items:
        for item in review_items:
            st.warning(item)
    else:
        st.success(
            "No additional prompts triggered by these selections. "
            "This is not confirmation that the regimen is suitable."
        )

    st.markdown("### Alternative endocrine approaches to discuss")
    st.write(
        "- For confirmed ER-positive disease after menopause: an aromatase inhibitor "
        "may be an option if clinically suitable.\\n"
        "- For confirmed ER-positive disease before menopause: an aromatase inhibitor "
        "generally requires ovarian function suppression.\\n"
        "- If aromatase inhibitors are unsuitable, the oncology team should review "
        "other endocrine options and the reason for intolerance/contraindication.\\n"
        "- For confirmed ER-negative disease, routine endocrine therapy with "
        "tamoxifen or an aromatase inhibitor is generally not indicated."
    )
    st.caption(
        "Guideline context: CPIC's CYP2D6–tamoxifen guidance supports standard "
        "tamoxifen 20 mg/day for normal/ultrarapid metabolizers; for reduced "
        "function, it discusses an AI (with ovarian suppression when premenopausal) "
        "and allows 40 mg/day only as a clinician-considered alternative when an AI "
        "cannot be used. 40 mg does not guarantee normal endoxifen exposure. "
        "This prototype does not prescribe or change treatment. Verify current "
        "CPIC, oncology guidelines, pathology and product labeling."
    )

# -------------------- TOXICITY SCREENING --------------------

elif page == "Toxicity Screening":
    st.subheader("Treatment safety and toxicity-factor explorer")

    st.warning(
        "This is a transparent checklist, NOT an AI model. It does not "
        "estimate an individual's probability of toxicity or replace "
        "clinical assessment."
    )

    st.markdown("### Scenario factors")
    age = st.number_input("Age (years)", min_value=18, max_value=110, value=52)
    bmi = st.number_input(
        "BMI (kg/m²; optional context)",
        min_value=10.0,
        max_value=80.0,
        value=25.0,
        step=0.5,
    )
    liver_status = st.selectbox(
        "Liver status",
        ["Unknown", "No known impairment", "Impairment reported"],
    )
    clot_history = st.selectbox(
        "History of venous thromboembolism",
        ["Unknown", "No known history", "History reported"],
    )
    uterine_status = st.selectbox(
        "Uterine / endometrial context",
        ["Unknown", "Not applicable / absent uterus", "Present / needs review"],
    )
    symptoms = st.multiselect(
        "Symptoms or concerns reported in scenario",
        [
            "Hot flashes",
            "Abnormal vaginal bleeding",
            "Leg swelling or pain",
            "Chest pain or sudden breathlessness",
            "Jaundice or dark urine",
        ],
    )

    st.markdown("### Review output")
    flags = []

    if liver_status == "Impairment reported":
        flags.append(
            "Liver impairment reported: clinician review may be needed."
        )
    if clot_history == "History reported":
        flags.append(
            "VTE history reported: assess thromboembolic risk with the "
            "treating team."
        )
    if uterine_status == "Present / needs review":
        flags.append(
            "Endometrial context requires appropriate clinical monitoring "
            "and assessment of symptoms."
        )
    if age >= 65:
        flags.append(
            "Age 65 or older: interpret overall risks in the full clinical context."
        )
    if bmi >= 30:
        flags.append(
            "BMI at least 30: consider it within the broader clinical risk profile."
        )

    symptom_actions = {
        "Hot flashes": "Hot flashes: discuss symptom management if troublesome.",
        "Abnormal vaginal bleeding": (
            "Abnormal vaginal bleeding: prompt clinical assessment is needed."
        ),
        "Leg swelling or pain": (
            "New leg swelling or pain: urgent assessment may be needed for VTE."
        ),
        "Chest pain or sudden breathlessness": (
            "Chest pain or sudden breathlessness: seek emergency medical care."
        ),
        "Jaundice or dark urine": (
            "Jaundice or dark urine: urgent clinical assessment is needed."
        ),
    }

    for symptom in symptoms:
        flags.append(symptom_actions[symptom])

    if flags:
        st.metric("Review prompts", len(flags))
        for flag in flags:
            st.warning(flag)
    else:
        st.info(
            "No checklist prompts triggered by these entries. This does not "
            "mean the patient is at low risk or free from toxicity."
        )

    st.markdown("### Future validated toxicity model")
    st.write(
        "A genuine prediction model would require a defined endpoint, "
        "a suitable patient dataset, prespecified predictors, missing-data "
        "handling, model training, external validation, calibration, "
        "and performance reporting."
    )
    st.caption(
        "No percentage, low/medium/high probability, or personalised "
        "dose recommendation is generated here."
    )

# -------------------- PHARMACOVIGILANCE --------------------

elif page == "Pharmacovigilance":
    st.subheader("Pharmacovigilance and adverse-event review")

    st.write(
        "Tamoxifen safety monitoring includes thromboembolic events, "
        "endometrial abnormalities or cancer, vasomotor symptoms, and "
        "less common hepatic adverse effects. Risk varies by patient "
        "and treatment context."
    )

    pv = pd.DataFrame([
        {
            "Safety topic": "Venous thromboembolism",
            "Example signal": "Leg swelling, pain, sudden breathlessness",
            "Response": "Urgent assessment when clinically suspected",
        },
        {
            "Safety topic": "Endometrial effects",
            "Example signal": "Abnormal vaginal bleeding",
            "Response": "Clinical evaluation; follow appropriate guidance",
        },
        {
            "Safety topic": "Vasomotor effects",
            "Example signal": "Hot flashes or night sweats",
            "Response": "Assess severity and discuss symptom management",
        },
        {
            "Safety topic": "Hepatic effects",
            "Example signal": "Jaundice or dark urine",
            "Response": "Prompt clinical assessment",
        },
    ])
    st.dataframe(pv, use_container_width=True, hide_index=True)

    st.markdown("### Demonstration report form")
    with st.form("pv_demo"):
        event = st.selectbox(
            "Event category",
            ["Hot flashes", "VTE concern", "Abnormal bleeding", "Hepatic concern", "Other"],
        )
        seriousness = st.selectbox(
            "Seriousness (demo classification)",
            ["Not assessed", "Non-serious", "Serious"],
        )
        outcome = st.selectbox(
            "Outcome",
            ["Unknown", "Recovering", "Recovered", "Ongoing", "Fatal"],
        )
        submitted = st.form_submit_button("Review demonstration report")

    if submitted:
        st.write({
            "Event": event,
            "Seriousness": seriousness,
            "Outcome": outcome,
        })
        st.info(
            "Demonstration only: this form does not submit to a regulator, "
            "create a validated safety report, or establish causality."
        )

# -------------------- GUIDELINES & EVIDENCE --------------------

elif page == "Guidelines & Evidence":
    st.subheader("Evidence and guideline workspace")

    st.write(
        "Use current, authoritative documents to verify every clinical "
        "statement before presenting or using this prototype."
    )

    sources = [
        (
            "CPIC — CYP2D6 and tamoxifen",
            "Clinical Pharmacogenetics Implementation Consortium guidance "
            "on CYP2D6 genotype and tamoxifen therapy (2018 guideline; verify "
            "whether newer local guidance applies).",
            "https://pmc.ncbi.nlm.nih.gov/articles/5931215/",
        ),
        (
            "NCCN — Breast Cancer",
            "Current oncology guidance; access and recommendations may "
            "depend on the guideline version.",
            "https://www.nccn.org/",
        ),
        (
            "FDA — Drug labels",
            "Check current prescribing information and interaction warnings.",
            "https://www.accessdata.fda.gov/scripts/cder/daf/",
        ),
        (
            "NCI — Breast Cancer",
            "Authoritative background on breast cancer and treatment.",
            "https://www.cancer.gov/types/breast",
        ),
        (
            "NCI — Hormone Therapy for Breast Cancer",
            "Explains that endocrine therapy is used for hormone-receptor-positive "
            "disease and that aromatase inhibitors generally require ovarian "
            "suppression in premenopausal patients.",
            "https://www.cancer.gov/types/breast/treatment/hormone-therapy",
        ),
        (
            "PubMed",
            "Search primary studies and systematic reviews.",
            "https://pubmed.ncbi.nlm.nih.gov/",
        ),
    ]

    for title, description, url in sources:
        with st.container(border=True):
            st.markdown(f"### {title}")
            st.write(description)
            st.link_button("Open source", url)

    st.markdown("### Evidence audit")
    st.write(
        "- Record the exact guideline title, version, and access date.\n"
        "- Link each clinical rule to a supporting source.\n"
        "- Separate guideline recommendations from hypotheses.\n"
        "- Do not present an exploratory algorithm as a validated clinical model."
    )


# -------------------- ADVANCED RENAL / HEPATIC MODULE --------------------

elif page == "Renal & Hepatic Labs":
    st.subheader("Renal and hepatic laboratory workspace")
    st.caption("Research calculations only. Equations and flags do not diagnose organ impairment or determine a dose.")
    left, right = st.columns(2)
    with left:
        st.markdown("### Kidney estimates")
        age_lab = st.number_input("Age (years)", min_value=18, max_value=110, value=52, key="lab_age")
        sex_eq = st.selectbox("Sex factor for equations", ["Female equation", "Male equation", "Not specified"], key="lab_sex")
        wt = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=65.0, step=0.5, key="lab_wt")
        scr = st.number_input("Serum creatinine (mg/dL)", min_value=0.1, max_value=25.0, value=0.9, step=0.1, key="lab_scr")
        if sex_eq != "Not specified":
            female = sex_eq == "Female equation"
            crcl = ((140 - age_lab) * wt) / (72 * scr) * (0.85 if female else 1.0)
            k = 0.7 if female else 0.9
            alpha = -0.241 if female else -0.302
            egfr = 142 * (min(scr / k, 1) ** alpha) * (max(scr / k, 1) ** -1.200) * (0.9938 ** age_lab) * (1.012 if female else 1.0)
            m1, m2 = st.columns(2)
            m1.metric("Cockcroft–Gault CrCl", f"{crcl:.1f} mL/min")
            m2.metric("2021 CKD-EPI eGFR", f"{egfr:.1f} mL/min/1.73 m²")
            st.info("CrCl and eGFR are different estimates and are not interchangeable. The 2021 CKD-EPI creatinine equation uses a sex-specific coefficient; 'Not specified' intentionally suppresses the estimates.")
        else:
            st.warning("Select the equation's sex factor to calculate these estimates. Do not guess the input.")
    with right:
        st.markdown("### Liver laboratory review")
        ast = st.number_input("AST (U/L)", min_value=0.0, max_value=10000.0, value=25.0, key="lab_ast")
        ast_uln = st.number_input("AST upper limit of normal (U/L)", min_value=1.0, max_value=1000.0, value=40.0, key="lab_ast_uln")
        alt = st.number_input("ALT (U/L)", min_value=0.0, max_value=10000.0, value=25.0, key="lab_alt")
        alt_uln = st.number_input("ALT upper limit of normal (U/L)", min_value=1.0, max_value=1000.0, value=40.0, key="lab_alt_uln")
        bili = st.number_input("Total bilirubin (mg/dL)", min_value=0.0, max_value=100.0, value=0.8, key="lab_bili")
        bili_uln = st.number_input("Bilirubin upper limit of normal (mg/dL)", min_value=0.1, max_value=20.0, value=1.2, key="lab_bili_uln")
        alp = st.number_input("ALP (U/L; optional)", min_value=0.0, max_value=10000.0, value=80.0, key="lab_alp")
        alp_uln = st.number_input("ALP upper limit of normal (U/L)", min_value=1.0, max_value=1000.0, value=120.0, key="lab_alp_uln")
        st.metric("AST / ULN", f"{ast/ast_uln:.2f}×")
        st.metric("ALT / ULN", f"{alt/alt_uln:.2f}×")
        st.metric("Bilirubin / ULN", f"{bili/bili_uln:.2f}×")
        if alt >= 3*alt_uln or ast >= 3*ast_uln or bili >= 2*bili_uln:
            st.warning("One or more entered values cross a simple review threshold. This is not a diagnosis and does not establish Hy's law; clinical context, ALP, symptoms, timing and alternative causes matter.")
        else:
            st.success("No simple threshold flag from these entries. Normal-looking values do not rule out disease.")
    if st.button("Save lab scenario to session"):
        st.session_state["last_lab_scenario"] = {
            "recorded_at": datetime.now().isoformat(timespec="seconds"),
            "age": age_lab, "equation_sex_factor": sex_eq, "weight_kg": wt, "serum_creatinine_mg_dl": scr,
            "Cockcroft-Gault CrCl_mL_min": round(crcl, 2) if sex_eq != "Not specified" else None,
            "CKD-EPI 2021 eGFR_mL_min_1.73m2": round(egfr, 2) if sex_eq != "Not specified" else None,
            "AST_U_L": ast, "ALT_U_L": alt, "bilirubin_mg_dl": bili, "ALP_U_L": alp
        }
        st.success("Saved in current session only.")

# -------------------- END OXIFEN TDM --------------------

elif page == "Endoxifen TDM":
    st.subheader("Endoxifen therapeutic drug monitoring (TDM)")
    st.warning("Enter measured results only. This tool does not infer endoxifen from genotype, dose, adherence, or a simulated curve; no universal therapeutic threshold is applied.")
    cols = ["recorded_at", "scenario_id", "sample_date", "endoxifen_value", "unit", "tamoxifen_dose_mg_day", "adherence", "notes"]
    history = read_local_csv(TDM_DB, cols)
    with st.form("tdm_entry_form"):
        scenario_id = st.text_input("Fictional scenario ID", value="DEMO-001")
        sample_date = st.date_input("Sample date", value=date.today())
        level = st.number_input("Measured endoxifen value", min_value=0.0, max_value=100000.0, value=0.0, step=0.1, help="Enter the laboratory-reported numeric result.")
        unit = st.selectbox("Unit as reported by lab", ["ng/mL", "nM", "µg/L", "Other / specify in notes"])
        dose = st.selectbox("Prescribed tamoxifen dose (mg/day)", ["Unknown", "10", "20", "40", "Other"])
        adher = st.selectbox("Adherence context", ["Unknown", "Reported consistent", "Missed doses reported", "Recently changed"])
        notes = st.text_input("Notes (optional; no identifying details)")
        add_tdm = st.form_submit_button("Save measured result")
    if add_tdm:
        if level <= 0:
            st.error("Enter a positive measured value. Use zero only if that is a valid lab result and document the context separately.")
        else:
            row = {"recorded_at": datetime.now().isoformat(timespec="seconds"), "scenario_id": scenario_id.strip() or "DEMO-001",
                   "sample_date": sample_date.isoformat(), "endoxifen_value": level, "unit": unit,
                   "tamoxifen_dose_mg_day": dose, "adherence": adher, "notes": notes}
            history = append_local_row(TDM_DB, cols, row)
            st.success("Saved to local CSV. On hosted platforms, local storage may be reset when the app restarts.")
    history = read_local_csv(TDM_DB, cols)
    if not history.empty:
        st.markdown("### Stored measured results")
        scenario_filter = st.selectbox("Display scenario", ["All scenarios"] + sorted(history["scenario_id"].dropna().astype(str).unique().tolist()))
        shown = history if scenario_filter == "All scenarios" else history[history["scenario_id"].astype(str) == scenario_filter]
        st.dataframe(shown, use_container_width=True, hide_index=True)
        plot_df = shown.copy()
        plot_df["sample_date"] = pd.to_datetime(plot_df["sample_date"], errors="coerce")
        plot_df["endoxifen_value"] = pd.to_numeric(plot_df["endoxifen_value"], errors="coerce")
        for unit_value, unit_df in plot_df.groupby("unit"):
            unit_df = unit_df.dropna(subset=["sample_date", "endoxifen_value"]).sort_values("sample_date")
            if not unit_df.empty:
                fig_tdm = go.Figure()
                fig_tdm.add_trace(go.Scatter(x=unit_df["sample_date"], y=unit_df["endoxifen_value"], mode="lines+markers", name=str(unit_value)))
                fig_tdm.update_layout(template="plotly_dark", title=f"Measured endoxifen trend ({unit_value})", xaxis_title="Sample date", yaxis_title=f"Measured value ({unit_value})")
                st.plotly_chart(fig_tdm, use_container_width=True)
        st.download_button("Download TDM CSV", data=history.to_csv(index=False).encode("utf-8"), file_name="oncopgx_tdm_measurements.csv", mime="text/csv")
    else:
        st.info("No TDM records saved yet.")
    st.caption("Values in different units are plotted separately; the app does not convert them without a verified analyte-specific conversion and lab context.")

# -------------------- PK / AUC SANDBOX --------------------

elif page == "PK/AUC Sandbox":
    st.subheader("Illustrative pharmacokinetic model sandbox")
    st.warning("Educational one-compartment model only—not calibrated to tamoxifen, endoxifen, or any patient. Do not use for dosing, efficacy, or toxicity predictions.")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        dose_demo = st.number_input("Illustrative input amount (arbitrary units)", min_value=1.0, max_value=10000.0, value=100.0, step=10.0)
        ka = st.number_input("Absorption rate constant ka (1/h)", min_value=0.01, max_value=5.0, value=1.0, step=0.05)
    with col_b:
        kel = st.number_input("Elimination rate constant kel (1/h)", min_value=0.005, max_value=2.0, value=0.08, step=0.005)
        volume = st.number_input("Apparent volume V (arbitrary L)", min_value=1.0, max_value=10000.0, value=100.0, step=5.0)
    with col_c:
        bioavail = st.slider("Bioavailability F (illustrative)", min_value=0.05, max_value=1.0, value=0.7, step=0.05)
        hours = st.slider("Display window (hours)", min_value=12, max_value=720, value=120, step=12)
    if abs(ka-kel) < 1e-6:
        st.warning("Choose ka and kel that are not equal for this equation.")
    else:
        n_steps = 241
        times = [hours*i/(n_steps-1) for i in range(n_steps)]
        # One-compartment oral input; units are illustrative, not clinically calibrated.
        concentrations = [bioavail*dose_demo*ka/(volume*(ka-kel))*(math.exp(-kel*t)-math.exp(-ka*t)) for t in times]
        concentrations = [max(0.0, c) for c in concentrations]
        auc = sum((concentrations[i]+concentrations[i+1])*(times[i+1]-times[i])/2 for i in range(len(times)-1))
        fig_pk = go.Figure()
        fig_pk.add_trace(go.Scatter(x=times, y=concentrations, mode="lines", name="Illustrative concentration"))
        fig_pk.update_layout(template="plotly_dark", title="Simulated concentration–time curve (arbitrary units)", xaxis_title="Time (h)", yaxis_title="Illustrative concentration")
        st.plotly_chart(fig_pk, use_container_width=True)
        p1, p2 = st.columns(2)
        p1.metric("Numerical AUC over displayed window", f"{auc:.2f} arbitrary units·h")
        p2.metric("Peak in displayed window", f"{max(concentrations):.3f} arbitrary units")
        st.caption("AUC depends on chosen parameters and the finite display window. This is a mathematical demonstration, not a tamoxifen PK model and not a patient-specific estimate.")
        export_pk = pd.DataFrame({"time_h": times, "illustrative_concentration": concentrations})
        st.download_button("Download simulated curve CSV", export_pk.to_csv(index=False).encode("utf-8"), "illustrative_pk_curve.csv", "text/csv")

# -------------------- PV REGISTRY AND REPORT EXPORT --------------------

elif page == "PV Registry & Reports":
    st.subheader("Local pharmacovigilance registry and research exports")
    st.caption("Use fictional or properly de-identified records only. This local log is not connected to PvPI, a hospital EHR, or a regulator.")
    pv_cols = ["report_id", "recorded_at", "scenario_id", "drug", "event_term", "onset_date", "seriousness", "outcome", "dechallenge", "rechallenge", "stage", "notes"]
    pv_df = read_local_csv(PV_DB, pv_cols)
    with st.form("pv_registry_form"):
        p1, p2 = st.columns(2)
        with p1:
            scenario = st.text_input("Fictional scenario ID", value="DEMO-001", key="pv_scenario")
            drug = st.text_input("Suspected medicine", value="Tamoxifen")
            event_term = st.selectbox("Adverse event term", ["Hot flashes", "Venous thromboembolism concern", "Abnormal vaginal bleeding", "Hepatic concern", "Nausea", "Other"])
            onset = st.date_input("Event onset date", value=date.today(), key="pv_onset")
            stage = st.selectbox("Cancer stage (if relevant)", ["Unknown", "Stage 0 / DCIS", "Stage I", "Stage II", "Stage III", "Stage IV / metastatic"])
        with p2:
            serious = st.selectbox("Seriousness", ["Not assessed", "Non-serious", "Serious"])
            outcome = st.selectbox("Outcome", ["Unknown", "Recovering", "Recovered", "Ongoing", "Fatal"])
            dechallenge = st.selectbox("Improved after stopping/withdrawing?", ["Unknown", "Yes", "No", "Not applicable"])
            rechallenge = st.selectbox("Recurred after restarting?", ["Unknown", "Yes", "No", "Not applicable"])
            pv_notes = st.text_input("Non-identifying notes")
        submit_pv = st.form_submit_button("Add report to local registry")
    if submit_pv:
        report_id = f"PV-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        row = {"report_id": report_id, "recorded_at": datetime.now().isoformat(timespec="seconds"),
               "scenario_id": scenario.strip() or "DEMO-001", "drug": drug.strip() or "Unknown",
               "event_term": event_term, "onset_date": onset.isoformat(), "seriousness": serious,
               "outcome": outcome, "dechallenge": dechallenge, "rechallenge": rechallenge,
               "stage": stage, "notes": pv_notes}
        pv_df = append_local_row(PV_DB, pv_cols, row)
        st.success(f"Saved local demonstration record: {report_id}")
    pv_df = read_local_csv(PV_DB, pv_cols)
    if not pv_df.empty:
        st.markdown("### Registry overview")
        m1, m2, m3 = st.columns(3)
        m1.metric("Reports recorded", len(pv_df))
        m2.metric("Marked serious", int((pv_df["seriousness"] == "Serious").sum()))
        m3.metric("Distinct event terms", int(pv_df["event_term"].nunique()))
        st.dataframe(pv_df.sort_values("recorded_at", ascending=False), use_container_width=True, hide_index=True)
        st.download_button("Download PV registry CSV", pv_df.to_csv(index=False).encode("utf-8"), "oncopgx_pv_registry.csv", "text/csv")
        counts = pv_df.groupby(["drug", "event_term"], dropna=False).size().reset_index(name="record_count")
        st.markdown("### Descriptive counts only")
        st.dataframe(counts, use_container_width=True, hide_index=True)
        st.caption("Counts are not incidence rates, causality assessments, validated disproportionality analyses, or regulatory safety signals.")
    else:
        st.info("No local PV reports saved yet.")

    st.markdown("### Export current research scenario")
    profile_export = st.session_state.get("patient_profile", {})
    report = {
        "app": "OncoPGx",
        "version": "advanced research prototype",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "notice": "Educational/research use only; not a clinical decision-support validation.",
        "patient_profile": profile_export,
        "last_lab_scenario": st.session_state.get("last_lab_scenario", {}),
        "data_files": {"pv_registry": str(PV_DB), "tdm_measurements": str(TDM_DB)},
        "limitations": [
            "No validated individual toxicity prediction",
            "No autonomous prescribing or dose adjustment",
            "Local CSV storage may be ephemeral on hosted platforms",
            "Use fictional/de-identified data; no patient identifiers",
        ],
    }
    st.download_button("Export scenario report (JSON)", data=json.dumps(report, indent=2, default=str), file_name="oncopgx_research_report.json", mime="application/json")
    st.download_button("Export active profile (CSV)", data=pd.DataFrame([profile_export]).to_csv(index=False).encode("utf-8") if profile_export else b"", file_name="oncopgx_active_profile.csv", mime="text/csv", disabled=not bool(profile_export))
    st.info("PDF export is not included in this advanced add-on; JSON/CSV exports are provided to keep the report transparent and reproducible.")

# -------------------- FOOTER --------------------

st.markdown("---")
st.caption(
    "OncoPGx • Educational precision-oncology prototype • "
    "Clinical decisions remain with qualified healthcare professionals."
)
