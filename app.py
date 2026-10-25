
import io
from datetime import date

import pandas as pd
import streamlit as st
import plotly.express as px


# --------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------
st.set_page_config(
    page_title="OncoPGx | Tamoxifen Research Workbench",
    page_icon="🧬",
    layout="wide",
)

st.title("🧬 OncoPGx — Tamoxifen Research Workbench")
st.caption(
    "Patient assessment • Pharmacogenomics • Drug interactions • "
    "Toxicity monitoring • Evidence-based research report"
)

st.warning(
    "RESEARCH PROTOTYPE — NOT FOR AUTONOMOUS CLINICAL DECISIONS. "
    "Do not start, stop, switch, or change cancer treatment using this app. "
    "All treatment decisions require review by the treating oncology team."
)

st.info(
    "This tool organizes user-entered clinical information. "
    "It does not diagnose disease, validate a prescription, predict a "
    "patient's actual endoxifen concentration, or replace clinical review."
)

# --------------------------------------------------
# REFERENCE LISTS
# --------------------------------------------------
CYP_PHENOTYPES = [
    "Unknown / not tested",
    "Poor metabolizer",
    "Intermediate metabolizer",
    "Normal metabolizer",
    "Rapid metabolizer",
    "Ultrarapid metabolizer",
    "Genotype available; phenotype not assigned",
]

CYP_INHIBITORS = {
    "Fluoxetine": "Strong CYP2D6 inhibitor",
    "Paroxetine": "Strong CYP2D6 inhibitor",
    "Bupropion": "Strong CYP2D6 inhibitor",
    "Quinidine": "Strong CYP2D6 inhibitor",
    "Duloxetine": "Moderate CYP2D6 inhibitor",
    "Mirabegron": "Moderate CYP2D6 inhibitor",
    "Sertraline": "Inhibition can be dose-dependent",
    "Citalopram": "Generally weaker CYP2D6 inhibition",
    "Escitalopram": "Generally weaker CYP2D6 inhibition",
}

# --------------------------------------------------
# PATIENT AND CLINICAL CONTEXT
# --------------------------------------------------
st.header("1. Patient and clinical context")

c1, c2, c3 = st.columns(3)

with c1:
    patient_code = st.text_input(
        "Research patient ID (avoid identifiable details)",
        value="P001",
    )
    age = st.number_input("Age (years)", 18, 110, 50)
    menopausal_status = st.selectbox(
        "Menopausal status",
        ["Unknown", "Premenopausal", "Perimenopausal", "Postmenopausal"],
    )

with c2:
    cancer_stage = st.selectbox(
        "Breast cancer context",
        [
            "Not specified",
            "Stage 0 / DCIS",
            "Stage I",
            "Stage II",
            "Stage III",
            "Stage IV / metastatic",
        ],
    )
    receptor_status = st.selectbox(
        "Hormone receptor status",
        [
            "Unknown",
            "ER-positive",
            "PR-positive only / other",
            "ER-positive and PR-positive",
            "Hormone receptor-negative",
        ],
    )
    treatment_intent = st.selectbox(
        "Treatment context",
        [
            "Not yet established",
            "Adjuvant treatment",
            "Neoadjuvant treatment",
            "Metastatic disease",
            "Risk reduction / prevention",
            "Other",
        ],
    )

with c3:
    treatment_status = st.selectbox(
        "Tamoxifen status",
        [
            "Not started — under consideration",
            "Currently taking",
            "Previously taken",
            "Temporarily held by clinical team",
            "Unknown",
        ],
    )
    treatment_start = st.date_input(
        "Start date, if known",
        value=None,
    )
    prescribed_daily_dose = st.selectbox(
        "Dose recorded in the prescription",
        [
            "Not available",
            "5 mg/day",
            "10 mg/day",
            "20 mg/day",
            "Other / verify prescription",
        ],
    )

