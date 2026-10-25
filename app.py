import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import json
import html
from datetime import datetime, date
from pathlib import Path

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False

st.set_page_config(
    page_title="OncoPGx | Tamoxifen CDSS",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = Path("oncopgx_records.sqlite3")

st.markdown("""
<style>
.stApp {
 background:
 radial-gradient(circle at 8% 2%, rgba(20,184,166,.13), transparent 28%),
 radial-gradient(circle at 92% 10%, rgba(59,130,246,.13), transparent 25%),
 linear-gradient(135deg,#07111f 0%,#0b1220 52%,#101827 100%);
 color:#edf4ff;
}
.block-container {padding-top:1.4rem;max-width:1500px}
.hero {
 padding:1.6rem;border-radius:20px;margin-bottom:1rem;
 background:linear-gradient(120deg,rgba(13,148,136,.22),rgba(37,99,235,.17),rgba(99,102,241,.12));
 border:1px solid rgba(94,234,212,.25);
}
.kicker {color:#5eead4;text-transform:uppercase;letter-spacing:.15em;font-size:.75rem;font-weight:800}
.panel {padding:1rem;border:1px solid rgba(148,163,184,.2);border-radius:14px;background:rgba(15,23,42,.72)}
.notice {padding:1rem;border-left:4px solid #f59e0b;border-radius:8px;background:rgba(120,53,15,.2)}
div[data-testid="stMetric"] {background:rgba(15,23,42,.7);border:1px solid rgba(148,163,184,.18);padding:.8rem;border-radius:12px}
[data-testid="stSidebar"] {background:rgba(5,12,24,.96)}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
 <div class="kicker">Pharmacogenomics · Clinical pharmacology · Research prototype</div>
 <h1>🧬 OncoPGx — Tamoxifen Clinical Review</h1>
 <p>Patient-linked pharmacology, CYP2D6 interpretation, interaction review,
 safety monitoring and tumor-board reporting.</p>
</div>
<div class="notice"><b>Research-use only:</b> This prototype is not a validated clinical prediction model
and does not prescribe treatment. Use de-identified/demo data only. Clinical decisions require
the treating oncology team and current guidelines.</div>
""", unsafe_allow_html=True)

CPIC_URL = "https://cpicpgx.org/guidelines/guideline-for-cyp2d6-and-tamoxifen-therapy/"
CPIC_PAPER = "https://pmc.ncbi.nlm.nih.gov/articles/PMC5931215/"

# ----------------------------- DATABASE ---------------------------------------
def db():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.execute("""CREATE TABLE IF NOT EXISTS snapshots(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_code TEXT, saved_at TEXT, data TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS adverse_events(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_code TEXT, event_date TEXT, event TEXT,
        severity TEXT, serious TEXT, suspected_drug TEXT, notes TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS followups(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_code TEXT, visit_date TEXT, adherence REAL,
        endoxifen REAL, toxicity TEXT, labs TEXT)""")
    con.commit()
    return con

con = db()

# --------------------------- CALCULATIONS -------------------------------------
def egfr_ckdepi_2021(age, sex, scr):
    """Adult CKD-EPI 2021 creatinine estimate; not for pediatric patients."""
    if age < 18 or scr <= 0 or sex not in ("Female", "Male"):
        return None
    female = sex == "Female"
    k = 0.7 if female else 0.9
    alpha = -0.241 if female else -0.302
    ratio = scr / k
    sex_factor = 1.012 if female else 1.0
    return 142 * min(ratio, 1)**alpha * max(ratio, 1)**(-1.2) * (0.9938**age) * sex_factor

def crcl_cockcroft_gault(age, weight, scr, sex):
    if age < 18 or scr <= 0 or sex not in ("Female", "Male"):
        return None
    value = ((140-age)*weight)/(72*scr)
    return value*0.85 if sex == "Female" else value

def pgx_guidance(phenotype):
    if phenotype == "Poor metabolizer (PM)":
        return ("CPIC guidance supports considering an alternative endocrine therapy that does not "
                "depend on CYP2D6, when clinically appropriate. If an aromatase inhibitor is used "
                "in a premenopausal patient, ovarian suppression may be required. A clinician may "
                "consider 40 mg/day tamoxifen in selected cases when an alternative is unsuitable; "
                "this is not an automatic dose instruction.")
    if phenotype == "Intermediate metabolizer (IM)":
        return ("Consider guideline-based endocrine alternatives in clinical context. Review CYP2D6 "
                "inhibitors, menopausal status and the oncology plan with the treating team.")
    if phenotype in ("Normal metabolizer (NM)", "Ultrarapid metabolizer (UM)"):
        return ("CPIC generally supports standard tamoxifen dosing, commonly 20 mg/day, for these "
                "phenotypes, subject to the indication, product label and treating team's plan.")
    return "Phenotype is unknown or indeterminate. Obtain and interpret a valid laboratory report before phenotype-specific recommendations."

def interaction_review(meds):
    strong = {
        "Paroxetine", "Fluoxetine", "Bupropion", "Quinidine"
    }
    moderate = {"Duloxetine", "Terbinafine", "Sertraline"}
    results = []
    for med in meds:
        if med in strong:
            results.append((med, "High-priority review",
                "Potentially important CYP2D6 inhibition may reduce endoxifen formation. Discuss suitable alternatives with the prescriber."))
        elif med in moderate:
            results.append((med, "Review",
                "Potential CYP2D6 inhibition; clinical relevance varies. Review the full medication list with a pharmacist/prescriber."))
        elif med == "Other medicine — review required":
            results.append((med, "Unclassified",
                "Exact medicine and regimen need review in a reliable interaction resource."))
    return results

# ------------------------------- SIDEBAR --------------------------------------
with st.sidebar:
    st.title("🗂️ Patient workspace")
    st.caption("Use a study code only. Do not enter names, addresses or hospital IDs.")
    patient_code = st.text_input("De-identified patient code", "DEMO-001")
    st.markdown("---")
    st.markdown(f"[CPIC guideline]({CPIC_URL})")
    st.markdown(f"[CPIC publication]({CPIC_PAPER})")

tabs = st.tabs([
    "👤 Patient profile",
    "🧪 Labs & PGx",
    "💊 Treatment & interactions",
    "📈 Pharmacology",
    "🛡️ Safety / PV",
    "🧾 Report",
    "🗃️ Patient records",
])

# --------------------------- PATIENT PROFILE ----------------------------------
with tabs[0]:
    st.subheader("Patient and cancer profile")
    c1,c2,c3 = st.columns(3)

    with c1:
        age = st.number_input("Age (years)", 18, 110, 55, key="age")
        sex = st.selectbox("Sex for calculation", ["Female","Male","Not specified"], key="sex")
        menopausal = st.selectbox("Menopausal status", [
            "Premenopausal","Perimenopausal / uncertain","Postmenopausal","Unknown"
        ], key="menopausal")
        height = st.number_input("Height (cm)", 100.0, 230.0, 160.0, key="height")
        weight = st.number_input("Weight (kg)", 25.0, 250.0, 65.0, key="weight")

    with c2:
        subtype = st.selectbox("Cancer subtype", [
            "Invasive ductal breast cancer","Invasive lobular breast cancer",
            "Other / unspecified breast cancer","Other cancer / not applicable"
        ], key="subtype")
        er = st.selectbox("ER status", ["Positive","Negative","Unknown"], key="er")
        pr = st.selectbox("PR status", ["Positive","Negative","Unknown"], key="pr")
        her2 = st.selectbox("HER2 status", ["Positive","Negative","Equivocal / pending","Unknown"], key="her2")
        stage = st.selectbox("Cancer stage", [
            "Stage 0","Stage I","Stage II","Stage III","Stage IV","Unknown"
        ], key="stage")

    with c3:
        mets = st.selectbox("Metastasis", [
            "No known distant metastasis","Distant metastasis present","Unknown"
        ], key="mets")
        disease = st.selectbox("Current disease status", [
            "New diagnosis / work-up","Active treatment","Adjuvant treatment",
            "Neoadjuvant treatment","Recurrent/progressive disease",
            "Stable disease","Remission / surveillance","Unknown"
        ], key="disease")
        treatment_status = st.selectbox("Tamoxifen status", [
            "Not started","Currently taking","Previously stopped","Planned / under consideration"
        ], key="treatment_status")
        start_date = st.date_input("Treatment start date", date.today(), key="start_date")

    clinical_notes = st.text_area("Clinical notes (de-identified)", key="clinical_notes")

    if er == "Negative":
        st.warning("ER-negative disease generally does not support tamoxifen as standard endocrine therapy. Confirm pathology and treatment rationale with oncology.")
    if stage == "Stage IV" or mets == "Distant metastasis present":
        st.info("Metastatic treatment selection requires current oncology guidelines, tumor biology and prior treatment history.")

# ----------------------------- LABS & PGX -------------------------------------
with tabs[1]:
    st.subheader("Laboratory data and pharmacogenomics")
    l1,l2 = st.columns(2)

    with l1:
        scr = st.number_input("Serum creatinine (mg/dL)", 0.1, 15.0, 0.9, 0.1, key="scr")
        ast = st.number_input("AST (U/L)", 0.0, 5000.0, 25.0, 1.0, key="ast")
        alt = st.number_input("ALT (U/L)", 0.0, 5000.0, 25.0, 1.0, key="alt")
        bilirubin = st.number_input("Total bilirubin (mg/dL)", 0.0, 30.0, 0.8, 0.1, key="bilirubin")
        albumin = st.number_input("Albumin (g/dL)", 0.0, 8.0, 4.0, 0.1, key="albumin")
        cbc = st.text_area("CBC / other laboratory results (include units and dates)", key="cbc")

        if sex != "Not specified":
            egfr = egfr_ckdepi_2021(age, sex, scr)
            crcl = crcl_cockcroft_gault(age, weight, scr, sex)
        else:
            egfr, crcl = None, None

        m1,m2 = st.columns(2)
        m1.metric("eGFR CKD-EPI 2021", f"{egfr:.1f}" if egfr is not None else "N/A",
                  help="mL/min/1.73 m²; adult estimate")
        m2.metric("CrCl Cockcroft–Gault", f"{crcl:.1f}" if crcl is not None else "N/A",
                  help="mL/min; weight selection requires clinical judgment")
        st.caption("These estimates are not interchangeable and do not independently determine tamoxifen dose.")

    with l2:
        alleles = st.selectbox("CYP2D6 diplotype", [
            "Not entered","*1/*1","*1/*2","*1/*4","*1/*10",
            "*4/*10","*4/*4","*10/*10","*1/*1xN","Other / lab report"
        ], key="alleles")
        phenotype = st.selectbox("Laboratory-reported phenotype", [
            "Unknown / not tested","Ultrarapid metabolizer (UM)",
            "Normal metabolizer (NM)","Intermediate metabolizer (IM)",
            "Poor metabolizer (PM)","Indeterminate / needs lab interpretation"
        ], key="phenotype")
        pgx_date = st.date_input("PGx report date", date.today(), key="pgx_date")
        activity_score = st.text_input("Activity score / lab interpretation", key="activity_score")
        measured_endoxifen = st.number_input(
            "Measured endoxifen (ng/mL; 0 = not entered)",
            min_value=0.0, max_value=1000.0, value=0.0, step=0.1, key="measured_endoxifen"
        )
        st.markdown("""
        <div class="panel"><b>PGx guardrail</b><br>
        Star alleles must be interpreted using the laboratory's methods, activity score and
        relevant structural/copy-number variants. This app does not call a genotype from DNA.</div>
        """, unsafe_allow_html=True)

    st.markdown("#### Guideline interpretation")
    st.info(pgx_guidance(phenotype))

# ---------------------- TREATMENT & INTERACTIONS ------------------------------
with tabs[2]:
    st.subheader("Treatment, adherence and interaction screen")
    t1,t2 = st.columns(2)
    with t1:
        dose = st.selectbox("Current/planned tamoxifen dose", [
            "Not applicable / not started","10 mg/day","20 mg/day",
            "40 mg/day","Other / verify prescription"
        ], key="dose")
        adherence = st.slider("Self-reported adherence (%)",0,100,90,5,key="adherence")
        missed = st.number_input("Missed doses in last 30 days",0,30,2,key="missed")
        comorbidities = st.multiselect("Relevant comorbidities / safety history", [
            "History of venous thromboembolism (DVT/PE)",
            "Endometrial pathology / abnormal uterine bleeding",
            "Liver disease","Visual symptoms / retinopathy",
            "Osteoporosis / fracture risk","Cardiovascular disease",
            "Other / review required"
        ], key="comorbidities")
        symptoms = st.multiselect("Current symptoms / possible adverse effects", [
            "Hot flashes","Vaginal symptoms","Abnormal uterine bleeding",
            "Leg swelling/pain or shortness of breath (urgent assessment)",
            "Visual symptoms","Mood/sleep symptoms","GI symptoms",
            "No symptoms reported","Other"
        ], key="symptoms")

    with t2:
        meds = st.multiselect("Concomitant medicines", [
            "None entered","Paroxetine","Fluoxetine","Bupropion","Quinidine",
            "Duloxetine","Terbinafine","Sertraline","Other medicine — review required"
        ], key="meds")
        other_meds = st.text_area("Other prescription / OTC medicines and supplements", key="other_meds")
        interaction_notes = st.text_area("Pharmacist / prescriber review notes", key="interaction_notes")

    interaction_results = interaction_review(meds)
    if not interaction_results:
        st.success("No selected medicine triggered this limited screen. This is not a complete interaction check.")
    for med,level,detail in interaction_results:
        if level == "High-priority review":
            st.error(f"**{level}: {med}.** {detail}")
        else:
            st.warning(f"**{level}: {med}.** {detail}")

    if adherence < 80 or missed >= 5:
        st.warning("Discuss adherence barriers with the care team. Do not double doses to compensate for missed doses.")
    if "History of venous thromboembolism (DVT/PE)" in comorbidities:
        st.warning("History of DVT/PE requires explicit clinical risk/benefit review.")
    if "Leg swelling/pain or shortness of breath (urgent assessment)" in symptoms:
        st.error("Potential urgent warning symptom selected. Seek prompt clinical assessment.")

# ----------------------------- PHARMACOLOGY -----------------------------------
with tabs[3]:
    st.subheader("Patient-linked pharmacology visuals")
    st.markdown("""
    <div class="notice"><b>Illustrative model only:</b> This prototype does not calculate validated
    patient-specific AUC, endoxifen concentration, recurrence probability or toxicity probability.
    Genotype alone cannot supply these outputs.</div>
    """, unsafe_allow_html=True)

    phenotype_factor = {
        "Ultrarapid metabolizer (UM)":1.15,
        "Normal metabolizer (NM)":1.0,
        "Intermediate metabolizer (IM)":0.70,
        "Poor metabolizer (PM)":0.35,
        "Unknown / not tested":1.0,
        "Indeterminate / needs lab interpretation":1.0
    }.get(phenotype,1.0)
    strong = {"Paroxetine","Fluoxetine","Bupropion","Quinidine"}
    moderate = {"Duloxetine","Terbinafine","Sertraline"}
    inhibitor_factor = 0.60 if any(m in strong for m in meds) else 0.80 if any(m in moderate for m in meds) else 1.0
    adherence_factor = adherence / 100
    relative_index = phenotype_factor * inhibitor_factor * adherence_factor

    q1,q2,q3,q4 = st.columns(4)
    q1.metric("Phenotype factor",f"{phenotype_factor:.2f}×")
    q2.metric("Inhibitor scenario",f"{inhibitor_factor:.2f}×")
    q3.metric("Adherence factor",f"{adherence_factor:.2f}×")
    q4.metric("Illustrative index",f"{relative_index:.2f}")

    if PLOTLY_OK:
        days = np.linspace(0,30,121)
        ref = 1-np.exp(-0.12*days)
        selected = relative_index*ref
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days,y=ref,mode="lines",name="Reference scenario"))
        fig.add_trace(go.Scatter(x=days,y=selected,mode="lines",name="Selected-input scenario",fill="tozeroy"))
        fig.update_layout(template="plotly_dark",height=400,
            title="Illustrative relative formation curve (arbitrary units)",
            xaxis_title="Illustrative time (days)",yaxis_title="Relative index — not concentration")
        st.plotly_chart(fig,use_container_width=True)
    else:
        st.line_chart(pd.DataFrame({
            "Reference scenario":np.linspace(0,1,31),
            "Selected-input scenario":np.linspace(0,relative_index,31)
        }))

    if measured_endoxifen > 0:
        st.metric("Entered measured endoxifen",f"{measured_endoxifen:.1f} ng/mL")
        st.caption("Interpret with sampling timing, assay, adherence and evidence; no automatic therapeutic classification is made.")
    else:
        st.info("No measured endoxifen result entered. No concentration or AUC has been fabricated.")

    st.markdown("""
    <div class="panel">
    <b>Mechanism</b><br>
    Tamoxifen → CYP2D6 contributes to endoxifen formation → endoxifen acts at estrogen receptors.
    CYP2D6 phenotype and inhibitors can affect endoxifen formation. Clinical response also depends
    on tumor biology, adherence, other treatments and patient context.
    </div>
    """, unsafe_allow_html=True)

