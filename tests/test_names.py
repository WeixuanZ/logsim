"""Test the names module."""
import sys

import pytest

from custom_types import ReservedSymbolTypeMeta, ExtendedEnum


# mock reserved symbols
# -----------------------------------------------------------------------------
class TestTypeContext(ExtendedEnum):
    """Mock up of symbol type context."""

    TEST_RESERVED1 = "TEST_RESERVED1"
    TEST_RESERVED2 = "TEST_RESERVED2"
    TEST_RESERVED3 = "TEST_RESERVED3"


class ReservedSymbolType(metaclass=ReservedSymbolTypeMeta):
    """Mock up of ReservedSymbolType."""

    symbol_contexts = [TestTypeContext]


class ExternalSymbolType(ExtendedEnum):
    """ExternalSymbolType for injection into mock module."""

    NUMBERS = "NUMBERS"
    EXTERNAL_NAMES = "EXTERNAL_NAMES"


module = type(sys)("custom_types")
# use the mock classes
module.ReservedSymbolType = ReservedSymbolType
module.ExternalSymbolType = ExternalSymbolType
# inject mock module, so Names is initialized based on mock classes
sys.modules["custom_types"] = module
from names import Names  # noqa: E402

# -----------------------------------------------------------------------------


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return Names()


@pytest.fixture
def name_string_list():
    """Return a list of test names."""
    return ["TEST1", "TEST2", "TEST3"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    names = Names()
    names.unique_error_codes(1)
    names.lookup(name_string_list)
    return names


# -----------------------------------------------------------------------------


def test_unique_error_codes_raises_exceptions(new_names):
    """Test if unique_error_codes raises expected exceptions."""
    with pytest.raises(TypeError):
        new_names.unique_error_codes(1.4)
    with pytest.raises(ValueError):
        new_names.unique_error_codes(-1)


@pytest.mark.parametrize(
    "num_error_codes, error_codes", [(0, []), (1, [0]), (2, [0, 1])]
)
def test_unique_error_codes(
    new_names, used_names, num_error_codes, error_codes
):
    """Test if unique_error_codes behaves as expected."""
    assert new_names.unique_error_codes(num_error_codes) == error_codes
    assert used_names.unique_error_codes(num_error_codes) == [
        c + 1 for c in error_codes
    ]


# -----------------------------------------------------------------------------


def test_query_raises_exceptions(new_names):
    """Test if query raises expected exceptions."""
    with pytest.raises(TypeError):
        new_names.query(1.4)
    with pytest.raises(TypeError):
        new_names.query(["TEST"])


@pytest.mark.parametrize(
    "name_id, name_string",
    [
        (0, "TEST_RESERVED1"),
        (1, "TEST_RESERVED2"),
        (2, "TEST_RESERVED3"),
        (None, "TEST"),
    ],
)
def test_query_reserved_symbols(new_names, name_id, name_string):
    """Test if query works correctly on reserved names."""
    assert new_names.query(name_string) == name_id


@pytest.mark.parametrize(
    "name_id, name_string",
    [(3, "TEST1"), (4, "TEST2"), (5, "TEST3"), (None, "TEST4")],
)
def test_lookup_query(used_names, name_id, name_string):
    """Test if query works correctly on external names."""
    assert used_names.query(name_string) == name_id


# -----------------------------------------------------------------------------


def test_lookup_raises_exceptions(new_names):
    """Test if lookup raises expected exceptions."""
    with pytest.raises(TypeError):
        new_names.lookup("TEST")
    with pytest.raises(TypeError):
        new_names.lookup(1)


@pytest.mark.parametrize(
    "name_id_list, name_string_list",
    [
        ([], []),
        ([0], ["TEST_RESERVED1"]),
        ([0, 1], ["TEST_RESERVED1", "TEST_RESERVED2"]),
        ([0, 0], ["TEST_RESERVED1", "TEST_RESERVED1"]),
        ([3], ["TEST"]),
        ([3, 4], ["TEST1", "TEST2"]),
        ([3, 3], ["TEST", "TEST"]),
    ],
)
def test_lookup(new_names, name_id_list, name_string_list):
    """Test if lookup behaves as expected."""
    assert new_names.lookup(name_string_list) == name_id_list


# -----------------------------------------------------------------------------


def test_get_name_string_raises_exceptions(new_names):
    """Test if get_name_string raises expected exceptions."""
    with pytest.raises(TypeError):
        new_names.get_name_string(1.4)
    with pytest.raises(TypeError):
        new_names.get_name_string("hello")
    with pytest.raises(ValueError):
        new_names.get_name_string(-1)


@pytest.mark.parametrize(
    "name_id, expected_string",
    [
        (0, "TEST_RESERVED1"),
        (1, "TEST_RESERVED2"),
        (2, "TEST_RESERVED3"),
        (3, None),
    ],
)
def test_get_name_string_reserved_symbols(new_names, name_id, expected_string):
    """Test if get_name_string returns the expected reserved string."""
    assert new_names.get_name_string(name_id) == expected_string


@pytest.mark.parametrize(
    "name_id, expected_string",
    [(3, "TEST1"), (4, "TEST2"), (5, "TEST3"), (6, None)],
)
def test_get_name_string(used_names, name_id, expected_string):
    """Test if get_name_string returns the expected external string."""
    assert used_names.get_name_string(name_id) == expected_string


# -----------------------------------------------------------------------------


def test_get_name_type_raises_exceptions(new_names):
    """Test if get_name_type raises expected exceptions."""
    with pytest.raises(TypeError):
        new_names.get_name_string(1.4)
    with pytest.raises(TypeError):
        new_names.get_name_string("hello")
    with pytest.raises(ValueError):
        new_names.get_name_string(-1)


@pytest.mark.parametrize(
    "name_id, expected_type",
    [
        (0, TestTypeContext.TEST_RESERVED1),
        (1, TestTypeContext.TEST_RESERVED2),
        (2, TestTypeContext.TEST_RESERVED3),
        (3, None),
    ],
)
def test_get_name_type_reserved_symbols(new_names, name_id, expected_type):
    """Test if get_name_type returns the expected string on reserved names."""
    assert new_names.get_name_type(name_id) is expected_type


def test_get_name_type(used_names):
    """Test if get_name_type returns the expected string on external names."""
    assert used_names.get_name_type(3) is ExternalSymbolType.EXTERNAL_NAMES
    used_names.lookup(["01", "1"])
    assert used_names.get_name_type(6) is ExternalSymbolType.NUMBERS
    assert used_names.get_name_type(7) is ExternalSymbolType.NUMBERS
