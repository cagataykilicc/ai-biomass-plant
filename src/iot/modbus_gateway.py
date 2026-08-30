"""Industrial Modbus TCP Register Bank Gateway and Frame Serializer."""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class ModbusRegisterMap:
    """Represents a standard Modbus TCP register bank holding real-time plant state."""

    # Discrete Inputs (10001 - 10008, Read-Only Booleans)
    discrete_inputs: Dict[int, bool] = field(default_factory=lambda: {
        10001: True,   # DI_PLANT_RUNNING
        10002: False,  # DI_SIL2_INTERLOCK_TRIPPED
        10003: False,  # DI_PULSE_JET_ACTIVE
        10004: True,   # DI_FLAME_ESTABLISHED
        10005: True,   # DI_DRYER_MOTOR_OK
        10006: False,  # DI_AUGER_JAM_ALARM
        10007: False,  # DI_CYCLONE_CLOG_ALARM
        10008: True,   # DI_AUTONOMOUS_CRUISE_ACTIVE
    })

    # Coils (00001 - 00008, Read/Write Booleans)
    coils: Dict[int, bool] = field(default_factory=lambda: {
        1: False,      # COIL_PULSE_JET_MANUAL_TRIGGER
        2: False,      # COIL_EMERGENCY_SAFE_PARK_TRIGGER
        3: False,      # COIL_RESET_ALARMS
        4: True,       # COIL_ENABLE_AUTOPILOT
    })

    # Input Registers (30001 - 30010, Read-Only 16-bit Unsigned Integers)
    input_registers: Dict[int, int] = field(default_factory=lambda: {
        30001: 1050,   # TI_101_DRYER_TEMP_C (105.0 °C * 10)
        30002: 5000,   # TI_103_REACTOR_TEMP_C (500.0 °C * 10)
        30003: 125,    # PI_102_CYCLONE_DP_MBAR (12.5 mbar * 10)
        30004: 1013,   # PI_104_COMBUSTOR_PRESS_MBAR (101.3 kPa * 10)
        30005: 1000,   # FT_101_BIOMASS_INFEED_KG_H (100.0 kg/h * 10)
        30006: 150,    # FI_102_N2_CARRIER_L_MIN (15.0 L/min * 10)
        30007: 1145,   # TSI_SELF_SUFFICIENCY_PCT (114.5 % * 10)
        30008: 72,     # RUL_MINIMUM_ASSET_DAYS (72 days)
        30009: 34,     # ANOMALY_SCORE_SPE_Q (0.34 * 100)
        30010: 58,     # ANOMALY_SCORE_T2 (0.58 * 100)
    })

    # Holding Registers (40001 - 40008, Read/Write 16-bit Unsigned Integers)
    holding_registers: Dict[int, int] = field(default_factory=lambda: {
        40001: 5000,   # HR_SETPOINT_TEMP_C (500.0 °C * 10)
        40002: 1000,   # HR_SETPOINT_FEED_RATE_KG_H (100.0 kg/h * 10)
        40003: 450,    # HR_BURNER_DUTY_PCT (45.0 % * 10)
        40004: 400,    # HR_PULSE_JET_DURATION_SEC (40.0 s * 10)
        40005: 150,    # HR_CARRIER_FLOW_SETPOINT_L_MIN (15.0 L/min * 10)
    })


