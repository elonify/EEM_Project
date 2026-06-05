# EEM_Project – Complete Architecture & Implementation Plan
**For AI Coding Agents (Claude, Cursor, Local Ollama, Grok, etc.)**

**Project Goal**  
Transform the 36-sheet `Econ_Model_Draft_2.xlsm` (Nigerian PIA 2021 upstream economic model) into a clean, modular, scalable, auditable Python application with a modern Streamlit interface that can eventually be packaged as a cross-platform desktop executable.

This document is the single source of truth for any AI coding agent working on the project.

---

## 1. Project Overview & Success Criteria

### Success Criteria (MVP)
- Replicate key outputs (NPV@10%, IRR, Payout, Government/Contractor Take, Unit Costs) from the original Excel model within acceptable tolerance.
- Support the existing blocks/fields in OML 123/124.
- Allow easy addition of new blocks/fields without copying sheets.
- Have a working Fiscal Regime system driven by YAML (not hardcoded).
- Clean separation between Project-level and Equity-level calculations.
- Professional, interactive dashboards.

### Non-Functional Goals
- Type-safe (Pydantic)
- Well-tested (compare against Excel)
- Git-friendly and AI-agent friendly (small focused files + clear specs)
- Scalable to multiple countries/regimes in the future

---

## 2. Tech Stack (Do Not Deviate Without Discussion)

- **Language**: Python 3.11+
- **UI**: Streamlit (multi-page)
- **Data Validation & Models**: Pydantic v2
- **Data Processing**: pandas + Polars (for performance)
- **Persistence**: SQLite via SQLModel (local-first)
- **Fiscal Config**: YAML files (versioned, human + AI editable)
- **Charts**: Plotly
- **Packaging (later)**: PyInstaller (primary) or NiceGUI/Tauri
- **Version Control**: Git + clear conventional commits

**Repository Root**: `eem-project/` (workspace)

**Package**: `src/EEM_Project/` (kept per user preference; imports use `EEM_Project.xxx`. Architecture examples below use the canonical names; adjust paths when reading.)

---

## 3. Repository Structure (Follow Exactly)

```
eem-project/
├── README.md
├── ARCHITECTURE_AND_IMPLEMENTATION_PLAN.md   ← This file (read me first)
├── requirements.txt
├── pyproject.toml (optional later)
├── data/
│   ├── fiscal_regimes/          # Versioned YAML files
│   │   └── nigeria_pia_2021_concessionary.yaml
│   └── examples/                # Sample imported data
├── src/EEM_Project/             # Actual package (user chose to keep this name)
│   ├── __init__.py
│   ├── core/
│   │   ├── models.py            # All Pydantic models
│   │   ├── config.py
│   │   ├── orchestrator.py      # Runs the full model
│   │   └── utils.py
│   ├── fiscal/
│   │   ├── library.py           # Loads & queries regimes
│   │   └── calculators.py       # Royalty, tax helpers
│   ├── production/
│   │   ├── data_handler.py
│   │   └── profiles.py
│   ├── costs/
│   │   └── allowances.py
│   ├── calculations/
│   │   ├── royalties_flgt.py
│   │   ├── ht_ncf.py
│   │   ├── cit_ncf.py
│   │   ├── ncf_consolidator.py
│   │   └── metrics.py
│   ├── ui/
│   │   ├── app.py
│   │   ├── pages/               # One file per major page
│   │   └── components.py
│   ├── db/
│   │   ├── database.py
│   │   └── repositories.py
│   └── tests/
├── docs/
│   └── module_specs/            # One .md per module with formulas
├── scripts/
│   └── import_from_xlsm.py      # Critical migration script
└── .gitignore
```

**Agent Rule**: Never create files outside this structure without updating this document.

---

## 4. Sheet-by-Sheet Analysis (Source of Truth)

### Group 1: Navigation & Control
- **Master** → Use as reference for UI navigation order.
- **Ec_IO** → Central source of assumptions (discount rate, equity %, terrain, gas utilization, scenario multipliers, price deck). Will become `ScenarioConfig` + global settings page.
- **Model Map** → Visual reference only.

### Group 2: Input Data (Highest Priority for Normalization)
- **Block_Oil Data** & **Block_Gas Data**: Wide format with multiple fields side-by-side. Daily + Annual volumes. Links to Block_TC.
- **Prod_Summary**: Cleaner combined view used by Royalties.
- **Block_TC** & **Block_TC_Gas**: Time-series costs categorized for capital allowances.
- **Equity Dash**: Equity share, acquisition costs.

