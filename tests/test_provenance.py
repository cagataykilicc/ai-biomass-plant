"""Unit tests for scientific data provenance and lineage framework."""

import pytest
from src.data.provenance import DataProvenance, DataSourceType


def test_synthetic_provenance_tagging() -> None:
    """Verify that synthetic data source automatically tags is_synthetic=True."""
    prov = DataProvenance(
        source_type=DataSourceType.SYNTHETIC_SIMULATED,
        facility_or_model="BiomassPlantSimulator_V0.3",
    )
    assert prov.is_synthetic is True
    assert prov.source_type == DataSourceType.SYNTHETIC_SIMULATED

    d = prov.to_dict()
    assert d["is_synthetic"] is True
    assert d["source_type"] == "SYNTHETIC_SIMULATED"


def test_literature_provenance_tagging() -> None:
    """Verify that experimental literature provenance maintains citation and DOI."""
    prov = DataProvenance(
        source_type=DataSourceType.EXPERIMENTAL_LITERATURE,
        citation="Neves et al. (2011) Prog Energy Combust Sci 37(5)",
        doi="10.1016/j.pecs.2011.01.001",
        authors="Neves, R.C. et al.",
        publication_year=2011,
    )
    assert prov.is_synthetic is False
    assert prov.citation is not None
    assert prov.doi == "10.1016/j.pecs.2011.01.001"

    prov_reconstructed = DataProvenance.from_dict(prov.to_dict())
    assert prov_reconstructed.is_synthetic is False
    assert prov_reconstructed.doi == "10.1016/j.pecs.2011.01.001"
