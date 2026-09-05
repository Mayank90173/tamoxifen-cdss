import streamlit as st
import numpy as np
import pandas as pd
import json
import io
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# 1. Clean Page Config Setup
st.set_page_config(
    page_title="Zurich Pharmacology Command Center", 
    layout="wide"
)

st.title("🧬 Systems Pharmacology Diagnostic Matrix")
st.caption("H-Informatics Core | Lead Consultant: Dr. Mayank Virmani (PharmD, PV Scientist Portfolio)")

if 'patient_ledger' not in st.session_state:
    st.session_state.patient_ledger = []

# 2. Main Parameters Inputs Group
st.header("📋 1. Patient Parameters & Comorbidities")
col1, col2, col3 = st.columns(3)

with col1:
    pt_id = st.text_input("Patient System Hash ID", "ZRH-2026-9843X")
    age = st.slider("Age (Years)", 18, 100, 64)
    weight = st.slider("Weight (kg)", 35, 150, 82)
    gender = st.radio("Biological Configuration", ["Female", "Male"], horizontal=True)
    cyp2d6_profile = st.selectbox("CYP2D6 Genomic Architecture", [
        "*1xN/*1 (Ultra-rapid Metabolizer)",
        "*1/*1 (Normal Metabolizer)", 
        "*1/*10 (Intermediate Metabolizer)", 
        "*4/*4 (Poor Metabolizer)"
    ])
    er_status = st.radio("ERα Receptor Status", ["Positive Status", "Negative Status"], horizontal=True)

with col2:
    cyp2d6_inhibitor = st.selectbox("CYP2D6 Potent Inhibitors", [
        "None / Sub-clinical",
        "Paroxetine / Fluoxetine (Severe Invalidation)",
        "Bupropion / Quinidine (High Affinity Capture)",
        "Sertraline / Duloxetine (Moderate Saturation)"
    ])
    cyp3a4_modulator = st.selectbox("Secondary CYP3A4 Competitors", [
        "None / Normal Turnover",
        "Rifampicin (Extreme Induction Hazard)",
        "Ketoconazole (Clearance Suppression Matrix)"
    ])
    comorbidities = st.multiselect("Active Architectural Overlays", [
        "Deep Vein Thrombosis (DVT Cluster Risk)",
        "Endometrial Hyperplasia",
        "Non-Alcoholic Fatty Liver Disease (NAFLD)",
        "Severe Retinopathy"
    ], default=["Non-Alcoholic Fatty Liver Disease (NAFLD)"])

with col3:
    creatinine = st.number_input("Serum Creatinine (mg/dL)", min_value=0.2, max_value=12.0, value=1.40, step=0.05)
    serum_ast = st.number_input("Hepatic AST (U/L)", min_value=5, max_value=3000, value=145, step=5)
    serum_alt = st.number_input("Hepatic ALT (U/L)", min_value=5, max_value=3000, value=165, step=5)
    total_bilirubin = st.number_input("Total Bilirubin (mg/dL)", min_value=0.1, max_value=20.0, value=2.6, step=0.1)
    compliance = st.slider("MEMS Adherence Cap (%)", 10, 100, 85) / 100.0
    days_on_therapy = st.number_input("Duration Cycle Status (Days Active)", min_value=1, max_value=730, value=24)

# --- 3. PHARMACOLOGY COMPUTATION ENGINE ---
gender_multiplier = 0.85 if gender == "Female" else 1.0
calculated_crcl = round(((140 - age) * weight) / (72 * creatinine) * gender_multiplier, 1)
ke = 0.028 if calculated_crcl >= 60 else 0.045 if calculated_crcl >= 30 else 0.065

if "*4/*4" in cyp2d6_profile: base_flux = 7.2
elif "*1/*10" in cyp2d6_profile: base_flux = 13.8
elif "*1/*1" in cyp2d6_profile: base_flux = 24.5
else: base_flux = 34.0  

if "Paroxetine" in cyp2d6_inhibitor: base_flux *= 0.15 
elif "Bupropion" in cyp2d6_inhibitor: base_flux *= 0.30
elif "Sertraline" in cyp2d6_inhibitor: base_flux *= 0.65

if "Rifampicin" in cyp3a4_modulator: base_flux *= 0.45 
elif "Ketoconazole" in cyp3a4_modulator: base_flux *= 1.25 

if "Non-Alcoholic Fatty Liver Disease" in comorbidities: base_flux *= 0.80

hys_law_triggered = (serum_ast > 120 or serum_alt > 120) and (total_bilirubin > 2.0)
if hys_law_triggered: base_flux *= 0.35

calculated_endoxifen = round(base_flux * compliance * (1 - np.exp(-ke * days_on_therapy)), 2)
time_axis = list(range(1, 31))
kinetics_curve = [round(base_flux * compliance * (1 - np.exp(-ke * t)), 2) for t in time_axis]

# --- 4. CLINICAL DIRECTIVES ---
if "Negative Status" in er_status:
    clinical_directive = "TERMINATE ENDOCRINE PROTOCOL IMMEDIATELY"
    directive_notes = "Target ERα receptor architecture is entirely absent. Tamoxifen lacks biological efficacy."
    status_alert = st.error
elif hys_law_triggered or "Deep Vein Thrombosis (DVT Cluster Risk)" in comorbidities:
    clinical_directive = "CRITICAL MEDICAL SUSPENSION ORDERED"
    directive_notes = "🚨 IMMEDIATE SUSPENSION. Active Hy's Law parameters or severe thromboembolic indices met."
    status_alert = st.error
