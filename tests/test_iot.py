"""Automated unit and integration tests for Industrial IoT, Modbus TCP, MQTT Sparkplug B, OPC-UA, and HIL."""

import pytest
from src.iot.modbus_gateway import ModbusTCPGateway, ModbusRegisterMap
from src.iot.mqtt_bridge import MQTTOperationalBridge, SparkplugBPayload
from src.iot.opcua_bridge import OPCUAAddressSpace, OPCUANode
from src.iot.hil_simulator import HILHardwareSimulator, AnalogLoopChannel
from src.api.handlers import APIRequestHandler


def test_modbus_gateway_registers_and_scaling() -> None:
    """Verify Modbus TCP register bank reads, writes, and engineering unit scaling."""
    gateway = ModbusTCPGateway(unit_id=1)

    # 1. Update from live telemetry
    telemetry = {
        "reactor_temp_c": 525.4,
        "feed_rate_kg_h": 120.0,
        "tsi_pct": 118.2,
        "rul_days": 85,
        "pulse_jet_active": True,
    }
    gateway.update_from_telemetry(telemetry, fsm_state="AUTONOMOUS_CRUISE")

    assert gateway.registers.input_registers[30002] == 5254  # 525.4 * 10
    assert gateway.registers.input_registers[30005] == 1200  # 120.0 * 10
    assert gateway.registers.input_registers[30007] == 1182  # 118.2 * 10
    assert gateway.registers.input_registers[30008] == 85
    assert gateway.registers.discrete_inputs[10003] is True  # Pulse Jet Active
    assert gateway.registers.discrete_inputs[10008] is True  # Cruise Active

    # 2. Test holding register write and validation
    gateway.write_holding_register(40001, 5500)
    assert gateway.read_holding_register(40001) == 5500

    with pytest.raises(ValueError):
        gateway.write_holding_register(40001, 70000)  # > 65535

    # 3. Test coil write
    gateway.write_coil(1, True)
    assert gateway.read_coil(1) is True

    # 4. Test export format
    table = gateway.export_register_table()
    assert "input_registers_30000" in table
    assert "holding_registers_40000" in table
    assert table["input_registers_30000"]["30002"]["scaled"] == 525.4


def test_mqtt_sparkplug_b_bridge() -> None:
    """Verify MQTT Sparkplug B topic formatting, payload encoding, and command handling."""
    bridge = MQTTOperationalBridge(group_id="BiomassPlant", edge_node_id="Node_01", device_id="Reactor_01")

    # 1. Topic namespace check
    assert bridge.get_topic("DBIRTH") == "spBv1.0/BiomassPlant/DBIRTH/Node_01/Reactor_01"
    assert bridge.get_topic("DDATA") == "spBv1.0/BiomassPlant/DDATA/Node_01/Reactor_01"

    # 2. Build DBIRTH
    telemetry = {"reactor_temp_c": 500.0, "feed_rate_kg_h": 100.0, "tsi_pct": 110.0}
    birth = bridge.build_dbirth_payload(telemetry)
    assert birth["qos"] == 1
    assert birth["retain"] is True
    assert len(birth["payload"]["metrics"]) >= 5
    assert birth["payload"]["seq"] == 0

    # 3. Build DDATA sequence increments
    ddata1 = bridge.build_ddata_payload(telemetry)
    assert ddata1["payload"]["seq"] == 1
    ddata2 = bridge.build_ddata_payload(telemetry)
    assert ddata2["payload"]["seq"] == 2

    # 4. Handle NCMD
    cmd_res = bridge.handle_ncmd({"metrics": [{"name": "Setpoints/TargetTemp", "value": 520.0}]})
    assert cmd_res["status"] == "COMMANDS_ACKNOWLEDGED"


