"""High-throughput synthetic process dataset generator with Latin Hypercube Sampling.

Generates realistic, physically-constrained synthetic biomass conversion datasets across
diverse feedstock families and operating envelopes with optional sensor noise injection.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd

from src.data.feedstock import (
    BiomassFeedstock,
    UltimateAnalysis,
    ProximateAnalysis,
    PhysicalProperties,
)
from src.data.preprocessing import FeedstockLibrary
from src.data.provenance import DataProvenance, DataSourceType
from src.data.schema import ProcessDataRecord
from src.simulation.plant_simulator import BiomassPlantSimulator, SimulationReport
from src.utils.config import PlantScenarioConfig


@dataclass
class SyntheticGeneratorConfig:
    """Configuration for Latin Hypercube Monte Carlo process data generator.

    Attributes:
        n_samples: Total number of synthetic process runs to generate.
        random_seed: Random seed for reproducible sampling.
        temp_min_c: Lower bound for reactor temperature (°C).
        temp_max_c: Upper bound for reactor temperature (°C).
        heating_rate_min_c_min: Lower bound for heating rate (°C/min).
        heating_rate_max_c_min: Upper bound for heating rate (°C/min).
        residence_time_min: Lower bound for residence time (min).
        residence_time_max: Upper bound for residence time (min).
        feed_rate_min_kg_h: Lower bound for wet biomass feed rate (kg/h).
        feed_rate_max_kg_h: Upper bound for wet biomass feed rate (kg/h).
        moisture_min_pct: Lower bound for feedstock moisture (wt%).
        moisture_max_pct: Upper bound for feedstock moisture (wt%).
        inject_sensor_noise: Whether to simulate industrial sensor uncertainty.
        temp_sensor_noise_std_c: Thermocouple Gaussian measurement noise (std, °C).
        mass_sensor_noise_pct: Load cell mass measurement relative noise (std, %).
        gas_gc_noise_pct: Gas chromatography volume relative noise (std, %).
    """
    n_samples: int = 1000
    random_seed: int = 42
    temp_min_c: float = 350.0
    temp_max_c: float = 750.0
    heating_rate_min_c_min: float = 5.0
    heating_rate_max_c_min: float = 800.0
    residence_time_min: float = 0.1
    residence_time_max: float = 45.0
    feed_rate_min_kg_h: float = 50.0
    feed_rate_max_kg_h: float = 500.0
    moisture_min_pct: float = 6.0
    moisture_max_pct: float = 28.0
    inject_sensor_noise: bool = True
    temp_sensor_noise_std_c: float = 1.5
    mass_sensor_noise_pct: float = 0.8
    gas_gc_noise_pct: float = 1.2


class SyntheticProcessDataGenerator:
    """Latin Hypercube Sampling dataset generator for biomass conversion plants."""

    def __init__(
        self,
        config: Optional[SyntheticGeneratorConfig] = None,
        simulator: Optional[BiomassPlantSimulator] = None,
    ) -> None:
        self.config = config or SyntheticGeneratorConfig()
        self.simulator = simulator or BiomassPlantSimulator()
        self._feedstocks = self._build_feedstock_portfolio()

    def _build_feedstock_portfolio(self) -> Dict[str, BiomassFeedstock]:
        """Portfolio of 8 realistic biomass feedstocks across distinct classes."""
        return {
            "pine_sawdust": BiomassFeedstock(
                name="Pine Sawdust",
                category="woody_biomass",
                ultimate=UltimateAnalysis(carbon=51.5, hydrogen=6.3, oxygen=41.6, nitrogen=0.2, sulfur=0.05, ash=0.35),
                proximate=ProximateAnalysis(moisture=12.0, volatile_matter=82.5, fixed_carbon=17.15, ash=0.35),
                physical=PhysicalProperties(particle_size_mm=1.5, bulk_density_kg_m3=420.0),
            ),
            "beech_wood": BiomassFeedstock(
                name="Beech Wood",
                category="woody_biomass",
                ultimate=UltimateAnalysis(carbon=49.5, hydrogen=6.1, oxygen=43.8, nitrogen=0.2, sulfur=0.02, ash=0.38),
                proximate=ProximateAnalysis(moisture=10.0, volatile_matter=84.0, fixed_carbon=15.62, ash=0.38),
                physical=PhysicalProperties(particle_size_mm=1.0, bulk_density_kg_m3=460.0),
            ),
            "olive_pomace": BiomassFeedstock(
                name="Olive Pomace",
                category="agricultural_residue",
                ultimate=UltimateAnalysis(carbon=50.2, hydrogen=6.2, oxygen=39.8, nitrogen=1.4, sulfur=0.1, ash=2.3),
                proximate=ProximateAnalysis(moisture=15.0, volatile_matter=76.5, fixed_carbon=21.2, ash=2.3),
                physical=PhysicalProperties(particle_size_mm=2.0, bulk_density_kg_m3=550.0),
            ),
            "wheat_straw": BiomassFeedstock(
                name="Wheat Straw",
                category="agricultural_residue",
                ultimate=UltimateAnalysis(carbon=46.5, hydrogen=5.9, oxygen=41.2, nitrogen=0.7, sulfur=0.1, ash=5.6),
                proximate=ProximateAnalysis(moisture=14.0, volatile_matter=75.0, fixed_carbon=19.4, ash=5.6),
                physical=PhysicalProperties(particle_size_mm=3.0, bulk_density_kg_m3=220.0),
            ),
            "rice_husk": BiomassFeedstock(
                name="Rice Husk",
                category="agricultural_residue",
                ultimate=UltimateAnalysis(carbon=39.5, hydrogen=5.1, oxygen=36.5, nitrogen=0.4, sulfur=0.1, ash=18.4),
                proximate=ProximateAnalysis(moisture=10.0, volatile_matter=63.5, fixed_carbon=18.1, ash=18.4),
                physical=PhysicalProperties(particle_size_mm=2.5, bulk_density_kg_m3=340.0),
            ),
            "sugarcane_bagasse": BiomassFeedstock(
                name="Sugarcane Bagasse",
                category="agricultural_residue",
                ultimate=UltimateAnalysis(carbon=48.0, hydrogen=5.8, oxygen=43.5, nitrogen=0.3, sulfur=0.05, ash=2.35),
                proximate=ProximateAnalysis(moisture=18.0, volatile_matter=81.0, fixed_carbon=16.65, ash=2.35),
                physical=PhysicalProperties(particle_size_mm=2.0, bulk_density_kg_m3=180.0),
            ),
            "miscanthus": BiomassFeedstock(
                name="Miscanthus",
                category="energy_crop",
                ultimate=UltimateAnalysis(carbon=48.5, hydrogen=5.7, oxygen=42.6, nitrogen=0.6, sulfur=0.1, ash=2.5),
                proximate=ProximateAnalysis(moisture=11.0, volatile_matter=79.5, fixed_carbon=18.0, ash=2.5),
                physical=PhysicalProperties(particle_size_mm=2.2, bulk_density_kg_m3=200.0),
            ),
            "almond_shells": BiomassFeedstock(
                name="Almond Shells",
                category="nut_shells",
                ultimate=UltimateAnalysis(carbon=51.0, hydrogen=6.0, oxygen=39.5, nitrogen=0.5, sulfur=0.05, ash=2.95),
                proximate=ProximateAnalysis(moisture=10.0, volatile_matter=73.5, fixed_carbon=23.55, ash=2.95),
                physical=PhysicalProperties(particle_size_mm=3.5, bulk_density_kg_m3=480.0),
            ),
        }

    def _latin_hypercube_sample(self, n_samples: int, n_dim: int, rng: np.random.Generator) -> np.ndarray:
        """Generate stratified Latin Hypercube samples uniformly in [0, 1]^n_dim."""
        result = np.empty((n_samples, n_dim))
        for j in range(n_dim):
            intervals = np.linspace(0, 1, n_samples + 1)
            pts = rng.uniform(intervals[:-1], intervals[1:])
            rng.shuffle(pts)
            result[:, j] = pts
        return result

    def generate_dataset(
        self,
        n_samples: Optional[int] = None,
        random_seed: Optional[int] = None,
    ) -> List[ProcessDataRecord]:
        """Generate N simulated process records using Latin Hypercube Sampling.

        Args:
            n_samples: Number of sample records to generate (default from config).
            random_seed: Random seed for RNG reproducibility.

        Returns:
            List of ProcessDataRecord instances.
        """
        n = n_samples if n_samples is not None else self.config.n_samples
        seed = random_seed if random_seed is not None else self.config.random_seed
        rng = np.random.default_rng(seed)

        feedstock_keys = list(self._feedstocks.keys())
        n_feedstocks = len(feedstock_keys)

        # 5 continuous dimensions: Temperature, log(HeatingRate), log(ResidenceTime), FeedRate, Moisture
        lhs_matrix = self._latin_hypercube_sample(n_samples=n, n_dim=5, rng=rng)

        records: List[ProcessDataRecord] = []

        for i in range(n):
            record_id = f"SYN_{i+1:05d}"
            # Stratified discrete feedstock selection
            fs_key = feedstock_keys[i % n_feedstocks]
            base_feedstock = self._feedstocks[fs_key]

            # Scale LHS continuous dimensions
            # 1. Temperature (°C)
            t_min, t_max = self.config.temp_min_c, self.config.temp_max_c
            temp_c = t_min + (t_max - t_min) * lhs_matrix[i, 0]

            # 2. Heating Rate (°C/min) - log-uniform
            log_hr_min = np.log10(self.config.heating_rate_min_c_min)
            log_hr_max = np.log10(self.config.heating_rate_max_c_min)
            hr_c_min = 10.0 ** (log_hr_min + (log_hr_max - log_hr_min) * lhs_matrix[i, 1])

            # 3. Residence Time (min) - log-uniform
            log_rt_min = np.log10(self.config.residence_time_min)
            log_rt_max = np.log10(self.config.residence_time_max)
            res_time_min = 10.0 ** (log_rt_min + (log_rt_max - log_rt_min) * lhs_matrix[i, 2])

            # 4. Feed Rate (kg/h)
            fr_min, fr_max = self.config.feed_rate_min_kg_h, self.config.feed_rate_max_kg_h
            feed_rate_kg_h = fr_min + (fr_max - fr_min) * lhs_matrix[i, 3]

            # 5. Moisture content (wt%)
            m_min, m_max = self.config.moisture_min_pct, self.config.moisture_max_pct
            moisture_pct = m_min + (m_max - m_min) * lhs_matrix[i, 4]

            # Run physical simulation
            scenario_cfg = PlantScenarioConfig(
                feedstock_name=fs_key,
                feed_rate_kg_h=float(feed_rate_kg_h),
                moisture_pct_override=float(moisture_pct),
            )
            scenario_cfg.reactor.temperature_c = float(temp_c)
            scenario_cfg.reactor.heating_rate_c_min = float(hr_c_min)
            scenario_cfg.reactor.residence_time_min = float(res_time_min)

            report: SimulationReport = self.simulator.run_simulation(
                scenario=scenario_cfg,
                feedstock_name=fs_key,
                feed_rate_kg_h=float(feed_rate_kg_h),
                moisture_pct=float(moisture_pct),
                reactor_temp_c=float(temp_c),
                heating_rate_c_min=float(hr_c_min),
                residence_time_min=float(res_time_min),
            )

            # Optional Sensor Noise Injection
            measured_temp = temp_c
            measured_char_rate = report.separation.recovered_biochar_kg_h
            measured_oil_rate = report.separation.recovered_bio_oil_liquid_kg_h
            measured_syngas_rate = report.separation.clean_syngas_kg_h
            co_vol = report.syngas.molar_fractions.get("CO", 0.40) * 100.0
            co2_vol = report.syngas.molar_fractions.get("CO2", 0.35) * 100.0
            ch4_vol = report.syngas.molar_fractions.get("CH4", 0.12) * 100.0
            h2_vol = report.syngas.molar_fractions.get("H2", 0.05) * 100.0

            if self.config.inject_sensor_noise:
                # Add slight measurement variance to mimic plant instrumentation
                measured_temp += float(rng.normal(0.0, self.config.temp_sensor_noise_std_c))
                noise_char = float(rng.normal(1.0, self.config.mass_sensor_noise_pct / 100.0))
                noise_oil = float(rng.normal(1.0, self.config.mass_sensor_noise_pct / 100.0))
                noise_gas = float(rng.normal(1.0, self.config.mass_sensor_noise_pct / 100.0))
                measured_char_rate *= noise_char
                measured_oil_rate *= noise_oil
                measured_syngas_rate *= noise_gas

            provenance = DataProvenance(
                source_type=DataSourceType.SYNTHETIC_SIMULATED,
                facility_or_model="BiomassPlantSimulator_V0.3_LHS",
                is_synthetic=True,
                sensor_noise_applied=self.config.inject_sensor_noise,
                validation_status="VERIFIED",
            )

            rec = ProcessDataRecord(
                record_id=record_id,
                provenance=provenance,
                feedstock_name=report.feedstock.name,
                feedstock_category=report.feedstock.category,
                carbon_pct=report.feedstock.ultimate.carbon,
                hydrogen_pct=report.feedstock.ultimate.hydrogen,
                oxygen_pct=report.feedstock.ultimate.oxygen,
                nitrogen_pct=report.feedstock.ultimate.nitrogen,
                sulfur_pct=report.feedstock.ultimate.sulfur,
                ash_pct=report.feedstock.ultimate.ash,
                moisture_ar_pct=report.feedstock.proximate.moisture,
                volatile_matter_pct=report.feedstock.proximate.volatile_matter,
                fixed_carbon_pct=report.feedstock.proximate.fixed_carbon,
                particle_size_mm=report.feedstock.physical.particle_size_mm,
                bulk_density_kg_m3=report.feedstock.physical.bulk_density_kg_m3,
                feedstock_hhv_dry_mj_kg=report.feedstock.calculate_hhv_dry(),
                feedstock_lhv_ar_mj_kg=report.feedstock.calculate_lhv_as_received(),
                feed_rate_wet_kg_h=report.scenario_config.feed_rate_kg_h,
                dryer_temp_c=report.drying.dryer_temperature_c,
                dried_biomass_moisture_pct=report.drying.final_moisture_pct,
                reactor_temp_c=round(measured_temp, 2),
                heating_rate_c_min=round(hr_c_min, 2),
                residence_time_min=round(res_time_min, 2),
                biochar_yield_dry_pct=round(report.reactor.yields_dry.biochar_yield * 100.0, 2),
                bio_oil_yield_dry_pct=round(report.reactor.yields_dry.bio_oil_yield * 100.0, 2),
                syngas_yield_dry_pct=round(report.reactor.yields_dry.syngas_yield * 100.0, 2),
                recovered_biochar_kg_h=round(measured_char_rate, 3),
                recovered_bio_oil_kg_h=round(measured_oil_rate, 3),
                clean_syngas_kg_h=round(measured_syngas_rate, 3),
                dryer_exhaust_water_kg_h=round(report.drying.water_evaporated_kg_h, 3),
                mass_balance_closure_pct=round(report.mass_balance.closure_pct, 2),
                syngas_co_vol_pct=round(co_vol, 2),
                syngas_co2_vol_pct=round(co2_vol, 2),
                syngas_ch4_vol_pct=round(ch4_vol, 2),
                syngas_h2_vol_pct=round(h2_vol, 2),
                syngas_c2h6_vol_pct=round(report.syngas.molar_fractions.get("C2H6", 0.03) * 100.0, 2),
                syngas_mw_kg_kmol=round(report.syngas.mean_molecular_weight_kg_kmol, 2),
                syngas_volume_flow_nm3_h=round(report.syngas.standard_volume_flow_nm3_h, 2),
                syngas_lhv_vol_mj_nm3=round(report.syngas.lhv_vol_mj_nm3, 2),
                bio_oil_water_pct=round(report.bio_oil.water_content_pct, 2),
                bio_oil_hhv_mj_kg=round(report.bio_oil.higher_heating_value_mj_kg, 2),
                bio_oil_predicted_ph=round(report.bio_oil.predicted_ph, 2),
                bio_oil_tan_mg_koh_g=round(report.bio_oil.total_acid_number_mg_koh_g, 1),
                bio_oil_density_kg_m3=round(report.bio_oil.density_kg_m3, 1),
                bio_oil_kinematic_viscosity_cst=round(report.bio_oil.kinematic_viscosity_cst_40c, 1),
                drying_thermal_duty_kw=round(report.energy_balance.drying_thermal_duty_kw, 2),
                reactor_thermal_duty_kw=round(report.energy_balance.reactor_thermal_duty_kw, 2),
                gross_thermal_demand_kw=round(report.energy_balance.gross_thermal_demand_kw, 2),
                combustor_heat_recovered_kw=round(report.combustion.thermal_heat_recovered_kw, 2),
                thermal_self_sufficiency_index_pct=round(report.combustion.thermal_self_sufficiency_index_pct, 2),
                is_thermally_self_sufficient=report.combustion.is_thermally_self_sufficient,
                energy_recovery_ratio_pct=round(report.energy_balance.energy_recovery_ratio_pct, 2),
                net_thermal_efficiency_pct=round(report.energy_balance.net_thermal_efficiency_pct, 2),
                second_law_exergy_efficiency_pct=(
                    round(report.energy_balance.exergy.second_law_exergy_efficiency_pct, 2)
                    if report.energy_balance.exergy else 80.0
                ),
            )
            records.append(rec)

        return records

    def save_dataset_csv(
        self,
        output_path: Optional[Union[str, Path]] = None,
        n_samples: Optional[int] = None,
        random_seed: Optional[int] = None,
    ) -> Path:
        """Generate synthetic dataset and write to CSV file."""
        if output_path is None:
            out_file = (
                Path(__file__).resolve().parent.parent.parent
                / "data"
                / "processed"
                / "synthetic_process_dataset.csv"
            )
        else:
            out_file = Path(output_path)

        out_file.parent.mkdir(parents=True, exist_ok=True)
        records = self.generate_dataset(n_samples=n_samples, random_seed=random_seed)
        df = ProcessDataRecord.records_to_dataframe(records)
        df.to_csv(out_file, index=False)
        return out_file


def main() -> None:
    """CLI generator command."""
    parser = argparse.ArgumentParser(description="Latin Hypercube Synthetic Process Dataset Generator")
    parser.add_argument("--samples", type=int, default=1000, help="Number of records to generate (default: 1000)")
    parser.add_argument("--seed", type=int, default=42, help="Random RNG seed (default: 42)")
    parser.add_argument("--output", type=str, default=None, help="Output CSV path")
    args = parser.parse_args()

    cfg = SyntheticGeneratorConfig(n_samples=args.samples, random_seed=args.seed)
    gen = SyntheticProcessDataGenerator(config=cfg)
    out_path = gen.save_dataset_csv(output_path=args.output, n_samples=args.samples, random_seed=args.seed)
    print(f"[OK] Generated {args.samples} synthetic process records -> {out_path}")


if __name__ == "__main__":
    main()
