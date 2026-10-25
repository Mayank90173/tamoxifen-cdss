
from datetime import date, datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# OncoPGx India — Tamoxifen research decision-support prototype
# Research use only. Not a validated clinical decision system.
# ============================================================

st.set_page_config(
    page_title="OncoPGx India",
    page_icon="🧬",
    layout="wide",
)

st.title("🧬 OncoPGx India")
st.subheader("Tamoxifen • Pharmacogenomics • Safety • Evidence")

st.warning(
    "RESEARCH ONLY: Outputs are evidence summaries, not patient-specific "
    "prescriptions. Do not start, stop, switch or change a dose using this app. "
    "Use fictional or appropriately de-identified data."
)

CPIC_URL = "https://pmc.ncbi.nlm.nih.gov/articles/5931215/"
FDA_URL = "https://www.accessdata.fda.gov/drugsatfda_docs/label/2018/021807s005lbl.pdf"
CPIC_GENE_URL = "https://cpicpgx.org/gene/CYP2D6/"
CKD_EPI_URL = "https://doi.org/10.1056/NEJMoa2102953"

# ---------------- CYP2D6 reference table ----------------
# Curated examples, not a complete clinical allele database.
# Activity values reflect the illustrative CPIC examples used below.
# The *10 and activity score 1.0 interpretation requires special handling.

DIPLOTYPES = {
    "Not tested / unknown": None,
    "*1/*1": 2.0,
    "*1/*2": 2.0,
    "*2/*2": 2.0,
    "*1/*4": 1.0,
    "*1/*5": 1.0,
    "*1/*10": 1.5,
    "*2/*10": 1.5,
    "*1/*9": 1.5,
    "*1/*41": 1.5,
    "*1/*10 (lab-confirmed activity score 1.0)": 1.0,
    "*10/*10": 1.0,
    "*4/*10": 0.5,
    "*4/*41": 0.5,
    "*5/*9": 0.5,
    "*4/*4": 0.0,
    "*4/*5": 0.0,
    "*5/*5": 0.0,
    "Other / complex / copy-number variant": None,
}

def infer_phenotype(diplotype, score):
    """Conservative interpretation for this curated teaching table."""
    if score is None or pd.isna(score):
        return "Unknown / requires lab interpretation"

    if score == 1.0:
        if "*10" in diplotype:
            return "Reduced activity; CPIC tamoxifen-specific interpretation"
        return "Activity score 1.0; interpretation may be allele-dependent"

    if score == 0:
        return "Poor metabolizer"
    if score <= 0.5:
        return "Intermediate metabolizer"
    if 1.5 <= score <= 2.0:
        return "Normal metabolizer"
    if score > 2.0:
        return "Ultrarapid metabolizer"

    return "Unknown / requires lab interpretation"


def crcl_cockcroft_gault(age, weight, scr, sex):
    """CrCl estimate in mL/min; requires clinical interpretation."""
    if age <= 0 or weight <= 0 or scr <= 0:
        return np.nan
    value = ((140 - age) * weight) / (72 * scr)
    if sex == "Female":
        value *= 0.85
    return value


def egfr_ckd_epi_2021(age, scr, sex):
    """2021 CKD-EPI creatinine equation, eGFR in mL/min/1.73m²."""
    if age <= 0 or scr <= 0:
        return np.nan

    if sex == "Female":
        k, alpha, factor = 0.7, -0.241, 1.012
    else:
        k, alpha, factor = 0.9, -0.302, 1.0

    return (
        142
        * min(scr / k, 1) ** alpha
        * max(scr / k, 1) ** (-1.200)
        * 0.9938 ** age
        * factor
    )


# ---------------- Layout / navigation ----------------

tabs = st.tabs([
    "Patient context",
    "PGx",
    "Drug interactions",
    "Labs & graphs",
    "Dose & duration evidence",
    "Pharmacovigilance",
    "Export & references",
])

# ---------------- TAB 1: PATIENT CONTEXT ----------------

