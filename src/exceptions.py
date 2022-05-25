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

import copy


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
    UnexpectedParam = Error("Unexpected parameter for device type")
    NoDevices = Error("No devices found")
    NoConnections = Error("No connections found")
    NoMonitors = Error("No monitor pins found")
    UnexpectedEOF = Error("Unexpected end of file")


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
        # TODO restructure Error classes so that there is no need to copy
        self.error_list.append(copy.deepcopy(error))

    def show_error_position(self, colno, lineno):
        """TODO."""
        # prints a line of error and an arrow pointing to its exact position
        pass

    def print_error_message(self, error: Error):
        """TODO."""
        pass
