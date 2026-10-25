
# app.py
# OncoPGx Advanced Research Workbench
# IMPORTANT: Research demonstration only; not validated for clinical use.

from __future__ import annotations

import io
import json
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from sklearn.metrics import (
    roc_curve, roc_auc_score, confusion_matrix,
    accuracy_score, precision_score, recall_score, f1_score,
    brier_score_loss
)

st.set_page_config(
    page_title="OncoPGx Advanced Workbench",
    page_icon="🧬",
    layout="wide",
)

# ------------------------- Styling -------------------------

st.markdown("""
<style>
.stApp {background:#0b1020;color:#edf2ff}
[data-testid="stSidebar"] {background:#111a30}
[data-testid="stMetric"] {
 background:#14213b;border:1px solid #304364;
 border-radius:12px;padding:12px
}
.hero {
 padding:22px;border-radius:16px;
 background:linear-gradient(120deg,#152d4d,#202344);
 border:1px solid #385175;margin-bottom:15px
}
.smallnote {font-size:0.85rem;color:#b5c3db}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>🧬 OncoPGx Advanced Research Workbench</h1>
<p>Pharmacogenomics • Tamoxifen TDM • Drug interactions •
Pharmacokinetics • Safety • Model evaluation</p>
<p class="smallnote">Research prototype — clinical validation pending</p>
</div>
""", unsafe_allow_html=True)

st.error(
    "NOT FOR CLINICAL DECISIONS. This application is an educational "
    "proof-of-concept, not a validated medical device. Simulated curves "
    "and synthetic model metrics are not patient evidence. No dosing "
    "recommendation or validated individual toxicity probability is produced."
)

# ------------------------- Helpers -------------------------

def simulate_tdm_curve(dose, cyp_factor, inhibitor_factor, adherence, times):
    """
    Illustrative curve only. This is NOT a validated population PK model.
    The factors are arbitrary demonstration parameters, not clinical estimates.
    """
    exposure_factor = (
        max(dose, 0.1) / 20.0
        * cyp_factor
        * inhibitor_factor
        * adherence
    )
    plateau = 22.0 * exposure_factor
    rate = 0.65
    return plateau * (1 - np.exp(-rate * times))


def safe_auc(y_true, y_score):
    if len(np.unique(y_true)) < 2:
        return None
    return roc_auc_score(y_true, y_score)


