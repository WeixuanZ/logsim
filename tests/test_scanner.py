"""Test the scanner module."""

import pytest

from scanner import Symbol, Scanner
from names import Names
from custom_types import (
    ReservedSymbolTypeMeta,
    ExtendedEnum,
    ExternalSymbolType,
)


@pytest.fixture()
def file_content():
    """Content of the test file."""
    return (
        "Hello World!\n"  # 13
        "Some numbers: 1, 23, 456\n"  # 38
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n"  # 95
        "Aenean vitae quam eget ex laoreet vehicula ac a diam.\n"  # 149
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
def scanner(input_file):
    """Create a scanner instance with the test file."""
    return Scanner(input_file, Names())


# -----------------------------------------------------------------------------


def test_file_content(scanner, file_content):
    """Test if the scanner reads file correctly."""
    assert scanner.file_content == file_content


def test_get_lineno_colno_raises_exceptions(scanner):
    """Test if get_lineno_colno raises expected exceptions."""
    with pytest.raises(TypeError):
        scanner.get_lineno_colno(1.1)
    with pytest.raises(ValueError):
        scanner.get_lineno_colno(-1)
    with pytest.raises(ValueError):
        scanner.get_lineno_colno(150)


@pytest.mark.parametrize(
    "pos, lineno, colno,",
    [
        (0, 0, 0),
        (1, 0, 1),
        (12, 0, 12),
        (13, 1, 0),
        (14, 1, 1),
        (38, 2, 0),
        (39, 2, 1),
        (95, 3, 0),
        (148, 3, 53),
    ],
)
def test_get_lineno_colno(scanner, pos, lineno, colno):
    """Test if get_lineno_colno behaves as expected."""
    assert scanner.get_lineno_colno(pos) == (lineno, colno)


def test_get_line_raises_exceptions(scanner):
    """Test if get line functions raise expected exceptions."""
    with pytest.raises(TypeError):
        scanner.get_line_by_lineno(1.1)
    with pytest.raises(ValueError):
        scanner.get_line_by_lineno(-1)
    with pytest.raises(ValueError):
        scanner.get_line_by_lineno(4)
    with pytest.raises(TypeError):
        scanner.get_line_by_pos(1.1)
    with pytest.raises(ValueError):
        scanner.get_line_by_pos(-1)
    with pytest.raises(ValueError):
        scanner.get_line_by_pos(1000)


@pytest.mark.parametrize(
    "lineno, line",
    [
        (0, "Hello World!\n"),
        (1, "Some numbers: 1, 23, 456\n"),
        (2, "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n"),
        (3, "Aenean vitae quam eget ex laoreet vehicula ac a diam.\n"),
    ],
)
def test_get_line_by_lineno(scanner, lineno, line):
    """Test if get_lineno_by_lineno behaves as expected."""
    assert scanner.get_line_by_lineno(lineno) == line


@pytest.mark.parametrize(
    "pos, line",
    [
        (0, "Hello World!\n"),
        (1, "Hello World!\n"),
        (12, "Hello World!\n"),
        (13, "Some numbers: 1, 23, 456\n"),
        (37, "Some numbers: 1, 23, 456\n"),
    ],
)
def test_get_line_by_pos(scanner, pos, line):
    """Test if get_lineno_by_pos behaves as expected."""
    assert scanner.get_line_by_pos(pos) == line


def test_move_pointer_raises_exceptions(scanner):
    """Test if move pointer functions raise expected exceptions."""
    with pytest.raises(TypeError):
        scanner.move_pointer_absolute(1.1)
    with pytest.raises(ValueError):
        scanner.move_pointer_absolute(-1)
    with pytest.raises(ValueError):
        scanner.move_pointer_absolute(1000)


def test_move_pointer(scanner):
    """Test if move pointer functions behave as expected."""
    assert scanner.pointer == (0, 0, 0)
    scanner.move_pointer_absolute(3)
    assert scanner.pointer == (3, 0, 3)
    scanner.move_pointer_relative(1)
    assert scanner.pointer == (4, 0, 4)
    scanner.move_pointer_relative(-2)
    assert scanner.pointer == (2, 0, 2)

    # pointer at EOF
    scanner.move_pointer_absolute(149)
    assert scanner.pointer_pos is Scanner.EOF


def test_read_raises_exceptions(scanner):
    """Test if read raise expected exceptions."""
    with pytest.raises(TypeError):
        scanner.read(1.1)
    with pytest.raises(ValueError):
        scanner.read(-1)


def test_read(scanner, file_content):
    """Test if read behaves as expected."""
    assert scanner.read(0) == ""
    assert scanner.read(2) == "He"
    assert scanner.read(2) == "ll"

    assert scanner.read(5, start=0) == "Hello"
    assert scanner.read(1, reset_pointer=True) == " "
    assert scanner.read(1) == " "

    assert scanner.read(1000, start=0) == file_content
    assert scanner.read(1) is scanner.EOF
    assert scanner.read(1) is scanner.EOF

    assert scanner.read(1, start=148) == "\n"
    assert scanner.read(1, start=149) == scanner.EOF


def test_get_next_character(scanner, file_content):
    """Test if get_next_character behaves as expected."""
    assert scanner.get_next_character() == "H"
    assert scanner.pointer_pos == 1
    assert scanner.get_next_character() == "e"
    assert scanner.pointer_pos == 2
    # test reset_pointer
    assert scanner.get_next_character(reset_pointer=True) == "l"
    assert scanner.pointer_pos == 2
    # test predicate
    assert scanner.get_next_character(predicate=lambda c: c.isdigit()) == "1"
    assert scanner.pointer_pos == 28

    # check every character in the file
    scanner.move_pointer_absolute(0)
    file_content = iter(file_content)
    while (c := scanner.get_next_character()) is not Scanner.EOF:
        assert c == next(file_content)


def test_move_pointer_onto_next_character(scanner):
    """Test if move_pointer_onto_next_character behaves as expected."""
    scanner.move_pointer_onto_next_character()
    assert scanner.pointer_pos == 0
    scanner.move_pointer_onto_next_character()
    assert scanner.pointer_pos == 0

    # test predicate
    scanner.move_pointer_onto_next_character(predicate=lambda c: c == "!")
    assert scanner.pointer_pos == 11
    # check the pointer is on the desired character
    assert scanner.read(1, reset_pointer=True) == "!"
    scanner.move_pointer_onto_next_character(predicate=lambda c: c.isdigit())
    assert scanner.pointer_pos == 27
    assert scanner.read(1, reset_pointer=True) == "1"

    scanner.move_pointer_absolute(148)
    scanner.move_pointer_onto_next_character()
    assert scanner.pointer_pos == 148
    scanner.move_pointer_absolute(149)
    scanner.move_pointer_onto_next_character()
    assert scanner.pointer_pos is Scanner.EOF
    assert scanner.read(1) is Scanner.EOF


def test_move_pointer_after_next_match(scanner):
    """Test if move_pointer_after_next_match behaves as expected."""
    scanner.move_pointer_after_next_match("23")
    assert scanner.pointer_pos == 32
    scanner.move_pointer_after_next_match("23")
    assert scanner.pointer_pos == Scanner.EOF

    scanner.move_pointer_absolute(0)
    scanner.move_pointer_after_next_match("456")
    assert scanner.pointer_pos == 37

    scanner.move_pointer_absolute(0)
    scanner.move_pointer_after_next_match("am")
    assert scanner.pointer_pos == 62
    scanner.move_pointer_after_next_match("am")
    assert scanner.pointer_pos == 112
    scanner.move_pointer_after_next_match("am")
    assert scanner.pointer_pos == 147
    scanner.move_pointer_after_next_match("am")
    assert scanner.pointer_pos == Scanner.EOF


def test_get_next_non_whitespace_character(scanner, file_content):
    """Test if get_next_non_whitespace_chcaracter behaves as expected."""
    assert scanner.get_next_non_whitespace_character() == "H"
    # test reset_pointer
    assert scanner.get_next_non_whitespace_character(reset_pointer=True) == "e"
    assert scanner.pointer_pos == 1
    assert scanner.get_next_non_whitespace_character() == "e"

    # check every non-whitespace character in file
    scanner.move_pointer_absolute(0)
    file_content_no_whitespace = filter(
        lambda c: not c.isspace(), file_content
    )
    while (
        c := scanner.get_next_non_whitespace_character()
    ) is not Scanner.EOF:
        assert c == next(file_content_no_whitespace)


def test_move_pointer_skip_whitespace_characters(scanner):
    """Test if move_pointer_skip_whitespace_characters behaves as expected."""
    scanner.move_pointer_skip_whitespace_characters()
    assert scanner.pointer_pos == 0
    scanner.move_pointer_skip_whitespace_characters()
    assert scanner.pointer_pos == 0
    scanner.move_pointer_absolute(12)
    scanner.move_pointer_skip_whitespace_characters()
    assert scanner.pointer_pos == 13
    scanner.move_pointer_absolute(17)
    scanner.move_pointer_skip_whitespace_characters()
    assert scanner.pointer_pos == 18


def test_get_next_chunk(scanner):
    """Test if get_next_chunk behaves as expected."""
    assert (
        scanner.get_next_chunk(
            start_predicate=lambda c: c == "H",
            end_predicate=lambda c: c == " ",
        )
        == "Hello"
    )
    assert scanner.pointer_pos == 5

    scanner.move_pointer_absolute(0)
    assert (
        scanner.get_next_chunk(
            start_predicate=lambda c: c == "H",
            end_predicate=lambda c: c.isspace(),
        )
        == "Hello"
    )
    assert scanner.pointer_pos == 5


def test_get_next_number(scanner):
    """Test if get_next_number behaves as expected."""
    assert scanner.get_next_number() == "1"
    assert scanner.pointer_pos == 28
    assert scanner.get_next_number() == "23"
    assert scanner.pointer_pos == 32
    assert scanner.get_next_number() == "456"
    assert scanner.pointer_pos == 37


def test_get_next_name(scanner):
    """Test if get_next_name behaves as expected."""
    assert scanner.get_next_name() == "Hello"
    assert scanner.get_next_name() == "World"
    assert scanner.get_next_name() == "Some"
    assert scanner.get_next_name() == "numbers"
    assert scanner.get_next_name() == "Lorem"


# -----------------------------------------------------------------------------


# mock reserved symbols
class MockKeywordTypeContext(ExtendedEnum):
    """Mock of keyword symbol type context."""

    KEYWORD1 = "KEYWORD1"  # id = 0
    KEYWORD2 = "KEYWORD2"  # id = 1
    KEYWORD3 = "KEYWORD3"  # id = 2


class MockOperatorTypeContext(ExtendedEnum):
    """Mock of operator symbol type context"""

    COMMA = ","  # id = 3


class ReservedSymbolType(metaclass=ReservedSymbolTypeMeta):
    """Mock up of ReservedSymbolType."""

    symbol_contexts = [MockKeywordTypeContext, MockOperatorTypeContext]


@pytest.mark.parametrize(
    "content, expected_symbols",
    [
        (  # keyword
            "KEYWORD1",
            [
                Symbol(
                    symbol_type=ReservedSymbolType.KEYWORD1,
                    symbol_id=0,
                    lineno=0,
                    colno=0,
                )
            ],
        ),
        (  # not keyword
            "KEYWORD",
            [
                Symbol(
                    symbol_type=ExternalSymbolType.IDENTIFIER,
                    symbol_id=4,
                    lineno=0,
                    colno=0,
                )
            ],
        ),
        (  # new line
            "KEYWORD1\nKEYWORD2",
            [
                Symbol(
                    symbol_type=ReservedSymbolType.KEYWORD1,
                    symbol_id=0,
                    lineno=0,
                    colno=0,
                ),
                Symbol(
                    symbol_type=ReservedSymbolType.KEYWORD2,
                    symbol_id=1,
                    lineno=1,
                    colno=0,
                ),
            ],
        ),
        (  # line comment
            "KEYWORD1 // line comment",
            [
                Symbol(
                    symbol_type=ReservedSymbolType.KEYWORD1,
                    symbol_id=0,
                    lineno=0,
                    colno=0,
                )
            ],
        ),
        (  # not line comment
            "KEYWORD1 / line comment",
            [
                Symbol(
                    symbol_type=ReservedSymbolType.KEYWORD1,
                    symbol_id=0,
                    lineno=0,
                    colno=0,
                ),
                Symbol(
                    symbol_type=ExternalSymbolType.IDENTIFIER,
                    symbol_id=4,
                    lineno=0,
                    colno=11,
                ),
                Symbol(
                    symbol_type=ExternalSymbolType.IDENTIFIER,
                    symbol_id=5,
                    lineno=0,
                    colno=16,
                ),
            ],
        ),
        (  # block comment
            "KEYWORD1 /* block \n" "comment */",
            [
                Symbol(
                    symbol_type=ReservedSymbolType.KEYWORD1,
                    symbol_id=0,
                    lineno=0,
                    colno=0,
                )
            ],
        ),
        (  # not block comment
            "KEYWORD1 /* block \n" "comment /*",
            [
                Symbol(
                    symbol_type=ReservedSymbolType.KEYWORD1,
                    symbol_id=0,
                    lineno=0,
                    colno=0,
                ),
                Symbol(
                    symbol_type=ExternalSymbolType.IDENTIFIER,
                    symbol_id=4,
                    lineno=0,
                    colno=12,
                ),
                Symbol(
                    symbol_type=ExternalSymbolType.IDENTIFIER,
                    symbol_id=5,
                    lineno=1,
                    colno=0,
                ),
            ],
        ),
        (  # operator
            "KEYWORD1, KEYWORD2",
            [
                Symbol(
                    symbol_type=ReservedSymbolType.KEYWORD1,
                    symbol_id=0,
                    lineno=0,
                    colno=0,
                ),
                Symbol(
                    symbol_type=ReservedSymbolType.COMMA,
                    symbol_id=3,
                    lineno=0,
                    colno=8,
                ),
                Symbol(
                    symbol_type=ReservedSymbolType.KEYWORD2,
                    symbol_id=1,
                    lineno=0,
                    colno=10,
                ),
            ],
        ),
        (  # new line and whitespaces
            "KEYWORD1,\n    KEYWORD2",
            [
                Symbol(
                    symbol_type=ReservedSymbolType.KEYWORD1,
                    symbol_id=0,
                    lineno=0,
                    colno=0,
                ),
                Symbol(
                    symbol_type=ReservedSymbolType.COMMA,
                    symbol_id=3,
                    lineno=0,
                    colno=8,
                ),
                Symbol(
                    symbol_type=ReservedSymbolType.KEYWORD2,
                    symbol_id=1,
                    lineno=1,
                    colno=4,
                ),
            ],
        ),
        (  # identifier and numbers
            "KEYWORD1 a123 123",
            [
                Symbol(
                    symbol_type=ReservedSymbolType.KEYWORD1,
                    symbol_id=0,
                    lineno=0,
                    colno=0,
                ),
                Symbol(
                    symbol_type=ExternalSymbolType.IDENTIFIER,
                    symbol_id=4,
                    lineno=0,
                    colno=9,
                ),
                Symbol(
                    symbol_type=ExternalSymbolType.NUMBERS,
                    symbol_id=5,
                    lineno=0,
                    colno=14,
                ),
            ],
        ),
        (  # naming starting with _
            "_NEW_KEYWORD",
            [
                Symbol(
                    symbol_type=ExternalSymbolType.IDENTIFIER,
                    symbol_id=4,
                    lineno=0,
                    colno=0,
                ),
            ],
        ),
        (  # invalid character
            "!! KEYWORD1",
            [
                Symbol(
                    symbol_type=MockKeywordTypeContext.KEYWORD1,
                    symbol_id=0,
                    lineno=0,
                    colno=3,
                ),
            ],
        ),
    ],
)
def test_get_symbol(tmp_path, monkeypatch, content, expected_symbols):
    """Test get_symbol behaves as expected."""
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "test.txt"
    p.write_text(content)

    monkeypatch.setattr("names.ReservedSymbolType", ReservedSymbolType)
    monkeypatch.setattr("scanner.ReservedSymbolType", ReservedSymbolType)
    scanner = Scanner(p, Names())

    expected_symbols = iter(expected_symbols)
    while (symbol := scanner.get_symbol()) is not None:
        assert symbol == next(expected_symbols)
