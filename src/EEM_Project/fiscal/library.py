"""
Fiscal Library for Ebony EEM.

Loads and manages fiscal regime configurations from YAML/JSON files.
Provides easy access to rates, rules, and calculation parameters.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from ebony_eem.core.models import FiscalRegime, RegimeType


class FiscalLibrary:
    """Central service for loading and querying fiscal regimes."""

    def __init__(self, regimes_dir: Path | str = "data/fiscal_regimes"):
        self.regimes_dir = Path(regimes_dir)
        self._regimes: dict[str, FiscalRegime] = {}
        self._load_all()

    def _load_all(self) -> None:
        """Load all YAML/JSON regime files from the regimes directory."""
        if not self.regimes_dir.exists():
            self.regimes_dir.mkdir(parents=True, exist_ok=True)
            return

        for file_path in self.regimes_dir.glob("*.y*ml"):  # .yaml or .yml
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or json.load(f)
                regime = FiscalRegime(**data)
                self._regimes[regime.id] = regime
            except (ValidationError, yaml.YAMLError, json.JSONDecodeError) as e:
                print(f"Warning: Could not load {file_path}: {e}")

    def get_regime(self, regime_id: str) -> FiscalRegime | None:
        return self._regimes.get(regime_id)

    def list_regimes(self) -> list[str]:
        return list(self._regimes.keys())

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
    example = lib.get_regime("nigeria_pia_2021_concessionary_v1")
    if example:
        print("Example regime loaded successfully:", example.name)
