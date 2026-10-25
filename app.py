import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date

st.set_page_config(page_title="OncoPGx | Tamoxifen Safe-Use Explorer", page_icon="🧬", layout="wide")
st.markdown("""
<style>
.stApp{background:#07111f;color:#eef5ff}
[data-testid="stSidebar"]{background:#0b1b2c}
[data-testid="stMetric"]{background:#102238;border:1px solid #29435d;padding:12px;border-radius:12px}
</style>""", unsafe_allow_html=True)

st.title("🧬 OncoPGx | Tamoxifen Safe-Use Explorer")
st.caption("Advanced pharmacology • Pharmacogenomics • Drug interactions • Pharmacovigilance")
st.error("RESEARCH / EDUCATION PROTOTYPE ONLY. Not validated for clinical use. It cannot determine individual safety, recommend a dose, or replace an oncologist/pharmacist. Never change medicines using this app.")

INTERACTIONS = {
"Paroxetine": ("Strong CYP2D6 inhibitor","May markedly inhibit CYP2D6-mediated endoxifen formation.","HIGH-PRIORITY REVIEW","Prescriber/pharmacist review; do not stop an antidepressant abruptly."),
"Fluoxetine": ("Strong CYP2D6 inhibitor","May markedly inhibit CYP2D6-mediated endoxifen formation; effects may persist due to long half-life.","HIGH-PRIORITY REVIEW","Prescriber/pharmacist review; do not stop or switch psychiatric medicine without a plan."),
"Bupropion": ("Strong CYP2D6 inhibitor","May reduce CYP2D6 activity and endoxifen formation.","HIGH-PRIORITY REVIEW","Prescriber/pharmacist review of alternatives and clinical context."),
"Quinidine": ("Strong CYP2D6 inhibitor","May substantially inhibit CYP2D6.","HIGH-PRIORITY REVIEW","Check indication and alternatives with prescriber/pharmacist."),
"Duloxetine": ("Moderate CYP2D6 inhibitor","May reduce CYP2D6 activity; relevance depends on dose and patient context.","REVIEW","Review with prescriber/pharmacist; do not change independently."),
"Terbinafine": ("CYP2D6 inhibitor","Can inhibit CYP2D6 and may affect tamoxifen activation.","REVIEW","Review indication, duration and alternatives with prescriber/pharmacist."),
"Sertraline": ("CYP2D6 inhibition varies","Generally less inhibitory than paroxetine/fluoxetine; context and dose matter.","CONTEXT-DEPENDENT REVIEW","Review full medicine list and clinical context."),
"Rifampicin / rifampin": ("Strong CYP3A4 inducer","Can reduce tamoxifen exposure; product labeling advises against strong CYP3A4 inducers.","HIGH-PRIORITY REVIEW","Prompt prescriber/pharmacist review."),
"Carbamazepine": ("Enzyme inducer","May alter exposure; verify the specific interaction with a current clinical resource.","REVIEW","Pharmacist/prescriber should verify current interaction information."),
"Phenytoin": ("Enzyme inducer","May alter exposure; verify the specific interaction with a current clinical resource.","REVIEW","Pharmacist/prescriber should verify current interaction information."),
"Warfarin": ("Anticoagulant interaction","Tamoxifen can increase anticoagulant effect and bleeding risk.","HIGH-PRIORITY REVIEW","Anticoagulation team/prescriber review; monitoring may be needed."),
"Anastrozole": ("Endocrine regimen overlap","Routine concurrent use with tamoxifen has not shown added benefit and is generally avoided in product labeling.","REGIMEN REVIEW","Confirm intended regimen with oncology team."),
"Letrozole": ("Endocrine regimen overlap","Concurrent use is not generally recommended in product labeling; combination efficacy is not established.","REGIMEN REVIEW","Confirm intended regimen with oncology team.")
}
PHENOTYPE = {
"Not tested / unknown":("Status unknown; do not infer genotype from symptoms or ancestry.","NCCN does not recommend routine CYP2D6 testing to select adjuvant endocrine therapy."),
"Normal metabolizer":("Expected CYP2D6 activity in normal range.","CPIC 2018: standard tamoxifen 20 mg/day; avoid moderate and strong CYP2D6 inhibitors."),
"Intermediate metabolizer":("Reduced CYP2D6 activity expected.","CPIC 2018 discusses endocrine alternatives in context and avoidance of CYP2D6 inhibitors; clinician must individualise."),
"Poor metabolizer":("Little or no CYP2D6 activity expected.","CPIC 2018 recommends considering alternative endocrine therapy; 40 mg/day is only a clinician-considered option in selected situations."),
"Ultrarapid metabolizer":("Higher-than-normal CYP2D6 activity expected.","CPIC 2018: standard tamoxifen 20 mg/day; avoid moderate and strong CYP2D6 inhibitors.")
}

