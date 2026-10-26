            row = {"recorded_at": datetime.now().isoformat(timespec="seconds"), "scenario_id": scenario_id.strip() or "DEMO-001",
                   "sample_date": sample_date.isoformat(), "endoxifen_value": level, "unit": unit,
                   "tamoxifen_dose_mg_day": dose, "adherence": adher, "notes": notes}
            history = append_local_row(TDM_DB, cols, row)
            st.success("Saved to local CSV. On hosted platforms, local storage may be reset when the app restarts.")
    history = read_local_csv(TDM_DB, cols)
    if not history.empty:
        st.markdown("### Stored measured results")
        scenario_filter = st.selectbox("Display scenario", ["All scenarios"] + sorted(history["scenario_id"].dropna().astype(str).unique().tolist()))
        shown = history if scenario_filter == "All scenarios" else history[history["scenario_id"].astype(str) == scenario_filter]
        st.dataframe(shown, use_container_width=True, hide_index=True)
        plot_df = shown.copy()
        plot_df["sample_date"] = pd.to_datetime(plot_df["sample_date"], errors="coerce")
        plot_df["endoxifen_value"] = pd.to_numeric(plot_df["endoxifen_value"], errors="coerce")
        for unit_value, unit_df in plot_df.groupby("unit"):
            unit_df = unit_df.dropna(subset=["sample_date", "endoxifen_value"]).sort_values("sample_date")
            if not unit_df.empty:
                fig_tdm = go.Figure()
                fig_tdm.add_trace(go.Scatter(x=unit_df["sample_date"], y=unit_df["endoxifen_value"], mode="lines+markers", name=str(unit_value)))
                fig_tdm.update_layout(template="plotly_dark", title=f"Measured endoxifen trend ({unit_value})", xaxis_title="Sample date", yaxis_title=f"Measured value ({unit_value})")
                st.plotly_chart(fig_tdm, use_container_width=True)
        st.download_button("Download TDM CSV", data=history.to_csv(index=False).encode("utf-8"), file_name="oncopgx_tdm_measurements.csv", mime="text/csv")
    else:
        st.info("No TDM records saved yet.")
    st.caption("Values in different units are plotted separately; the app does not convert them without a verified analyte-specific conversion and lab context.")

# -------------------- PK / AUC SANDBOX --------------------

elif page == "PK/AUC Sandbox":
    st.subheader("Illustrative pharmacokinetic model sandbox")
    st.warning("Educational one-compartment model only—not calibrated to tamoxifen, endoxifen, or any patient. Do not use for dosing, efficacy, or toxicity predictions.")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        dose_demo = st.number_input("Illustrative input amount (arbitrary units)", min_value=1.0, max_value=10000.0, value=100.0, step=10.0)
        ka = st.number_input("Absorption rate constant ka (1/h)", min_value=0.01, max_value=5.0, value=1.0, step=0.05)
    with col_b:
        kel = st.number_input("Elimination rate constant kel (1/h)", min_value=0.005, max_value=2.0, value=0.08, step=0.005)
        volume = st.number_input("Apparent volume V (arbitrary L)", min_value=1.0, max_value=10000.0, value=100.0, step=5.0)
    with col_c:
        bioavail = st.slider("Bioavailability F (illustrative)", min_value=0.05, max_value=1.0, value=0.7, step=0.05)
        hours = st.slider("Display window (hours)", min_value=12, max_value=720, value=120, step=12)
    if abs(ka-kel) < 1e-6:
        st.warning("Choose ka and kel that are not equal for this equation.")
    else:
        n_steps = 241
        times = [hours*i/(n_steps-1) for i in range(n_steps)]
        # One-compartment oral input; units are illustrative, not clinically calibrated.
        concentrations = [bioavail*dose_demo*ka/(volume*(ka-kel))*(math.exp(-kel*t)-math.exp(-ka*t)) for t in times]
        concentrations = [max(0.0, c) for c in concentrations]
        auc = sum((concentrations[i]+concentrations[i+1])*(times[i+1]-times[i])/2 for i in range(len(times)-1))
        fig_pk = go.Figure()
        fig_pk.add_trace(go.Scatter(x=times, y=concentrations, mode="lines", name="Illustrative concentration"))
        fig_pk.update_layout(template="plotly_dark", title="Simulated concentration–time curve (arbitrary units)", xaxis_title="Time (h)", yaxis_title="Illustrative concentration")
        st.plotly_chart(fig_pk, use_container_width=True)
        p1, p2 = st.columns(2)
        p1.metric("Numerical AUC over displayed window", f"{auc:.2f} arbitrary units·h")
        p2.metric("Peak in displayed window", f"{max(concentrations):.3f} arbitrary units")
        st.caption("AUC depends on chosen parameters and the finite display window. This is a mathematical demonstration, not a tamoxifen PK model and not a patient-specific estimate.")
        export_pk = pd.DataFrame({"time_h": times, "illustrative_concentration": concentrations})
        st.download_button("Download simulated curve CSV", export_pk.to_csv(index=False).encode("utf-8"), "illustrative_pk_curve.csv", "text/csv")

