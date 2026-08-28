"""Plant-wide mass balance accounting, stream tracking, and closure verification.

Computes overall material conservation, stream phase breakdowns, component and elemental
balances, and flags mass balance closure deviations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from src.process.drying import DryingResult
from src.process.reactor import ReactorOutput
from src.process.separation import SeparationResult
from src.data.feedstock import BiomassFeedstock


@dataclass
class StreamFlow:
    """Detailed mass flow stream representation."""
    stream_id: str
    name: str
    source_unit: str
    destination_unit: str
    phase: str  # "solid", "liquid", "gas", "vapor", "multiphase"
    mass_rate_kg_h: float
    temperature_c: float
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stream_id": self.stream_id,
            "name": self.name,
            "source_unit": self.source_unit,
            "destination_unit": self.destination_unit,
            "phase": self.phase,
            "mass_rate_kg_h": round(self.mass_rate_kg_h, 3),
            "temperature_c": round(self.temperature_c, 1),
            "description": self.description,
        }


@dataclass
class MassBalanceSummary:
    """Comprehensive mass balance results across the entire plant."""
    total_input_kg_h: float
    total_output_kg_h: float
    total_losses_kg_h: float
    closure_pct: float
    closure_error_pct: float
    streams: Dict[str, StreamFlow]
    is_balanced: bool
    status: str  # "PASS" or "FAIL"
    warnings: List[str] = field(default_factory=list)

    # Product Breakdown
    biochar_recovered_kg_h: float = 0.0
    bio_oil_recovered_kg_h: float = 0.0
    syngas_recovered_kg_h: float = 0.0
    dryer_water_evap_kg_h: float = 0.0
    cyclone_fines_kg_h: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_input_kg_h": round(self.total_input_kg_h, 3),
            "total_output_kg_h": round(self.total_output_kg_h, 3),
            "total_losses_kg_h": round(self.total_losses_kg_h, 3),
            "closure_pct": round(self.closure_pct, 4),
            "closure_error_pct": round(self.closure_error_pct, 4),
            "status": self.status,
            "is_balanced": self.is_balanced,
            "warnings": self.warnings,
            "products_summary": {
                "biochar_recovered_kg_h": round(self.biochar_recovered_kg_h, 3),
                "bio_oil_recovered_kg_h": round(self.bio_oil_recovered_kg_h, 3),
                "syngas_recovered_kg_h": round(self.syngas_recovered_kg_h, 3),
                "dryer_water_evaporated_kg_h": round(self.dryer_water_evap_kg_h, 3),
                "cyclone_fines_kg_h": round(self.cyclone_fines_kg_h, 3),
            },
            "streams": {k: v.to_dict() for k, v in self.streams.items()},
        }


class MassBalanceEngine:
    """Plant-wide mass balance calculation and verification engine."""

    def __init__(self, closure_tolerance_pct: float = 0.1) -> None:
        self.closure_tolerance_pct = closure_tolerance_pct

    def compute_plant_mass_balance(
        self,
        raw_feed_rate_kg_h: float,
        feedstock: BiomassFeedstock,
        drying_result: DryingResult,
        reactor_output: ReactorOutput,
        separation_result: SeparationResult,
    ) -> MassBalanceSummary:
        """Calculate and verify mass conservation across all unit operations.

        Args:
            raw_feed_rate_kg_h: Mass flow rate of raw as-received biomass (kg/h).
            feedstock: Biomass feedstock definition.
            drying_result: Outputs from drying model.
            reactor_output: Outputs from pyrolysis reactor model.
            separation_result: Outputs from separation and condensation model.

        Returns:
            MassBalanceSummary with verified closure and stream table.
        """
        streams: Dict[str, StreamFlow] = {}

        # 1. Inlet Streams
        carrier_gas_flow = reactor_output.carrier_gas_kg_h
        streams["S101_RAW_BIOMASS"] = StreamFlow(
            stream_id="S101",
            name="Raw Biomass Feed",
            source_unit="BATTERY_LIMITS",
            destination_unit="DRYER_D101",
            phase="solid",
            mass_rate_kg_h=raw_feed_rate_kg_h,
            temperature_c=25.0,
            description="As-received raw biomass with initial moisture",
        )

        if carrier_gas_flow > 0:
            streams["S102_CARRIER_GAS"] = StreamFlow(
                stream_id="S102",
                name="Inert Carrier Gas (N2)",
                source_unit="UTILITY_N2",
                destination_unit="REACTOR_R101",
                phase="gas",
                mass_rate_kg_h=carrier_gas_flow,
                temperature_c=25.0,
                description="Inert sweep gas",
            )

        # 2. Intermediate Streams
        streams["S103_DRIED_BIOMASS"] = StreamFlow(
            stream_id="S103",
            name="Dried Biomass",
            source_unit="DRYER_D101",
            destination_unit="REACTOR_R101",
            phase="solid",
            mass_rate_kg_h=drying_result.dried_feed_rate_out_kg_h,
            temperature_c=drying_result.dryer_temperature_c,
            description="Pretreated biomass solids at reduced moisture",
        )

        streams["S104_REACTOR_EFFLUENT"] = StreamFlow(
            stream_id="S104",
            name="Pyrolysis Reactor Effluent",
            source_unit="REACTOR_R101",
            destination_unit="SEPARATION_S101",
            phase="multiphase",
            mass_rate_kg_h=reactor_output.total_product_rate_kg_h,
            temperature_c=reactor_output.operating_temperature_c,
            description="Combined hot vapors and char particulate exiting reactor",
        )

        # 3. Outlet & Product Streams
        streams["S105_DRYER_EXHAUST_WATER"] = StreamFlow(
            stream_id="S105",
            name="Dryer Water Vapor Exhaust",
            source_unit="DRYER_D101",
            destination_unit="BATTERY_LIMITS",
            phase="vapor",
            mass_rate_kg_h=drying_result.water_evaporated_kg_h,
            temperature_c=drying_result.dryer_temperature_c,
            description="Evaporated moisture from raw feedstock drying",
        )

        streams["S106_BIOCHAR_PRODUCT"] = StreamFlow(
            stream_id="S106",
            name="Recovered Biochar Product",
            source_unit="CYCLONE_C101",
            destination_unit="STORAGE_TK101",
            phase="solid",
            mass_rate_kg_h=separation_result.recovered_biochar_kg_h,
            temperature_c=reactor_output.operating_temperature_c,
            description="Solid biochar product recovered in cyclone",
        )

        streams["S107_BIO_OIL_PRODUCT"] = StreamFlow(
            stream_id="S107",
            name="Liquid Bio-oil Product",
            source_unit="CONDENSER_E101",
            destination_unit="STORAGE_TK102",
            phase="liquid",
            mass_rate_kg_h=separation_result.recovered_bio_oil_liquid_kg_h,
            temperature_c=separation_result.assumptions.get("condenser_exit_temp_c", 35.0),
            description="Condensed liquid pyrolytic oil (organics + pyrolytic water)",
        )

        streams["S108_CLEAN_SYNGAS"] = StreamFlow(
            stream_id="S108",
            name="Clean Product Syngas",
            source_unit="CONDENSER_E101",
            destination_unit="BATTERY_LIMITS",
            phase="gas",
            mass_rate_kg_h=separation_result.clean_syngas_kg_h,
            temperature_c=separation_result.assumptions.get("condenser_exit_temp_c", 35.0),
            description="Non-condensable fuel gas stream",
        )

        streams["S109_CYCLONE_FINES_LOSS"] = StreamFlow(
            stream_id="S109",
            name="Cyclone Particulate Fines Loss",
            source_unit="CYCLONE_C101",
            destination_unit="EFFLUENT_TREATMENT",
            phase="solid",
            mass_rate_kg_h=separation_result.cyclone_fines_loss_kg_h,
            temperature_c=reactor_output.operating_temperature_c,
            description="Uncaptured char particulate carried over in gas stream",
        )

        # 4. Totals and Closure Calculation
        total_input = raw_feed_rate_kg_h + carrier_gas_flow
        
        # Total accounted output: Dryer exhaust + Recovered Biochar + Bio-oil + Syngas + Fines loss
        total_output = (
            drying_result.water_evaporated_kg_h
            + separation_result.recovered_biochar_kg_h
            + separation_result.recovered_bio_oil_liquid_kg_h
            + separation_result.clean_syngas_kg_h
            + separation_result.cyclone_fines_loss_kg_h
        )

        total_losses = total_input - total_output
        closure_pct = (total_output / total_input) * 100.0 if total_input > 0 else 0.0
        closure_error_pct = abs(100.0 - closure_pct)

        warnings: List[str] = []
        is_balanced = closure_error_pct <= self.closure_tolerance_pct
        status = "PASS" if is_balanced else "FAIL"

        if not is_balanced:
            warnings.append(
                f"Mass balance closure deviation ({closure_error_pct:.4f}%) exceeds tolerance ({self.closure_tolerance_pct}%)."
            )

        if feedstock.proximate.moisture > 40.0:
            warnings.append(
                f"High feedstock moisture ({feedstock.proximate.moisture}%) results in significant drying load."
            )

        return MassBalanceSummary(
            total_input_kg_h=total_input,
            total_output_kg_h=total_output,
            total_losses_kg_h=total_losses,
            closure_pct=closure_pct,
            closure_error_pct=closure_error_pct,
            streams=streams,
            is_balanced=is_balanced,
            status=status,
            warnings=warnings,
            biochar_recovered_kg_h=separation_result.recovered_biochar_kg_h,
            bio_oil_recovered_kg_h=separation_result.recovered_bio_oil_liquid_kg_h,
            syngas_recovered_kg_h=separation_result.clean_syngas_kg_h,
            dryer_water_evap_kg_h=drying_result.water_evaporated_kg_h,
            cyclone_fines_kg_h=separation_result.cyclone_fines_loss_kg_h,
        )
