"""
src/EEM_Project/api.py

Simple FastAPI server for direct integration with other applications.

Other apps (Python, JS, etc.) that produce production or cost data can POST JSON
directly to these endpoints instead of (or in addition to) file exports.

Example usage from another app:
    import requests
    data = [{"block_name": "MY_BLOCK", "year": 2025, "annual_volume": 10.0, ...}, ...]
    requests.post("http://localhost:8000/import/production", json=data)

Run the API server:
    python -m EEM_Project.api
    # or uvicorn EEM_Project.api:app --reload

The data is persisted to the same JSON cache used by the Streamlit UI,
so it appears immediately in the app (after refresh or using the load functions).

This enables seamless "production or cost output upon integration".
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from EEM_Project.core.models import CostProfile, ProductionProfile
from EEM_Project.production.data_handler import save_profiles
from EEM_Project.costs.data_handler import save_cost_profiles

app = FastAPI(
    title="Elonify EEM Integration API",
    description="Receive production and cost data directly from other applications.",
    version="0.1.0",
)

DATA_DIR = Path("data/examples")
DATA_DIR.mkdir(parents=True, exist_ok=True)
COSTS_DIR = DATA_DIR / "costs"
COSTS_DIR.mkdir(parents=True, exist_ok=True)


class ProductionInput(BaseModel):
    """Minimal model for incoming production data. Full validation happens in ProductionProfile."""
    block_name: str
    year: int
    annual_volume: float
    daily_rate: float = 0.0
    fluid_type: str = "oil"


class CostInput(BaseModel):
    block_name: str
    year: int
    category: str
    amount_usd_mln: float
    is_oil: bool = True
    is_gas: bool = False


@app.post("/import/production", summary="Import production profiles from another app")
def import_production(data: List[dict]):
    """
    Accept a list of production records (or full ProductionProfile dicts).
    Other apps can send their output directly as JSON.
    Data is converted to ProductionProfile, validated, and saved to JSON cache.
    """
    try:
        profiles = []
        for item in data:
            # Try to build full profile; fall back to minimal
            if "years" in item:
                p = ProductionProfile(**item)
            else:
                # Assume flat list of year records; group them
                # For simplicity, expect caller to group or send one per block with lists
                # Here we support both flat and grouped for flexibility
                p = ProductionProfile(
                    block_name=item.get("block_name"),
                    fluid_type=item.get("fluid_type", "oil"),
                    years=[item["year"]] if "year" in item else item.get("years", []),
                    daily_rates_kbd=[item.get("daily_rate", 0.0)],
                    annual_volumes=[item.get("annual_volume", 0.0)],
                )
            profiles.append(p)

        # Group by block+fluid in case flat list was sent
        grouped = {}
        for p in profiles:
            key = (p.block_name, p.fluid_type)
            if key not in grouped:
                grouped[key] = p
            else:
                # merge years (simple concat + dedup later if needed)
                grouped[key].years.extend(p.years)
                grouped[key].daily_rates_kbd.extend(p.daily_rates_kbd)
                grouped[key].annual_volumes.extend(p.annual_volumes)

        final = list(grouped.values())
        save_profiles(final, DATA_DIR)
        return {"status": "success", "imported": len(final), "message": "Data saved to JSON cache. Refresh UI to see."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/import/costs", summary="Import cost profiles from another app")
def import_costs(data: List[dict]):
    try:
        profiles = []
        for item in data:
            if "items" in item:
                cp = CostProfile(**item)
            else:
                # flat cost item
                ci = CostItem(**{k: v for k, v in item.items() if k in CostItem.model_fields})
                cp = CostProfile(block_name=item.get("block_name", "UNKNOWN"), items=[ci])
            profiles.append(cp)

        save_cost_profiles(profiles, COSTS_DIR)
        return {"status": "success", "imported": len(profiles)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok", "app": "Elonify EEM Integration API"}


if __name__ == "__main__":
    import uvicorn
    print("Starting Elonify EEM Integration API on http://localhost:8000")
    print("Use /docs for Swagger UI to test POSTs from other apps.")
    uvicorn.run(app, host="0.0.0.0", port=8000)