def test_opcua_address_space() -> None:
    """Verify OPC-UA IEC 62541 node tree structure and telemetry synchronization."""
    space = OPCUAAddressSpace()
    assert len(space.nodes) >= 12

    # 1. Read standard nodes
    temp_node = space.get_node("ns=2;s=BioPlant.ProcessData.ReactorTemp")
    assert temp_node is not None
    assert temp_node.node_class == "Variable"
    assert temp_node.engineering_unit == "°C"

    # 2. Write variable
    space.write_variable("ns=2;s=BioPlant.Setpoints.TemperatureTarget", 540.0)
    assert space.get_node("ns=2;s=BioPlant.Setpoints.TemperatureTarget").value == 540.0

    # 3. Update from telemetry
    space.update_from_telemetry({"reactor_temp_c": 515.0, "feed_rate_kg_h": 95.0})
    assert space.get_node("ns=2;s=BioPlant.ProcessData.ReactorTemp").value == 515.0
    assert space.get_node("ns=2;s=BioPlant.ProcessData.BiomassFeedRate").value == 95.0

    # 4. Export tree
    tree = space.export_address_space_tree()
    assert "nodes" in tree
    assert "server_uri" in tree


def test_hil_simulator_4_20ma_and_adc() -> None:
    """Verify HIL analog 4-20mA current loop mathematics, 12-bit ADC scaling, and circuit fault injection."""
    hil = HILHardwareSimulator()

    # 1. Step nominal values
    telemetry = {
        "dryer_temp_c": 150.0,    # 50% of 0-300°C -> ~12.0 mA
        "reactor_temp_c": 500.0,  # 50% of 0-1000°C -> ~12.0 mA
        "cyclone_dp_mbar": 25.0,  # 50% of 0-50 mbar -> ~12.0 mA
        "feed_rate_kg_h": 250.0,  # 50% of 0-500 kg/h -> ~12.0 mA
        "tsi_pct": 125.0,         # 50% of 0-250% -> ~12.0 mA
    }
    state = hil.step_hardware_signals(telemetry, pulse_jet_command=True)

    assert state["clock_ticks"] == 1
    assert state["gpio_pins"]["GPIO_21_PULSE_JET_SOLENOID"] is True

    # Check 4-20mA analog channels (around 12 mA ± noise)
    ch_reactor = state["analog_channels"]["AI_1"]
    assert 11.5 <= ch_reactor["current_ma"] <= 12.5
    assert 2000 <= ch_reactor["adc_12bit"] <= 2600
    assert ch_reactor["namur_ne43_status"] == "NORMAL"

    # 2. Inject NAMUR NE 43 Loop Open circuit fault (< 3.6 mA)
    hil.inject_hardware_fault("AI_1", "loop_open")
    fault_state = hil.export_hil_state()
    assert fault_state["analog_channels"]["AI_1"]["current_ma"] == 0.0
    assert fault_state["analog_channels"]["AI_1"]["namur_ne43_status"] == "FAULT_OPEN"

    # 3. Clear fault
    hil.inject_hardware_fault("AI_1", "clear")
    cleared_state = hil.export_hil_state()
    assert cleared_state["analog_channels"]["AI_1"]["namur_ne43_status"] == "NORMAL"


def test_api_iot_handlers() -> None:
    """Verify REST API handlers for IoT status, Modbus read/write, MQTT publish, and HIL step."""
    # 1. IoT Status
    status = APIRequestHandler.handle_iot_status()
    assert status["status"] == "ONLINE"
    assert "modbus_tcp" in status["protocols"]
    assert "mqtt_sparkplug_b" in status["protocols"]
    assert "opc_ua" in status["protocols"]
    assert "hil_simulator" in status["protocols"]

    # 2. Modbus Read & Write
    read_res = APIRequestHandler.handle_modbus_read()
    assert "input_registers_30000" in read_res

    write_res = APIRequestHandler.handle_modbus_write({
        "register_type": "holding_register",
        "address": 40001,
        "value": 5200,
    })
    assert write_res["status"] == "SUCCESS"
    assert write_res["scaled_value"] == 520.0

    # 3. MQTT Publish
    mqtt_res = APIRequestHandler.handle_mqtt_publish({
        "message_type": "DDATA",
        "telemetry": {"reactor_temp_c": 500.0},
    })
    assert "topic" in mqtt_res
    assert "payload" in mqtt_res

    # 4. HIL Step
    hil_res = APIRequestHandler.handle_hil_step({
        "telemetry": {"reactor_temp_c": 510.0},
        "pulse_jet_command": False,
    })
    assert "analog_channels" in hil_res
    assert "gpio_pins" in hil_res
