"""Syngas combustor, burner aerodynamics, flue gas thermodynamics, and plant heat integration.

Models combustion of product syngas with excess air, calculates adiabatic/actual flame
and flue gas temperatures, heat exchanger recovery duty, and plant Thermal Self-Sufficiency Index (TSI).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import math

from src.models.syngas_model import SyngasComposition, MW_CO, MW_H2, MW_CH4, MW_C2H6


# Air composition: 21% O2, 79% N2 molar (~23.2% O2, 76.8% N2 mass)
MW_AIR = 28.96
MW_O2 = 31.999
MW_N2 = 28.013
MW_CO2 = 44.010
MW_H2O = 18.015
CP_FLUE_GAS_KJ_KG_K = 1.18  # Average specific heat capacity of hot flue gas


@dataclass
class CombustorConfig:
    """Design specifications for syngas combustion chamber and heat recovery boiler/exchanger.

    Attributes:
        excess_air_ratio: Excess air coefficient lambda (typically 1.15 - 1.30).
        combustion_efficiency: Burner thermal conversion efficiency (0 < eta <= 1.0).
        heat_recovery_efficiency: Exchanger thermal recovery efficiency (0 < eta <= 1.0).
        flue_gas_exit_temp_c: Stack discharge temperature after heat recovery (°C).
        ambient_air_temp_c: Inlet ambient combustion air temperature (°C).
        auxiliary_fan_power_kw: Forced-draft burner fan and flue gas blower load (kW).
    """
    excess_air_ratio: float = 1.20
    combustion_efficiency: float = 0.985
    heat_recovery_efficiency: float = 0.850
    flue_gas_exit_temp_c: float = 140.0
    ambient_air_temp_c: float = 25.0
    auxiliary_fan_power_kw: float = 1.2

    def __post_init__(self) -> None:
        if self.excess_air_ratio < 1.0:
            raise ValueError(f"Excess air ratio must be >= 1.0. Got: {self.excess_air_ratio}")
        if not (0.0 < self.combustion_efficiency <= 1.0):
            raise ValueError(f"Combustion efficiency must be in (0, 1.0]. Got: {self.combustion_efficiency}")
        if not (0.0 < self.heat_recovery_efficiency <= 1.0):
            raise ValueError(f"Heat recovery efficiency must be in (0, 1.0]. Got: {self.heat_recovery_efficiency}")


@dataclass
class CombustionResult:
    """Thermal output, air requirements, flue gas thermodynamics, and self-sufficiency KPIs."""
    thermal_heat_released_kw: float
    thermal_heat_recovered_kw: float
    stoichiometric_air_rate_kg_h: float
    actual_combustion_air_rate_kg_h: float
    flue_gas_mass_flow_kg_h: float
    flue_gas_actual_temp_c: float
    flue_gas_stack_temp_c: float
    thermal_self_sufficiency_index_pct: float
    net_external_heat_required_kw: float
    surplus_heat_available_kw: float
    flue_gas_composition_vol_pct: Dict[str, float]
    is_thermally_self_sufficient: bool
    assumptions: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "thermal_heat_released_kw": round(self.thermal_heat_released_kw, 2),
            "thermal_heat_recovered_kw": round(self.thermal_heat_recovered_kw, 2),
            "stoichiometric_air_rate_kg_h": round(self.stoichiometric_air_rate_kg_h, 2),
            "actual_combustion_air_rate_kg_h": round(self.actual_combustion_air_rate_kg_h, 2),
            "flue_gas_mass_flow_kg_h": round(self.flue_gas_mass_flow_kg_h, 2),
            "flue_gas_actual_temp_c": round(self.flue_gas_actual_temp_c, 1),
            "flue_gas_stack_temp_c": round(self.flue_gas_stack_temp_c, 1),
            "thermal_self_sufficiency_index_pct": round(self.thermal_self_sufficiency_index_pct, 2),
            "net_external_heat_required_kw": round(self.net_external_heat_required_kw, 2),
            "surplus_heat_available_kw": round(self.surplus_heat_available_kw, 2),
            "is_thermally_self_sufficient": self.is_thermally_self_sufficient,
            "flue_gas_composition_vol_pct": {
                k: round(v, 2) for k, v in self.flue_gas_composition_vol_pct.items()
            },
        }


class SyngasCombustor:
    """Combustor simulator for syngas utilization and plant waste heat recovery."""

    def __init__(self, config: Optional[CombustorConfig] = None) -> None:
        self.config = config or CombustorConfig()

    def process(
        self,
        syngas: SyngasComposition,
        total_plant_thermal_demand_kw: float,
    ) -> CombustionResult:
        """Simulate syngas combustion and calculate heat recovery to meet plant thermal duties.

        Args:
            syngas: Detailed SyngasComposition from syngas speciation model.
            total_plant_thermal_demand_kw: Total drying + reactor thermal demand (kW).

        Returns:
            CombustionResult with thermal outputs, flue gas flows, and self-sufficiency metrics.
        """
        # 1. Stoichiometric O2 requirement (kmol/h) based on combustible species
        # CO + 0.5 O2 -> CO2
        # H2 + 0.5 O2 -> H2O
        # CH4 + 2 O2 -> CO2 + 2 H2O
        # C2H6 + 3.5 O2 -> 2 CO2 + 3 H2O
        masses = syngas.mass_flow_rates_kg_h
        moles_co = masses.get("CO", 0.0) / MW_CO
        moles_h2 = masses.get("H2", 0.0) / MW_H2
        moles_ch4 = masses.get("CH4", 0.0) / MW_CH4
        moles_c2h6 = masses.get("C2H6", 0.0) / MW_C2H6

        o2_stoich_kmol_h = (0.5 * moles_co) + (0.5 * moles_h2) + (2.0 * moles_ch4) + (3.5 * moles_c2h6)
        
        # Stoichiometric air (kmol/h and kg/h)
        air_stoich_kmol_h = o2_stoich_kmol_h / 0.21
        air_stoich_kg_h = air_stoich_kmol_h * MW_AIR

        # Actual combustion air with excess coefficient
        air_actual_kg_h = air_stoich_kg_h * self.config.excess_air_ratio
        air_actual_kmol_h = air_actual_kg_h / MW_AIR
        o2_actual_kmol_h = air_actual_kmol_h * 0.21
        n2_air_kmol_h = air_actual_kmol_h * 0.79

        # 2. Thermal Energy Release
        # Q_comb = (m_syngas * LHV_syngas) / 3.6 * eta_comb
        raw_heat_input_kw = (syngas.total_mass_flow_kg_h * syngas.lhv_mass_mj_kg * 1000.0) / 3600.0
        q_released_kw = raw_heat_input_kw * self.config.combustion_efficiency

        # Recoverable heat through heat exchanger HX101
        q_recovered_kw = q_released_kw * self.config.heat_recovery_efficiency

        # 3. Flue Gas Products (kmol/h)
        # CO2 formed = initial CO2 + CO + CH4 + 2*C2H6
        moles_co2_in = masses.get("CO2", 0.0) / MW_CO2
        co2_flue_kmol_h = moles_co2_in + moles_co + moles_ch4 + (2.0 * moles_c2h6)

        # H2O formed = initial H2O + H2 + 2*CH4 + 3*C2H6
        moles_h2o_in = masses.get("H2O", 0.0) / MW_H2O
        h2o_flue_kmol_h = moles_h2o_in + moles_h2 + (2.0 * moles_ch4) + (3.0 * moles_c2h6)

        # Excess unreacted O2
        o2_excess_kmol_h = max(0.0, o2_actual_kmol_h - o2_stoich_kmol_h)

        # Total N2 in flue = N2 from combustion air + carrier N2 from syngas
        moles_n2_in = masses.get("N2", 0.0) / MW_N2
        n2_flue_kmol_h = n2_air_kmol_h + moles_n2_in

        total_flue_kmol_h = co2_flue_kmol_h + h2o_flue_kmol_h + o2_excess_kmol_h + n2_flue_kmol_h

        # Flue gas volume percentages (vol%)
        flue_vol_pct = {
            "CO2": (co2_flue_kmol_h / total_flue_kmol_h * 100.0) if total_flue_kmol_h > 0 else 0.0,
            "H2O": (h2o_flue_kmol_h / total_flue_kmol_h * 100.0) if total_flue_kmol_h > 0 else 0.0,
            "N2": (n2_flue_kmol_h / total_flue_kmol_h * 100.0) if total_flue_kmol_h > 0 else 0.0,
            "O2": (o2_excess_kmol_h / total_flue_kmol_h * 100.0) if total_flue_kmol_h > 0 else 0.0,
        }

        # Flue gas mass rate (kg/h) = Syngas mass + Actual Air mass
        flue_gas_mass_kg_h = syngas.total_mass_flow_kg_h + air_actual_kg_h

        # 4. Flue Gas Flame / Operating Temperature (°C)
        # Q_comb (kJ/h) = m_flue * Cp_flue * (T_flue - T_amb)
        q_comb_kj_h = q_released_kw * 3600.0
        t_amb = self.config.ambient_air_temp_c
        delta_t_flue = q_comb_kj_h / (flue_gas_mass_kg_h * CP_FLUE_GAS_KJ_KG_K) if flue_gas_mass_kg_h > 0 else 0.0
        t_flue_actual = min(1400.0, max(t_amb, t_amb + delta_t_flue))

        # 5. Plant Heat Integration & Self-Sufficiency Index (TSI)
        if total_plant_thermal_demand_kw > 0:
            tsi_pct = (q_recovered_kw / total_plant_thermal_demand_kw) * 100.0
        else:
            tsi_pct = 100.0

        is_self_sufficient = tsi_pct >= 100.0

        if is_self_sufficient:
            net_external_heat = 0.0
            surplus_heat = q_recovered_kw - total_plant_thermal_demand_kw
        else:
            net_external_heat = total_plant_thermal_demand_kw - q_recovered_kw
            surplus_heat = 0.0

        assumptions = {
            "excess_air_ratio": self.config.excess_air_ratio,
            "combustion_efficiency": self.config.combustion_efficiency,
            "heat_recovery_efficiency": self.config.heat_recovery_efficiency,
            "flue_gas_cp_kj_kg_k": CP_FLUE_GAS_KJ_KG_K,
        }

        return CombustionResult(
            thermal_heat_released_kw=q_released_kw,
            thermal_heat_recovered_kw=q_recovered_kw,
            stoichiometric_air_rate_kg_h=air_stoich_kg_h,
            actual_combustion_air_rate_kg_h=air_actual_kg_h,
            flue_gas_mass_flow_kg_h=flue_gas_mass_kg_h,
            flue_gas_actual_temp_c=t_flue_actual,
            flue_gas_stack_temp_c=self.config.flue_gas_exit_temp_c,
            thermal_self_sufficiency_index_pct=tsi_pct,
            net_external_heat_required_kw=net_external_heat,
            surplus_heat_available_kw=surplus_heat,
            flue_gas_composition_vol_pct=flue_vol_pct,
            is_thermally_self_sufficient=is_self_sufficient,
            assumptions=assumptions,
        )
