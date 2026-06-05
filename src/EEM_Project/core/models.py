"""
Core Pydantic data models for Ebony EEM.

These models define the canonical data structures used across the application.
They ensure type safety, validation, and clear contracts between modules.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal

import pandas as pd
from pydantic import BaseModel, Field, field_validator, model_validator


class TerrainType(str, Enum):
    ONSHORE = "onshore"
    SHALLOW_WATER = "shallow_water"
    DEEP_WATER = "deep_water"
    # Add more as needed from PIA / your model


class GasUtilization(str, Enum):
    DOMESTIC = "domestic"
    EXPORT = "export"
    REINJECTION = "reinjection"


class RegimeType(str, Enum):
    CONCESSIONARY = "concessionary"
    PSC = "psc"
    JV = "jv"
    SOLE_RISK = "sole_risk"


class FiscalRegime(BaseModel):
    """Represents a complete fiscal regime configuration (e.g., Nigeria PIA 2021)."""
    id: str = Field(..., description="Unique identifier, e.g. 'nigeria_pia_2021_concessionary'")
    name: str
    regime_type: RegimeType
    country: str = "Nigeria"
    effective_from: str | None = None
    version: str = "1.0"
    description: str | None = None

    # Core rates and rules (populated from YAML)
    royalty_oil_rates: dict[str, Any] = Field(default_factory=dict)  # terrain -> rates or formula
    royalty_gas_rates: dict[str, Any] = Field(default_factory=dict)
    price_royalty_rules: dict[str, Any] = Field(default_factory=dict)
    tax_rates: dict[str, float] = Field(default_factory=dict)  # HT, CIT, Edu/Dev Levy
    levies: dict[str, float] = Field(default_factory=dict)     # NDDC, HCDT
    capital_allowance_rules: dict[str, Any] = Field(default_factory=dict)
    cost_recovery_limit: float | None = None
    profit_split_rules: dict[str, Any] = Field(default_factory=dict)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class YearlyRecord(BaseModel):
    """Single year record for production or cash flow."""
    year: int
    value: float = 0.0


class ProductionProfile(BaseModel):
    """Standardized production profile for a block/field (oil or gas)."""
    block_name: str
    oml: str | None = None
    fluid_type: Literal["oil", "gas", "combined"] = "oil"
    terrain: TerrainType = TerrainType.SHALLOW_WATER
    gas_utilization: GasUtilization = GasUtilization.DOMESTIC

    # Time series data
    years: list[int] = Field(default_factory=list)
    daily_rates_kbd: list[float] = Field(default_factory=list)   # kb/d or mmscfd
    annual_volumes: list[float] = Field(default_factory=list)    # mmbbl or bcf

    # Metadata
    source: str | None = None  # e.g. "Block_Oil Data - IZOMBE"
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode='after')
    def check_lengths(self) -> ProductionProfile:
        if len(self.years) != len(self.annual_volumes):
            raise ValueError("years and annual_volumes must have same length")
        return self

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame({
            "year": self.years,
            "daily_rate": self.daily_rates_kbd,
            "annual_volume": self.annual_volumes,
        })


class CostItem(BaseModel):
    """Categorized cost item for capital allowance and tax treatment."""
    block_name: str
    year: int
    category: Literal["exploration", "wells_capex", "facilities_capex", "opex", "abandonment", "other"]
    amount_usd_mln: float
    is_oil: bool = True
    is_gas: bool = False


class CostProfile(BaseModel):
    """Collection of cost items for one or more blocks."""
    block_name: str
    items: list[CostItem] = Field(default_factory=list)

    def to_dataframe(self) -> pd.DataFrame:
        if not self.items:
            return pd.DataFrame()
        return pd.DataFrame([item.model_dump() for item in self.items])


class ScenarioConfig(BaseModel):
    """User scenario definition (Base, S1, S2, custom)."""
    id: str
    name: str
    description: str | None = None
    price_deck: dict[int, float] | None = None  # year -> $/bbl or $/mcf
    production_multiplier: float = 1.0
    capex_multiplier: float = 1.0
    opex_multiplier: float = 1.0
    discount_rate: float = 0.10
    equity_share: float = 1.0  # 1.0 = 100% working interest


class NCFResult(BaseModel):
    """Standardized Net Cash Flow result for a year or full profile."""
    year: int
    revenue: float = 0.0
    royalty: float = 0.0
    levies: float = 0.0
    opex: float = 0.0
    capex: float = 0.0
    abandonment: float = 0.0
    allowable_costs: float = 0.0
    ht: float = 0.0
    cit: float = 0.0
    education_levy: float = 0.0
    ncf_project: float = 0.0
    ncf_equity: float = 0.0
    cumulative_ncf: float = 0.0


class MetricsResult(BaseModel):
    """Key economic metrics (NPV, IRR, etc.)."""
    npv_10: float
    irr: float
    payout_years: float | None
    profitability_index: float
    present_value_ratio: float
    total_royalty: float
    total_ht: float
    total_cit: float
    unit_capex_usd_boe: float | None = None
    unit_opex_usd_boe: float | None = None
    government_take_undisc: float
    contractor_take_undisc: float


class RunResult(BaseModel):
    """Complete result of one model run."""
    scenario_id: str
    fiscal_regime_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ncf_table: list[NCFResult] = Field(default_factory=list)
    metrics: MetricsResult | None = None
    assumptions: dict[str, Any] = Field(default_factory=dict)  # full audit trail


# Example helper
def example_fiscal_regime() -> FiscalRegime:
    return FiscalRegime(
        id="nigeria_pia_2021_concessionary_v1",
        name="Nigeria PIA 2021 - Concessionary (Shallow Water)",
        regime_type=RegimeType.CONCESSIONARY,
        royalty_oil_rates={"shallow_water": {"base": 0.075, "sliding": True}},
        tax_rates={"ht": 0.15, "cit": 0.30, "edu_dev_levy": 0.03},
        levies={"nddc": 0.03, "hcdt": 0.03},
    )
