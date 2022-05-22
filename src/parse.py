"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""

from scanner import Symbol

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

    def throw_error(self):
        """Error"""
        pass

    def match_symbol(self, symbol_id: int):
        """Checks if current symbol matches expected"""
        if symbol_id == self.current_symbol.id:
            self.current_symbol = self.scanner.get_symbol()
        else:
            self.throw_error()

        


    def parse_devices_statement(self):
        """Parse definition statement from DEVICES block"""
        pass

    def parse_connection(self):
        """Parse connection statement from CONNECTIONS block"""

        pass

    def parse_monitor_statement(self):
        """Parse monitor statement from MONITORS block"""
        pass


    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.




        return True
