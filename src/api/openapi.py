"""OpenAPI 3.0.3 specification generator and interactive Swagger UI / ReDoc documentation renderers."""

from __future__ import annotations

import json
from typing import Dict, Any


def get_openapi_spec() -> Dict[str, Any]:
    """Generate complete OpenAPI 3.0.3 schema specification for BIOPLANT AI REST API."""
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "BIOPLANT AI — Digital Twin & Autonomous Platform REST API",
            "description": (
                "Industrial REST API for real-time thermochemical biomass conversion simulation, "
                "physics-constrained ML surrogates, Bayesian soft sensors (95% UQ), multi-objective "
                "Pareto optimization, tri-layer fault diagnostics, 20-year DCF techno-economics, "
                "ISO 14040/14044 LCA carbon accounting, and 5-State Autonomous Autopilot supervision."
            ),
            "version": "2.5.0",
            "contact": {
                "name": "Çağatay Kılıç",
                "url": "https://github.com/cagataykilicc/ai-biomass-plant",
            },
            "license": {
                "name": "MIT License",
                "url": "https://opensource.org/licenses/MIT",
            },
        },
        "servers": [
            {
                "url": "/",
                "description": "Active Digital Twin Server Instance",
            }
        ],
        "security": [
            {"ApiKeyAuth": []}
        ],
        "components": {
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "API key authentication token (configured via BIOPLANT_API_KEY environment variable).",
                }
            },
            "schemas": {
                "ErrorResponse": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Parameter 'feed_rate_kg_h' value -50.0 is outside allowed range [0.1, 100000.0]."},
                        "endpoint": {"type": "string", "example": "/api/simulate"},
                    },
                    "required": ["error"],
                },
                "StatusResponse": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "ONLINE"},
                        "version": {"type": "string", "example": "2.1.0"},
                        "modules": {
                            "type": "object",
                            "additionalProperties": {"type": "string"},
                            "example": {
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
                        },
                        "available_feedstocks": {
                            "type": "array",
                            "items": {"type": "string"},
                            "example": ["pine_sawdust", "olive_pomace", "wheat_straw", "rice_husk"],
                        },
                    },
                    "required": ["status", "version", "modules", "available_feedstocks"],
                },
                "SimulateRequest": {
                    "type": "object",
                    "properties": {
                        "feedstock": {
                            "type": "string",
                            "enum": ["pine_sawdust", "olive_pomace", "wheat_straw", "rice_husk"],
                            "default": "pine_sawdust",
                            "description": "Biomass feedstock identifier",
                        },
                        "feed_rate_kg_h": {
                            "type": "number",
                            "minimum": 0.1,
                            "maximum": 100000.0,
                            "default": 100.0,
                            "description": "Wet biomass infeed mass flow rate (kg/h)",
                        },
                        "reactor_temp_c": {
                            "type": "number",
                            "minimum": 100.0,
                            "maximum": 1500.0,
                            "default": 500.0,
                            "description": "Pyrolysis reactor operating temperature (°C)",
                        },
                        "moisture_pct": {
                            "type": "number",
                            "minimum": 0.0,
                            "maximum": 80.0,
                            "default": 12.0,
                            "description": "Feedstock raw moisture content (wt%)",
                        },
                        "heating_rate_c_min": {
                            "type": "number",
                            "minimum": 0.1,
                            "maximum": 500.0,
                            "default": 10.0,
                            "description": "Reactor thermal heating ramp rate (°C/min)",
                        },
                        "residence_time_min": {
                            "type": "number",
                            "minimum": 0.1,
                            "maximum": 600.0,
                            "default": 20.0,
                            "description": "Biomass vapor/solid residence time (min)",
                        },
                        "yield_mode": {
                            "type": "string",
                            "enum": ["deterministic", "ml"],
                            "default": "deterministic",
                            "description": "Prediction engine: First-principles stoichiometric or physics-constrained ML surrogate",
                        },
                    },
                },
                "EconomicsRequest": {
                    "type": "object",
                    "properties": {
                        "feedstock": {"type": "string", "default": "olive_pomace"},
                        "feed_rate_kg_h": {"type": "number", "minimum": 0.1, "maximum": 100000.0, "default": 100.0},
                        "reactor_temp_c": {"type": "number", "minimum": 100.0, "maximum": 1500.0, "default": 500.0},
                        "oil_price": {"type": "number", "minimum": 0.0, "maximum": 1000.0, "default": 0.65, "description": "Bio-oil market price ($/kg)"},
                        "char_price": {"type": "number", "minimum": 0.0, "maximum": 1000.0, "default": 0.45, "description": "Biochar agricultural price ($/kg)"},
                        "corc_price": {"type": "number", "minimum": 0.0, "maximum": 5000.0, "default": 65.0, "description": "Carbon Removal Certificate price ($/t CO2)"},
                    },
                },
                "AutopilotStepRequest": {
                    "type": "object",
                    "properties": {
                        "moisture": {"type": "number", "minimum": 0.0, "maximum": 80.0, "default": 12.0},
                        "fault": {"type": "string", "enum": ["none", "cyclone_blockage", "condenser_fouling", "thermal_runaway", "sensor_drift", "feed_jam"], "default": "none"},
                        "setpoint": {"type": "number", "minimum": 100.0, "maximum": 1500.0, "default": 500.0},
                        "reset": {"type": "boolean", "default": False},
                    },
                },
                "AutopilotMissionRequest": {
                    "type": "object",
                    "properties": {
                        "dt": {"type": "number", "minimum": 0.1, "maximum": 60.0, "default": 2.0, "description": "Simulation time step increment (seconds)"},
                    },
                },
            },
        },
        "paths": {
            "/api/status": {
                "get": {
                    "summary": "System Health & Module Status",
                    "description": "Returns operational health, system version 2.1.0, and active AI modules.",
                    "responses": {
                        "200": {
                            "description": "Digital twin is online and healthy",
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/StatusResponse"}}},
                        },
                        "401": {
                            "description": "Unauthorized - Missing or invalid X-API-Key header",
                            "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}},
                        },
                    },
                }
            },
            "/api/feedstocks": {
                "get": {
                    "summary": "Feedstock Chemical Catalog",
                    "description": "Returns proximate, ultimate, and heating values (HHV/LHV) for all calibrated biomass feedstocks.",
                    "responses": {
                        "200": {"description": "Feedstock catalog retrieved successfully"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/simulate": {
                "post": {
                    "summary": "Execute Process Flowsheet Simulation",
                    "description": "Executes digital twin unit operations (drying, pyrolysis, separation, combustion) with mass/energy closures.",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/SimulateRequest"}}},
                    },
                    "responses": {
                        "200": {"description": "Simulation completed with mass/energy balances and product yields"},
                        "400": {"description": "Invalid input parameter or value out of physical bounds"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/soft-sensors": {
                "post": {
                    "summary": "Infer Virtual Soft Sensors (95% UQ)",
                    "description": "Extracts hardware telemetry and evaluates 6 Bayesian Gaussian Process soft sensors with 95% Confidence Intervals.",
                    "responses": {
                        "200": {"description": "Soft sensor point estimates and uncertainty bounds"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/optimize": {
                "post": {
                    "summary": "Multi-Objective Pareto & Single-Objective Optimization",
                    "description": "Executes NSGA-II multiobjective Pareto frontier generation with TOPSIS stakeholder MCDM ranking.",
                    "responses": {
                        "200": {"description": "Pareto frontier solutions and champion TOPSIS setpoints"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/diagnostics": {
                "post": {
                    "summary": "Tri-Layer Anomaly Detection & SIL-2 Alarms",
                    "description": "Simulates equipment fault injection and runs physical residual checks, Isolation Forest, and PCA Hotelling's T2 / Q-statistics.",
                    "responses": {
                        "200": {"description": "Anomaly scores, fault classification, and safety interlock actions"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/maintenance": {
                "post": {
                    "summary": "Predictive Maintenance & Fleet RUL Prognostics",
                    "description": "Evaluates physics-informed asset degradation (Archard wear, refractory spalling) and dispatches prescriptive work orders.",
                    "responses": {
                        "200": {"description": "Remaining useful life (RUL) estimates and maintenance work orders"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/control": {
                "post": {
                    "summary": "Dynamic Process Control Benchmark (PID vs MPC)",
                    "description": "Executes 60-minute dynamic closed-loop response ODE simulation comparing Open-Loop, Discrete PID, and Model Predictive Control.",
                    "responses": {
                        "200": {"description": "Dynamic state trajectory and control performance KPIs"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/economics": {
                "post": {
                    "summary": "Techno-Economic Assessment (TEA) & ISO 14040/14044 LCA",
                    "description": "Computes Guthrie Total Capital Investment (TCI), 20-Year DCF viability (NPV, IRR, LCOB), and Net Carbon Negative LCA emissions.",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/EconomicsRequest"}}},
                    },
                    "responses": {
                        "200": {"description": "Full financial viability and life cycle assessment carbon accounting"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/autopilot/step": {
                "post": {
                    "summary": "Advance Autonomous Autopilot Step",
                    "description": "Advances closed-loop supervisory FSM decision loop by one discrete time step.",
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AutopilotStepRequest"}}},
                    },
                    "responses": {
                        "200": {"description": "Plant state, supervisory actuation command, and blackbox telemetry log"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/autopilot/mission": {
                "post": {
                    "summary": "Execute 4-Hour Autonomous Qualification Mission",
                    "description": "Simulates complete 240-minute autonomous stress test across all 6 operational flight phases.",
                    "requestBody": {
                        "required": False,
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AutopilotMissionRequest"}}},
                    },
                    "responses": {
                        "200": {"description": "4-Hour mission qualification results and event log"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/iot/status": {
                "get": {
                    "summary": "Industrial IoT Protocols Status",
                    "description": "Returns operational status of Modbus TCP, MQTT Sparkplug B, OPC-UA, and HIL Simulator bridges.",
                    "responses": {
                        "200": {"description": "IoT protocols state and statistics"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/iot/modbus/read": {
                "get": {
                    "summary": "Read Modbus TCP Register Bank",
                    "description": "Returns structured JSON of all Input Registers (30001+), Holding Registers (40001+), Discrete Inputs (10001+), and Coils (00001+).",
                    "responses": {
                        "200": {"description": "Modbus register map tables"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/iot/modbus/write": {
                "post": {
                    "summary": "Write Modbus Holding Register or Coil",
                    "description": "Writes 16-bit word to Holding Register or boolean state to Coil with industrial validation.",
                    "responses": {
                        "200": {"description": "Register write confirmed"},
                        "400": {"description": "Invalid register address or value out of bounds"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/iot/mqtt/publish": {
                "post": {
                    "summary": "Publish MQTT Sparkplug B Payload",
                    "description": "Generates and publishes Sparkplug B compliant DBIRTH, DDATA, or processes NCMD commands.",
                    "responses": {
                        "200": {"description": "Sparkplug B payload generated or command executed"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/iot/hil/step": {
                "post": {
                    "summary": "Execute Hardware-in-the-Loop Signal Conditioning Step",
                    "description": "Converts twin telemetry into 4-20mA current loops and 12-bit ADC quantization counts with fault injection.",
                    "responses": {
                        "200": {"description": "HIL analog channels and GPIO pin status"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/fleet/status": {
                "get": {
                    "summary": "Regional Multi-Plant Fleet Status & KPIs",
                    "description": "Returns operational status, utilization, OEE, daily throughput, bio-oil, and carbon sinks across all decentralized plant nodes.",
                    "responses": {
                        "200": {"description": "Fleet KPIs and plant node metrics"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/fleet/dispatch": {
                "post": {
                    "summary": "Dispatch Fleet Setpoints or Seasonal Harvest Optimization",
                    "description": "Allocates throughput setpoints across regional hubs based on seasonal agricultural biomass availability.",
                    "responses": {
                        "200": {"description": "Fleet dispatch schedule updated"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/fleet/corc-arbitrage": {
                "post": {
                    "summary": "Evaluate Dynamic CORC Carbon Credit Arbitrage",
                    "description": "Calculates revenue trade-offs across bio-oil and permanent carbon removal credits based on spot market prices.",
                    "responses": {
                        "200": {"description": "Optimal pyrolysis temperature and arbitrage revenue breakdown"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
            "/api/fleet/renewable-dispatch": {
                "post": {
                    "summary": "Compute Hybrid Solar PV & TOU Grid Energy Balance",
                    "description": "Optimizes 24-hour microgrid power dispatch, shifting drying and auxiliary electric loads to peak solar generation.",
                    "responses": {
                        "200": {"description": "24-Hour hourly power schedule and annual cost savings"},
                        "401": {"description": "Unauthorized"},
                    },
                }
            },
        },
    }


def get_swagger_ui_html() -> str:
    """Generate standalone interactive Swagger UI HTML page with dark theme styling."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BIOPLANT AI — OpenAPI Interactive Documentation (Swagger UI)</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <style>
    body {
      margin: 0;
      padding: 0;
      background-color: #0d1117;
      color: #c9d1d9;
      font-family: 'Inter', sans-serif;
    }
    .topbar-header {
      background: #161b22;
      border-bottom: 1px solid #30363d;
      padding: 12px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .topbar-title {
      font-size: 1.1rem;
      font-weight: 700;
      color: #58a6ff;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .topbar-links a {
      color: #8b949e;
      text-decoration: none;
      font-size: 0.9rem;
      margin-left: 16px;
      transition: color 0.2s;
    }
    .topbar-links a:hover {
      color: #58a6ff;
    }
    /* Swagger UI Dark Mode Adaptations */
    .swagger-ui {
      filter: invert(88%) hue-rotate(180deg);
    }
    .swagger-ui .topbar { display: none; }
  </style>
</head>
<body>
  <div class="topbar-header">
    <div class="topbar-title">
      🌿 BIOPLANT AI &mdash; REST API Reference (v2.1.0)
    </div>
    <div class="topbar-links">
      <a href="/">← Live Dashboard</a>
      <a href="/redoc">ReDoc View</a>
      <a href="/openapi.json" target="_blank">Raw JSON</a>
    </div>
  </div>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"></script>
  <script>
    window.onload = () => {
      window.ui = SwaggerUIBundle({
        url: '/openapi.json',
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout"
      });
    };
  </script>
</body>
</html>"""


def get_redoc_html() -> str:
    """Generate standalone interactive ReDoc HTML page."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>BIOPLANT AI &mdash; ReDoc API Documentation</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
  <style>
    body {
      margin: 0;
      padding: 0;
      background: #0d1117;
    }
  </style>
</head>
<body>
  <redoc spec-url="/openapi.json" theme='{"colors":{"primary":{"main":"#00f0ff"}},"typography":{"fontFamily":"Inter, sans-serif"}}'></redoc>
  <script src="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"></script>
</body>
</html>"""
