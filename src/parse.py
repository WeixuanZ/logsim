"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from custom_types import (
    KeywordType,
    DeviceType,
    ExternalSymbolType,
    Errors,
    OperatorType,
    SyntaxErrors,
)


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

    Methods
    -------
    parse_network(self):
        Parses the circuit definition file.
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

    def throw_error(self, error, description=None):
        """Add error with optional description to the list."""
        if description:
            error.set_description(description)
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
            print(self.current_symbol.type)
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
            # TODO check this in code when it gets to end of file
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
        if not self.current_symbol.type == KeywordType.DEVICES:
            # TODO check for typos later to give suggestions for improvement
            self.throw_error(SyntaxErrors.NoDevices, "Missing DEVICES block")
            return False

        if not self.get_next():
            return None

        if not self.current_symbol.type == OperatorType.COLON:
            self.throw_error(
                SyntaxErrors.UnexpectedToken, "Expected ':' after DEVICES"
            )
            return False

        if not self.get_next():
            return None

        # TODO could be a problem here with misspelling of CONNECTIONS
        while self.current_symbol.type != KeywordType.CONNECTIONS:
            success, device = self.parse_devices_statement()
            if not success:
                self.syntax_valid = False
                self.skip_to_end_of_line()  # current symbol should now be ;
            elif self.syntax_valid:
                # TODO add devices and pins, check validity of parameters
                (device_names, gate_type, parameter) = device
                pass
            if not self.get_next():  # move to start of new line
                return None
        return True

    def parse_devices_statement(self):
        """Parse device statement from DEVICES block.

        EBNF syntax: device_name ,{"," , device_name}, "=" ,device_type ,";"
        Return: success: True if valid statement
                         False if there was a syntax error
                         None if there was unexpected end of file
                device: (device_names, gate_type, parameter) when success=True
                        None otherwise
        """
        if self.current_symbol is None:
            return None, None

        device_names = []
        if self.current_symbol.type == ExternalSymbolType.IDENTIFIER:
            device_names.append(
                self.names.get_name_string(self.current_symbol.id)
            )
            if not self.get_next():
                return None, None
        else:
            self.throw_error(
                SyntaxErrors.UnexpectedToken, "Expected device name"
            )
            return False, None

        if self.current_symbol.type == OperatorType.COMMA:
            while self.current_symbol.type == OperatorType.COMMA:
                if not self.get_next():
                    return None, None
                if self.current_symbol.type == ExternalSymbolType.IDENTIFIER:
                    device_names.append(
                        self.names.get_name_string(self.current_symbol.id)
                    )
                    if not self.get_next():
                        return None, None
                else:
                    self.throw_error(
                        SyntaxErrors.UnexpectedToken, "Expected device name"
                    )
                    return False, None
        elif not self.current_symbol.type == OperatorType.EQUAL:
            self.throw_error(
                SyntaxErrors.UnexpectedToken, "Expected ',' or '='"
            )
            return False, None

        if not self.get_next():
            return None, None

        success, device_type = self.parse_device_type()
        if success is None:
            return None, None
        elif not success:
            return False, None

        (dtype, parameter) = device_type

        if not self.current_symbol.type == OperatorType.SEMICOLON:
            self.throw_error(SyntaxErrors.MissingSemicolon)
            return False, None, None

        return True, (device_names, dtype, parameter)

    def parse_device_type(self):
        """Parse device type.

        EBNF syntax: device_type = ( "CLOCK", parameter )
            | ( "SWITCH", "<" , ( "0" | "1" ) , ">" )
            | ( ( "AND" | "NAND" | "OR" | "NOR" ), parameter )
            | "XOR"
            | "D_TYPE" ;
            parameter = "<" , digit , { digit } , ">" ;
        """
        if self.current_symbol is None:
            return None, None
        if self.current_symbol.type in DeviceType:
            device_type = self.current_symbol.type
            if not self.get_next():
                return None, None
        else:
            self.throw_error(
                SyntaxErrors.UnexpectedToken, "Expected device type"
            )
            return False, None

        if self.current_symbol.type == OperatorType.SEMICOLON:
            return True, (device_type, None)

        if not self.current_symbol.type == OperatorType.LEFT_ANGLE:
            self.throw_error(
                SyntaxErrors.UnexpectedToken, "Expected '<' or ';'"
            )
            return False, None

        if not self.get_next():
            return None, None

        if self.current_symbol.type == ExternalSymbolType.NUMBERS:
            parameter = int(self.names.get_name_string(self.current_symbol.id))

            if not self.get_next():
                return None, None

            if not self.current_symbol.type == OperatorType.RIGHT_ANGLE:
                self.throw_error(SyntaxErrors.UnexpectedToken, "Expected '>'")
                return False, None

            if not self.get_next():
                self.throw_error(SyntaxErrors.MissingSemicolon)
                return None, None

            return True, (device_type, parameter)

        self.throw_error(
            SyntaxErrors.UnexpectedToken, "Expected number parameter"
        )
        return False, None

    def parse_connection_block(self):
        """Parse CONNECTIONS block.

        EBNF syntax: "CONNECTIONS" , ":" , connection , { connection }
        Return: True if successful parsing,
        False if there was an error
        None if there was (unexpected) end of file
        """
        if not self.current_symbol.type == KeywordType.CONNECTIONS:
            # TODO check for typos later
            self.throw_error(
                SyntaxErrors.NoDevices, "Missing CONNECTIONS block"
            )
            return False

        if not self.get_next():
            return None

        if not self.current_symbol.type == OperatorType.COLON:
            self.throw_error(
                SyntaxErrors.UnexpectedToken, "Expected ':' after CONNECTIONS"
            )
            return False

        if not self.get_next():
            return None

        # TODO could be a problem here with misspelling of MONITORS
        while self.current_symbol.type != KeywordType.MONITORS:
            success, connections = self.parse_connection_statement()
            if not success:
                self.syntax_valid = False
                self.skip_to_end_of_line()  # current symbol should now be ;
            elif self.syntax_valid:
                # TODO add a connection, check validity of parameters
                pass
            if not self.get_next():  # move to start of new line
                # end of file, allowed by syntax
                return None
        return True

    def parse_connection_statement(self):
        """Parse connection statement from CONNECTIONS block.

        EBNF syntax: pin , "-" , pin , ";"
        """
        pass

    def parse_monitors_block(self):
        """Parse MONITORS block.

        EBNF syntax: "MONITORS" , ":" , [ monitor_statement ]
        """
        pass

    def parse_monitor_statement(self):
        """Parse monitor statement from MONITORS block.

        EBNF syntax: pin , { "," , pin } , ";"
        """
        pass

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        # TODO check for semantics and empty devices/connections

        success = self.parse_device_block()
        if success is None:
            # there was end of file
            self.syntax_valid = False
            self.throw_error(SyntaxErrors.NoDevices, "Missing DEVICES block")
        elif not success:
            # syntax error in DEVICES block
            self.syntax_valid = False
            self.skip_to_block(KeywordType.CONNECTIONS)

        success = self.parse_connection_block()
        if success is None:
            # there was unexpected end of file
            self.syntax_valid = False
            self.throw_error(
                SyntaxErrors.NoConnections, "Missing CONNECTIONS block"
            )
        elif not success:
            # syntax error in DEVICES block
            self.syntax_valid = False
            # TODO check if end of file, could be there is no MONITORS block
            self.skip_to_block(KeywordType.MONITORS)

        # TODO: move the rest to parse_monitors_block
        self.get_next()

        # TODO could be a problem here with misspelling of MONITORS
        while self.current_symbol.type != KeywordType.MONITORS:
            success, connection = self.parse_connection_statement()
            # TODO check validity of connection
            if not success:
                self.syntax_valid = False
                self.skip_to_block(KeywordType.MONITORS)
                break

        return True
