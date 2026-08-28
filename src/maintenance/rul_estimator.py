"""Remaining Useful Life (RUL) estimation and fleet prognostics engine with 95% Confidence Intervals.

Evaluates asset degradation states, computes remaining operating hours until safety thresholds
are reached, and quantifies prognostic uncertainty.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
import numpy as np

from src.maintenance.degradation_models import (
    AssetDegradationState,
    AugerDegradationModel,
    RefractoryDegradationModel,
    FilterDegradationModel,
    CondenserDegradationModel,
)


@dataclass
class AssetRULSummary:
    """Prognostic health assessment and Remaining Useful Life projection for a single asset."""
    asset_id: str
    asset_name: str
    current_operating_hours: float
    current_health_index_pct: float
    estimated_rul_hours: float
    rul_95_ci_lower_hours: float
    rul_95_ci_upper_hours: float
    maintenance_urgency: str  # HEALTHY, PLANNED_MAINTENANCE, URGENT_INTERVENTION, CRITICAL_REPLACEMENT
    degradation_state: AssetDegradationState

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


@dataclass
class FleetMaintenanceSummary:
    """Plant-wide fleet prognostic health matrix and minimum RUL bottleneck."""
    current_operating_hours: float
    assets: Dict[str, AssetRULSummary]
    most_critical_asset_id: str
    minimum_fleet_rul_hours: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_operating_hours": self.current_operating_hours,
            "most_critical_asset_id": self.most_critical_asset_id,
            "minimum_fleet_rul_hours": self.minimum_fleet_rul_hours,
            "assets": {k: v.to_dict() for k, v in self.assets.items()},
        }


class RULEstimator:
    """Prognostics engine for estimating remaining useful life of plant assets."""

    @classmethod
    def _triage_urgency(cls, rul_hours: float, health_index_pct: float) -> str:
        """Classify maintenance intervention urgency from RUL and health index."""
        if health_index_pct <= 15.0 or rul_hours <= 250.0:
            return "CRITICAL_REPLACEMENT"
        elif health_index_pct <= 35.0 or rul_hours <= 1000.0:
            return "URGENT_INTERVENTION"
        elif health_index_pct <= 65.0 or rul_hours <= 2500.0:
            return "PLANNED_MAINTENANCE"
        return "HEALTHY"

    @classmethod
    def _compute_rul_with_uncertainty(
        cls,
        current_hours: float,
        current_wear: float,
        eol_limit: float,
    ) -> Tuple[float, float, float]:
        """Project linear/quasi-linear RUL and compute 95% confidence intervals."""
        if current_hours <= 0.0 or current_wear <= 0.0:
            rul_point = 8000.0  # Nominal baseline life
        else:
            wear_rate_per_hour = current_wear / current_hours
            remaining_wear_allowance = max(0.0, eol_limit - current_wear)
            rul_point = float(remaining_wear_allowance / max(1e-6, wear_rate_per_hour))

        rul_point = float(max(0.0, round(rul_point, 1)))

        # Prognostic uncertainty grows with longer time horizons: sigma = 7% * RUL + 40h
        sigma = float(0.07 * rul_point + 40.0)
        ci_lower = float(max(0.0, round(rul_point - 1.96 * sigma, 1)))
        ci_upper = float(round(rul_point + 1.96 * sigma, 1))

        return rul_point, ci_lower, ci_upper

    @classmethod
    def assess_fleet(
        cls,
        operating_hours: float,
        feed_rate_kg_h: float = 100.0,
        reactor_temp_c: float = 500.0,
        ash_content_pct: float = 2.0,
        bio_oil_tan_mg_koh_g: float = 100.0,
        vibration_rms_mm_s: float = 2.5,
    ) -> FleetMaintenanceSummary:
        """Run prognostic evaluation across all 4 plant assets."""
        asset_summaries: Dict[str, AssetRULSummary] = {}

        # 1. Auger A101
        auger_state = AugerDegradationModel.evaluate(
            operating_hours=operating_hours,
            feed_rate_kg_h=feed_rate_kg_h,
            ash_content_pct=ash_content_pct,
            vibration_rms_mm_s=vibration_rms_mm_s,
        )
        rul_a, lo_a, hi_a = cls._compute_rul_with_uncertainty(
            operating_hours, auger_state.current_wear_value, auger_state.wear_threshold_eol
        )
        asset_summaries["AUGER_A101"] = AssetRULSummary(
            asset_id="AUGER_A101",
            asset_name="Biomass Infeed Auger Screw",
            current_operating_hours=operating_hours,
            current_health_index_pct=auger_state.health_index_pct,
            estimated_rul_hours=rul_a,
            rul_95_ci_lower_hours=lo_a,
            rul_95_ci_upper_hours=hi_a,
            maintenance_urgency=cls._triage_urgency(rul_a, auger_state.health_index_pct),
            degradation_state=auger_state,
        )

        # 2. Refractory Liner R101
        ref_state = RefractoryDegradationModel.evaluate(
            operating_hours=operating_hours,
            reactor_temp_c=reactor_temp_c,
        )
        rul_r, lo_r, hi_r = cls._compute_rul_with_uncertainty(
            operating_hours, ref_state.current_wear_value, ref_state.wear_threshold_eol
        )
        asset_summaries["REACTOR_R101_LINER"] = AssetRULSummary(
            asset_id="REACTOR_R101_LINER",
            asset_name="Pyrolysis Reactor Refractory Liner",
            current_operating_hours=operating_hours,
            current_health_index_pct=ref_state.health_index_pct,
            estimated_rul_hours=rul_r,
            rul_95_ci_lower_hours=lo_r,
            rul_95_ci_upper_hours=hi_r,
            maintenance_urgency=cls._triage_urgency(rul_r, ref_state.health_index_pct),
            degradation_state=ref_state,
        )

        # 3. Filter F101
        fil_state = FilterDegradationModel.evaluate(
            operating_hours=operating_hours,
        )
        rul_f, lo_f, hi_f = cls._compute_rul_with_uncertainty(
            operating_hours,
            fil_state.current_wear_value - FilterDegradationModel.P0_CLEAN_KPA,
            FilterDegradationModel.EOL_THRESHOLD_KPA - FilterDegradationModel.P0_CLEAN_KPA,
        )
        asset_summaries["FILTER_F101"] = AssetRULSummary(
            asset_id="FILTER_F101",
            asset_name="Syngas Particulate Ceramic Filter",
            current_operating_hours=operating_hours,
            current_health_index_pct=fil_state.health_index_pct,
            estimated_rul_hours=rul_f,
            rul_95_ci_lower_hours=lo_f,
            rul_95_ci_upper_hours=hi_f,
            maintenance_urgency=cls._triage_urgency(rul_f, fil_state.health_index_pct),
            degradation_state=fil_state,
        )

        # 4. Condenser HX102
        cond_state = CondenserDegradationModel.evaluate(
            operating_hours=operating_hours,
            bio_oil_tan_mg_koh_g=bio_oil_tan_mg_koh_g,
        )
        rul_c, lo_c, hi_c = cls._compute_rul_with_uncertainty(
            operating_hours, cond_state.current_wear_value, cond_state.wear_threshold_eol
        )
        asset_summaries["CONDENSER_HX102"] = AssetRULSummary(
            asset_id="CONDENSER_HX102",
            asset_name="Bio-Oil Condenser Tube Bundle",
            current_operating_hours=operating_hours,
            current_health_index_pct=cond_state.health_index_pct,
            estimated_rul_hours=rul_c,
            rul_95_ci_lower_hours=lo_c,
            rul_95_ci_upper_hours=hi_c,
            maintenance_urgency=cls._triage_urgency(rul_c, cond_state.health_index_pct),
            degradation_state=cond_state,
        )

        # Identify plant-wide bottleneck asset
        sorted_assets = sorted(asset_summaries.values(), key=lambda a: a.estimated_rul_hours)
        bottleneck = sorted_assets[0]

        return FleetMaintenanceSummary(
            current_operating_hours=operating_hours,
            assets=asset_summaries,
            most_critical_asset_id=bottleneck.asset_id,
            minimum_fleet_rul_hours=bottleneck.estimated_rul_hours,
        )