**Critical Requirement (User Directive)**:  
The Input Data Layer must support **two modes**:
1. **Imported** from Excel/CSV/JSON (via `scripts/import_data.py`).
2. **Typed directly** inside the Streamlit app (using `st.data_editor` for new blocks or editing existing production/cost/equity data).

All data — whether imported or manually entered — must validate against the same Pydantic models (`ProductionProfile`, `CostProfile`, etc.) and be persistable per Project/Scenario.

**Action for Agent**: Design `production/data_handler.py` and `costs/` modules from the start to support both import and in-app direct entry/editing. Do not make the layer import-only.

### Group 3: Fiscal Configuration
- **Fiscal Terms_PIA**: Contains royalty rates (by terrain + sliding scales), tax rates, levies, capital allowance rules, cost recovery, profit split. Heavily referenced by formulas in other sheets.

**Action**: Extract all rates/rules into `data/fiscal_regimes/nigeria_pia_2021_concessionary.yaml`. Build `FiscalLibrary` to load it.

### Group 4: Calculation Chain (Follow This Dependency Order)

1. **Royalties** → Production-based + price-based royalties by terrain. Complex sliding scale IF formulas referencing `Fiscal Terms_PIA`.
2. **FLGT** → Royalties + Rentals + Bonuses + NDDC + HCDT.
3. **Cap_Allow** & **Cap_Allow Gas** → Capital allowance calculations (different rules for oil vs gas).
4. **HT_NCF** / **HT_NCF_Oil** → Hydrocarbon Tax NCF.
5. **CIT_NCF** / **CIT_NCF_Oil** / **CIT_NCF_Gas** → Companies Income Tax + Education/Dev Levy.
6. **CR Economics_123** → PSC Cost Recovery & Profit Split (generalize this).
7. **Project_NCF_Con** → Consolidated Project NCF (Oil + Gas).
8. **Equity_* versions** + **Equity_NCF_Con** → Apply equity share and produce contractor NCF.

### Group 5: Results
- **RESULTS** & **RESULTS Equity** → NPV, IRR, Payout, Take statistics, Unit costs, etc.
- These are the final outputs we must replicate first.

---

## 5. Core Data Models (Start Here)

All modules must use these Pydantic models (defined in `src/EEM_Project/core/models.py`):

- `FiscalRegime`
- `ProductionProfile`
- `CostItem` / `CostProfile`
- `ScenarioConfig`
- `NCFResult` (yearly)
- `MetricsResult`
- `RunResult`

**Agent Instruction**: When you implement a new module, update `core/models.py` if new models are needed, and document the model in `docs/module_specs/`.

---

## 6. Formula Capture & Documentation Protocol (Critical)

Because the user wants to give formula bar logic to the agent on every step, follow this process:

### For Every Calculation Module:

1. **Identify source sheets** (e.g., Royalties sheet for royalty logic).
2. **Use openpyxl to extract formula text** (not calculated values).
3. **Create a file** in `docs/module_specs/royalties_flgt.md` containing:
   - Purpose of the module
   - Input models
   - Output models
   - **Excel Formula Reference** section with actual formula text + cell references
   - Business logic explanation (translate the formula into plain English + PIA reference if known)
   - Edge cases / assumptions
4. Only then implement the Python version.

**Example Structure for `docs/module_specs/royalties_flgt.md`**:

```markdown
## Royalties + FLGT Module

### Source Sheets
- Royalties
- FLGT
- Fiscal Terms_PIA (rates)

### Key Excel Formulas (extracted)

**Royalty by Oil Production (Shallow Water sliding scale)**  
Cell in Royalties sheet (example):
```
=IF(B5=0,0,IF(AND('Fiscal Terms_PIA'!$T$18=Ec_IO!$G$20,B5<='Fiscal Terms_PIA'!$V$18/1000),'Fiscal Terms_PIA'!$W$18, ... ))
```

**Translation**:
- If production volume is below first tranche → use base rate
- Between tranche 1 and 2 → marginal rate calculation
- etc.

### Python Implementation Requirements
- Support sliding scale via configuration in YAML
- Handle different terrains (Onshore, Shallow, Deep, Frontier)
- Separate oil vs gas + gas utilization flag
```

**Agent Rule**: Never implement calculation logic without first creating/updating the corresponding `docs/module_specs/` file with the original Excel formulas.

---

## 7. Implementation Roadmap (Follow in Order)

### Phase 0: Foundation (Do this first)
- [ ] Create full folder structure
- [ ] Implement `core/models.py` (all key Pydantic models)
- [ ] Implement `fiscal/library.py` + sample YAML
- [ ] Create `scripts/import_data.py` (normalize Block_Oil Data, Block_Gas Data, Block_TC, etc. into clean models)
- [ ] Basic Streamlit skeleton (`ui/app.py`)

