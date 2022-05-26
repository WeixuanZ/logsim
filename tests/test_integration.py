"""Test parser and scanner modules jointly."""
import pytest
from parse import Parser
from devices import Devices
from scanner import Scanner
from network import Network
from names import Names
from monitors import Monitors


@pytest.fixture()
def file_content():
    """Content of the test file."""
    return (
        "DEVICES: \n"
        "SW1, SW2 = SWITCH < 0 > ; \n"
        "A = AND < 2 > ; \n"
        "CONNECTIONS: \n"
        "SW1 - A.I1 ; \n"
        "A.I2 - SW2 ; \n"
        "MONITORS:"
        "A ;"
    )


@pytest.fixture()
def input_file(tmp_path, file_content):
    """Create a test file in a temporary directory."""
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test.txt"
    p.write_text(file_content)
    return p


@pytest.fixture()
def names():
    """Create an instance of names class."""
    return Names()


@pytest.fixture()
def scanner(input_file, names):
    """Create a scanner instance with the test file."""
    return Scanner(input_file, names)


@pytest.fixture()
def parser(names, scanner):
    """Create a parser instance."""
    devices = Devices(names)
    network = Network(names, devices)
    monitors = Monitors(names, devices, network)
    return Parser(names, devices, network, monitors, scanner)


def test_parse_definition_file(parser):
    """Test if parser successfully parses file"""
    outcome = parser.parse_network()
    assert outcome is True
    device_list = parser.devices.devices_list
    assert len(device_list) == 3
    assert device_list[0].device_kind == parser.devices.SWITCH
    assert device_list[1].device_kind == parser.devices.SWITCH
    assert device_list[2].device_kind == parser.devices.AND

    # check connections
    dev_id = device_list[2].device_id
    input_ids = list(device_list[2].inputs.keys())
    in1 = input_ids[0]
    in2 = input_ids[1]
    # print(parser.network.get_connected_output(dev_id, in1))
    # print(parser.network.get_connected_output(dev_id, in2))
    (id, out) = parser.network.get_connected_output(dev_id, in1)
    assert id == device_list[0].device_id
    assert out is None
    (id, out) = parser.network.get_connected_output(dev_id, in2)
    assert id == device_list[1].device_id
    assert out is None

    # check monitors

    monitor_dict = parser.monitors.monitors_dictionary
    assert len(monitor_dict) == 1
    (device_id, pin_id) = list(monitor_dict.keys())[0]
    assert device_id == parser.names.query("A")
    assert pin_id is None
