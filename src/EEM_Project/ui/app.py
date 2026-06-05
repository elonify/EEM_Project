"""
Ebony EEM - Main Streamlit Application Entry Point

This is the starting skeleton. We will expand it into full multi-page navigation
as per the architectural plan.
"""

import streamlit as st

from ebony_eem.core.models import example_fiscal_regime
from ebony_eem.fiscal.library import FiscalLibrary

st.set_page_config(
    page_title="Ebony EEM - Economic Evaluation Model",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Ebony EEM")
st.subheader("Scalable Economic Evaluation Model for Upstream Oil & Gas (PIA 2021)")

st.success("✅ Project scaffold created successfully by Grok following the detailed architectural plan.")

with st.sidebar:
    st.header("Navigation (Coming Soon)")
    st.info("We will build proper multi-page navigation matching your Master sheet workflow.")
    page = st.selectbox(
        "Select View",
        ["Dashboard", "Fiscal Terms", "Production Data", "Run Model", "Results"],
        index=0,
    )

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.header("Quick Status")
    lib = FiscalLibrary()
    regimes = lib.list_regimes()
    st.write(f"**Fiscal Regimes Loaded:** {len(regimes)}")
    if regimes:
        st.write(regimes)

    st.write("**Core Models:** Pydantic models for FiscalRegime, ProductionProfile, CostProfile, NCFResult, etc. are ready.")

with col2:
    st.header("Next Steps")
    st.markdown("""
    1. Copy this folder to your local machine.
    2. Create a virtual environment and `pip install -r requirements.txt`.
    3. Run `streamlit run src/ebony_eem/ui/app.py`.
    4. Tell Grok what to implement next (e.g. "Build the import script from my xlsm" or "Implement the Royalties module").
    """)

st.markdown("---")
st.caption("This app will replicate and improve upon your 36-sheet Excel model while adding scalability, auditability, and a modern interface.")