st.sidebar.header("Scenario setup")
indication = st.sidebar.selectbox("Clinical context", [
    "ER/PR-positive breast cancer — adjuvant setting",
    "Metastatic hormone receptor-positive breast cancer",
    "Risk reduction / DCIS context", "Other / not specified"])
phenotype = st.sidebar.selectbox("CYP2D6 phenotype (from validated lab report)", list(PHENOTYPE.keys()))
menopause = st.sidebar.selectbox("Menopausal status", ["Unknown / not documented", "Premenopausal", "Postmenopausal", "Perimenopausal / uncertain"])
hr_status = st.sidebar.selectbox("Hormone receptor status", ["Positive (ER and/or PR)", "Negative", "Unknown / not documented"])
ai_contraindicated = st.sidebar.selectbox("Aromatase inhibitor (AI) suitability", ["Not assessed", "No known contraindication / may be considered", "AI contraindicated or not tolerated (clinician-confirmed)"])
selected_meds = st.sidebar.multiselect("Co-medications to screen", list(INTERACTIONS.keys()),
    help="Select medicines in a fictional scenario. List is not exhaustive.")
scenario = st.sidebar.text_input("Scenario label", "Demo case A")
st.sidebar.caption("Do not enter identifiable patient data.")

high = [m for m in selected_meds if INTERACTIONS[m][2] == "HIGH-PRIORITY REVIEW"]
review = [m for m in selected_meds if INTERACTIONS[m][2] in ("REVIEW","CONTEXT-DEPENDENT REVIEW","REGIMEN REVIEW")]
a,b,c,d = st.columns(4)
a.metric("Selected medicines",len(selected_meds))
b.metric("High-priority review flags",len(high))
c.metric("Other review flags",len(review))
d.metric("CYP2D6 status","Unknown" if phenotype=="Not tested / unknown" else phenotype)
if high:
    st.error("High-priority review prompt: "+", ".join(high)+". This is not an automatic contraindication or treatment instruction.")
elif review:
    st.warning("Potential interaction/regimen review: "+", ".join(review)+". Verify with current product information and a clinical pharmacist/prescriber.")
else:
    st.info("No listed interaction selected. This is NOT proof the full medication list is interaction-free or that treatment is safe.")

tabs = st.tabs(["🧬 Mechanism & PK/PGx","💊 Interaction checker","🛡️ Pharmacovigilance","📚 Standard vs modifications","📊 Live dashboard"])

with tabs[0]:
    st.subheader("Live mechanism explorer — multiple pathways")
    st.caption("Choose a mechanism below. The diagram, explanation and clinical relevance update live when you change the selection or scenario inputs.")

    MECHANISMS = {
        "1 · CYP2D6 pharmacogenomics": {
            "title": "CYP2D6 genotype → endoxifen formation",
            "description": "Tamoxifen undergoes metabolism to several metabolites. CYP2D6 contributes to formation of endoxifen, an active metabolite. Reduced-function alleles can reduce CYP2D6 activity; the diplotype and activity score must be interpreted using a validated laboratory report.",
            "nodes": [("Tamoxifen", "Parent drug", "#2563eb"), ("N-desmethyl tamoxifen", "Intermediate metabolite", "#0f766e"), ("Endoxifen", "Active metabolite", "#0f766e"), ("Clinical effect", "Not predicted by this diagram", "#475569")],
            "edges": [(0,1),(1,2),(2,3)],
            "modifier": "CYP2D6 diplotype / activity score",
            "effect": "May alter endoxifen formation. This diagram does not estimate an individual concentration or response.",
            "source": "CPIC tamoxifen–CYP2D6 guideline (2018); confirm current guideline and validated phenotype translation."
        },
        "2 · CYP2D6 inhibitor interaction": {
            "title": "Co-medication inhibits CYP2D6",
            "description": "Some medicines inhibit CYP2D6 and can reduce conversion toward endoxifen. The magnitude depends on the specific medicine, dose, duration, other drugs and patient context.",
            "nodes": [("Tamoxifen", "Parent drug", "#2563eb"), ("CYP2D6", "Metabolic enzyme", "#7c3aed"), ("Endoxifen", "Active metabolite", "#0f766e"), ("Potentially lower formation", "Qualitative only", "#b45309")],
            "edges": [(0,1),(1,2),(2,3)],
            "modifier": "CYP2D6-inhibiting co-medication",
            "effect": "Selected inhibitors trigger a medication-review prompt. Never stop or switch a prescribed medicine without the prescriber.",
            "source": "CPIC 2018; verify each interaction against current product information / a trusted interaction resource."
        },
        "3 · CYP3A4 induction": {
            "title": "Enzyme induction may alter tamoxifen exposure",