# ---------------------------- SAFETY / PV -------------------------------------
with tabs[4]:
    st.subheader("Safety monitoring and adverse-event case log")
    st.caption("Local case log only—not a live global pharmacovigilance feed.")
    with st.form("ae_form",clear_on_submit=True):
        ev1,ev2 = st.columns(2)
        with ev1:
            event_date = st.date_input("Event date",date.today())
            event = st.selectbox("Adverse event",[
                "Hot flashes","Venous thromboembolism / suspected clot",
                "Abnormal uterine bleeding / endometrial event","Visual disturbance",
                "Hepatic event","Nausea / GI event","Other"
            ])
            severity = st.selectbox("Severity",["Not assessed","Mild","Moderate","Severe","Life-threatening"])
        with ev2:
            serious = st.selectbox("Seriousness",["Not assessed","Non-serious","Serious"])
            suspected_drug = st.text_input("Suspected medicine","Tamoxifen")
            ae_notes = st.text_area("Description, outcome and source (no identifiers)")
        submit_ae = st.form_submit_button("Save adverse-event record")
        if submit_ae:
            con.execute("""INSERT INTO adverse_events
                (patient_code,event_date,event,severity,serious,suspected_drug,notes)
                VALUES(?,?,?,?,?,?,?)""",
                (patient_code,event_date.isoformat(),event,severity,serious,suspected_drug,ae_notes))
            con.commit()
            st.success("Adverse-event record saved locally.")

    ae_df = pd.read_sql_query(
        "SELECT event_date,event,severity,serious,suspected_drug,notes FROM adverse_events WHERE patient_code=? ORDER BY event_date DESC",
        con,params=(patient_code,))
    if ae_df.empty:
        st.info("No adverse-event cases saved for this study code.")
    else:
        st.dataframe(ae_df,use_container_width=True,hide_index=True)
        st.download_button("Export case log CSV",ae_df.to_csv(index=False).encode(),
            file_name=f"{patient_code}_adverse_events.csv",mime="text/csv")

    st.info("A case log alone cannot establish causality or a statistical signal. Real PV analysis needs a defined data source, deduplication, case definitions, comparator terms and a prespecified method.")

