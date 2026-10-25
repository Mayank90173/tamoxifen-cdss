
with st.sidebar:
    st.header("Scenario inputs")
    phenotype = st.selectbox("CYP2D6 phenotype", [
        "Normal metabolizer", "Intermediate metabolizer", "Poor metabolizer", "Ultrarapid metabolizer"
    ])
    inhibitor = st.selectbox("CYP2D6 inhibitor scenario", [
        "None selected", "Strong inhibitor scenario", "Moderate inhibitor scenario"
    ])
    adherence = st.slider("Illustrative adherence (%)", 10, 100, 90, 5)
    age_band = st.selectbox("Age band (for scenario description)", ["18–39", "40–59", "60+"])
    note = st.text_input("Scenario label (optional)", "Example scenario")

# Explicitly illustrative relative index: not a concentration or probability.
phenotype_values = {
    "Poor metabolizer": 0.35,
    "Intermediate metabolizer": 0.62,
    "Normal metabolizer": 1.00,
    "Ultrarapid metabolizer": 1.08,
}
inhibitor_factors = {
    "None selected": 1.00,
    "Strong inhibitor scenario": 0.55,
    "Moderate inhibitor scenario": 0.78,
}
base = phenotype_values[phenotype]
relative_index = round(base * inhibitor_factors[inhibitor] * adherence / 100, 3)

def band(v):
    if v < 0.45:
        return "Lower illustrative index"
    if v < 0.75:
        return "Intermediate illustrative index"
    return "Higher illustrative index"

m1, m2, m3 = st.columns(3)
m1.metric("Scenario relative index", f"{relative_index:.3f}")
m2.metric("Phenotype input", phenotype)
m3.metric("Adherence input", f"{adherence}%")
st.caption("The index is unitless and illustrative. It is not endoxifen concentration, toxicity risk, or a treatment target.")

left, right = st.columns([1.1, 1])
with left:
    st.markdown("### 1. Relative index by CYP2D6 phenotype")
    p_df = pd.DataFrame({
        "Phenotype": list(phenotype_values.keys()),
        "Illustrative relative index": list(phenotype_values.values())
    })
    fig = px.bar(
        p_df, x="Phenotype", y="Illustrative relative index",
        color="Phenotype", text="Illustrative relative index",
        title="Baseline scenario only (inhibitor absent; adherence 100%)"
    )
    fig.update_layout(template="plotly_dark", showlegend=False, margin=dict(l=10,r=10,t=55,b=10),
                      yaxis_range=[0, 1.2])
    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("### 2. Input scenario contribution")
    contrib = pd.DataFrame({
        "Component": ["Phenotype factor", "Inhibitor factor", "Adherence factor"],
        "Factor": [base, inhibitor_factors[inhibitor], adherence / 100]
    })
    fig2 = px.bar(contrib, x="Component", y="Factor", text="Factor",
                  title="Illustrative multipliers used in this scenario")
    fig2.update_layout(template="plotly_dark", showlegend=False, margin=dict(l=10,r=10,t=55,b=10),
                       yaxis_range=[0, 1.2])
    fig2.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("### 3. Sensitivity analysis")
st.write("Compare how the illustrative index changes across adherence levels for the selected phenotype and inhibitor scenario.")
sens = pd.DataFrame({"Adherence (%)": np.arange(10, 101, 5)})
sens["Illustrative relative index"] = (
    base * inhibitor_factors[inhibitor] * sens["Adherence (%)"] / 100
)
fig3 = px.line(sens, x="Adherence (%)", y="Illustrative relative index", markers=True,
               title="Illustrative index vs adherence")
fig3.add_vline(x=adherence, line_dash="dash", annotation_text="Selected adherence")
fig3.update_layout(template="plotly_dark", margin=dict(l=10,r=10,t=55,b=10))
st.plotly_chart(fig3, use_container_width=True)

st.markdown("### 4. Scenario summary")
st.write(f"**Label:** {note or 'Unlabelled scenario'}  ")
st.write(f"**Scenario:** {phenotype}; {inhibitor}; adherence {adherence}%; age band {age_band}.")
st.write(f"**Model output:** {relative_index:.3f} — {band(relative_index)}.")
st.info(
    "Interpretation boundary: this output is a transparent demonstration of how assumptions combine. "
    "It does not predict an individual patient's endoxifen concentration, recurrence, adverse events, "
    "or the benefit of a specific dose."
)

with st.expander("Methods, assumptions & limitations"):
    st.markdown("""
    - **Model type:** rule-based, multiplicative toy index.
    - **Inputs:** selected CYP2D6 phenotype category, a generic inhibitor scenario, and user-entered adherence.
    - **Output:** unitless relative index only.
    - **Not included:** measured endoxifen concentrations, genotype-level allele translation, drug-specific effect estimates,
      validated pharmacokinetics, external validation, calibration, uncertainty intervals, or clinical outcomes.
    - **Next research steps:** define a protocol; extract published clinical data; pre-specify endpoints; compare model estimates
      against measured endoxifen data; report discrimination/calibration and external validation before clinical claims.
    """)

st.markdown("---")
st.markdown("**Poster-ready takeaway:** A transparent prototype can visualise the direction of assumed CYP2D6, inhibitor, and adherence effects; clinical validity requires real data and independent validation.")
st.caption("Prototype for research discussion only • No patient data required • Not for diagnosis or treatment decisions")