elif calculated_endoxifen < 5.97:
    clinical_directive = "SUB-THERAPEUTIC PHARMACOKINETIC SPECTRUM"
    directive_notes = f"Current concentration profile ({calculated_endoxifen} ng/mL) scales below the targeted 5.97 ng/mL threshold."
    status_alert = st.warning
else:
    clinical_directive = "OPTIMAL THERAPEUTIC MAINTENANCE STABILIZED"
    directive_notes = f"Steady-state target successfully achieved ({calculated_endoxifen} ng/mL)."
    status_alert = st.success

# --- 5. MAIN DISPLAY GRID ---
st.header("📊 2. Clinical Evaluation Panel")
m1, m2, m3 = st.columns(3)
m1.metric("Calculated Renal CrCl", f"{calculated_crcl} mL/min")
m2.metric("Steady-State Endoxifen", f"{calculated_endoxifen} ng/mL")
m3.metric("Minimum Therapeutic Cutoff", "5.97 ng/mL")

st.markdown("### Clinical Verdict Directive")
status_alert(f"**{clinical_directive}** — {directive_notes}")

# --- 6. PHARMACOKINETIC LIVE CHART ENGINE ---
st.header("📈 3. Projected 30-Day Simulation Array Curve")
fig = go.Figure()
fig.add_trace(go.Scatter(x=time_axis, y=kinetics_curve, mode='lines+markers', name='Accumulation Curve', line=dict(color='#10b981', width=3)))
fig.add_trace(go.Scatter(x=[1, 30], y=[5.97, 5.97], mode='lines', name='Therapeutic Target Floor', line=dict(color='#ef4444', dash='dash')))
fig.update_layout(xaxis_title="Days Since Dosing Start", yaxis_title="Plasma Level (ng/mL)", height=350)
st.plotly_chart(fig, use_container_width=True)

# --- 7. AUTOMATED DIETARY MATRIX ---
st.header("🥗 4. Tailored Patient-Specific Diet Blueprint")
dietary_matrix = []
fluid_target = max(1.5, round((weight * 30) / 1000, 1))

if "Deep Vein Thrombosis (DVT Cluster Risk)" in comorbidities:
    dietary_matrix.append("- **Vascular Focus:** Absolute exclusion of isolated Vitamin K supplements; tightly regulate uniform clean greens intake.")
if "Non-Alcoholic Fatty Liver Disease (NAFLD)" in comorbidities:
    dietary_matrix.append("- **Hepatic Protection Protocol:** Restrict processed clean sugars entirely to optimize cellular enzyme synthesis.")
if calculated_crcl < 45:
    dietary_matrix.append(f"- **Renal Clearance Fluid Control:** Limit total daily liquid ingestion to precisely **{fluid_target} Litres**.")
else:
    dietary_matrix.append(f"- **Standard Maintenance Hydration:** Target **{fluid_target} Litres** daily to assist normal phase II liver conjugation.")

if not dietary_matrix:
    dietary_matrix.append("- **Balanced Profile:** Standard clean Mediterranean dietary matrix to stabilize absorption metrics.")

final_diet_compiled = "\n".join(dietary_matrix)
st.markdown(final_diet_compiled)

# --- 8. SYSTEMATIC REPORTLAB PDF ENGINE ---
def generate_pdf_payload():
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#0f172a'))
    sec_style = ParagraphStyle('Sec', parent=styles['Heading2'], fontSize=11, textColor=colors.HexColor('#1e3a8a'))
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, leading=14)
    
    story = []
    story.append(Paragraph("<b>SWISS INSTITUTIONAL TRANSLATIONAL DISPATCH</b>", title_style))
    story.append(Paragraph(f"Patient ID HASH Tracker: {pt_id} | Signature: Dr. Mayank Virmani", styles['Normal']))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b>1. Diagnostics Parameters Narrative Summary:</b>", sec_style))
    summary_text = f"""
    • Patient Age Profile: {age} Years old.<br/>
    • Calculated Renal Clearance Value: {calculated_crcl} mL/min.<br/>
    • Microsomal Genotype Configuration: {str(cyp2d6_profile)}.<br/>
    • Steady State Metabolite Loading Vector: {calculated_endoxifen} ng/mL.<br/>
    • System Decision Assessment Vector: {clinical_directive}.
    """
    story.append(Paragraph(summary_text, body_style))
    
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>2. Tailored Diet Adaptation Instructions:</b>", sec_style))
    story.append(Paragraph(final_diet_compiled.replace('\n', '<br/>'), body_style))
    
    doc.build(story)
    return pdf_buffer.getvalue()

st.spacer = st.write("")
try:
    pdf_data = generate_pdf_payload()
    st.download_button(
        label="📥 DOWNLOAD SYSTEMATIC MEDICAL PHARMACOLOGY REPORT (PDF)",
        data=pdf_data,
        file_name=f"Pharmacology_Report_{pt_id}.pdf",
        mime="application/pdf"
    )
except Exception as e:
    st.error(f"PDF Compiler Error: {str(e)}")

# --- 9. PATIENT LEDGER RECORD ENGINE ---
st.header("🗄️ 5. Secure Vault Ledger Record System")
with st.form("ledger_commitment_form", clear_on_submit=True):
    notes_to_commit = st.text_area("Add Custom Clinical Directive Notes", "")
    submit_record = st.form_submit_button("🔒 LOCK RECORD PERMANENTLY")

if submit_record:
    record_payload = {
        "Patient ID Hash": pt_id,
        "CYP2D6 Profile": str(cyp2d6_profile),
        "Endoxifen Level (ng/mL)": calculated_endoxifen,
        "Renal CrCl (mL/min)": calculated_crcl,
        "Verdict": clinical_directive,
        "Observations Notes": notes_to_commit if notes_to_commit else "None"
    }
    st.session_state.patient_ledger.append(record_payload)