# -------------------------------- REPORT ---------------------------------------
with tabs[5]:
    st.subheader("Tumor-board report")
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = f"""# OncoPGx — Tamoxifen Clinical Review

**Study code:** {patient_code}  
**Generated:** {report_time}  
**Status:** Research prototype; not a validated clinical decision system.

## Patient and cancer
- Age: {age}; sex for equations: {sex}; menopausal status: {menopausal}
- Cancer subtype: {subtype}
- ER / PR / HER2: {er} / {pr} / {her2}
- Stage: {stage}; metastasis: {mets}
- Disease status: {disease}
- Tamoxifen status: {treatment_status}; entered dose: {dose}

## Laboratory data
- Creatinine: {scr} mg/dL
- AST / ALT: {ast} / {alt} U/L
- Total bilirubin: {bilirubin} mg/dL; albumin: {albumin} g/dL
- eGFR CKD-EPI 2021: {f'{egfr:.1f} mL/min/1.73 m²' if egfr is not None else 'Not calculated'}
- CrCl Cockcroft-Gault: {f'{crcl:.1f} mL/min' if crcl is not None else 'Not calculated'}
- CBC / other labs: {cbc or 'Not entered'}

## Pharmacogenomics
- CYP2D6 diplotype: {alleles}
- Phenotype entered: {phenotype}
- Guideline context: {pgx_guidance(phenotype)}
- Measured endoxifen: {f'{measured_endoxifen:.1f} ng/mL' if measured_endoxifen > 0 else 'Not entered'}

## Treatment, adherence and interactions
- Adherence: {adherence}%; missed doses in last 30 days: {missed}
- Selected medicines: {', '.join(meds) if meds else 'None entered'}
- Other medicines/supplements: {other_meds or 'Not entered'}
- Comorbidities: {', '.join(comorbidities) if comorbidities else 'None entered'}
- Symptoms: {', '.join(symptoms) if symptoms else 'None entered'}
- Interaction review notes: {interaction_notes or 'Not entered'}

## Review flags
"""
    flags = []
    if er == "Negative":
        flags.append("ER-negative status: confirm pathology and endocrine treatment rationale.")
    if phenotype in ("Poor metabolizer (PM)","Intermediate metabolizer (IM)"):
        flags.append("CYP2D6 phenotype may affect endoxifen formation; review CPIC guidance and clinical context.")
    for med,level,detail in interaction_results:
        flags.append(f"{level}: {med} — {detail}")
    if "History of venous thromboembolism (DVT/PE)" in comorbidities:
        flags.append("History of DVT/PE requires explicit risk/benefit review.")
    if not flags:
        flags.append("No flag triggered by the limited rules in this prototype; not a comprehensive clearance.")
    report += "\n".join(f"- {x}" for x in flags)
    report += f"""

## Limitations and next steps
- No validated patient-specific AUC, endoxifen prediction, recurrence prediction, toxicity probability or autonomous dose selection is implemented.
- Confirm pathology, complete medication list, lab dates/units, PGx laboratory interpretation and current institutional guidance.
- Aromatase inhibitor selection depends on menopausal status, ovarian suppression, contraindications and cancer context.
- Treating oncologist and pharmacist must make final decisions.

## References
- CPIC CYP2D6 and Tamoxifen Therapy Guideline: {CPIC_URL}
- CPIC guideline publication: {CPIC_PAPER}
- Check current local oncology protocols and product information.
"""
    st.markdown(report)
    st.download_button("⬇️ Download report (Markdown)",report.encode(),
        file_name=f"{patient_code}_tumor_board_report.md",mime="text/markdown",use_container_width=True)

    html_report = f"""<!doctype html><html><head><meta charset="utf-8">
    <title>OncoPGx Report</title><style>body{{font-family:Arial;max-width:900px;margin:35px auto;line-height:1.5;color:#172033}}h1,h2{{color:#0f766e}}</style></head>
    <body><h1>OncoPGx Tumor-board Report</h1>
    <p><b>Research prototype:</b> Not a validated clinical decision system or prescription.</p>
    <pre style="white-space:pre-wrap;font-family:Arial">{html.escape(report)}</pre>
    <p>Use browser Print → Save as PDF to create a PDF copy.</p></body></html>"""
    st.download_button("⬇️ Download printable HTML report",html_report.encode(),
        file_name=f"{patient_code}_tumor_board_report.html",mime="text/html",use_container_width=True)

    if st.button("💾 Save current patient snapshot",type="primary"):
        snapshot = {
            "patient_code":patient_code,"saved_at":report_time,
            "age":age,"sex":sex,"menopausal":menopausal,"height_cm":height,"weight_kg":weight,
            "subtype":subtype,"ER":er,"PR":pr,"HER2":her2,"stage":stage,"metastasis":mets,
            "disease_status":disease,"treatment_status":treatment_status,"start_date":str(start_date),
            "creatinine":scr,"AST":ast,"ALT":alt,"bilirubin":bilirubin,"albumin":albumin,
            "eGFR":egfr,"CrCl":crcl,"CYP2D6_diplotype":alleles,"phenotype":phenotype,
            "activity_score":activity_score,"measured_endoxifen":measured_endoxifen,
            "dose":dose,"adherence":adherence,"missed_doses":missed,"medicines":meds,
            "comorbidities":comorbidities,"symptoms":symptoms,"clinical_notes":clinical_notes
        }
        con.execute("INSERT INTO snapshots(patient_code,saved_at,data) VALUES(?,?,?)",
            (patient_code,report_time,json.dumps(snapshot,default=str)))
        con.commit()
        st.success("Patient snapshot saved.")

