# Fiscal Terms (PIA 2021) - Module Spec

## Source Sheets
- Fiscal Terms_PIA (primary rates, tables, rules)
- Cross-referenced by: Royalties, FLGT, Cap_Allow, HT_NCF, CIT_NCF, etc.

## Purpose
Central configuration for all Nigerian PIA 2021 fiscal calculations (royalty rates by terrain + sliding scales, price-based royalty, HT/CIT rates, levies (NDDC, HCDT), capital allowance schedules (oil vs gas), cost recovery (PSC), profit split (PSC)).

Must be versioned and human/AI editable → drives `data/fiscal_regimes/nigeria_pia_2021_concessionary.yaml` (and future PSC/JV variants).

## Input Models
- (none - source of truth for `FiscalRegime`)
- Later: `FiscalRegime` Pydantic model (core/models.py)

## Output Models
- `FiscalRegime` (populated and saved to YAML)
- Helper dicts / lookup tables used by royalty, tax, allowance calculators.

## Excel Formula Reference / Extracted Tables (from openpyxl on Econ_Model_Draft_2.xlsm - Acquisitions copy, 05-Jun-2026)

**Royalty Oil Sliding Scale Table** (Fiscal Terms_PIA rows ~16-26, cols T/W ~20/23):
```
TERRAIN                | MIN   | MAX    | PIA RATE | MECHANISM | PRE-PIA
Onshore                | 0     | 5000   | 0.05     | Sliding   | 0.2
                       | 5001  | 10000  | 0.075    |           |
                       | Above | 10000  | 0.15     |           |
Shallow Water (<200m   | 0     | 5000   | 0.05     | Sliding   | 0.185
                       | 5001  | 10000  | 0.075    |           |
                       | Above | 10000  | 0.125    |           |
Deep Offshore (>200m   | 0     | 50000  | 0.05     | Sliding   | 0.1
                       | Above | 50000  | 0.075    |           |
Frontier Basin         |       |        | 0.075    | Flat      | 0.075
```

**Gas Royalty** (rows 28-30):
- Terrain | Out-Country | In-Country (Dom Gas)
- Onshore  | 0.05        | 0.025
(plus other terrains)

**Ec_IO terrain / gas flags used to select row (G20 / G21)**:
- G20: "Shallow Water (<200m water depth)"
- G21: "In-Country (Dom Gas)"

**Royalty Formulas** (exact from Royalties sheet row 5, the chargeable production row; B5 = chargeable oil bopd):
Onshore (col I):
```
=IF(B5=0,0,IF(AND('Fiscal Terms_PIA'!$T$18=Ec_IO!$G$20,B5<='Fiscal Terms_PIA'!$V$18/1000),'Fiscal Terms_PIA'!$W$18,IF(AND('Fiscal Terms_PIA'!$T$18=Ec_IO!$G$20,B5>'Fiscal Terms_PIA'!$V$18/1000,B5<='Fiscal Terms_PIA'!$V$19/1000),('Fiscal Terms_PIA'!$W$18*'Fiscal Terms_PIA'!$V$18/1000+(B5-'Fiscal Terms_PIA'!$V$18/1000)*'Fiscal Terms_PIA'!$W$19)/B5,IF(AND('Fiscal Terms_PIA'!$T$18=Ec_IO!$G$20,B5>'Fiscal Terms_PIA'!$V$19/1000),('Fiscal Terms_PIA'!$W$18*'Fiscal Terms_PIA'!$V$18/1000+('Fiscal Terms_PIA'!$V$19/1000-'Fiscal Terms_PIA'!$V$18/1000)*'Fiscal Terms_PIA'!$W$19+(B5-'Fiscal Terms_PIA'!$V$20/1000)*'Fiscal Terms_PIA'!$W$20)/B5,0))))
```

