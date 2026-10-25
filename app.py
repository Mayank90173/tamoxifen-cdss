
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

st.set_page_config(
    page_title="OncoPGx | Tamoxifen Safe-Use Explorer",
    page_icon="🧬",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #07111f;
    color: #eef5ff;
}
[data-testid="stSidebar"] {
    background-color: #0b1b2c;
}
[data-testid="stMetric"] {
    background: #102238;
    border: 1px solid #29435d;
    padding: 12px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("🧬 OncoPGx | Tamoxifen Safe-Use Explorer")
st.caption(
    "Pharmacogenomics • Clinical Pharmacology • "
    "Drug Interactions • Pharmacovigilance"
)
st.error(
    "RESEARCH / EDUCATION PROTOTYPE ONLY. "
    "Not validated for clinical use. Do not use this app "
    "to prescribe, change doses, or stop medicines."
)

# ---------------------------------------------------------
# REFERENCE DATA
# ---------------------------------------------------------

INTERACTIONS = {
    "Paroxetine": {
        "class": "Strong CYP2D6 inhibitor",
        "concern": "May reduce CYP2D6-mediated endoxifen formation.",
        "priority": "High-priority review"
    },
    "Fluoxetine": {
        "class": "Strong CYP2D6 inhibitor",
        "concern": "May reduce CYP2D6-mediated endoxifen formation.",
        "priority": "High-priority review"
    },
    "Bupropion": {
        "class": "Strong CYP2D6 inhibitor",
        "concern": "May reduce CYP2D6 activity.",
        "priority": "High-priority review"
    },
    "Duloxetine": {
        "class": "CYP2D6 inhibitor",
        "concern": "Potential interaction; assess clinical context.",
        "priority": "Review"
    },
    "Sertraline": {
        "class": "CYP2D6 inhibition varies",
        "concern": "Review dose, alternatives and clinical context.",
        "priority": "Context-dependent review"
    },
    "Rifampicin": {
        "class": "Strong enzyme inducer",
        "concern": "May alter tamoxifen exposure; verify current product information.",
        "priority": "High-priority review"
    },
    "Carbamazepine": {
        "class": "Enzyme inducer",
        "concern": "Potential pharmacokinetic interaction; verify with a clinical resource.",
        "priority": "Review"
    },
    "Warfarin": {
        "class": "Anticoagulant interaction",
        "concern": "Potentially increased anticoagulant effect and bleeding risk.",
        "priority": "High-priority review"
    }
}

PHENOTYPES = [
    "Not tested / unknown",
    "Normal metabolizer",
    "Intermediate metabolizer",
    "Poor metabolizer",
    "Ultrarapid metabolizer"
]

# ---------------------------------------------------------
# SIDEBAR: DEMO SCENARIO
# ---------------------------------------------------------

st.sidebar.title("Scenario setup")
st.sidebar.caption("Use fictional cases only. Do not enter patient identifiers.")

scenario = st.sidebar.text_input("Scenario name", "Demo case A")

indication = st.sidebar.selectbox(
    "Clinical context",
    [
        "ER/PR-positive breast cancer — adjuvant",
        "Metastatic hormone receptor-positive breast cancer",
        "DCIS / risk-reduction context",
        "Other / not specified"
    ]
)

phenotype = st.sidebar.selectbox(
    "CYP2D6 phenotype",
    PHENOTYPES
)

menopause = st.sidebar.selectbox(
    "Menopausal status",
    [
        "Unknown / not documented",
        "Premenopausal",
        "Postmenopausal"
    ]
)

ai_status = st.sidebar.selectbox(
    "Aromatase inhibitor suitability",
    [
        "Not assessed",
        "May be considered by oncology team",
        "Contraindicated / not tolerated — clinician confirmed"
    ]
)

selected_meds = st.sidebar.multiselect(
    "Medicines to screen",
    list(INTERACTIONS.keys())
)

# ---------------------------------------------------------
# TOP-LEVEL SCENARIO SUMMARY
# ---------------------------------------------------------

high_priority = [
    med for med in selected_meds
    if INTERACTIONS[med]["priority"] == "High-priority review"
]

other_review = [
    med for med in selected_meds
    if INTERACTIONS[med]["priority"] != "High-priority review"
]

m1, m2, m3, m4 = st.columns(4)
m1.metric("Scenario", scenario)
m2.metric("Medicines selected", len(selected_meds))
m3.metric("High-priority flags", len(high_priority))
m4.metric("CYP2D6 status", phenotype)

if high_priority:
    st.warning(
        "High-priority interaction review: "
        + ", ".join(high_priority)
        + ". This is a review prompt, not an automatic contraindication."
    )

if other_review:
    st.info("Additional review flags: " + ", ".join(other_review))

# ---------------------------------------------------------
# MAIN TABS
# ---------------------------------------------------------

tabs = st.tabs([
    "🧬 Live Mechanism Explorer",
    "💊 Interaction Checker",
    "🛡️ Safety Signals",
    "📚 Clinical Decision Support",
    "📊 Research Dashboard"
])

# =========================================================
# TAB 1: INTERACTIVE MECHANISM EXPLORER
# =========================================================

with tabs[0]:
    st.header("Live mechanism explorer")
    st.write(
        "Select a pathway to change the diagram and explanation. "
        "Use the visual pathway to explain the biology during your presentation."
    )

    mechanisms = {
        "1. CYP2D6 and endoxifen": {
            "title": "CYP2D6 pharmacogenomics",
            "steps": [
                "Tamoxifen",
                "N-desmethyl tamoxifen",
                "Endoxifen",
                "Clinical interpretation"
            ],
            "explanation": (
                "CYP2D6 contributes to the formation of endoxifen, "
                "an active tamoxifen metabolite. Reduced enzyme activity "
                "or CYP2D6-inhibiting medicines may reduce endoxifen formation. "
                "This diagram does not calculate an individual endoxifen level."
            ),
            "modifier": "Diplotype, activity score, phenotype and interacting medicines",
            "clinical": (
                "Use a validated laboratory report and current CPIC guidance "
                "when interpreting CYP2D6 results. Do not infer phenotype "
                "from symptoms or ancestry."
            ),
            "source": "CPIC tamoxifen–CYP2D6 guideline; verify the current version."
        },
        "2. CYP2D6 inhibitor interaction": {
            "title": "Drug interaction pathway",
            "steps": [
                "Tamoxifen",
                "CYP2D6 inhibition",
                "Potentially reduced endoxifen formation",
                "Medication review"
            ],
            "explanation": (
                "Some medicines inhibit CYP2D6 and can reduce the conversion "
                "of tamoxifen to endoxifen. The magnitude depends on the drug, "
                "dose, exposure and clinical context."
            ),
            "modifier": "Co-medication, dose, duration and alternatives",
            "clinical": (
                "Review the full medication list with the prescriber or pharmacist. "
                "Do not stop antidepressants or other prescribed medicines abruptly."
            ),
            "source": "CPIC guidance and current medicine product information."
        },
        "3. CYP3A4 and enzyme induction": {
            "title": "Enzyme induction and drug exposure",
            "steps": [
                "Tamoxifen exposure",
                "Enzyme-inducing medicine",
                "Possible altered drug exposure",
                "Clinical review"
            ],
            "explanation": (
                "Enzyme induction can change the exposure of medicines and "
                "their metabolites. The effect is drug-specific; do not assume "
                "that every inducer has the same effect on tamoxifen."
            ),
            "modifier": "Inducer identity, dose, duration and product label",
            "clinical": (
                "Check the exact interaction in a current clinical resource "
                "and obtain pharmacist/prescriber review before any change."
            ),
            "source": "Current tamoxifen product information and interaction resources."
        },
        "4. Estrogen receptor action": {
            "title": "Selective estrogen receptor modulator",
            "steps": [
                "Tamoxifen",
                "Estrogen receptor interaction",
                "Tissue-dependent effects",
                "Clinical context"
            ],
            "explanation": (
                "Tamoxifen is a selective estrogen receptor modulator (SERM). "
                "Its effects differ by tissue; it acts as an estrogen antagonist "
                "in breast tissue, while effects in other tissues are different."
            ),
            "modifier": "Tissue, disease setting and endocrine context",
            "clinical": (
                "Mechanism alone does not determine whether tamoxifen is the "
                "right treatment for a particular patient."
            ),
            "source": "Established pharmacology and current oncology guidance."
        },
        "5. Aromatase inhibitor pathway": {
            "title": "Reduction of estrogen synthesis",
            "steps": [
                "Aromatase inhibitor",
                "Aromatase inhibition",
                "Reduced estrogen synthesis",
                "Oncology assessment"
            ],
            "explanation": (
                "Anastrozole, letrozole and exemestane inhibit aromatase, "
                "reducing estrogen synthesis. Suitability depends on the "
                "clinical setting and patient factors."
            ),
            "modifier": "Menopausal status, tolerability and recurrence risk",
            "clinical": (
                "In premenopausal patients, an aromatase inhibitor generally "
                "requires ovarian function suppression. Regimen choice belongs "
                "to the oncology team."
            ),
            "source": "Current ASCO/ESMO guidance and relevant product information."
        },
        "6. Ovarian function suppression": {
            "title": "Ovarian function suppression",
            "steps": [
                "OFS treatment",
                "Reduced ovarian activity",
                "Lower ovarian estrogen production",
                "Regimen review"
            ],
            "explanation": (
                "Ovarian function suppression reduces ovarian estrogen production. "
                "It may be part of selected endocrine regimens for premenopausal "
                "patients, depending on clinical indication and risk."
            ),
            "modifier": "Menopausal status, regimen and patient preferences",
            "clinical": (
                "The need for ovarian suppression and the choice of endocrine "
                "therapy require individual oncology assessment."
            ),
            "source": "Current oncology endocrine-therapy guidance."
        },
        "7. Safety and pharmacovigilance": {
            "title": "Adverse-event recognition",
            "steps": [
                "Medicine exposure",
                "New symptom",
                "Clinical assessment",
                "Appropriate escalation"
            ],
            "explanation": (
                "A safety signal is a reason to assess a symptom, not proof that "
                "tamoxifen caused it. The app does not calculate adverse-event "
                "probability or establish causality."
            ),
            "modifier": "Symptom severity, timing, history and competing causes",
            "clinical": (
                "Sudden breathlessness or chest pain requires emergency assessment. "
                "New unilateral leg swelling/pain needs urgent assessment. "
                "Abnormal vaginal bleeding needs prompt clinical review."
            ),
            "source": "Current product safety information and local clinical protocols."
        }
    }

    choice = st.selectbox(
        "Choose a pathway to demonstrate",
        list(mechanisms.keys())
    )

    selected = mechanisms[choice]

    st.subheader(selected["title"])

    # Build a live, selectable pathway diagram.
    labels = selected["steps"]
    x_positions = list(range(len(labels)))

    fig = go.Figure()

    for i, label in enumerate(labels):
        fig.add_trace(go.Scatter(
            x=[i],
            y=[0],
            mode="markers+text",
            text=[label],
            textposition="bottom center",
            marker=dict(size=42),
            hovertemplate="%{text}<extra></extra>",
            showlegend=False
        ))

    for i in range(len(labels) - 1):
        fig.add_annotation(
            x=i + 1,
            y=0,
            ax=i,
            ay=0,
            xref="x",
            yref="y",
            axref="x",
            ayref="y",
            text="",
            showarrow=True,
            arrowhead=3,
            arrowsize=1.5,
            arrowwidth=2
        )

    fig.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=30, b=100),
        xaxis=dict(
            visible=False,
            range=[-0.5, len(labels) - 0.5]
        ),
        yaxis=dict(visible=False, range=[-0.6, 0.7]),
        template="plotly_dark",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Live explanation")
    st.write(selected["explanation"])

    st.markdown("### What can modify this pathway?")
    st.info(selected["modifier"])

    st.markdown("### Clinical relevance")
    st.write(selected["clinical"])

    st.caption("Evidence note: " + selected["source"])

    st.markdown("### Current demo scenario")
    st.write({
        "Scenario": scenario,
        "CYP2D6 phenotype": phenotype,
        "Selected medicines": selected_meds if selected_meds else "None selected"
    })

    st.caption(
        "Educational visualization only. No individual risk, drug concentration, "
        "treatment response or toxicity probability is predicted."
    )