with tabs[0]:
    st.header("Clinical context")

    c1, c2 = st.columns(2)

    with c1:
        scenario_id = st.text_input("Scenario ID", "DEMO-001")
        demo_data = st.checkbox("This is fictional demonstration data", True)

        age = st.number_input("Age (years)", 18, 110, 55)
        sex = st.selectbox("Sex coefficient used for equations", ["Female", "Male"])
        menopausal = st.selectbox(
            "Menopausal status",
            ["Unknown", "Premenopausal", "Perimenopausal", "Postmenopausal"],
        )
        weight = st.number_input("Weight (kg)", 1.0, 350.0, 65.0)
        scr = st.number_input(
            "Serum creatinine (mg/dL)", 0.1, 30.0, 1.0, step=0.1
        )

    with c2:
        intent = st.selectbox(
            "Treatment indication",
            [
                "Adjuvant treatment",
                "DCIS",
                "High-risk incidence reduction",
                "Metastatic disease",
                "Other / not confirmed",
            ],
        )
        histology = st.selectbox(
            "Histology",
            [
                "Invasive ductal carcinoma",
                "Invasive lobular carcinoma",
                "DCIS",
                "Other / unknown",
            ],
        )
        stage = st.selectbox(
            "Recorded stage", ["0", "I", "II", "III", "IV", "Unknown"]
        )
        metastasis = st.selectbox(
            "Distant metastasis", ["Unknown", "No", "Yes"]
        )
        tumour_size = st.number_input("Tumour size (cm)", 0.0, 30.0, 0.0)
        nodes = st.selectbox("Regional nodes", ["Unknown", "Negative", "Positive"])
        grade = st.selectbox("Grade", ["Unknown", "1", "2", "3"])

    st.markdown("### Tumour biomarkers")
    b1, b2, b3 = st.columns(3)
    er = b1.selectbox("ER status", ["Positive", "Negative", "Unknown"])
    pr = b2.selectbox("PR status", ["Positive", "Negative", "Unknown"])
    her2 = b3.selectbox(
        "HER2 status", ["Positive", "Negative", "Equivocal", "Unknown"]
    )

    st.markdown("### Treatment status")
    treatment_status = st.selectbox(
        "Tamoxifen status",
        [
            "Not started",
            "Currently taking",
            "Previously taken",
            "Unknown",
        ],
    )
    current_dose = st.selectbox(
        "Currently recorded daily dose",
        ["Unknown", "10 mg", "20 mg", "30 mg", "40 mg", "Other"],
    )
    treatment_start = st.date_input("Treatment start date", value=date.today())
    adherence = st.selectbox(
        "Reported adherence",
        ["Unknown", "Consistent", "Some missed doses", "Frequent missed doses"],
    )

    if er == "Negative":
        st.warning(
            "ER is recorded as negative. Verify the indication and pathology with "
            "the treating oncology team; the app does not determine eligibility."
        )
    elif er == "Unknown":
        st.info("ER status is unknown. Do not infer treatment eligibility from this field.")

# ---------------- TAB 2: PHARMACOGENOMICS ----------------

