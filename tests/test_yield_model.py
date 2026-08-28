"""Unit tests for the pyrolysis yield kinetics and empirical correlations."""

import pytest
from src.data.feedstock import BiomassFeedstock
from src.models.yield_model import EmpiricalPyrolysisYieldModel, YieldFractions


def test_yield_fractions_normalization() -> None:
    """Test YieldFractions unity sum enforcement."""
    yf = YieldFractions(biochar_yield=0.30, bio_oil_yield=0.50, syngas_yield=0.20)
    assert sum([yf.biochar_yield, yf.bio_oil_yield, yf.syngas_yield]) == 1.0

    with pytest.raises(ValueError, match="Yield fractions must sum to 1.0"):
        YieldFractions(biochar_yield=0.40, bio_oil_yield=0.50, syngas_yield=0.30)


def test_yield_model_normalization_across_temperatures(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify that empirical yield model strictly normalizes yields across 300 - 800 °C."""
    model = EmpiricalPyrolysisYieldModel()
    for temp in [350.0, 400.0, 450.0, 500.0, 550.0, 600.0, 700.0, 800.0]:
        daf_yields, dry_yields = model.predict_yields(
            temperature_c=temp,
            heating_rate_c_min=10.0,
            residence_time_min=20.0,
            feedstock=sample_olive_pomace,
        )
        total_daf = daf_yields.biochar_yield + daf_yields.bio_oil_yield + daf_yields.syngas_yield
        total_dry = dry_yields.biochar_yield + dry_yields.bio_oil_yield + dry_yields.syngas_yield

        assert pytest.approx(total_daf, rel=1e-5) == 1.0
        assert pytest.approx(total_dry, rel=1e-5) == 1.0


def test_temperature_yield_trends(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify physical trend: biochar decreases with temperature, syngas increases with temperature."""
    model = EmpiricalPyrolysisYieldModel()
    _, yields_low = model.predict_yields(temperature_c=380.0, heating_rate_c_min=10.0, residence_time_min=20.0, feedstock=sample_olive_pomace)
    _, yields_high = model.predict_yields(temperature_c=700.0, heating_rate_c_min=10.0, residence_time_min=20.0, feedstock=sample_olive_pomace)

    # Low temp should produce significantly higher char
    assert yields_low.biochar_yield > yields_high.biochar_yield
    # High temp should produce significantly higher syngas
    assert yields_high.syngas_yield > yields_low.syngas_yield


def test_heating_rate_influence(sample_olive_pomace: BiomassFeedstock) -> None:
    """Verify slow heating rate increases char yield compared to fast heating rate."""
    model = EmpiricalPyrolysisYieldModel()
    _, slow_yields = model.predict_yields(temperature_c=500.0, heating_rate_c_min=5.0, residence_time_min=20.0, feedstock=sample_olive_pomace)
    _, fast_yields = model.predict_yields(temperature_c=500.0, heating_rate_c_min=500.0, residence_time_min=0.5, feedstock=sample_olive_pomace)

    assert slow_yields.biochar_yield > fast_yields.biochar_yield
