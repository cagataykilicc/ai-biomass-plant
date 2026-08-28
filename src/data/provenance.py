"""Data provenance, scientific lineage, and source tracking framework.

Enforces strict distinction between real experimental literature data, industrial measurements,
and synthetically simulated datasets in compliance with Scientific Integrity standards.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, Optional


class DataSourceType(str, Enum):
    """Classification of data origin."""
    SYNTHETIC_SIMULATED = "SYNTHETIC_SIMULATED"
    EXPERIMENTAL_LITERATURE = "EXPERIMENTAL_LITERATURE"
    INDUSTRIAL_PILOT = "INDUSTRIAL_PILOT"
    BENCH_SCALE_LAB = "BENCH_SCALE_LAB"


@dataclass
class DataProvenance:
    """Rigorous scientific lineage and metadata record for a dataset or observation.

    Attributes:
        source_type: Category of origin (Synthetic vs Experimental).
        citation: Formal academic bibliographic reference (if literature).
        doi: Digital Object Identifier (if literature/published).
        authors: Author list or data generator identity.
        publication_year: Year of publication or experimental run.
        facility_or_model: Experimental facility name or simulator model version.
        license_name: Data distribution license.
        created_at_utc: ISO-8601 UTC creation timestamp.
        is_synthetic: Boolean flag explicitly declaring synthetic nature.
        sensor_noise_applied: Whether measurement uncertainty/noise was added.
        validation_status: Validation gate result ("VERIFIED", "PROVISIONAL", "FAILED").
    """
    source_type: DataSourceType
    citation: Optional[str] = None
    doi: Optional[str] = None
    authors: Optional[str] = None
    publication_year: Optional[int] = None
    facility_or_model: str = "BiomassPlantSimulator_V0.3"
    license_name: str = "CC-BY-4.0"
    created_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_synthetic: bool = False
    sensor_noise_applied: bool = False
    validation_status: str = "VERIFIED"

    def __post_init__(self) -> None:
        if self.source_type == DataSourceType.SYNTHETIC_SIMULATED:
            self.is_synthetic = True
        elif self.source_type in [DataSourceType.EXPERIMENTAL_LITERATURE, DataSourceType.BENCH_SCALE_LAB]:
            self.is_synthetic = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_type": self.source_type.value if isinstance(self.source_type, DataSourceType) else self.source_type,
            "is_synthetic": self.is_synthetic,
            "citation": self.citation,
            "doi": self.doi,
            "authors": self.authors,
            "publication_year": self.publication_year,
            "facility_or_model": self.facility_or_model,
            "license_name": self.license_name,
            "created_at_utc": self.created_at_utc,
            "sensor_noise_applied": self.sensor_noise_applied,
            "validation_status": self.validation_status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DataProvenance:
        src_str = data.get("source_type", "SYNTHETIC_SIMULATED")
        try:
            src_type = DataSourceType(src_str)
        except ValueError:
            src_type = DataSourceType.SYNTHETIC_SIMULATED

        return cls(
            source_type=src_type,
            citation=data.get("citation"),
            doi=data.get("doi"),
            authors=data.get("authors"),
            publication_year=data.get("publication_year"),
            facility_or_model=data.get("facility_or_model", "BiomassPlantSimulator_V0.3"),
            license_name=data.get("license_name", "CC-BY-4.0"),
            created_at_utc=data.get("created_at_utc", datetime.now(timezone.utc).isoformat()),
            is_synthetic=bool(data.get("is_synthetic", src_type == DataSourceType.SYNTHETIC_SIMULATED)),
            sensor_noise_applied=bool(data.get("sensor_noise_applied", False)),
            validation_status=data.get("validation_status", "VERIFIED"),
        )