weight = st.number_input(
    "Weight (kg), if available",
    min_value=0.0,
    max_value=350.0,
    value=0.0,
    step=0.5,
)

st.caption(
    "Treatment eligibility, dose and duration depend on indication, "
    "disease context, menopausal status, treatment history and the "
    "oncology team's assessment. This app does not determine eligibility."
)

# --------------------------------------------------
# PGX
# --------------------------------------------------
st.header("2. Pharmacogenomics — CYP2D6")

p1, p2 = st.columns(2)

with p1:
    cyp_genotype = st.text_input(
        "CYP2D6 genotype / diplotype",
        placeholder="Enter the laboratory-reported result, if available",
    )
    cyp_phenotype = st.selectbox(
        "Laboratory-reported phenotype",
        CYP_PHENOTYPES,
    )

with p2:
    pgx_source = st.selectbox(
        "Result source",
        [
            "Not tested / unknown",
            "Clinical laboratory report",
            "Research laboratory",
            "Published dataset",
            "Other",
        ],
    )
    pgx_notes = st.text_area(
        "PGx notes",
        placeholder=(
            "Allele calls, copy-number findings, test limitations, "
            "report date or interpretation notes"
        ),
    )

st.markdown(
    "**Interpretation note:** CYP2D6 contributes to conversion of "
    "tamoxifen into endoxifen. Genotype, phenotype, CYP2D6-inhibiting "
    "medicines, adherence and other factors may affect exposure. "
    "A genotype alone does not establish an individual's endoxifen "
    "concentration or guarantee treatment response."
)

# --------------------------------------------------
# CONCOMITANT MEDICINES
# --------------------------------------------------
st.header("3. Concomitant medicines and interaction review")

st.write(
    "Select medicines the patient reports taking. Confirm the full "
    "medication list, dose and timing with the clinical team."
)

medicine_options = sorted(CYP_INHIBITORS.keys())
selected_medicines = st.multiselect(
    "Medicines to screen for CYP2D6 interaction relevance",
    medicine_options,
)

other_medicines = st.text_area(
    "Other medicines, supplements and relevant substances",
    placeholder="Enter name, dose and frequency where known",
)

interaction_rows = []
for medicine in selected_medicines:
    interaction_rows.append(
        {
            "Medicine": medicine,
            "Reference note": CYP_INHIBITORS[medicine],
        }
    )

if interaction_rows:
    st.dataframe(
        pd.DataFrame(interaction_rows),
        use_container_width=True,
        hide_index=True,
    )
    st.warning(
        "Potential interaction flag only. Do not stop or change any "
        "medicine independently. A prescriber or pharmacist should "
        "review alternatives and the clinical context."
    )
else:
    st.write("No medicines selected in this screening list.")

# --------------------------------------------------
# LABS AND ORGAN FUNCTION
# --------------------------------------------------
st.header("4. Laboratory values and organ-function context")

l1, l2, l3 = st.columns(3)

with l1:
    scr = st.number_input(
        "Serum creatinine (mg/dL), if known",
        min_value=0.0,
        max_value=30.0,
        value=0.0,
        step=0.1,
    )
    egfr = st.number_input(
        "Reported eGFR (mL/min/1.73 m²)",
        min_value=0.0,
        max_value=200.0,
        value=0.0,
        step=0.1,
    )

with l2:
    alt = st.number_input(
        "ALT (U/L), if known",
        min_value=0.0,
        max_value=10000.0,
        value=0.0,
        step=1.0,
    )
    ast = st.number_input(
        "AST (U/L), if known",
        min_value=0.0,
        max_value=10000.0,
        value=0.0,
        step=1.0,
    )

with l3:
    bilirubin = st.number_input(
        "Total bilirubin (mg/dL), if known",
        min_value=0.0,
        max_value=100.0,
        value=0.0,
        step=0.1,
    )
    lab_date = st.date_input("Laboratory date", value=None)

