"""Test the custom_types module."""

from custom_types import ExtendedEnum, ReservedSymbolTypeMeta


class MockSymbolContext(ExtendedEnum):
    """Mock up of a symbol type context."""

    TEST1 = "TEST1"
    TEST2 = "TEST2"
    TEST3 = ","
    TEST4 = ";"


class MockReservedSymbolType(metaclass=ReservedSymbolTypeMeta):
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
    assert MockReservedSymbolType.TEST1 is MockSymbolContext.TEST1
    assert MockReservedSymbolType.TEST2 is MockSymbolContext.TEST2
    assert MockReservedSymbolType.values() == ["TEST1", "TEST2", ",", ";"]
    assert MockReservedSymbolType.__members__ == {
        "TEST1": MockSymbolContext.TEST1,
        "TEST2": MockSymbolContext.TEST2,
        "TEST3": MockSymbolContext.TEST3,
        "TEST4": MockSymbolContext.TEST4,
    }
    assert MockReservedSymbolType.mappings == {
        "TEST1": MockSymbolContext.TEST1,
        "TEST2": MockSymbolContext.TEST2,
        ",": MockSymbolContext.TEST3,
        ";": MockSymbolContext.TEST4,
    }
