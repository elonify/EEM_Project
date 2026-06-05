# Royalties + FLGT Module Spec

## Source Sheets
- Royalties
- FLGT
- Fiscal Terms_PIA (rates)
- Ec_IO (scenario flags, price deck, terrain?)

## Purpose
Calculate gross royalty (oil + gas, by terrain sliding scales + price royalty) then add other FLGT items (rentals, bonuses, NDDC levy, HCDT).

First step in the calculation chain. Output feeds allowable costs / NCF.

## Input Models (planned)
- `ProductionProfile` (per block, with terrain + gas_util)
- `ScenarioConfig` (multipliers, price deck)
- `FiscalRegime` (from library)

## Output Models
- Per-year royalty amounts (oil, gas, total)
- FLGT total per year
- Will feed into `NCFResult.royalty` and `levies`

## Excel Formula Reference (extracted 05-Jun-2026 via openpyxl from the user's current Econ_Model_Draft_2.xlsm)

**Source of chargeable volumes**: Prod_Summary (linked to Block_Oil Data / Block_Gas Data annuals).

**Royalty Oil Formulas** (Royalties sheet, row 5, for the three terrain columns; these are the core marginal sliding scale calcs):
- Onshore (col I / B column production):
```
=IF(B5=0,0,IF(AND('Fiscal Terms_PIA'!$T$18=Ec_IO!$G$20,B5<='Fiscal Terms_PIA'!$V$18/1000),'Fiscal Terms_PIA'!$W$18,IF(AND('Fiscal Terms_PIA'!$T$18=Ec_IO!$G$20,B5>'Fiscal Terms_PIA'!$V$18/1000,B5<='Fiscal Terms_PIA'!$V$19/1000),('Fiscal Terms_PIA'!$W$18*'Fiscal Terms_PIA'!$V$18/1000+(B5-'Fiscal Terms_PIA'!$V$18/1000)*'Fiscal Terms_PIA'!$W$19)/B5,IF(AND('Fiscal Terms_PIA'!$T$18=Ec_IO!$G$20,B5>'Fiscal Terms_PIA'!$V$19/1000),('Fiscal Terms_PIA'!$W$18*'Fiscal Terms_PIA'!$V$18/1000+('Fiscal Terms_PIA'!$V$19/1000-'Fiscal Terms_PIA'!$V$18/1000)*'Fiscal Terms_PIA'!$W$19+(B5-'Fiscal Terms_PIA'!$V$20/1000)*'Fiscal Terms_PIA'!$W$20)/B5,0))))
```
- Shallow Water (col J):
```
=IF(B5=0,0,IF(AND('Fiscal Terms_PIA'!$T$21=Ec_IO!$G$20,B5<='Fiscal Terms_PIA'!$V$21/1000),'Fiscal Terms_PIA'!$W$21,IF(AND('Fiscal Terms_PIA'!$T$21=Ec_IO!$G$20,B5>'Fiscal Terms_PIA'!$V$21/1000,B5<='Fiscal Terms_PIA'!$V$22/1000),('Fiscal Terms_PIA'!$W$21*'Fiscal Terms_PIA'!$V$21/1000+(B5-'Fiscal Terms_PIA'!$V$21/1000)*'Fiscal Terms_PIA'!$W$22)/B5,IF(AND('Fiscal Terms_PIA'!$T$21=Ec_IO!$G$20,B5>'Fiscal Terms_PIA'!$V$22/1000),('Fiscal Terms_PIA'!$W$21*'Fiscal Terms_PIA'!$V$21/1000+('Fiscal Terms_PIA'!$V$22/1000-'Fiscal Terms_PIA'!$V$21/1000)*'Fiscal Terms_PIA'!$W$22+(B5-'Fiscal Terms_PIA'!$V$23/1000)*'Fiscal Terms_PIA'!$W$23)/B5,0))))
```
- Deep (col K):
```
=IF(B5=0,0,IF(AND(Ec_IO!$G$20='Fiscal Terms_PIA'!$T$24,B5<='Fiscal Terms_PIA'!$V$24/1000),'Fiscal Terms_PIA'!$W$24,IF(AND(Ec_IO!$G$20='Fiscal Terms_PIA'!$T$24,B5>'Fiscal Terms_PIA'!$V$24/1000),('Fiscal Terms_PIA'!$W$24*'Fiscal Terms_PIA'!$V$24/1000+(B5-'Fiscal Terms_PIA'!$V$25/1000)*'Fiscal Terms_PIA'!$W$25)/B5,0)))
```

**Gas Royalty** (row 5):
```
=IF(E5=0,0,IF(Ec_IO!$G$21='Fiscal Terms_PIA'!$U$29,'Fiscal Terms_PIA'!$U$30,'Fiscal Terms_PIA'!$V$30))
```

**Fiscal Terms_PIA tables** (see fiscal_terms_pia.md for the full pasted rate table; rows 16-30 contain the MIN/MAX/RATE per terrain + gas in/out country rates).

**Translation** (plain English):
- Chargeable production (bopd or mmscfd daily equivalent for the year row) is tested against the tranche thresholds for the terrain selected by Ec_IO!$G$20 (or G21 for gas).
- Base rate applies below first tranche.
- Between tranches a marginal rate is calculated as (volume_in_lower * lower_rate + volume_in_this_tranche * this_rate) / total_chargeable. This is the classic "average royalty rate on the barrel".
- The result (royalty rate) * chargeable volume (or value?) gives the royalty $ for that row/year/terrain column.
- FLGT sheet then adds the other front-end loaded payments (rentals, bonuses, NDDC, HCDT) on top of royalties.

**Edge cases**:
- Zero production rows return 0.
- The formulas reference named ranges like Production_Days (from Ec_IO) and cross-sheet links (Prod_Summary for chargeable vols).
- Terrain is global for the model run via Ec_IO flag (not per-block in this version).

See the full rate table and more context in docs/module_specs/fiscal_terms_pia.md .

## Implementation Location (after this spec complete)
`src/EEM_Project/calculations/royalties_flgt.py`

## Validation
Row-by-row match on the Royalties and FLGT sheets for the golden blocks/years. Use both formula view and data_only values.
