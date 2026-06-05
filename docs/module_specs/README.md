# Module Specifications (Formula Capture)

This directory holds one .md per major calculation / data module.

**Mandatory Protocol (from ARCHITECTURE_AND_IMPLEMENTATION_PLAN.md §6)**:

For every calculation module:
1. Identify source sheet(s) in Econ_Model_Draft_2.xlsm.
2. Use `openpyxl` (data_only=False) to extract the *exact formula text* from the formula bar (not values).
3. Document here:
   - Purpose
   - Input models (Pydantic)
   - Output models
   - **Excel Formula Reference** section: paste real cell + formula + surrounding context
   - Business logic translation (plain English + PIA 2021 reference)
   - Edge cases / assumptions / terrain differences (oil vs gas)
4. *Only then* implement the equivalent pure Python in `src/EEM_Project/calculations/*.py` (or fiscal/calculators etc).
5. Validate side-by-side (same inputs -> match outputs row-by-row within tol) before git commit / next module.

Golden fields for validation: IZOMBE, ORON WEST, ADANGA, EBUGHU, etc. (use consistent time span e.g. 2026-2040 or whatever your model uses).

## Modules (to be populated)

- fiscal_terms_pia.md
- production_data.md
- royalties_flgt.md
- capital_allowances.md
- ht_ncf.md
- cit_ncf.md
- ncf_consolidator.md (Project + Equity)
- metrics.md (NPV, IRR, Payout, Takes, unit costs)
- equity_dash.md
- ec_io_assumptions.md (global scenario inputs)

Start with high priority input + early calc chain.
