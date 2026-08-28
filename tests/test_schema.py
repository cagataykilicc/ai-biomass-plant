"""Unit tests for ProcessDataRecord tabular schema and DataFrame conversion."""

import pytest
import pandas as pd
from src.data.provenance import DataProvenance, DataSourceType
from src.data.schema import ProcessDataRecord


def test_process_data_record_serialization() -> None:
    """Verify flat dictionary serialization and round-trip conversion."""
    prov = DataProvenance(source_type=DataSourceType.SYNTHETIC_SIMULATED)
    rec = ProcessDataRecord(
        record_id="REC_001",
        provenance=prov,
        feedstock_name="Olive Pomace",
        feedstock_category="agricultural_residue",
        carbon_pct=50.2,
        hydrogen_pct=6.2,
        oxygen_pct=39.8,
        nitrogen_pct=1.4,
        sulfur_pct=0.1,
        ash_pct=2.3,
        moisture_ar_pct=15.0,
        volatile_matter_pct=76.5,
        fixed_carbon_pct=21.2,
        particle_size_mm=2.0,
        bulk_density_kg_m3=550.0,
        feedstock_hhv_dry_mj_kg=20.6,
        feedstock_lhv_ar_mj_kg=16.0,
        feed_rate_wet_kg_h=100.0,
        dryer_temp_c=105.0,
        dried_biomass_moisture_pct=8.0,
        reactor_temp_c=500.0,
        heating_rate_c_min=10.0,
        residence_time_min=20.0,
        biochar_yield_dry_pct=27.4,
        bio_oil_yield_dry_pct=48.1,
        syngas_yield_dry_pct=24.5,
        recovered_biochar_kg_h=22.9,
        recovered_bio_oil_kg_h=46.3,
        clean_syngas_kg_h=22.8,
        dryer_exhaust_water_kg_h=7.6,
        mass_balance_closure_pct=100.0,
        syngas_co_vol_pct=44.5,
        syngas_co2_vol_pct=31.6,
        syngas_ch4_vol_pct=12.6,
        syngas_h2_vol_pct=4.7,
        syngas_c2h6_vol_pct=3.0,
        syngas_mw_kg_kmol=30.2,
        syngas_volume_flow_nm3_h=16.9,
        syngas_lhv_vol_mj_nm3=13.4,
        bio_oil_water_pct=25.5,
        bio_oil_hhv_mj_kg=14.1,
        bio_oil_predicted_ph=2.21,
        bio_oil_tan_mg_koh_g=100.6,
        bio_oil_density_kg_m3=1164.0,
        bio_oil_kinematic_viscosity_cst=22.0,
        drying_thermal_duty_kw=11.7,
        reactor_thermal_duty_kw=35.4,
        gross_thermal_demand_kw=47.1,
        combustor_heat_recovered_kw=52.7,
        thermal_self_sufficiency_index_pct=111.8,
        is_thermally_self_sufficient=True,
        energy_recovery_ratio_pct=81.9,
        net_thermal_efficiency_pct=81.2,
        second_law_exergy_efficiency_pct=82.3,
    )

    flat_dict = rec.to_flat_dict()
    assert flat_dict["record_id"] == "REC_001"
    assert flat_dict["feedstock_name"] == "Olive Pomace"
    assert flat_dict["is_synthetic"] is True

    # DataFrame test
    df = ProcessDataRecord.records_to_dataframe([rec])
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert "reactor_temp_c" in df.columns
