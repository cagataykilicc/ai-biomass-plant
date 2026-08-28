"""Biomass feedstock loading, parsing, and preprocessing utilities.

Handles loading of feedstock definitions from YAML/JSON files and built-in repositories,
applying moisture adjustments, and validating process consistency.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional, List, Union
import yaml

from src.data.feedstock import (
    BiomassFeedstock,
    UltimateAnalysis,
    ProximateAnalysis,
    PhysicalProperties,
    FeedstockValidationError,
)


class FeedstockLibrary:
    """Repository of standardized and custom biomass feedstock profiles."""

    def __init__(self, config_dir: Optional[Union[str, Path]] = None) -> None:
        if config_dir is None:
            # Default to project configs/feedstocks directory
            self.config_dir = Path(__file__).resolve().parent.parent.parent / "configs" / "feedstocks"
        else:
            self.config_dir = Path(config_dir)

        self._cache: Dict[str, BiomassFeedstock] = {}

    def list_available_feedstocks(self) -> List[str]:
        """List all feedstock profiles available in the config directory."""
        if not self.config_dir.exists():
            return list(self._get_builtin_feedstocks().keys())

        yaml_files = list(self.config_dir.glob("*.yaml")) + list(self.config_dir.glob("*.yml"))
        names = [f.stem for f in yaml_files]
        for builtin_name in self._get_builtin_feedstocks().keys():
            if builtin_name not in names:
                names.append(builtin_name)
        return sorted(names)

    def load_feedstock(
        self,
        name_or_path: str,
        moisture_override: Optional[float] = None,
        particle_size_override: Optional[float] = None,
    ) -> BiomassFeedstock:
        """Load a biomass feedstock by name or direct file path, with optional overrides.

        Args:
            name_or_path: Identifier (e.g. 'olive_pomace') or path to YAML file.
            moisture_override: Optional moisture percentage to override the profile.
            particle_size_override: Optional particle size (mm) to override.

        Returns:
            BiomassFeedstock instance.
        """
        path = Path(name_or_path)
        if path.is_file():
            feedstock = self._load_from_yaml(path)
        else:
            # Try finding in config_dir
            yaml_path = self.config_dir / f"{name_or_path}.yaml"
            yml_path = self.config_dir / f"{name_or_path}.yml"
            if yaml_path.is_file():
                feedstock = self._load_from_yaml(yaml_path)
            elif yml_path.is_file():
                feedstock = self._load_from_yaml(yml_path)
            else:
                builtins = self._get_builtin_feedstocks()
                if name_or_path in builtins:
                    feedstock = builtins[name_or_path]
                else:
                    raise FileNotFoundError(
                        f"Feedstock '{name_or_path}' not found in {self.config_dir} or built-in presets."
                    )

        # Apply overrides if specified
        if moisture_override is not None:
            if not (0.0 <= moisture_override <= 95.0):
                raise FeedstockValidationError(f"Invalid moisture override: {moisture_override}%")
            feedstock.proximate.moisture = float(moisture_override)

        if particle_size_override is not None:
            if particle_size_override <= 0.0:
                raise FeedstockValidationError(f"Invalid particle size override: {particle_size_override} mm")
            feedstock.physical.particle_size_mm = float(particle_size_override)

        return feedstock

    def _load_from_yaml(self, path: Path) -> BiomassFeedstock:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return BiomassFeedstock.from_dict(data)

    def _get_builtin_feedstocks(self) -> Dict[str, BiomassFeedstock]:
        """Fallback built-in feedstock definitions."""
        return {
            "olive_pomace": BiomassFeedstock(
                name="Olive Pomace",
                category="agricultural_residue",
                description="Residue from olive oil extraction (orujo/pomace)",
                ultimate=UltimateAnalysis(carbon=50.2, hydrogen=6.2, oxygen=39.8, nitrogen=1.4, sulfur=0.1, ash=2.3),
                proximate=ProximateAnalysis(moisture=15.0, volatile_matter=76.5, fixed_carbon=21.2, ash=2.3),
                physical=PhysicalProperties(particle_size_mm=2.0, bulk_density_kg_m3=550.0, porosity=0.45),
            ),
            "pine_sawdust": BiomassFeedstock(
                name="Pine Sawdust",
                category="woody_biomass",
                description="Clean softwood pine sawdust from timber processing",
                ultimate=UltimateAnalysis(carbon=51.5, hydrogen=6.3, oxygen=41.6, nitrogen=0.2, sulfur=0.05, ash=0.35),
                proximate=ProximateAnalysis(moisture=12.0, volatile_matter=82.5, fixed_carbon=17.15, ash=0.35),
                physical=PhysicalProperties(particle_size_mm=1.5, bulk_density_kg_m3=420.0, porosity=0.50),
            ),
            "wheat_straw": BiomassFeedstock(
                name="Wheat Straw",
                category="agricultural_residue",
                description="Post-harvest agricultural wheat cereal straw",
                ultimate=UltimateAnalysis(carbon=46.5, hydrogen=5.9, oxygen=41.2, nitrogen=0.7, sulfur=0.1, ash=5.6),
                proximate=ProximateAnalysis(moisture=14.0, volatile_matter=75.0, fixed_carbon=19.4, ash=5.6),
                physical=PhysicalProperties(particle_size_mm=3.0, bulk_density_kg_m3=220.0, porosity=0.60),
            ),
            "rice_husk": BiomassFeedstock(
                name="Rice Husk",
                category="agricultural_residue",
                description="Silica-rich outer protective hull of rice grains",
                ultimate=UltimateAnalysis(carbon=39.5, hydrogen=5.1, oxygen=36.5, nitrogen=0.4, sulfur=0.1, ash=18.4),
                proximate=ProximateAnalysis(moisture=10.0, volatile_matter=63.5, fixed_carbon=18.1, ash=18.4),
                physical=PhysicalProperties(particle_size_mm=2.5, bulk_density_kg_m3=340.0, porosity=0.52),
            ),
            "beech_wood": BiomassFeedstock(
                name="Beech Wood",
                category="woody_biomass",
                description="Hardwood beech timber residue",
                ultimate=UltimateAnalysis(carbon=49.5, hydrogen=6.1, oxygen=43.8, nitrogen=0.2, sulfur=0.02, ash=0.38),
                proximate=ProximateAnalysis(moisture=10.0, volatile_matter=84.0, fixed_carbon=15.62, ash=0.38),
                physical=PhysicalProperties(particle_size_mm=1.0, bulk_density_kg_m3=460.0),
            ),
            "sugarcane_bagasse": BiomassFeedstock(
                name="Sugarcane Bagasse",
                category="agricultural_residue",
                description="Fibrous residue remaining after crushing sugarcane stalks",
                ultimate=UltimateAnalysis(carbon=48.0, hydrogen=5.8, oxygen=43.5, nitrogen=0.3, sulfur=0.05, ash=2.35),
                proximate=ProximateAnalysis(moisture=18.0, volatile_matter=81.0, fixed_carbon=16.65, ash=2.35),
                physical=PhysicalProperties(particle_size_mm=2.0, bulk_density_kg_m3=180.0),
            ),
            "miscanthus": BiomassFeedstock(
                name="Miscanthus",
                category="energy_crop",
                description="Perennial high-yield lignocellulosic energy crop grass",
                ultimate=UltimateAnalysis(carbon=48.5, hydrogen=5.7, oxygen=42.6, nitrogen=0.6, sulfur=0.1, ash=2.5),
                proximate=ProximateAnalysis(moisture=11.0, volatile_matter=79.5, fixed_carbon=18.0, ash=2.5),
                physical=PhysicalProperties(particle_size_mm=2.2, bulk_density_kg_m3=200.0),
            ),
            "almond_shells": BiomassFeedstock(
                name="Almond Shells",
                category="nut_shells",
                description="Dense, lignin-rich hard nutshell byproduct from almond hulling",
                ultimate=UltimateAnalysis(carbon=51.0, hydrogen=6.0, oxygen=39.5, nitrogen=0.5, sulfur=0.05, ash=2.95),
                proximate=ProximateAnalysis(moisture=10.0, volatile_matter=73.5, fixed_carbon=23.55, ash=2.95),
                physical=PhysicalProperties(particle_size_mm=3.5, bulk_density_kg_m3=480.0),
            ),
        }