# =========================================================
# TAB 2: INTERACTION CHECKER
# =========================================================

with tabs[1]:
    st.header("Drug interaction review")

    if not selected_meds:
        st.info("Select one or more medicines in the sidebar to screen the demo case.")
    else:
        rows = []

        for med in selected_meds:
            item = INTERACTIONS[med]
            rows.append({
                "Medicine": med,
                "Interaction class": item["class"],
                "Potential concern": item["concern"],
                "Review priority": item["priority"]
            })

        interaction_df = pd.DataFrame(rows)

        st.dataframe(
            interaction_df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download interaction review CSV",
            data=interaction_df.to_csv(index=False).encode("utf-8"),
            file_name="tamoxifen_interaction_review.csv",
            mime="text/csv"
        )

    st.warning(
        "This list is not exhaustive. A medicine not listed here is not "
        "automatically safe. Confirm interactions using current clinical resources."
    )

# =========================================================
# TAB 3: SAFETY SIGNALS
# =========================================================

with tabs[2]:
    st.header("Safety signals and pharmacovigilance")
    st.write(
        "Record a fictional teaching scenario. This form is not a diagnostic "
        "tool and does not submit an adverse-event report."
    )

    symptom = st.selectbox(
        "Demo symptom",
        [
            "No symptom selected",
            "Unilateral leg swelling or pain",
            "Chest pain or sudden breathlessness",
            "Abnormal vaginal bleeding",
            "Possible liver injury symptoms",
            "Other / nonspecific symptom"
        ]
    )

    severity = st.selectbox(
        "Demo severity",
        ["Not assessed", "Mild", "Moderate", "Severe"]
    )

    onset = st.selectbox(
        "Timing relative to treatment",
        ["Unknown", "Before treatment", "After treatment started"]
    )

    if symptom == "Chest pain or sudden breathlessness":
        st.error(
            "Emergency warning: chest pain or sudden breathlessness needs "
            "emergency medical assessment."
        )
    elif symptom == "Unilateral leg swelling or pain":
        st.warning(
            "Urgent assessment is needed to evaluate possible causes, including "
            "a blood clot. This app cannot diagnose the cause."
        )
    elif symptom == "Abnormal vaginal bleeding":
        st.warning(
            "Prompt clinical assessment is needed. Do not assume the symptom "
            "is caused by tamoxifen without evaluation."
        )
    elif symptom == "Possible liver injury symptoms":
        st.warning(
            "Seek prompt medical evaluation for possible liver injury symptoms."
        )
    else:
        st.info("Select a demo symptom to see the relevant safety prompt.")

    safety_record = pd.DataFrame([{
        "Scenario": scenario,
        "Symptom": symptom,
        "Severity": severity,
        "Timing": onset,
        "Record date": date.today().isoformat()
    }])

    st.subheader("Demo safety record")
    st.dataframe(safety_record, use_container_width=True, hide_index=True)

    st.download_button(
        "Download demo safety record",
        data=safety_record.to_csv(index=False).encode("utf-8"),
        file_name="tamoxifen_demo_safety_record.csv",
        mime="text/csv"
    )

    st.caption(
        "This is a fictional educational record, not a submitted adverse drug "
        "reaction report. Follow local pharmacovigilance procedures."
    )

