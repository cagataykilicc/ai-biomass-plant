"""Unit tests for physics-informed asset degradation models."""

import pytest
from src.maintenance.degradation_models import (
    AugerDegradationModel,
    RefractoryDegradationModel,
    FilterDegradationModel,
    CondenserDegradationModel,
    AssetDegradationState,
)


def test_auger_degradation_wear() -> None:
    """Verify infeed auger flight thickness wear increases with hours and ash."""
    state_early = AugerDegradationModel.evaluate(operating_hours=1000.0, ash_content_pct=2.0)
    state_late = AugerDegradationModel.evaluate(operating_hours=6000.0, ash_content_pct=2.0)

    assert isinstance(state_early, AssetDegradationState)
    assert state_early.current_wear_value < state_late.current_wear_value
    assert state_early.health_index_pct > state_late.health_index_pct
    assert 0.0 <= state_late.health_index_pct <= 100.0


def test_refractory_and_filter_degradation() -> None:
    """Verify refractory thickness loss and ceramic filter delta-P blinding."""
    ref_state = RefractoryDegradationModel.evaluate(operating_hours=4000.0, reactor_temp_c=520.0)
    assert ref_state.current_wear_value > 0.0
    assert ref_state.health_index_pct < 100.0

    fil_state = FilterDegradationModel.evaluate(operating_hours=5000.0)
    assert fil_state.current_wear_value > FilterDegradationModel.P0_CLEAN_KPA
    assert fil_state.health_index_pct < 100.0


def test_condenser_tube_corrosion() -> None:
    """Verify condenser corrosion increases with bio-oil TAN."""
    state_low_tan = CondenserDegradationModel.evaluate(operating_hours=3000.0, bio_oil_tan_mg_koh_g=60.0)
    state_high_tan = CondenserDegradationModel.evaluate(operating_hours=3000.0, bio_oil_tan_mg_koh_g=120.0)

    assert state_high_tan.current_wear_value > state_low_tan.current_wear_value
    assert state_high_tan.health_index_pct < state_low_tan.health_index_pct
