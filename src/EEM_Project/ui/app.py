"""
Elonify EEM - Main Streamlit Application Entry Point

This is the starting skeleton. We will expand it into full multi-page navigation
as per the architectural plan.
"""

import streamlit as st
import pandas as pd
from pathlib import Path

from EEM_Project.core.models import (
    example_fiscal_regime,
    ProductionProfile,
    TerrainType,
    GasUtilization,
    RegimeType,
)
from EEM_Project.fiscal.library import FiscalLibrary
import json

from EEM_Project.production.data_handler import (
    load_production_profiles,
    to_summary_dataframe,
    get_unique_blocks,
    save_profiles,
    import_from_uploaded_file,
)
from EEM_Project.costs.data_handler import (
    load_cost_profiles,
    save_cost_profiles,
    import_costs_from_uploaded_file,
)

st.set_page_config(
    page_title="Elonify EEM - Economic Evaluation Model",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Elonify EEM")
st.subheader("Scalable Economic Evaluation Model for Upstream Oil & Gas — Multi-Country Fiscal Regimes (Concessionary/PSC)")

st.success("✅ Elonify EEM — Scalable fiscal regimes (Concessionary Sole Risk/JV + PSC across countries) + multi-format import + external integration ready. Data layer complete for expansion.")

with st.sidebar:
    st.header("Navigation")
    st.caption("Master sheet order (target)")
    page = st.selectbox(
        "Select View",
        [
            "Dashboard",
            "Assumptions (Ec_IO)",
            "Fiscal Regimes",
            "Production Data",
            "Costs Data",
            "Run Model",
            "Results (NPV/IRR/Take)",
            "Sensitivity & Scenarios",
            "Reports / Export",
        ],
        index=0,
    )
    st.markdown("---")
    st.info("Full multi-page + st.data_editor for direct input (import + manual) coming in M1/M5 per plan.")

st.markdown("---")

if page == "Dashboard":
    col1, col2 = st.columns(2)
    with col1:
        st.header("Quick Status")
        lib = FiscalLibrary()
        regimes = lib.list_regimes()
        st.write(f"**Fiscal Regimes Loaded:** {len(regimes)}")
        if regimes:
            for rid in regimes:
                r = lib.get_regime(rid)
                st.write(f"- {rid}: {r.name if r else ''}")
        st.write("**Core Models:** All Pydantic models ready.")
        st.write("**Data Input (Production):** Using production.data_handler (supports xlsm import + JSON fallback + editing).")
        try:
            profs = load_production_profiles(include_totals=False)
            st.write(f"**Profiles available:** {len(profs)} (oil+gas)")
            st.write("Blocks:", ", ".join(get_unique_blocks(profs)[:5]) + " ...")
        except Exception as e:
            st.warning(f"Could not load profiles yet: {e}")
    with col2:
        st.header("Project Goal")
        st.markdown("""
        - Replicate **every key output** from your 36-sheet `Econ_Model_Draft_2.xlsm` (cell-level where possible).
        - Multi-block OML 123/124 support.
        - Professional interactive UI + auditability.
        - **Cross-platform executable** (PyInstaller) at M6.
        """)
        st.caption("Strict validation on every module. Data input is the foundation.")

        st.subheader("🔌 Direct Integration")
        st.markdown("""
        Other apps can send production/cost data **directly**:
        - Python import: `from EEM_Project.production.data_handler import import_from_file`
        - REST: POST to `http://localhost:8000/import/production` (run `python -m EEM_Project.api`)
        - Data lands in the same cache used by this UI.
        """)

elif page == "Production Data":
    st.header("Production Data Input")
    st.caption("Loaded via production.data_handler (two-mode: xlsm or edited JSON). Edit below — changes can be saved back to JSON for persistence.")

    # Prefer JSONs in data/examples for fast local runs (produced by the import script).
    # Falls back to xlsm if JSONs missing and default xlsm path is valid.
    try:
        profiles = load_production_profiles(include_totals=False)
    except Exception as e:
        st.error(f"Failed to load production data: {e}")
        st.info("Run this first (in pwsh from project root):\n$env:PYTHONPATH='src'\npython scripts/import_data.py --full --out data/examples/  # or import_from_xlsm.py (historical name)")
        profiles = []

    source_note = "Loaded from data/examples JSONs (or xlsm if no JSONs and path valid)"
    st.caption(source_note)

    if profiles:
        blocks = get_unique_blocks(profiles)
        # Sensible defaults: prefer key golden blocks mentioned in the model
        default_blocks = [b for b in blocks if any(k in b.upper() for k in ["EBUGHU", "INAGHA", "ORON WEST", "ADANGA MAIN"])]
        if not default_blocks:
            default_blocks = blocks[:4]
        selected_blocks = st.multiselect("Select blocks to view/edit", blocks, default=default_blocks[:6])

        fluid_filter = st.radio("Fluid", ["oil", "gas", "both"], horizontal=True, index=0)

        df = to_summary_dataframe(profiles, fluid=None if fluid_filter == "both" else fluid_filter)
        if selected_blocks:
            df = df[df["block_name"].isin(selected_blocks)]

        st.write(f"**{len(df)} rows** across {df['block_name'].nunique()} blocks")

        st.info(
            "Fully dynamic editor: \n"
            "- Edit any **Block / Field / Well Name** to rename.\n"
            "- To create a **brand new block**, scroll to bottom of table, click '+ Add row', enter a new name in the first column, pick fluid, add year(s) + values.\n"
            "- Edit **Year** numbers freely (no commas).\n"
            "- Add or delete rows to manage years per block or remove entire blocks (delete all rows for a block then Save).\n"
            "- Unselected blocks are preserved on Save."
        )

        # --- NEW: Multi-format file import (very dynamic) ---
        with st.expander("📥 Import / Upload data from other files (.xlsx, .xlsm, .csv, .txt, .docx, etc.)", expanded=False):
            st.write("Upload your own data files. The importer auto-detects EEM wide format or treats the file as a generic table.")
            st.caption("Supported: .xlsx .xlsm .csv .txt .tsv .docx (limited .xls). For .docx it reads the first table.")

            uploaded = st.file_uploader(
                "Choose a data file",
                type=["xlsx", "xlsm", "xls", "csv", "txt", "tsv", "docx"],
                key="data_import_uploader",
            )

            eem_mode = st.checkbox("Use EEM wide structure parser (for original Econ_Model style files)", value=True)

            col_map_text = st.text_input(
                "Optional column mapping (JSON, e.g. {\"MyBlockCol\":\"block_name\"})",
                value="",
                help="Only needed for generic/non-EEM files if auto-detection fails.",
            )

            if uploaded is not None:
                if st.button("Import this file into current session", key="do_import"):
                    try:
                        column_map = None
                        if col_map_text.strip():
                            column_map = json.loads(col_map_text)

                        imported = import_from_uploaded_file(
                            uploaded,
                            eem_structure=eem_mode,
                            column_map=column_map,
                        )

                        if imported:
                            # Merge with currently loaded (avoid total overwrite)
                            current_keys = {(p.block_name, p.fluid_type): p for p in profiles}
                            for p in imported:
                                current_keys[(p.block_name, p.fluid_type)] = p
                            profiles = list(current_keys.values())

                            st.success(f"Successfully imported {len(imported)} profiles from {uploaded.name}!")
                            st.info("The table below now reflects the merged data. Use Save to persist to JSONs.")
                        else:
                            st.warning("No profiles were extracted from the file.")
                    except Exception as ex:
                        st.error(f"Import failed: {ex}")
                        st.exception(ex)

        # Editable table — this is the key "direct entry" mode.
        # Fully dynamic: edit block names (rename or create new blocks by adding rows with new names),
        # edit years, add/delete rows for new years or entirely new blocks/fields/wells.
        edited_df = st.data_editor(
            df,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "block_name": st.column_config.TextColumn(
                    "Block / Field / Well Name",
                    help="Rename an existing block or type a new name here and add rows to create a completely new block/field/well.",
                    required=True,
                ),
                "fluid_type": st.column_config.SelectboxColumn(
                    "Fluid Type",
                    options=["oil", "gas"],
                    required=True,
                ),
                "year": st.column_config.NumberColumn(
                    "Year",
                    format="%d",  # plain integer, no commas or separators
                    step=1,
                    help="Edit the year. Add new year rows for a block by adding rows in the editor.",
                ),
                "daily_rate": st.column_config.NumberColumn(
                    "Daily Rate (mb/d or mmscfd)",
                    format="%.4f",
                    help="Edit daily production rate",
                ),
                "annual_volume": st.column_config.NumberColumn(
                    "Annual Volume (mmbbl or bscf)",
                    format="%.4f",
                    help="Edit annual volume",
                ),
            },
            key="prod_editor",
        )

        if st.button("Save edited data as JSON (updates data/examples)"):
            # Dynamic rebuild supporting:
            # - Editing/renaming block names (new name = new/renamed block)
            # - Adding completely new blocks/fields/wells (add rows with new block_name + years + values)
            # - Adding or deleting year rows for any block
            # - Deleting entire blocks (select the block, delete all its rows in the editor, save)
            # Unselected blocks from the original load are always preserved.
            try:
                final_by_key = {(p.block_name, p.fluid_type): p for p in profiles}

                for (bname, ftype), group in edited_df.groupby(["block_name", "fluid_type"]):
                    if len(group) == 0:
                        # User cleared all rows for this (block, fluid) in the dynamic editor → delete it
                        final_by_key.pop((bname, ftype), None)
                        continue

                    g = group.sort_values("year")
                    yrs = [int(y) for y in g["year"].tolist()]
                    dailys = [float(x) if pd.notna(x) else 0.0 for x in g["daily_rate"].tolist()]
                    anns = [float(x) if pd.notna(x) else 0.0 for x in g["annual_volume"].tolist()]

                    # If this exact (name, fluid) existed originally, carry its metadata (terrain etc.)
                    # so renames or edits keep the original settings. New names get sensible defaults.
                    orig = final_by_key.get((bname, ftype)) or next(
                        (p for p in profiles if p.block_name == bname and p.fluid_type == ftype), None
                    )
                    if orig:
                        terrain = orig.terrain
                        gas_util = orig.gas_utilization
                        oml = orig.oml
                        src = "Edited in UI (from " + (orig.source or "") + ")"
                    else:
                        terrain = TerrainType.SHALLOW_WATER
                        gas_util = GasUtilization.DOMESTIC
                        oml = None
                        src = "Edited in UI - new/renamed block"

                    prof = ProductionProfile(
                        block_name=str(bname).strip(),
                        oml=oml,
                        fluid_type=ftype,
                        terrain=terrain,
                        gas_utilization=gas_util,
                        years=yrs,
                        daily_rates_kbd=dailys,
                        annual_volumes=anns,
                        source=src,
                    )
                    final_by_key[(bname, ftype)] = prof

                rebuilt = list(final_by_key.values())
                save_profiles(rebuilt, Path("data/examples"))
                st.success(
                    f"Saved {len(rebuilt)} profiles (blocks/fields/wells) back to data/examples/ as JSON. "
                    "Unselected blocks were preserved. Reload page or change filters to see updates."
                )
            except Exception as ex:
                st.error(f"Save failed: {ex}")

        # Quick summary chart
        if not edited_df.empty:
            chart_df = edited_df.pivot_table(index="year", columns="block_name", values="annual_volume", aggfunc="sum")
            st.line_chart(chart_df)

