"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

SPHINX-IGNORE
Classes
-------
Parser - parses the definition file and builds the logic network.
SPHINX-IGNORE
"""

from symbol_types import (
    KeywordType,
    DeviceType,
    ExternalSymbolType,
    OperatorType,
    DTypeInputType,
    DTypeOutputType,
)
from exceptions import SyntaxErrors, SemanticErrors, Errors


class Parser:
    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names:
        instance of the names.Names() class.
    devices:
        instance of the devices.Devices() class.
    network:
        instance of the network.Network() class.
    monitors:
        instance of the monitors.Monitors() class.
    scanner:
        instance of the scanner.Scanner() class.

    SPHINX-IGNORE
    Public Methods
    --------------
    parse_network(self):
        Parses the circuit definition file.
    SPHINX-IGNORE
    """

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner

        # initialize by getting first symbol from scanner
        self.current_symbol = scanner.get_symbol()

        # build the network while this is True, then just parse for errors
        self.syntax_valid = True

        # initialize errors
        self.errors = Errors()

    def throw_error(self, error_type, description=None):
        """Add error with optional description to the list."""
        error = error_type(description)
        error.symbol = self.current_symbol
        self.errors.add_error(error)

    def get_next(self):
        """Get next symbol from scanner and set it as current symbol.

        Return: False if there is end of file,
                True if new symbol was successfully retrieved
        """
        self.current_symbol = self.scanner.get_symbol()
        # check for end of file
        if self.current_symbol is None:
            return False
        return True

    def skip_to_end_of_line(self):
        """Update self.current_symbol until end of line SEMICOLON is reached.

        Return: False if there was unexpected end of file
                True if moved to end of line
        """
        if self.current_symbol is None:
            return False
        while self.current_symbol.type != OperatorType.SEMICOLON:
            if not self.get_next():
                return False
        return True

    def skip_to_block(self, keyword: KeywordType):
        """Skip all symbols until it gets to Keyword (eg CONNECTIONS).

        Return: False if there is unexpected end of file
                True if moved to block Keyword
        """
        if self.current_symbol is None:
            return False
        while self.current_symbol.type != keyword:
            if not self.get_next():
                return False
        return True

    def parse_device_block(self):
        """Parse DEVICES block.

        EBNF syntax: "DEVICES" , ":" , device_definition , {device_definition}

        Return: True if successful parsing,
        False if there was an error,
        None if there was (unexpected) end of file
        """
        if self.current_symbol is None:
            self.throw_error(
                SyntaxErrors.UnexpectedEOF, "Missing DEVICES block"
            )
            return None

        if not self.current_symbol.type == KeywordType.DEVICES:
            # TODO check for typos later to give suggestions for improvement
            self.throw_error(SyntaxErrors.NoDevices, "Missing DEVICES block")
            return False

        if not self.get_next():
            self.throw_error(
                SyntaxErrors.UnexpectedEOF, "Expected ':' after DEVICES"
            )
            return None

        if not self.current_symbol.type == OperatorType.COLON:
            self.throw_error(
                SyntaxErrors.UnexpectedToken, "Expected ':' after DEVICES"
            )
            return False

        self.get_next()
        outcome, device = self.parse_devices_statement()
        if outcome is None:
            self.syntax_valid = False
            self.throw_error(SyntaxErrors.NoDevices, "Empty DEVICES block")
            return None
        if not outcome:
            self.syntax_valid = False
            if not self.skip_to_end_of_line():
                # there was end of file
                self.throw_error(SyntaxErrors.NoDevices, "Empty DEVICES block")
                return None
            self.get_next()

        if self.syntax_valid:
            (device_names, gate_type, parameter) = device
            self.add_devices(device_names, gate_type, parameter)

        while (
            self.current_symbol is not None
            and self.current_symbol.type != KeywordType.CONNECTIONS
        ):
            success, device = self.parse_devices_statement()
            if success is None or not success:
                self.syntax_valid = False
                if not self.skip_to_end_of_line():
                    # unexpected end of file
                    return success
            if self.syntax_valid:
                (device_names, gate_type, parameter) = device
                self.add_devices(device_names, gate_type, parameter)
            self.get_next()
        return True

    def parse_devices_statement(self):
        """Parse device statement from DEVICES block.

        EBNF syntax: device_name ,{"," , device_name}, "=" ,device_type ,";"

        Return: success, (device_names, gate_type, parameter)
        success = None(unexpected eof), False(syntax not ok), True(syntax ok)
        device_names = list of strings
        gate_type = 'AND'|'NAND'|'OR'|'NOR'|'XOR'|'CLOCK'|'SWITCH'|'DTYPE'
        parameter = None or number
        """
        if self.current_symbol is None:
            self.throw_error(
                SyntaxErrors.UnexpectedEOF, "Expected device definition"
            )
            return None, None

        if not self.current_symbol.type == ExternalSymbolType.IDENTIFIER:
            self.throw_error(
                SyntaxErrors.UnexpectedToken, "Expected device name"
            )
            return False, None

        device_names = [self.names.get_name_string(self.current_symbol.id)]

        self.get_next()

        while (
            self.current_symbol is not None
            and self.current_symbol.type == OperatorType.COMMA
        ):
            if not self.get_next():
                self.throw_error(
                    SyntaxErrors.UnexpectedEOF, "Expected device name"
                )
                return None, None
            if not self.current_symbol.type == ExternalSymbolType.IDENTIFIER:
                self.throw_error(
                    SyntaxErrors.UnexpectedToken, "Expected device name"
                )
                return False, None
            device_names.append(
                self.names.get_name_string(self.current_symbol.id)
            )
            self.get_next()

        if self.current_symbol is None:
            self.throw_error(SyntaxErrors.UnexpectedEOF, "Expected ',' or '='")
            return None, None

        if not self.current_symbol.type == OperatorType.EQUAL:
            self.throw_error(
                SyntaxErrors.UnexpectedToken, "Expected ',' or '='"
            )
            return False, None

        self.get_next()

        success, device_type = self.parse_device_type()
        if success is None or not success:
            return success, None

        (dtype, parameter) = device_type

        if self.current_symbol is None:
            self.throw_error(SyntaxErrors.MissingSemicolon)
            return None, None

        if not self.current_symbol.type == OperatorType.SEMICOLON:
            self.throw_error(SyntaxErrors.UnexpectedToken, "Expected ';'")
            return False, None

        self.get_next()
        return True, (device_names, dtype, parameter)

    def parse_device_type(self):
        """Parse device type.

        EBNF syntax: device_type = ( "CLOCK", parameter )
            | ( "SWITCH", "<" , ( "0" | "1" ) , ">" )
            | ( ( "AND" | "NAND" | "OR" | "NOR" ), parameter )
            | "XOR"
            | "D_TYPE" ;
            parameter = "<" , digit , { digit } , ">" ;

        Return: success, (device_type, parameter)
        success = None(unexpected eof), False(syntax not ok), True(syntax ok)
        device_type = 'AND'|'NAND'|'OR'|'NOR'|'XOR'|'CLOCK'|'SWITCH'|'DTYPE'
        parameter = None or number
        """
        if self.current_symbol is None:
            self.throw_error(
                SyntaxErrors.UnexpectedEOF, "Expected device type"
            )
            return None, None

        if self.current_symbol.type not in DeviceType:
            self.throw_error(
                SyntaxErrors.UnexpectedToken, "Expected device type"
            )
            return False, None

        device_type = self.current_symbol.type

        if not self.get_next():
            self.throw_error(SyntaxErrors.UnexpectedEOF, "Expected '<' or ';'")
            return None, None

        if self.current_symbol.type == OperatorType.SEMICOLON:
            return True, (device_type, None)

        if not self.current_symbol.type == OperatorType.LEFT_ANGLE:
            self.throw_error(
                SyntaxErrors.UnexpectedToken, "Expected '<' or ';'"
            )
            return False, None

        if not self.get_next():
            self.throw_error(
                SyntaxErrors.UnexpectedEOF, "Expected number parameter"
            )
            return None, None

        if not self.current_symbol.type == ExternalSymbolType.NUMBERS:
            self.throw_error(
                SyntaxErrors.UnexpectedToken, "Expected number parameter"
            )
            return False, None

        parameter = int(self.names.get_name_string(self.current_symbol.id))

        if not self.get_next():
            self.throw_error(SyntaxErrors.UnexpectedEOF, "Expected '>'")
            return None, None

        if not self.current_symbol.type == OperatorType.RIGHT_ANGLE:
            self.throw_error(SyntaxErrors.UnexpectedToken, "Expected '>'")
            return False, None

        self.get_next()
        return True, (device_type, parameter)

    def parse_connection_block(self):
        """Parse CONNECTIONS block.

        EBNF syntax: "CONNECTIONS" , ":" , connection , { connection }
        Return:
        success - None(unexpected eof), False(syntax not ok), True(syntax ok)
        """
        if self.current_symbol is None:
            self.throw_error(
                SyntaxErrors.UnexpectedEOF, "Missing CONNECTIONS block"
            )
            return None

        if not self.current_symbol.type == KeywordType.CONNECTIONS:
            self.throw_error(
                SyntaxErrors.NoConnections, "Missing CONNECTIONS block"
            )
            return False

        if not self.get_next():
            self.throw_error(SyntaxErrors.UnexpectedEOF, "Expected ':'")
            return None

        if not self.current_symbol.type == OperatorType.COLON:
            self.throw_error(SyntaxErrors.UnexpectedToken, "Expected ':'")
            return False

        self.get_next()
        outcome = self.parse_connection_statement()
        if outcome is None:
            self.throw_error(
                SyntaxErrors.NoConnections, "Empty CONNECTIONS block"
            )
            return None
        if not outcome:
            if not self.skip_to_end_of_line():
                # there was end of file
                self.throw_error(
                    SyntaxErrors.NoConnections, "Empty CONNECTIONS block"
                )
                return None
            self.get_next()

        while (
            self.current_symbol is not None
            and self.current_symbol.type != KeywordType.MONITORS
        ):
            outcome = self.parse_connection_statement()
            if outcome is None or not outcome:
                if not self.skip_to_end_of_line():
                    # there was end of file
                    return None
                self.get_next()

        # end of file possible here
        return True

    def parse_connection_statement(self):
        """Parse connection statement from CONNECTIONS block.

        EBNF syntax: pin , "-" , pin , ";"

        Return:
        success - None(unexpected eof), False(syntax not ok), True(syntax ok)
        """
        if self.current_symbol is None:
            self.throw_error(
                SyntaxErrors.UnexpectedEOF,
                "Expected " "connection " "statement",
            )
            return None

        outcome, pin1 = self.parse_pin(connection_statement=True)
        if outcome is None or not outcome:
            self.syntax_valid = False
            return outcome

        if self.current_symbol is None:
            self.throw_error(SyntaxErrors.UnexpectedEOF, "Expected '-'")
            return None

        if not self.current_symbol.type == OperatorType.CONNECT:
            self.throw_error(SyntaxErrors.UnexpectedToken, "Expected '-'")
            return False

        self.get_next()

        outcome, pin2 = self.parse_pin(connection_statement=True)
        if outcome is None or not outcome:
            self.syntax_valid = False
            # TODO this is a bit hacky, change if time allows
            if self.errors.error_counter == 1:
                if (
                    self.errors.error_list[0].description
                    == "Expected '.', '-', or ';'"
                ):
                    self.errors.error_list[0] = SyntaxErrors.MissingSemicolon()
            return outcome

        if self.current_symbol is None:
            self.throw_error(SyntaxErrors.MissingSemicolon)
            return None

        if not self.current_symbol.type == OperatorType.SEMICOLON:
            self.throw_error(SyntaxErrors.UnexpectedToken, "Expected ';'")
            return False

        if self.syntax_valid:
            self.add_connection(pin1, pin2)
        self.get_next()
        return True

    def parse_pin(self, connection_statement):
        """Parse pin.

        EBNF syntax:    pin = ( in_pin | out_pin ) ;
        in_pin = ( device_name , "." , " I " , digit_excluding_zero , [digit])
        31 | ( device_name , "." , (" DATA " | " CLK " | " SET " | " CLEAR "));
        out_pin = device_name | ( device_name , "." , ( " Q " | " QBAR " ) ) ;

        Parameters: connection_statement = True if called from
                    parse_connection_statement
                    False if called from parse_monitors_statement

        Return: success, (out_pin, device_name, pin_name)
        success = None(unexpected eof), False(syntax not ok), True(syntax ok)
        out_pin = 'out' or 'in'
        device_name = string
        pin_name = None or string
        """
        if self.current_symbol is None:
            self.throw_error(
                SyntaxErrors.UnexpectedEOF, "Expected pin's device name"
            )
            return None, None

        if not self.current_symbol.type == ExternalSymbolType.IDENTIFIER:
            self.throw_error(
                SyntaxErrors.UnexpectedToken, "Expected pin's device name"
            )
            return False, None

        device_name = self.names.get_name_string(self.current_symbol.id)

        if not self.get_next():
            if connection_statement:
                self.throw_error(
                    SyntaxErrors.UnexpectedEOF, "Expected '.', '-', or ';'"
                )
            else:
                self.throw_error(
                    SyntaxErrors.UnexpectedEOF, "Expected ',' or ';'"
                )
            return None, None

        if connection_statement and self.current_symbol.type in [
            OperatorType.SEMICOLON,
            OperatorType.CONNECT,
            OperatorType.COMMA,
        ]:
            # out_pin = device_name
            return True, ("out", device_name, None)

        if not connection_statement and self.current_symbol.type in [
            OperatorType.COMMA,
            OperatorType.SEMICOLON,
        ]:
            # out_pin = device_name
            return True, ("out", device_name, None)

        if not self.current_symbol.type == OperatorType.DOT:
            if connection_statement:
                self.throw_error(
                    SyntaxErrors.UnexpectedToken, "Expected '.', '-', or ';'"
                )
            else:
                self.throw_error(
                    SyntaxErrors.UnexpectedToken, "Expected '.', ',' or ';'"
                )
            return False, None

        if not self.get_next():
            self.throw_error(SyntaxErrors.UnexpectedEOF, "Expected pin name")
            return None, None

        if (
            self.current_symbol.type in DTypeInputType
            or self.current_symbol.type == ExternalSymbolType.IDENTIFIER
        ):
            pin_name = self.names.get_name_string(self.current_symbol.id)
            self.get_next()
            return True, ("in", device_name, pin_name)

        if self.current_symbol.type in DTypeOutputType:
            pin_name = self.names.get_name_string(self.current_symbol.id)
            self.get_next()
            return True, ("out", device_name, pin_name)

        self.throw_error(SyntaxErrors.UnexpectedToken, "Expected pin name")
        return False, None

    def parse_monitors_block(self):
        """Parse MONITORS block.

        EBNF syntax: "MONITORS" , ":" , [ monitor_statement ]
        Return:
        success - None(unexpected eof), False(syntax not ok), True(syntax ok)
        """
        if self.current_symbol is None:
            # allowed to not have monitors block
            return True

        if not self.current_symbol.type == KeywordType.MONITORS:
            self.throw_error(
                SyntaxErrors.UnexpectedToken,
                "Expected MONITORS keyword or end of file",
            )
            return False

        if not self.get_next():
            self.throw_error(SyntaxErrors.UnexpectedEOF, "Expected ':'")
            return None

        if not self.current_symbol.type == OperatorType.COLON:
            self.throw_error(SyntaxErrors.UnexpectedToken, "Expected ':'")
            return False

        self.get_next()
        outcome, pins = self.parse_monitor_statement()
        if outcome is None or not outcome:
            return outcome

        if pins is None:
            return True

        # TODO set pins to monitor and check validity
        return True

    def parse_monitor_statement(self):
        """Parse monitor statement from MONITORS block.

        EBNF syntax: pin , { "," , pin } , ";"

        Return: success, pins = {(out_pin, device_name, pin_name)}
        success = None(unexpected eof), False(syntax not ok), True(syntax ok)
        out_pin = 'out' or 'in'
        device_name = string
        pin_name = None or string
        """
        if self.current_symbol is None:
            # end of file allowed here
            return True, None

        outcome, pin = self.parse_pin(connection_statement=False)
        if outcome is None or not outcome:
            self.syntax_valid = False
            return outcome, None

        pins = [pin]

        while (
            self.current_symbol is not None
            and self.current_symbol.type == OperatorType.COMMA
        ):
            self.get_next()
            outcome, pin = self.parse_pin(connection_statement=False)
            if outcome is None or not outcome:
                self.syntax_valid = False
                return outcome, None
            pins.append(pin)

        if self.current_symbol is None:
            self.throw_error(SyntaxErrors.MissingSemicolon)
            return None, None

        if not self.current_symbol.type == OperatorType.SEMICOLON:
            self.throw_error(
                SyntaxErrors.UnexpectedToken, "Expected ',' or ';'"
            )
            return None, None

        self.get_next()
        return True, pins

    def add_devices(self, device_names, gate_type, parameter):
        """Add devices parsed by parse_device_statement, add errors.

        Parameters:
            device_names - list of names of devices
            gate_type - DeviceType.AND|NAND|NOR|OR|XOR|DTYPE|CLOCK|SWITCH
            parameter - number or None
        """
        device_type = self.names.query(gate_type.value)
        if gate_type == DeviceType.SWITCH.value:
            if parameter == 0:
                parameter = self.devices.LOW
            elif parameter == 1:
                parameter = self.devices.HIGH
        for device_name in device_names:
            device_id = self.names.query(device_name)
            if self.devices is None:
                return
            error = self.devices.make_device(device_id, device_type, parameter)
            if error == self.devices.NO_ERROR:
                continue

            self.syntax_valid = False
            if error == self.devices.DEVICE_PRESENT:
                self.throw_error(SemanticErrors.NameClash)
            elif error == self.devices.QUALIFIER_PRESENT:
                self.throw_error(SyntaxErrors.UnexpectedParam)
            elif error == self.devices.NO_QUALIFIER:
                self.throw_error(SyntaxErrors.MissingParam)
            elif error == self.devices.INVALID_QUALIFIER:
                if gate_type == DeviceType.SWITCH:
                    self.throw_error(SyntaxErrors.InvalidSwitchParam)
                elif gate_type == DeviceType.CLOCK:
                    self.throw_error(SemanticErrors.InvalidClockParam)
                else:
                    self.throw_error(SemanticErrors.InvalidAndParam)
            elif error == self.devices.BAD_DEVICE:
                # should not happen as parser already checks this
                pass

    def add_connection(self, pin1, pin2):
        """Add connection between pin1 and pin2 if valid.

        Parameters: pin1 = (out_pin1, device_name1, pin_name1),
        pin2 = (out_pin2, device_name2, pin_name2)
        out_pin = 'out' or 'in'
        device_name = string
        pin_name = None or string
        """
        (out1, device_name, pin_name) = pin1
        device1_id = self.names.query(device_name)
        if pin_name is not None:
            pin1_id = self.names.query(pin_name)
        else:
            pin1_id = None

        (out2, device_name, pin_name) = pin2
        device2_id = self.names.query(device_name)
        if pin_name is not None:
            pin2_id = self.names.query(pin_name)
        else:
            pin2_id = None

        if self.network is None:
            return

        error = self.network.make_connection(
            device1_id, pin1_id, device2_id, pin2_id
        )
        if error == self.network.NO_ERROR:
            return

        self.syntax_valid = False

        if error == self.network.INPUT_TO_INPUT:
            self.throw_error(SemanticErrors.ConnectInToIn)
        elif error == self.network.OUTPUT_TO_OUTPUT:
            self.throw_error(SemanticErrors.ConnectOutToOut)
        elif error == self.network.INPUT_CONNECTED:
            self.throw_error(SemanticErrors.MultipleConnections)
        elif error == self.network.DEVICE_ABSENT:
            self.throw_error(SemanticErrors.UndefinedDevice)
        elif error == self.network.FIRST_PORT_ABSENT:
            if out1 == "out":
                self.throw_error(SemanticErrors.UndefinedOutPin)
            else:
                self.throw_error(SemanticErrors.UndefinedInPin)
        else:
            if out2 == "out":
                self.throw_error(SemanticErrors.UndefinedOutPin)
            else:
                self.throw_error(SemanticErrors.UndefinedInPin)

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        # TODO check for semantics and empty devices/connections
        success = self.parse_device_block()
        if success is None:
            # there was end of file
            return False
        elif not success:
            # syntax error in DEVICES block
            if not self.skip_to_block(KeywordType.CONNECTIONS):
                return False

        success = self.parse_connection_block()
        if success is None:
            # there was unexpected end of file
            return False
        elif not success:
            # syntax error in DEVICES block
            if not self.skip_to_block(KeywordType.MONITORS):
                return False

        success = self.parse_monitors_block()
        if success is None or not success:
            return False

        return True