with tabs[1]:
    st.header("CYP2D6 pharmacogenomics")

    st.caption(
        "The diplotype list is a limited teaching subset, not a comprehensive "
        "clinical genotype interpreter. Confirm all results with the testing laboratory."
    )

    diplotype = st.selectbox("CYP2D6 diplotype", list(DIPLOTYPES.keys()))
    derived_score = DIPLOTYPES[diplotype]

    manual_score = st.selectbox(
        "Lab-reported activity score (if available)",
        [
            "Not reported",
            "0",
            "0.25",
            "0.5",
            "0.75",
            "1.0",
            "1.25",
            "1.5",
            "1.75",
            "2.0",
            "Greater than 2.0",
            "Other / complex",
        ],
    )

    if manual_score == "Not reported":
        activity_score = derived_score
        score_source = "Curated example table" if derived_score is not None else "Unavailable"
    elif manual_score == "Greater than 2.0":
        activity_score = 2.5
        score_source = "Entered from laboratory report"
    elif manual_score in ["Other / complex"]:
        activity_score = None
        score_source = "Requires laboratory interpretation"
    else:
        activity_score = float(manual_score)
        score_source = "Entered from laboratory report"

    phenotype = infer_phenotype(diplotype, activity_score)

    g1, g2 = st.columns(2)
    g1.metric(
        "Activity score",
        "Unknown" if activity_score is None else str(activity_score),
    )
    g2.metric("Phenotype interpretation", phenotype)

    st.caption(f"Score source: {score_source}")

    if activity_score == 1.0:
        st.warning(
            "Activity score 1.0 is not a simple universal category for tamoxifen. "
            "Allele identity matters, especially CYP2D6*10. Use the laboratory's "
            "validated phenotype and CPIC guidance rather than this label alone."
        )
    elif activity_score is None:
        st.info(
            "No reliable activity score can be inferred for this selection. "
            "The app will not guess the phenotype."
        )

    st.markdown("### Evidence interpretation")

    if phenotype == "Poor metabolizer":
        pgx_note = (
            "CPIC: lower endoxifen exposure is expected. Alternative endocrine therapy "
            "may be considered in the relevant clinical context. If alternatives are "
            "contraindicated, a higher tamoxifen dose is a clinician-considered option, "
            "not an automatic escalation."
        )
        st.warning(pgx_note)

    elif phenotype == "Intermediate metabolizer":
        pgx_note = (
            "CPIC: lower endoxifen exposure may occur. Review endocrine treatment options "
            "and CYP2D6-inhibiting medicines with the oncology team."
        )
        st.warning(pgx_note)

    elif phenotype == "Normal metabolizer":
        pgx_note = (
            "CPIC supports standard-of-care dosing and avoiding moderate/strong CYP2D6 "
            "inhibitors. The genotype does not prove a specific endoxifen concentration."
        )
        st.info(pgx_note)

    elif phenotype == "Ultrarapid metabolizer":
        pgx_note = (
            "CPIC supports standard-of-care dosing and avoiding moderate/strong CYP2D6 "
            "inhibitors. Do not increase or decrease the dose solely from this label."
        )
        st.info(pgx_note)

    else:
        pgx_note = (
            "PGx interpretation unresolved. Obtain or verify a validated laboratory "
            "report, including diplotype, copy-number status where relevant, and phenotype."
        )
        st.info(pgx_note)

    st.markdown(f"[Open CPIC guideline]({CPIC_URL})")

    st.markdown("### Optional measured endoxifen")
    endoxifen_value = st.text_input(
        "Laboratory-reported endoxifen concentration",
        placeholder="Leave blank if not measured",
    )
    endoxifen_unit = st.selectbox(
        "Reported unit", ["ng/mL", "nM", "Other / not recorded"]
    )
    endoxifen_date = st.date_input("Sample collection date", value=date.today())
    endoxifen_lab_range = st.text_input(
        "Laboratory-provided reference / interpretive range",
        placeholder="Enter the exact laboratory range and source, if supplied",
    )

    if endoxifen_value.strip():
        st.info(
            f"Recorded measured result: {endoxifen_value} {endoxifen_unit}; "
            f"sample date {endoxifen_date}."
        )
    else:
        st.caption("No measured endoxifen value entered; no concentration will be fabricated.")

    st.caption(
        "There is no universal endoxifen threshold that this prototype can safely use "
        "to select an individual's optimal dose. Record the assay, units and source."
    )

# ---------------- TAB 3: DRUG INTERACTIONS ----------------

