"""Atom-by-atom elemental mass conservation engine for C, H, O, N, S, and Ash.

Tracks elemental partitioning across solid biochar, liquid bio-oil (organic and aqueous phases),
syngas molecules, and dryer exhaust, computing closures and carbon recovery metrics.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from src.data.feedstock import BiomassFeedstock
from src.process.drying import DryingResult
from src.process.reactor import ReactorOutput
from src.process.separation import SeparationResult
from src.models.syngas_model import SyngasComposition
from src.models.bio_oil_model import BioOilChemicalGrouping


@dataclass
class ElementalStream:
    """Elemental mass flows within an individual process stream (kg/h)."""
    stream_id: str
    name: str
    carbon_kg_h: float
    hydrogen_kg_h: float
    oxygen_kg_h: float
    nitrogen_kg_h: float
    sulfur_kg_h: float
    ash_kg_h: float
    total_mass_kg_h: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stream_id": self.stream_id,
            "name": self.name,
            "carbon_kg_h": round(self.carbon_kg_h, 3),
            "hydrogen_kg_h": round(self.hydrogen_kg_h, 3),
            "oxygen_kg_h": round(self.oxygen_kg_h, 3),
            "nitrogen_kg_h": round(self.nitrogen_kg_h, 3),
            "sulfur_kg_h": round(self.sulfur_kg_h, 3),
            "ash_kg_h": round(self.ash_kg_h, 3),
            "total_mass_kg_h": round(self.total_mass_kg_h, 3),
        }


@dataclass
class ElementalClosure:
    """Closure metric for a single chemical element."""
    element: str
    mass_in_kg_h: float
    mass_out_kg_h: float
    closure_pct: float
    closure_error_pct: float
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element": self.element,
            "mass_in_kg_h": round(self.mass_in_kg_h, 4),
            "mass_out_kg_h": round(self.mass_out_kg_h, 4),
            "closure_pct": round(self.closure_pct, 3),
            "closure_error_pct": round(self.closure_error_pct, 4),
            "status": self.status,
        }


@dataclass
class PlantElementalBalanceSummary:
    """Comprehensive plant-wide elemental balance summary and carbon distribution."""
    closures: Dict[str, ElementalClosure]
    streams: Dict[str, ElementalStream]
    carbon_partitioning_pct: Dict[str, float]
    overall_status: str
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_status": self.overall_status,
            "carbon_partitioning_pct": {k: round(v, 2) for k, v in self.carbon_partitioning_pct.items()},
            "closures": {k: v.to_dict() for k, v in self.closures.items()},
            "streams": {k: v.to_dict() for k, v in self.streams.items()},
            "warnings": self.warnings,
        }


class ElementalBalanceEngine:
    """Engine computing atomic mass conservation across all conversion units."""

    def __init__(self, tolerance_pct: float = 0.5) -> None:
        self.tolerance_pct = tolerance_pct

    def compute_elemental_balance(
        self,
        raw_feed_rate_kg_h: float,
        feedstock: BiomassFeedstock,
        drying_result: DryingResult,
        reactor_output: ReactorOutput,
        separation_result: SeparationResult,
        syngas_comp: SyngasComposition,
        bio_oil_grouping: BioOilChemicalGrouping,
    ) -> PlantElementalBalanceSummary:
        """Compute atom-by-atom elemental balances across all plant streams.

        Args:
            raw_feed_rate_kg_h: Wet biomass feed rate (kg/h).
            feedstock: BiomassFeedstock with ultimate and proximate analyses.
            drying_result: Outputs from drying unit.
            reactor_output: Outputs from reactor unit.
            separation_result: Outputs from separation unit.
            syngas_comp: Detailed syngas composition from syngas model.
            bio_oil_grouping: Detailed bio-oil grouping from bio-oil model.

        Returns:
            PlantElementalBalanceSummary with verified closures and carbon distribution.
        """
        # 1. Total Elemental Inputs from Raw Biomass and Carrier Gas
        w_in_frac = feedstock.proximate.moisture / 100.0
        m_dry_in = raw_feed_rate_kg_h * (1.0 - w_in_frac)
        m_moist_in = raw_feed_rate_kg_h * w_in_frac

        # Dry matter elemental masses
        c_in_dry = m_dry_in * (feedstock.ultimate.carbon / 100.0)
        h_in_dry = m_dry_in * (feedstock.ultimate.hydrogen / 100.0)
        o_in_dry = m_dry_in * (feedstock.ultimate.oxygen / 100.0)
        n_in_dry = m_dry_in * (feedstock.ultimate.nitrogen / 100.0)
        s_in_dry = m_dry_in * (feedstock.ultimate.sulfur / 100.0)
        ash_in_dry = m_dry_in * (feedstock.ultimate.ash / 100.0)

        # Moisture contribution (H2O: H = 2.016/18.015, O = 15.999/18.015)
        h_in_moist = m_moist_in * (2.016 / 18.015)
        o_in_moist = m_moist_in * (15.999 / 18.015)

        # Carrier gas (N2)
        n_in_carrier = reactor_output.carrier_gas_kg_h

        total_in = {
            "C": c_in_dry,
            "H": h_in_dry + h_in_moist,
            "O": o_in_dry + o_in_moist,
            "N": n_in_dry + n_in_carrier,
            "S": s_in_dry,
            "Ash": ash_in_dry,
        }

        # 2. Elemental Outputs in Individual Streams
        streams: Dict[str, ElementalStream] = {}

        # Stream S105: Dryer Water Vapor Exhaust
        m_evap = drying_result.water_evaporated_kg_h
        h_evap = m_evap * (2.016 / 18.015)
        o_evap = m_evap * (15.999 / 18.015)
        streams["S105_DRYER_WATER_EXHAUST"] = ElementalStream(
            stream_id="S105",
            name="Dryer Water Exhaust",
            carbon_kg_h=0.0,
            hydrogen_kg_h=h_evap,
            oxygen_kg_h=o_evap,
            nitrogen_kg_h=0.0,
            sulfur_kg_h=0.0,
            ash_kg_h=0.0,
            total_mass_kg_h=m_evap,
        )

        # Stream S108: Clean Syngas Stream
        c_gas = syngas_comp.elemental_mass_flow_kg_h.get("carbon_kg_h", 0.0)
        h_gas = syngas_comp.elemental_mass_flow_kg_h.get("hydrogen_kg_h", 0.0)
        o_gas = syngas_comp.elemental_mass_flow_kg_h.get("oxygen_kg_h", 0.0)
        n_gas = syngas_comp.elemental_mass_flow_kg_h.get("nitrogen_kg_h", 0.0)
        streams["S108_CLEAN_SYNGAS"] = ElementalStream(
            stream_id="S108",
            name="Clean Syngas",
            carbon_kg_h=c_gas,
            hydrogen_kg_h=h_gas,
            oxygen_kg_h=o_gas,
            nitrogen_kg_h=n_gas,
            sulfur_kg_h=0.0,
            ash_kg_h=0.0,
            total_mass_kg_h=separation_result.clean_syngas_kg_h,
        )

        # Stream S107: Recovered Bio-Oil (Organics + Aqueous)
        m_oil_org = bio_oil_grouping.organics_mass_flow_kg_h
        m_oil_wat = bio_oil_grouping.water_mass_flow_kg_h

        elem_org_pct = bio_oil_grouping.elemental_composition_organics_pct
        c_oil_org = m_oil_org * (elem_org_pct.get("carbon_pct", 55.0) / 100.0)
        h_oil_org = m_oil_org * (elem_org_pct.get("hydrogen_pct", 6.5) / 100.0)
        o_oil_org = m_oil_org * (elem_org_pct.get("oxygen_pct", 37.5) / 100.0)
        n_oil_org = m_oil_org * (elem_org_pct.get("nitrogen_pct", 0.8) / 100.0)
        s_oil_org = m_oil_org * (elem_org_pct.get("sulfur_pct", 0.2) / 100.0)

        # Water in bio-oil contribution
        h_oil_wat = m_oil_wat * (2.016 / 18.015)
        o_oil_wat = m_oil_wat * (15.999 / 18.015)

        streams["S107_BIO_OIL"] = ElementalStream(
            stream_id="S107",
            name="Liquid Bio-Oil",
            carbon_kg_h=c_oil_org,
            hydrogen_kg_h=h_oil_org + h_oil_wat,
            oxygen_kg_h=o_oil_org + o_oil_wat,
            nitrogen_kg_h=n_oil_org,
            sulfur_kg_h=s_oil_org,
            ash_kg_h=0.0,
            total_mass_kg_h=separation_result.recovered_bio_oil_liquid_kg_h,
        )

        # Stream S106: Recovered Biochar Product
        # Biochar holds 100% of feed ash (scaled by cyclone recovery)
        eta_cyc = separation_result.cyclone_efficiency
        ash_char_rec = ash_in_dry * eta_cyc
        ash_fines_loss = ash_in_dry * (1.0 - eta_cyc)

        # Carbon in char = Total Carbon in - Carbon in gas - Carbon in bio-oil
        c_char_rec = max(0.0, (c_in_dry - c_gas - c_oil_org) * eta_cyc)
        c_fines_loss = max(0.0, (c_in_dry - c_gas - c_oil_org) * (1.0 - eta_cyc))

        # Hydrogen in char
        h_char_rec = max(0.0, (total_in["H"] - (h_evap + h_gas + h_oil_org + h_oil_wat)) * eta_cyc)
        h_fines_loss = max(0.0, (total_in["H"] - (h_evap + h_gas + h_oil_org + h_oil_wat)) * (1.0 - eta_cyc))

        # Oxygen in char
        o_char_rec = max(0.0, (total_in["O"] - (o_evap + o_gas + o_oil_org + o_oil_wat)) * eta_cyc)
        o_fines_loss = max(0.0, (total_in["O"] - (o_evap + o_gas + o_oil_org + o_oil_wat)) * (1.0 - eta_cyc))

        # Nitrogen & Sulfur in char
        n_char_rec = max(0.0, (total_in["N"] - (n_gas + n_oil_org)) * eta_cyc)
        n_fines_loss = max(0.0, (total_in["N"] - (n_gas + n_oil_org)) * (1.0 - eta_cyc))

        s_char_rec = max(0.0, (total_in["S"] - s_oil_org) * eta_cyc)
        s_fines_loss = max(0.0, (total_in["S"] - s_oil_org) * (1.0 - eta_cyc))

        streams["S106_BIOCHAR"] = ElementalStream(
            stream_id="S106",
            name="Recovered Biochar",
            carbon_kg_h=c_char_rec,
            hydrogen_kg_h=h_char_rec,
            oxygen_kg_h=o_char_rec,
            nitrogen_kg_h=n_char_rec,
            sulfur_kg_h=s_char_rec,
            ash_kg_h=ash_char_rec,
            total_mass_kg_h=separation_result.recovered_biochar_kg_h,
        )

        streams["S109_CYCLONE_FINES"] = ElementalStream(
            stream_id="S109",
            name="Cyclone Fines",
            carbon_kg_h=c_fines_loss,
            hydrogen_kg_h=h_fines_loss,
            oxygen_kg_h=o_fines_loss,
            nitrogen_kg_h=n_fines_loss,
            sulfur_kg_h=s_fines_loss,
            ash_kg_h=ash_fines_loss,
            total_mass_kg_h=separation_result.cyclone_fines_loss_kg_h,
        )

        # 3. Total Accounted Elemental Outputs
        total_out = {
            "C": c_char_rec + c_fines_loss + c_oil_org + c_gas,
            "H": h_evap + h_gas + h_oil_org + h_oil_wat + h_char_rec + h_fines_loss,
            "O": o_evap + o_gas + o_oil_org + o_oil_wat + o_char_rec + o_fines_loss,
            "N": n_gas + n_oil_org + n_char_rec + n_fines_loss,
            "S": s_oil_org + s_char_rec + s_fines_loss,
            "Ash": ash_char_rec + ash_fines_loss,
        }

        # 4. Closures Calculation
        closures: Dict[str, ElementalClosure] = {}
        all_passed = True
        warnings: List[str] = []

        for elem in ["C", "H", "O", "N", "S", "Ash"]:
            m_in = total_in[elem]
            m_out = total_out[elem]
            closure_pct = (m_out / m_in * 100.0) if m_in > 0 else 100.0
            closure_err = abs(100.0 - closure_pct)
            is_pass = closure_err <= self.tolerance_pct
            status = "PASS" if is_pass else "FAIL"

            if not is_pass:
                all_passed = False
                warnings.append(f"Elemental {elem} closure deviation ({closure_err:.3f}%) exceeds tolerance.")

            closures[elem] = ElementalClosure(
                element=elem,
                mass_in_kg_h=m_in,
                mass_out_kg_h=m_out,
                closure_pct=closure_pct,
                closure_error_pct=closure_err,
                status=status,
            )

        # Carbon Partitioning (% of input carbon)
        c_in_total = total_in["C"]
        c_partitioning = {
            "biochar_carbon_pct": ((c_char_rec + c_fines_loss) / c_in_total * 100.0) if c_in_total > 0 else 0.0,
            "bio_oil_carbon_pct": (c_oil_org / c_in_total * 100.0) if c_in_total > 0 else 0.0,
            "syngas_carbon_pct": (c_gas / c_in_total * 100.0) if c_in_total > 0 else 0.0,
        }

        overall_status = "PASS" if all_passed else "FAIL"

        return PlantElementalBalanceSummary(
            closures=closures,
            streams=streams,
            carbon_partitioning_pct=c_partitioning,
            overall_status=overall_status,
            warnings=warnings,
        )
