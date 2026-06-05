# EEM_Project - Economic Evaluation Model
**Elonify EEM - Scalable Cross-Platform App for Nigerian Upstream Fiscal Modeling (PIA 2021)**

App name changed from previous "Ebony EEM" to "Elonify EEM".

Built following the detailed architectural plan for Dr. Emmanuel Onwuka / Teno Upstream.

## Vision
Transform the 36-sheet Excel economic model (Econ_Model_Draft_2.xlsm) into a modern, modular, auditable, and highly scalable Python application.

**Key Features (Target)**
- Multi-block / multi-field production and cost modeling
- Flexible Fiscal Regime configuration (scalable: any country, Concessionary (Sole Risk/JV) or PSC)
- Full calculation chain: Royalties → FLGT → Capital Allowances → HT → CIT → NCF (Project & Equity)
- Interactive dashboards, sensitivity analysis, and professional reporting
- Cross-platform desktop executable (via packaging)
- Git-friendly + excellent support for AI-assisted development (local Ollama / Claude Code / Cursor)

## Current Status
Scaffold + package structure fixes complete. Following ARCHITECTURE_AND_IMPLEMENTATION_PLAN.md **strictly** (user confirmed).

**Implemented so far**:
- Full directory structure with package __init__.py files (src/EEM_Project/)
- Core Pydantic data models (core/models.py)
- Fiscal library + scalable regime support (multi-country, Concessionary (Sole Risk/JV) + PSC, UI form to add, country subdirs)
- Basic Streamlit entry (ui/app.py) - now importable
- Package imports standardized to EEM_Project (kept src/EEM_Project/ per preference)
- .venv-ready instructions

**Important**: The source `Econ_Model_Draft_2.xlsm` (36-sheet model) is still needed in the workspace root for import script + formula extraction + validation. It is .gitignored.

See the full architectural plan (ARCHITECTURE_AND_IMPLEMENTATION_PLAN.md) for module mapping, dependency graph, UI pages, and phased roadmap. Strict validation (cell-level match to Excel) applies to every calculation module.

## Tech Stack
- Python 3.11+
- Streamlit (UI)
- Pydantic v2 + pandas/Polars (data & calculations)
- SQLModel / SQLite (persistence)
- Plotly (charts)
- PyInstaller or similar for executable packaging (planned)

## Multi-Format Data Import & Integration
The data input layer now supports importing production and cost data from:
- Spreadsheets: .xls .xlsx .xlsm
- Delimited: .csv .txt .tsv
- Documents: .docx (tables; .doc via conversion)
- Generic or EEM-specific wide formats (auto-detected)
- Direct from other apps via Python import or REST API (FastAPI at /import/production and /import/costs)

See the "Production Data" and "Costs Data" pages in the app for uploaders, and `src/EEM_Project/api.py` for integration.

## Getting Started (Development)
```powershell
# On Windows (pwsh) - from the eem-project folder
cd "C:\path\to\eem-project"

# Create virtual environment (recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # or .venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Run the app (from project root; PYTHONPATH makes src/EEM_Project importable as package)
$env:PYTHONPATH="src"
streamlit run src/EEM_Project/ui/app.py
```

Alternative (editable install):
```powershell
pip install -e .
$env:PYTHONPATH="src"
streamlit run src/EEM_Project/ui/app.py
```
(Requires pyproject.toml for full -e support; can be added in packaging phase.)
```

## Roadmap (High-Level)
See the detailed phased plan in the original architecture document:
- M0: Scaffold + core models + fiscal loader
- M1: Production & Cost data handling + import from Excel
- M2: Royalties, FLGT, Cap Allow
- M3: HT/CIT NCF chain + RESULTS replication
- M4: Equity path + consolidation
- M5: Dashboards, sensitivity, persistence
- M6: Packaging for cross-platform executable + polish

## Collaboration
This project is designed to be built collaboratively:
- Grok (me) scaffolds and implements core logic here.
- You test on your machine and provide feedback (or use your local Ollama/Claude Code agents on specific modules).
- We iterate module by module, always validating against your original Excel outputs.

## License & Notes
Internal tool for Teno Upstream / personal use. All fiscal logic must be validated against PIA 2021 and your existing model before any commercial use.

---

**Next Step (per strict plan)**: Once you copy `Econ_Model_Draft_2.xlsm` to the workspace root, I will:
1. Detect it and list all sheets.
2. Implement `scripts/import_from_xlsm.py` (Phase 0 / M1).
3. Create `docs/module_specs/` with exact formula extractions from your Excel (using openpyxl).
4. Proceed module-by-module with validation (e.g. start with Ec_IO / Fiscal Terms_PIA / Royalties).

Run the current scaffold with the commands above to confirm it works (you should see the welcome + loaded fiscal regime). Provide feedback on the UI look/feel direction for "professional" polish.
