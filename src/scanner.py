"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""

from names import Names
from custom_types import SymbolType


class Symbol:
    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    TODO

    Methods
    -------
    TODO
    """

    def __init__(self, symbol_type: SymbolType):
        """Initialise symbol properties."""
        self.type = symbol_type
        self.id = None
        self.lineno = None
        self.colno = None

    def __repr__(self):
        """Customised repr of Symbol objects."""
        return f"Symbol({self.type}, {self.id}, position={self.lineno}:{self.colno})"


class Scanner:
    """Read circuit definition file and translate the characters into symbols.

    Once supplied with the path to a valid definition file, the scanner
    translates the sequence of characters in the definition file into symbols
    that the parser can use. It also skips over comments and irrelevant
    formatting characters, such as spaces and line breaks.

    Parameters
    ----------
    path:
        path to the circuit definition file.
    names:
        instance of the names.Names() class.

    Methods
    -------
    get_symbol(self):
        Translates the next sequence of characters into a symbol and returns the symbol.
    """

    def __init__(self, path: str, names: Names):
        """Open specified file and initialise reserved words and IDs."""

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
