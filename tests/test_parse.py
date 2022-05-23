"""Test parser module"""
import pytest

from parse import Parser
from scanner import Symbol
from names import Names
from custom_types import OperatorType


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
