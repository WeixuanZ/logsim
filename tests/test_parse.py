"""Test parser module"""
import pytest
from typing import Union
from parse import Parser
from scanner import Symbol
from names import Names
from custom_types import OperatorType, SyntaxErrors, SemanticErrors, DeviceType


class MockScanner:
    """Mock a scanner class."""

    def __init__(self, names: Names, names_list):
        self.names = names
        self.symbols = []

        for name in names_list:
            id = names.query(name)
            type = names.get_name_type(id)
            self.symbols.append(Symbol(type, id))
        pass

    def get_symbol(self):
        """reads and pops first name in the symbol list."""
        if len(self.symbols) == 0:
            return None
        value = self.symbols.pop(0)
        return value


def make_parser(statement):
    """Return parser"""

    names = Names()
    names.lookup(statement)
    scanner = MockScanner(names, statement)

    return Parser(names, None, None, None, scanner)


@pytest.mark.parametrize(
    "statement, error_type, description",
    [
        ([], SyntaxErrors.UnexpectedToken, None),
        ([], SyntaxErrors.NoDevices, "Missing DEVICES block"),
    ],
)
def test_throw_error(
    statement, error_type: Union[SyntaxErrors, SemanticErrors], description
):
    """Test module throw_error."""

    parser = make_parser(statement)
    assert parser.errors.error_counter == 0
    parser.throw_error(error_type, description)
    assert parser.errors.error_counter == 1
    assert (
        parser.errors.error_list[0].basic_message == error_type.basic_message
    )
    if description is not None:
        assert parser.errors.error_list[0].description


@pytest.mark.parametrize(
    "example_statement",
    [["0005", ";", "3"], ["sdgks"], []],
)
def test_get_next(example_statement):
    """Test get_next gets proper symbols and return False for end of file."""
    parser = make_parser(example_statement)
    success = True
    for i in range(len(example_statement)):
        assert success is True
        assert example_statement[i] == parser.names.get_name_string(
            parser.current_symbol.id
        )
        success = parser.get_next()

    if len(example_statement) == 0:
        success = parser.get_next()
    assert success is False
    assert parser.current_symbol is None


@pytest.mark.parametrize(
    "example_newline, num_of_semicolons",
    [(["AND", "or", ";", "Something"], 1), ([], 0), ([";"], 1), (["AND"], 0)],
)
def test_skip_to_end_of_line(example_newline, num_of_semicolons):
    """Test module skip_to_next_line."""
    parser = make_parser(example_newline)

    for i in range(num_of_semicolons):
        out = parser.skip_to_end_of_line()
        assert out is True
        assert parser.current_symbol.type == OperatorType.SEMICOLON

    parser.get_next()
    out = parser.skip_to_end_of_line()
    assert out is False
    assert parser.current_symbol is None


@pytest.mark.parametrize(
    "statement, keyword, success",
    [
        (
            ["AND", "<", "3", ">", ";", "CONNECTIONS", "kgds"],
            "CONNECTIONS",
            True,
        ),
        (["CONNECTIONS", "MONITORS"], "MONITORS", True),
        (["AND"], "MONITORS", False),
        ([], "MONITORS", False),
    ],
)
def test_skip_to_block(statement, keyword, success):
    """Test module skip_to_block."""
    parser = make_parser(statement)
    out = parser.skip_to_block(
        parser.names.get_name_type(parser.names.query(keyword))
    )
    assert out == success
    if success is True:
        assert parser.current_symbol.type == parser.names.get_name_type(
            parser.names.query(keyword)
        )


@pytest.mark.parametrize(
    "statement, type, parameter, success",
    [
        (["AND", ";"], DeviceType.AND, None, True),
        (["SWITCH", ";"], DeviceType.SWITCH, None, True),
        (["CLOCK", "<", "2", ">", ";"], DeviceType.CLOCK, 2, True),
        (["snaf"], None, None, False),
    ],
)
def test_parse_device_type(statement, type, parameter, success):
    """Test module parse_device_type."""
    parser = make_parser(statement)
    out, device = parser.parse_device_type()
    assert out == success
    if success:
        (dtype, param) = device
        assert dtype == type
        assert param == parameter