elif page == "Costs Data":
    st.header("Costs Data Input (Block_TC / Block_TC_Gas)")
    st.caption("Flexible import for cost data from various formats. Editor coming soon; current focus on import + persistence for capex/opex categorization.")

    with st.expander("📥 Import Costs from file (supports .xlsx .xlsm .csv .docx etc)", expanded=True):
        uploaded_c = st.file_uploader(
            "Upload costs file",
            type=["xlsx", "xlsm", "xls", "csv", "txt", "tsv", "docx"],
            key="cost_import",
        )
        fluid_choice = st.radio("Fluid", ["oil", "gas"], horizontal=True)
        if uploaded_c and st.button("Import & Save Costs"):
            try:
                imported_c = import_costs_from_uploaded_file(uploaded_c, eem_structure=True, fluid=fluid_choice)
                if imported_c:
                    from pathlib import Path as PPath
                    save_cost_profiles(imported_c, PPath("data/examples/costs"))
                    st.success(f"Imported {len(imported_c)} cost profiles for {fluid_choice}.")
                    st.rerun()
            except Exception as ex:
                st.error(f"Failed: {ex}")

    try:
        cprofs = load_cost_profiles(fluid="oil")
        st.write(f"Loaded oil cost profiles: {len(cprofs)}")
        if cprofs:
            st.dataframe([{"block": p.block_name, "items": len(p.items)} for p in cprofs[:5]])
    except Exception:
        st.info("No cost profiles loaded yet. Use importer above.")