other_labs = st.text_area(
    "Other relevant labs / clinical findings",
    placeholder="Enter value, unit, date and laboratory reference range",
)

st.caption(
    "Zero means 'not entered' in these fields, not a measured result. "
    "eGFR and creatinine require clinical interpretation with units, "
    "history and trends. Kidney values do not directly calculate a "
    "tamoxifen dose."
)

# --------------------------------------------------
# COMORBIDITIES AND RISK FACTORS
# --------------------------------------------------
st.header("5. Comorbidities and risk review")

risk_options = [
    "History of venous thromboembolism (DVT/PE)",
    "Current or recent immobility",
    "Liver disease",
    "History of stroke",
    "Abnormal uterine bleeding / endometrial concern",
    "Osteoporosis / fracture concern",
    "Cardiovascular risk factors",
    "Pregnancy possible / pregnancy-related concern",
    "Adherence difficulty",
    "Other significant comorbidity",
]

risk_flags = st.multiselect(
    "Relevant history or risk factors",
    risk_options,
)

risk_notes = st.text_area(
    "Additional comorbidity notes",
    placeholder="Add context, dates and clinician findings if available",
)

# --------------------------------------------------
# TOXICITY AND SYMPTOMS
# --------------------------------------------------
st.header("6. Toxicity and symptom monitoring")

symptoms = [
    "Hot flashes",
    "Fatigue",
    "Nausea",
    "Mood changes",
    "Joint or muscle symptoms",
    "Vaginal symptoms",
    "Abnormal uterine bleeding",
    "Leg swelling or pain",
    "Chest pain or shortness of breath",
    "Visual symptoms",
    "Other symptoms",
]

st.write(
    "Record patient-reported severity. These ratings are descriptive "
    "and are not a validated toxicity score."
)

symptom_rows = []
for symptom in symptoms:
    a, b = st.columns([2, 1])
    with a:
        st.write(symptom)
    with b:
        severity = st.selectbox(
            f"Severity — {symptom}",
            ["Not reported", "Mild", "Moderate", "Severe"],
            key=f"symptom_{symptom}",
            label_visibility="collapsed",
        )
    symptom_rows.append(
        {"Symptom": symptom, "Reported severity": severity}
    )

toxicity_df = pd.DataFrame(symptom_rows)
toxicity_df = toxicity_df[
    toxicity_df["Reported severity"] != "Not reported"
]

toxicity_notes = st.text_area(
    "Onset, duration, impact, adherence and clinician assessment",
)

if not toxicity_df.empty:
    severity_order = ["Mild", "Moderate", "Severe"]
    plot_df = toxicity_df[
        toxicity_df["Reported severity"].isin(severity_order)
    ].copy()

    if not plot_df.empty:
        fig = px.bar(
            plot_df,
            x="Symptom",
            y="Reported severity",
            color="Reported severity",
            category_orders={"Reported severity": severity_order},
            title="Patient-reported symptom severity",
        )
        fig.update_layout(xaxis_tickangle=-35)
        st.plotly_chart(fig, use_container_width=True)

st.error(
    "Urgent symptoms: new chest pain, sudden shortness of breath, "
    "one-sided leg swelling/pain, stroke-like symptoms, or severe "
    "bleeding need urgent medical assessment. Do not wait for this app "
    "to assess them."
)

# --------------------------------------------------
# EXPOSURE / EVIDENCE
# --------------------------------------------------
st.header("7. Exposure and evidence review")

st.write(
    "Tamoxifen exposure and endoxifen concentrations cannot be "
    "reliably calculated from CYP2D6 phenotype alone. This prototype "
    "does not generate a simulated concentration or a dose-response curve."
)

exposure_status = st.selectbox(
    "Endoxifen measurement status",
    [
        "Not measured",
        "Measured by a laboratory",
        "Published / external dataset value",
    ],
)

endoxifen_value = None
endoxifen_unit = "ng/mL"
endoxifen_date = None

