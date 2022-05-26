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

    def __repr__(self):
        """Customised repr of error objects."""
        return (
            f"{self.__class__.__name__}: {self.message} - {self.description}"
        )

    def explain(self):
        """TODO."""
        pass


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

    def add_error(self, error):
        """Add an error to the existing list."""
        self.error_counter += 1
        self.error_list.append(error)

    def print_error_message(self, error):
        """TODO."""
        pass
