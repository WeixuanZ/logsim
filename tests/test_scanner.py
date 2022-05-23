"""Test the scanner module."""

import pytest

from scanner import Scanner
from names import Names


@pytest.fixture()
def file_content():
    """Test file content."""
    return (
        "Hello World!\n"
        "Some numbers: 1, 23, 456\n"
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n"
        "Aenean vitae quam eget ex laoreet vehicula ac a diam.\n"
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
        (96, 3, 0),
        (148, 3, 52),
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
    assert scanner.read(1, start=148) == "\n"
    assert scanner.read(1, start=149) == scanner.EOF