# =========================================================
# TAB 4: CLINICAL DECISION SUPPORT
# =========================================================

with tabs[3]:
    st.header("Guideline-informed clinical discussion")
    st.caption(
        "Educational summary, not a prescription engine. Confirm current "
        "guidelines, product labeling and the full clinical context."
    )

    st.markdown("### Clinical eligibility")
    st.write("Selected context: **" + indication + "**")

    if indication == "Other / not specified":
        st.warning(
            "The clinical indication is unclear. Do not generate a treatment "
            "pathway until the oncology team confirms the indication."
        )
    elif indication == "Metastatic hormone receptor-positive breast cancer":
        st.warning(
            "Metastatic disease requires a separate oncology assessment. "
            "Previous therapies, disease characteristics, biomarkers and "
            "patient factors influence treatment selection."
        )
    else:
        st.info(
            "Confirm pathology, disease setting, stage, previous therapies, "
            "comorbidities and patient preferences before applying a guideline."
        )

    st.markdown("### CYP2D6 interpretation")

    if phenotype == "Not tested / unknown":
        st.info(
            "CYP2D6 status is unknown. Do not infer genotype from symptoms "
            "or ancestry. Routine CYP2D6 testing is not universally recommended "
            "by all oncology guidelines."
        )
    elif phenotype in ["Normal metabolizer", "Ultrarapid metabolizer"]:
        st.write(
            "CPIC reference: standard tamoxifen dosing is generally supported "
            "for normal and ultrarapid metabolizers when tamoxifen is otherwise "
            "appropriate. Review CYP2D6-inhibiting co-medications."
        )
    elif phenotype == "Intermediate metabolizer":
        st.write(
            "Reduced CYP2D6 activity may affect endoxifen formation. Confirm "
            "the laboratory diplotype and activity score; discuss options with "
            "the oncology team using current guidance."
        )
    elif phenotype == "Poor metabolizer":
        st.write(
            "CPIC guidance supports considering an alternative endocrine "
            "approach when clinically appropriate. Menopausal status and "
            "other clinical factors affect the options."
        )

    st.markdown("### Menopausal status and AI suitability")
    st.write("Menopausal status: **" + menopause + "**")
    st.write("AI suitability: **" + ai_status + "**")

    if menopause == "Premenopausal":
        st.info(
            "If an aromatase inhibitor is considered, ovarian function "
            "suppression is generally required in premenopausal patients."
        )

    st.warning(
        "This prototype does not choose a regimen, prescribe a dose, or "
        "determine whether an individual patient should change treatment."
    )

    st.markdown("### Evidence sources to consult")
    st.markdown("""
    - CPIC: CYP2D6 genotype and tamoxifen therapy.
    - ASCO: endocrine therapy guidance for breast cancer.
    - ESMO: breast cancer clinical practice guidance.
    - Current official product information for tamoxifen and interacting medicines.
    """)