if exposure_status != "Not measured":
    e1, e2 = st.columns(2)
    with e1:
        endoxifen_value = st.number_input(
            "Reported endoxifen value",
            min_value=0.0,
            max_value=100000.0,
            value=0.0,
            step=0.1,
        )
        endoxifen_unit = st.selectbox(
            "Reported unit",
            ["ng/mL", "nM", "Other — verify"],
        )
    with e2:
        endoxifen_date = st.date_input(
            "Measurement date",
            value=None,
            key="endoxifen_date",
        )

    st.caption(
        "Enter only a real reported value. Verify units, assay, sampling "
        "conditions and interpretation with the source laboratory or study."
    )

st.markdown("**Guideline / literature references for review**")
st.markdown(
    "- [CPIC guideline for CYP2D6 and tamoxifen therapy]"
    "(https://pmc.ncbi.nlm.nih.gov/articles/5931215/)"
)
st.markdown(
    "- [NCI: Hormone therapy for breast cancer]"
    "(https://www.cancer.gov/types/breast/treatment/hormone-therapy)"
)
st.markdown(
    "- [FDA tamoxifen prescribing information]"
    "(https://www.accessdata.fda.gov/drugsatfda_docs/label/2018/021807s005lbl.pdf)"
)

st.caption(
    "Confirm the latest guideline version, local prescribing information "
    "and applicability to the individual clinical situation."
)

# --------------------------------------------------
# CLINICIAN REVIEW
# --------------------------------------------------
st.header("8. Clinician review and plan")

review_status = st.selectbox(
    "Clinical review status",
    [
        "Not reviewed",
        "Pending oncology review",
        "Reviewed by treating team",
    ],
)

reviewer_notes = st.text_area(
    "Clinician / researcher notes",
    placeholder=(
        "Document evidence considered, unresolved questions, "
        "and the agreed follow-up plan"
    ),
)

follow_up = st.text_area(
    "Monitoring / follow-up plan",
    placeholder="Enter the plan agreed with the treating team",
)

st.subheader("Alternative treatment discussion")
st.write(
    "For discussion with the oncology team only; not a treatment "
    "recommendation generated by this app."
)

alternatives = st.multiselect(
    "Options the clinical team may consider reviewing",
    [
        "Continue current plan after clinical review",
        "Review interacting medicines with prescriber/pharmacist",
        "Review adherence and tolerability",
        "Discuss alternative endocrine therapy",
        "Review ovarian function / menopausal status",
        "Review guideline and indication",
        "Consider specialist PGx consultation",
        "Consider therapeutic drug monitoring if clinically appropriate",
    ],
)

alternative_notes = st.text_area(
    "Context for alternatives",
    placeholder=(
        "Record why options are being discussed and who will review them"
    ),
)

# --------------------------------------------------
# REPORT GENERATION
# --------------------------------------------------
st.header("9. Generate research report")

def show_value(value):
    if value is None or value == "":
        return "Not entered"
    return str(value)