Shallow (col J):
```
=IF(B5=0,0,IF(AND('Fiscal Terms_PIA'!$T$21=Ec_IO!$G$20,B5<='Fiscal Terms_PIA'!$V$21/1000),'Fiscal Terms_PIA'!$W$21,IF(AND('Fiscal Terms_PIA'!$T$21=Ec_IO!$G$20,B5>'Fiscal Terms_PIA'!$V$21/1000,B5<='Fiscal Terms_PIA'!$V$22/1000),('Fiscal Terms_PIA'!$W$21*'Fiscal Terms_PIA'!$V$21/1000+(B5-'Fiscal Terms_PIA'!$V$21/1000)*'Fiscal Terms_PIA'!$W$22)/B5,IF(AND('Fiscal Terms_PIA'!$T$21=Ec_IO!$G$20,B5>'Fiscal Terms_PIA'!$V$22/1000),('Fiscal Terms_PIA'!$W$21*'Fiscal Terms_PIA'!$V$21/1000+('Fiscal Terms_PIA'!$V$22/1000-'Fiscal Terms_PIA'!$V$21/1000)*'Fiscal Terms_PIA'!$W$22+(B5-'Fiscal Terms_PIA'!$V$23/1000)*'Fiscal Terms_PIA'!$W$23)/B5,0))))
```

Deep (col K):
```
=IF(B5=0,0,IF(AND(Ec_IO!$G$20='Fiscal Terms_PIA'!$T$24,B5<='Fiscal Terms_PIA'!$V$24/1000),'Fiscal Terms_PIA'!$W$24,IF(AND(Ec_IO!$G$20='Fiscal Terms_PIA'!$T$24,B5>'Fiscal Terms_PIA'!$V$24/1000),('Fiscal Terms_PIA'!$W$24*'Fiscal Terms_PIA'!$V$24/1000+(B5-'Fiscal Terms_PIA'!$V$25/1000)*'Fiscal Terms_PIA'!$W$25)/B5,0)))
```

**Gas royalty** (simple lookup):
```
=IF(E5=0,0,IF(Ec_IO!$G$21='Fiscal Terms_PIA'!$U$29,'Fiscal Terms_PIA'!$U$30,'Fiscal Terms_PIA'!$V$30))
```

**Translation**:
- The long IF chain picks the correct terrain row in Fiscal Terms_PIA using the Ec_IO flag (G20).
- For each tranche: if volume below first threshold use base rate; between thresholds compute the marginal weighted average royalty rate for the total volume.
- Chargeable volumes come from Prod_Summary (linked to Block_* Data annuals * factors).
- Gas uses G21 (In-Country vs export) to pick rate.

**Capital Allowances, Taxes, Levies**
- Tables and rates exist further in the sheet (initial/annual % by oil/gas, HT/CIT rates, NDDC 3%, HCDT 3%, etc.).
- To be extracted in follow-up passes as we implement Cap_Allow / HT_NCF / CIT_NCF modules (per strict order).
- Price royalty adder when oil > threshold (e.g. $70).

**Capital Allowances (Oil vs Gas)**
- Initial allowance % + annual % (pool or straight line).
- Different for oil facilities vs gas.

**Taxes**
- HT (Hydrocarbon Tax) rate
- CIT 30% + Education/Development Levy 3%?
- NDDC 3%, HCDT 3%

## Business Logic (to be refined with real formulas + PIA text)
- Royalties calculated on gross production value or volume? (check model).
- FLGT = Royalties + Rentals + Bonuses + NDDC + HCDT.
- Capital allowances deducted for tax purposes (HT then CIT).
- Order critical: Royalties → FLGT → allowable costs incl. CA → HT NCF → CIT on (HT NCF?).

## Edge Cases / Assumptions
- Gas utilization flag affects royalty and perhaps other.
- Terrain per block (some blocks may have multiple?).
- Sliding scales: marginal or block? (document exact IF/AND structure).
- Pre- vs post- PIA conversion terms (OML 123/124 specific?).

## Current YAML (data/fiscal_regimes/nigeria_pia_2021_concessionary.yaml)
See file for initial populated values (illustrative - **must validate and expand from your Excel Fiscal Terms_PIA sheet**).

## Validation Target
After import + regime loader, the rates used in Python royalties must exactly reproduce the royalty numbers coming out of the Excel Royalties sheet for the same production/price inputs.

## Next
Once xlsm present:
1. Run `python scripts/import_from_xlsm.py --list-sheets`
2. Use openpyxl to dump key cells + formulas from "Fiscal Terms_PIA" (and any linked).
3. Paste here + implement loader enhancements if needed.