# =========================================================
# TAB 5: RESEARCH DASHBOARD
# =========================================================

with tabs[4]:
    st.header("Research dashboard")
    st.write(
        "This dashboard summarizes the current fictional scenario. "
        "It is not a patient registry or validated prediction model."
    )

    dashboard = pd.DataFrame([
        {"Metric": "Scenario", "Value": scenario},
        {"Metric": "Clinical context", "Value": indication},
        {"Metric": "CYP2D6 phenotype", "Value": phenotype},
        {"Metric": "Menopausal status", "Value": menopause},
        {"Metric": "Selected medicines", "Value": len(selected_meds)},
        {"Metric": "High-priority interaction flags", "Value": len(high_priority)},
        {"Metric": "Other interaction review flags", "Value": len(other_review)}
    ])

    st.dataframe(dashboard, use_container_width=True, hide_index=True)

    c1, c2 = st.columns(2)
    c1.metric("Interaction flags", len(selected_meds))
    c2.metric("High-priority review flags", len(high_priority))

    if selected_meds:
        counts = pd.DataFrame({
            "Medicine": selected_meds,
            "Priority": [
                INTERACTIONS[m]["priority"] for m in selected_meds
            ]
        })

        st.subheader("Selected medicine review priorities")
        st.bar_chart(counts["Priority"].value_counts())

    st.download_button(
        "Download scenario summary CSV",
        data=dashboard.to_csv(index=False).encode("utf-8"),
        file_name="oncoPGx_demo_dashboard.csv",
        mime="text/csv"
    )

    st.caption(
        "No model training, external validation, calibration, individual "
        "toxicity prediction or clinical outcome prediction is performed."
    )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.divider()
st.caption(
    "OncoPGx | Tamoxifen Safe-Use Explorer — educational research prototype. "
    "Verify all clinical statements against current authoritative sources."
)
