"""Test the custom_types module."""

from custom_types import ExtendedEnum, ReservedSymbolTypeMeta


class TestSymbolContext(ExtendedEnum):
    """Mock up of a symbol type context."""

    TEST1 = "TEST1"
    TEST2 = "TEST2"


class ReservedSymbolType(metaclass=ReservedSymbolTypeMeta):
    """Mock up of ReservedSymbolType class."""

    symbol_contexts = [TestSymbolContext]


def test_extended_enum():
    """Test the values method correctly list all values of the Enum."""

    class TestEnum(ExtendedEnum):
        TEST1 = "TEST1"
        TEST2 = "TEST2"

    test_enum = TestEnum

    assert test_enum.values() == ["TEST1", "TEST2"]


def test_reserved_symbol_type():
    """Test ReservedSymbolTypeMeta creates classes with the correct methods."""
    assert ReservedSymbolType.TEST1 is TestSymbolContext.TEST1
    assert ReservedSymbolType.TEST2 is TestSymbolContext.TEST2
    assert ReservedSymbolType.values() == ["TEST1", "TEST2"]
    assert ReservedSymbolType.__members__ == {
        "TEST1": TestSymbolContext.TEST1,
        "TEST2": TestSymbolContext.TEST2,
    }
