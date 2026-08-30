"""Automated unit and integration tests for Bilingual (Turkish & English) Internationalization."""

from pathlib import Path
import json
import pytest
from src.copilot.agent import SCADAOperatorCopilot
from src.copilot.knowledge_base import CopilotKnowledgeBase
from src.api.handlers import APIRequestHandler


def test_i18n_javascript_dictionary_parity() -> None:
    """Verify that i18n.js exists and has complete translation dictionaries for both EN and TR."""
    i18n_path = Path(__file__).resolve().parent.parent / "src" / "web" / "static" / "i18n.js"
    assert i18n_path.exists(), "i18n.js file is missing"

    content = i18n_path.read_text(encoding="utf-8")
    assert "en: {" in content
    assert "tr: {" in content

    # Check key navigation translations
    assert '"nav.flowsheet": "Control Room"' in content
    assert '"nav.flowsheet": "Kontrol Odası"' in content
    assert '"nav.spatial": "3D Spatial & Copilot"' in content
    assert '"nav.spatial": "3B Mekansal İkiz & Copilot"' in content


def test_copilot_turkish_query_processing() -> None:
    """Verify SCADA Copilot detects Turkish language and returns Turkish technical guidance."""
    copilot = SCADAOperatorCopilot()

    # 1. Cyclone Blockage in Turkish
    res_cyclone = copilot.process_query(
        "Siklon basınç farkı neden yükseliyor ve nasıl çözülür?",
        plant_state={"cyclone_dp_mbar": 28.5, "fsm_state": "DISTURBANCE_ADAPTATION"},
    )
    assert res_cyclone["language"] == "tr"
    assert "Siklon Basınç Farkı" in res_cyclone["copilot_response"]
    assert "SOP-204" in str(res_cyclone["matched_engineering_documents"])
    assert res_cyclone["recommended_action"] == "EXECUTE_PULSE_JET_BLOWBACK"

    # 2. Moisture Surge in Turkish
    res_moist = copilot.process_query(
        "Hammadde nem oranı aniden yükseldi, brülörü nasıl ayarlamalıyım?",
        plant_state={"moisture_pct": 21.0, "fsm_state": "AUTONOMOUS_CRUISE"},
    )
    assert res_moist["language"] == "tr"
    assert "Nem Dalgalanması" in res_moist["copilot_response"]
    assert res_moist["recommended_action"] == "INCREASE_BURNER_DUTY"

    # 3. Emergency Safe Park in Turkish
    res_emergency = copilot.process_query("SIL-2 acil güvenli duruş prosedürünü başlat")
    assert res_emergency["language"] == "tr"
    assert "SIL-2 Acil Güvenli Park" in res_emergency["copilot_response"]
    assert res_emergency["recommended_action"] == "TRIGGER_EMERGENCY_SAFE_PARK"

    # 4. Startup Preheat in Turkish
    res_startup = copilot.process_query("Reaktör ön ısıtma ve başlatma adımları nelerdir?")
    assert res_startup["language"] == "tr"
    assert "Reaktör Termal Başlatma" in res_startup["copilot_response"]
    assert res_startup["recommended_action"] == "INITIATE_PREHEAT_RAMP"

    # 5. General Supervisory State in Turkish
    res_general = copilot.process_query("Tesisin genel çalışma durumu nedir?")
    assert res_general["language"] == "tr"
    assert "SCADA Denetim Özeti" in res_general["copilot_response"]
    assert res_general["recommended_action"] == "MAINTAIN_AUTONOMOUS_CRUISE"


def test_api_copilot_turkish_integration() -> None:
    """Verify REST API handle_copilot_chat handles Turkish queries."""
    res = APIRequestHandler.handle_copilot_chat({
        "query": "Siklon DP 28 mbar oldu, ne yapmalı?",
        "plant_state": {"cyclone_dp_mbar": 28.0},
    })
    assert res["language"] == "tr"
    assert "Siklon" in res["copilot_response"]
    assert res["recommended_action"] == "EXECUTE_PULSE_JET_BLOWBACK"


def test_user_manual_language_synchronization() -> None:
    """Verify manual.html integrates with localStorage bioplant_lang."""
    manual_path = Path(__file__).resolve().parent.parent / "src" / "web" / "static" / "manual.html"
    assert manual_path.exists(), "manual.html is missing"

    content = manual_path.read_text(encoding="utf-8")
    assert "localStorage.setItem('bioplant_lang', lang)" in content
    assert "localStorage.getItem('bioplant_lang')" in content
    assert "id=\"content-tr\"" in content
    assert "id=\"content-en\"" in content

