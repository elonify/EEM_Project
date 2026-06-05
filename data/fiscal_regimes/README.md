# Fiscal Regimes (Scalable Structure)

This directory supports easy addition of countries and fiscal regimes for future expansion of the model.

## Directory Layout (recommended)
```
data/fiscal_regimes/
├── nigeria/
│   └── pia_2021_concessionary.yaml     # Concessionary Sole Risk (or copy for JV)
├── angola/
│   └── psc_2025.yaml
├── generic/
│   └── psc_template.yaml               # Use as starting point for new regimes
└── README.md
```

## Regime Types
- **Concessionary**: Royalty + tax based NCF.
  - `ownership_type`: `sole_risk` or `jv`
- **PSC**: Production Sharing Contract.
  - Use `cost_recovery_limit` + `profit_split_rules`
  - `ownership_type` should be null/omitted

## Adding a New Country/Regime
1. Create a country subfolder (e.g. `data/fiscal_regimes/kenya/`).
2. Copy `generic/psc_template.yaml` or the Nigeria example.
3. Edit `id`, `name`, `country`, `regime_type`, `ownership_type` (if concessionary), rates, etc.
4. The `FiscalLibrary` will automatically discover it (uses `rglob`).
5. Or use the in-app "Add New Fiscal Regime" form in the **Fiscal Regimes** page (saves YAML automatically).

## Model Extensibility
See `src/EEM_Project/core/models.py`:
- `FiscalRegime` uses flexible `dict` fields for rates/rules.
- `additional_parameters` for country-specific logic.
- Validation ensures correct `ownership_type` for concessionary vs PSC.

This structure allows the NCF calculation engine (future) to branch cleanly:
- Concessionary Sole Risk → full equity NCF after royalty/tax
- Concessionary JV → apply equity share
- PSC → cost recovery then profit split

## Validation
All regimes must validate against `FiscalRegime` Pydantic model when loaded.
