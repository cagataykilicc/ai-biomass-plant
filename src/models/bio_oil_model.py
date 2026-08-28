"""Bio-oil chemical grouping, acidity (TAN/pH), and physical property model.

Classifies crude pyrolytic bio-oil into primary chemical functional families
(carboxylic acids, phenolics, furans, anhydrosugars, aldehydes/ketones),
and estimates pH, Total Acid Number (TAN), density, and viscosity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import math

from src.data.feedstock import BiomassFeedstock


@dataclass
class BioOilChemicalGrouping:
    """Chemical characterization and physical properties of liquid bio-oil product.

    Attributes:
        water_content_pct: Total water content in liquid bio-oil (wt%).
        organics_mass_flow_kg_h: Mass flow rate of organic fraction (kg/h).
        water_mass_flow_kg_h: Mass flow rate of aqueous fraction (kg/h).
        total_liquid_mass_flow_kg_h: Total liquid bio-oil mass flow (kg/h).
        chemical_families_pct: Mass percentages within the dry organic phase (wt%).
        predicted_ph: Estimated pH value of the liquid (typically 2.2 - 3.4).
        total_acid_number_mg_koh_g: Total Acid Number TAN (mg KOH/g oil).
        density_kg_m3: Bulk liquid density at 20 °C (kg/m3).
        kinematic_viscosity_cst_40c: Kinematic viscosity at 40 °C (cSt or mm2/s).
        higher_heating_value_mj_kg: HHV of the wet crude bio-oil (MJ/kg).
        elemental_composition_organics_pct: C, H, O, N, S wt% of the organic fraction.
    """
    water_content_pct: float
    organics_mass_flow_kg_h: float
    water_mass_flow_kg_h: float
    total_liquid_mass_flow_kg_h: float
    chemical_families_pct: Dict[str, float]
    predicted_ph: float
    total_acid_number_mg_koh_g: float
    density_kg_m3: float
    kinematic_viscosity_cst_40c: float
    higher_heating_value_mj_kg: float
    elemental_composition_organics_pct: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_liquid_mass_flow_kg_h": round(self.total_liquid_mass_flow_kg_h, 3),
            "organics_mass_flow_kg_h": round(self.organics_mass_flow_kg_h, 3),
            "water_mass_flow_kg_h": round(self.water_mass_flow_kg_h, 3),
            "water_content_pct": round(self.water_content_pct, 2),
            "predicted_ph": round(self.predicted_ph, 2),
            "total_acid_number_mg_koh_g": round(self.total_acid_number_mg_koh_g, 1),
            "density_kg_m3": round(self.density_kg_m3, 1),
            "kinematic_viscosity_cst_40c": round(self.kinematic_viscosity_cst_40c, 1),
            "higher_heating_value_mj_kg": round(self.higher_heating_value_mj_kg, 2),
            "chemical_families_pct": {k: round(v, 2) for k, v in self.chemical_families_pct.items()},
            "elemental_composition_organics_pct": {
                k: round(v, 2) for k, v in self.elemental_composition_organics_pct.items()
            },
        }


class BioOilPropertyModel:
    """Predicts bio-oil chemical grouping, acidity, and physical properties."""

    def __init__(self) -> None:
        pass

    def evaluate_bio_oil(
        self,
        organics_flow_kg_h: float,
        water_flow_kg_h: float,
        temperature_c: float,
        feedstock: BiomassFeedstock,
        raw_bio_oil_hhv: float,
    ) -> BioOilChemicalGrouping:
        """Compute chemical functional families and physical properties for bio-oil.

        Args:
            organics_flow_kg_h: Net mass flow of condensable organic compounds (kg/h).
            water_flow_kg_h: Net water mass flow in bio-oil (reaction water + residual) (kg/h).
            temperature_c: Reactor operating temperature (°C).
            feedstock: BiomassFeedstock providing proximate/ultimate composition.
            raw_bio_oil_hhv: Higher Heating Value of the wet bio-oil mixture (MJ/kg).

        Returns:
            BioOilChemicalGrouping dataclass.
        """
        total_liquid = organics_flow_kg_h + water_flow_kg_h
        water_pct = (water_flow_kg_h / total_liquid * 100.0) if total_liquid > 0 else 0.0

        t = max(300.0, min(800.0, temperature_c))

        # 1. Chemical functional grouping of the organic phase (% of dry organics)
        # Carboxylic acids (acetic, formic) from hemicellulose deacetylation
        # Increases at lower temperatures, slight secondary thermal cracking at higher temps
        acids_raw = 14.5 - 0.008 * (t - 450.0)

        # Lignin-derived phenolics (monomers + pyrolytic lignin oligomers)
        # Increases at higher temperatures due to deeper lignin cleavage
        phenolics_raw = 30.0 + 0.025 * (t - 450.0)

        # Furans and pyrones (furfural, 5-HMF) from cellulose/hemicellulose
        furans_raw = 10.0 + 0.005 * (t - 450.0)

        # Anhydrosugars (primarily levoglucosan)
        # Peaks near 480-500 °C, cracks into smaller fragments above 550 °C
        sugars_raw = max(8.0, 24.0 - 0.040 * max(0.0, t - 480.0))

        # Aldehydes and ketones (hydroxyacetaldehyde, acetol, acetone)
        carbonyls_raw = 18.0 + 0.015 * (t - 450.0)

        raw_sum = acids_raw + phenolics_raw + furans_raw + sugars_raw + carbonyls_raw
        families = {
            "carboxylic_acids_pct": (acids_raw / raw_sum) * 100.0,
            "phenolics_and_lignin_pct": (phenolics_raw / raw_sum) * 100.0,
            "furans_and_pyrones_pct": (furans_raw / raw_sum) * 100.0,
            "anhydrosugars_pct": (sugars_raw / raw_sum) * 100.0,
            "aldehydes_and_ketones_pct": (carbonyls_raw / raw_sum) * 100.0,
        }

        # 2. Acidity: Total Acid Number (TAN) and Predicted pH
        # Acetic acid equivalent mass fraction in total liquid
        acid_fraction_total = (families["carboxylic_acids_pct"] / 100.0) * (organics_flow_kg_h / total_liquid) if total_liquid > 0 else 0.0
        # TAN (mg KOH / g oil): Acetic acid (MW=60.05), KOH (MW=56.11) -> 1 g acetic acid = 934 mg KOH
        tan = max(10.0, acid_fraction_total * 934.0)

        # Predicted pH based on weak acid dissociation in aqueous phase
        # pH = -log10(sqrt(Ka * [Acid])), Ka_acetic ~ 1.75e-5
        acid_molarity = (acid_fraction_total * 1200.0) / 60.05 if acid_fraction_total > 0 else 1e-6
        h_conc = math.sqrt(1.75e-5 * max(1e-6, acid_molarity))
        ph = max(2.0, min(4.5, -math.log10(max(1e-7, h_conc))))

        # 3. Density (kg/m3 at 20 °C)
        # Organic density ~ 1250 kg/m3, Water density ~ 1000 kg/m3
        density = 1000.0 + (organics_flow_kg_h / total_liquid * 220.0) if total_liquid > 0 else 1000.0

        # 4. Kinematic Viscosity (cSt at 40 °C)
        # Highly dependent on water content: high water decreases viscosity significantly
        # Empirical log-viscosity correlation
        viscosity = max(5.0, 180.0 * math.exp(-0.085 * water_pct))

        # 5. Elemental composition of dry organic fraction (wt%)
        # Biomass ultimate analysis partitioned into bio-oil organics
        c_oil = min(62.0, max(52.0, feedstock.ultimate.carbon * 1.10))
        h_oil = min(8.0, max(5.5, feedstock.ultimate.hydrogen * 1.12))
        n_oil = min(2.0, max(0.1, feedstock.ultimate.nitrogen * 0.75))
        s_oil = min(0.5, max(0.01, feedstock.ultimate.sulfur * 0.50))
        o_oil = max(25.0, 100.0 - (c_oil + h_oil + n_oil + s_oil))

        elem_organics = {
            "carbon_pct": c_oil,
            "hydrogen_pct": h_oil,
            "oxygen_pct": o_oil,
            "nitrogen_pct": n_oil,
            "sulfur_pct": s_oil,
        }

        return BioOilChemicalGrouping(
            water_content_pct=water_pct,
            organics_mass_flow_kg_h=organics_flow_kg_h,
            water_mass_flow_kg_h=water_flow_kg_h,
            total_liquid_mass_flow_kg_h=total_liquid,
            chemical_families_pct=families,
            predicted_ph=ph,
            total_acid_number_mg_koh_g=tan,
            density_kg_m3=density,
            kinematic_viscosity_cst_40c=viscosity,
            higher_heating_value_mj_kg=raw_bio_oil_hhv,
            elemental_composition_organics_pct=elem_organics,
        )