@pytest.mark.parametrize(
    "statement, error_type, description, success",
    [
        ([], SyntaxErrors.UnexpectedEOF, "Expected device type", None),
        (
            ["Swnass"],
            SyntaxErrors.UnexpectedToken,
            "Expected device type",
            False,
        ),
        (["SWITCH"], SyntaxErrors.UnexpectedEOF, "Expected '<' or ';'", None),
        (
            ["SWITCH", ">"],
            SyntaxErrors.UnexpectedToken,
            "Expected '<' or ';'",
            False,
        ),
        (
            ["DTYPE", "<"],
            SyntaxErrors.UnexpectedEOF,
            "Expected number parameter",
            None,
        ),
        (
            ["DTYPE", "<", "a"],
            SyntaxErrors.UnexpectedToken,
            "Expected number parameter",
            False,
        ),
        (
            ["AND", "<", "025"],
            SyntaxErrors.UnexpectedEOF,
            "Expected '>'",
            None,
        ),
        (
            ["AND", "<", "025", "A"],
            SyntaxErrors.UnexpectedToken,
            "Expected '>'",
            False,
        ),
    ],
)
def test_parse_device_type_errors(statement, error_type, description, success):
    """Test specific syntax errors arising in parse_device_type."""
    parser = make_parser(statement)
    out, _ = parser.parse_device_type()
    assert out == success
    assert parser.errors.error_counter == 1
    assert (
        parser.errors.error_list[0].basic_message == error_type.basic_message
    )
    assert parser.errors.error_list[0].description == description


@pytest.mark.parametrize(
    "statement, names, type, param, success",
    [
        (["Jeevan", "=", "AND", ";"], ["Jeevan"], DeviceType.AND, None, True),
        (
            ["Weixuan", "=", "OR", "<", "2", ">", ";"],
            ["Weixuan"],
            DeviceType.OR,
            2,
            True,
        ),
        (
            ["A", ",", "B", "=", "SWITCH", ";"],
            ["A", "B"],
            DeviceType.SWITCH,
            None,
            True,
        ),
        (
            ["A", ",", "B", ",", "C", "=", "SWITCH", ";"],
            ["A", "B", "C"],
            DeviceType.SWITCH,
            None,
            True,
        ),
        (["A", "=", ";"], None, None, None, False),
    ],
)
def test_parse_devices_statement(statement, names, type, param, success):
    """Test parse_devices_statement."""
    parser = make_parser(statement)
    out, device = parser.parse_devices_statement()
    assert out == success
    if success:
        (device_names, device_type, parameter) = device
        assert device_names == names
        assert device_type == type
        assert parameter == param


@pytest.mark.parametrize(
    "statement, error_type, description, success",
    [
        ([], SyntaxErrors.UnexpectedEOF, "Expected device definition", None),
        (["AND"], SyntaxErrors.UnexpectedToken, "Expected device name", False),
        (["A"], SyntaxErrors.UnexpectedEOF, "Expected ',' or '='", None),
        (
            ["A", ";"],
            SyntaxErrors.UnexpectedToken,
            "Expected ',' or '='",
            False,
        ),
        (
            ["A", ","],
            SyntaxErrors.UnexpectedEOF,
            "Expected device name",
            None,
        ),
        (
            ["A", ",", "B", ",", "C", "SWITCH", ";"],
            SyntaxErrors.UnexpectedToken,
            "Expected ',' or '='",
            False,
        ),
        (
            ["A", ",", "B", ",", "C", "=", "SWITCH", "<", "1", ">", "A"],
            SyntaxErrors.UnexpectedToken,
            "Expected ';'",
            False,
        ),
    ],
)
def test_parse_devices_statement_errors(
    statement, error_type, description, success
):
    """Test specific syntax errors arising in parse_devices_statement."""
    parser = make_parser(statement)
    out, _ = parser.parse_devices_statement()
    assert out == success
    assert parser.errors.error_counter == 1
    assert (
        parser.errors.error_list[0].basic_message == error_type.basic_message
    )
    assert parser.errors.error_list[0].description == description