with tabs[2]:
    st.header("Medication interaction screening")

    medication_catalogue = {
        "Paroxetine": (
            "CYP2D6 inhibitor",
            "Strong",
            "May reduce endoxifen formation; review alternatives with the prescriber.",
        ),
        "Fluoxetine": (
            "CYP2D6 inhibitor",
            "Strong",
            "May reduce endoxifen formation; review alternatives with the prescriber.",
        ),
        "Bupropion": (
            "CYP2D6 inhibitor",
            "Strong",
            "Potential to reduce endoxifen formation.",
        ),
        "Quinidine": (
            "CYP2D6 inhibitor",
            "Strong",
            "Potential to reduce CYP2D6-mediated metabolism.",
        ),
        "Terbinafine": (
            "CYP2D6 inhibitor",
            "Potential / context-dependent",
            "Review dose, duration and the complete medication list.",
        ),
        "Duloxetine": (
            "CYP2D6 inhibitor",
            "Moderate",
            "Review interaction and suitable alternatives with the prescriber.",
        ),
        "Sertraline": (
            "CYP2D6 inhibitor",
            "Variable",
            "Inhibition differs from strong inhibitors; review clinical context.",
        ),
        "Escitalopram": (
            "CYP2D6 inhibitor",
            "Lower than strong inhibitors",
            "Check current evidence and the clinical context before any change.",
        ),
        "Citalopram": (
            "CYP2D6 inhibitor",
            "Lower than strong inhibitors",
            "Check current evidence and the clinical context before any change.",
        ),
        "Rifampicin / rifampin": (
            "Enzyme inducer",
            "Important potential interaction",
            "May alter drug exposure; use a current interaction reference.",
        ),
        "Carbamazepine": (
            "Enzyme inducer",
            "Potential interaction",
            "Review the complete regimen with a pharmacist/clinician.",
        ),
        "Phenytoin": (
            "Enzyme inducer",
            "Potential interaction",
            "Review the complete regimen with a pharmacist/clinician.",
        ),
        "Warfarin": (
            "Other",
            "Clinically important review",
            "Potential anticoagulation interaction; monitoring may be required.",
        ),
        "Anastrozole": (
            "Endocrine therapy",
            "Treatment-context review",
            "Do not combine, stop or switch endocrine therapy from this screen alone.",
        ),
        "Letrozole": (
            "Endocrine therapy",
            "Treatment-context review",
            "Do not combine, stop or switch endocrine therapy from this screen alone.",
        ),
        "Exemestane": (
            "Endocrine therapy",
            "Treatment-context review",
            "Do not combine, stop or switch endocrine therapy from this screen alone.",
        ),
        "Other medicine": (
            "Unscreened",
            "Unknown",
            "Not covered by this limited built-in list.",
        ),
    }

    selected_medicines = st.multiselect(
        "Select current or recently used medicines",
        list(medication_catalogue.keys()),
    )

    extra_medicines = st.text_area(
        "Other medicines / supplements (manual review only)",
        placeholder="Enter names for the exported record; this field is not automatically screened.",
    )

    interaction_results = []
    for med in selected_medicines:
        mechanism, level, note = medication_catalogue[med]
        interaction_results.append({
            "Medicine": med,
            "Mechanism/category": mechanism,
            "Screening level": level,
            "Evidence note": note,
        })

    if interaction_results:
        interaction_df = pd.DataFrame(interaction_results)
        st.dataframe(interaction_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download interaction screen CSV",
            interaction_df.to_csv(index=False).encode("utf-8"),
            "interaction_screen.csv",
            "text/csv",
        )
    else:
        st.info("Select one or more medicines to run the built-in screen.")

    st.warning(
        "This is not a comprehensive interaction database. A flag is not proof of harm, "
        "and no flag is not proof of safety. Never stop or substitute medicines without "
        "the treating prescriber."
    )

# ---------------- TAB 4: LABS & GRAPHS ----------------

