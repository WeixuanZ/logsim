"""Test the custom_types module."""

from custom_types import ExtendedEnum, ReservedSymbolTypeMeta


# mock reserved symbols
class MockKeywordTypeContext(ExtendedEnum):
    """Mock of keyword symbol type context."""

    TEST_KEYWORD1 = "TEST_KEYWORD1"
    TEST_KEYWORD2 = "TEST_KEYWORD2"
    TEST_KEYWORD3 = "TEST_KEYWORD3"


class MockOperatorTypeContext(ExtendedEnum):
    """Mock of operator symbol type context"""

    COMMA = ","


class MockReservedSymbolType(metaclass=ReservedSymbolTypeMeta):
    """Mock of ReservedSymbolType."""

    symbol_contexts = [MockKeywordTypeContext, MockOperatorTypeContext]


def test_extended_enum():
    """Test the values method correctly list all values of the Enum."""

    class TestEnum(ExtendedEnum):
        TEST1 = "TEST1"
        TEST2 = "TEST2"

    test_enum = TestEnum

    assert test_enum.values() == ["TEST1", "TEST2"]


def test_reserved_symbol_type():
    """Test ReservedSymbolTypeMeta creates classes with the correct methods."""
    assert (
        MockReservedSymbolType.TEST_KEYWORD1
        is MockKeywordTypeContext.TEST_KEYWORD1
    )
    assert MockReservedSymbolType.COMMA is MockOperatorTypeContext.COMMA

    # iter
    for (type, expected_type) in zip(
        MockReservedSymbolType,
        [
            MockKeywordTypeContext.TEST_KEYWORD1,
            MockKeywordTypeContext.TEST_KEYWORD2,
            MockKeywordTypeContext.TEST_KEYWORD3,
        ],
    ):
        assert type is expected_type

    # values()
    assert MockReservedSymbolType.values() == [
        "TEST_KEYWORD1",
        "TEST_KEYWORD2",
        "TEST_KEYWORD3",
        ",",
    ]

    # __members__
    assert MockReservedSymbolType.__members__ == {
        "TEST_KEYWORD1": MockKeywordTypeContext.TEST_KEYWORD1,
        "TEST_KEYWORD2": MockKeywordTypeContext.TEST_KEYWORD2,
        "TEST_KEYWORD3": MockKeywordTypeContext.TEST_KEYWORD3,
        "COMMA": MockOperatorTypeContext.COMMA,
    }

    # mappings
    assert MockReservedSymbolType.mappings == {
        "TEST_KEYWORD1": MockKeywordTypeContext.TEST_KEYWORD1,
        "TEST_KEYWORD2": MockKeywordTypeContext.TEST_KEYWORD2,
        "TEST_KEYWORD3": MockKeywordTypeContext.TEST_KEYWORD3,
        ",": MockOperatorTypeContext.COMMA,
    }
