"""Hardware-in-the-Loop (HIL) 4-20mA Current Loop & ADC/DAC Instrumentation Simulator."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class AnalogLoopChannel:
    """Represents an industrial 4-20mA instrumentation current loop channel."""
    tag: str
    name: str
    eng_min: float
    eng_max: float
    eng_unit: str
    current_pv: float = 0.0
    current_ma: float = 4.0
    voltage_0_10v: float = 0.0
    adc_12bit_counts: int = 0
    fault_loop_open: bool = False
    fault_loop_short: bool = False

    def update_engineering_value(self, value: float, add_noise: bool = True) -> None:
        """Convert physical engineering value to industrial 4.0 - 20.0 mA loop current and 12-bit ADC counts."""
        self.current_pv = max(self.eng_min, min(self.eng_max, value))

        if self.fault_loop_open:
            self.current_ma = 0.0  # NAMUR NE 43 loop failure (< 3.6 mA)
            self.voltage_0_10v = 0.0
            self.adc_12bit_counts = 0
            return

        if self.fault_loop_short:
            self.current_ma = 24.0  # NAMUR NE 43 loop short (> 21.0 mA)
            self.voltage_0_10v = 10.0
            self.adc_12bit_counts = 4095
            return

        span = self.eng_max - self.eng_min
        fraction = (self.current_pv - self.eng_min) / span if span > 0 else 0.0

        # Base 4-20mA current with optional analog instrumentation noise (±0.02 mA)
        noise = random.gauss(0.0, 0.015) if add_noise else 0.0
        ma = 4.0 + (fraction * 16.0) + noise
        self.current_ma = max(3.8, min(20.5, ma))

        # Precision 250-ohm shunt resistor: V = I * R (4mA*250 = 1.0V, 20mA*250 = 5.0V; or 0-10V scaled)
        self.voltage_0_10v = (self.current_ma / 20.0) * 10.0

        # 12-bit ADC quantization (0 - 4095 counts across 0-10V)
        self.adc_12bit_counts = int(round((self.voltage_0_10v / 10.0) * 4095))
        self.adc_12bit_counts = max(0, min(4095, self.adc_12bit_counts))


class HILHardwareSimulator:
    """Simulates physical Hardware-in-the-Loop (HIL) signal conditioning and GPIO relay actuation."""

    def __init__(self):
        self.channels: Dict[str, AnalogLoopChannel] = {
            "AI_0": AnalogLoopChannel("TI-101", "Dryer Outlet Temperature", 0.0, 300.0, "°C", 105.0),
            "AI_1": AnalogLoopChannel("TI-103", "Reactor Core Temperature", 0.0, 1000.0, "°C", 500.0),
            "AI_2": AnalogLoopChannel("PI-102", "Cyclone Differential Pressure", 0.0, 50.0, "mbar", 12.5),
            "AI_3": AnalogLoopChannel("FT-101", "Biomass Feed Rate Transmitter", 0.0, 500.0, "kg/h", 100.0),
            "AI_4": AnalogLoopChannel("TSI-100", "Thermal Energy Self Sufficiency", 0.0, 250.0, "%", 114.5),
        }
        self.gpio_pins: Dict[str, bool] = {
            "GPIO_21_PULSE_JET_SOLENOID": False,
            "GPIO_22_BURNER_IGNITER": True,
            "GPIO_23_AUGER_MOTOR_ENABLE": True,
            "GPIO_24_EMERGENCY_VENT_VALVE": False,
        }
        self.hardware_clock_ticks = 0

    def step_hardware_signals(self, telemetry: Dict[str, Any], pulse_jet_command: bool = False) -> Dict[str, Any]:
        """Update HIL analog current loops and digital GPIO states from twin telemetry."""
        self.hardware_clock_ticks += 1

        # 1. Update Analog Inputs
        if "dryer_temp_c" in telemetry:
            self.channels["AI_0"].update_engineering_value(float(telemetry["dryer_temp_c"]))
        if "reactor_temp_c" in telemetry:
            self.channels["AI_1"].update_engineering_value(float(telemetry["reactor_temp_c"]))
        if "cyclone_dp_mbar" in telemetry:
            self.channels["AI_2"].update_engineering_value(float(telemetry["cyclone_dp_mbar"]))
        if "feed_rate_kg_h" in telemetry:
            self.channels["AI_3"].update_engineering_value(float(telemetry["feed_rate_kg_h"]))
        if "tsi_pct" in telemetry:
            self.channels["AI_4"].update_engineering_value(float(telemetry["tsi_pct"]))

        # 2. Update GPIO Relays
        self.gpio_pins["GPIO_21_PULSE_JET_SOLENOID"] = bool(pulse_jet_command)
        self.gpio_pins["GPIO_24_EMERGENCY_VENT_VALVE"] = telemetry.get("fsm_state") == "EMERGENCY_SAFE_PARK"

        return self.export_hil_state()

    def inject_hardware_fault(self, channel_key: str, fault_type: str) -> None:
        """Inject physical circuit fault (loop_open or loop_short)."""
        if channel_key not in self.channels:
            raise KeyError(f"Invalid analog channel '{channel_key}'.")
        ch = self.channels[channel_key]
        if fault_type == "loop_open":
            ch.fault_loop_open = True
            ch.fault_loop_short = False
        elif fault_type == "loop_short":
            ch.fault_loop_short = True
            ch.fault_loop_open = False
        elif fault_type == "clear":
            ch.fault_loop_open = False
            ch.fault_loop_short = False
        else:
            raise ValueError(f"Unknown fault type '{fault_type}'. Options: loop_open, loop_short, clear.")
        ch.update_engineering_value(ch.current_pv, add_noise=False)

    def export_hil_state(self) -> Dict[str, Any]:
        """Export HIL state summary for web UI inspection."""
        return {
            "clock_ticks": self.hardware_clock_ticks,
            "sampling_rate_hz": 50.0,
            "analog_channels": {
                k: {
                    "tag": ch.tag,
                    "name": ch.name,
                    "pv": round(ch.current_pv, 2),
                    "eng_unit": ch.eng_unit,
                    "current_ma": round(ch.current_ma, 3),
                    "voltage_v": round(ch.voltage_0_10v, 3),
                    "adc_12bit": ch.adc_12bit_counts,
                    "namur_ne43_status": "NORMAL" if 3.8 <= ch.current_ma <= 20.5 else ("FAULT_OPEN" if ch.current_ma < 3.8 else "FAULT_SHORT"),
                }
                for k, ch in self.channels.items()
            },
            "gpio_pins": self.gpio_pins,
        }
