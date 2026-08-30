"""Automated unit and integration tests for SCADA Operator Copilot and Web UI Documentation."""

from pathlib import Path
import pytest
from src.copilot.agent import SCADAOperatorCopilot
from src.copilot.knowledge_base import CopilotKnowledgeBase
from src.api.handlers import APIRequestHandler


def test_copilot_english_query_processing() -> None:
    """Verify SCADA Copilot returns accurate English technical guidance and recommended actions."""
    copilot = SCADAOperatorCopilot()

    # 1. Cyclone Blockage Query
    res_cyclone = copilot.process_query(
        "Cyclone DP is spiking to 28 mbar. What is the SOP?",
        plant_state={"cyclone_dp_mbar": 28.5, "fsm_state": "DISTURBANCE_ADAPTATION"},
    )
    assert "Cyclone DP Analysis" in res_cyclone["copilot_response"]
    assert "SOP-204" in str(res_cyclone["matched_engineering_documents"])
    assert res_cyclone["recommended_action"] == "EXECUTE_PULSE_JET_BLOWBACK"

    # 2. Moisture Surge Query
    res_moist = copilot.process_query(
        "Feedstock moisture increased to 20%. Adjust burner setpoints.",
        plant_state={"moisture_pct": 21.0, "fsm_state": "AUTONOMOUS_CRUISE"},
    )
    assert "Feedstock Moisture Advisory" in res_moist["copilot_response"]
    assert res_moist["recommended_action"] == "INCREASE_BURNER_DUTY"

    # 3. Emergency Safe Park Query
    res_emergency = copilot.process_query("Initiate SIL-2 emergency safe park trip.")
    assert "SIL-2 Safety Shutdown Procedure" in res_emergency["copilot_response"]
    assert res_emergency["recommended_action"] == "TRIGGER_EMERGENCY_SAFE_PARK"

    # 4. Startup Preheat Query
    res_startup = copilot.process_query("Give me the thermal preheat and startup procedure.")
    assert "Reactor Thermal Startup Guidance" in res_startup["copilot_response"]
    assert res_startup["recommended_action"] == "INITIATE_PREHEAT_RAMP"

    # 5. General Supervisory State Query
    res_general = copilot.process_query("What is the general plant operating state?")
    assert "SCADA Supervisory Overview" in res_general["copilot_response"]
    assert res_general["recommended_action"] == "MAINTAIN_AUTONOMOUS_CRUISE"


def test_api_copilot_chat_integration() -> None:
    """Verify REST API handle_copilot_chat handles queries and returns suggested setpoints."""
    res = APIRequestHandler.handle_copilot_chat({
        "query": "Cyclone DP is 28 mbar, what should I do?",
        "plant_state": {"cyclone_dp_mbar": 28.0},
    })
    assert "copilot_response" in res
    assert "Cyclone DP Analysis" in res["copilot_response"]
    assert res["recommended_action"] == "EXECUTE_PULSE_JET_BLOWBACK"
    assert "suggested_setpoints" in res
    assert res["suggested_setpoints"]["pulse_count"] == 3


def test_user_manual_english_documentation() -> None:
    """Verify manual.html exists and contains comprehensive English technical documentation."""
    manual_path = Path(__file__).resolve().parent.parent / "src" / "web" / "static" / "manual.html"
    assert manual_path.exists(), "manual.html is missing"

    content = manual_path.read_text(encoding="utf-8")
    assert "BIOPLANT AI Digital Twin & Autopilot" in content
    assert "1. System Overview" in content
    assert "2. Quick Start" in content
    assert "3. 8 Core Modules" in content
    assert "4. Autonomous Autopilot" in content
    assert "5. REST API" in content
    assert "6. Feedstocks" in content
    assert "7. Safety & LOTO" in content
    assert "8. Troubleshooting & FAQ" in content
    assert "← Back to Live Dashboard" in content
    assert "id=\"manual-theme-toggle\"" in content


def test_seo_geo_metadata_and_theme_support() -> None:
    """Verify SEO meta tags, GEO coordinates, sitemap, robots.txt, and theme toggling."""
    static_dir = Path(__file__).resolve().parent.parent / "src" / "web" / "static"
    index_path = static_dir / "index.html"
    robots_path = static_dir / "robots.txt"
    sitemap_path = static_dir / "sitemap.xml"

    assert robots_path.exists(), "robots.txt is missing"
    robots_content = robots_path.read_text(encoding="utf-8")
    assert "Sitemap:" in robots_content

    assert sitemap_path.exists(), "sitemap.xml is missing"
    sitemap_content = sitemap_path.read_text(encoding="utf-8")
    assert "<loc>http://127.0.0.1:8000/</loc>" in sitemap_content

    assert index_path.exists(), "index.html is missing"
    index_content = index_path.read_text(encoding="utf-8")

    # SEO verification
    assert '<meta name="description"' in index_content
    assert '<meta name="keywords"' in index_content
    assert '<meta name="author" content="Çağatay Kılıç">' in index_content
    assert '<link rel="canonical"' in index_content
    assert '<meta property="og:title"' in index_content
    assert '<meta name="twitter:card"' in index_content
    assert '"@type": "SoftwareApplication"' in index_content

    # GEO verification
    assert '<meta name="geo.region" content="TR-34">' in index_content
    assert '<meta name="geo.placename" content="Istanbul, Turkey">' in index_content
    assert '<meta name="geo.position"' in index_content
    assert '<meta name="ICBM"' in index_content

    # Theme toggle verification
    assert 'data-theme="dark"' in index_content
    assert 'id="theme-toggle-btn"' in index_content
    assert 'id="theme-icon-sun"' in index_content
    assert 'id="theme-icon-moon"' in index_content




