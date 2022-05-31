"""Error handling.

Used in the Logic Simulator project. Mainly used by the parser.

SPHINX-IGNORE
Classes
-------
ParseBaseExceptionMeta - Metaclass create ParseBaseException classes.
ParseBaseException - Base parse exception.
SyntaxErrors - Different types of syntax errors.
SemanticErrors - Different types of semantic errors.
Errors - Collect and handle errors found while parsing circuit descriptions.
SPHINX-IGNORE
"""
import inspect
from typing import Union
from itertools import takewhile, starmap

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
            cls.message = msg.partition("\n")[0][:-1]
        super().__init__(classname, bases, dictionary)


class ParseBaseException(metaclass=ParseBaseExceptionMeta):
    """Base parse exception.

    Parameter
    ---------
    description: Union[None, str]
        Error description

    Attributes
    ----------
    symbol: Union[Symbol, None]
        The symbol associated with the error
    depth: int
        The stack depth where the error is thrown

    SPHINX-IGNORE
    Public Methods
    --------------
    explain(self, names, scanner, show_depth=True):
        Return an explanation of the error
    """

    def __init__(self, description=None):
        """Initialize the exception instance."""
        self.description = description if description is not None else ""
        self.symbol: Union[Symbol, None] = None
        self.depth = 0

    def __repr__(self):
        """Customised repr of error objects."""
        return f"{self.__class__.__qualname__}: {self.message}" + (
            f" - {self.description}"
            if self.description is not None and self.description != ""
            else ""
        )

    def explain(self, names: Names, scanner: Scanner, show_depth=True) -> str:
        """Return an explanation of the error.

        If show_depth is True, the error message will be indented according
        to the stack depth of the function that throws the error.
        """
        if self.symbol is None:
            return self.__repr__() + "\n"

        error_line = scanner.get_line_by_lineno(self.symbol.lineno)
        # use this long way to deal with tabs
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
            ("  " * self.depth if show_depth else "")
            + (f"Line {self.symbol.lineno + 1}: " if self.depth > 0 else "")
            + self.__repr__()
            + "\n"
            + (
                ("  " * self.depth if show_depth else "")
                + error_line
                + ("  " * self.depth if show_depth else "")
                + cursor_line
                if self.depth > 0
                else ""
            )
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
    names: Names
    scanner: Scanner

    SPHINX-IGNORE
    Public Methods
    --------------
    add_error(self, error):
        Add an error to the error list.
    print_error_messages(self):
        Pretty print all error messages.
    SPHINX-IGNORE
    """

    def __init__(self, names: Names, scanner: Scanner):
        """Initialise Errors class."""
        self.error_counter = 0
        self.error_list = []
        self.names = names
        self.scanner = scanner

    def add_error(
        self,
        error: ParseBaseException,
        parse_entry_func_name="parse_network",
        base_depth=2,
    ) -> None:
        """Add an error to the error list.

        Parameters
        ----------
        error: ParseBaseException
            The error instance
        parse_entry_func_name: str
            The name of the top level parse function
        base_depth:
            Extra stack depth added on top of the top level parse function,
            by error handling functions.
        """
        # get the caller function stack depth from parse entry point
        error.depth = (
            sum(
                1
                for _ in takewhile(
                    lambda frame: frame.function != parse_entry_func_name,
                    inspect.stack(),
                )
            )
            - base_depth
        )

        self.error_counter += 1
        self.error_list.append(error)

    def print_error_messages(self) -> None:
        """Pretty print all error messages."""
        # sort errors by depth if on the same line
        sorted_error_list = sorted(
            self.error_list,
            key=lambda e: (
                e.symbol.lineno if e.symbol is not None else 0,
                e.depth,
            ),
        )
        show_depth_list = [False] + [
            getattr(sorted_error_list[i].symbol, "lineno", 0)
            == getattr(sorted_error_list[i - 1].symbol, "lineno", None)
            for i in range(1, len(sorted_error_list))
        ]

        print(
            "\033[91m"
            + f"{self.error_counter} Errors\n\n"
            + "\n".join(
                starmap(
                    lambda error, show_depth: error.explain(
                        self.names, self.scanner, show_depth=show_depth
                    ),
                    zip(sorted_error_list, show_depth_list),
                )
            )
            + "\033[91m"
        )
