"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
"""

from typing import Union, Tuple, Type
from itertools import accumulate, dropwhile, starmap
import logging

from names import Names
from custom_types import ReservedSymbolType, ExternalSymbolType


class Symbol:
    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    TODO

    Methods
    -------
    TODO
    """

    def __init__(
        self,
        symbol_type: Union[ReservedSymbolType, ExternalSymbolType],
        symbol_id: int,
        lineno: int,
        colno: int,
    ):
        """Initialise symbol properties."""
        self.type = symbol_type
        self.id = symbol_id
        self.lineno = lineno
        self.colno = colno

    def __repr__(self):
        """Customised repr of Symbol objects."""
        return (
            f"Symbol({self.type}, {self.id},"
            f"position={self.lineno}:{self.colno})"
        )


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

    SPHINX-IGNORE
    Public Methods
    --------------
    TODO
    get_symbol(self):
        Translates the next sequence of characters into a symbol
        and returns the symbol.
    SPHINX-IGNORE
    """

    class EOF:
        """Symbol indicating the end of file."""

        pass

    def __init__(self, path: str, names: Names):
        """Open specified file and initialise reserved words and IDs."""
        self.path = path
        self.names = names

        # >= 0, <= file_content_length, at EOF when = file_content_length
        self._pointer_pos = 0
        self._line_lengths = []
        self._file_content = ""

        with open(self.path, "r") as file:
            for line in file.readlines():
                self._line_lengths.append(len(line))
                self._file_content += line
        self._file_content_length = len(self._file_content)

        # the pos of last character on the line
        self._line_end_pos = list(accumulate(self._line_lengths, initial=-1))[
            1:
        ]
        # EOF
        self._line_end_pos[-1] += 1
        self._line_lengths[-1] += 1

    @property
    def file_content(self) -> str:
        """Content of the file."""
        return self._file_content

    @property
    def pointer_pos(self) -> Union[int, Type[EOF]]:
        """Return current pointer position in the file.

        It is zero-indexed and protected. If the pointer is at end of file,
        Scanner.EOF will be returned.
        """
        return (
            self._pointer_pos
            if self._pointer_pos < self._file_content_length
            else Scanner.EOF
        )

    @property
    def pointer_lineno(self) -> int:
        """Return current line number of the pointer.

        It is zero-indexed and protected.
        """
        return self.get_lineno_colno(self._pointer_pos)[0]

    @property
    def pointer_colno(self) -> int:
        """Return current column number of the pointer.

        It is zero-indexed and protected. It can be one larger than the length
        of the line if the pointer is on the last line, which denotes the end
        of file is reached.
        """
        return self.get_lineno_colno(self._pointer_pos)[1]

    @property
    def pointer(self) -> Tuple[int, int, int]:
        """Return current pointer position, line number, and column number."""
        lineno, colno = self.get_lineno_colno(self._pointer_pos)
        return self._pointer_pos, lineno, colno

    @staticmethod
    def _check_is_natural_number(num, num_name):
        """Check if a number is a natural number.

        The second argument is the name of the number used in error messages.
        """
        if not isinstance(num, int):
            raise TypeError(f"{num_name} must be an integer")
        if num < 0:
            raise ValueError(f"{num_name} must be at least zero")

    def get_lineno_colno(self, pos: int) -> Tuple[int, int]:
        """Get the line and column numbers of a position in file.

        The position is zero-indexed. It is allowed to be one greater than the
        length of the file, which denotes end of file.
        """
        Scanner._check_is_natural_number(pos, "Pointer position")
        # allowing going past end by 1 for eof
        if pos > self._file_content_length:
            raise ValueError("Pointer position larger than input file length")

        # noinspection PyTypeChecker
        return next(
            starmap(
                lambda lineno, line_end_pos: (
                    lineno,
                    pos - line_end_pos + self._line_lengths[lineno] - 1,
                ),
                dropwhile(
                    lambda lineno_end_pos: lineno_end_pos[1] < pos,
                    enumerate(self._line_end_pos),
                ),
            )
        )

    def get_line_by_lineno(self, lineno: int) -> str:
        """Get the content of a line using the line number."""
        Scanner._check_is_natural_number(lineno, "Line number")
        if lineno > len(self._line_lengths) - 1:
            raise ValueError(
                "Line number larger than the number of lines in file"
            )

        if lineno == 0:
            return self._file_content[: self._line_end_pos[lineno] + 1]

        return self._file_content[
            self._line_end_pos[lineno - 1] + 1 : self._line_end_pos[lineno] + 1
        ]

    def get_line_by_pos(self, pos: int) -> str:
        """Get the content of a line a given position is on."""
        lineno, _ = self.get_lineno_colno(pos)
        return self.get_line_by_lineno(lineno)

    def move_pointer_absolute(self, pos: int) -> None:
        """Move the pointer to an absolute position."""
        Scanner._check_is_natural_number(pos, "New pointer position")
        # allow going past end by 1 for eof
        if pos > self._file_content_length:
            raise ValueError(
                "New pointer position is greater than file content length."
            )

        self._pointer_pos = pos

    def move_pointer_relative(self, n: int) -> None:
        """Move the pointer by a relative distance."""
        self.move_pointer_absolute(self._pointer_pos + n)

    def read(
        self,
        n: int,
        start: Union[int, None] = None,
        reset_pointer: bool = False,
    ) -> Union[str, Type[EOF]]:
        """Read up to n characters from the file and return them.

        An optional start position can be specified, without which the read
        will start from the current pointer position. The returned value
        includes the character at this start position.

        Fewer than n characters can be returned if the end of file is
        reached. If no character is left, Scanner.EOF will be returned.

        The pointer will be moved to one position after the last character
        returned by read. This can be prevented using the reset_pointer flag.

        Parameters
        ----------
        n: int
            Number of characters to read
        start: Union[int, None]
            Optional start position to read
        reset_pointer: bool
            Whether to reset the pointer after read. Default to False
        """
        Scanner._check_is_natural_number(n, "Chunk size n")

        if start is not None:
            Scanner._check_is_natural_number(start, "Start position")
            if start > self._file_content_length - 1:
                logging.warning(
                    "Read start position greater than file content length. "
                    "Will return EOF."
                )
            self.move_pointer_absolute(start)

        if self._pointer_pos > self._file_content_length - 1:
            return Scanner.EOF

        chunk = self.file_content[
            self._pointer_pos : min(
                self._pointer_pos + n, self._file_content_length
            )
        ]

        if not reset_pointer:
            if self._pointer_pos + n > self._file_content_length:
                logging.warning(
                    "End of file reached, subsequent reads will return EOF "
                    "if pointer position is not reset."
                )
            self.move_pointer_absolute(
                min(self._file_content_length, self._pointer_pos + n)
            )
        return chunk

    def _reset_pointer_wrapper(self, reset_pointer: bool = False):
        """Add an option to return pointer to original position.

        This is useful for lookaheads.
        """

        def wrapper(func):
            def wrapped(*args, **kwargs):
                if reset_pointer:
                    old_pos = self._pointer_pos
                returned = func(*args, **kwargs)
                if reset_pointer:
                    self.move_pointer_absolute(old_pos)  # noqa
                return returned

            return wrapped

        return wrapper

    def get_symbol(self):
        """Translate the next sequence of characters into a symbol."""
