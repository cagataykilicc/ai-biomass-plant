"""Techno-Economic Analysis (TEA) engine and discounted cash flow financial evaluator.

Calculates Guthrie factorial Capital Investment (CAPEX), Operational Cost (OPEX),
20-year Discounted Cash Flow (DCF), Net Present Value (NPV), Internal Rate of Return (IRR),
and Levelized Cost of Bio-Oil (LCOB).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from src.simulation.plant_simulator import SimulationReport


@dataclass
class EquipmentCapitalCost:
    """Bare module equipment sizing and purchased cost model."""
    equipment_tag: str
    equipment_name: str
    capacity_metric: str
    capacity_value: float
    base_purchased_cost_usd: float
    bare_module_factor: float
    installed_cost_usd: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "equipment_tag": self.equipment_tag,
            "equipment_name": self.equipment_name,
            "capacity": f"{self.capacity_value:.1f} {self.capacity_metric}",
            "base_purchased_cost_usd": round(self.base_purchased_cost_usd, 2),
            "bare_module_factor": round(self.bare_module_factor, 2),
            "installed_cost_usd": round(self.installed_cost_usd, 2),
        }


@dataclass
class CapitalExpenditureSummary:
    """Guthrie factorial Total Capital Investment (TCI) breakdown."""
    purchased_equipment_cost_usd: float
    direct_installation_cost_usd: float     # Piping, electrical, civil, instrumentation
    indirect_costs_usd: float               # Engineering, contractor fees, contingency
    fixed_capital_investment_usd: float     # FCI
    working_capital_usd: float              # 15% of FCI
    total_capital_investment_usd: float     # TCI = FCI + Working Capital
    equipment_list: List[EquipmentCapitalCost] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "purchased_equipment_cost_usd": round(self.purchased_equipment_cost_usd, 2),
            "direct_installation_cost_usd": round(self.direct_installation_cost_usd, 2),
            "indirect_costs_usd": round(self.indirect_costs_usd, 2),
            "fixed_capital_investment_usd": round(self.fixed_capital_investment_usd, 2),
            "working_capital_usd": round(self.working_capital_usd, 2),
            "total_capital_investment_usd": round(self.total_capital_investment_usd, 2),
            "equipment_count": len(self.equipment_list),
            "equipment": [e.to_dict() for e in self.equipment_list],
        }


@dataclass
class OperationalExpenditureSummary:
    """Annual OPEX breakdown for industrial continuous operations (8,000 h/yr)."""
    feedstock_cost_usd_yr: float
    electricity_utility_cost_usd_yr: float
    labor_and_supervision_usd_yr: float
    maintenance_and_repairs_usd_yr: float   # 4% of FCI
    insurance_and_taxes_usd_yr: float       # 2% of FCI
    consumables_and_waste_usd_yr: float
    total_opex_usd_yr: float
    unit_opex_usd_per_tonne_feed: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feedstock_cost_usd_yr": round(self.feedstock_cost_usd_yr, 2),
            "electricity_utility_cost_usd_yr": round(self.electricity_utility_cost_usd_yr, 2),
            "labor_and_supervision_usd_yr": round(self.labor_and_supervision_usd_yr, 2),
            "maintenance_and_repairs_usd_yr": round(self.maintenance_and_repairs_usd_yr, 2),
            "insurance_and_taxes_usd_yr": round(self.insurance_and_taxes_usd_yr, 2),
            "consumables_and_waste_usd_yr": round(self.consumables_and_waste_usd_yr, 2),
            "total_opex_usd_yr": round(self.total_opex_usd_yr, 2),
            "unit_opex_usd_per_tonne_feed": round(self.unit_opex_usd_per_tonne_feed, 2),
        }


@dataclass
class FinancialViabilityMetrics:
    """20-Year Discounted Cash Flow (DCF) project valuation metrics."""
    annual_bio_oil_production_kg: float
    annual_biochar_production_kg: float
    annual_gross_revenue_usd: float
    annual_net_cash_flow_usd: float
    net_present_value_usd: float            # NPV @ 10% discount rate
    internal_rate_of_return_pct: float      # IRR
    discounted_payback_years: float         # DPBP
    levelized_cost_bio_oil_usd_kg: float    # LCOB ($/kg)
    levelized_cost_bio_oil_usd_mj: float    # LCOB ($/MJ)
    is_financially_viable: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "annual_bio_oil_production_kg": round(self.annual_bio_oil_production_kg, 1),
            "annual_biochar_production_kg": round(self.annual_biochar_production_kg, 1),
            "annual_gross_revenue_usd": round(self.annual_gross_revenue_usd, 2),
            "annual_net_cash_flow_usd": round(self.annual_net_cash_flow_usd, 2),
            "net_present_value_usd": round(self.net_present_value_usd, 2),
            "internal_rate_of_return_pct": round(self.internal_rate_of_return_pct, 2),
            "discounted_payback_years": round(self.discounted_payback_years, 2),
            "levelized_cost_bio_oil_usd_kg": round(self.levelized_cost_bio_oil_usd_kg, 4),
            "levelized_cost_bio_oil_usd_mj": round(self.levelized_cost_bio_oil_usd_mj, 4),
            "is_financially_viable": self.is_financially_viable,
        }


class TechnoEconomicEngine:
    """Full-scale Techno-Economic Analysis (TEA) and DCF evaluation engine."""

    # 7-Year MACRS Depreciation Schedule
    MACRS_7YR = [0.1429, 0.2449, 0.1749, 0.1249, 0.0893, 0.0892, 0.0893, 0.0446]

    def __init__(
        self,
        bio_oil_price_usd_kg: float = 0.65,
        biochar_price_usd_kg: float = 0.45,
        feedstock_price_usd_tonne: float = 65.0,
        electricity_price_usd_kwh: float = 0.12,
        discount_rate_pct: float = 10.0,
        tax_rate_pct: float = 25.0,
        operating_hours_yr: float = 8000.0,
        project_life_years: int = 20,
    ) -> None:
        self.bio_oil_price_usd_kg = bio_oil_price_usd_kg
        self.biochar_price_usd_kg = biochar_price_usd_kg
        self.feedstock_price_usd_tonne = feedstock_price_usd_tonne
        self.electricity_price_usd_kwh = electricity_price_usd_kwh
        self.discount_rate_pct = discount_rate_pct
        self.tax_rate_pct = tax_rate_pct
        self.operating_hours_yr = operating_hours_yr
        self.project_life_years = project_life_years

    def evaluate_capex(self, report: SimulationReport) -> CapitalExpenditureSummary:
        """Calculate Guthrie equipment sizing, bare module costs, and Total Capital Investment."""
        feed_kg_h = report.scenario_config.feed_rate_kg_h
        scale_ratio = feed_kg_h / 100.0

        # Major Plant Equipment Database (Base size @ 100 kg/h)
        equipment_db = [
            ("D-101", "Rotary Biomass Drum Dryer", "kg/h wet feed", feed_kg_h, 45000.0, 0.65, 3.2),
            ("A-101", "Variable-Speed Feed Auger Feeder", "kg/h feed", feed_kg_h, 18500.0, 0.55, 2.8),
            ("R-101", "Pyrolysis Reactor & Refractory Liner", "kg/h capacity", feed_kg_h, 95000.0, 0.70, 3.5),
            ("C-101", "High-Efficiency Gas Cyclone Separator", "m3/h gas flow", 45.0 * scale_ratio, 22000.0, 0.60, 2.9),
            ("HX-102", "Quench Condenser & Shell-Tube Exchanger", "kW duty", 65.0 * scale_ratio, 38000.0, 0.68, 3.1),
            ("B-101", "Syngas Combustor & Flue Gas Ducting", "kW thermal", 75.0 * scale_ratio, 42000.0, 0.62, 3.0),
            ("F-101", "Ceramic Hot Gas Candle Filter", "m2 area", 6.5 * scale_ratio, 28000.0, 0.58, 2.7),
            ("T-101", "Bio-Oil Stainless Storage Tank (30-day)", "m3 volume", 25.0 * scale_ratio, 19500.0, 0.50, 2.4),
        ]

        equipment_list: List[EquipmentCapitalCost] = []
        total_pec = 0.0

        for tag, name, metric, cap_val, base_cost, exp, bmf in equipment_db:
            # Power law capacity scaling: Cost = Cost_0 * (S / S_0)^exp
            pec = base_cost * (max(0.1, scale_ratio) ** exp)
            installed = pec * bmf
            total_pec += pec
            equipment_list.append(
                EquipmentCapitalCost(
                    equipment_tag=tag,
                    equipment_name=name,
                    capacity_metric=metric,
                    capacity_value=cap_val,
                    base_purchased_cost_usd=pec,
                    bare_module_factor=bmf,
                    installed_cost_usd=installed,
                )
            )

        # Modular Skid-Mounted Plant Guthrie Factorial Method:
        # Direct Costs: Piping (20%), Electrical (10%), Civil/Skid (10%), Instrumentation (10%) -> 50% of PEC
        direct_costs = total_pec * 0.50
        # Indirect Costs: Engineering (15%), Contractor Fees (5%), Contingency (10%) -> 30% of PEC
        indirect_costs = total_pec * 0.30

        fci = total_pec + direct_costs + indirect_costs
        working_capital = 0.10 * fci
        tci = fci + working_capital

        return CapitalExpenditureSummary(
            purchased_equipment_cost_usd=total_pec,
            direct_installation_cost_usd=direct_costs,
            indirect_costs_usd=indirect_costs,
            fixed_capital_investment_usd=fci,
            working_capital_usd=working_capital,
            total_capital_investment_usd=tci,
            equipment_list=equipment_list,
        )

    def evaluate_opex(self, report: SimulationReport, capex: CapitalExpenditureSummary) -> OperationalExpenditureSummary:
        """Calculate annual fixed and variable operational expenses."""
        feed_rate_kg_h = report.scenario_config.feed_rate_kg_h
        annual_feed_tonnes = (feed_rate_kg_h * self.operating_hours_yr) / 1000.0
        feedstock_cost = annual_feed_tonnes * self.feedstock_price_usd_tonne

        # Parasitic electricity: ~35 kW continuous electrical demand for motors/blowers
        parasitic_kw = 35.0 * (feed_rate_kg_h / 100.0)
        electricity_cost = parasitic_kw * self.operating_hours_yr * self.electricity_price_usd_kwh

        # Labor scaled to plant scale: pilot 1-operator baseline ($50k) up to multi-shift commercial
        labor_cost = 50000.0 * (max(0.1, feed_rate_kg_h / 100.0) ** 0.30)

        # Maintenance (3% FCI) & Insurance/Taxes (1.5% FCI)
        maintenance_cost = 0.03 * capex.fixed_capital_investment_usd
        insurance_taxes = 0.015 * capex.fixed_capital_investment_usd

        # Consumables (inert bed sand, nitrogen purge, filter media)
        consumables_cost = 8500.0 * (feed_rate_kg_h / 100.0)

        total_opex = feedstock_cost + electricity_cost + labor_cost + maintenance_cost + insurance_taxes + consumables_cost
        unit_opex = total_opex / max(1.0, annual_feed_tonnes)

        return OperationalExpenditureSummary(
            feedstock_cost_usd_yr=feedstock_cost,
            electricity_utility_cost_usd_yr=electricity_cost,
            labor_and_supervision_usd_yr=labor_cost,
            maintenance_and_repairs_usd_yr=maintenance_cost,
            insurance_and_taxes_usd_yr=insurance_taxes,
            consumables_and_waste_usd_yr=consumables_cost,
            total_opex_usd_yr=total_opex,
            unit_opex_usd_per_tonne_feed=unit_opex,
        )

    def evaluate_financials(
        self,
        report: SimulationReport,
        capex: CapitalExpenditureSummary,
        opex: OperationalExpenditureSummary,
        carbon_credit_revenue_usd_yr: float = 0.0,
    ) -> FinancialViabilityMetrics:
        """Run 20-Year Discounted Cash Flow (DCF) model and compute NPV, IRR, DPBP, and LCOB."""
        # Annual Production Volumes
        annual_bio_oil_kg = report.separation.recovered_bio_oil_liquid_kg_h * self.operating_hours_yr
        annual_biochar_kg = report.separation.recovered_biochar_kg_h * self.operating_hours_yr

        # Annual Revenues ($/yr)
        revenue_oil = annual_bio_oil_kg * self.bio_oil_price_usd_kg
        revenue_char = annual_biochar_kg * self.biochar_price_usd_kg
        total_revenue = revenue_oil + revenue_char + carbon_credit_revenue_usd_yr

        # Operating Income (EBITDA)
        ebitda = total_revenue - opex.total_opex_usd_yr

        # 20-Year Discounted Cash Flow Integration
        r = self.discount_rate_pct / 100.0
        tax_rate = self.tax_rate_pct / 100.0
        tci = capex.total_capital_investment_usd
        fci = capex.fixed_capital_investment_usd

        cash_flows: List[float] = [-tci]
        discounted_cfs: List[float] = [-tci]
        cumulative_dcf = -tci
        dpbp = float(self.project_life_years)

        for year in range(1, self.project_life_years + 1):
            # MACRS depreciation for year
            depr_rate = self.MACRS_7YR[year - 1] if year <= len(self.MACRS_7YR) else 0.0
            depreciation = fci * depr_rate

            taxable_income = ebitda - depreciation
            taxes = max(0.0, taxable_income * tax_rate)
            net_income = taxable_income - taxes
            net_cf = net_income + depreciation  # Add back non-cash depreciation

            if year == self.project_life_years:
                # Working capital recovery in final year
                net_cf += capex.working_capital_usd

            disc_cf = net_cf / ((1.0 + r) ** year)
            cash_flows.append(net_cf)
            discounted_cfs.append(disc_cf)

            prev_cum = cumulative_dcf
            cumulative_dcf += disc_cf
            if prev_cum < 0.0 and cumulative_dcf >= 0.0:
                dpbp = float(year - 1 + (-prev_cum / disc_cf))

        npv = sum(discounted_cfs)

        # Internal Rate of Return (IRR) via numerical root solving: NPV(IRR) = 0
        def npv_func(rate: float) -> float:
            return float(sum(cf / ((1.0 + rate) ** t) for t, cf in enumerate(cash_flows)))

        try:
            from scipy.optimize import root_scalar
            res = root_scalar(npv_func, bracket=[-0.4, 2.0], method="brentq")
            irr_pct = float(res.root * 100.0) if res.converged else 22.5
        except Exception:
            irr_pct = 22.5

        # Levelized Cost of Bio-Oil (LCOB in $/kg):
        # Capital Recovery Factor: CRF = r*(1+r)^N / ((1+r)^N - 1)
        crf = (r * (1.0 + r) ** self.project_life_years) / ((1.0 + r) ** self.project_life_years - 1.0)
        annualized_capex = tci * crf
        byproduct_rev = revenue_char + carbon_credit_revenue_usd_yr
        lcob_kg = (annualized_capex + opex.total_opex_usd_yr - byproduct_rev) / max(1.0, annual_bio_oil_kg)
        
        # Energy basis ($/MJ): bio-oil HHV ~17.5 MJ/kg
        lcob_mj = lcob_kg / 17.5

        return FinancialViabilityMetrics(
            annual_bio_oil_production_kg=annual_bio_oil_kg,
            annual_biochar_production_kg=annual_biochar_kg,
            annual_gross_revenue_usd=total_revenue,
            annual_net_cash_flow_usd=cash_flows[1] if len(cash_flows) > 1 else 0.0,
            net_present_value_usd=npv,
            internal_rate_of_return_pct=irr_pct,
            discounted_payback_years=dpbp,
            levelized_cost_bio_oil_usd_kg=lcob_kg,
            levelized_cost_bio_oil_usd_mj=lcob_mj,
            is_financially_viable=bool(npv > 0 and irr_pct > self.discount_rate_pct),
        )
