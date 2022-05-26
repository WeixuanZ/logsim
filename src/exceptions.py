"""Error handling.

Used in the Logic Simulator project. Mainly used by the parser.

SPHINX-IGNORE
Classes
-------
Error
Errors
SemanticErrors
SyntaxErrors
SPHINX-IGNORE
"""

from typing import Union

from names import Names
from scanner import Symbol, Scanner


class ParseBaseExceptionMeta(type):
    """Metaclass create ParseBaseException classes.

    This allows default message to be defined using the doc string, simplify
    the code.
    """

    def __init__(cls, classname, bases, dictionary):
        """Initialize the class object."""
        if msg := dictionary.get("__doc__"):
            cls.message = msg[:-1]
        super().__init__(classname, bases, dictionary)


class ParseBaseException(metaclass=ParseBaseExceptionMeta):
    """Base parse exception."""

    def __init__(self, description=None):
        """Initialize the exception instance."""
        self.description = description if description is not None else ""
        self.symbol: Union[Symbol, None] = None

    def __repr__(self):
        """Customised repr of error objects."""
        return f"{self.__class__.__qualname__}: {self.message}" + (
            f" - {self.description}"
            if self.description is not None and self.description != ""
            else ""
        )

    def explain(self, names: Names, scanner: Scanner) -> str:
        """Return an explanation of the error."""
        if self.symbol is None:
            return self.__repr__()

        error_line = scanner.get_line_by_lineno(self.symbol.lineno)
        cursor_line = list(
            map(
                lambda c: " " if not c.isspace() or c in ("\n", "\r") else c,
                error_line,
            )
        )
        cursor_line[
            int(self.symbol.colno) + len(names.get_name_string(self.symbol.id))
        ] = "^"
        cursor_line = "".join(cursor_line)

        return (
            f"Line {self.symbol.lineno + 1}: "
            + self.__repr__()
            + "\n"
            + error_line
            + cursor_line
        )


class SyntaxErrors:
    """Different types of syntax errors."""

    class UnexpectedToken(ParseBaseException):
        """Unexpected token."""

    class MissingSemicolon(ParseBaseException):
        """Missing ';' at the end of statement."""

    class MissingParam(ParseBaseException):
        """Missing parameter for device type."""

    class InvalidSwitchParam(ParseBaseException):
        """Invalid parameter for SWITCH device."""

    class UnexpectedParam(ParseBaseException):
        """Unexpected parameter for device type."""

    class NoDevices(ParseBaseException):
        """No devices found."""

    class NoConnections(ParseBaseException):
        """No connections found."""

    class NoMonitors(ParseBaseException):
        """No monitor pins found."""

    class UnexpectedEOF(ParseBaseException):
        """Unexpected end of file."""


class SemanticErrors:
    """Different types of semantic errors."""

    class UndefinedDevice(ParseBaseException):
        """Undefined device name."""

    class NameClash(ParseBaseException):
        """NameClash."""

    class UndefinedInPin(ParseBaseException):
        """Undefined input pin."""

    class UndefinedOutPin(ParseBaseException):
        """Undefined output pin."""

    class ConnectInToIn(ParseBaseException):
        """Attempting to connect input pin to input pin."""

    class ConnectOutToOut(ParseBaseException):
        """Attempting to connect output pin to output pin."""

    class FloatingInput(ParseBaseException):
        """Floating input."""

    class MultipleConnections(ParseBaseException):
        """Attempting to connect multiple pins to a single pin."""

    class InvalidAndParam(ParseBaseException):
        """Invalid number of inputs for the gate."""

        # for AND/NAND/NOR/OR/XOR

    class InvalidClockParam(ParseBaseException):
        """Invalid clock period."""

    class MonitorInputPin(ParseBaseException):
        """Attempting to monitor an input pin."""

    class MonitorSamePin(ParseBaseException):
        """Warning: duplicate monitor pin."""


class Errors:
    """Collect and handle errors found while parsing circuit descriptions.

    Parameters
    ----------
    No parameters.

    Methods
    -------
    add_error(self, error):
        Add an error to the error list.
    print_error_messages(self):
        Pretty print all error messages.
    """

    def __init__(self, names: Names, scanner: Scanner):
        """Initialise Errors class."""
        self.error_counter = 0
        self.error_list = []
        self.names = names
        self.scanner = scanner

    def add_error(self, error: ParseBaseException) -> None:
        """Add an error to the error list."""
        self.error_counter += 1
        self.error_list.append(error)

    def print_error_messages(self) -> None:
        """Pretty print all error messages."""
        print(
            "\033[91m"
            + f"{self.error_counter} Errors\n\n"
            + "\n".join(
                map(
                    lambda error: error.explain(self.names, self.scanner),
                    self.error_list,
                )
            )
            + "\033[91m"
        )