### Phase 1: Data Layer
- [ ] Production data handler (normalize wide format)
- [ ] Cost data handler + categorization for allowances
- [ ] Scenario & Project configuration

### Phase 2: Core Calculations (in strict order)
- [ ] Royalties + FLGT module (with full formula translation)
- [ ] Capital Allowances (Oil + Gas)
- [ ] HT_NCF
- [ ] CIT_NCF (Oil + Gas)
- [ ] PSC Cost Recovery (generalize CR Economics_123)
- [ ] NCF Consolidator (Project + Equity)

### Phase 3: Results & UI
- [ ] Metrics calculator (NPV, IRR, Payout, Take stats, Unit costs)
- [ ] Full multi-page Streamlit UI
- [ ] Scenario comparison & sensitivity

### Phase 4: Persistence, Polish & Packaging
- [ ] SQLite persistence for projects/scenarios
- [ ] Audit logging (save inputs + regime version + outputs)
- [ ] Professional Excel/PDF export
- [ ] PyInstaller packaging for cross-platform executable

---

## 8. Validation Strategy (Strict – Non-Negotiable)

**Core Rule**: The output of every module **must match the corresponding Excel sheet and key cells** from beginning to end (not just final NPV/IRR).

### Mandatory Process for Every Module
1. Identify the source Excel sheet(s) the module replaces.
2. Extract the exact formulas/logic from the formula bar (document in `docs/module_specs/`).
3. Implement the Python version.
4. Run **side-by-side comparison**:
   - Use the same input values from the Excel.
   - Compare **cell-by-cell or row-by-row** outputs for critical calculated columns (e.g., Annual Royalty, Total Allowable Cost, HT, CIT, NCF per year, etc.).
   - Use pandas DataFrame comparison or direct value checks with tolerance only where floating-point is expected.
5. **Only proceed to the next module/step after explicit confirmation** that outputs match.
6. **After every validated step/module, perform a git commit** with a clear message (e.g., `feat(royalties): implement sliding scale royalty matching Excel Royalties sheet`).

**No shortcuts**. Approximate high-level metrics are not sufficient. We aim for cell-level / intermediate value fidelity where possible.

**Golden Test Cases**: IZOMBE, ORON WEST, ADANGA, EBUGHU, etc. (use consistent input years, e.g. 2026–2040).

**Agent Instruction**: Before asking to move to the next module, you must state:  
"Validation complete for [Module Name]. Outputs match Excel sheet [Sheet Name] for key cells. Ready for git commit and next step."

---

## 9. How to Work With This Document (For AI Agents)

1. **Always read this file first** at the start of a session.
2. When asked to implement a module:
   - Go to the relevant section in this document.
   - Read the corresponding `docs/module_specs/` file (create it if missing).
   - Extract or ask for the latest Excel formulas from the source sheets.
   - Implement following the spec.
3. Update this document and the module spec when you discover new logic or make changes.
4. Prefer small, focused files and clear type hints.

---

## 10. Current Status (updated 2026)

- Folder structure created + all `__init__.py` added (src/EEM_Project/ is now a proper importable package)
- `core/models.py` implemented with all key Pydantic models (FiscalRegime, ProductionProfile, CostProfile, ScenarioConfig, NCFResult, MetricsResult, RunResult, enums)
- `fiscal/library.py` + sample YAML (loads regimes from data/fiscal_regimes/; load logic hardened)
- Basic Streamlit `ui/app.py` exists and runs cleanly under EEM_Project package
- README + this architecture document updated to match actual layout (src/EEM_Project kept per preference) and user decisions
- User confirmed via session: **follow this plan *strictly*** (phase order, formula protocol §6, cell-by-cell validation §8 mandatory). GUI: **Streamlit + PyInstaller** (no deviation). Source xlsm to be copied to workspace root.

**Next Immediate Task for Agent** (after user copies Econ_Model_Draft_2.xlsm):  
- Detect the xlsm and list/analyze all 36 sheets.
- Create `scripts/import_data.py` (and `docs/module_specs/` structure).
- Start formula extraction + implementation for highest priority modules (Ec_IO assumptions, Fiscal Terms_PIA, Block_* Data, Royalties/FLGT) per the groups in §4 and roadmap in §7.
- Only advance after explicit validation match statement per §8.

---

**End of Document**

This file should be the first thing any coding agent reads when working on EEM_Project.