# -------------------- PV REGISTRY AND REPORT EXPORT --------------------

elif page == "PV Registry & Reports":
    st.subheader("Local pharmacovigilance registry and research exports")
    st.caption("Use fictional or properly de-identified records only. This local log is not connected to PvPI, a hospital EHR, or a regulator.")
    pv_cols = ["report_id", "recorded_at", "scenario_id", "drug", "event_term", "onset_date", "seriousness", "outcome", "dechallenge", "rechallenge", "stage", "notes"]
    pv_df = read_local_csv(PV_DB, pv_cols)
    with st.form("pv_registry_form"):
        p1, p2 = st.columns(2)
        with p1:
            scenario = st.text_input("Fictional scenario ID", value="DEMO-001", key="pv_scenario")
            drug = st.text_input("Suspected medicine", value="Tamoxifen")
            event_term = st.selectbox("Adverse event term", ["Hot flashes", "Venous thromboembolism concern", "Abnormal vaginal bleeding", "Hepatic concern", "Nausea", "Other"])
            onset = st.date_input("Event onset date", value=date.today(), key="pv_onset")
            stage = st.selectbox("Cancer stage (if relevant)", ["Unknown", "Stage 0 / DCIS", "Stage I", "Stage II", "Stage III", "Stage IV / metastatic"])
        with p2:
            serious = st.selectbox("Seriousness", ["Not assessed", "Non-serious", "Serious"])
            outcome = st.selectbox("Outcome", ["Unknown", "Recovering", "Recovered", "Ongoing", "Fatal"])
            dechallenge = st.selectbox("Improved after stopping/withdrawing?", ["Unknown", "Yes", "No", "Not applicable"])
            rechallenge = st.selectbox("Recurred after restarting?", ["Unknown", "Yes", "No", "Not applicable"])
            pv_notes = st.text_input("Non-identifying notes")
        submit_pv = st.form_submit_button("Add report to local registry")
    if submit_pv:
        report_id = f"PV-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        row = {"report_id": report_id, "recorded_at": datetime.now().isoformat(timespec="seconds"),
               "scenario_id": scenario.strip() or "DEMO-001", "drug": drug.strip() or "Unknown",
               "event_term": event_term, "onset_date": onset.isoformat(), "seriousness": serious,
               "outcome": outcome, "dechallenge": dechallenge, "rechallenge": rechallenge,
               "stage": stage, "notes": pv_notes}
        pv_df = append_local_row(PV_DB, pv_cols, row)
        st.success(f"Saved local demonstration record: {report_id}")
    pv_df = read_local_csv(PV_DB, pv_cols)
    if not pv_df.empty:
        st.markdown("### Registry overview")
        m1, m2, m3 = st.columns(3)
        m1.metric("Reports recorded", len(pv_df))
        m2.metric("Marked serious", int((pv_df["seriousness"] == "Serious").sum()))
        m3.metric("Distinct event terms", int(pv_df["event_term"].nunique()))
        st.dataframe(pv_df.sort_values("recorded_at", ascending=False), use_container_width=True, hide_index=True)
        st.download_button("Download PV registry CSV", pv_df.to_csv(index=False).encode("utf-8"), "oncopgx_pv_registry.csv", "text/csv")
        counts = pv_df.groupby(["drug", "event_term"], dropna=False).size().reset_index(name="record_count")
        st.markdown("### Descriptive counts only")
        st.dataframe(counts, use_container_width=True, hide_index=True)
        st.caption("Counts are not incidence rates, causality assessments, validated disproportionality analyses, or regulatory safety signals.")
    else:
        st.info("No local PV reports saved yet.")

    st.markdown("### Export current research scenario")
    profile_export = st.session_state.get("patient_profile", {})
    report = {
        "app": "OncoPGx",
        "version": "advanced research prototype",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "notice": "Educational/research use only; not a clinical decision-support validation.",
        "patient_profile": profile_export,
        "last_lab_scenario": st.session_state.get("last_lab_scenario", {}),
        "data_files": {"pv_registry": str(PV_DB), "tdm_measurements": str(TDM_DB)},
        "limitations": [
            "No validated individual toxicity prediction",
            "No autonomous prescribing or dose adjustment",
            "Local CSV storage may be ephemeral on hosted platforms",
            "Use fictional/de-identified data; no patient identifiers",
        ],
    }
    st.download_button("Export scenario report (JSON)", data=json.dumps(report, indent=2, default=str), file_name="oncopgx_research_report.json", mime="application/json")
    st.download_button("Export active profile (CSV)", data=pd.DataFrame([profile_export]).to_csv(index=False).encode("utf-8") if profile_export else b"", file_name="oncopgx_active_profile.csv", mime="text/csv", disabled=not bool(profile_export))
    st.info("PDF export is not included in this advanced add-on; JSON/CSV exports are provided to keep the report transparent and reproducible.")
