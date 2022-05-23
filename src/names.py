"""Map variable names and string names to unique integers.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

Classes
-------
Names - maps variable names and string names to unique integers.
"""
from typing import Union

from custom_types import (
    ReservedSymbolType,
    ExternalSymbolType,
)


class Names:
    """Map variable names and string names to unique integers.

    This class deals with storing grammatical keywords and user-defined words,
    and their corresponding name IDs, which are internal indexing integers. It
    provides functions for looking up either the name ID or the name string.
    It also keeps track of the number of error codes defined by other classes,
    and allocates new, unique error codes on demand.

    Parameters
    ----------
    No parameters.

    SPHINX-IGNORE
    Public Methods
    --------------
    unique_error_codes(self, num_error_codes: int):
        Returns a list of unique integer error codes.
    query(self, name_string: str):
        Returns the corresponding name ID for the name string.
        Returns None if the string is not present.
    lookup(self, name_string_list: list):
        Returns a list of name IDs for each name string.
        Adds a name if not already present.
    get_name_string(self, name_id: int):
        Returns the corresponding name string for the name ID.
        Returns None if the ID is not present.
    get_name_type(self, name_id: int):
        Returns the corresponding name type for the name ID.
        Returns None if the ID is not present.
    SPHINX-IGNORE
    """

    def __init__(self):
        """Initialise names list."""
        self.error_code_count = 0  # how many error codes have been declared
        self._name_count = 0
        self._name_to_id_table = dict()
        self._id_to_name_table = dict()
        self._add_reserved_name()

        self._name_to_reserved_type_table = ReservedSymbolType.__members__

    def _add_reserved_name(self) -> None:
        """Add reserved names to the table.

        This should be called upon initialization of the object.
        """
        list(map(self._query_or_add, ReservedSymbolType.values()))

    def unique_error_codes(self, num_error_codes: int) -> list:
        """Return a list of unique integer error codes."""
        if not isinstance(num_error_codes, int):
            raise TypeError("Expected num_error_codes to be an integer.")
        if num_error_codes < 0:
            raise ValueError("num_error_codes must be at least zero")

        self.error_code_count += num_error_codes
        return list(
            range(
                self.error_code_count - num_error_codes, self.error_code_count
            )
        )

    def query(self, name_string: str) -> Union[int, None]:
        """Return the corresponding name ID for name string.

        If the name string is not present in the names list, return None.
        """
        if not isinstance(name_string, str):
            raise TypeError("name_string must be a string")

        return self._name_to_id_table.get(name_string)

    def _query_or_add(self, name_string: str) -> int:
        """Return the corresponding name ID for name string.

        If the name string is not present in the name list, add it.
        """
        if not isinstance(name_string, str):
            raise TypeError("name_string must be a string")

        if name_string not in self._name_to_id_table:
            self._name_to_id_table[name_string] = self._name_count
            self._id_to_name_table[self._name_count] = name_string
            self._name_count += 1

        return self._name_to_id_table.get(name_string)

    def lookup(self, name_string_list: list) -> list:
        """Return a list of name IDs for each name string in name_string_list.

        If the name string is not present in the names list, add it.
        """
        if not isinstance(name_string_list, list):
            raise TypeError("name_string_list must be a list")

        return list(map(self._query_or_add, name_string_list))

    def get_name_string(self, name_id: int) -> Union[str, None]:
        """Return the corresponding name string for name_id.

        If the name_id is not an index in the names list, return None.
        """
        if not isinstance(name_id, int):
            raise TypeError("name_id must be an integer")
        if name_id < 0:
            raise ValueError("name_id must be at least 0")

        return self._id_to_name_table.get(name_id)

    def get_name_type(
        self, name_id: int
    ) -> Union[ReservedSymbolType, ExternalSymbolType, None]:
        """Return the corresponding type for name_id.

        If the name_id is not an index in the names list, return None.
        """
        if not isinstance(name_id, int):
            raise TypeError("name_id must be an integer")
        if name_id < 0:
            raise ValueError("name_id must be at least 0")

        name_string = self.get_name_string(name_id)
        if name_string is None:
            return None

        if name_string in self._name_to_reserved_type_table:
            return self._name_to_reserved_type_table[name_string]

        if name_string.isnumeric():
            return ExternalSymbolType.NUMBERS

        return ExternalSymbolType.EXTERNAL_NAMES
