"""
Fiscal Library for Elonify EEM.

Loads and manages fiscal regime configurations from YAML/JSON files.
Provides easy access to rates, rules, and calculation parameters.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from EEM_Project.core.models import FiscalRegime, RegimeType, OwnershipType


class FiscalLibrary:
    """Central service for loading and querying fiscal regimes."""

    def __init__(self, regimes_dir: Path | str = "data/fiscal_regimes"):
        self.regimes_dir = Path(regimes_dir)
        self._regimes: dict[str, FiscalRegime] = {}
        self._load_all()

    def _load_all(self) -> None:
        """Load all YAML/JSON regime files from the regimes directory (and subdirs for countries).

        Supports scalable structure:
          data/fiscal_regimes/nigeria/pia_2021_concessionary.yaml
          data/fiscal_regimes/angola/psc_2025.yaml
          etc.
        """
        if not self.regimes_dir.exists():
            self.regimes_dir.mkdir(parents=True, exist_ok=True)
            return

        # Recurse to support country subdirectories for future scalability
        for file_path in self.regimes_dir.rglob("*.y*ml"):  # .yaml, .yml (and .json if needed)
            if file_path.suffix.lower() == ".json":
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    continue
            else:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                except Exception:
                    continue

            if not data:
                continue
            try:
                regime = FiscalRegime(**data)
                self._regimes[regime.id] = regime
            except (ValidationError, TypeError) as e:
                print(f"Warning: Could not load {file_path}: {e}")

    def get_regime(self, regime_id: str) -> FiscalRegime | None:
        return self._regimes.get(regime_id)

    def list_regimes(self) -> list[str]:
        return list(self._regimes.keys())

    def list_countries(self) -> list[str]:
        """Return unique countries with loaded regimes (scalable for multi-country)."""
        return sorted({r.country for r in self._regimes.values()})

    def get_regimes_for_country(self, country: str) -> list[FiscalRegime]:
        """Get all regimes for a specific country."""
        return [r for r in self._regimes.values() if r.country.lower() == country.lower()]

    def list_regime_types(self) -> list[str]:
        """Available main regime types (concessionary, psc)."""
        return sorted({r.regime_type.value for r in self._regimes.values()})

    def get_concessionary_regimes(self, ownership: OwnershipType | None = None) -> list[FiscalRegime]:
        """Filter concessionary regimes, optionally by ownership (sole_risk / jv)."""
        regimes = [r for r in self._regimes.values() if r.regime_type == RegimeType.CONCESSIONARY]
        if ownership:
            regimes = [r for r in regimes if r.ownership_type == ownership]
        return regimes

    def get_psc_regimes(self) -> list[FiscalRegime]:
        """Get all PSC regimes."""
        return [r for r in self._regimes.values() if r.regime_type == RegimeType.PSC]

    def add_or_update_regime(self, regime: FiscalRegime, save_to_file: bool = True) -> None:
        self._regimes[regime.id] = regime
        if save_to_file:
            self._save_regime_to_file(regime)

    def _save_regime_to_file(self, regime: FiscalRegime) -> None:
        file_path = self.regimes_dir / f"{regime.id}.yaml"
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(regime.model_dump(mode="json"), f, sort_keys=False, allow_unicode=True)

    def get_royalty_rate(
        self, regime_id: str, terrain: str, fluid: str = "oil", gas_util: str | None = None
    ) -> float | dict[str, Any]:
        """Example helper - extend with full sliding scale / formula logic."""
        regime = self.get_regime(regime_id)
        if not regime:
            return 0.0
        if fluid == "oil":
            return regime.royalty_oil_rates.get(terrain, 0.0)
        return regime.royalty_gas_rates.get(terrain, 0.0)


# Quick test helper
if __name__ == "__main__":
    lib = FiscalLibrary()
    print("Loaded regimes:", lib.list_regimes())
    print("Countries:", lib.list_countries())
    print("Concessionary regimes:", [r.id for r in lib.get_concessionary_regimes()])
    print("PSC regimes:", [r.id for r in lib.get_psc_regimes()])
    example = lib.get_regime("nigeria_pia_2021_concessionary_v1")
    if example:
        print("Example regime loaded successfully:", example.name, "type=", example.regime_type, "ownership=", example.ownership_type)
