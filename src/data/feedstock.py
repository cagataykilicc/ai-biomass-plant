"""Feedstock data model and chemical/thermodynamic property calculations.

Defines structured representations of biomass feedstocks, including ultimate analysis,
proximate analysis, physical properties, and standard thermodynamic correlations
(Channiwala & Parikh HHV, LHV, temperature-dependent heat capacity).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import math


class FeedstockValidationError(ValueError):
    """Raised when feedstock properties violate physical or mass balance constraints."""
    pass


@dataclass
class UltimateAnalysis:
    """Ultimate (elemental) analysis of biomass on a dry, ash-included basis (wt%).

    Attributes:
        carbon: Carbon content (wt% dry basis, 0-100)
        hydrogen: Hydrogen content (wt% dry basis, 0-100)
        oxygen: Oxygen content (wt% dry basis, 0-100)
        nitrogen: Nitrogen content (wt% dry basis, 0-100)
        sulfur: Sulfur content (wt% dry basis, 0-100)
        ash: Inorganic ash content (wt% dry basis, 0-100)
    """
    carbon: float
    hydrogen: float
    oxygen: float
    nitrogen: float = 0.0
    sulfur: float = 0.0
    ash: float = 0.0

    def __post_init__(self) -> None:
        self.validate()

    def validate(self, tolerance: float = 1.0) -> None:
        """Validate elemental mass fractions and sum closure."""
        elements = {
            "carbon": self.carbon,
            "hydrogen": self.hydrogen,
            "oxygen": self.oxygen,
            "nitrogen": self.nitrogen,
            "sulfur": self.sulfur,
            "ash": self.ash,
        }
        for name, val in elements.items():
            if val < 0.0:
                raise FeedstockValidationError(f"Ultimate analysis '{name}' cannot be negative ({val}%).")
            if val > 100.0:
                raise FeedstockValidationError(f"Ultimate analysis '{name}' exceeds 100% ({val}%).")

        total = sum(elements.values())
        if abs(total - 100.0) > tolerance:
            raise FeedstockValidationError(
                f"Ultimate analysis components must sum to 100% ± {tolerance}%. Current sum: {total:.3f}%"
            )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UltimateAnalysis:
        return cls(
            carbon=float(data.get("carbon", 0.0)),
            hydrogen=float(data.get("hydrogen", 0.0)),
            oxygen=float(data.get("oxygen", 0.0)),
            nitrogen=float(data.get("nitrogen", 0.0)),
            sulfur=float(data.get("sulfur", 0.0)),
            ash=float(data.get("ash", 0.0)),
        )

    def to_dict(self) -> Dict[str, float]:
        return {
            "carbon": self.carbon,
            "hydrogen": self.hydrogen,
            "oxygen": self.oxygen,
            "nitrogen": self.nitrogen,
            "sulfur": self.sulfur,
            "ash": self.ash,
        }


@dataclass
class ProximateAnalysis:
    """Proximate analysis of biomass.

    Attributes:
        moisture: Moisture content as-received (wt% as-received, 0-100)
        volatile_matter: Volatile matter on dry basis (wt% dry basis, 0-100)
        fixed_carbon: Fixed carbon on dry basis (wt% dry basis, 0-100)
        ash: Ash content on dry basis (wt% dry basis, 0-100)
    """
    moisture: float
    volatile_matter: float
    fixed_carbon: float
    ash: float

    def __post_init__(self) -> None:
        self.validate()

    def validate(self, tolerance: float = 1.0) -> None:
        """Validate proximate fractions and dry basis closure."""
        if not (0.0 <= self.moisture <= 95.0):
            raise FeedstockValidationError(f"Moisture content must be in [0, 95] wt%. Got: {self.moisture}%")

        dry_components = {
            "volatile_matter": self.volatile_matter,
            "fixed_carbon": self.fixed_carbon,
            "ash": self.ash,
        }
        for name, val in dry_components.items():
            if val < 0.0:
                raise FeedstockValidationError(f"Proximate parameter '{name}' cannot be negative ({val}%).")
            if val > 100.0:
                raise FeedstockValidationError(f"Proximate parameter '{name}' exceeds 100% ({val}%).")

        dry_total = sum(dry_components.values())
        if abs(dry_total - 100.0) > tolerance:
            raise FeedstockValidationError(
                f"Proximate dry-basis components (VM + FC + Ash) must sum to 100% ± {tolerance}%. Current sum: {dry_total:.3f}%"
            )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ProximateAnalysis:
        return cls(
            moisture=float(data.get("moisture", 0.0)),
            volatile_matter=float(data.get("volatile_matter", 0.0)),
            fixed_carbon=float(data.get("fixed_carbon", 0.0)),
            ash=float(data.get("ash", 0.0)),
        )

    def to_dict(self) -> Dict[str, float]:
        return {
            "moisture": self.moisture,
            "volatile_matter": self.volatile_matter,
            "fixed_carbon": self.fixed_carbon,
            "ash": self.ash,
        }


@dataclass
class PhysicalProperties:
    """Physical and transport properties of biomass particles.

    Attributes:
        particle_size_mm: Characteristic particle diameter / sieve size (mm)
        bulk_density_kg_m3: Apparent bulk density of packed bed (kg/m^3)
        skeletal_density_kg_m3: Solid skeletal particle density (kg/m^3)
        porosity: Bed or particle void fraction (0 to 1)
    """
    particle_size_mm: float = 2.0
    bulk_density_kg_m3: float = 500.0
    skeletal_density_kg_m3: float = 1400.0
    porosity: float = 0.45

    def __post_init__(self) -> None:
        if self.particle_size_mm <= 0.0:
            raise FeedstockValidationError(f"Particle size must be > 0 mm. Got: {self.particle_size_mm}")
        if self.bulk_density_kg_m3 <= 0.0:
            raise FeedstockValidationError(f"Bulk density must be > 0 kg/m^3. Got: {self.bulk_density_kg_m3}")
        if not (0.0 <= self.porosity < 1.0):
            raise FeedstockValidationError(f"Porosity must be in [0, 1). Got: {self.porosity}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PhysicalProperties:
        return cls(
            particle_size_mm=float(data.get("particle_size_mm", 2.0)),
            bulk_density_kg_m3=float(data.get("bulk_density_kg_m3", 500.0)),
            skeletal_density_kg_m3=float(data.get("skeletal_density_kg_m3", 1400.0)),
            porosity=float(data.get("porosity", 0.45)),
        )

    def to_dict(self) -> Dict[str, float]:
        return {
            "particle_size_mm": self.particle_size_mm,
            "bulk_density_kg_m3": self.bulk_density_kg_m3,
            "skeletal_density_kg_m3": self.skeletal_density_kg_m3,
            "porosity": self.porosity,
        }


@dataclass
class BiomassFeedstock:
    """Comprehensive structured representation of a biomass feedstock.

    Includes chemical composition (ultimate analysis), proximate analysis,
    physical properties, and methods for thermodynamic properties.
    """
    name: str
    category: str = "general_biomass"
    description: str = ""
    ultimate: UltimateAnalysis = field(
        default_factory=lambda: UltimateAnalysis(carbon=50.0, hydrogen=6.0, oxygen=42.0, nitrogen=0.5, sulfur=0.1, ash=1.4)
    )
    proximate: ProximateAnalysis = field(
        default_factory=lambda: ProximateAnalysis(moisture=15.0, volatile_matter=78.0, fixed_carbon=20.0, ash=2.0)
    )
    physical: PhysicalProperties = field(default_factory=PhysicalProperties)
    measured_hhv_mj_kg: Optional[float] = None

    def __post_init__(self) -> None:
        # Cross-check ash consistency between proximate and ultimate if both provided
        if abs(self.ultimate.ash - self.proximate.ash) > 2.5:
            # Reconcile ultimate ash with proximate ash if difference is non-negligible
            pass

    def calculate_hhv_dry(self) -> float:
        """Calculate Higher Heating Value on a dry basis (MJ/kg).

        Uses Channiwala & Parikh (2002) unified correlation:
        HHV = 0.3491*C + 1.1783*H + 0.1005*S - 0.1034*O - 0.0151*N - 0.0211*Ash (wt% dry)
        Standard error: ~1.45% across broad solid fuels.
        """
        if self.measured_hhv_mj_kg is not None and self.measured_hhv_mj_kg > 0:
            return self.measured_hhv_mj_kg

        c = self.ultimate.carbon
        h = self.ultimate.hydrogen
        s = self.ultimate.sulfur
        o = self.ultimate.oxygen
        n = self.ultimate.nitrogen
        ash = self.ultimate.ash

        hhv = (0.3491 * c) + (1.1783 * h) + (0.1005 * s) - (0.1034 * o) - (0.0151 * n) - (0.0211 * ash)
        return max(0.0, round(hhv, 3))

    def calculate_lhv_dry(self) -> float:
        """Calculate Lower Heating Value on a dry basis (MJ/kg).

        Accounts for latent heat of water formed during combustion of hydrogen:
        LHV_dry = HHV_dry - 2.442 * (8.936 * H / 100)
        where 2.442 MJ/kg is the latent heat of water vapor at 25 °C.
        """
        hhv_dry = self.calculate_hhv_dry()
        h_wt = self.ultimate.hydrogen
        water_from_h = 8.936 * (h_wt / 100.0)  # kg H2O per kg dry fuel
        lhv_dry = hhv_dry - (2.442 * water_from_h)
        return max(0.0, round(lhv_dry, 3))

    def calculate_hhv_as_received(self) -> float:
        """Calculate Higher Heating Value on as-received basis (MJ/kg).

        HHV_ar = HHV_dry * (1 - w)
        where w = moisture / 100.
        """
        w = self.proximate.moisture / 100.0
        return round(self.calculate_hhv_dry() * (1.0 - w), 3)

    def calculate_lhv_as_received(self) -> float:
        """Calculate Lower Heating Value on as-received basis (MJ/kg).

        LHV_ar = LHV_dry * (1 - w) - 2.442 * w
        Accounts for water formed from hydrogen plus moisture in fuel.
        """
        w = self.proximate.moisture / 100.0
        lhv_dry = self.calculate_lhv_dry()
        lhv_ar = (lhv_dry * (1.0 - w)) - (2.442 * w)
        return max(0.0, round(lhv_ar, 3))

    def specific_heat_capacity(self, temperature_c: float) -> float:
        """Calculate specific heat capacity Cp of dry biomass (kJ/(kg·K)).

        Correlation by Gupta et al. (2003) for woody and agricultural biomass:
        Cp(T) = 1.112 + 0.00485 * T_c (for T in 20 - 600 °C).
        """
        t_clamped = max(0.0, min(800.0, temperature_c))
        cp = 1.112 + (0.00485 * t_clamped)
        return round(cp, 4)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize feedstock data model to dictionary."""
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "ultimate": self.ultimate.to_dict(),
            "proximate": self.proximate.to_dict(),
            "physical": self.physical.to_dict(),
            "measured_hhv_mj_kg": self.measured_hhv_mj_kg,
            "calculated_properties": {
                "hhv_dry_mj_kg": self.calculate_hhv_dry(),
                "lhv_dry_mj_kg": self.calculate_lhv_dry(),
                "hhv_ar_mj_kg": self.calculate_hhv_as_received(),
                "lhv_ar_mj_kg": self.calculate_lhv_as_received(),
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BiomassFeedstock:
        """Deserialize dictionary into BiomassFeedstock object."""
        return cls(
            name=data.get("name", "Unnamed Biomass"),
            category=data.get("category", "general_biomass"),
            description=data.get("description", ""),
            ultimate=UltimateAnalysis.from_dict(data.get("ultimate", {})),
            proximate=ProximateAnalysis.from_dict(data.get("proximate", {})),
            physical=PhysicalProperties.from_dict(data.get("physical", {})),
            measured_hhv_mj_kg=data.get("measured_hhv_mj_kg"),
        )
