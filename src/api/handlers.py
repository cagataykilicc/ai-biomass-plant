"""REST API business logic and route handlers for Digital Twin simulation, optimization, diagnostics, and maintenance."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, Optional

from src.simulation.plant_simulator import BiomassPlantSimulator
from src.utils.config import ConfigManager
from src.data.preprocessing import FeedstockLibrary
from src.sensors.telemetry import TelemetryExtractor
from src.sensors.soft_sensor_engine import SoftSensorSuite
from src.sensors.calibration import SoftSensorCalibrator
from src.optimization.objectives import OptimizationObjective
from src.optimization.problem import OptimizationProblem, DecisionBounds
from src.optimization.optimizer import PlantProcessOptimizer
from src.optimization.pareto import ParetoOptimizer, ParetoFrontier
from src.diagnostics.fault_simulator import IndustrialFaultType, FaultInjectionConfig, ProcessFaultSimulator
from src.diagnostics.run_diagnostics import load_or_train_models
from src.diagnostics.alarm_manager import AlarmManager
from src.maintenance.rul_estimator import RULEstimator
from src.maintenance.work_order_manager import WorkOrderManager
from src.optimization.decision_maker import TOPSISDecisionMaker


def _parse_bounded_float(
    data: Dict[str, Any],
    key: str,
    default: float,
    min_val: float,
    max_val: float,
) -> float:
    """Parse and validate numeric input bounds, rejecting negative or out-of-range values."""
    raw = data.get(key, default)
    if raw is None:
        raw = default
    try:
        val = float(raw)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid numeric value for parameter '{key}': {raw}")

    if val < min_val or val > max_val:
        raise ValueError(
            f"Parameter '{key}' value {val} is outside allowed range [{min_val}, {max_val}]."
        )
    return val


class APIRequestHandler:
    """Dispatches and processes REST API calls for the digital twin platform."""

    _simulator = BiomassPlantSimulator()
    _detector = None
    _classifier = None
    _soft_sensor_suite = None

    @classmethod
    def _get_soft_sensors(cls) -> SoftSensorSuite:
        if cls._soft_sensor_suite is None:
            root = Path(__file__).resolve().parent.parent.parent
            chk = root / "models" / "checkpoints" / "soft_sensors.joblib"
            if not chk.is_file():
                SoftSensorCalibrator().calibrate()
            cls._soft_sensor_suite = SoftSensorSuite.load(chk)
        return cls._soft_sensor_suite

    @classmethod
    def _get_diag_models(cls):
        if cls._detector is None or cls._classifier is None:
            det, clf = load_or_train_models()
            cls._detector = det
            cls._classifier = clf
        return cls._detector, cls._classifier

    @classmethod
    def handle_status(cls) -> Dict[str, Any]:
        """System status and module availability."""
        return {
            "status": "ONLINE",
            "version": "2.1.0",
            "modules": {
                "thermodynamic_flowsheet": "ACTIVE",
                "ml_yield_surrogate": "ACTIVE",
                "multiobjective_optimizer": "ACTIVE",
                "inferential_soft_sensors": "ACTIVE",
                "fault_anomaly_diagnostics": "ACTIVE",
                "predictive_maintenance_rul": "ACTIVE",
                "dynamic_process_control_mpc": "ACTIVE",
                "techno_economic_lca_carbon": "ACTIVE",
                "autonomous_autopilot_agent": "ACTIVE",
            },
            "available_feedstocks": ["pine_sawdust", "olive_pomace", "wheat_straw", "rice_husk"],
        }

    @classmethod
    def handle_feedstocks(cls) -> Dict[str, Any]:
        """Available feedstock fingerprints and proximate/ultimate properties."""
        feedstocks = {}
        lib = FeedstockLibrary()
        for name in ["pine_sawdust", "olive_pomace", "wheat_straw", "rice_husk"]:
            fs = lib.load_feedstock(name)
            feedstocks[name] = {
                "name": fs.name,
                "category": fs.category,
                "moisture_pct": fs.proximate.moisture,
                "volatile_matter_dry_pct": fs.proximate.volatile_matter,
                "fixed_carbon_dry_pct": fs.proximate.fixed_carbon,
                "ash_dry_pct": fs.proximate.ash,
                "carbon_dry_pct": fs.ultimate.carbon,
                "hydrogen_dry_pct": fs.ultimate.hydrogen,
                "oxygen_dry_pct": fs.ultimate.oxygen,
                "nitrogen_dry_pct": fs.ultimate.nitrogen,
                "sulfur_dry_pct": fs.ultimate.sulfur,
                "hhv_dry_mj_kg": round(fs.calculate_hhv_dry(), 2),
                "lhv_dry_mj_kg": round(fs.calculate_lhv_dry(), 2),
            }
        return {"feedstocks": feedstocks}

    @classmethod
    def handle_simulate(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run digital twin flowsheet simulation with input bounds validation."""
        fs_name = data.get("feedstock", "pine_sawdust")
        feed_rate = _parse_bounded_float(data, "feed_rate_kg_h", 100.0, 0.1, 100000.0)
        temp = _parse_bounded_float(data, "reactor_temp_c", 500.0, 100.0, 1500.0)
        moisture = _parse_bounded_float(data, "moisture_pct", 12.0, 0.0, 80.0)
        heating_rate = _parse_bounded_float(data, "heating_rate_c_min", 10.0, 0.1, 500.0)
        residence_time = _parse_bounded_float(data, "residence_time_min", 20.0, 0.1, 600.0)
        yield_mode = data.get("yield_mode", "deterministic")

        report = cls._simulator.run_simulation(
            feedstock_name=fs_name,
            feed_rate_kg_h=feed_rate,
            moisture_pct=moisture,
            reactor_temp_c=temp,
            heating_rate_c_min=heating_rate,
            residence_time_min=residence_time,
            yield_mode="ML_SURROGATE" if yield_mode.lower() == "ml" else "DETERMINISTIC",
        )

        return {
            "feedstock": report.feedstock.name,
            "operating_conditions": {
                "feed_rate_kg_h": feed_rate,
                "reactor_temp_c": temp,
                "moisture_pct": moisture,
                "heating_rate_c_min": heating_rate,
                "residence_time_min": residence_time,
            },
            "yields_dry": {
                "biochar_yield_pct": round(report.reactor.yields_dry.biochar_yield * 100, 2),
                "bio_oil_yield_pct": round(report.reactor.yields_dry.bio_oil_yield * 100, 2),
                "syngas_yield_pct": round(report.reactor.yields_dry.syngas_yield * 100, 2),
            },
            "product_rates_kg_h": {
                "bio_oil": round(report.separation.recovered_bio_oil_liquid_kg_h, 2),
                "biochar": round(report.separation.recovered_biochar_kg_h, 2),
                "syngas": round(report.separation.clean_syngas_kg_h, 2),
                "dryer_water": round(report.drying.water_evaporated_kg_h, 2),
            },
            "energy_and_heat": {
                "gross_thermal_demand_kw": round(report.energy_balance.gross_thermal_demand_kw, 2),
                "syngas_heat_released_kw": round(report.combustion.thermal_heat_released_kw, 2),
                "heat_recovered_kw": round(report.combustion.thermal_heat_recovered_kw, 2),
                "tsi_pct": round(report.combustion.thermal_self_sufficiency_index_pct, 1),
                "is_self_sufficient": report.combustion.is_thermally_self_sufficient,
                "net_surplus_kw": round(report.combustion.surplus_heat_available_kw, 2),
            },
            "closures": {
                "mass_closure_pct": round(report.mass_balance.closure_pct, 2),
                "carbon_closure_pct": round(report.elemental_balance.closures["C"].closure_pct, 2),
            },
        }

    @classmethod
    def handle_soft_sensors(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Infer unmeasured stream states from telemetry."""
        fs_name = data.get("feedstock", "pine_sawdust")
        feed_rate = _parse_bounded_float(data, "feed_rate_kg_h", 100.0, 0.1, 100000.0)
        temp = _parse_bounded_float(data, "reactor_temp_c", 500.0, 100.0, 1500.0)

        report = cls._simulator.run_simulation(
            feedstock_name=fs_name,
            feed_rate_kg_h=feed_rate,
            reactor_temp_c=temp,
        )
        telemetry = TelemetryExtractor.extract_from_report(report, add_sensor_noise=True)
        suite = cls._get_soft_sensors()
        estimates = suite.estimate_all(telemetry)

        return {
            "telemetry": telemetry.to_dict(),
            "soft_sensors": {k: v.to_dict() for k, v in estimates.items()},
        }

    @classmethod
    def handle_optimize(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Solve process optimization."""
        fs_name = data.get("feedstock", "pine_sawdust")
        mode = data.get("mode", "pareto")

        if mode == "pareto":
            opt = ParetoOptimizer(feedstock_name=fs_name)
            frontier = opt.generate_pareto_frontier(n_candidates=30)
            ranked = TOPSISDecisionMaker.rank_solutions(frontier, profile_name="balanced_sustainability")
            top_sol = ranked[0] if ranked else None
            non_dom = frontier.get_non_dominated_solutions()
            return {
                "frontier_size": len(non_dom),
                "frontier": [s.to_dict() for s in non_dom],
                "top_solution": top_sol,
                "topsis_score": top_sol["closeness_score"] if top_sol else None,
            }
        else:
            obj_map = {
                "max_bio_oil": OptimizationObjective.MAX_BIO_OIL_YIELD,
                "max_biochar": OptimizationObjective.MAX_BIOCHAR_CARBON,
                "max_profit": OptimizationObjective.MAX_ECONOMIC_MARGIN,
                "max_efficiency": OptimizationObjective.MAX_THERMAL_EFFICIENCY,
            }
            target_obj = obj_map.get(mode.lower(), OptimizationObjective.MAX_BIO_OIL_YIELD)
            problem = OptimizationProblem(feedstock_name=fs_name, objective=target_obj, yield_mode="ML_SURROGATE")
            opt = PlantProcessOptimizer(problem=problem)
            res = opt.optimize(solver="differential_evolution")
            return {
                "objective": mode,
                "optimal_setpoints": res.optimal_setpoints,
                "optimal_objective_value": round(res.optimal_objective_value, 2),
                "success": res.success,
                "tsi_pct": round(res.key_kpis.get("thermal_self_sufficiency_index_pct", 100.0), 1),
            }

    @classmethod
    def handle_diagnostics(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate fault mode and run tri-layer anomaly detector."""
        f_str = data.get("fault_type", "cyclone_blockage")
        sev = _parse_bounded_float(data, "severity", 0.85, 0.0, 1.0)

        f_map = {
            "none": IndustrialFaultType.NONE,
            "cyclone_blockage": IndustrialFaultType.CYCLONE_DIPLEG_BLOCKAGE,
            "condenser_fouling": IndustrialFaultType.CONDENSER_TAR_FOULING,
            "thermal_runaway": IndustrialFaultType.REACTOR_THERMAL_RUNAWAY,
            "sensor_drift": IndustrialFaultType.THERMOCOUPLE_SENSOR_DRIFT,
            "feed_jam": IndustrialFaultType.FEED_AUGER_JAMMING,
        }
        fault_type = f_map.get(f_str.lower(), IndustrialFaultType.NONE)
        fault_cfg = FaultInjectionConfig(fault_type=fault_type, severity=sev)

        sim = ProcessFaultSimulator()
        report, telemetry = sim.run_faulted_simulation(fault_cfg)

        detector, classifier = cls._get_diag_models()
        anomaly_res = detector.detect(telemetry, report)
        diag_res = classifier.diagnose(telemetry, anomaly_res)
        alarm = AlarmManager.evaluate_alarm(anomaly_res, diag_res)

        return {
            "fault_injected": fault_type.value,
            "severity": sev,
            "telemetry": telemetry.to_dict(),
            "anomaly_detection": anomaly_res.to_dict(),
            "fault_diagnosis": diag_res.to_dict(),
            "alarm": alarm.to_dict(),
        }

    @classmethod
    def handle_maintenance(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate fleet RUL prognostics and work orders."""
        hours = _parse_bounded_float(data, "operating_hours", 4500.0, 0.0, 500000.0)
        feed_rate = _parse_bounded_float(data, "feed_rate_kg_h", 100.0, 0.1, 100000.0)
        temp = _parse_bounded_float(data, "reactor_temp_c", 500.0, 100.0, 1500.0)

        fleet = RULEstimator.assess_fleet(
            operating_hours=hours,
            feed_rate_kg_h=feed_rate,
            reactor_temp_c=temp,
        )
        work_orders = WorkOrderManager.generate_work_orders(fleet)

        return {
            "fleet_summary": fleet.to_dict(),
            "work_orders": [wo.to_dict() for wo in work_orders],
        }

    @classmethod
    def handle_control(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute dynamic closed-loop response simulation (PID / MPC / Open-Loop)."""
        from src.control.benchmark_control import ControlBenchmarkSuite
        ctrl_type = data.get("controller", "mpc")
        setpoint = _parse_bounded_float(data, "setpoint", 520.0, 100.0, 1500.0)
        moist_disturb = _parse_bounded_float(data, "moisture_disturb", 20.0, 0.0, 80.0)

        suite = ControlBenchmarkSuite(simulation_duration_sec=3600.0, dt_sec=4.0)
        states, metrics = suite.run_simulation(
            controller_type=ctrl_type,
            setpoint_step_c=setpoint,
            moisture_disturb_pct=moist_disturb,
        )

        # Subsample states for efficient JSON transmission (every 2nd point)
        sub_states = [s.to_dict() for s in states[::2]]

        return {
            "controller": ctrl_type.upper(),
            "metrics": metrics.to_dict(),
            "trajectory_points": len(sub_states),
            "trajectory": sub_states,
        }

    @classmethod
    def handle_economics(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Techno-Economic Analysis and LCA carbon accounting."""
        from src.economics.run_economics import evaluate_plant_economics_and_lca
        fs_name = data.get("feedstock", "olive_pomace")
        feed_rate = _parse_bounded_float(data, "feed_rate_kg_h", 100.0, 0.1, 100000.0)
        temp = _parse_bounded_float(data, "reactor_temp_c", 500.0, 100.0, 1500.0)
        oil_price = _parse_bounded_float(data, "oil_price", 0.65, 0.0, 1000.0)
        char_price = _parse_bounded_float(data, "char_price", 0.45, 0.0, 1000.0)
        corc_price = _parse_bounded_float(data, "corc_price", 65.0, 0.0, 5000.0)

        return evaluate_plant_economics_and_lca(
            feedstock_name=fs_name,
            feed_rate_kg_h=feed_rate,
            reactor_temp_c=temp,
            bio_oil_price_usd_kg=oil_price,
            biochar_price_usd_kg=char_price,
            corc_price_usd_tonne=corc_price,
        )

    _autopilot_agent = None

    @classmethod
    def _get_autopilot(cls):
        from src.autonomous.autopilot import AutonomousSupervisoryAgent
        if cls._autopilot_agent is None:
            cls._autopilot_agent = AutonomousSupervisoryAgent(dt_sec=2.0)
        return cls._autopilot_agent

    @classmethod
    def handle_autopilot_step(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Advance autonomous autopilot by one decision step."""
        agent = cls._get_autopilot()
        moist = _parse_bounded_float(data, "moisture", 12.0, 0.0, 80.0)
        fault = data.get("fault", "none")
        sp = _parse_bounded_float(data, "setpoint", 500.0, 100.0, 1500.0)
        reset_agent = data.get("reset", False)

        if reset_agent:
            agent.reset()

        state, cmd = agent.step(
            mission_phase="WEB_AUTONOMOUS_OPERATION",
            moisture_override=moist,
            injected_fault=fault,
            target_temp_override=sp,
        )

        return {
            "plant_state": state.to_dict(),
            "command": cmd.to_dict(),
            "active_events": agent.flight_recorder.events[-5:],
        }

    @classmethod
    def handle_autopilot_mission(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute full autonomous stress test mission."""
        from src.autonomous.stress_test import AutonomousStressTestRunner
        dt = _parse_bounded_float(data, "dt", 2.0, 0.1, 60.0)
        runner = AutonomousStressTestRunner(dt_sec=dt)
        return runner.run_4hour_mission()