def make_chromatogram(sequence, seed=7):
    """Generate a synthetic teaching chromatogram, not real sequencing data."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0, len(sequence), len(sequence) * 100)
    colors = {"A": "#28c76f", "C": "#29a8ff",
              "G": "#ffbd3d", "T": "#ff5d73"}
    traces = {}
    for base in "ACGT":
        y = rng.normal(0.015, 0.008, len(x))
        for i, called in enumerate(sequence):
            center = i + 0.5 + rng.normal(0, 0.012)
            amplitude = rng.uniform(0.65, 1.0) if called == base else rng.uniform(0.01, 0.06)
            width = rng.uniform(0.025, 0.045)
            y += amplitude * np.exp(-((x - center) ** 2) / (2 * width ** 2))
        traces[base] = (x, np.clip(y, 0, None), colors[base])
    return traces


def make_report(data):
    return (
        "OncoPGx Advanced Research Workbench\n"
        "Research prototype — clinical validation pending\n\n"
        f"Generated: {datetime.now().astimezone().isoformat()}\n\n"
        + json.dumps(data, indent=2, ensure_ascii=False, default=str)
        + "\n\nLIMITATIONS\n"
        "- Synthetic chromatogram is not patient sequencing evidence.\n"
        "- Simulated PK curve is not a validated pharmacokinetic model.\n"
        "- A literature threshold is not a universal treatment target.\n"
        "- Synthetic model metrics do not represent clinical performance.\n"
        "- Drug interactions and safety checks are not exhaustive.\n"
        "- No dosing or treatment recommendation is generated.\n"
    )


# ------------------------- Sidebar -------------------------

st.sidebar.title("Research case setup")

case_id = st.sidebar.text_input("Pseudonymous case ID", "DEMO-001")
mode = st.sidebar.radio(
    "Workspace mode",
    ["Demonstration / simulated data", "Evaluate uploaded labelled data"],
)
drug = st.sidebar.selectbox(
    "Primary endocrine therapy",
    ["Tamoxifen", "Anastrozole", "Letrozole", "Exemestane", "Fulvestrant"],
)
age = st.sidebar.number_input("Age (years)", 18, 110, 52)
weight = st.sidebar.number_input("Weight (kg)", 25.0, 250.0, 65.0)
menopause = st.sidebar.selectbox(
    "Menopausal status",
    ["Premenopausal", "Perimenopausal", "Postmenopausal", "Unknown"],
)
dose = st.sidebar.selectbox("Recorded tamoxifen dose (mg/day)", [10, 20, 30, 40])
adherence = st.sidebar.slider(
    "Illustrative adherence factor",
    0.50, 1.00, 0.95, 0.05,
    help="Only changes the simulated curve; it is not a clinical adherence estimate."
)

st.sidebar.caption(
    "Use synthetic or appropriately de-identified research data only."
)

# ------------------------- PGx inputs -------------------------

tabs = st.tabs([
    "Overview",
    "DNA & CYP2D6",
    "TDM / PK",
    "Interaction engine",
    "Safety & labs",
    "Model evaluation",
    "Report & validation",
])

with tabs[0]:
    st.subheader("Research case overview")

    a, b, c, d = st.columns(4)
    a.metric("Case", case_id)
    b.metric("Medicine", drug)
    c.metric("Recorded dose", f"{dose} mg/day" if drug == "Tamoxifen" else "Not applicable")
    d.metric("Workspace", "Simulated" if mode.startswith("Demonstration") else "Evaluation")

    st.markdown("### Mechanistic workflow")

    st.graphviz_chart("""
    digraph pathway {
      rankdir=LR;
      graph [bgcolor="transparent"];
      node [shape=box, style="rounded,filled", color="#45658c",
            fillcolor="#182c49", fontcolor="white"];
      edge [color="#80b7e8", fontcolor="white"];
      G [label="CYP2D6 genotype"];
      P [label="Reported phenotype"];
      I [label="Concomitant inhibitors"];
      M [label="Tamoxifen metabolism"];
      E [label="Measured endoxifen"];
      S [label="Safety / clinical outcomes"];
      R [label="Oncologist review"];
      G -> P;
      P -> M;
      I -> M;
      M -> E;
      E -> R;
      S -> R;
    }
    """)

    st.info(
        "Genotype and medication interactions can affect endoxifen exposure. "
        "Measured concentration, adherence, assay context and clinical outcomes "
        "must be interpreted together. This diagram represents a research framework, "
        "not a validated causal or prediction model."
    )

    st.markdown("### Evidence anchors")
    st.markdown("""
    - [CPIC CYP2D6–tamoxifen guideline](https://pmc.ncbi.nlm.nih.gov/articles/PMC5931215/)
    - [Endoxifen TDM prospective study](https://pmc.ncbi.nlm.nih.gov/articles/PMC8975771/)
    - [TRIPOD+AI reporting guideline](https://www.bmj.com/content/385/bmj-2023-078378)
    """)

with tabs[1]:
    st.subheader("DNA fragment & CYP2D6 research interface")

    st.warning(
        "The displayed sequence and chromatogram are SYNTHETIC illustrations. "
        "They cannot identify a patient's allele, star allele, copy-number "
        "variation, genotype, or metabolizer phenotype."
    )

    seq = st.text_input(
        "Illustrative DNA sequence (A/C/G/T only)",
        "ATGCTACGTTAGCGATCGATGCTAGCTAGGCTAACG",
    ).upper().strip()

    if not seq or any(base not in "ACGT" for base in seq):
        st.error("Enter a non-empty sequence containing only A, C, G and T.")
    elif len(seq) > 150:
        st.error("For this illustrative display, use at most 150 bases.")
    else:
        st.markdown("#### DNA fragment")
        st.code("5' — " + " ".join(seq) + " — 3'", language="text")

        color_map = {"A": "#28c76f", "C": "#29a8ff",
                     "G": "#ffbd3d", "T": "#ff5d73"}
        dna_html = "".join(
            f'<span style="color:{color_map[b]};font-weight:800;'
            f'font-family:monospace;font-size:18px;margin-right:3px">{b}</span>'
            for b in seq
        )
        st.markdown(
            f'<div style="padding:12px;background:#111a30;'
            f'border-radius:10px;overflow-wrap:anywhere">{dna_html}</div>',
            unsafe_allow_html=True,
        )

        traces = make_chromatogram(seq)
        fig = go.Figure()
        for base, (x, y, color) in traces.items():
            fig.add_trace(go.Scatter(
                x=x, y=y, mode="lines", name=base,
                line=dict(color=color, width=1.7),
            ))
        fig.update_layout(
            title="Synthetic Sanger-style chromatogram",
            xaxis_title="Illustrative base position",
            yaxis_title="Synthetic signal intensity",
            template="plotly_dark",
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Reported CYP2D6 data")

    p1, p2 = st.columns(2)
    with p1:
        genotype = st.selectbox(
            "Reported genotype / diplotype",
            ["Unknown", "*1/*1", "*1/*4", "*4/*4", "*1/*10",
             "*10/*10", "*1/*5", "*5/*4", "Other / complex"],
        )
        phenotype = st.selectbox(
            "Reported phenotype",
            ["Unknown", "Poor metabolizer", "Intermediate metabolizer",
             "Normal metabolizer", "Ultrarapid metabolizer"],
        )
    with p2:
        pgx_source = st.selectbox(
            "Result source",
            ["Not available", "Clinical laboratory",
             "Research assay", "Published dataset", "Unverified manual entry"],
        )
        activity_score = st.text_input("Reported activity score (optional)", "")

    pgx_notes = st.text_area("Assay / allele / CNV notes", "")

    st.info(
        "Genotype and phenotype are stored independently. A real clinical workflow "
        "requires a validated assay, allele translation rules, copy-number review, "
        "and interpretation using current guidance."
    )

with tabs[2]:
    st.subheader("Tamoxifen TDM & pharmacokinetic visualization")

    st.markdown(
        "Enter a measured endoxifen result, or switch to the explicitly simulated "
        "curve for the research demonstration."
    )

    t1, t2, t3 = st.columns(3)
    with t1:
        tdm_mode = st.radio(
            "Curve source",
            ["Illustrative simulation", "Measured concentration data"],
        )
    with t2:
        threshold = st.number_input(
            "Reference line (nM)",
            min_value=1.0,
            max_value=50.0,
            value=16.0,
            step=0.5,
            help="Literature-derived reference for display, not a universal target.",
        )
    with t3:
        measured_unit = st.selectbox("Concentration unit", ["nM", "ng/mL"])

    st.caption(
        "The 16 nM threshold was used in published TDM research. It is not a "
        "universally established efficacy cutoff and should not drive dosing by itself."
    )

    measured_df = None

    if tdm_mode == "Illustrative simulation":
        cyp_factor = st.select_slider(
            "Demonstration enzyme-function parameter",
            options=[0.35, 0.55, 0.75, 1.0, 1.15],
            value=1.0,
            help="Arbitrary simulation parameter, not a validated phenotype conversion.",
        )
        inhibitor_factor = st.select_slider(
            "Demonstration interaction parameter",
            options=[0.35, 0.55, 0.75, 0.9, 1.0],
            value=1.0,
            help="Arbitrary visual parameter; not a quantitative drug interaction estimate.",
        )

        times = np.linspace(0, 12, 120)
        curve = simulate_tdm_curve(
            dose, cyp_factor, inhibitor_factor, adherence, times
        )

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=times, y=curve, mode="lines",
            name="Simulated endoxifen",
            line=dict(color="#54b9ff", width=3),
        ))
        fig.add_hline(
            y=threshold,
            line_dash="dash",
            annotation_text=f"Reference line: {threshold:g} nM",
        )
        fig.update_layout(
            title="Illustrative concentration-time curve — NOT a validated PK model",
            xaxis_title="Illustrative time (arbitrary months)",
            yaxis_title="Simulated concentration (nM)",
            template="plotly_dark",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "This curve is generated from arbitrary teaching parameters. "
            "It must not be used to predict a patient's concentration or select a dose."
        )

    else:
        st.markdown("Upload measured serial TDM data as a CSV with columns:")
        st.code("time_months,endoxifen_nM", language="text")
        uploaded_tdm = st.file_uploader(
            "Measured TDM CSV",
            type=["csv"],
            key="tdm_upload",
        )
        if uploaded_tdm:
            try:
                measured_df = pd.read_csv(uploaded_tdm)
                required = {"time_months", "endoxifen_nM"}
                if not required.issubset(measured_df.columns):
                    st.error("CSV must include time_months and endoxifen_nM.")
                    measured_df = None
                else:
                    measured_df = measured_df.dropna(
                        subset=["time_months", "endoxifen_nM"]
                    )
                    fig = px.line(
                        measured_df.sort_values("time_months"),
                        x="time_months", y="endoxifen_nM",
                        markers=True,
                        title="Uploaded measured endoxifen data",
                    )
                    fig.add_hline(
                        y=threshold, line_dash="dash",
                        annotation_text=f"Reference line: {threshold:g} nM",
                    )
                    fig.update_layout(
                        xaxis_title="Time (months)",
                        yaxis_title="Measured endoxifen (nM)",
                        template="plotly_dark",
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(measured_df, use_container_width=True)
            except Exception as exc:
                st.error(f"Unable to read CSV: {exc}")

    st.markdown("#### Record a single measured concentration")
    m1, m2, m3 = st.columns(3)
    with m1:
        measured_conc = st.number_input(
            "Measured endoxifen (nM)",
            min_value=0.0, max_value=500.0, value=0.0, step=0.5,
        )
    with m2:
        sample_month = st.number_input(
            "Sample time (months)", min_value=0.0, max_value=120.0,
            value=3.0, step=0.5,
        )
    with m3:
        assay_name = st.text_input("Assay / laboratory", "Not entered")

    if measured_conc > 0:
        if measured_conc < threshold:
            st.warning(
                "Measured value is below the selected reference line. "
                "Review sample timing, adherence, interacting medicines, assay "
                "details and clinical context with the treating team."
            )
        else:
            st.info(
                "Measured value is at or above the selected reference line. "
                "This does not independently establish treatment efficacy or safety."
            )

    st.markdown("#### Factors to review when interpreting exposure")
    st.write(
        "CYP2D6 result • CYP2D6 inhibitors • adherence • dose history • "
        "time on treatment • sample timing • assay method • liver function • "
        "other relevant clinical factors."
    )

with tabs[3]:
    st.subheader("Drug interaction & mechanism engine")

    medicines = [
        "None entered", "Paroxetine", "Fluoxetine", "Bupropion",
        "Quinidine", "Duloxetine", "Escitalopram", "Citalopram",
        "Sertraline", "Venlafaxine", "Rifampin", "Warfarin",
        "Apixaban", "Rivaroxaban", "Clopidogrel", "Other",
    ]
    selected = st.multiselect(
        "Concomitant medicines",
        medicines,
        default=["None entered"],
    )

    interaction_info = {
        "Paroxetine": (
            "Strong CYP2D6 inhibition",
            "Can reduce formation of endoxifen",
            "Verify whether a suitable alternative is clinically appropriate.",
        ),
        "Fluoxetine": (
            "Strong CYP2D6 inhibition",
            "Can reduce formation of endoxifen",
            "Verify whether a suitable alternative is clinically appropriate.",
        ),
        "Bupropion": (
            "Clinically important CYP2D6 inhibition",
            "May reduce CYP2D6-mediated metabolism",
            "Check current prescribing information and clinical context.",
        ),
        "Quinidine": (
            "Strong CYP2D6 inhibition",
            "May reduce CYP2D6-mediated metabolite formation",
            "Check current prescribing information and clinical context.",
        ),
        "Duloxetine": (
            "CYP2D6 inhibition",
            "Potential reduction in endoxifen formation",
            "Review dose, indication, alternatives and evidence.",
        ),
        "Escitalopram": (
            "Generally less CYP2D6 inhibition than strong inhibitors",
            "Effect differs from strong CYP2D6 inhibitors",
            "Review the complete medication context.",
        ),
        "Citalopram": (
            "Generally less CYP2D6 inhibition than strong inhibitors",
            "Effect differs from strong CYP2D6 inhibitors",
            "Review the complete medication context.",
        ),
        "Sertraline": (
            "CYP2D6 inhibition varies",
            "Magnitude depends on context",
            "Review the complete medication context.",
        ),
        "Venlafaxine": (
            "Generally less CYP2D6 inhibition than strong inhibitors",
            "Not equivalent to strong CYP2D6 inhibitors",
            "Review indication and full medication list.",
        ),
        "Rifampin": (
            "Enzyme induction",
            "May alter exposure to multiple medicines",
            "Use a current authoritative interaction reference.",
        ),
        "Warfarin": (
            "Potential anticoagulation interaction / safety concern",
            "Not a CYP2D6 endoxifen alert",
            "Review coagulation monitoring and current prescribing information.",
        ),
        "Apixaban": (
            "Anticoagulant safety review",
            "Not a CYP2D6 endoxifen alert",
            "Review bleeding risk and relevant interaction pathways.",
        ),
        "Rivaroxaban": (
            "Anticoagulant safety review",
            "Not a CYP2D6 endoxifen alert",
            "Review bleeding risk and relevant interaction pathways.",
        ),
        "Clopidogrel": (
            "Potential interaction considerations",
            "Not directly interpreted by this simplified engine",
            "Verify with a current authoritative resource.",
        ),
        "Other": (
            "Medicine not specified",
            "No assessment possible",
            "Enter the exact medicine and verify independently.",
        ),
    }

    rows = []
    for med in selected:
        if med in interaction_info:
            mechanism, effect, action = interaction_info[med]
            rows.append({
                "Medicine": med,
                "Mechanism category": mechanism,
                "Potential effect": effect,
                "Review prompt": action,
            })

    if rows:
        interaction_df = pd.DataFrame(rows)
        st.dataframe(interaction_df, use_container_width=True, hide_index=True)
    else:
        interaction_df = pd.DataFrame(
            columns=["Medicine", "Mechanism category", "Potential effect", "Review prompt"]
        )
        st.info("No medicine-specific screening rows selected.")

    st.markdown("#### Mechanistic pathway")
    st.graphviz_chart("""
    digraph interactions {
      rankdir=TB;
      graph [bgcolor="transparent"];
      node [shape=box, style="rounded,filled", color="#45658c",
            fillcolor="#182c49", fontcolor="white"];
      edge [color="#80b7e8", fontcolor="white"];
      T [label="Tamoxifen"];
      N [label="N-desmethyl tamoxifen"];
      C [label="CYP2D6"];
      E [label="Endoxifen"];
      G [label="CYP2D6 genetic function"];
      I [label="CYP2D6-inhibiting co-medication"];
      T -> N [label="main pathway"];
      N -> C;
      C -> E [label="bioactivation"];
      G -> C [label="genetic effect"];
      I -> C [label="inhibition"];
    }
    """)

    st.warning(
        "This is a limited screening prototype, not a comprehensive interaction "
        "database. No alert does not mean a combination is safe. All alerts need "
        "verification against current prescribing information and clinical references."
    )

with tabs[4]:
    st.subheader("Safety and laboratory review")

    st.caption(
        "Record observations and trends. The prototype does not diagnose toxicity "
        "or calculate a validated individual risk score."
    )

    labs = {}
    cols = st.columns(3)
    for i, (name, unit, default, maximum) in enumerate([
        ("AST", "U/L", 25.0, 10000.0),
        ("ALT", "U/L", 25.0, 10000.0),
        ("Bilirubin", "mg/dL", 0.8, 100.0),
        ("Platelets", "×10⁹/L", 250.0, 3000.0),
        ("Hemoglobin", "g/dL", 12.5, 30.0),
        ("Creatinine", "mg/dL", 0.9, 30.0),
    ]):
        with cols[i % 3]:
            labs[name] = st.number_input(
                f"{name} ({unit})", min_value=0.0,
                max_value=maximum, value=default, step=0.1,
                key=f"lab_{name}",
            )

    h1, h2 = st.columns(2)
    with h1:
        vte_history = st.selectbox(
            "VTE / DVT / pulmonary embolism history",
            ["Unknown", "No", "Yes"],
        )
        liver_history = st.selectbox(
            "Liver disease history", ["Unknown", "No", "Yes"]
        )
    with h2:
        endometrial_history = st.selectbox(
            "Relevant endometrial history",
            ["Unknown", "No", "Yes", "Not applicable"],
        )
        adverse_event = st.selectbox(
            "Treatment-related adverse event",
            ["Unknown", "No", "Yes"],
        )

    lab_df = pd.DataFrame({
        "Lab": list(labs.keys()),
        "Entered value": list(labs.values()),
    })
    fig = px.bar(
        lab_df, x="Lab", y="Entered value",
        title="Entered laboratory values (different units)",
    )
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Different laboratory units must not be compared by bar height. "
        "Use laboratory-specific reference ranges, trends and clinical context."
    )

    st.info(
        "Tamoxifen requires attention to relevant thromboembolic and endometrial "
        "precautions. This checklist does not calculate an individual's risk and "
        "does not replace clinical assessment."
    )

with tabs[5]:
    st.subheader("Model performance and validation")

    st.markdown("""
    For a real model, upload a held-out evaluation dataset with:
    - `y_true`: observed binary outcome (0/1)
    - `y_score`: model-predicted probability for the positive outcome (0–1)

    Do not evaluate on the same cases used to train or tune the model.
    """)

    if mode.startswith("Demonstration"):
        st.warning(
            "DEMO ONLY: the following metrics come from a synthetic teaching "
            "dataset. They do not represent a trained or clinically validated "
            "toxicity model. Do not report them as research findings."
        )

        rng = np.random.default_rng(42)
        n = 250
        y_true = rng.binomial(1, 0.30, n)
        y_score = np.clip(
            rng.normal(0.68, 0.18, n) * y_true
            + rng.normal(0.28, 0.18, n) * (1 - y_true),
            0.001, 0.999
        )
        evaluation_df = pd.DataFrame({
            "y_true": y_true,
            "y_score": y_score,
        })
        source_label = "Synthetic demonstration data"
    else:
        uploaded_eval = st.file_uploader(
            "Upload held-out evaluation CSV",
            type=["csv"],
            key="eval_upload",
        )
        evaluation_df = None
        source_label = "Uploaded evaluation dataset"

        if uploaded_eval:
            try:
                candidate = pd.read_csv(uploaded_eval)
                if {"y_true", "y_score"}.issubset(candidate.columns):
                    candidate = candidate.dropna(subset=["y_true", "y_score"])
                    if (
                        len(candidate) > 0
                        and candidate["y_true"].isin([0, 1]).all()
                        and candidate["y_score"].between(0, 1).all()
                    ):
                        evaluation_df = candidate
                    else:
                        st.error(
                            "y_true must contain only 0/1 and y_score must be between 0 and 1."
                        )
                else:
                    st.error("CSV requires y_true and y_score columns.")
            except Exception as exc:
                st.error(f"Could not read evaluation CSV: {exc}")

    if evaluation_df is not None:
        yt = evaluation_df["y_true"].astype(int).to_numpy()
        ys = evaluation_df["y_score"].astype(float).to_numpy()

        if len(np.unique(yt)) < 2:
            st.error("ROC/AUC cannot be calculated unless both outcome classes are present.")
        else:
            auc = roc_auc_score(yt, ys)
            fpr, tpr, _ = roc_curve(yt, ys)

            k1, k2, k3, k4 = st.columns(4)
            k1.metric("AUC", f"{auc:.3f}")
            k2.metric("N evaluated", str(len(yt)))
            k3.metric("Outcome positive", str(int(yt.sum())))
            k4.metric("Data source", "Synthetic" if mode.startswith("Demonstration") else "Uploaded")

            roc_fig = go.Figure()
            roc_fig.add_trace(go.Scatter(
                x=fpr, y=tpr, mode="lines",
                name=f"ROC (AUC={auc:.3f})",
            ))
            roc_fig.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1], mode="lines",
                name="Chance reference", line=dict(dash="dash"),
            ))
            roc_fig.update_layout(
                title="ROC curve",
                xaxis_title="False positive rate",
                yaxis_title="True positive rate / sensitivity",
                template="plotly_dark",
            )
            st.plotly_chart(roc_fig, use_container_width=True)

            threshold_model = st.slider(
                "Illustrative classification threshold",
                0.05, 0.95, 0.50, 0.05,
            )
            pred = (ys >= threshold_model).astype(int)
            cm = confusion_matrix(yt, pred, labels=[0, 1])
            tn, fp, fn, tp = cm.ravel()

            cm_fig = px.imshow(
                cm,
                text_auto=True,
                x=["Predicted 0", "Predicted 1"],
                y=["Observed 0", "Observed 1"],
                title="Confusion matrix",
                color_continuous_scale="Blues",
            )
            st.plotly_chart(cm_fig, use_container_width=True)

            sensitivity = recall_score(yt, pred, zero_division=0)
            specificity = tn / (tn + fp) if (tn + fp) else 0.0
            precision = precision_score(yt, pred, zero_division=0)
            f1 = f1_score(yt, pred, zero_division=0)
            accuracy = accuracy_score(yt, pred)
            brier = brier_score_loss(yt, ys)

            metrics_df = pd.DataFrame({
                "Metric": [
                    "Sensitivity / recall", "Specificity", "Precision",
                    "F1-score", "Accuracy", "Brier score",
                ],
                "Value": [
                    sensitivity, specificity, precision,
                    f1, accuracy, brier,
                ],
            })
            st.dataframe(metrics_df, use_container_width=True, hide_index=True)

            st.markdown("#### Calibration by prediction bin")
            cal_df = pd.DataFrame({
                "y_true": yt,
                "y_score": ys,
            })
            cal_df["bin"] = pd.cut(
                cal_df["y_score"],
                bins=np.linspace(0, 1, 6),
                include_lowest=True,
            )
            calibration = (
                cal_df.groupby("bin", observed=False)
                .agg(
                    Mean_predicted=("y_score", "mean"),
                    Observed_event_rate=("y_true", "mean"),
                    N=("y_true", "size"),
                )
                .dropna()
                .reset_index()
            )
            if not calibration.empty:
                fig_cal = go.Figure()
                fig_cal.add_trace(go.Scatter(
                    x=calibration["Mean_predicted"],
                    y=calibration["Observed_event_rate"],
                    mode="lines+markers",
                    name="Observed",
                ))
                fig_cal.add_trace(go.Scatter(
                    x=[0, 1], y=[0, 1],
                    mode="lines", name="Ideal calibration",
                    line=dict(dash="dash"),
                ))
                fig_cal.update_layout(
                    title="Calibration plot",
                    xaxis_title="Mean predicted probability",
                    yaxis_title="Observed event rate",
                    template="plotly_dark",
                )
                st.plotly_chart(fig_cal, use_container_width=True)
                st.dataframe(calibration, use_container_width=True)

            st.caption(
                f"Evaluation source: {source_label}. AUC, calibration and all other "
                "metrics depend on the dataset and study design. Uploaded data are "
                "not automatically proof of external validation."
            )

            st.download_button(
                "Download evaluation metrics CSV",
                data=metrics_df.to_csv(index=False).encode("utf-8"),
                file_name="model_evaluation_metrics.csv",
                mime="text/csv",
            )

with tabs[6]:
    st.subheader("Research report & oncologist-validation plan")

    validation_checklist = [
        "Define primary endpoint (e.g., a prespecified toxicity grade/time window).",
        "Specify inclusion/exclusion criteria and treatment setting.",
        "Define CYP2D6 assay, allele calling, phenotype translation and CNV handling.",
        "Record dose, adherence, interacting medicines and measured endoxifen with dates.",
        "Predefine missing-data handling and avoid information leakage.",
        "Separate training, tuning and held-out evaluation participants.",
        "Report AUC with confidence intervals and calibration.",
        "Assess sensitivity, specificity and clinical utility at prespecified thresholds.",
        "Perform external validation at an independent site before clinical use.",
        "Obtain appropriate ethics, governance, privacy and clinician review.",
    ]

    checks = {}
    for item in validation_checklist:
        checks[item] = st.checkbox(item, key=f"check_{item}")

    st.markdown("### Literature links")
    st.markdown("""
    - [CPIC CYP2D6 and tamoxifen guideline](https://pmc.ncbi.nlm.nih.gov/articles/PMC5931215/)
    - [Endoxifen TDM prospective study](https://pmc.ncbi.nlm.nih.gov/articles/PMC8975771/)
    - [2025 model-informed precision dosing study](https://pmc.ncbi.nlm.nih.gov/articles/PMC11783121/)
    - [TRIPOD+AI reporting guideline](https://pmc.ncbi.nlm.nih.gov/articles/PMC11019967/)
    """)

    report_data = {
        "case_id": case_id,
        "workspace_mode": mode,
        "primary_drug": drug,
        "age": age,
        "weight_kg": weight,
        "menopausal_status": menopause,
        "tamoxifen_dose_mg_day": dose if drug == "Tamoxifen" else None,
        "pgx": {
            "genotype": genotype,
            "phenotype": phenotype,
            "activity_score": activity_score,
            "source": pgx_source,
            "notes": pgx_notes,
        },
        "tdm": {
            "measured_endoxifen_nM": measured_conc,
            "sample_time_months": sample_month,
            "assay": assay_name,
            "reference_line_nM": threshold,
        },
        "concomitant_medicines": selected,
        "labs": labs,
        "history": {
            "vte": vte_history,
            "liver_disease": liver_history,
            "endometrial_history": endometrial_history,
            "prior_adverse_event": adverse_event,
        },
        "validation_checklist": checks,
        "generated_at": datetime.now().astimezone().isoformat(),
        "disclaimer": "Research prototype; not clinically validated.",
    }

    st.json(report_data)

    report_text = make_report(report_data)
    st.download_button(
        "Download research report (.txt)",
        data=report_text,
        file_name=f"{case_id}_oncopgx_report.txt",
        mime="text/plain",
        use_container_width=True,
    )
    st.download_button(
        "Download structured case data (.json)",
        data=json.dumps(report_data, indent=2, ensure_ascii=False, default=str),
        file_name=f"{case_id}_oncopgx_data.json",
        mime="application/json",
        use_container_width=True,
    )

    st.info(
        "The prototype can support an oncologist discussion about feasibility, "
        "data requirements and validation design. It is not itself evidence that "
        "a toxicity model is accurate or clinically useful."
    )

st.markdown("---")
st.caption(
    "OncoPGx Advanced Research Workbench • Educational demonstration • "
    "Clinical validation pending"
)