with tabs[3]:
    st.header("Laboratory reference ranges and renal estimates")

    st.markdown(
        "Enter the reporting laboratory's reference limits where available. "
        "Default values below are illustrative software defaults, not universal normal ranges."
    )

    lab_table = pd.DataFrame([
        {"Test": "ALT", "Value": 25.0, "Unit": "U/L", "Lower": 0.0, "Upper": 40.0},
        {"Test": "AST", "Value": 25.0, "Unit": "U/L", "Lower": 0.0, "Upper": 40.0},
        {"Test": "Total bilirubin", "Value": 1.0, "Unit": "mg/dL", "Lower": 0.0, "Upper": 1.2},
        {"Test": "Albumin", "Value": 4.0, "Unit": "g/dL", "Lower": 3.5, "Upper": 5.0},
        {"Test": "INR", "Value": 1.0, "Unit": "ratio", "Lower": 0.8, "Upper": 1.2},
    ])

    lab_table = st.data_editor(
        lab_table,
        num_rows="fixed",
        use_container_width=True,
        key="lab_editor",
        column_config={
            "Value": st.column_config.NumberColumn("Measured value"),
            "Lower": st.column_config.NumberColumn("Lab lower limit"),
            "Upper": st.column_config.NumberColumn("Lab upper limit"),
        },
    )

    def lab_flag(row):
        try:
            v = float(row["Value"])
            lo = float(row["Lower"])
            hi = float(row["Upper"])
        except (TypeError, ValueError):
            return "Invalid / missing"

        if not np.isfinite(v) or not np.isfinite(lo) or not np.isfinite(hi) or lo > hi:
            return "Invalid range / missing value"
        if v < lo:
            return "Below entered range"
        if v > hi:
            return "Above entered range"
        return "Within entered range"

    lab_table["Screening flag"] = lab_table.apply(lab_flag, axis=1)

    st.subheader("Laboratory review")
    st.dataframe(lab_table, hide_index=True, use_container_width=True)

    fig = px.bar(
        lab_table,
        x="Test",
        y="Value",
        color="Screening flag",
        title="Entered laboratory values",
        hover_data=["Unit", "Lower", "Upper"],
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "The bars display measured values in their original units. Because units differ, "
        "do not compare bar heights across different tests as if they were equivalent."
    )

    crcl = crcl_cockcroft_gault(age, weight, scr, sex)
    egfr = egfr_ckd_epi_2021(age, scr, sex)

    r1, r2 = st.columns(2)
    r1.metric("Cockcroft–Gault CrCl", "Unavailable" if np.isnan(crcl) else f"{crcl:.1f} mL/min")
    r2.metric("CKD-EPI 2021 eGFR", "Unavailable" if np.isnan(egfr) else f"{egfr:.1f} mL/min/1.73 m²")

    st.markdown(
        f"[CKD-EPI 2021 equation reference]({CKD_EPI_URL})"
    )
    st.caption(
        "CrCl and eGFR are different estimates with different units. Neither is a validated "
        "tamoxifen exposure model. Interpret with clinical context."
    )

# ---------------- TAB 5: DOSE & DURATION EVIDENCE ----------------