# ----------------------------- PATIENT RECORDS -------------------------------
with tabs[6]:
    st.subheader("Saved patient snapshots and follow-up")
    st.caption("SQLite persistence depends on the hosting filesystem. For production, use managed persistent storage, authentication and access controls.")

    with st.form("followup_form",clear_on_submit=True):
        f1,f2 = st.columns(2)
        with f1:
            visit_date = st.date_input("Follow-up date",date.today())
            follow_adherence = st.slider("Adherence at follow-up (%)",0,100,90,5)
            follow_endoxifen = st.number_input("Measured endoxifen (ng/mL; 0 = not entered)",0.0,1000.0,0.0,0.1)
        with f2:
            follow_toxicity = st.text_area("Toxicity / patient-reported outcomes")
            follow_labs = st.text_area("Follow-up lab notes (units and dates)")
        submit_follow = st.form_submit_button("Save follow-up")
        if submit_follow:
            con.execute("""INSERT INTO followups
                (patient_code,visit_date,adherence,endoxifen,toxicity,labs)
                VALUES(?,?,?,?,?,?)""",
                (patient_code,visit_date.isoformat(),follow_adherence,
                 follow_endoxifen if follow_endoxifen > 0 else None,
                 follow_toxicity,follow_labs))
            con.commit()
            st.success("Follow-up saved.")

    snap_df = pd.read_sql_query(
        "SELECT id,patient_code,saved_at,data FROM snapshots WHERE patient_code=? ORDER BY id DESC",
        con,params=(patient_code,))
    if snap_df.empty:
        st.info("No saved snapshots yet. Save one from the Report tab.")
    else:
        st.dataframe(snap_df[["id","patient_code","saved_at"]],use_container_width=True,hide_index=True)
        snap_id = st.selectbox("Choose snapshot ID",snap_df["id"].tolist())
        row = snap_df[snap_df["id"] == snap_id].iloc[0]
        st.json(json.loads(row["data"]))
        st.download_button("Download snapshot JSON",row["data"].encode(),
            file_name=f"{patient_code}_snapshot_{snap_id}.json",mime="application/json")

    follow_df = pd.read_sql_query(
        "SELECT visit_date,adherence,endoxifen,toxicity,labs FROM followups WHERE patient_code=? ORDER BY visit_date",
        con,params=(patient_code,))
    if not follow_df.empty:
        st.markdown("#### Follow-up timeline")
        st.dataframe(follow_df,use_container_width=True,hide_index=True)
        if PLOTLY_OK:
            fig = px.line(follow_df,x="visit_date",y="adherence",markers=True,
                title="Self-reported adherence over time")
            fig.update_layout(template="plotly_dark",yaxis_title="Adherence (%)",yaxis_range=[0,100])
            st.plotly_chart(fig,use_container_width=True)
        st.download_button("Export follow-up CSV",follow_df.to_csv(index=False).encode(),
            file_name=f"{patient_code}_followups.csv",mime="text/csv")

st.markdown("---")
st.caption("OncoPGx Research Prototype · De-identified data only · Not for autonomous diagnosis, prescribing, emergency triage or validated toxicity prediction.")
