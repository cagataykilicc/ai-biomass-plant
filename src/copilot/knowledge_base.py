"""Plant Engineering Knowledge Base, SOP Manuals, P&ID Tag Index, and Fault Symptom Trees."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class EngineeringDocument:
    """Represents an engineering reference guide or standard operating procedure."""
    doc_id: str
    title: str
    category: str  # "SOP", "PID_TAG", "SAFETY_SIL2", "TROUBLESHOOTING"
    keywords: List[str]
    content: str


class CopilotKnowledgeBase:
    """Searchable technical library indexing plant operations documentation."""

    def __init__(self):
        self.documents: List[EngineeringDocument] = [
            EngineeringDocument(
                doc_id="SOP-101",
                title="Reactor Startup & Thermal Pre-Heating / Reaktör Başlatma ve Ön Isıtma",
                category="SOP",
                keywords=["startup", "preheat", "ignition", "nitrogen", "fluidization", "başlatma", "ön ısıtma", "ateşleme", "azot", "akışkanlaşma"],
                content=(
                    "1. Verify carrier N2 flow >= 15.0 Nm3/h.\n"
                    "2. Ignite auxiliary burner B-101 and ramp reactor temp TI-103 at <= 5.0 °C/min.\n"
                    "3. When TI-103 reaches 450.0 °C, engage biomass feeder FT-101 at 30% nominal (30 kg/h).\n"
                    "4. Transition FSM to AUTONOMOUS_CRUISE once bed reaches 500.0 °C and syngas self-sustains."
                ),
            ),
            EngineeringDocument(
                doc_id="SOP-204",
                title="Cyclone DP Spikes & Pulse-Jet Blowback Clearing / Siklon Basınç Farkı ve Geri Üfleme",
                category="TROUBLESHOOTING",
                keywords=["cyclone", "pressure drop", "dp", "blockage", "pulse jet", "clog", "siklon", "basınç", "fark", "tıkanma", "geri üfleme"],
                content=(
                    "1. If cyclone DP (PI-102) exceeds 25.0 mbar, trigger pulsed N2 blowback valve XV-105.\n"
                    "2. Apply 3 pulses (6.0 bar N2 reservoir, 1.5s duration, 8s interval).\n"
                    "3. Reduce infeed rate FT-101 by 20% until PI-102 settles below 15.0 mbar.\n"
                    "4. Verify biochar rotary airlock motor current is within 2.1 - 2.8 A."
                ),
            ),
            EngineeringDocument(
                doc_id="SOP-305",
                title="Moisture Surge Disturbance Compensation / Nem Dalgalanması ve Bozulma Dengeleme",
                category="TROUBLESHOOTING",
                keywords=["moisture", "water", "wet", "temperature drop", "cold feed", "feedstock", "nem", "ıslak", "su", "sıcaklık düşüşü", "hammadde"],
                content=(
                    "1. When feedstock moisture surges from 10% to > 18%, reactor temp TI-103 drops rapidly.\n"
                    "2. The AI Autopilot immediately ramps burner duty +15% and increases rotary dryer heat.\n"
                    "3. If moisture exceeds 22%, throttle feed rate -15 kg/h to maintain thermal self-sufficiency (TSI > 100%)."
                ),
            ),
            EngineeringDocument(
                doc_id="SOP-400",
                title="SIL-2 Emergency Safe Park Protocol / SIL-2 Acil Güvenli Duruş Protokolü",
                category="SAFETY_SIL2",
                keywords=["emergency", "safe park", "trip", "overtemp", "flame failure", "shutdown", "acil", "duruş", "güvenli park", "kapatma", "trip"],
                content=(
                    "1. Immediate emergency stop: Trip feed screw FT-101 and isolate burner fuel valve PY-101.\n"
                    "2. Flood reactor bed with high-volume N2 purge (35 Nm3/h) to inert flammable pyrolysis vapors.\n"
                    "3. Keep condenser coolant pumps running to quench remaining gas volume.\n"
                    "4. Maintain plant in SAFE_PARK state until operator manual SIL-2 reset is confirmed."
                ),
            ),
            EngineeringDocument(
                doc_id="TAG-INDEX",
                title="Process Instrumentation & P&ID Loop Directory / Enstrümantasyon Dizini",
                category="PID_TAG",
                keywords=["tags", "instrumentation", "ti-103", "pi-102", "ft-101", "py-101", "p&id", "etiketler", "sensörler"],
                content=(
                    "- TI-103: Fluidized Bed Thermocouple (0 - 800 °C, 4-20mA, SIL-2)\n"
                    "- PI-102: Cyclone Differential Pressure Transmitter (0 - 50 mbar, 4-20mA)\n"
                    "- FT-101: Loss-in-Weight Biomass Metering Feeder (0 - 250 kg/h, Modbus)\n"
                    "- PY-101: Burner Modulating Syngas/Propane Control Valve (0 - 100% duty)\n"
                    "- XV-105: Nitrogen Pulse-Jet Solenoid Actuator (24VDC Relay Coil 00001)"
                ),
            ),
        ]

    def query(self, text: str, top_k: int = 2) -> List[EngineeringDocument]:
        """Search knowledge base using keyword relevance scoring."""
        terms = [t.lower() for t in text.split() if len(t) > 2]
        scored_docs = []

        for doc in self.documents:
            score = 0
            doc_text = (doc.title + " " + " ".join(doc.keywords) + " " + doc.content).lower()
            for t in terms:
                if t in doc_text:
                    score += 1
                for kw in doc.keywords:
                    if t in kw or kw in t:
                        score += 2

            if score > 0:
                scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored_docs[:top_k]]
