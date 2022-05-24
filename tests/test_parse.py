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
    "statement, error_type, description, early_eof",
    [
        (
            ["Swnass"],
            SyntaxErrors.UnexpectedToken,
            "Expected device type",
            False,
        ),
        (
            ["SWITCH", ">"],
            SyntaxErrors.UnexpectedToken,
            "Expected '<' or ';'",
            False,
        ),
        (
            ["DTYPE", "<", "a"],
            SyntaxErrors.UnexpectedToken,
            "Expected number parameter",
            False,
        ),
        (
            ["AND", "<", "025", ";"],
            SyntaxErrors.UnexpectedToken,
            "Expected '>'",
            False,
        ),
        (["AND"], None, "", True),
        (["NAND", "<", "2"], None, "", True),
        (["NOR", "<", "0000", ">"], SyntaxErrors.MissingSemicolon, "", True),
        ([], None, "", True),
    ],
)
def test_parse_device_type_errors(
    statement, error_type, description, early_eof
):
    """Test specific syntax errors arising in parse_device_type."""
    parser = make_parser(statement)
    out, _ = parser.parse_device_type()
    if not early_eof:
        assert out is False
        assert parser.errors.error_counter == 1
        assert (
            parser.errors.error_list[0].basic_message
            == error_type.basic_message
        )
        assert parser.errors.error_list[0].description == description
    else:
        assert out is None
        if error_type is not None:
            assert parser.errors.error_counter == 1
            assert (
                parser.errors.error_list[0].basic_message
                == error_type.basic_message
            )


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
    "statement, error_type, description, early_eof",
    [
        ([], None, None, True),
        (["Weixuan", "=", "OR", "<", "2"], None, None, True),
        (
            ["AND", ",", "B", "=", "SWITCH", ";"],
            SyntaxErrors.UnexpectedToken,
            "Expected device name",
            False,
        ),
        (
            ["A", "B", "=", "SWITCH", ";"],
            SyntaxErrors.UnexpectedToken,
            "Expected ','",
            False,
        ),
        (
            ["A", ",", "B", ",", "C", "SWITCH", ";"],
            SyntaxErrors.UnexpectedToken,
            "Expected '='",
            False,
        ),
        (
            ["A", ",", "B", ",", "C", "=", "SWITCH"],
            SyntaxErrors.MissingSemicolon,
            "",
            True,
        ),
    ],
)
def test_parse_devices_statement_errors(
    statement, error_type, description, early_eof
):
    """Test specific syntax errors arising in parse_devices_statement."""
    parser = make_parser(statement)
    out, _ = parser.parse_devices_statement()
    if not early_eof:
        assert out is False
        assert parser.errors.error_counter == 1
        assert (
            parser.errors.error_list[0].basic_message
            == error_type.basic_message
        )
        assert parser.errors.error_list[0].description == description
    else:
        print(parser.errors.error_list[0].description)
        assert out is None
        if error_type == SyntaxErrors.MissingSemicolon:
            assert parser.errors.error_counter == 1
            assert (
                parser.errors.error_list[0].basic_message
                == error_type.basic_message
            )
