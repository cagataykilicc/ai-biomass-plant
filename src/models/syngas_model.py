"""Thermodynamic syngas speciation, gas equilibrium, and volumetric property model.

Predicts molecular composition (CO, CO2, CH4, H2, C2H6, H2O, N2), mean molecular weight,
standard volumetric flow (Nm3/h), and volumetric/mass heating values as functions of
pyrolysis reactor temperature and feedstock properties.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import math

from src.data.feedstock import BiomassFeedstock

# Molecular weights (kg/kmol or g/mol)
MW_H2 = 2.016
MW_CO = 28.010
MW_CO2 = 44.010
MW_CH4 = 16.043
MW_C2H6 = 30.070  # Representative light hydrocarbon
MW_H2O = 18.015
MW_N2 = 28.013

# Species Lower Heating Values (MJ/kg on mass basis)
LHV_H2_MJ_KG = 120.0
LHV_CO_MJ_KG = 10.10
LHV_CH4_MJ_KG = 50.00
LHV_C2H6_MJ_KG = 47.50
LHV_CO2_MJ_KG = 0.0
LHV_H2O_MJ_KG = 0.0
LHV_N2_MJ_KG = 0.0

# Standard molar volume of ideal gas at 0 °C and 1.01325 bar (Nm3/kmol)
STANDARD_MOLAR_VOLUME_NM3_KMOL = 22.414


@dataclass
class SyngasComposition:
    """Detailed molecular speciation, molar fractions, and physical properties of syngas.

    Attributes:
        molar_fractions: Mole fraction of each gas species (sum = 1.0).
        mass_fractions: Mass fraction of each gas species (sum = 1.0).
        mass_flow_rates_kg_h: Mass rate of each individual component (kg/h).
        total_mass_flow_kg_h: Total syngas mass flow (kg/h).
        mean_molecular_weight_kg_kmol: Average molecular weight of mixture (kg/kmol).
        standard_volume_flow_nm3_h: Volumetric flow at standard conditions (Nm3/h).
        lhv_mass_mj_kg: Lower Heating Value of gas mixture on mass basis (MJ/kg).
        lhv_vol_mj_nm3: Lower Heating Value of gas mixture on standard volume basis (MJ/Nm3).
        hhv_vol_mj_nm3: Higher Heating Value on volume basis (MJ/Nm3).
        elemental_mass_flow_kg_h: C, H, O, N mass contained in the gas stream (kg/h).
    """
    molar_fractions: Dict[str, float]
    mass_fractions: Dict[str, float]
    mass_flow_rates_kg_h: Dict[str, float]
    total_mass_flow_kg_h: float
    mean_molecular_weight_kg_kmol: float
    standard_volume_flow_nm3_h: float
    lhv_mass_mj_kg: float
    lhv_vol_mj_nm3: float
    hhv_vol_mj_nm3: float
    elemental_mass_flow_kg_h: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_mass_flow_kg_h": round(self.total_mass_flow_kg_h, 3),
            "standard_volume_flow_nm3_h": round(self.standard_volume_flow_nm3_h, 3),
            "mean_molecular_weight_kg_kmol": round(self.mean_molecular_weight_kg_kmol, 3),
            "lhv_mass_mj_kg": round(self.lhv_mass_mj_kg, 2),
            "lhv_vol_mj_nm3": round(self.lhv_vol_mj_nm3, 2),
            "hhv_vol_mj_nm3": round(self.hhv_vol_mj_nm3, 2),
            "molar_fractions_pct": {k: round(v * 100.0, 2) for k, v in self.molar_fractions.items()},
            "mass_fractions_pct": {k: round(v * 100.0, 2) for k, v in self.mass_fractions.items()},
            "mass_flow_rates_kg_h": {k: round(v, 3) for k, v in self.mass_flow_rates_kg_h.items()},
            "elemental_mass_flow_kg_h": {k: round(v, 3) for k, v in self.elemental_mass_flow_kg_h.items()},
        }


class SyngasSpeciationModel:
    """Predicts temperature-dependent pyrolysis gas speciation and thermodynamics."""

    def __init__(self) -> None:
        self.mw_map = {
            "H2": MW_H2,
            "CO": MW_CO,
            "CO2": MW_CO2,
            "CH4": MW_CH4,
            "C2H6": MW_C2H6,
            "H2O": MW_H2O,
            "N2": MW_N2,
        }
        self.lhv_map = {
            "H2": LHV_H2_MJ_KG,
            "CO": LHV_CO_MJ_KG,
            "CO2": LHV_CO2_MJ_KG,
            "CH4": LHV_CH4_MJ_KG,
            "C2H6": LHV_C2H6_MJ_KG,
            "H2O": LHV_H2O_MJ_KG,
            "N2": LHV_N2_MJ_KG,
        }

    def predict_speciation(
        self,
        temperature_c: float,
        syngas_mass_flow_kg_h: float,
        carrier_gas_n2_kg_h: float = 0.0,
        feedstock: Optional[BiomassFeedstock] = None,
    ) -> SyngasComposition:
        """Calculate molecular speciation and thermodynamic properties of syngas.

        Args:
            temperature_c: Reactor temperature (°C).
            syngas_mass_flow_kg_h: Total pure syngas mass generation rate (kg/h).
            carrier_gas_n2_kg_h: Inert N2 sweep gas flow rate (kg/h).
            feedstock: BiomassFeedstock providing composition context.

        Returns:
            SyngasComposition object with molar, volumetric, and elemental properties.
        """
        if syngas_mass_flow_kg_h < 0:
            raise ValueError(f"Syngas flow rate cannot be negative. Got: {syngas_mass_flow_kg_h}")

        total_gas_mass = syngas_mass_flow_kg_h + carrier_gas_n2_kg_h
        if total_gas_mass <= 1e-9:
            # Handle zero gas edge case
            empty_dict = {k: 0.0 for k in self.mw_map}
            return SyngasComposition(
                molar_fractions=empty_dict,
                mass_fractions=empty_dict,
                mass_flow_rates_kg_h=empty_dict,
                total_mass_flow_kg_h=0.0,
                mean_molecular_weight_kg_kmol=28.0,
                standard_volume_flow_nm3_h=0.0,
                lhv_mass_mj_kg=0.0,
                lhv_vol_mj_nm3=0.0,
                hhv_vol_mj_nm3=0.0,
                elemental_mass_flow_kg_h={"C": 0.0, "H": 0.0, "O": 0.0, "N": 0.0},
            )

        # Base molar fractions on dry carrier-free basis as a function of temperature T (°C)
        # Normalized logistic / polynomial functions derived from literature pyrolysis data
        t = max(250.0, min(900.0, temperature_c))

        # 1. CO2 fraction: Decreases as temperature rises (decarboxylation dominates early at <450 °C)
        # Fraction ~ 0.55 at 350 °C, ~ 0.35 at 500 °C, ~ 0.18 at 750 °C
        y_co2_raw = 0.15 + (0.45 / (1.0 + math.exp((t - 440.0) / 70.0)))

        # 2. CO fraction: Increases with temperature due to primary decarbonylation and secondary cracking
        # Fraction ~ 0.28 at 350 °C, ~ 0.42 at 500 °C, ~ 0.48 at 750 °C
        y_co_raw = 0.25 + (0.25 / (1.0 + math.exp(-(t - 470.0) / 75.0)))

        # 3. CH4 fraction: Increases with temperature due to methanation and alkyl cracking
        # Fraction ~ 0.06 at 350 °C, ~ 0.12 at 500 °C, ~ 0.16 at 750 °C
        y_ch4_raw = 0.04 + (0.13 / (1.0 + math.exp(-(t - 480.0) / 80.0)))

        # 4. H2 fraction: Drastically surges above 500 °C due to dehydrogenation and secondary cracking
        # Fraction ~ 0.01 at 350 °C, ~ 0.05 at 500 °C, ~ 0.16 at 750 °C
        y_h2_raw = 0.005 + (0.18 / (1.0 + math.exp(-(t - 580.0) / 60.0)))

        # 5. C2H6 / light hydrocarbon fraction: ~ 0.03 - 0.05
        y_c2h6_raw = 0.02 + (0.03 / (1.0 + math.exp(-(t - 450.0) / 100.0)))

        # 6. Trace pyrolytic gas moisture (H2O in non-condensable phase at exit)
        y_h2o_raw = 0.02

        # Normalize raw molar fractions of the generated syngas
        sum_raw = y_co2_raw + y_co_raw + y_ch4_raw + y_h2_raw + y_c2h6_raw + y_h2o_raw
        raw_moles = {
            "CO2": y_co2_raw / sum_raw,
            "CO": y_co_raw / sum_raw,
            "CH4": y_ch4_raw / sum_raw,
            "H2": y_h2_raw / sum_raw,
            "C2H6": y_c2h6_raw / sum_raw,
            "H2O": y_h2o_raw / sum_raw,
        }

        # Calculate mean molecular weight of pure generated syngas
        mw_pure_syngas = sum(raw_moles[k] * self.mw_map[k] for k in raw_moles)

        # Molar flow rates (kmol/h)
        moles_pure_syngas_kmol_h = syngas_mass_flow_kg_h / mw_pure_syngas if mw_pure_syngas > 0 else 0.0
        moles_n2_kmol_h = carrier_gas_n2_kg_h / MW_N2

        total_moles_kmol_h = moles_pure_syngas_kmol_h + moles_n2_kmol_h

        # Compute actual molar flow and molar fractions including carrier N2
        moles_dict: Dict[str, float] = {}
        for sp, frac in raw_moles.items():
            moles_dict[sp] = moles_pure_syngas_kmol_h * frac
        moles_dict["N2"] = moles_n2_kmol_h

        molar_fractions: Dict[str, float] = {
            k: (v / total_moles_kmol_h) if total_moles_kmol_h > 0 else 0.0
            for k, v in moles_dict.items()
        }

        # Mass flow rates (kg/h) and mass fractions
        mass_flow_dict: Dict[str, float] = {
            k: moles_dict[k] * self.mw_map[k] for k in moles_dict
        }
        total_calc_mass = sum(mass_flow_dict.values())
        mass_fractions: Dict[str, float] = {
            k: (v / total_calc_mass) if total_calc_mass > 0 else 0.0
            for k, v in mass_flow_dict.items()
        }

        # Mean molecular weight of combined mixture
        mean_mw = total_calc_mass / total_moles_kmol_h if total_moles_kmol_h > 0 else 28.0

        # Standard volumetric flow (Nm3/h)
        std_vol_flow_nm3_h = total_moles_kmol_h * STANDARD_MOLAR_VOLUME_NM3_KMOL

        # Heating values
        # Mass-basis LHV (MJ/kg) = sum(x_i * LHV_i)
        lhv_mass = sum(mass_fractions[k] * self.lhv_map[k] for k in mass_fractions)

        # Volume-basis LHV (MJ/Nm3) = (total_mass * LHV_mass) / std_vol_flow
        lhv_vol = (total_calc_mass * lhv_mass) / std_vol_flow_nm3_h if std_vol_flow_nm3_h > 0 else 0.0

        # HHV estimate on volumetric basis (MJ/Nm3)
        # HHV includes latent heat of condensed moisture from H2 and CH4 combustion
        hhv_vol = lhv_vol + (molar_fractions["H2"] * 1.80) + (molar_fractions["CH4"] * 4.20) + (molar_fractions["C2H6"] * 5.80)

        # Elemental C, H, O, N mass distribution in syngas (kg/h)
        # C mass: CO (12/28), CO2 (12/44), CH4 (12/16), C2H6 (24/30)
        c_mass = (
            mass_flow_dict["CO"] * (12.011 / MW_CO)
            + mass_flow_dict["CO2"] * (12.011 / MW_CO2)
            + mass_flow_dict["CH4"] * (12.011 / MW_CH4)
            + mass_flow_dict["C2H6"] * (24.022 / MW_C2H6)
        )

        # H mass: H2 (1.0), CH4 (4/16), C2H6 (6/30), H2O (2/18)
        h_mass = (
            mass_flow_dict["H2"]
            + mass_flow_dict["CH4"] * (4.032 / MW_CH4)
            + mass_flow_dict["C2H6"] * (6.048 / MW_C2H6)
            + mass_flow_dict["H2O"] * (2.016 / MW_H2O)
        )

        # O mass: CO (16/28), CO2 (32/44), H2O (16/18)
        o_mass = (
            mass_flow_dict["CO"] * (15.999 / MW_CO)
            + mass_flow_dict["CO2"] * (31.998 / MW_CO2)
            + mass_flow_dict["H2O"] * (15.999 / MW_H2O)
        )

        # N mass: N2
        n_mass = mass_flow_dict["N2"]

        elemental_gas = {
            "carbon_kg_h": max(0.0, c_mass),
            "hydrogen_kg_h": max(0.0, h_mass),
            "oxygen_kg_h": max(0.0, o_mass),
            "nitrogen_kg_h": max(0.0, n_mass),
        }

        return SyngasComposition(
            molar_fractions=molar_fractions,
            mass_fractions=mass_fractions,
            mass_flow_rates_kg_h=mass_flow_dict,
            total_mass_flow_kg_h=total_calc_mass,
            mean_molecular_weight_kg_kmol=mean_mw,
            standard_volume_flow_nm3_h=std_vol_flow_nm3_h,
            lhv_mass_mj_kg=lhv_mass,
            lhv_vol_mj_nm3=lhv_vol,
            hhv_vol_mj_nm3=hhv_vol,
            elemental_mass_flow_kg_h=elemental_gas,
        )