report_lines = [
    "# OncoPGx — Tamoxifen Patient Assessment Report",
    "",
    "> RESEARCH PROTOTYPE — NOT FOR AUTONOMOUS CLINICAL DECISIONS.",
    "> This report does not prescribe treatment or replace oncology review.",
    "",
    "## 1. Patient and clinical context",
    f"- Research ID: {show_value(patient_code)}",
    f"- Age: {age} years",
    f"- Weight: {weight if weight > 0 else 'Not entered'} kg",
    f"- Menopausal status: {menopausal_status}",
    f"- Cancer stage: {cancer_stage}",
    f"- Receptor status: {receptor_status}",
    f"- Treatment intent: {treatment_intent}",
    f"- Tamoxifen status: {treatment_status}",
    f"- Recorded prescription: {prescribed_daily_dose}",
    f"- Treatment start date: {show_value(treatment_start)}",
    "",
    "## 2. Pharmacogenomics",
    f"- CYP2D6 genotype: {show_value(cyp_genotype)}",
    f"- Reported phenotype: {cyp_phenotype}",
    f"- Result source: {pgx_source}",
    f"- Notes: {show_value(pgx_notes)}",
    "",
    "## 3. Medicines",
    "- Selected CYP2D6 interaction-screen medicines: "
    + (", ".join(selected_medicines) if selected_medicines else "None entered"),
    f"- Other medicines: {show_value(other_medicines)}",
    "",
    "## 4. Laboratory values",
    f"- Serum creatinine: {scr if scr > 0 else 'Not entered'} mg/dL",
    f"- Reported eGFR: {egfr if egfr > 0 else 'Not entered'} mL/min/1.73 m²",
    f"- ALT: {alt if alt > 0 else 'Not entered'} U/L",
    f"- AST: {ast if ast > 0 else 'Not entered'} U/L",
    f"- Total bilirubin: {bilirubin if bilirubin > 0 else 'Not entered'} mg/dL",
    f"- Laboratory date: {show_value(lab_date)}",
    f"- Other labs: {show_value(other_labs)}",
    "",
    "## 5. Risk factors",
    "- " + ("\n- ".join(risk_flags) if risk_flags else "None entered"),
    f"- Notes: {show_value(risk_notes)}",
    "",
    "## 6. Patient-reported symptoms",
    toxicity_df.to_string(index=False) if not toxicity_df.empty
    else "No symptom severity entered.",
    f"- Additional notes: {show_value(toxicity_notes)}",
    "",
    "## 7. Endoxifen data",
    f"- Measurement status: {exposure_status}",
    f"- Value: {show_value(endoxifen_value)}",
    f"- Unit: {endoxifen_unit}",
    f"- Measurement date: {show_value(endoxifen_date)}",
    "- No concentration was estimated by this application.",
    "",
    "## 8. Review and follow-up",
    f"- Review status: {review_status}",
    f"- Reviewer notes: {show_value(reviewer_notes)}",
    f"- Follow-up plan: {show_value(follow_up)}",
    "- Options for discussion: "
    + (", ".join(alternatives) if alternatives else "None selected"),
    f"- Alternative-treatment context: {show_value(alternative_notes)}",
    "",
    "## Interpretation limitations",
    "- This report reflects manually entered information.",
    "- Interaction flags are screening prompts, not proof of a clinical interaction.",
    "- Missing values are not normal results.",
    "- No individualized dose, duration, eligibility or treatment switch is prescribed.",
    "- Final interpretation must be performed by the treating oncology team.",
    "",
    "## References",
    "- CPIC: CYP2D6 and tamoxifen therapy — https://pmc.ncbi.nlm.nih.gov/articles/5931215/",
    "- NCI: Hormone therapy — https://www.cancer.gov/types/breast/treatment/hormone-therapy",
    "- FDA tamoxifen label — https://www.accessdata.fda.gov/drugsatfda_docs/label/2018/021807s005lbl.pdf",
]

report_text = "\n".join(report_lines)

st.download_button(
    "📄 Download assessment report (.md)",
    data=report_text,
    file_name=f"OncoPGx_{patient_code or 'patient'}_report.md",
    mime="text/markdown",
    use_container_width=True,
)

if not toxicity_df.empty:
    csv_buffer = io.StringIO()
    toxicity_df.to_csv(csv_buffer, index=False)
    st.download_button(
        "📊 Download symptom data (.csv)",
        data=csv_buffer.getvalue(),
        file_name=f"OncoPGx_{patient_code or 'patient'}_symptoms.csv",
        mime="text/csv",
        use_container_width=True,
    )

with st.expander("View report before downloading"):
    st.markdown(report_text)

st.divider()
st.caption(
    "OncoPGx research workbench • Verify all entered information. "
    "Use synthetic or properly de-identified data for research demonstrations."
)
