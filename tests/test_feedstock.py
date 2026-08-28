"""Unit tests for BiomassFeedstock and thermodynamic property calculations."""

import pytest
from src.data.feedstock import (
    BiomassFeedstock,
    UltimateAnalysis,
    ProximateAnalysis,
    PhysicalProperties,
    FeedstockValidationError,
)


def test_valid_feedstock_creation(sample_olive_pomace: BiomassFeedstock) -> None:
    """Test valid feedstock instantiation and field accessibility."""
    assert sample_olive_pomace.name == "Olive Pomace"
    assert sample_olive_pomace.ultimate.carbon == 50.2
    assert sample_olive_pomace.proximate.moisture == 15.0
    assert sample_olive_pomace.physical.particle_size_mm == 2.0


def test_ultimate_analysis_sum_validation() -> None:
    """Test that ultimate analysis components must sum to 100%."""
    with pytest.raises(FeedstockValidationError, match="Ultimate analysis components must sum to 100%"):
        UltimateAnalysis(carbon=60.0, hydrogen=10.0, oxygen=50.0, nitrogen=1.0, sulfur=0.1, ash=2.0)


def test_ultimate_analysis_negative_value() -> None:
    """Test that negative elemental percentages are rejected."""
    with pytest.raises(FeedstockValidationError, match="cannot be negative"):
        UltimateAnalysis(carbon=-5.0, hydrogen=6.0, oxygen=97.0, nitrogen=1.0, sulfur=0.0, ash=1.0)


def test_proximate_analysis_sum_validation() -> None:
    """Test proximate analysis dry basis sum validation."""
    with pytest.raises(FeedstockValidationError, match="Proximate dry-basis components"):
        ProximateAnalysis(moisture=10.0, volatile_matter=90.0, fixed_carbon=30.0, ash=5.0)


def test_proximate_moisture_bounds() -> None:
    """Test that excessive or negative moisture is rejected."""
    with pytest.raises(FeedstockValidationError, match="Moisture content must be in"):
        ProximateAnalysis(moisture=-1.0, volatile_matter=80.0, fixed_carbon=18.0, ash=2.0)

    with pytest.raises(FeedstockValidationError, match="Moisture content must be in"):
        ProximateAnalysis(moisture=98.0, volatile_matter=80.0, fixed_carbon=18.0, ash=2.0)


def test_channiwala_parikh_hhv_calculation(sample_olive_pomace: BiomassFeedstock) -> None:
    """Test Channiwala & Parikh HHV dry correlation."""
    # HHV = 0.3491*C + 1.1783*H + 0.1005*S - 0.1034*O - 0.0151*N - 0.0211*Ash
    # For Olive Pomace: C=50.2, H=6.2, O=39.8, N=1.4, S=0.1, Ash=2.3
    # Expected HHV dry ~ 20.65 MJ/kg
    hhv_dry = sample_olive_pomace.calculate_hhv_dry()
    assert 18.0 <= hhv_dry <= 23.0
    assert isinstance(hhv_dry, float)


def test_lhv_dry_and_as_received(sample_olive_pomace: BiomassFeedstock) -> None:
    """Test LHV dry and LHV as-received calculations."""
    hhv_dry = sample_olive_pomace.calculate_hhv_dry()
    lhv_dry = sample_olive_pomace.calculate_lhv_dry()
    lhv_ar = sample_olive_pomace.calculate_lhv_as_received()

    # Physical consistency: HHV dry > LHV dry > LHV as-received
    assert hhv_dry > lhv_dry
    assert lhv_dry > lhv_ar
    assert lhv_ar > 0.0


def test_specific_heat_capacity(sample_olive_pomace: BiomassFeedstock) -> None:
    """Test temperature-dependent heat capacity calculation."""
    cp_25 = sample_olive_pomace.specific_heat_capacity(25.0)
    cp_500 = sample_olive_pomace.specific_heat_capacity(500.0)

    # Cp should increase with temperature
    assert cp_500 > cp_25
    assert 1.10 <= cp_25 <= 1.30
    assert 3.00 <= cp_500 <= 4.00
