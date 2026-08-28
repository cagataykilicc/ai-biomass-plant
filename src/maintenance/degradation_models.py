"""Physics-informed degradation kinematics and asset wear trajectory models.

Simulates progressive physical wear on 4 mission-critical plant assets:
1. AUGER_A101: Biomass infeed auger screw flight abrasive thinning.
2. REACTOR_R101_LINER: Pyrolysis reactor refractory thermal spalling and shell skin heating.
3. FILTER_F101: Syngas ceramic particulate filter pore blinding & delta-P rise.
4. CONDENSER_HX102: Bio-oil condenser tube bundle organic acid corrosion and tar fouling.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, Tuple


@dataclass
class AssetDegradationState:
    """Current physical degradation metrics for an asset."""
    asset_id: str
    asset_name: str
    primary_wear_metric: str
    current_wear_value: float
    wear_threshold_eol: float
    unit: str
    health_index_pct: float  # [100.0% = brand new, 0.0% = EoL reached]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AugerDegradationModel:
    """Archard abrasive wear model for infeed screw conveyor flights."""

    K_WEAR_MM_PER_1000H = 0.65  # Base wear: 0.65 mm per 1,000 operating hours at 100 kg/h, 2% ash
    EOL_THRESHOLD_MM = 6.0      # End-of-life limit: 6.0 mm flight thickness loss

    @classmethod
    def evaluate(
        cls,
        operating_hours: float,
        feed_rate_kg_h: float = 100.0,
        ash_content_pct: float = 2.0,
        vibration_rms_mm_s: float = 2.5,
    ) -> AssetDegradationState:
        """Calculate auger flight wear and health index."""
        # Operational wear multiplier
        ash_factor = max(0.5, ash_content_pct / 2.0)
        feed_factor = max(0.2, feed_rate_kg_h / 100.0)
        vib_factor = 1.0 + 0.08 * max(0.0, vibration_rms_mm_s - 2.0)

        wear_mm = (cls.K_WEAR_MM_PER_1000H / 1000.0) * operating_hours * ash_factor * feed_factor * vib_factor
        wear_mm = float(round(wear_mm, 3))

        hi_pct = float(max(0.0, min(100.0, (1.0 - wear_mm / cls.EOL_THRESHOLD_MM) * 100.0)))

        return AssetDegradationState(
            asset_id="AUGER_A101",
            asset_name="Biomass Infeed Auger Screw",
            primary_wear_metric="Screw Flight Thickness Loss",
            current_wear_value=wear_mm,
            wear_threshold_eol=cls.EOL_THRESHOLD_MM,
            unit="mm",
            health_index_pct=round(hi_pct, 1),
        )


class RefractoryDegradationModel:
    """Thermal spalling and refractory lining loss model for pyrolysis reactor."""

    K_SPALL_MM_PER_1000H = 4.2  # 4.2 mm refractory loss per 1,000h at 500°C
    EOL_THRESHOLD_MM = 40.0     # 40.0 mm refractory loss limit (initial lining: 100 mm)

    @classmethod
    def evaluate(
        cls,
        operating_hours: float,
        reactor_temp_c: float = 500.0,
        thermal_cycles_count: int = 15,
    ) -> AssetDegradationState:
        """Calculate refractory lining thickness loss and outer shell skin temperature rise."""
        temp_factor = np_exp_approx = float(2.71828 ** ((reactor_temp_c - 500.0) / 120.0))
        cycle_factor = 1.0 + 0.02 * thermal_cycles_count

        wear_mm = (cls.K_SPALL_MM_PER_1000H / 1000.0) * operating_hours * temp_factor * cycle_factor
        wear_mm = float(round(wear_mm, 2))

        hi_pct = float(max(0.0, min(100.0, (1.0 - wear_mm / cls.EOL_THRESHOLD_MM) * 100.0)))

        return AssetDegradationState(
            asset_id="REACTOR_R101_LINER",
            asset_name="Pyrolysis Reactor Refractory Liner",
            primary_wear_metric="Refractory Wall Thickness Loss",
            current_wear_value=wear_mm,
            wear_threshold_eol=cls.EOL_THRESHOLD_MM,
            unit="mm",
            health_index_pct=round(hi_pct, 1),
        )


class FilterDegradationModel:
    """Ceramic particulate candle filter pore blinding and residual clean delta-P model."""

    P0_CLEAN_KPA = 2.0          # Initial clean filter delta-P: 2.0 kPa
    EOL_THRESHOLD_KPA = 12.0    # End-of-life limit: 12.0 kPa clean residual delta-P
    K_BLIND = 0.00035           # Blinding kinetic coefficient (8,000h design life)

    @classmethod
    def evaluate(
        cls,
        operating_hours: float,
        soot_load_factor: float = 1.0,
    ) -> AssetDegradationState:
        """Calculate clean residual filter pressure drop and health index."""
        dp_rise = cls.P0_CLEAN_KPA * ((1.0 + cls.K_BLIND * operating_hours * soot_load_factor) ** 1.35)
        dp_clean_kpa = float(round(dp_rise, 2))

        fraction_used = (dp_clean_kpa - cls.P0_CLEAN_KPA) / (cls.EOL_THRESHOLD_KPA - cls.P0_CLEAN_KPA)
        hi_pct = float(max(0.0, min(100.0, (1.0 - fraction_used) * 100.0)))

        return AssetDegradationState(
            asset_id="FILTER_F101",
            asset_name="Syngas Particulate Ceramic Filter",
            primary_wear_metric="Clean Residual Pressure Drop",
            current_wear_value=dp_clean_kpa,
            wear_threshold_eol=cls.EOL_THRESHOLD_KPA,
            unit="kPa",
            health_index_pct=round(hi_pct, 1),
        )


class CondenserDegradationModel:
    """Bio-oil condenser tube bundle carboxylic acid corrosion and tar fouling resistance model."""

    K_CORR_MM_PER_1000H = 0.15  # 0.15 mm corrosion per 1,000h at TAN 100
    EOL_THRESHOLD_MM = 1.5      # End-of-life limit: 1.5 mm tube metal loss

    @classmethod
    def evaluate(
        cls,
        operating_hours: float,
        bio_oil_tan_mg_koh_g: float = 100.0,
    ) -> AssetDegradationState:
        """Calculate condenser tube corrosion thickness loss and health index."""
        tan_factor = max(0.5, bio_oil_tan_mg_koh_g / 100.0)
        corr_mm = (cls.K_CORR_MM_PER_1000H / 1000.0) * operating_hours * tan_factor
        corr_mm = float(round(corr_mm, 3))

        hi_pct = float(max(0.0, min(100.0, (1.0 - corr_mm / cls.EOL_THRESHOLD_MM) * 100.0)))

        return AssetDegradationState(
            asset_id="CONDENSER_HX102",
            asset_name="Bio-Oil Condenser Tube Bundle",
            primary_wear_metric="Tube Wall Corrosion Loss",
            current_wear_value=corr_mm,
            wear_threshold_eol=cls.EOL_THRESHOLD_MM,
            unit="mm",
            health_index_pct=round(hi_pct, 1),
        )
