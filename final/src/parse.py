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
    errors:
        instance of the exceptions.Errors() class

    SPHINX-IGNORE
    Public Methods
    --------------
    parse_network(self):
        Parses the circuit definition file.
    SPHINX-IGNORE
    """

    def __init__(
        self, names, devices, network, monitors, scanner, errors: Errors
    ):
        """Initialise constants."""
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.scanner = scanner
        self.errors = errors

        # initialize by getting first symbol from scanner
        self.current_symbol = scanner.get_symbol()
        self.previous_symbol = None

        # build the network while this is True, then just parse for errors
        self.syntax_valid = True

    def _throw_error(
        self, error_type, description=None, prev_word=False, show_cursor=True
    ):
        """Add error with optional description to the list."""
        error = error_type(description)
        if prev_word:
            error.symbol = self.previous_symbol
            end_of_word = True
        else:
            error.symbol = self.current_symbol
            end_of_word = False
        self.errors.add_error(
            error, show_end_of_word=end_of_word, show_cursor=show_cursor
        )

    def _get_next(self):
        """Get next symbol from scanner and set it as current symbol.

        Return: False if there is end of file,
                True if new symbol was successfully retrieved
        """
        self.previous_symbol = (
            self.current_symbol
            if self.current_symbol is not None
            else self.previous_symbol
        )
        self.current_symbol = self.scanner.get_symbol()
        # check for end of file
        if self.current_symbol is None:
            return False
        return True

    def _skip_to_end_of_line(self):
        """Update self.current_symbol until end of line SEMICOLON is reached.

        Return: False if there was unexpected end of file
                True if moved to end of line
                None if found the next block, i.e.
        """
        if self.current_symbol is None:
            return False
        while self.current_symbol.type != OperatorType.SEMICOLON:
            if self.current_symbol.type in KeywordType:
                return None
            if not self._get_next():
                return False
        return True

    def _skip_to_block(self, keyword: KeywordType):
        """Skip all symbols until it gets to Keyword (eg CONNECTIONS).

        Return: False if there is unexpected end of file
                True if moved to block Keyword
        """
        if self.current_symbol is None:
            return False
        while self.current_symbol.type != keyword:
            if not self._get_next():
                return False
        return True

    def _parse_device_block(self):
        """Parse DEVICES block.

        EBNF syntax: "DEVICES" , ":" , device_definition , {device_definition}

        Return: True if successful parsing,
        False if there was an error,
        None if there was (unexpected) end of file
        """
        if self.current_symbol is None:
            self._throw_error(
                SyntaxErrors.UnexpectedEOF, _("Missing DEVICES block"), True
            )
            return None

        if not self.current_symbol.type == KeywordType.DEVICES:
            # TODO check for typos later to give suggestions for improvement
            self._throw_error(
                SyntaxErrors.NoDevices, _("Missing DEVICES block")
            )
            return False

        if not self._get_next():
            self._throw_error(
                SyntaxErrors.UnexpectedEOF,
                _("Expected ':' after DEVICES"),
                True,
            )
            return None

        if not self.current_symbol.type == OperatorType.COLON:
            self._throw_error(
                SyntaxErrors.UnexpectedToken, _("Expected ':' after DEVICES")
            )
            return False

        self._get_next()
        outcome = self._parse_devices_statement()
        if outcome is None:
            self.syntax_valid = False
            self._throw_error(SyntaxErrors.NoDevices, _("Empty DEVICES block"))
            return None
        if not outcome:
            self.syntax_valid = False
            outcome = self._skip_to_end_of_line()
            if outcome is None:
                # reached another block
                return False
            elif not outcome:
                # there was end of file
                self._throw_error(
                    SyntaxErrors.NoDevices, _("Empty DEVICES block")
                )
                return None
            self._get_next()

        while (
            self.current_symbol is not None
            and self.current_symbol.type != KeywordType.CONNECTIONS
        ):
            success = self._parse_devices_statement()
            if success is None or not success:
                self.syntax_valid = False
                outcome = self._skip_to_end_of_line()
                if outcome is None:
                    return False
                elif not outcome:
                    # unexpected end of file
                    return success
                self._get_next()
        return True

    def _parse_devices_statement(self):
        """Parse device statement from DEVICES block.

        EBNF syntax: device_name ,{"," , device_name}, "=" ,device_type ,";"

        Return: success, (device_names, gate_type, parameter)
        success = None(unexpected eof), False(syntax not ok), True(syntax ok)
        device_names = list of strings
        gate_type = 'AND'|'NAND'|'OR'|'NOR'|'XOR'|'CLOCK'|'SWITCH'|'DTYPE'
        parameter = None or number
        """
        if self.current_symbol is None:
            self._throw_error(
                SyntaxErrors.UnexpectedEOF,
                _("Expected device definition"),
                True,
            )
            return None

        if not self.current_symbol.type == ExternalSymbolType.IDENTIFIER:
            self._throw_error(
                SyntaxErrors.UnexpectedToken, _("Expected device name")
            )
            return False

        device_names = [self.names.get_name_string(self.current_symbol.id)]

        self._get_next()

        while (
            self.current_symbol is not None
            and self.current_symbol.type == OperatorType.COMMA
        ):
            if not self._get_next():
                self._throw_error(
                    SyntaxErrors.UnexpectedEOF, _("Expected device name"), True
                )
                return None
            if not self.current_symbol.type == ExternalSymbolType.IDENTIFIER:
                self._throw_error(
                    SyntaxErrors.UnexpectedToken, _("Expected device name")
                )
                return False
            device_names.append(
                self.names.get_name_string(self.current_symbol.id)
            )
            self._get_next()

        if self.current_symbol is None:
            self._throw_error(
                SyntaxErrors.UnexpectedEOF, _("Expected ',' or '='"), True
            )
            return None

        if not self.current_symbol.type == OperatorType.EQUAL:
            self._throw_error(
                SyntaxErrors.UnexpectedToken, _("Expected ',' or '='")
            )
            return False

        self._get_next()

        success, device_type = self._parse_device_type()
        if success is None or not success:
            return success

        (dtype, parameter) = device_type

        if self.current_symbol is None:
            self._throw_error(SyntaxErrors.MissingSemicolon)
            return None

        if not self.current_symbol.type == OperatorType.SEMICOLON:
            self._throw_error(
                SyntaxErrors.UnexpectedToken, _("Expected ';'"), prev_word=True
            )
            return False

        if self.syntax_valid:
            self._add_devices(device_names, dtype, parameter)
        self._get_next()
        return True

    def _parse_device_type(self):
        """Parse device type.

        EBNF syntax: device_type = ( "CLOCK", parameter )
            | ( "SWITCH", "<" , ( "0" | "1" ) , ">" )
            | ( ( "AND" | "NAND" | "OR" | "NOR" ), parameter )
            | "NOT"
            | "XOR"
            | "D_TYPE" ;
            parameter = "<" , digit , { digit } , ">" ;

        Return: success, (device_type, parameter)
        success = None(unexpected eof), False(syntax not ok), True(syntax ok)
        device_type = 'AND'|'NAND'|'OR'|'NOR'|'NOT'|
                      'XOR'|'CLOCK'|'SWITCH'|'DTYPE'
        parameter = None or number
        """
        if self.current_symbol is None:
            self._throw_error(
                SyntaxErrors.UnexpectedEOF, _("Expected device type"), True
            )
            return None, None

        if self.current_symbol.type not in DeviceType:
            self._throw_error(
                SyntaxErrors.UnexpectedToken, _("Expected device type")
            )
            return False, None

        device_type = self.current_symbol.type

        if not self._get_next():
            self._throw_error(
                SyntaxErrors.UnexpectedEOF, _("Expected '<' or ';'"), True
            )
            return None, None

        if self.current_symbol.type == OperatorType.SEMICOLON:
            return True, (device_type, None)

        if not self.current_symbol.type == OperatorType.LEFT_ANGLE:
            self._throw_error(
                SyntaxErrors.UnexpectedToken,
                _("Expected '<' or ';'"),
                prev_word=True,
            )
            return False, None

        if not self._get_next():
            self._throw_error(
                SyntaxErrors.UnexpectedEOF,
                _("Expected number parameter"),
                True,
            )
            return None, None

        if not self.current_symbol.type == ExternalSymbolType.NUMBERS:
            self._throw_error(
                SyntaxErrors.UnexpectedToken, _("Expected number parameter")
            )
            return False, None

        parameter = int(self.names.get_name_string(self.current_symbol.id))

        if not self._get_next():
            self._throw_error(
                SyntaxErrors.UnexpectedEOF, _("Expected '>'"), True
            )
            return None, None

        if not self.current_symbol.type == OperatorType.RIGHT_ANGLE:
            self._throw_error(SyntaxErrors.UnexpectedToken, _("Expected '>'"))
            return False, None

        self._get_next()
        return True, (device_type, parameter)

    def _parse_connection_block(self):
        """Parse CONNECTIONS block.

        EBNF syntax: "CONNECTIONS" , ":" , connection , { connection }
        Return:
        success - None(unexpected eof), False(syntax not ok), True(syntax ok)
        """
        if self.current_symbol is None:
            self._throw_error(
                SyntaxErrors.UnexpectedEOF,
                _("Missing CONNECTIONS block"),
                True,
            )
            return None

        if not self.current_symbol.type == KeywordType.CONNECTIONS:
            self._throw_error(
                SyntaxErrors.NoConnections, _("Missing CONNECTIONS block")
            )
            return False

        if not self._get_next():
            self._throw_error(
                SyntaxErrors.UnexpectedEOF, _("Expected ':'"), True
            )
            return None

        if not self.current_symbol.type == OperatorType.COLON:
            self._throw_error(SyntaxErrors.UnexpectedToken, _("Expected ':'"))
            return False

        self._get_next()
        outcome = self._parse_connection_statement()
        if outcome is None:
            self._throw_error(
                SyntaxErrors.NoConnections, _("Empty CONNECTIONS block")
            )
            return None
        if not outcome:
            out = self._skip_to_end_of_line()
            if out is None:
                return False
            elif not out:
                # there was end of file
                self._throw_error(
                    SyntaxErrors.NoConnections, _("Empty CONNECTIONS block")
                )
                return None
            self._get_next()

        while (
            self.current_symbol is not None
            and self.current_symbol.type != KeywordType.MONITORS
        ):
            outcome = self._parse_connection_statement()
            if outcome is None or not outcome:
                out = self._skip_to_end_of_line()
                if out is None:
                    return False
                elif not out:
                    # there was end of file
                    return None
                self._get_next()
        # end of file possible here
        return True

    def _parse_connection_statement(self):
        """Parse connection statement from CONNECTIONS block.

        EBNF syntax: pin , "-" , pin , ";"

        Return:
        success - None(unexpected eof), False(syntax not ok), True(syntax ok)
        """
        if self.current_symbol is None:
            self._throw_error(
                SyntaxErrors.UnexpectedEOF,
                _("Expected connection statement"),
                True,
            )
            return None

        outcome, pin1 = self._parse_pin(connection_statement=True)
        if outcome is None or not outcome:
            self.syntax_valid = False
            return outcome

        if self.current_symbol is None:
            self._throw_error(
                SyntaxErrors.UnexpectedEOF, _("Expected '-'"), True
            )
            return None

        if not self.current_symbol.type == OperatorType.CONNECT:
            self._throw_error(SyntaxErrors.UnexpectedToken, _("Expected '-'"))
            return False

        self._get_next()

        outcome, pin2 = self._parse_pin(connection_statement=True)
        if outcome is None or not outcome:
            self.syntax_valid = False
            # TODO this is a bit hacky, change if time allows
            if self.errors.error_counter == 1:
                if self.errors.error_list[0].description == _(
                    "Expected '.', '-', or ';'"
                ):
                    self.errors.error_list[0] = SyntaxErrors.MissingSemicolon()
            return outcome

        if self.current_symbol is None:
            self._throw_error(SyntaxErrors.MissingSemicolon)
            return None

        if not self.current_symbol.type == OperatorType.SEMICOLON:
            self._throw_error(
                SyntaxErrors.UnexpectedToken, _("Expected ';'"), prev_word=True
            )
            return False

        if self.syntax_valid:
            self._add_connection(pin1, pin2)
        self._get_next()
        return True

    def _parse_pin(self, connection_statement):
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
            self._throw_error(
                SyntaxErrors.UnexpectedEOF,
                _("Expected pin's device name"),
                True,
            )
            return None, None

        if not self.current_symbol.type == ExternalSymbolType.IDENTIFIER:
            self._throw_error(
                SyntaxErrors.UnexpectedToken, _("Expected pin's device name")
            )
            return False, None

        device_name = self.names.get_name_string(self.current_symbol.id)

        if not self._get_next():
            if connection_statement:
                self._throw_error(
                    SyntaxErrors.UnexpectedEOF,
                    _("Expected '.', '-', or ';'"),
                    True,
                )
            else:
                self._throw_error(
                    SyntaxErrors.UnexpectedEOF, _("Expected ',' or ';'"), True
                )
            return None, None

        if connection_statement and self.current_symbol.type in [
            OperatorType.SEMICOLON,
            OperatorType.CONNECT,
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
                self._throw_error(
                    SyntaxErrors.UnexpectedToken,
                    _("Expected '.', '-', or ';'"),
                )
            else:
                self._throw_error(
                    SyntaxErrors.UnexpectedToken, _("Expected '.', ',' or ';'")
                )
            return False, None

        if not self._get_next():
            self._throw_error(
                SyntaxErrors.UnexpectedEOF, _("Expected pin name"), True
            )
            return None, None

        if (
            self.current_symbol.type in DTypeInputType
            or self.current_symbol.type == ExternalSymbolType.IDENTIFIER
        ):
            pin_name = self.names.get_name_string(self.current_symbol.id)
            self._get_next()
            return True, ("in", device_name, pin_name)

        if self.current_symbol.type in DTypeOutputType:
            pin_name = self.names.get_name_string(self.current_symbol.id)
            self._get_next()
            return True, ("out", device_name, pin_name)

        self._throw_error(SyntaxErrors.UnexpectedToken, _("Expected pin name"))
        return False, None

    def _parse_monitors_block(self):
        """Parse MONITORS block.

        EBNF syntax: "MONITORS" , ":" , [ monitor_statement ]
        Return:
        success - None(unexpected eof), False(syntax not ok), True(syntax ok)
        """
        if self.current_symbol is None:
            # allowed to not have monitors block
            return True

        if not self.current_symbol.type == KeywordType.MONITORS:
            self._throw_error(
                SyntaxErrors.UnexpectedToken,
                _("Expected MONITORS keyword or end of file"),
            )
            return False

        if not self._get_next():
            self._throw_error(
                SyntaxErrors.UnexpectedEOF, _("Expected ':'"), True
            )
            return None

        if not self.current_symbol.type == OperatorType.COLON:
            self._throw_error(SyntaxErrors.UnexpectedToken, _("Expected ':'"))
            return False

        self._get_next()
        outcome = self._parse_monitor_statement()
        if outcome is None or not outcome:
            return outcome

        return True

    def _parse_monitor_statement(self):
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
            return True

        outcome, pin = self._parse_pin(connection_statement=False)
        if outcome is None or not outcome:
            self.syntax_valid = False
            return outcome

        pins = [pin]

        while (
            self.current_symbol is not None
            and self.current_symbol.type == OperatorType.COMMA
        ):
            self._get_next()
            outcome, pin = self._parse_pin(connection_statement=False)
            if outcome is None or not outcome:
                self.syntax_valid = False
                return outcome
            pins.append(pin)

        if self.current_symbol is None:
            self._throw_error(SyntaxErrors.MissingSemicolon)
            return None

        if not self.current_symbol.type == OperatorType.SEMICOLON:
            self._throw_error(
                SyntaxErrors.UnexpectedToken, _("Expected ',' or ';'")
            )
            return None

        if pins is None:
            return True

        if self.syntax_valid:
            self._add_monitors(pins)
        self._get_next()
        return True

    def _add_devices(self, device_names, gate_type, parameter):
        """Add devices parsed by parse_devices_statement, throws errors.

        Parameters
        ------------
        device_names
            list of names of devices
        gate_type
            DeviceType.AND|NAND|NOR|NOT|OR|XOR|DTYPE|CLOCK|SWITCH
        parameter
            number or None
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
                self._throw_error(
                    SemanticErrors.NameClash,
                    _("Device with this name already exists"),
                    show_cursor=False,
                )
            elif error == self.devices.QUALIFIER_PRESENT:
                self._throw_error(
                    SyntaxErrors.UnexpectedParam,
                    _("Device of this type does not require a parameter"),
                    show_cursor=False,
                )
            elif error == self.devices.NO_QUALIFIER:
                self._throw_error(
                    SyntaxErrors.MissingParam,
                    _("Device of this type requires a parameter"),
                    show_cursor=False,
                )
            elif error == self.devices.INVALID_QUALIFIER:
                if gate_type == DeviceType.SWITCH:
                    self._throw_error(
                        SyntaxErrors.InvalidSwitchParam,
                        _("Parameter for a SWITCH device can only be 0 or 1"),
                        show_cursor=False,
                    )
                elif gate_type == DeviceType.CLOCK:
                    self._throw_error(
                        SemanticErrors.InvalidClockParam,
                        _("Parameter for a CLOCK device has to be > 0"),
                        show_cursor=False,
                    )
                else:
                    self._throw_error(
                        SemanticErrors.InvalidAndParam,
                        _("Gates can only have 1-16 inputs"),
                        show_cursor=False,
                    )
            elif error == self.devices.BAD_DEVICE:
                # should not happen as parser already checks this
                pass

    def _add_connection(self, pin1, pin2):
        """Add connection between pin1 and pin2 if valid, throw errors if not.

        Parameters
        ----------
        pin1
            tuple (out_pin1, device_name1, pin_name1),
        pin2
            tuple (out_pin2, device_name2, pin_name2)
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
            self._throw_error(SemanticErrors.ConnectInToIn, show_cursor=False)
        elif error == self.network.OUTPUT_TO_OUTPUT:
            self._throw_error(
                SemanticErrors.ConnectOutToOut, show_cursor=False
            )
        elif error == self.network.INPUT_CONNECTED:
            self._throw_error(
                SemanticErrors.MultipleConnections, show_cursor=False
            )
        elif error == self.network.DEVICE_ABSENT:
            self._throw_error(
                SemanticErrors.UndefinedDevice, show_cursor=False
            )
        elif error == self.network.FIRST_PORT_ABSENT:
            if out1 == "out":
                self._throw_error(
                    SemanticErrors.UndefinedOutPin, show_cursor=False
                )
            else:
                self._throw_error(
                    SemanticErrors.UndefinedInPin, show_cursor=False
                )
        else:
            if out2 == "out":
                self._throw_error(
                    SemanticErrors.UndefinedOutPin, show_cursor=False
                )
            else:
                self._throw_error(
                    SemanticErrors.UndefinedInPin, show_cursor=False
                )

    def _add_monitors(self, pins):
        """Add monitors pins, throw errors if not possible.

        Parameters
        -----------
        pins
            list of tuples (out, device_name, pin_name)
        """
        for pin in pins:
            (out, device_name, pin_name) = pin
            if out == "in":
                self._throw_error(
                    SemanticErrors.MonitorInputPin, show_cursor=False
                )
                self.syntax_valid = False
                return

            device_id = self.names.query(device_name)
            if pin_name is not None:
                pin_id = self.names.query(pin_name)
            else:
                pin_id = None

            if self.monitors is not None:
                error = self.monitors.make_monitor(device_id, pin_id)
                if error == self.monitors.NO_ERROR:
                    continue
                if error == self.monitors.MONITOR_PRESENT:
                    # this is just a warning
                    self._throw_error(
                        SemanticErrors.MonitorSamePin, show_cursor=False
                    )
                    continue

                self.syntax_valid = False
                if error == self.monitors.NOT_OUTPUT:
                    self._throw_error(
                        SemanticErrors.MonitorInputPin, show_cursor=False
                    )
                if error == self.monitors.MONITOR_PRESENT:
                    self._throw_error(
                        SemanticErrors.MonitorSamePin, show_cursor=False
                    )
                if error == self.network.DEVICE_ABSENT:
                    self._throw_error(
                        SemanticErrors.UndefinedDevice, show_cursor=False
                    )

    def parse_network(self):
        """Parse the circuit definition file.

        Returns: True if parsing was successful and simulation should run,
        False if there were errors.
        """
        success = self._parse_device_block()
        if success is None:
            # there was end of file
            self.syntax_valid = False
            return False
        elif not success:
            # syntax error in DEVICES block
            self.syntax_valid = False
            if not self._skip_to_block(KeywordType.CONNECTIONS):
                return False

        success = self._parse_connection_block()
        if success is None:
            # there was unexpected end of file
            self.syntax_valid = False
            return False
        elif not success:
            # syntax error in DEVICES block
            self.syntax_valid = False
            if not self._skip_to_block(KeywordType.MONITORS):
                return False

        # check if all inputs are connected
        if self.syntax_valid:
            if self.network is not None and not self.network.check_network():
                self._throw_error(
                    SemanticErrors.FloatingInput,
                    _("Some pins are not connected"),
                )
                self.syntax_valid = False

        success = self._parse_monitors_block()
        if success is None or not success:
            self.syntax_valid = False
            return False

        return self.syntax_valid
