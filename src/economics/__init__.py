"""Techno-Economic Analysis (TEA) and Life Cycle Assessment (LCA) Carbon Accounting module."""

from src.economics.tea_engine import (
    TechnoEconomicEngine,
    EquipmentCapitalCost,
    CapitalExpenditureSummary,
    OperationalExpenditureSummary,
    FinancialViabilityMetrics,
)
from src.economics.lca_engine import (
    LCACarbonEngine,
    ScopeEmissionsSummary,
    CarbonSequestrationMetrics,
    PlantLCAProfile,
)

__all__ = [
    "TechnoEconomicEngine",
    "EquipmentCapitalCost",
    "CapitalExpenditureSummary",
    "OperationalExpenditureSummary",
    "FinancialViabilityMetrics",
    "LCACarbonEngine",
    "ScopeEmissionsSummary",
    "CarbonSequestrationMetrics",
    "PlantLCAProfile",
]
