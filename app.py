
# app.py
# OncoPGx Tamoxifen: Clinical Decision-Support & Research Prototype
# Research/educational use only. NOT a prescribing or validated PK tool.

import io
import json
from datetime import date, datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="OncoPGx | Tamoxifen",
    page_icon="🧬",
    layout="wide",
)

# ------------------------- STYLING -------------------------

st.markdown("""
<style>
.block-container {padding-top: 1.4rem; padding-bottom: 2rem;}
.main-title {font-size: 2rem; font-weight: 750;}
.subtle {color: #64748b; font-size: 0.9rem;}
.section-card {
    border: 1px solid rgba(128,128,128,.28);
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🧬 OncoPGx — Tamoxifen Research Workbench</div>',
            unsafe_allow_html=True)
st.caption(
    "Patient assessment • Pharmacogenomics • Drug interactions • "
    "Toxicity monitoring • Exposure data • Evidence-based report"
)

st.warning(
    "RESEARCH PROTOTYPE — NOT FOR AUTONOMOUS CLINICAL DECISIONS. "
    "Do not start, stop, switch, or alter cancer treatment using this app alone. "
    "All treatment decisions require the treating oncology team's review."
)

# ------------------------- REFERENCES -------------------------

REFERENCES = {
    "CPIC CYP2D6–tamoxifen guideline":
        "https://pmc.ncbi.nlm.nih.gov/articles/5931215/",
    "CPIC recommendations table":
        "https://www.ncbi.nlm.nih.gov/books/NBK247013/table/tamoxifen.T.cpic_2018_dosing_recommendat/",
    "NCI breast cancer hormone therapy":
        "https://www.cancer.gov/types/breast/treatment/hormone-therapy",
    "FDA tamoxifen oral solution label":
        "https://www.accessdata.fda.gov/drugsatfda_docs/label/2018/021807s005lbl.pdf",
    "CKD-EPI 2021 eGFR equation":
        "https://doi.org/10.1056/NEJMoa2102953",
}

INTERACTIONS = {
    "Paroxetine": ("Strong CYP2D6 inhibitor",
                   "May reduce endoxifen formation; prescriber/pharmacist review."),
    "Fluoxetine": ("Strong CYP2D6 inhibitor",
                   "May reduce endoxifen formation; prescriber/pharmacist review."),
    "Bupropion": ("Strong CYP2D6 inhibitor",
                  "May reduce endoxifen formation; review indication and alternatives."),
    "Quinidine": ("Strong CYP2D6 inhibitor",
                  "Potential reduction in endoxifen formation."),
    "Terbinafine": ("CYP2D6 inhibitor",
                    "Potential interaction; verify current use and clinical relevance."),
    "Duloxetine": ("CYP2D6 inhibitor",
                   "Review interaction and potential alternatives with prescriber."),
    "Sertraline": ("CYP2D6 inhibition possible",
                   "Interaction strength depends on context; review with pharmacist."),
    "Escitalopram": ("Lower CYP2D6 inhibition than strong inhibitors",
                     "Review all medicines; do not assume zero interaction."),
    "Citalopram": ("Lower CYP2D6 inhibition than strong inhibitors",
                   "Review all medicines; do not assume zero interaction."),
    "Rifampicin": ("Enzyme induction",
                   "May alter drug exposure; specialist medication review required."),
    "Carbamazepine": ("Enzyme induction",
                      "May alter drug exposure; specialist medication review required."),
    "Phenytoin": ("Enzyme induction",
                  "May alter drug exposure; specialist medication review required."),
    "Warfarin": ("Potential clinically important interaction",
                 "Anticoagulation/bleeding monitoring and prescriber review."),
    "Anastrozole": ("Endocrine therapy combination/sequence",
                    "Confirm intended oncology regimen."),
    "Letrozole": ("Endocrine therapy combination/sequence",
                  "Confirm intended oncology regimen."),
    "Exemestane": ("Endocrine therapy combination/sequence",
                   "Confirm intended oncology regimen."),
    "Other / not listed": ("Needs manual review",
                           "Enter full medication name and verify with a pharmacist."),
}

SYMPTOM_LIST = [
    "Hot flashes / sweating",
    "Fatigue",
    "Nausea",
    "Joint pain",
    "Muscle pain",
    "Vaginal bleeding / discharge",
    "Menstrual changes",
    "Leg swelling / pain",
    "Chest pain / sudden breathlessness",
    "Visual changes",
    "Abdominal pain",
    "Jaundice / dark urine",
    "Unusual bruising / bleeding",
    "No symptoms reported",
]

# ------------------------- HELPERS -------------------------

def safe_float(value):
    try:
        x = float(value)
        return x if np.isfinite(x) else None
    except (TypeError, ValueError):
        return None


def cockcroft_gault(age, weight_kg, creatinine, sex):
    """Approximate CrCl in mL/min; requires appropriate weight selection."""
    if not all([age > 0, weight_kg > 0, creatinine > 0]):
        return None
    result = ((140 - age) * weight_kg) / (72 * creatinine)
    if sex == "Female":
        result *= 0.85
    return round(result, 1)


def ckd_epi_2021(creatinine, age, sex):
    """2021 CKD-EPI creatinine equation; eGFR in mL/min/1.73 m²."""
    if creatinine <= 0 or age <= 0:
        return None
    female = sex == "Female"
    k = 0.7 if female else 0.9
    alpha = -0.241 if female else -0.302
    ratio = creatinine / k
    result = (
        142
        * min(ratio, 1) ** alpha
        * max(ratio, 1) ** (-1.200)
        * (0.9938 ** age)
        * (1.012 if female else 1)
    )
    return round(result, 1)


def lab_status(value, low, high):
    if value is None:
        return "Missing"
    if value < low:
        return "Below entered range"
    if value > high:
        return "Above entered range"
    return "Within entered range"


def phenotype_from_activity(score, diplotype):
    if score is None:
        return "Unknown — activity score not supplied"
    if score == 0:
        return "Poor metabolizer"
    if score <= 1:
        if "*10" in diplotype:
            return "Reduced activity; *10-specific interpretation required"
        return "Intermediate/reduced activity; allele-specific interpretation required"
    if score <= 2:
        return "Normal metabolizer (verify diplotype and current CPIC translation)"
    return "Ultrarapid metabolizer (verify diplotype and current CPIC translation)"