class ModbusTCPGateway:
    """High-level Modbus TCP Gateway mapping plant state into industrial register tables."""

    def __init__(self, unit_id: int = 1):
        self.unit_id = unit_id
        self.registers = ModbusRegisterMap()

    def update_from_telemetry(self, telemetry: Dict[str, Any], fsm_state: str = "AUTONOMOUS_CRUISE") -> None:
        """Update Modbus register bank values from real-time digital twin telemetry."""
        # Update Input Registers
        temp_c = float(telemetry.get("reactor_temp_c", 500.0))
        self.registers.input_registers[30002] = int(round(max(0.0, temp_c) * 10))

        feed_kg_h = float(telemetry.get("feed_rate_kg_h", 100.0))
        self.registers.input_registers[30005] = int(round(max(0.0, feed_kg_h) * 10))

        tsi_pct = float(telemetry.get("tsi_pct", telemetry.get("thermal_self_sufficiency_index_pct", 100.0)))
        self.registers.input_registers[30007] = int(round(max(0.0, tsi_pct) * 10))

        rul_days = int(telemetry.get("rul_days", telemetry.get("minimum_rul_days", 60)))
        self.registers.input_registers[30008] = max(0, min(65535, rul_days))

        # Update Discrete Inputs
        self.registers.discrete_inputs[10001] = fsm_state not in ("EMERGENCY_SAFE_PARK", "OFFLINE")
        self.registers.discrete_inputs[10002] = fsm_state == "EMERGENCY_SAFE_PARK"
        self.registers.discrete_inputs[10003] = bool(telemetry.get("pulse_jet_active", False))
        self.registers.discrete_inputs[10007] = bool(telemetry.get("cyclone_clog", False))
        self.registers.discrete_inputs[10008] = fsm_state == "AUTONOMOUS_CRUISE"

    def read_holding_register(self, address: int) -> int:
        """Read a single holding register (40001-40005)."""
        if address not in self.registers.holding_registers:
            raise KeyError(f"Invalid Holding Register address {address}. Valid range: 40001-40005.")
        return self.registers.holding_registers[address]

    def write_holding_register(self, address: int, value: int) -> None:
        """Write a value to a holding register with 16-bit bounds validation."""
        if address not in self.registers.holding_registers:
            raise KeyError(f"Invalid Holding Register address {address}. Valid range: 40001-40005.")
        if not (0 <= value <= 65535):
            raise ValueError(f"Value {value} out of 16-bit range [0, 65535].")
        self.registers.holding_registers[address] = value

    def read_coil(self, address: int) -> bool:
        """Read a single coil (1-4)."""
        if address not in self.registers.coils:
            raise KeyError(f"Invalid Coil address {address}. Valid range: 1-4.")
        return self.registers.coils[address]

    def write_coil(self, address: int, value: bool) -> None:
        """Write a coil boolean state."""
        if address not in self.registers.coils:
            raise KeyError(f"Invalid Coil address {address}. Valid range: 1-4.")
        self.registers.coils[address] = bool(value)

    def export_register_table(self) -> Dict[str, Any]:
        """Export all register tables in structured JSON format for web UI / SCADA clients."""
        return {
            "unit_id": self.unit_id,
            "discrete_inputs_10000": {
                f"{k}": {"value": v, "name": self._get_di_name(k)}
                for k, v in self.registers.discrete_inputs.items()
            },
            "coils_00000": {
                f"{k:05d}": {"value": v, "name": self._get_coil_name(k)}
                for k, v in self.registers.coils.items()
            },
            "input_registers_30000": {
                f"{k}": {"raw": v, "scaled": v / 10.0 if k not in (30008,) else v, "unit": self._get_ir_unit(k), "name": self._get_ir_name(k)}
                for k, v in self.registers.input_registers.items()
            },
            "holding_registers_40000": {
                f"{k}": {"raw": v, "scaled": v / 10.0, "unit": self._get_hr_unit(k), "name": self._get_hr_name(k)}
                for k, v in self.registers.holding_registers.items()
            },
        }

    @staticmethod
    def _get_di_name(address: int) -> str:
        names = {
            10001: "DI_PLANT_RUNNING",
            10002: "DI_SIL2_INTERLOCK_TRIPPED",
            10003: "DI_PULSE_JET_ACTIVE",
            10004: "DI_FLAME_ESTABLISHED",
            10005: "DI_DRYER_MOTOR_OK",
            10006: "DI_AUGER_JAM_ALARM",
            10007: "DI_CYCLONE_CLOG_ALARM",
            10008: "DI_AUTONOMOUS_CRUISE_ACTIVE",
        }
        return names.get(address, "UNKNOWN_DI")

    @staticmethod
    def _get_coil_name(address: int) -> str:
        names = {
            1: "COIL_PULSE_JET_MANUAL_TRIGGER",
            2: "COIL_EMERGENCY_SAFE_PARK_TRIGGER",
            3: "COIL_RESET_ALARMS",
            4: "COIL_ENABLE_AUTOPILOT",
        }
        return names.get(address, "UNKNOWN_COIL")

    @staticmethod
    def _get_ir_name(address: int) -> str:
        names = {
            30001: "TI-101 Dryer Outlet Temp",
            30002: "TI-103 Reactor Core Temp",
            30003: "PI-102 Cyclone Diff Pressure",
            30004: "PI-104 Combustor Chamber Pressure",
            30005: "FT-101 Biomass Feed Rate",
            30006: "FI-102 N2 Sweep Flow",
            30007: "TSI Energy Self-Sufficiency",
            30008: "RUL Plant Minimum Asset RUL",
            30009: "SPE Q Residual Anomaly Score",
            30010: "Hotelling T2 Anomaly Score",
        }
        return names.get(address, "UNKNOWN_IR")

    @staticmethod
    def _get_ir_unit(address: int) -> str:
        units = {
            30001: "°C", 30002: "°C", 30003: "mbar", 30004: "kPa",
            30005: "kg/h", 30006: "L/min", 30007: "%", 30008: "days",
            30009: "score", 30010: "score"
        }
        return units.get(address, "")

    @staticmethod
    def _get_hr_name(address: int) -> str:
        names = {
            40001: "SP_Reactor_Temperature",
            40002: "SP_Feed_Rate",
            40003: "SP_Burner_Firing_Duty",
            40004: "SP_Pulse_Jet_Duration",
            40005: "SP_N2_Carrier_Flow",
        }
        return names.get(address, "UNKNOWN_HR")

    @staticmethod
    def _get_hr_unit(address: int) -> str:
        units = {40001: "°C", 40002: "kg/h", 40003: "%", 40004: "s", 40005: "L/min"}
        return units.get(address, "")
