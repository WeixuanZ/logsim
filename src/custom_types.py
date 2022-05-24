"""Custom types and corresponding strings in the language.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

SPHINX-IGNORE
Classes
-------
DTypeInputType - D-type flip-flop inputs.
DTypeOutputType - D-type flip-flop outputs.
DeviceType - Supported devices.
Error
ErrorCode
Errors
ExtendedEnum - Subclass of default Enum with add values method.
ExternalSymbolType - User-defined symbol types.
KeywordType - Language builtin keywords, used to initiate blocks.
OperatorType - Operators defined in the logic definition language.
ReservedSymbolType -
    All built-in symbol types in the language, which are reserved.
ReservedSymbolTypeMeta -
    Metaclass that create classes acting as wrapper around Enums.
SemanticErrors
SyntaxErrors
SPHINX-IGNORE
"""

from types import MappingProxyType
from enum import Enum
from operator import attrgetter, methodcaller
from itertools import chain


class ExtendedEnum(Enum):
    """Subclass of default Enum with add values method."""

    @classmethod
    def values(cls) -> list:
        """List all the values of the Enum."""
        return list(map(attrgetter("value"), cls))


class KeywordType(ExtendedEnum):
    """Language builtin keywords, used to initiate blocks."""

    DEVICES = "DEVICES"
    CONNECTIONS = "CONNECTIONS"
    MONITORS = "MONITORS"


class OperatorType(ExtendedEnum):
    """Operators defined in the logic definition language."""

    EQUAL = "="
    CONNECT = "-"
    DOT = "."
    COMMA = ","
    LEFT_ANGLE = "<"
    RIGHT_ANGLE = ">"
    COLON = ":"
    SEMICOLON = ";"


class DeviceType(ExtendedEnum):
    """Supported devices."""

    AND = "AND"
    OR = "OR"
    NOR = "NOR"
    NAND = "NAND"
    XOR = "XOR"
    D_TYPE = "DTYPE"
    CLOCK = "CLOCK"
    SWITCH = "SWITCH"


class DTypeInputType(ExtendedEnum):
    """D-type flip-flop inputs."""

    CLK = "CLK"
    SET = "SET"
    CLEAR = "CLEAR"
    DATA = "DATA"


class DTypeOutputType(ExtendedEnum):
    """D-type flip-flop outputs."""

    Q = "Q"
    QBAR = "QBAR"


class ReservedSymbolTypeMeta(type):
    """Metaclass that create classes acting as wrapper around Enums.

    This allows combination of several Enums, with value pointing
    to the original Enum entry, enabling correct comparison.

    Class created have an interface similar to that of the standard Enum.
    """

    def __new__(mcs, classname, bases, dictionary):
        """Create the class object."""
        for symbol_context in dictionary.get("symbol_contexts", ()):
            for symbol_type in symbol_context:
                dictionary[symbol_type.name] = symbol_type
        return super().__new__(mcs, classname, bases, dictionary)

    def __init__(cls, classname, bases, dictionary):
        """Initialize the class object."""
        if not hasattr(cls, "symbol_contexts"):
            cls.symbol_contexts = []
        super().__init__(classname, bases, dictionary)

    def __iter__(cls):
        """Make the class an iterator of types."""
        return chain.from_iterable(cls.symbol_contexts)

    def values(cls) -> list:
        """Return all the type values."""
        return list(
            chain.from_iterable(
                map(methodcaller("values"), cls.symbol_contexts)
            )
        )

    @property
    def __members__(cls) -> MappingProxyType:
        """Property that returns a mapping between type name and type."""
        string_type_pair = chain.from_iterable(
            map(
                lambda symbol_context: symbol_context.__members__.items(),
                cls.symbol_contexts,
            )
        )
        return MappingProxyType(dict(string_type_pair))

    @property
    def mappings(cls) -> MappingProxyType:
        """Property that returns a mapping between type value and type."""
        return MappingProxyType(
            dict(map(lambda t: (t.value, t), cls.__members__.values()))
        )


class ReservedSymbolType(metaclass=ReservedSymbolTypeMeta):
    """All built-in symbol types in the language, which are reserved.

    This class is created from ReservedSymbolTypeMeta, combining all the types
    together.

    Specify all the symbol type contexts as a class attribute list.

    Attributes
    ----------
    symbol_contexts: list
        List of all symbol type contexts
    """

    symbol_contexts = [
        KeywordType,
        OperatorType,
        DeviceType,
        DTypeInputType,
        DTypeOutputType,
    ]


class ExternalSymbolType(ExtendedEnum):
    """User-defined symbol types."""

    NUMBERS = "NUMBERS"  # string of digits
    # User defined names (for devices) and pins (e.g. I1)
    IDENTIFIER = "IDENTIFIER"


class ErrorCode(Enum):
    """TODO."""

    pass


class Error:
    """Class describing each error.

    Parameters
    ----------
    error_message:
        short message presented to the user when the error is found

    Methods
    -------
    set_description(self, description):
        Sets a more detailed description of the error
    set_basic_message(self, message):
        Sets basic message of the error
    """

    def __init__(self, error_message, description=""):
        """Initialise error class."""
        self.basic_message = error_message
        self.description = description
        self.errorCode = None

    def set_description(self, description):
        """Set detailed description of error."""
        self.description = description

    def set_basic_message(self, message):
        """Set basic message of error."""
        self.basic_message = message


class SyntaxErrors(Error):
    """Different types of syntax errors."""

    UnexpectedToken = Error("Unexpected token")
    MissingSemicolon = Error("Missing ';' at the end of statement")
    MissingParam = Error("Missing parameter for device type")
    InvalidSwitchParam = Error("Invalid parameter for SWITCH device")
    NoDevices = Error("No devices found")
    NoConnections = Error("No connections found")
    NoMonitors = Error("No monitor pins found")


class SemanticErrors(Error):
    """Different types of semantic errors."""

    UndefinedDevice = Error("Undefined device name")
    NameClash = Error("NameClash")
    UndefinedInPin = Error("Undefined input pin")
    UndefinedOutPin = Error("Undefined output pin")
    ConnectInToIn = Error("Attempting to connect input pin to input pin")
    ConnectOutToOut = Error("Attempting to connect output pin to output pin")
    FloatingInput = Error("Floating input")
    MultipleConnections = Error(
        "Attempting to connect multiple pins to a signle pin"
    )
    InvalidCLK = Error(
        "Attempting to connect a device other than CLOCK to a CLK input of \
        DTYPE device"
    )
    InvalidAndParam = Error(
        "Invalid number of inputs for the gate"
    )  # for AND/NAND/NOR/OR/XOR
    InvalidClockParam = Error("Invalid clock period")


class Errors:
    """Collect and handle errors found while parsing circuit descriptions.

    Parameters
    ----------
    No parameters.

    Methods
    -------
    TODO.
    """

    def __init__(self):
        """Initialise Errors class."""
        self.error_counter = 0
        self.error_list = []

    def add_error(self, error: Error):
        """Add an error to the existing list."""
        self.error_counter += 1
        self.error_list.append(error)

    def show_error_position(self, colno, lineno):
        """TODO."""
        # prints a line of error and an arrow pointing to its exact position
        pass

    def print_error_message(self, error: Error):
        """TODO."""
        pass
