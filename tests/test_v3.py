"""Automated unit and integration tests for V3.0 Deep RL Non-Linear Gym, 3D Spatial Twin, and GenAI SCADA Copilot."""

import pytest
from src.drl.bioplant_env import BioPlantEnv
from src.drl.ppo_agent import PPOAgent, PolicyNetwork
from src.spatial.model_3d import PlantSpatialModel
from src.copilot.knowledge_base import CopilotKnowledgeBase
from src.copilot.agent import SCADAOperatorCopilot
from src.api.handlers import APIRequestHandler


def test_drl_bioplant_gym_environment() -> None:
    """Verify Gymnasium BioPlantEnv reset, step dynamics, and reward computations."""
    env = BioPlantEnv(target_temp_c=500.0, nominal_feed_kg_h=100.0, max_steps=50)
    obs, info = env.reset(seed=123)

    assert len(obs) == 8
    assert 470.0 <= info["reactor_temp_c"] <= 490.0
    assert info["target_temp_c"] == 500.0

    # Step with positive burner duty action [+5.0, 0.0, 0.0]
    next_obs, reward, terminated, truncated, step_info = env.step([5.0, 0.0, 0.0])
    assert len(next_obs) == 8
    assert step_info["step"] == 1
    assert step_info["burner_duty_pct"] == 50.0  # 45 + 5
    assert not terminated
    assert not truncated
    assert isinstance(reward, float)


def test_drl_ppo_agent_policy_and_training() -> None:
    """Verify PPO Actor-Critic network inference, action shapes, and episode rollouts."""
    agent = PPOAgent(obs_dim=8, act_dim=3)
    dummy_obs = [0.1, 0.0, 0.4, 0.3, 0.7, 0.5, 0.45, 0.0]

    action, value = agent.select_action(dummy_obs, explore=False)
    assert len(action) == 3
    assert -10.0 <= action[0] <= 10.0  # Burner duty delta
    assert -15.0 <= action[1] <= 15.0  # Feed rate delta
    assert 0.0 <= action[2] <= 1.0     # Pulse jet probability
    assert isinstance(value, float)

    # Test training rollout episode
    env = BioPlantEnv(max_steps=20)
    metrics = agent.train_episode(env, max_steps=20)
    assert metrics["steps_completed"] > 0
    assert "total_episode_reward" in metrics
    assert "mean_temperature_error_c" in metrics
    assert "convergence_status" in metrics


def test_plant_spatial_3d_model() -> None:
    """Verify 3D Spatial Digital Twin component hierarchy and conduit graph."""
    spatial = PlantSpatialModel()
    graph = spatial.export_spatial_graph()

    assert "nodes" in graph
    assert "conduits" in graph
    assert len(graph["nodes"]) >= 6  # Hopper, Reactor, Burner, Cyclone, Biochar Silo, Condenser
    assert len(graph["conduits"]) >= 5

    reactor_node = next(n for n in graph["nodes"] if n["id"] == "REACTOR_R101")
    assert reactor_node["category"] == "VESSEL"
    assert reactor_node["position"] == [0.0, 2.6, 0.0]


def test_copilot_knowledge_base_and_reasoning_agent() -> None:
    """Verify SCADA Copilot SOP retrieval and telemetry-informed diagnostic responses."""
    kb = CopilotKnowledgeBase()
    docs = kb.query("cyclone pressure drop blockage")
    assert len(docs) > 0
    assert any(d.doc_id == "SOP-204" for d in docs)

    copilot = SCADAOperatorCopilot(kb)

    # 1. Query Cyclone Blockage
    res_cyclone = copilot.process_query(
        "Cyclone DP is spiking to 28 mbar. What should I do?",
        plant_state={"cyclone_dp_mbar": 28.5, "fsm_state": "DISTURBANCE_ADAPTATION"}
    )
    assert "XV-105" in res_cyclone["copilot_response"]
    assert res_cyclone["recommended_action"] == "EXECUTE_PULSE_JET_BLOWBACK"

    # 2. Query Moisture Surge
    res_moist = copilot.process_query(
        "Biomass infeed moisture jumped to 20%. How to adjust?",
        plant_state={"moisture_pct": 20.0, "fsm_state": "AUTONOMOUS_CRUISE"}
    )
    assert "burner duty" in res_moist["copilot_response"].lower()
    assert res_moist["recommended_action"] == "INCREASE_BURNER_DUTY"

    # 3. Query Emergency Safe Park
    res_emergency = copilot.process_query("Initiate emergency SIL-2 trip")
    assert res_emergency["recommended_action"] == "TRIGGER_EMERGENCY_SAFE_PARK"


def test_api_v3_handlers() -> None:
    """Verify REST API handlers for DRL step/training, Spatial 3D model, and Copilot chat."""
    # 1. DRL Step
    drl_step = APIRequestHandler.handle_drl_step({"override_action": [2.0, -1.0, 0.0]})
    assert "action_executed" in drl_step
    assert "environment_state" in drl_step

    # 2. DRL Train Episode
    train_res = APIRequestHandler.handle_drl_train_episode({"max_steps": 15})
    assert "total_episode_reward" in train_res

    # 3. Spatial Model
    spatial_res = APIRequestHandler.handle_spatial_model()
    assert "nodes" in spatial_res
    assert "conduits" in spatial_res

    # 4. Copilot Chat
    chat_res = APIRequestHandler.handle_copilot_chat({"query": "What is the status of reactor TI-103?"})
    assert "copilot_response" in chat_res
    assert "recommended_action" in chat_res
