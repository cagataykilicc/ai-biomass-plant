"""Product separation, cyclone particulate recovery, and bio-oil condensation train model.

Models downstream separation of solid biochar from hot pyrolytic vapors via cyclone,
multistage condensation of liquid bio-oil (aqueous + organic fractions),
cooling thermal duty calculations, and syngas purification.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional

from src.process.reactor import ReactorOutput


CP_COOLING_WATER_KJ_KG_K = 4.184


@dataclass
class SeparationConfig:
    """Design and performance parameters for product separation train.

    Attributes:
        cyclone_efficiency: Mechanical recovery fraction of biochar particulate (0 < eta <= 1.0).
        condenser_efficiency: Recovery fraction of condensable bio-oil vapors into liquid phase (0 < eta <= 1.0).
        condenser_exit_temp_c: Final exit temperature of condensed bio-oil and cooled syngas (°C).
        cooling_water_inlet_c: Inlet cooling water utility temperature (°C).
        cooling_water_outlet_c: Outlet cooling water utility return temperature (°C).
        auxiliary_power_kw: Auxiliary pump/blower electrical load for separation section (kW).
    """
    cyclone_efficiency: float = 0.985
    condenser_efficiency: float = 0.960
    condenser_exit_temp_c: float = 35.0
    cooling_water_inlet_c: float = 20.0
    cooling_water_outlet_c: float = 32.0
    auxiliary_power_kw: float = 1.5

    def __post_init__(self) -> None:
        if not (0.0 < self.cyclone_efficiency <= 1.0):
            raise ValueError(f"Cyclone efficiency must be in (0, 1.0]. Got: {self.cyclone_efficiency}")
        if not (0.0 < self.condenser_efficiency <= 1.0):
            raise ValueError(f"Condenser efficiency must be in (0, 1.0]. Got: {self.condenser_efficiency}")
        if self.condenser_exit_temp_c < self.cooling_water_inlet_c:
            raise ValueError("Condenser exit temperature cannot be lower than cooling water inlet temperature.")


@dataclass
class SeparationResult:
    """Material stream flows and cooling duties from product separation."""
    recovered_biochar_kg_h: float
    cyclone_fines_loss_kg_h: float
    recovered_bio_oil_liquid_kg_h: float
    bio_oil_organics_kg_h: float
    bio_oil_water_kg_h: float
    bio_oil_water_content_pct: float
    clean_syngas_kg_h: float
    uncondensed_vapors_in_syngas_kg_h: float
    condenser_cooling_duty_kw: float
    condenser_cooling_duty_mj_h: float
    cooling_water_rate_kg_h: float
    liquid_bio_oil_hhv_mj_kg: float
    cyclone_efficiency: float
    condenser_efficiency: float
    assumptions: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recovered_biochar_kg_h": round(self.recovered_biochar_kg_h, 3),
            "cyclone_fines_loss_kg_h": round(self.cyclone_fines_loss_kg_h, 3),
            "recovered_bio_oil_liquid_kg_h": round(self.recovered_bio_oil_liquid_kg_h, 3),
            "bio_oil_organics_kg_h": round(self.bio_oil_organics_kg_h, 3),
            "bio_oil_water_kg_h": round(self.bio_oil_water_kg_h, 3),
            "bio_oil_water_content_pct": round(self.bio_oil_water_content_pct, 2),
            "clean_syngas_kg_h": round(self.clean_syngas_kg_h, 3),
            "uncondensed_vapors_in_syngas_kg_h": round(self.uncondensed_vapors_in_syngas_kg_h, 3),
            "condenser_cooling_duty_kw": round(self.condenser_cooling_duty_kw, 3),
            "condenser_cooling_duty_mj_h": round(self.condenser_cooling_duty_mj_h, 3),
            "cooling_water_rate_kg_h": round(self.cooling_water_rate_kg_h, 2),
            "liquid_bio_oil_hhv_mj_kg": round(self.liquid_bio_oil_hhv_mj_kg, 2),
            "cyclone_efficiency": self.cyclone_efficiency,
            "condenser_efficiency": self.condenser_efficiency,
        }


class ProductSeparator:
    """Separator unit simulating solids cyclone and multi-stage condensation."""

    def __init__(self, config: Optional[SeparationConfig] = None) -> None:
        self.config = config or SeparationConfig()

    def process(
        self,
        reactor_output: ReactorOutput,
        cyclone_eff_override: Optional[float] = None,
        condenser_eff_override: Optional[float] = None,
    ) -> SeparationResult:
        """Perform separation and cooling calculations on pyrolysis reactor output stream.

        Args:
            reactor_output: Output stream data from PyrolysisReactor.
            cyclone_eff_override: Optional override for cyclone recovery efficiency.
            condenser_eff_override: Optional override for condenser vapor recovery efficiency.

        Returns:
            SeparationResult containing stream breakdowns and condenser cooling duties.
        """
        eta_cyc = cyclone_eff_override if cyclone_eff_override is not None else self.config.cyclone_efficiency
        eta_cond = condenser_eff_override if condenser_eff_override is not None else self.config.condenser_efficiency

        # 1. Cyclone Solids Separation
        m_char_in = reactor_output.char_mass_rate_kg_h
        m_char_recovered = m_char_in * eta_cyc
        m_char_fines_loss = m_char_in * (1.0 - eta_cyc)

        # 2. Condensation of Bio-oil Vapors
        m_oil_vapors_total = reactor_output.total_bio_oil_vapors_kg_h
        m_oil_recovered_total = m_oil_vapors_total * eta_cond
        m_uncondensed_vapors = m_oil_vapors_total * (1.0 - eta_cond)

        # Partition recovered bio-oil into organics and aqueous water fractions
        total_water_in_vapors = reactor_output.pyrolytic_water_kg_h + reactor_output.residual_moisture_vapor_kg_h
        total_organics_in_vapors = reactor_output.bio_oil_organics_kg_h

        water_ratio = total_water_in_vapors / m_oil_vapors_total if m_oil_vapors_total > 0 else 0.0
        organics_ratio = total_organics_in_vapors / m_oil_vapors_total if m_oil_vapors_total > 0 else 0.0

        m_oil_liquid_water = m_oil_recovered_total * water_ratio
        m_oil_liquid_organics = m_oil_recovered_total * organics_ratio

        bio_oil_water_pct = (m_oil_liquid_water / m_oil_recovered_total * 100.0) if m_oil_recovered_total > 0 else 0.0

        # Heating value of wet raw bio-oil (organics HHV diluted by water content)
        # Wet HHV = Dry_HHV * (1 - w_water) - 2.442 * w_water
        w_water_frac = bio_oil_water_pct / 100.0
        liquid_bio_oil_hhv = max(0.0, (reactor_output.dry_bio_oil_hhv_mj_kg * (1.0 - w_water_frac)) - (2.442 * w_water_frac))

        # 3. Syngas Purification
        m_syngas_in = reactor_output.syngas_mass_rate_kg_h + reactor_output.carrier_gas_kg_h
        # Uncondensed vapors and entrained fines exit in syngas stream (before final scrubbers)
        m_clean_syngas_total = m_syngas_in + m_uncondensed_vapors

        # 4. Condenser Cooling Duty Calculation
        # Vapors cool from T_reactor to T_condenser_exit
        t_hot = reactor_output.operating_temperature_c
        t_cold = self.config.condenser_exit_temp_c

        # A. Sensible cooling of condensable vapors in gas phase
        cp_oil_vapor = 2.10  # kJ/(kg*K)
        q_sens_vapor = m_oil_recovered_total * cp_oil_vapor * (t_hot - 100.0)

        # B. Latent heat of condensation of bio-oil organics (~850 kJ/kg) and water (~2257 kJ/kg)
        h_lat_organics = 850.0  # kJ/kg
        h_lat_water = 2257.0    # kJ/kg
        q_lat_cond = (m_oil_liquid_organics * h_lat_organics) + (m_oil_liquid_water * h_lat_water)

        # C. Sensible sub-cooling of condensed liquid bio-oil from 100 °C to T_cold
        cp_oil_liquid = 2.80  # kJ/(kg*K)
        q_sens_liquid = m_oil_recovered_total * cp_oil_liquid * (100.0 - t_cold)

        # D. Sensible cooling of non-condensable syngas stream from T_hot to T_cold
        cp_syngas = 1.35  # kJ/(kg*K)
        q_sens_syngas = m_clean_syngas_total * cp_syngas * (t_hot - t_cold)

        q_cooling_total_kj_h = q_sens_vapor + q_lat_cond + q_sens_liquid + q_sens_syngas
        q_cooling_kw = q_cooling_total_kj_h / 3600.0
        q_cooling_mj_h = q_cooling_total_kj_h / 1000.0

        # E. Cooling water utility requirement
        delta_t_cw = max(1.0, self.config.cooling_water_outlet_c - self.config.cooling_water_inlet_c)
        cooling_water_kg_h = q_cooling_total_kj_h / (CP_COOLING_WATER_KJ_KG_K * delta_t_cw)

        assumptions = {
            "condenser_exit_temp_c": t_cold,
            "latent_heat_organics_kj_kg": h_lat_organics,
            "latent_heat_water_kj_kg": h_lat_water,
            "cooling_water_delta_t_c": delta_t_cw,
        }

        return SeparationResult(
            recovered_biochar_kg_h=m_char_recovered,
            cyclone_fines_loss_kg_h=m_char_fines_loss,
            recovered_bio_oil_liquid_kg_h=m_oil_recovered_total,
            bio_oil_organics_kg_h=m_oil_liquid_organics,
            bio_oil_water_kg_h=m_oil_liquid_water,
            bio_oil_water_content_pct=bio_oil_water_pct,
            clean_syngas_kg_h=m_clean_syngas_total,
            uncondensed_vapors_in_syngas_kg_h=m_uncondensed_vapors,
            condenser_cooling_duty_kw=q_cooling_kw,
            condenser_cooling_duty_mj_h=q_cooling_mj_h,
            cooling_water_rate_kg_h=cooling_water_kg_h,
            liquid_bio_oil_hhv_mj_kg=liquid_bio_oil_hhv,
            cyclone_efficiency=eta_cyc,
            condenser_efficiency=eta_cond,
            assumptions=assumptions,
        )
