"""Pyrolysis reactor unit operation model.

Integrates kinetic/empirical yield models with thermal duty calculations,
accounting for sensible feedstock heating, residual moisture evaporation, reaction enthalpy,
and product phase partitioning.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from src.data.feedstock import BiomassFeedstock
from src.models.yield_model import EmpiricalPyrolysisYieldModel, YieldFractions


@dataclass
class ReactorConfig:
    """Operating conditions and thermal parameters for the pyrolysis reactor.

    Attributes:
        temperature_c: Reactor core operating temperature (°C).
        heating_rate_c_min: Average biomass heating rate (°C/min).
        residence_time_min: Nominal solids/vapor residence time (min).
        inlet_temperature_c: Temperature of dried feedstock entering reactor (°C).
        reaction_enthalpy_kj_kg: Net pyrolysis reaction heat on dry basis (kJ/kg, endothermic > 0).
        heat_loss_fraction: Reactor wall/shell thermal heat loss as fraction of sensible/reaction duty.
        carrier_gas_flow_kg_h: Inert sweep gas (N2) mass flow rate (kg/h).
    """
    temperature_c: float = 500.0
    heating_rate_c_min: float = 10.0
    residence_time_min: float = 20.0
    inlet_temperature_c: float = 105.0
    reaction_enthalpy_kj_kg: float = 300.0
    heat_loss_fraction: float = 0.08
    carrier_gas_flow_kg_h: float = 0.0

    def __post_init__(self) -> None:
        if not (250.0 <= self.temperature_c <= 950.0):
            raise ValueError(f"Pyrolysis temperature must be in [250, 950] °C. Got: {self.temperature_c}")
        if self.heating_rate_c_min <= 0.0:
            raise ValueError(f"Heating rate must be > 0. Got: {self.heating_rate_c_min}")
        if self.residence_time_min <= 0.0:
            raise ValueError(f"Residence time must be > 0. Got: {self.residence_time_min}")
        if not (0.0 <= self.heat_loss_fraction < 0.5):
            raise ValueError(f"Heat loss fraction must be in [0, 0.5). Got: {self.heat_loss_fraction}")


@dataclass
class ReactorOutput:
    """Mass flow rates, product yields, and energy demands of the pyrolysis reactor."""
    feed_rate_in_kg_h: float
    char_mass_rate_kg_h: float
    bio_oil_organics_kg_h: float
    pyrolytic_water_kg_h: float
    residual_moisture_vapor_kg_h: float
    total_bio_oil_vapors_kg_h: float
    syngas_mass_rate_kg_h: float
    carrier_gas_kg_h: float
    total_product_rate_kg_h: float
    yields_daf: YieldFractions
    yields_dry: YieldFractions
    reactor_thermal_duty_kw: float
    reactor_thermal_duty_mj_h: float
    sensible_heating_duty_kw: float
    reaction_duty_kw: float
    heat_loss_kw: float
    operating_temperature_c: float
    char_hhv_mj_kg: float
    dry_bio_oil_hhv_mj_kg: float
    syngas_lhv_mj_kg: float
    assumptions: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feed_rate_in_kg_h": round(self.feed_rate_in_kg_h, 3),
            "char_mass_rate_kg_h": round(self.char_mass_rate_kg_h, 3),
            "bio_oil_organics_kg_h": round(self.bio_oil_organics_kg_h, 3),
            "pyrolytic_water_kg_h": round(self.pyrolytic_water_kg_h, 3),
            "total_bio_oil_vapors_kg_h": round(self.total_bio_oil_vapors_kg_h, 3),
            "syngas_mass_rate_kg_h": round(self.syngas_mass_rate_kg_h, 3),
            "total_product_rate_kg_h": round(self.total_product_rate_kg_h, 3),
            "yields_dry": self.yields_dry.to_dict(),
            "yields_daf": self.yields_daf.to_dict(),
            "reactor_thermal_duty_kw": round(self.reactor_thermal_duty_kw, 3),
            "reactor_thermal_duty_mj_h": round(self.reactor_thermal_duty_mj_h, 3),
            "operating_temperature_c": self.operating_temperature_c,
            "product_heating_values": {
                "char_hhv_mj_kg": round(self.char_hhv_mj_kg, 2),
                "dry_bio_oil_hhv_mj_kg": round(self.dry_bio_oil_hhv_mj_kg, 2),
                "syngas_lhv_mj_kg": round(self.syngas_lhv_mj_kg, 2),
            }
        }


class PyrolysisReactor:
    """Pyrolysis reactor unit model."""

    def __init__(
        self,
        config: Optional[ReactorConfig] = None,
        yield_model: Optional[EmpiricalPyrolysisYieldModel] = None,
    ) -> None:
        self.config = config or ReactorConfig()
        self.yield_model = yield_model or EmpiricalPyrolysisYieldModel()

    def process(
        self,
        dried_feed_rate_kg_h: float,
        residual_moisture_pct: float,
        feedstock: BiomassFeedstock,
        temp_override: Optional[float] = None,
        heating_rate_override: Optional[float] = None,
        residence_time_override: Optional[float] = None,
    ) -> ReactorOutput:
        """Execute pyrolysis reactor mass and energy conversion.

        Args:
            dried_feed_rate_kg_h: Mass rate of dried biomass entering reactor (kg/h).
            residual_moisture_pct: Residual moisture of entering biomass (wt%).
            feedstock: BiomassFeedstock providing chemical and property correlations.
            temp_override: Optional override for reactor temperature (°C).
            heating_rate_override: Optional override for heating rate (°C/min).
            residence_time_override: Optional override for residence time (min).

        Returns:
            ReactorOutput containing product flows and energy consumption.
        """
        if dried_feed_rate_kg_h <= 0:
            raise ValueError(f"Dried feed rate must be > 0. Got: {dried_feed_rate_kg_h}")

        temp_c = temp_override if temp_override is not None else self.config.temperature_c
        hr_c_min = heating_rate_override if heating_rate_override is not None else self.config.heating_rate_c_min
        res_time = residence_time_override if residence_time_override is not None else self.config.residence_time_min
        t_in = self.config.inlet_temperature_c

        # 1. Mass decomposition of feed into dry matter and residual moisture
        dry_matter_mass_kg_h = dried_feed_rate_kg_h * (1.0 - (residual_moisture_pct / 100.0))
        residual_water_kg_h = dried_feed_rate_kg_h * (residual_moisture_pct / 100.0)

        # 2. Yield calculation via yield model
        daf_yields, dry_yields = self.yield_model.predict_yields(
            temperature_c=temp_c,
            heating_rate_c_min=hr_c_min,
            residence_time_min=res_time,
            feedstock=feedstock,
        )

        # 3. Product mass rates from dry matter
        m_char = dry_matter_mass_kg_h * dry_yields.biochar_yield
        m_syngas = dry_matter_mass_kg_h * dry_yields.syngas_yield
        m_bio_oil_dry = dry_matter_mass_kg_h * dry_yields.bio_oil_yield

        # Pyrolytic reaction water formed from volatile organic deoxygenation reactions
        # Typically ~12 wt% of dry bio-oil fraction
        pyrolytic_water_fraction = 0.12
        m_pyrolytic_water = m_bio_oil_dry * pyrolytic_water_fraction
        m_bio_oil_organics = m_bio_oil_dry * (1.0 - pyrolytic_water_fraction)

        # Total condensable bio-oil vapors includes organics + pyrolytic water + evaporated residual water
        m_total_bio_oil_vapors = m_bio_oil_organics + m_pyrolytic_water + residual_water_kg_h

        # Overall reactor product mass flow
        m_carrier = self.config.carrier_gas_flow_kg_h
        m_total_product = m_char + m_total_bio_oil_vapors + m_syngas + m_carrier

        # 4. Thermal Energy Requirements
        # A. Sensible heating of biomass dry matter from T_in to T_reactor
        t_mean = (t_in + temp_c) / 2.0
        cp_dry_bio = feedstock.specific_heat_capacity(t_mean)
        q_sens_dry_solid = dry_matter_mass_kg_h * cp_dry_bio * (temp_c - t_in)

        # B. Sensible heating & vaporization of residual moisture if T_in < 100 °C
        # If T_in >= 100 °C (from 105 °C dryer), water enters as vapor and is superheated to T_reactor
        cp_steam = 2.01  # kJ/(kg*K)
        q_sens_residual_water = residual_water_kg_h * cp_steam * (temp_c - t_in)

        # C. Pyrolysis reaction enthalpy
        q_reaction = dry_matter_mass_kg_h * self.config.reaction_enthalpy_kj_kg

        # D. Carrier gas sensible heating if present
        cp_n2 = 1.04  # kJ/(kg*K)
        q_carrier = m_carrier * cp_n2 * (temp_c - 25.0)

        # Subtotal reactor internal thermal demand
        q_internal_kj_h = q_sens_dry_solid + q_sens_residual_water + q_reaction + q_carrier

        # E. Wall heat loss
        q_loss_kj_h = q_internal_kj_h * self.config.heat_loss_fraction
        q_total_thermal_kj_h = q_internal_kj_h + q_loss_kj_h

        q_total_kw = q_total_thermal_kj_h / 3600.0
        q_total_mj_h = q_total_thermal_kj_h / 1000.0

        # 5. Estimated Higher/Lower Heating Values of Products based on feedstock energy content
        lhv_feed_dry = feedstock.calculate_lhv_dry()

        # Biochar HHV: Carbon-enriched solid matrix (typically 1.25 - 1.35x feed LHV on DAF basis)
        ash_in_char_pct = (feedstock.ultimate.ash / dry_yields.biochar_yield) if dry_yields.biochar_yield > 0 else 0
        char_hhv = max(14.0, min(29.0, (lhv_feed_dry * 1.32) * (1.0 - ash_in_char_pct / 100.0)))

        # Dry bio-oil organics HHV: ~0.95 - 1.05x feed LHV
        dry_bio_oil_hhv = max(15.0, min(23.0, lhv_feed_dry * 1.02))

        # Syngas LHV: ~0.45 - 0.55x feed LHV (CO, H2, CH4, CO2 mix, approx 8.5 - 11.5 MJ/kg)
        syngas_lhv = max(7.0, min(11.5, lhv_feed_dry * 0.50))

        assumptions = {
            "reaction_enthalpy_kj_kg": self.config.reaction_enthalpy_kj_kg,
            "pyrolytic_water_fraction_of_bio_oil": pyrolytic_water_fraction,
            "heat_loss_fraction": self.config.heat_loss_fraction,
            "carrier_gas_n2_kg_h": m_carrier,
        }

        return ReactorOutput(
            feed_rate_in_kg_h=dried_feed_rate_kg_h,
            char_mass_rate_kg_h=m_char,
            bio_oil_organics_kg_h=m_bio_oil_organics,
            pyrolytic_water_kg_h=m_pyrolytic_water,
            residual_moisture_vapor_kg_h=residual_water_kg_h,
            total_bio_oil_vapors_kg_h=m_total_bio_oil_vapors,
            syngas_mass_rate_kg_h=m_syngas,
            carrier_gas_kg_h=m_carrier,
            total_product_rate_kg_h=m_total_product,
            yields_daf=daf_yields,
            yields_dry=dry_yields,
            reactor_thermal_duty_kw=q_total_kw,
            reactor_thermal_duty_mj_h=q_total_mj_h,
            sensible_heating_duty_kw=(q_sens_dry_solid + q_sens_residual_water) / 3600.0,
            reaction_duty_kw=q_reaction / 3600.0,
            heat_loss_kw=q_loss_kj_h / 3600.0,
            operating_temperature_c=temp_c,
            char_hhv_mj_kg=char_hhv,
            dry_bio_oil_hhv_mj_kg=dry_bio_oil_hhv,
            syngas_lhv_mj_kg=syngas_lhv,
            assumptions=assumptions,
        )
