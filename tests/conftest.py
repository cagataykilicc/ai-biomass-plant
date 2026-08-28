"""Pytest fixtures for biomass conversion plant unit and integration tests."""

import pytest
from src.data.feedstock import (
    BiomassFeedstock,
    UltimateAnalysis,
    ProximateAnalysis,
    PhysicalProperties,
)
from src.data.preprocessing import FeedstockLibrary
from src.simulation.plant_simulator import BiomassPlantSimulator
from src.utils.config import PlantScenarioConfig


@pytest.fixture
def sample_olive_pomace() -> BiomassFeedstock:
    """Standard Olive Pomace feedstock fixture."""
    return BiomassFeedstock(
        name="Olive Pomace",
        category="agricultural_residue",
        description="Standard test olive pomace sample",
        ultimate=UltimateAnalysis(
            carbon=50.2, hydrogen=6.2, oxygen=39.8, nitrogen=1.4, sulfur=0.1, ash=2.3
        ),
        proximate=ProximateAnalysis(
            moisture=15.0, volatile_matter=76.5, fixed_carbon=21.2, ash=2.3
        ),
        physical=PhysicalProperties(
            particle_size_mm=2.0, bulk_density_kg_m3=550.0, porosity=0.45
        ),
    )


@pytest.fixture
def sample_pine_sawdust() -> BiomassFeedstock:
    """Pine sawdust woody biomass fixture."""
    return BiomassFeedstock(
        name="Pine Sawdust",
        category="woody_biomass",
        description="Test pine sawdust sample",
        ultimate=UltimateAnalysis(
            carbon=51.5, hydrogen=6.3, oxygen=41.6, nitrogen=0.2, sulfur=0.05, ash=0.35
        ),
        proximate=ProximateAnalysis(
            moisture=12.0, volatile_matter=82.5, fixed_carbon=17.15, ash=0.35
        ),
        physical=PhysicalProperties(
            particle_size_mm=1.5, bulk_density_kg_m3=420.0, porosity=0.50
        ),
    )


@pytest.fixture
def feedstock_library() -> FeedstockLibrary:
    """FeedstockLibrary fixture."""
    return FeedstockLibrary()


@pytest.fixture
def plant_simulator(feedstock_library: FeedstockLibrary) -> BiomassPlantSimulator:
    """BiomassPlantSimulator fixture."""
    return BiomassPlantSimulator(feedstock_library=feedstock_library)


@pytest.fixture
def standard_scenario() -> PlantScenarioConfig:
    """Standard baseline scenario config fixture."""
    return PlantScenarioConfig(
        feedstock_name="olive_pomace",
        feed_rate_kg_h=100.0,
        moisture_pct_override=15.0,
        particle_size_mm_override=2.0,
    )