@pytest.mark.parametrize(
    "statement, success",
    [
        (["DEVICES", ":", "A", "=", "AND", ";"], True),
        (
            ["DEVICES", ":", "A", ",", "B", "=", "XOR", "<", "0", ">", ";"],
            True,
        ),
        (["DEVICES", ":", "A", "=", "AND", ";" "B", "=", "SWITCH", ";"], True),
        (["DEVICES", ":", "CLOCK", "=", "AND"], None),
        ([], None),
        (["DEVICES", ":"], None),
    ],
)
def test_parse_device_block(statement, success):
    """Test module parse_device_block."""
    parser = make_parser(statement)
    out = parser.parse_device_block()
    assert out == success


@pytest.mark.parametrize(
    "statement, error_list",
    [
        ([], [(SyntaxErrors.UnexpectedEOF, "Missing DEVICES block")]),
        (["CONNEC"], [(SyntaxErrors.NoDevices, "Missing DEVICES block")]),
        (
            ["DEVICS", ":", "A", "=", "AND", ";"],
            [(SyntaxErrors.NoDevices, "Missing DEVICES block")],
        ),
        (
            ["DEVICES"],
            [(SyntaxErrors.UnexpectedEOF, "Expected ':' after DEVICES")],
        ),
        (
            ["DEVICES", ";"],
            [(SyntaxErrors.UnexpectedToken, "Expected ':' after DEVICES")],
        ),
        (
            ["DEVICES", ":"],
            [
                (SyntaxErrors.UnexpectedEOF, "Expected device definition"),
                (SyntaxErrors.NoDevices, "Empty DEVICES block"),
            ],
        ),
        (
            ["DEVICES", ":", "A", "=", "AD", ";", "B", "C", "=", "AND", ";"],
            [
                (SyntaxErrors.UnexpectedToken, "Expected device type"),
                (SyntaxErrors.UnexpectedToken, "Expected ',' or '='"),
            ],
        ),
    ],
)
def test_parse_device_block_errors(statement, error_list):
    """Test errors arising in parse_device_block."""
    parser = make_parser(statement)
    parser.parse_device_block()
    if len(error_list) > 0:
        assert parser.errors.error_counter == len(error_list)
        for i in range(len(error_list)):
            (type, des) = error_list[i]
            assert (
                parser.errors.error_list[i].basic_message == type.basic_message
            )
            assert parser.errors.error_list[i].description == des


@pytest.mark.parametrize(
    "statement, out, device_name, pin_name, success",
    [
        (["A", "-"], "out", "A", None, True),
        (["A", ".", "I1"], "in", "A", "I1", True),
        (["A", ".", "QBAR"], "out", "A", "QBAR", True),
        (["A", ".", "CLK"], "in", "A", "CLK", True),
        (["A", "I1"], None, None, None, False),
        (["A", "."], None, None, None, None),
    ],
)
def test_parse_pin(statement, out, device_name, pin_name, success):
    """Test module parse_pin."""
    parser = make_parser(statement)
    outcome, pin = parser.parse_pin()
    assert outcome == success
    if success:
        (o, d, p) = pin
        assert o == out
        assert device_name == d
        if pin_name is not None:
            assert p == pin_name


@pytest.mark.parametrize(
    "statement, error_type, description, success",
    [
        ([], SyntaxErrors.UnexpectedEOF, "Expected pin's device name", None),
        (
            ["AND"],
            SyntaxErrors.UnexpectedToken,
            "Expected pin's device name",
            False,
        ),
        (["A"], SyntaxErrors.UnexpectedEOF, "Expected '.', '-', or ';'", None),
        (
            ["A", "="],
            SyntaxErrors.UnexpectedToken,
            "Expected '.', '-', or ';'",
            False,
        ),
        (["A", "."], SyntaxErrors.UnexpectedEOF, "Expected pin name", None),
        (
            ["A", ".", ";"],
            SyntaxErrors.UnexpectedToken,
            "Expected pin name",
            False,
        ),
    ],
)
def test_parse_pin_errors(statement, error_type, description, success):
    """Test errors arising in parse_pin."""
    parser = make_parser(statement)
    out, pin = parser.parse_pin()
    if success is None or not success:
        assert out == success
        assert parser.errors.error_counter == 1
        assert (
            parser.errors.error_list[0].basic_message
            == error_type.basic_message
        )
        assert parser.errors.error_list[0].description == description


