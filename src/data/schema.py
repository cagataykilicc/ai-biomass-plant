"""Tabular schema and record definition for biomass conversion process datasets.

Provides clean tabular serialization (flat dictionary, Pandas DataFrame compatibility)
for machine learning workflows, statistical analysis, and experimental records.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
import pandas as pd

from src.data.provenance import DataProvenance, DataSourceType


@dataclass
class ProcessDataRecord:
    """Comprehensive tabular record of one complete process simulation or experimental run.

    Encapsulates all input feedstock parameters, operating conditions, product yields,
    syngas speciation, bio-oil quality, energy balances, and scientific data provenance.
    """
    record_id: str
    provenance: DataProvenance

    # Feedstock Ultimate & Proximate Analysis (wt%)
    feedstock_name: str
    feedstock_category: str
    carbon_pct: float
    hydrogen_pct: float
    oxygen_pct: float
    nitrogen_pct: float
    sulfur_pct: float
    ash_pct: float
    moisture_ar_pct: float
    volatile_matter_pct: float
    fixed_carbon_pct: float
    particle_size_mm: float
    bulk_density_kg_m3: float
    feedstock_hhv_dry_mj_kg: float
    feedstock_lhv_ar_mj_kg: float

    # Operating Conditions
    feed_rate_wet_kg_h: float
    dryer_temp_c: float
    dried_biomass_moisture_pct: float
    reactor_temp_c: float
    heating_rate_c_min: float
    residence_time_min: float

    # Product Yields (Dry Feedstock Basis, wt%)
    biochar_yield_dry_pct: float
    bio_oil_yield_dry_pct: float
    syngas_yield_dry_pct: float

    # Mass Flow Rates (kg/h)
    recovered_biochar_kg_h: float
    recovered_bio_oil_kg_h: float
    clean_syngas_kg_h: float
    dryer_exhaust_water_kg_h: float
    mass_balance_closure_pct: float

    # Syngas Speciation & Properties
    syngas_co_vol_pct: float
    syngas_co2_vol_pct: float
    syngas_ch4_vol_pct: float
    syngas_h2_vol_pct: float
    syngas_c2h6_vol_pct: float
    syngas_mw_kg_kmol: float
    syngas_volume_flow_nm3_h: float
    syngas_lhv_vol_mj_nm3: float

    # Bio-oil Quality & Physical Properties
    bio_oil_water_pct: float
    bio_oil_hhv_mj_kg: float
    bio_oil_predicted_ph: float
    bio_oil_tan_mg_koh_g: float
    bio_oil_density_kg_m3: float
    bio_oil_kinematic_viscosity_cst: float

    # Energy Balances, Combustor & KPIs
    drying_thermal_duty_kw: float
    reactor_thermal_duty_kw: float
    gross_thermal_demand_kw: float
    combustor_heat_recovered_kw: float
    thermal_self_sufficiency_index_pct: float
    is_thermally_self_sufficient: bool
    energy_recovery_ratio_pct: float
    net_thermal_efficiency_pct: float
    second_law_exergy_efficiency_pct: float

    def to_flat_dict(self) -> Dict[str, Any]:
        """Flatten record into a single-level dictionary for DataFrame creation."""
        prov_dict = self.provenance.to_dict()
        flat = {
            "record_id": self.record_id,
            "source_type": prov_dict["source_type"],
            "is_synthetic": prov_dict["is_synthetic"],
            "citation": prov_dict["citation"],
            "doi": prov_dict["doi"],
            "sensor_noise_applied": prov_dict["sensor_noise_applied"],
            "validation_status": prov_dict["validation_status"],
            
            # Feedstock
            "feedstock_name": self.feedstock_name,
            "feedstock_category": self.feedstock_category,
            "carbon_pct": self.carbon_pct,
            "hydrogen_pct": self.hydrogen_pct,
            "oxygen_pct": self.oxygen_pct,
            "nitrogen_pct": self.nitrogen_pct,
            "sulfur_pct": self.sulfur_pct,
            "ash_pct": self.ash_pct,
            "moisture_ar_pct": self.moisture_ar_pct,
            "volatile_matter_pct": self.volatile_matter_pct,
            "fixed_carbon_pct": self.fixed_carbon_pct,
            "particle_size_mm": self.particle_size_mm,
            "bulk_density_kg_m3": self.bulk_density_kg_m3,
            "feedstock_hhv_dry_mj_kg": self.feedstock_hhv_dry_mj_kg,
            "feedstock_lhv_ar_mj_kg": self.feedstock_lhv_ar_mj_kg,

            # Process conditions
            "feed_rate_wet_kg_h": self.feed_rate_wet_kg_h,
            "dryer_temp_c": self.dryer_temp_c,
            "dried_biomass_moisture_pct": self.dried_biomass_moisture_pct,
            "reactor_temp_c": self.reactor_temp_c,
            "heating_rate_c_min": self.heating_rate_c_min,
            "residence_time_min": self.residence_time_min,

            # Product yields
            "biochar_yield_dry_pct": self.biochar_yield_dry_pct,
            "bio_oil_yield_dry_pct": self.bio_oil_yield_dry_pct,
            "syngas_yield_dry_pct": self.syngas_yield_dry_pct,

            # Mass rates
            "recovered_biochar_kg_h": self.recovered_biochar_kg_h,
            "recovered_bio_oil_kg_h": self.recovered_bio_oil_kg_h,
            "clean_syngas_kg_h": self.clean_syngas_kg_h,
            "dryer_exhaust_water_kg_h": self.dryer_exhaust_water_kg_h,
            "mass_balance_closure_pct": self.mass_balance_closure_pct,

            # Syngas properties
            "syngas_co_vol_pct": self.syngas_co_vol_pct,
            "syngas_co2_vol_pct": self.syngas_co2_vol_pct,
            "syngas_ch4_vol_pct": self.syngas_ch4_vol_pct,
            "syngas_h2_vol_pct": self.syngas_h2_vol_pct,
            "syngas_c2h6_vol_pct": self.syngas_c2h6_vol_pct,
            "syngas_mw_kg_kmol": self.syngas_mw_kg_kmol,
            "syngas_volume_flow_nm3_h": self.syngas_volume_flow_nm3_h,
            "syngas_lhv_vol_mj_nm3": self.syngas_lhv_vol_mj_nm3,

            # Bio-oil properties
            "bio_oil_water_pct": self.bio_oil_water_pct,
            "bio_oil_hhv_mj_kg": self.bio_oil_hhv_mj_kg,
            "bio_oil_predicted_ph": self.bio_oil_predicted_ph,
            "bio_oil_tan_mg_koh_g": self.bio_oil_tan_mg_koh_g,
            "bio_oil_density_kg_m3": self.bio_oil_density_kg_m3,
            "bio_oil_kinematic_viscosity_cst": self.bio_oil_kinematic_viscosity_cst,

            # Energy KPIs
            "drying_thermal_duty_kw": self.drying_thermal_duty_kw,
            "reactor_thermal_duty_kw": self.reactor_thermal_duty_kw,
            "gross_thermal_demand_kw": self.gross_thermal_demand_kw,
            "combustor_heat_recovered_kw": self.combustor_heat_recovered_kw,
            "thermal_self_sufficiency_index_pct": self.thermal_self_sufficiency_index_pct,
            "is_thermally_self_sufficient": self.is_thermally_self_sufficient,
            "energy_recovery_ratio_pct": self.energy_recovery_ratio_pct,
            "net_thermal_efficiency_pct": self.net_thermal_efficiency_pct,
            "second_law_exergy_efficiency_pct": self.second_law_exergy_efficiency_pct,
        }
        return flat

    @classmethod
    def from_flat_dict(cls, d: Dict[str, Any]) -> ProcessDataRecord:
        prov = DataProvenance(
            source_type=DataSourceType(d.get("source_type", "SYNTHETIC_SIMULATED")),
            citation=d.get("citation"),
            doi=d.get("doi"),
            is_synthetic=bool(d.get("is_synthetic", True)),
            sensor_noise_applied=bool(d.get("sensor_noise_applied", False)),
            validation_status=d.get("validation_status", "VERIFIED"),
        )
        return cls(
            record_id=str(d.get("record_id", "REC_000")),
            provenance=prov,
            feedstock_name=str(d.get("feedstock_name", "Unknown")),
            feedstock_category=str(d.get("feedstock_category", "general_biomass")),
            carbon_pct=float(d.get("carbon_pct", 50.0)),
            hydrogen_pct=float(d.get("hydrogen_pct", 6.0)),
            oxygen_pct=float(d.get("oxygen_pct", 40.0)),
            nitrogen_pct=float(d.get("nitrogen_pct", 0.5)),
            sulfur_pct=float(d.get("sulfur_pct", 0.05)),
            ash_pct=float(d.get("ash_pct", 3.45)),
            moisture_ar_pct=float(d.get("moisture_ar_pct", 15.0)),
            volatile_matter_pct=float(d.get("volatile_matter_pct", 75.0)),
            fixed_carbon_pct=float(d.get("fixed_carbon_pct", 21.55)),
            particle_size_mm=float(d.get("particle_size_mm", 2.0)),
            bulk_density_kg_m3=float(d.get("bulk_density_kg_m3", 500.0)),
            feedstock_hhv_dry_mj_kg=float(d.get("feedstock_hhv_dry_mj_kg", 20.0)),
            feedstock_lhv_ar_mj_kg=float(d.get("feedstock_lhv_ar_mj_kg", 16.0)),
            feed_rate_wet_kg_h=float(d.get("feed_rate_wet_kg_h", 100.0)),
            dryer_temp_c=float(d.get("dryer_temp_c", 105.0)),
            dried_biomass_moisture_pct=float(d.get("dried_biomass_moisture_pct", 8.0)),
            reactor_temp_c=float(d.get("reactor_temp_c", 500.0)),
            heating_rate_c_min=float(d.get("heating_rate_c_min", 10.0)),
            residence_time_min=float(d.get("residence_time_min", 20.0)),
            biochar_yield_dry_pct=float(d.get("biochar_yield_dry_pct", 28.0)),
            bio_oil_yield_dry_pct=float(d.get("bio_oil_yield_dry_pct", 48.0)),
            syngas_yield_dry_pct=float(d.get("syngas_yield_dry_pct", 24.0)),
            recovered_biochar_kg_h=float(d.get("recovered_biochar_kg_h", 23.0)),
            recovered_bio_oil_kg_h=float(d.get("recovered_bio_oil_kg_h", 46.0)),
            clean_syngas_kg_h=float(d.get("clean_syngas_kg_h", 23.0)),
            dryer_exhaust_water_kg_h=float(d.get("dryer_exhaust_water_kg_h", 7.6)),
            mass_balance_closure_pct=float(d.get("mass_balance_closure_pct", 100.0)),
            syngas_co_vol_pct=float(d.get("syngas_co_vol_pct", 42.0)),
            syngas_co2_vol_pct=float(d.get("syngas_co2_vol_pct", 34.0)),
            syngas_ch4_vol_pct=float(d.get("syngas_ch4_vol_pct", 12.0)),
            syngas_h2_vol_pct=float(d.get("syngas_h2_vol_pct", 5.0)),
            syngas_c2h6_vol_pct=float(d.get("syngas_c2h6_vol_pct", 3.0)),
            syngas_mw_kg_kmol=float(d.get("syngas_mw_kg_kmol", 30.0)),
            syngas_volume_flow_nm3_h=float(d.get("syngas_volume_flow_nm3_h", 17.0)),
            syngas_lhv_vol_mj_nm3=float(d.get("syngas_lhv_vol_mj_nm3", 13.0)),
            bio_oil_water_pct=float(d.get("bio_oil_water_pct", 25.0)),
            bio_oil_hhv_mj_kg=float(d.get("bio_oil_hhv_mj_kg", 14.5)),
            bio_oil_predicted_ph=float(d.get("bio_oil_predicted_ph", 2.3)),
            bio_oil_tan_mg_koh_g=float(d.get("bio_oil_tan_mg_koh_g", 100.0)),
            bio_oil_density_kg_m3=float(d.get("bio_oil_density_kg_m3", 1170.0)),
            bio_oil_kinematic_viscosity_cst=float(d.get("bio_oil_kinematic_viscosity_cst", 25.0)),
            drying_thermal_duty_kw=float(d.get("drying_thermal_duty_kw", 11.5)),
            reactor_thermal_duty_kw=float(d.get("reactor_thermal_duty_kw", 35.0)),
            gross_thermal_demand_kw=float(d.get("gross_thermal_demand_kw", 46.5)),
            combustor_heat_recovered_kw=float(d.get("combustor_heat_recovered_kw", 52.0)),
            thermal_self_sufficiency_index_pct=float(d.get("thermal_self_sufficiency_index_pct", 111.0)),
            is_thermally_self_sufficient=bool(d.get("is_thermally_self_sufficient", True)),
            energy_recovery_ratio_pct=float(d.get("energy_recovery_ratio_pct", 82.0)),
            net_thermal_efficiency_pct=float(d.get("net_thermal_efficiency_pct", 80.0)),
            second_law_exergy_efficiency_pct=float(d.get("second_law_exergy_efficiency_pct", 82.0)),
        )

    @staticmethod
    def records_to_dataframe(records: List[ProcessDataRecord]) -> pd.DataFrame:
        """Convert a list of ProcessDataRecord instances to a Pandas DataFrame."""
        return pd.DataFrame([r.to_flat_dict() for r in records])
