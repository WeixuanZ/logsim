"""Custom types and corresponding strings in the language, and custom error types.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.
"""

from enum import Enum, auto, unique


class KeywordType(Enum):
    """Language builtin keywords, used to initiate blocks."""

    DEVICES = "DEVICES"
    CONNECTIONS = "CONNECTIONS"
    MONITORS = "MONITORS"


class OperatorType(Enum):
    """Language operators."""

    EQUAL = "="
    CONNECT = "-"
    DOT = "."
    LEFT_ANGLE = "<"
    RIGHT_ANGLE = ">"
    COLON = ":"
    SEMICOLON = ";"
    FORWARD_SLASH = "/"


class DeviceType(Enum):
    """Supported devices."""

    AND = "AND"
    OR = "OR"
    NOR = "NOR"
    NAND = "NAND"
    XOR = "XOR"
    D_TYPE = "DTYPE"
    CLOCK = "CLOCK"
    SWITCH = "SWITCH"


class DTypeInputType(Enum):
    """D-type flip-flop inputs."""

    CLK = "CLK"
    SET = "SET"
    CLEAR = "CLEAR"
    DATA = "DATA"


class DTypeOutputType(Enum):
    """D-type flip-flop outputs."""

    Q = "Q"
    QBAR = "QBAR"


@unique
class ReservedSymbolType(Enum):
    """All built-in symbol types in the language, which are reserved."""

    Keywords = KeywordType
    Operators = OperatorType
    Devices = DeviceType
    DTypeInputs = DTypeInputType
    DTypeOutputs = DTypeOutputType


class ExternalSymbolType(Enum):
    """User-defined symbol types."""

    Numbers = auto()  # string of digits
    ExternalNames = auto()  # User defined names (for devices) and pins (e.g. I1)


class ErrorCode(Enum):
    """TODO."""

    pass


class Error:
    """TODO."""

    pass


class SyntaxErrors(Error):
    """TODO."""

    pass


class SemanticErrors(Error):
    """TODO."""

    pass


class Errors(Error):
    """TODO."""

    pass
