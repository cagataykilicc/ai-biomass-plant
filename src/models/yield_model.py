"""Pyrolysis product yield kinetic and semi-empirical correlations.

Implements transparent, phenomenological yield calculations for biochar, bio-oil,
and syngas as a function of temperature, heating rate, residence time, and feedstock composition.
Enforces rigorous mass conservation and yield normalization: Y_char + Y_oil + Y_gas = 1.0.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Tuple
import math

from src.data.feedstock import BiomassFeedstock


@dataclass
class YieldFractions:
    """Normalized mass yield fractions of pyrolysis products.

    Attributes:
        biochar_yield: Mass fraction of solid biochar (dry or DAF basis, 0 to 1).
        bio_oil_yield: Mass fraction of condensable bio-oil organics (0 to 1).
        syngas_yield: Mass fraction of non-condensable syngas (0 to 1).
    """
    biochar_yield: float
    bio_oil_yield: float
    syngas_yield: float

    def __post_init__(self) -> None:
        self.validate()

    def validate(self, tolerance: float = 1e-4) -> None:
        """Ensure non-negative yields and strict unity sum."""
        yields = [self.biochar_yield, self.bio_oil_yield, self.syngas_yield]
        for y in yields:
            if y < -1e-6:
                raise ValueError(f"Yield fraction cannot be negative ({y}).")
        total = sum(yields)
        if abs(total - 1.0) > tolerance:
            raise ValueError(f"Yield fractions must sum to 1.0 (got {total:.6f}).")

    def to_dict(self) -> Dict[str, float]:
        return {
            "biochar_yield": round(self.biochar_yield, 5),
            "bio_oil_yield": round(self.bio_oil_yield, 5),
            "syngas_yield": round(self.syngas_yield, 5),
        }


class EmpiricalPyrolysisYieldModel:
    """Phenomenological pyrolysis yield model based on multi-component kinetics

    Correlates product yields with reactor temperature (300 - 800 °C), heating rate
    (slow vs intermediate vs fast), residence time, and feedstock composition (ash, volatile matter).
    """

    def __init__(self) -> None:
        # Reference kinetic parameters
        self.t_char_mid = 420.0       # °C (inflection temperature for char decomposition)
        self.s_char = 55.0            # °C (transition width)
        self.char_min_daf = 0.12      # High-temperature asymptotic char fraction
        self.char_max_daf = 0.72      # Low-temperature (torrefaction-onset) char fraction

        self.t_gas_mid = 580.0        # °C (inflection temperature for secondary cracking gas surge)
        self.s_gas = 75.0             # °C
        self.gas_min_daf = 0.10       # Low-temperature baseline gas fraction
        self.gas_max_daf = 0.65       # High-temperature asymptotic gas fraction

    def predict_yields(
        self,
        temperature_c: float,
        heating_rate_c_min: float,
        residence_time_min: float,
        feedstock: BiomassFeedstock,
    ) -> Tuple[YieldFractions, YieldFractions]:
        """Predict product yields on dry-ash-free (DAF) and dry-basis.

        Args:
            temperature_c: Pyrolysis reactor temperature (°C, valid range ~300 to 800 °C).
            heating_rate_c_min: Heating rate (°C/min, e.g. 5 to 5000 °C/min).
            residence_time_min: Vapor/solids residence time (min).
            feedstock: BiomassFeedstock providing proximate/ultimate composition.

        Returns:
            Tuple of (YieldFractions on DAF basis, YieldFractions on dry basis).
        """
        if not (200.0 <= temperature_c <= 1000.0):
            raise ValueError(f"Reactor temperature out of physical range (200-1000 °C): {temperature_c} °C")
        if heating_rate_c_min <= 0.0:
            raise ValueError(f"Heating rate must be positive: {heating_rate_c_min} °C/min")
        if residence_time_min <= 0.0:
            raise ValueError(f"Residence time must be positive: {residence_time_min} min")

        # 1. Base DAF Char yield as a decreasing sigmoidal function of temperature
        # y_char = char_min + (char_max - char_min) / (1 + exp((T - T_mid) / s))
        char_logistic = 1.0 / (1.0 + math.exp((temperature_c - self.t_char_mid) / self.s_char))
        y_char_raw = self.char_min_daf + (self.char_max_daf - self.char_min_daf) * char_logistic

        # Heating rate effect: Lower heating rates (<20 °C/min) promote secondary charring
        log_hr = math.log10(max(1.0, heating_rate_c_min))
        hr_char_factor = 1.0 + 0.18 * max(0.0, (2.0 - log_hr) / 2.0)
        
        # Fixed carbon adjustment (higher fixed carbon increases char yield)
        fc_factor = 1.0 + 0.006 * (feedstock.proximate.fixed_carbon - 20.0)
        
        y_char_adj = max(0.05, y_char_raw * hr_char_factor * fc_factor)

        # 2. Base DAF Gas yield as an increasing sigmoidal function of temperature
        # y_gas = gas_min + (gas_max - gas_min) / (1 + exp(-(T - T_mid) / s))
        gas_logistic = 1.0 / (1.0 + math.exp(-(temperature_c - self.t_gas_mid) / self.s_gas))
        y_gas_raw = self.gas_min_daf + (self.gas_max_daf - self.gas_min_daf) * gas_logistic

        # Secondary thermal cracking of vapors at high temperature and long residence time
        cracking_factor = 1.0
        if temperature_c > 480.0:
            temp_excess = (temperature_c - 480.0) / 200.0
            time_effect = min(1.0, residence_time_min / 15.0)
            cracking_factor += 0.25 * temp_excess * time_effect

        # Ash catalytic effect: Inorganic alkali metals (K, Na, Ca) promote gasification and charring
        ash_factor = 1.0 + 0.008 * min(25.0, feedstock.ultimate.ash)
        y_gas_adj = max(0.05, y_gas_raw * cracking_factor * ash_factor)

        # 3. Base DAF Bio-oil yield (organics)
        # Bio-oil is the primary condensable volatile product
        y_oil_raw = max(0.05, 1.0 - y_char_adj - y_gas_adj)

        # 4. Strict Normalization on DAF basis
        total_daf = y_char_adj + y_oil_raw + y_gas_adj
        y_char_daf = y_char_adj / total_daf
        y_oil_daf = y_oil_raw / total_daf
        y_gas_daf = y_gas_adj / total_daf

        daf_yields = YieldFractions(
            biochar_yield=y_char_daf,
            bio_oil_yield=y_oil_daf,
            syngas_yield=y_gas_daf,
        )

        # 5. Conversion to Dry Basis (integrating inorganic ash into solid biochar)
        ash_fraction = feedstock.ultimate.ash / 100.0
        daf_fraction = 1.0 - ash_fraction

        # Ash is fully conserved in the solid char product under pyrolysis conditions
        y_char_dry = (y_char_daf * daf_fraction) + ash_fraction
        y_oil_dry = y_oil_daf * daf_fraction
        y_gas_dry = y_gas_daf * daf_fraction

        dry_yields = YieldFractions(
            biochar_yield=y_char_dry,
            bio_oil_yield=y_oil_dry,
            syngas_yield=y_gas_dry,
        )

        return daf_yields, dry_yields