elif page == "Fiscal Regimes":
    st.header("Fiscal Regimes (Scalable: Countries + Concessionary (Sole Risk/JV) or PSC)")
    st.caption("Scalable across countries and regime types: Concessionary (Sole Risk / JV) or PSC. Add new countries/regimes below — they persist to YAML.")

    lib = FiscalLibrary()

    # Show by country for scalability
    countries = lib.list_countries()
    if countries:
        selected_country = st.selectbox("Select Country", countries, index=0 if "Nigeria" in countries else 0)
        regimes = lib.get_regimes_for_country(selected_country)
        for r in regimes:
            with st.expander(f"{r.name} ({r.regime_type.value}{f' / {r.ownership_type.value}' if r.ownership_type else ''})"):
                st.write(f"**ID:** {r.id} | **Country:** {r.country} | **Version:** {r.version}")
                col1, col2 = st.columns(2)
                with col1:
                    st.json({
                        "royalty_oil_rates": r.royalty_oil_rates,
                        "royalty_gas_rates": r.royalty_gas_rates,
                        "tax_rates": r.tax_rates,
                        "levies": r.levies,
                    })
                with col2:
                    st.json({
                        "capital_allowance_rules": r.capital_allowance_rules,
                        "cost_recovery_limit": r.cost_recovery_limit,
                        "profit_split_rules": r.profit_split_rules,
                        "additional_parameters": r.additional_parameters,
                    })
                if r.regime_type == RegimeType.CONCESSIONARY:
                    st.info("This is a CONCESSIONARY regime. NCF calculation follows royalty → tax path (Sole Risk or JV ownership).")
                else:
                    st.info("This is a PSC regime. NCF follows cost recovery → profit split path.")

    # --- Add new regime form (room for expansion) ---
    st.subheader("➕ Add New Fiscal Regime (for new country or type)")
    with st.form("add_regime_form"):
        new_id = st.text_input("ID (e.g. 'angola_psc_2025')", value="new_country_new_regime")
        new_name = st.text_input("Display Name", value="New Regime")
        new_country = st.text_input("Country", value="New Country")
        new_type = st.selectbox("Regime Type", ["concessionary", "psc"])
        new_ownership = None
        if new_type == "concessionary":
            new_ownership = st.selectbox("Ownership (for Concessionary)", ["sole_risk", "jv"])
        new_desc = st.text_area("Description", value="Add description here. Customize rates below.")

        st.markdown("**Basic Rates (edit YAML for full sliding scales, tranches, etc.)**")
        col1, col2 = st.columns(2)
        with col1:
            royalty_base = st.number_input("Royalty Oil Base Rate (e.g. 0.075)", value=0.075, step=0.005, format="%.3f")
            cit = st.number_input("CIT Rate", value=0.30, step=0.05, format="%.2f")
        with col2:
            cost_rec = st.number_input("Cost Recovery Limit (PSC only, 0-1)", value=0.5 if new_type=="psc" else 0.0, step=0.05, format="%.2f")
            profit_contractor = st.number_input("Base Contractor Profit Share (PSC)", value=0.7, step=0.05, format="%.2f")

        submitted = st.form_submit_button("Add / Update Regime (saves to YAML)")

        if submitted:
            try:
                from EEM_Project.core.models import FiscalRegime, RegimeType, OwnershipType
                regime_data = {
                    "id": new_id,
                    "name": new_name,
                    "regime_type": new_type,
                    "country": new_country,
                    "description": new_desc,
                    "royalty_oil_rates": {"default": {"base": royalty_base, "sliding": False}},
                    "tax_rates": {"cit": cit},
                    "cost_recovery_limit": cost_rec if new_type == "psc" else None,
                    "profit_split_rules": {"contractor_base_share": profit_contractor} if new_type == "psc" else {},
                }
                if new_ownership:
                    regime_data["ownership_type"] = new_ownership

                new_regime = FiscalRegime(**regime_data)
                lib.add_or_update_regime(new_regime, save_to_file=True)
                st.success(f"Regime '{new_id}' added/updated. YAML saved in data/fiscal_regimes/. Refresh to see.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to add regime: {e}")

    st.info(
        "Structure for future: Add country folders under data/fiscal_regimes/ (e.g. nigeria/, angola/). "
        "Each YAML defines one regime. Concessionary NCF uses royalty/tax path (with Sole Risk vs JV ownership affecting equity/NCF split). "
        "PSC NCF uses cost recovery + profit oil split. The library and models now support all combinations."
    )

else:
    st.info(f"**{page}** page is next. Data input (production + costs) is now the active module. Costs editor and full scenario config coming immediately after.")

st.markdown("---")
st.caption("Elonify EEM — Scalable cross-platform desktop app (Streamlit + PyInstaller). Supports Concessionary (Sole Risk/JV) and PSC regimes across countries. Data input, multi-format import, and direct app integration ready.")
