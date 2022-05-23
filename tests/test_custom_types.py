"""Test the custom_types module."""

from custom_types import ExtendedEnum, ReservedSymbolTypeMeta


class MockSymbolContext(ExtendedEnum):
    """Mock up of a symbol type context."""

    TEST1 = "TEST1"
    TEST2 = "TEST2"


class ReservedSymbolType(metaclass=ReservedSymbolTypeMeta):
    """Mock up of ReservedSymbolType class."""

    symbol_contexts = [MockSymbolContext]


def test_extended_enum():
    """Test the values method correctly list all values of the Enum."""

    class TestEnum(ExtendedEnum):
        TEST1 = "TEST1"
        TEST2 = "TEST2"

    test_enum = TestEnum

    assert test_enum.values() == ["TEST1", "TEST2"]


def test_reserved_symbol_type():
    """Test ReservedSymbolTypeMeta creates classes with the correct methods."""
    assert ReservedSymbolType.TEST1 is MockSymbolContext.TEST1
    assert ReservedSymbolType.TEST2 is MockSymbolContext.TEST2
    assert ReservedSymbolType.values() == ["TEST1", "TEST2"]
    assert ReservedSymbolType.__members__ == {
        "TEST1": MockSymbolContext.TEST1,
        "TEST2": MockSymbolContext.TEST2,
    }