with tabs[4]:
    st.header("Guideline-based regimen reference")
    st.error(
        "This section shows published regimen references and PGx evidence. "
        "It does NOT select a best dose for an individual patient."
    )

    st.markdown("### Label-based reference regimen")

    if intent == "Adjuvant treatment":
        regimen = "Label reference: tamoxifen 20 mg/day; duration commonly 5–10 years depending on the oncology plan."
        regimen_reason = (
            "The product label lists 20 mg daily for adjuvant treatment and describes "
            "a 5–10-year treatment range. The appropriate duration depends on recurrence "
            "risk, tolerability, menopausal status, prior therapy and the treating team's plan."
        )
        source = FDA_URL

    elif intent == "DCIS":
        regimen = "Label reference: tamoxifen 20 mg/day for 5 years in the specified DCIS setting."
        regimen_reason = (
            "The label lists 20 mg daily for 5 years for DCIS. Confirm eligibility and "
            "the treatment plan with the oncology team."
        )
        source = FDA_URL

    elif intent == "High-risk incidence reduction":
        regimen = "Label reference: tamoxifen 20 mg/day for 5 years in the specified risk-reduction setting."
        regimen_reason = (
            "The label lists 20 mg daily for 5 years for reduction of breast cancer incidence "
            "in women at high risk. Individual eligibility and benefit–risk assessment are required."
        )
        source = FDA_URL

    elif intent == "Metastatic disease":
        regimen = "Label reference: tamoxifen 20–40 mg/day; doses above 20 mg/day are divided."
        regimen_reason = (
            "The product label describes 20–40 mg/day for metastatic breast cancer. "
            "This range is not an instruction to select or escalate a dose; oncology "
            "management and treatment context determine the regimen."
        )
        source = FDA_URL

    else:
        regimen = "No regimen summary can be selected because the indication is not confirmed."
        regimen_reason = (
            "Confirm diagnosis, indication, receptor status and treatment intent before "
            "using a regimen reference."
        )
        source = FDA_URL

    st.markdown(f"**Reference:** {regimen}")
    st.write(regimen_reason)
    st.markdown(f"[Source: product label]({source})")

    st.markdown("### PGx evidence note")

    if phenotype == "Normal metabolizer" or phenotype == "Ultrarapid metabolizer":
        pgx_recommendation = (
            "CPIC: standard-of-care dosing is recommended for the relevant phenotype "
            "and moderate/strong CYP2D6 inhibitors should be avoided where clinically feasible. "
            "This does not prove that an individual has adequate endoxifen exposure."
        )
        strength = "CPIC recommendation: strong for the applicable phenotype"

    elif phenotype == "Poor metabolizer":
        pgx_recommendation = (
            "CPIC recommends considering alternative endocrine therapy in the appropriate "
            "setting (for example, an aromatase inhibitor in postmenopausal patients, or an "
            "aromatase inhibitor with ovarian function suppression in premenopausal patients). "
            "If alternatives are contraindicated, 40 mg/day may be considered by the clinician. "
            "Higher dosing does not necessarily normalize endoxifen exposure."
        )
        strength = "CPIC: strong recommendation to consider alternative endocrine therapy"

    elif phenotype == "Intermediate metabolizer":
        pgx_recommendation = (
            "CPIC describes lower endoxifen exposure and supports considering alternative "
            "endocrine therapy in the appropriate setting. If alternatives are contraindicated, "
            "a clinician may consider the label-supported 40 mg/day option. Do not escalate automatically."
        )
        strength = "CPIC recommendation: moderate for relevant intermediate-metabolizer groups"

    else:
        pgx_recommendation = (
            "No phenotype-specific recommendation is generated because the genotype or "
            "activity-score interpretation is uncertain. Obtain a validated laboratory interpretation."
        )
        strength = "Not assigned — insufficient PGx information"

    st.markdown(f"**Evidence classification:** {strength}")
    st.write(pgx_recommendation)
    st.markdown(f"[Source: CPIC CYP2D6–tamoxifen guideline]({CPIC_URL})")

    st.markdown("### Required checks before any clinical decision")

    checks = [
        "Confirm diagnosis, stage, ER status and the actual indication.",
        "Verify the laboratory-reported CYP2D6 diplotype, activity score and phenotype.",
        "Review CYP2D6 inhibitors and other clinically relevant interactions.",
        "Review treatment adherence, tolerability, comorbidities and contraindications.",
        "Verify measured endoxifen only if a validated assay was performed; record its unit and source.",
        "Discuss treatment alternatives, duration and monitoring with the oncology team.",
    ]

    for check in checks:
        st.checkbox(check, key="check_" + str(checks.index(check)))

    st.info(
        "Research output: label regimen reference + PGx evidence note + checklist. "
        "The app does not calculate an individualised optimum, efficacy probability or toxicity probability."
    )

# ---------------- TAB 6: PHARMACOVIGILANCE ----------------

with tabs[5]:
    st.header("Session-only pharmacovigilance register")
    st.caption(
        "Do not enter names, phone numbers, hospital numbers or other identifying information."
    )

    if "pv_cases" not in st.session_state:
        st.session_state.pv_cases = []

    with st.form("pv_form", clear_on_submit=True):
        case_id = st.text_input("Case reference")
        drug = st.selectbox(
            "Suspected drug",
            ["Tamoxifen", "Other medicine", "Multiple medicines"],
        )
        event = st.text_input("Adverse event term")
        onset = st.date_input("Onset date", value=date.today())
        serious = st.selectbox(
            "Seriousness", ["Not assessed", "Non-serious", "Serious"]
        )
        outcome = st.selectbox(
            "Outcome",
            ["Unknown", "Recovered", "Recovering", "Not recovered", "Fatal", "Other"],
        )
        notes = st.text_area("De-identified notes")
        submitted = st.form_submit_button("Add case")

    if submitted:
        if not case_id.strip() or not event.strip():
            st.error("Case reference and event term are required.")
        else:
            st.session_state.pv_cases.append({
                "Case reference": case_id,
                "Scenario ID": scenario_id,
                "Suspected drug": drug,
                "Event": event,
                "Onset": str(onset),
                "Seriousness": serious,
                "Outcome": outcome,
                "Notes": notes,
            })
            st.success("Case added to this session.")

    if st.session_state.pv_cases:
        pv_df = pd.DataFrame(st.session_state.pv_cases)
        st.dataframe(pv_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download PV CSV",
            pv_df.to_csv(index=False).encode("utf-8"),
            "oncopgx_pv_register.csv",
            "text/csv",
        )

        if st.button("Clear session register"):
            st.session_state.pv_cases = []
            st.rerun()

    st.warning(
        "This register does not submit reports to regulators or hospitals and is not a "
        "persistent, validated pharmacovigilance system."
    )