@pytest.mark.parametrize(
    "statement, success",
    [
        (["A", "-", "B", ";"], True),
        (["A", ".", "CLK", "-", "B", ";"], True),
        (["A", "-", "B", ".", "I3", ";"], True),
        (["A", ";"], False),
        (["A", "-", "B"], None),
    ],
)
def test_parse_connection_statement(statement, success):
    """Test module parse_connection_statement"""
    parser = make_parser(statement)
    outcome = parser.parse_connection_statement()
    assert outcome == success


@pytest.mark.parametrize(
    "statement, error_type, description, success",
    [
        (
            [],
            SyntaxErrors.UnexpectedEOF,
            "Expected connection statement",
            None,
        ),
        (["A", ".", "asa"], SyntaxErrors.UnexpectedEOF, "Expected '-'", None),
        (["A", ";"], SyntaxErrors.UnexpectedToken, "Expected '-'", False),
        (["A", "-", "B"], SyntaxErrors.MissingSemicolon, "", None),
        (
            ["A", "-", "B", ".", "Q", "A"],
            SyntaxErrors.UnexpectedToken,
            "Expected ';'",
            False,
        ),
    ],
)
def test_parse_connection_statement_errors(
    statement, error_type, description, success
):
    """Test errors arising in parse_connection_statement."""
    parser = make_parser(statement)
    outcome = parser.parse_connection_statement()
    if success is None or not success:
        assert outcome == success
        assert parser.errors.error_counter == 1
        assert (
            parser.errors.error_list[0].basic_message
            == error_type.basic_message
        )
        assert parser.errors.error_list[0].description == description


@pytest.mark.parametrize(
    "statement, success",
    [
        (["CONNECTIONS", ":", "A", "-", "B", ";"], True),
        (
            [
                "CONNECTIONS",
                ":",
                "A",
                "-",
                "B",
                ";",
                "C",
                ".",
                "I1",
                "-",
                "D",
                ";",
            ],
            True,
        ),
        (["CONNECTIONS", "A"], False),
        (["CONNECTIONS", ":"], None),
    ],
)
def test_parse_connection_block(statement, success):
    """Test module parse_connection_block"""
    parser = make_parser(statement)
    outcome = parser.parse_connection_block()
    assert outcome == success


@pytest.mark.parametrize(
    "statement, error_list",
    [
        (
            [],
            [(SyntaxErrors.UnexpectedEOF, "Missing CONNECTIONS block")],
        ),
        (
            ["A", ".", "asa"],
            [(SyntaxErrors.NoConnections, "Missing CONNECTIONS block")],
        ),
        (["CONNECTIONS"], [(SyntaxErrors.UnexpectedEOF, "Expected ':'")]),
        (
            ["CONNECTIONS", "-", "B"],
            [(SyntaxErrors.UnexpectedToken, "Expected ':'")],
        ),
        (
            ["CONNECTIONS", ":"],
            [
                (
                    SyntaxErrors.UnexpectedEOF,
                    "Expected connection statement",
                ),
                (SyntaxErrors.NoConnections, "Empty CONNECTIONS block"),
            ],
        ),
        (
            ["CONNECTIONS", ":", "A", "-", "AND", ";", "C", "D"],
            [
                (SyntaxErrors.UnexpectedToken, "Expected pin's device name"),
                (SyntaxErrors.UnexpectedToken, "Expected '.', '-', or ';'"),
            ],
        ),
    ],
)
def test_parse_connection_block_errors(statement, error_list):
    """Test errors arising in parse_block_statement."""
    parser = make_parser(statement)
    parser.parse_connection_block()
    if len(error_list) > 0:
        assert parser.errors.error_counter == len(error_list)
        for i in range(len(error_list)):
            (e_type, e_des) = error_list[i]
            assert (
                parser.errors.error_list[i].basic_message
                == e_type.basic_message
            )
            assert parser.errors.error_list[i].description == e_des
