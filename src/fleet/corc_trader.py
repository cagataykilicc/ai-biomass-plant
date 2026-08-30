"""Real-Time Dynamic Carbon Removal Certificate (CORC) Arbitrage & Pyrolysis Yield Optimization Engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class CarbonMarketQuote:
    """Represents current spot market price signals for carbon credits and commodities."""
    spot_corc_usd_tonne: float = 65.0       # Puro.earth CORC carbon removal price ($/t CO2)
    bio_oil_usd_kg: float = 0.65            # Bio-oil fuel / chemical market price ($/kg)
    biochar_usd_kg: float = 0.45            # Biochar agricultural soil amendment price ($/kg)
    syngas_power_credit_usd_kwh: float = 0.12 # On-site power displacement credit ($/kWh)


class CORCArbitrageEngine:
    """Calculates optimal operational setpoints balancing biofuel revenues against carbon removal credits."""

    def __init__(self, quote: Optional[CarbonMarketQuote] = None):
        self.quote = quote or CarbonMarketQuote()

    def evaluate_arbitrage_modes(self, feed_rate_kg_h: float = 100.0, feedstock: str = "olive_pomace") -> Dict[str, Any]:
        """Compare economics and yields across the operational spectrum."""
        # Simulated kinetic yield responses across 3 characteristic operating regimes
        regimes = [
            {
                "mode": "MAX_CORC_CARBON_REMOVAL",
                "temp_c": 420.0,
                "bio_oil_yield_pct": 48.0,
                "biochar_yield_pct": 36.5,
                "syngas_yield_pct": 15.5,
                "co2_permanence_ratio": 2.75,  # kg CO2 stored per kg biochar
            },
            {
                "mode": "BALANCED_SUSTAINABILITY",
                "temp_c": 490.0,
                "bio_oil_yield_pct": 62.0,
                "biochar_yield_pct": 25.0,
                "syngas_yield_pct": 13.0,
                "co2_permanence_ratio": 2.50,
            },
            {
                "mode": "MAX_BIO_OIL_YIELD",
                "temp_c": 530.0,
                "bio_oil_yield_pct": 68.5,
                "biochar_yield_pct": 18.0,
                "syngas_yield_pct": 13.5,
                "co2_permanence_ratio": 2.20,
            },
        ]

        evaluated_modes = []
        for reg in regimes:
            oil_kg_h = feed_rate_kg_h * (reg["bio_oil_yield_pct"] / 100.0)
            char_kg_h = feed_rate_kg_h * (reg["biochar_yield_pct"] / 100.0)
            
            # Revenues ($/h)
            oil_rev = oil_kg_h * self.quote.bio_oil_usd_kg
            char_rev = char_kg_h * self.quote.biochar_usd_kg
            
            # Carbon Removal Credits ($/h): (kg char * permanence / 1000) * $/t CORC
            co2_tonne_h = (char_kg_h * reg["co2_permanence_ratio"]) / 1000.0
            corc_rev = co2_tonne_h * self.quote.spot_corc_usd_tonne
            
            total_rev = oil_rev + char_rev + corc_rev
            
            evaluated_modes.append({
                "mode": reg["mode"],
                "target_temp_c": reg["temp_c"],
                "bio_oil_yield_pct": reg["bio_oil_yield_pct"],
                "biochar_yield_pct": reg["biochar_yield_pct"],
                "hourly_bio_oil_revenue_usd": round(oil_rev, 2),
                "hourly_biochar_revenue_usd": round(char_rev, 2),
                "hourly_corc_credits_usd": round(corc_rev, 2),
                "total_hourly_revenue_usd": round(total_rev, 2),
                "annual_corc_sequestration_tonnes_co2": round(co2_tonne_h * 8000.0, 1),
            })

        # Determine champion mode with highest total revenue
        champion = max(evaluated_modes, key=lambda m: m["total_hourly_revenue_usd"])

        return {
            "spot_market_quote": {
                "corc_price_usd_tonne": self.quote.spot_corc_usd_tonne,
                "bio_oil_price_usd_kg": self.quote.bio_oil_usd_kg,
                "biochar_price_usd_kg": self.quote.biochar_usd_kg,
            },
            "recommended_mode": champion["mode"],
            "optimal_setpoint_temp_c": champion["target_temp_c"],
            "projected_hourly_revenue_usd": champion["total_hourly_revenue_usd"],
            "arbitrage_analysis": evaluated_modes,
            "decision_rationale": (
                f"At ${self.quote.spot_corc_usd_tonne:.1f}/t CORC and ${self.quote.bio_oil_usd_kg:.2f}/kg Bio-Oil, "
                f"operating in '{champion['mode']}' at {champion['target_temp_c']}°C generates highest net revenue "
                f"(${champion['total_hourly_revenue_usd']:.2f}/h)."
            ),
        }
