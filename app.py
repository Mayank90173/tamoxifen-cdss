
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
    st.metric("Common adult tamoxifen reference", "20 mg/day")
    st.caption(
        "The appropriate regimen depends on indication, product labeling, "
        "treatment plan, and the prescribing clinician. This reference "
        "does not establish that 20 mg/day is appropriate for every setting."
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
        "- Aromatase inhibitor-based treatment when appropriate.\n"
        "- Aromatase inhibitor plus ovarian function suppression in "
        "selected premenopausal contexts.\n"
        "- Other clinician-directed endocrine options when alternatives "
        "are unsuitable."
    )
    st.caption(
        "The options are context-dependent and are not individual treatment "
        "recommendations. Verify current CPIC, oncology guidelines, and "
        "product labeling."
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
            "on CYP2D6 genotype and tamoxifen therapy.",
            "https://cpicpgx.org/",
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

# -------------------- FOOTER --------------------

st.markdown("---")
st.caption(
    "OncoPGx • Educational precision-oncology prototype • "
    "Clinical decisions remain with qualified healthcare professionals."
)