# ---------------- TAB 7: EXPORT & REFERENCES ----------------

with tabs[6]:
    st.header("Export scenario and evidence")

    summary = {
        "Scenario ID": scenario_id,
        "Demo data": demo_data,
        "Age": age,
        "Sex equation coefficient": sex,
        "Menopausal status": menopausal,
        "Indication": intent,
        "Histology": histology,
        "Stage": stage,
        "Metastasis": metastasis,
        "Tumour size cm": tumour_size,
        "Nodes": nodes,
        "Grade": grade,
        "ER": er,
        "PR": pr,
        "HER2": her2,
        "Treatment status": treatment_status,
        "Current recorded dose": current_dose,
        "Treatment start": str(treatment_start),
        "Adherence": adherence,
        "CYP2D6 diplotype": diplotype,
        "Activity score": activity_score,
        "Activity score source": score_source,
        "Phenotype interpretation": phenotype,
        "CrCl mL/min": crcl,
        "eGFR mL/min/1.73m2": egfr,
        "Measured endoxifen": endoxifen_value or "Not entered",
        "Endoxifen unit": endoxifen_unit,
        "Endoxifen date": str(endoxifen_date),
        "Other medicines manual entry": extra_medicines,
        "Generated at": datetime.now().isoformat(timespec="minutes"),
    }

    summary_df = pd.DataFrame(
        [{"Field": k, "Value": str(v)} for k, v in summary.items()]
    )

    st.download_button(
        "Download scenario CSV",
        summary_df.to_csv(index=False).encode("utf-8"),
        f"{scenario_id}_scenario.csv",
        "text/csv",
    )

    report_lines = [
        "OncoPGx India — Research Scenario",
        "=" * 40,
        f"Generated: {datetime.now().isoformat(timespec='minutes')}",
        "",
        "IMPORTANT: Not a clinical prescription or validated decision-support output.",
        "",
        "SCENARIO",
    ]
    report_lines.extend(f"{k}: {v}" for k, v in summary.items())
    report_lines += [
        "",
        "EVIDENCE LINKS",
        f"CPIC tamoxifen guideline: {CPIC_URL}",
        f"Product label: {FDA_URL}",
        f"CPIC CYP2D6 resource: {CPIC_GENE_URL}",
        f"CKD-EPI 2021: {CKD_EPI_URL}",
        "",
        "LIMITATIONS",
        "No validated individual endoxifen prediction is implemented.",
        "No individualised dose or treatment duration is prescribed.",
        "PGx diplotype mapping covers only a limited subset.",
        "Medication screening is incomplete and requires professional review.",
        "Laboratory flags depend on entered reference limits.",
    ]
    report_text = "\n".join(report_lines)

    st.download_button(
        "Download scenario report TXT",
        report_text,
        f"{scenario_id}_report.txt",
        "text/plain",
    )

    st.subheader("Evidence sources")

    st.markdown(
        f"""
        - [CPIC CYP2D6–tamoxifen guideline](https://pmc.ncbi.nlm.nih.gov/articles/5931215/)
        - [CPIC CYP2D6 gene resource]({CPIC_GENE_URL})
        - [Tamoxifen product label]({FDA_URL})
        - [CKD-EPI 2021 creatinine equation]({CKD_EPI_URL})
        """
    )

    st.subheader("Development limitations")
    st.markdown(
        """
        1. CYP2D6 interpretation requires a comprehensive, versioned allele database,
           copy-number assessment where applicable, and validated phenotype translation.
        2. Drug interactions need a maintained evidence source and explicit evidence grading.
        3. Laboratory reference intervals should be supplied by the reporting laboratory.
        4. A clinically deployed dose-support model needs prospective/retrospective validation,
           calibration, audit logging, governance and qualified clinical oversight.
        5. No machine-learning model is trained or claimed in this prototype.
        """
    )

st.divider()
st.caption(
    "OncoPGx India • Educational research prototype • "
    "All clinical decisions remain with the qualified treating team."
)
