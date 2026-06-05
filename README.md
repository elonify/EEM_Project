# EEM_Project - Economic Evaluation Model
**Scalable Cross-Platform App for Nigerian Upstream Fiscal Modeling (PIA 2021)**

Built following the detailed architectural plan for Dr. Emmanuel Onwuka / Teno Upstream.

## Vision
Transform the 36-sheet Excel economic model (Econ_Model_Draft_2.xlsm) into a modern, modular, auditable, and highly scalable Python application.

**Key Features (Target)**
- Multi-block / multi-field production and cost modeling
- Flexible Fiscal Regime configuration (Nigeria PIA Concessionary + PSC foundation)
- Full calculation chain: Royalties → FLGT → Capital Allowances → HT → CIT → NCF (Project & Equity)
- Interactive dashboards, sensitivity analysis, and professional reporting
- Cross-platform desktop executable (via packaging)
- Git-friendly + excellent support for AI-assisted development (local Ollama / Claude Code / Cursor)

## Current Status
This is the initial scaffold created by Grok following the architectural plan.

**Implemented so far**:
- Project directory structure
- Core Pydantic data models (in progress)
- Fiscal library foundation

See the full architectural plan in the conversation history for module mapping, dependency graph, UI pages, and phased roadmap.

## Tech Stack
- Python 3.11+
- Streamlit (UI)
- Pydantic v2 + pandas/Polars (data & calculations)
- SQLModel / SQLite (persistence)
- Plotly (charts)
- PyInstaller or similar for executable packaging (planned)

## Getting Started (Development)
```bash
# Clone or copy this folder to your machine
cd EEM_Project

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows

# Install dependencies (once requirements.txt or pyproject.toml is ready)
pip install -r requirements.txt

# Run the app
streamlit run src/EEM_Project/ui/app.py
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

**Next Step**: Tell me what to implement first (e.g., "Create the Pydantic models and Fiscal Terms loader" or "Build the import script from your xlsm" or "Start with the Streamlit skeleton").
