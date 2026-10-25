
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

# =========================================================
# ONCOPGX | TAMOXIFEN SAFE-USE EXPLORER
# Educational / research prototype — not validated CDS
# Dependencies: streamlit, pandas, plotly
# =========================================================

st.set_page_config(
    page_title="OncoPGx | Clinical Explorer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg,#07111f,#0b1728);
    color: #edf4ff;
}
[data-testid="stSidebar"] {background:#0b192b;}
[data-testid="stMetric"] {
    background:#11243a;
    border:1px solid #29465f;
    padding:14px;
    border-radius:12px;
}
h1,h2,h3 {color:#eaf5ff;}
</style>
""", unsafe_allow_html=True)

st.title("🧬 OncoPGx | Tamoxifen Safe-Use Explorer")
st.caption(
    "Clinical Pharmacology • PGx • Renal & Liver Assessment • "
    "Drug Interactions • Pharmacovigilance"
)

st.warning(
    "RESEARCH / EDUCATION ONLY — not validated for clinical decisions. "
    "Do not use this app to independently start, stop, switch or adjust "
    "any medicine. Do not enter identifiable patient information."
)

# ----------------------- REFERENCE DATA -----------------------

INTERACTIONS = {
    "Paroxetine": (
        "Strong CYP2D6 inhibitor",
        "May reduce endoxifen formation.",
        "High-priority medication review",
        "Discuss suitable options with the prescriber; do not stop abruptly."
    ),
    "Fluoxetine": (
        "Strong CYP2D6 inhibitor",
        "May reduce endoxifen formation.",
        "High-priority medication review",
        "Review with prescriber/pharmacist; account for its long half-life."
    ),
    "Bupropion": (
        "Strong CYP2D6 inhibitor",
        "May reduce CYP2D6-mediated activation.",
        "High-priority medication review",
        "Review with prescriber/pharmacist."
    ),
    "Quinidine": (
        "Strong CYP2D6 inhibitor",
        "Can inhibit CYP2D6 activity.",
        "Medication review",
        "Check current interaction references and indication."
    ),
    "Duloxetine": (
        "CYP2D6 inhibitor",
        "May reduce CYP2D6 activity.",
        "Medication review",
        "Review the full regimen with a clinician."
    ),
    "Terbinafine": (
        "CYP2D6 inhibitor",
        "May inhibit CYP2D6.",
        "Medication review",
        "Review indication, duration and alternatives with a clinician."
    ),
    "Sertraline": (
        "CYP2D6 inhibition varies",
        "Effect depends on dose and clinical context.",
        "Context-dependent review",
        "Verify against a current clinical interaction resource."
    ),
    "Rifampicin / rifampin": (
        "Strong enzyme inducer",
        "May reduce tamoxifen exposure.",
        "High-priority medication review",
        "Promptly review with the prescriber/pharmacist."
    ),
    "Carbamazepine": (
        "Enzyme inducer",
        "May alter exposure to concomitant medicines.",
        "Medication review",
        "Verify the specific interaction in current references."
    ),
    "Phenytoin": (
        "Enzyme inducer",
        "May alter exposure to concomitant medicines.",
        "Medication review",
        "Verify the specific interaction in current references."
    ),
    "Warfarin": (
        "Anticoagulant interaction",
        "Tamoxifen can increase anticoagulant effect and bleeding risk.",
        "High-priority medication review",
        "Prescriber/anticoagulation-team review and appropriate monitoring."
    ),
    "Anastrozole": (
        "Endocrine regimen",
        "Concurrent use needs confirmation of the intended treatment plan.",
        "Regimen review",
        "Confirm the intended oncology regimen."
    ),
    "Letrozole": (
        "Endocrine regimen",
        "Concurrent use needs confirmation of the intended treatment plan.",
        "Regimen review",
        "Confirm the intended oncology regimen."
    )
}

# ----------------------- CALCULATIONS -----------------------

def cockcroft_gault(age, weight_kg, scr_mg_dl, sex):
    """Estimated creatinine clearance in mL/min."""
    if age <= 0 or weight_kg <= 0 or scr_mg_dl <= 0:
        return None
    result = ((140 - age) * weight_kg) / (72 * scr_mg_dl)
    if sex == "Female":
        result *= 0.85
    return result


def ckd_epi_2021(age, scr_mg_dl, sex):
    """
    2021 CKD-EPI creatinine equation, race-free.
    Returns indexed eGFR in mL/min/1.73 m².
    Not suitable for every clinical context.
    """
    if age <= 0 or scr_mg_dl <= 0:
        return None

    if sex == "Female":
        k = 0.7
        alpha = -0.241
        sex_factor = 1.012
    else:
        k = 0.9
        alpha = -0.302
        sex_factor = 1.0

    ratio = scr_mg_dl / k
    egfr = (
        142
        * min(ratio, 1) ** alpha
        * max(ratio, 1) ** -1.200
        * 0.9938 ** age
        * sex_factor
    )
    return egfr


def liver_flags(alt, ast, bilirubin, albumin, inr):
    flags = []

    if alt > 40:
        flags.append("ALT above the illustrative reference threshold")
    if ast > 40:
        flags.append("AST above the illustrative reference threshold")
    if bilirubin > 1.2:
        flags.append("Bilirubin above the illustrative reference threshold")
    if albumin < 3.5:
        flags.append("Albumin below the illustrative reference threshold")
    if inr > 1.2:
        flags.append(
            "INR above the illustrative threshold; interpret in context, "
            "including anticoagulants"
        )

    if not flags:
        flags.append(
            "No flags using these illustrative thresholds; this does not "
            "exclude liver disease or establish safety."
        )

    return flags


# ----------------------- SESSION STATE -----------------------

if "pv_cases" not in st.session_state:
    st.session_state.pv_cases = []

# ----------------------- SIDEBAR INPUTS -----------------------

st.sidebar.header("Scenario setup")
st.sidebar.caption("Use fictional/demo data only.")

scenario_id = st.sidebar.text_input("Scenario label", "DEMO-001")

indication = st.sidebar.selectbox(
    "Clinical context",
    [
        "Adjuvant hormone-receptor-positive breast cancer",
        "Metastatic hormone-receptor-positive breast cancer",
        "Risk reduction / DCIS context",
        "Other / unspecified"
    ]
)

st.sidebar.subheader("Patient parameters")

age = st.sidebar.number_input(
    "Age (years)", min_value=18, max_value=110, value=55
)

sex = st.sidebar.selectbox("Sex used in equations", ["Female", "Male"])

weight = st.sidebar.number_input(
    "Weight (kg)", min_value=20.0, max_value=300.0,
    value=65.0, step=0.5
)

scr = st.sidebar.number_input(
    "Serum creatinine (mg/dL)", min_value=0.1,
    max_value=20.0, value=0.9, step=0.1
)

st.sidebar.subheader("PGx / medication review")

phenotype = st.sidebar.selectbox(
    "CYP2D6 phenotype",
    [
        "Unknown / not tested",
        "Normal metabolizer",
        "Intermediate metabolizer",
        "Poor metabolizer",
        "Ultrarapid metabolizer"
    ]
)

medicines = st.sidebar.multiselect(
    "Co-medications to screen",
    list(INTERACTIONS.keys())
)

st.sidebar.subheader("Liver laboratory inputs")

alt = st.sidebar.number_input(
    "ALT (U/L)", min_value=0.0, value=25.0, step=1.0
)
ast = st.sidebar.number_input(
    "AST (U/L)", min_value=0.0, value=24.0, step=1.0
)
bilirubin = st.sidebar.number_input(
    "Total bilirubin (mg/dL)", min_value=0.0,
    value=0.8, step=0.1
)
albumin = st.sidebar.number_input(
    "Albumin (g/dL)", min_value=0.1,
    max_value=10.0, value=4.0, step=0.1
)
inr = st.sidebar.number_input(
    "INR", min_value=0.5, max_value=15.0,
    value=1.0, step=0.1
)

# ----------------------- LIVE CALCULATIONS -----------------------

crcl = cockcroft_gault(age, weight, scr, sex)
egfr = ckd_epi_2021(age, scr, sex)
hepatic_flags = liver_flags(alt, ast, bilirubin, albumin, inr)

high_priority = [
    m for m in medicines
    if "High-priority" in INTERACTIONS[m][2]
]

other_interactions = [
    m for m in medicines
    if "High-priority" not in INTERACTIONS[m][2]
]

# ----------------------- TOP METRICS -----------------------

m1, m2, m3, m4 = st.columns(4)

m1.metric("Estimated CrCl", f"{crcl:.1f} mL/min")
m2.metric("Estimated eGFR", f"{egfr:.1f} mL/min/1.73 m²")
m3.metric("Selected medicines", len(medicines))
m4.metric("PV cases in session", len(st.session_state.pv_cases))

st.caption(
    "CrCl uses Cockcroft–Gault with entered body weight; eGFR uses "
    "the 2021 CKD-EPI creatinine equation. Weight choice, body composition, "
    "unstable creatinine and other clinical factors can affect interpretation. "
    "These estimates are not dose recommendations."
)

# ----------------------- TABS -----------------------

tabs = st.tabs([
    "📊 Live dashboard",
    "🧬 Pharmacology & PGx",
    "💊 Interactions",
    "🩺 Kidney & liver",
    "🛡️ Pharmacovigilance",
    "📋 Report"
])

# =========================================================
# TAB 1: LIVE DASHBOARD
# =========================================================

with tabs[0]:
    st.subheader("Live scenario dashboard")

    dashboard_data = pd.DataFrame({
        "Domain": [
            "Renal estimate",
            "Liver lab flags",
            "High-priority interaction flags",
            "Other interaction flags"
        ],
        "Count": [
            1 if crcl < 60 else 0,
            len(hepatic_flags) if not (
                len(hepatic_flags) == 1
                and hepatic_flags[0].startswith("No flags")
            ) else 0,
            len(high_priority),
            len(other_interactions)
        ]
    })

    fig = px.bar(
        dashboard_data,
        x="Domain",
        y="Count",
        color="Domain",
        text="Count",
        title="Current scenario: review indicators (not patient risk scores)"
    )
    fig.update_layout(
        template="plotly_dark",
        showlegend=False,
        xaxis_title="",
        yaxis_title="Count",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    renal_status = (
        "CrCl estimate below 60 mL/min: verify context and clinical relevance."
        if crcl < 60
        else "CrCl estimate is 60 mL/min or above; this alone does not establish safety."
    )

    st.info(renal_status)

    if high_priority:
        st.error(
            "High-priority medication review: " + ", ".join(high_priority)
        )
    elif medicines:
        st.info(
            "No high-priority flag from the selected subset. "
            "This does not mean the regimen is interaction-free."
        )
    else:
        st.info("No co-medications selected for screening.")

    st.write("**Scenario:**", scenario_id)
    st.write("**Clinical context:**", indication)
    st.write("**CYP2D6 phenotype:**", phenotype)

# =========================================================
# TAB 2: PHARMACOLOGY & PGx
# =========================================================

with tabs[1]:
    st.subheader("Tamoxifen activation pathway")

    st.write(
        "Tamoxifen is metabolised to active metabolites, including endoxifen. "
        "CYP2D6 contributes to endoxifen formation. CYP2D6 genetic variation "
        "and interacting medicines may influence exposure."
    )

    fig = go.Figure()

    nodes = [
        (0.08, 0.65, "Tamoxifen", "#1d4ed8"),
        (0.34, 0.65, "N-desmethyl-\ntamoxifen", "#0f766e"),
        (0.61, 0.65, "Endoxifen", "#0f766e"),
        (0.88, 0.65, "Clinical context", "#475569"),
        (0.35, 0.18, "CYP2D6 phenotype", "#7c3aed"),
        (0.65, 0.18, "Drug interactions", "#b45309")
    ]

    for x, y, label, color in nodes:
        fig.add_shape(
            type="rect",
            x0=x - 0.09, x1=x + 0.09,
            y0=y - 0.11, y1=y + 0.11,
            line=dict(color=color, width=2),
            fillcolor=color
        )
        fig.add_annotation(
            x=x, y=y, text=label.replace("\n", "<br>"),
            showarrow=False, font=dict(color="white", size=11)
        )

    for x0, y0, x1, y1 in [
        (0.17, 0.65, 0.25, 0.65),
        (0.43, 0.65, 0.52, 0.65),
        (0.70, 0.65, 0.79, 0.65),
        (0.36, 0.30, 0.56, 0.52),
        (0.65, 0.30, 0.63, 0.52)
    ]:
        fig.add_annotation(
            x=x1, y=y1, ax=x0, ay=y0,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True, arrowhead=3,
            arrowcolor="#a9c4df", arrowwidth=2
        )

    fig.update_layout(
        template="plotly_dark", height=380,
        xaxis=dict(visible=False, range=[0, 1]),
        yaxis=dict(visible=False, range=[0, 0.95]),
        showlegend=False, margin=dict(l=10, r=10, t=20, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

    phenotype_notes = {
        "Unknown / not tested":
            "No genotype inference is possible from an unknown result.",
        "Normal metabolizer":
            "Usually indicates expected CYP2D6 activity based on the reported result.",
        "Intermediate metabolizer":
            "Reduced CYP2D6 activity may affect endoxifen formation.",
        "Poor metabolizer":
            "Little or no CYP2D6 activity may be expected.",
        "Ultrarapid metabolizer":
            "Higher-than-normal CYP2D6 activity may be expected."
    }

    st.markdown("#### Selected phenotype")
    st.write(phenotype_notes[phenotype])

    st.warning(
        "Phenotype labels require a valid laboratory result and appropriate "
        "allele/activity-score interpretation. This app does not infer genotype "
        "from ancestry or predict endoxifen concentration."
    )

# =========================================================
# TAB 3: DRUG INTERACTION CHECKER
# =========================================================

with tabs[2]:
    st.subheader("Drug interaction review")

    if medicines:
        rows = []
        for medicine in medicines:
            group, mechanism, flag, action_text = INTERACTIONS[medicine]
            rows.append({
                "Medicine": medicine,
                "Mechanism/group": group,
                "Review flag": flag,
                "Potential concern": mechanism,
                "Workflow action": action_text
            })

        interaction_df = pd.DataFrame(rows)
        st.dataframe(
            interaction_df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download interaction table (CSV)",
            interaction_df.to_csv(index=False).encode("utf-8"),
            "tamoxifen_interaction_review.csv",
            "text/csv"
        )
    else:
        st.info("Select medicines in the sidebar to populate the checker.")

    st.caption(
        "This is a curated screening subset, not a complete interaction database. "
        "Confirm each finding using current product information and clinical references."
    )

# =========================================================
# TAB 4: KIDNEY & LIVER
# =========================================================

with tabs[3]:
    st.subheader("Renal function estimates")

    r1, r2 = st.columns(2)
    r1.metric("Cockcroft–Gault CrCl", f"{crcl:.1f} mL/min")
    r2.metric("CKD-EPI 2021 eGFR", f"{egfr:.1f} mL/min/1.73 m²")

    st.write(
        "**Interpretation note:** CrCl and eGFR are different estimates. "
        "They should not be substituted for one another without considering "
        "the clinical question. eGFR is indexed to a standard body surface area."
    )

    renal_df = pd.DataFrame({
        "Measure": ["CrCl (Cockcroft–Gault)", "eGFR (CKD-EPI 2021)"],
        "Value": [crcl, egfr],
        "Units": ["mL/min", "mL/min/1.73 m²"]
    })

    fig = px.bar(
        renal_df,
        x="Measure",
        y="Value",
        text="Value",
        title="Estimated renal measures (different units/interpretations)"
    )
    fig.update_layout(template="plotly_dark", height=350)
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Liver laboratory review")

    liver_df = pd.DataFrame({
        "Test": ["ALT", "AST", "Bilirubin", "Albumin", "INR"],
        "Entered value": [alt, ast, bilirubin, albumin, inr],
        "Unit": ["U/L", "U/L", "mg/dL", "g/dL", "ratio"]
    })

    st.dataframe(liver_df, use_container_width=True, hide_index=True)

    st.markdown("#### Illustrative flags")

    for flag in hepatic_flags:
        st.write("•", flag)

    st.caption(
        "Thresholds here are illustrative and are not laboratory-specific "
        "reference ranges. Interpret with the lab's reference intervals, trends, "
        "symptoms, medicines and clinical history."
    )

    with st.expander("Optional: Child–Pugh score (cirrhosis context only)"):
        st.write(
            "Use only when a clinician considers Child–Pugh appropriate for "
            "established chronic liver disease/cirrhosis. It is not a general "
            "liver toxicity score."
        )

        cp_bilirubin = st.selectbox(
            "Bilirubin category",
            ["<2 mg/dL", "2–3 mg/dL", ">3 mg/dL"]
        )
        cp_albumin = st.selectbox(
            "Albumin category",
            [">3.5 g/dL", "2.8–3.5 g/dL", "<2.8 g/dL"]
        )
        cp_inr = st.selectbox(
            "INR category",
            ["<1.7", "1.7–2.3", ">2.3"]
        )
        cp_ascites = st.selectbox(
            "Ascites (clinical assessment)",
            ["Absent", "Mild/controlled", "Moderate/severe"]
        )
        cp_enceph = st.selectbox(
            "Hepatic encephalopathy (clinical assessment)",
            ["Absent", "Grade I–II", "Grade III–IV"]
        )

        score_map = {
            "<2 mg/dL": 1, "2–3 mg/dL": 2, ">3 mg/dL": 3,
            ">3.5 g/dL": 1, "2.8–3.5 g/dL": 2, "<2.8 g/dL": 3,
            "<1.7": 1, "1.7–2.3": 2, ">2.3": 3,
            "Absent": 1, "Mild/controlled": 2, "Moderate/severe": 3,
            "Grade I–II": 2, "Grade III–IV": 3
        }

        cp_score = (
            score_map[cp_bilirubin]
            + score_map[cp_albumin]
            + score_map[cp_inr]
            + score_map[cp_ascites]
            + score_map[cp_enceph]
        )

        cp_class = (
            "Class A (5–6)" if cp_score <= 6
            else "Class B (7–9)" if cp_score <= 9
            else "Class C (10–15)"
        )

        st.metric("Calculated Child–Pugh points", cp_score)
        st.write("**Category:**", cp_class)
        st.warning(
            "Verify the score and inputs clinically. INR can be confounded by "
            "anticoagulation, and this result does not generate a tamoxifen dose."
        )

# =========================================================
# TAB 5: PHARMACOVIGILANCE
# =========================================================

with tabs[4]:
    st.subheader("Pharmacovigilance case register")

    event = st.selectbox(
        "Adverse event / symptom",
        [
            "Hot flashes / sweating",
            "Nausea / fatigue",
            "Abnormal vaginal bleeding",
            "Unilateral leg swelling / pain",
            "Sudden breathlessness / chest pain",
            "Stroke-like symptoms",
            "Yellow skin/eyes or dark urine",
            "Other / unspecified"
        ]
    )

    onset = st.selectbox(
        "Time to onset",
        ["Unknown", "Within 24 hours", "Days", "Weeks", "Months", "Long-term"]
    )

    severity = st.selectbox(
        "Reported severity", ["Mild", "Moderate", "Severe", "Unknown"]
    )

    seriousness = st.selectbox(
        "Seriousness assessment",
        [
            "Not assessed",
            "Not known to be serious",
            "Potentially serious — clinician assessment needed",
            "Hospitalisation / life-threatening / other serious criterion reported"
        ]
    )

    outcome = st.selectbox(
        "Outcome",
        ["Ongoing", "Resolved", "Improving", "Unknown", "Fatal outcome reported"]
    )

    action = st.selectbox(
        "Action taken",
        [
            "Unknown / not recorded",
            "Clinician contacted",
            "Emergency care sought",
            "Medicine changed by clinician",
            "Other"
        ]
    )

    event_notes = st.text_area(
        "Non-identifying case notes",
        placeholder="Optional: relevant timing, context, other medicines. No names or IDs."
    )

    if event in [
        "Sudden breathlessness / chest pain",
        "Stroke-like symptoms"
    ]:
        st.error(
            "Emergency warning sign: seek emergency medical care immediately."
        )
    elif event == "Unilateral leg swelling / pain":
        st.error(
            "Possible blood-clot warning sign: seek urgent medical assessment."
        )
    elif event in [
        "Abnormal vaginal bleeding",
        "Yellow skin/eyes or dark urine"
    ]:
        st.warning("Prompt clinical assessment is important.")

    if st.button("➕ Add case to this session", type="primary"):
        case = {
            "Case label": scenario_id,
            "Report date": date.today().isoformat(),
            "Event": event,
            "Onset": onset,
            "Severity": severity,
            "Seriousness": seriousness,
            "Outcome": outcome,
            "Action": action,
            "Notes": event_notes
        }
        st.session_state.pv_cases.append(case)
        st.success("Case added to the current session.")

    st.markdown("#### Saved cases")

    if st.session_state.pv_cases:
        pv_df = pd.DataFrame(st.session_state.pv_cases)
        st.dataframe(pv_df, use_container_width=True, hide_index=True)

        st.download_button(
            "Download PV register (CSV)",
            pv_df.to_csv(index=False).encode("utf-8"),
            "tamoxifen_pv_register.csv",
            "text/csv"
        )

        pv_text = pv_df.to_string(index=False)

        st.download_button(
            "Download PV summary (TXT)",
            pv_text.encode("utf-8"),
            "tamoxifen_pv_summary.txt",
            "text/plain"
        )

        if st.button("Clear session cases"):
            st.session_state.pv_cases = []
            st.rerun()
    else:
        st.info(
            "No cases saved yet. Add a demo case above. Entries persist only "
            "for this active app session and are not a permanent database."
        )

    st.caption(
        "This is not an official adverse-event submission. Follow local "
        "pharmacovigilance reporting requirements and verify cases before submission."
    )

# =========================================================
# TAB 6: REPORT GENERATOR
# =========================================================

with tabs[5]:
    st.subheader("Scenario report generator")

    liver_flag_count = len([
        x for x in hepatic_flags
        if not x.startswith("No flags")
    ])

    report_lines = [
        "ONCOPGX | TAMOXIFEN SAFE-USE EXPLORER",
        "EDUCATIONAL / RESEARCH SCENARIO REPORT",
        "=" * 55,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Scenario label: {scenario_id}",
        f"Clinical context: {indication}",
        "",
        "RENAL ESTIMATES",
        f"Cockcroft-Gault CrCl: {crcl:.1f} mL/min",
        f"CKD-EPI 2021 eGFR: {egfr:.1f} mL/min/1.73 m²",
        "",
        "LIVER LAB INPUTS",
        f"ALT: {alt} U/L",
        f"AST: {ast} U/L",
        f"Total bilirubin: {bilirubin} mg/dL",
        f"Albumin: {albumin} g/dL",
        f"INR: {inr}",
        "Liver flags:"
    ]

    report_lines += [f"- {x}" for x in hepatic_flags]

    report_lines += [
        "",
        "PHARMACOGENOMICS",
        f"CYP2D6 phenotype entered: {phenotype}",
        "No endoxifen concentration or toxicity probability calculated.",
        "",
        "MEDICATION INTERACTION REVIEW"
    ]

    if medicines:
        for med in medicines:
            group, mechanism, flag, action_text = INTERACTIONS[med]
            report_lines.append(
                f"- {med}: {flag}. {mechanism} Action: {action_text}"
            )
    else:
        report_lines.append("- No medicines selected.")

    report_lines += [
        "",
        "PHARMACOVIGILANCE",
        f"Cases saved in this session: {len(st.session_state.pv_cases)}",
        "",
        "LIMITATIONS",
        "- Not a validated clinical decision-support system.",
        "- Estimates and flags do not establish safety or diagnose disease.",
        "- No automatic dose changes or treatment switching.",
        "- Interaction list is not exhaustive.",
        "- Verify with current guidelines, product information and a clinician.",
        ""
    ]

    report_text = "\n".join(report_lines)

    st.text_area(
        "Preview report",
        report_text,
        height=450
    )

    st.download_button(
        "⬇️ Download scenario report (TXT)",
        report_text.encode("utf-8"),
        f"{scenario_id}_tamoxifen_report.txt",
        "text/plain"
    )

    summary_df = pd.DataFrame([{
        "Scenario": scenario_id,
        "Clinical context": indication,
        "Age": age,
        "Sex used in equations": sex,
        "Weight kg": weight,
        "Serum creatinine mg/dL": scr,
        "CrCl mL/min": round(crcl, 1),
        "eGFR mL/min/1.73m2": round(egfr, 1),
        "CYP2D6 phenotype": phenotype,
        "Selected medicines": "; ".join(medicines),
        "High-priority interaction flags": len(high_priority),
        "Liver lab flags": liver_flag_count,
        "PV cases in session": len(st.session_state.pv_cases)
    }])

    st.download_button(
        "⬇️ Download scenario data (CSV)",
        summary_df.to_csv(index=False).encode("utf-8"),
        f"{scenario_id}_scenario_data.csv",
        "text/csv"
    )

# ----------------------- FOOTER -----------------------

st.divider()
st.caption(
    "Evidence boundary: educational prototype only. "
    "For research use, document the version, data sources, validation plan, "
    "intended population and clinical oversight before evaluating performance."
)
