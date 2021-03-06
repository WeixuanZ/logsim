"""Read the circuit definition file and translate the characters into symbols.

Used in the Logic Simulator project to read the characters in the definition
file and translate them into symbols that are usable by the parser.

SPHINX-IGNORE
Classes
-------
Scanner - reads definition file and translates characters into symbols.
Symbol - encapsulates a symbol and stores its properties.
SPHINX-IGNORE
"""
from typing import Union, Tuple, Type, Callable
from operator import methodcaller
from itertools import accumulate, dropwhile, starmap
import logging
import mmap
import os

from names import Names
from symbol_types import ReservedSymbolType, ExternalSymbolType
from exceptions import SyntaxErrors, Errors


class Symbol:
    """Encapsulate a symbol and store its properties.

    Parameters
    ----------
    symbol_type: Union[ReservedSymbolType, ExternalSymbolType]
        The type of the symbol
    symbol_id: int
        ID of the symbol, from the Names instance
    lineno:
        The line number of the symbol string in file (optional)
    colno:
        The column number of the start of the symbol string in file (optional)

    SPHINX-IGNORE
    Public Methods
    --------------
    No public methods.
    SPHINX-IGNORE
    """

    def __init__(
        self,
        symbol_type: Union[ReservedSymbolType, ExternalSymbolType],
        symbol_id: int,
        lineno: Union[int, None] = None,
        colno: Union[int, None] = None,
    ):
        """Initialise symbol properties."""
        self.type = symbol_type
        self.id = symbol_id
        self.lineno = lineno
        self.colno = colno

    def __eq__(self, other):
        """Check if two Symbol instances are the same."""
        if isinstance(self, other.__class__):
            return all(
                (
                    self.type == other.type,
                    self.id == other.id,
                    self.lineno == other.lineno,
                    self.colno == other.colno,
                )
            )
        return False

    def __repr__(self):
        """Customised repr of Symbol objects."""
        return (  # pragma: no cover
            f"Symbol({self.type}, {self.id}, "
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
    path: str
        path to the circuit definition file.
    names: Names
        instance of the names.Names() class.

    SPHINX-IGNORE
    Attributes
    ----------
    encoding:
        Encoding scheme of the file.
    pointer:
        Pointer position, line number, and column number.
    pointer_pos:
        Pointer position in the file.
    pointer_lineno:
        Line number of the pointer.
    pointer_colno:
        Column number of the pointer.
    LINE_COMMENT_IDENTIFIER:
        Identifier specifying start of line comments, default '//'.
    BLOCK_COMMENT_IDENTIFIERS:
        Identifiers specifying start and end of block comments,
        default ('/*', '*/').
    TREAT_INVALID_CHAR_AS_ERROR:
        Whether to throw errors for invalid characters, default True.
    EOF:
        Symbol indicating the end of file.

    Public Methods
    --------------
    get_line_by_lineno(self, lineno):
        Get the content of a line using the line number.
    get_line_by_pos(self, pos):
        Get the content of a line a given position is on.
    get_lineno_colno(self, pos):
        Get the line and column numbers of a position in file.
    get_symbol(self):
        Translates the next sequence of characters into a symbol and returns
        the symbol.
    SPHINX-IGNORE
    """

    class EOF:
        """Symbol indicating the end of file."""

        pass

    LINE_COMMENT_IDENTIFIER = "//"
    BLOCK_COMMENT_IDENTIFIERS = ("/*", "*/")
    TREAT_INVALID_CHAR_AS_ERROR = True

    _reserved_symbol_values_set = set(ReservedSymbolType.values())
    _valid_char_not_comment_set = _reserved_symbol_values_set | {"_"}

    def __init__(self, path: str, names: Names, errors: Errors):
        """Open specified file and initialise reserved words and IDs."""
        self.path = path
        self.names = names
        self.errors = errors
        self.encoding = "utf-8"

        # >= 0, <= file_content_length, at EOF when = file_content_length
        self._pointer_pos = 0
        self._line_lengths = []

        # mmap cannot open empty file, add a new line if file empty
        filesize = os.path.getsize(path)
        if filesize == 0:
            with open(self.path, "r+") as file_obj:
                file_obj.write("\n")

        # using memory mapping to improve performance
        with open(self.path, "rb", buffering=0) as file_obj:
            self._file_obj = mmap.mmap(
                file_obj.fileno(), length=0, access=mmap.ACCESS_READ
            )

            try:
                self._file_obj.madvise(mmap.MADV_SEQUENTIAL)
            except AttributeError:
                pass

        while True:
            line = self._file_obj.readline()
            if line:
                self._line_lengths.append(len(line))
            else:
                break
        self._file_content_length = self._file_obj.tell()

        # the pos of last character on the line
        self._line_end_pos = list(
            map(lambda pos: pos - 1, accumulate(self._line_lengths))
        )
        # EOF
        self._line_end_pos[-1] += 1
        self._line_lengths[-1] += 1

    def __del__(self):
        """Close mmap on destruction."""
        self._file_obj.close()

    @property
    def pointer_pos(self) -> Union[int, Type[EOF]]:
        """Pointer position in the file.

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
        """Line number of the pointer.

        It is zero-indexed and protected.
        """
        return self.get_lineno_colno(self._pointer_pos)[0]

    @property
    def pointer_colno(self) -> int:
        """Column number of the pointer.

        It is zero-indexed and protected. It can be one larger than the length
        of the line if the pointer is on the last line, which denotes the end
        of file is reached.
        """
        return self.get_lineno_colno(self._pointer_pos)[1]

    @property
    def pointer(self) -> Tuple[int, int, int]:
        """Pointer position, line number, and column number."""
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

    def _move_pointer_absolute(self, pos: int) -> None:
        """Move the pointer to an absolute position."""
        Scanner._check_is_natural_number(pos, "New pointer position")
        # allow going past end by 1 for eof
        if pos > self._file_content_length:
            raise ValueError(
                "New pointer position is greater than file content length."
            )

        self._pointer_pos = pos

    def _move_pointer_relative(self, n: int) -> None:
        """Move the pointer by a relative distance."""
        self._move_pointer_absolute(self._pointer_pos + n)

    def _read(
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
        old_pos = self._pointer_pos

        if start is not None:
            Scanner._check_is_natural_number(start, "Start position")
            if start > self._file_content_length - 1:
                logging.warning(
                    "Read start position greater than file content length. "
                    "Will return EOF."
                )
            self._move_pointer_absolute(start)

        if self._pointer_pos > self._file_content_length - 1:
            return Scanner.EOF

        chunk_end_pos = min(self._pointer_pos + n, self._file_content_length)
        chunk = self._file_obj[self._pointer_pos : chunk_end_pos].decode(
            self.encoding
        )

        if reset_pointer:
            self._move_pointer_absolute(old_pos)
        else:
            if self._pointer_pos + n > self._file_content_length:
                logging.warning(
                    "End of file reached, subsequent reads will return EOF "
                    "if pointer position is not reset."
                )
            self._move_pointer_absolute(chunk_end_pos)
        return chunk

    def get_line_by_lineno(self, lineno: int) -> str:
        """Get the content of a line using the line number."""
        Scanner._check_is_natural_number(lineno, "Line number")
        if lineno > len(self._line_lengths) - 1:
            raise ValueError(
                "Line number larger than the number of lines in file"
            )

        start_pos = 0 if lineno == 0 else self._line_end_pos[lineno - 1] + 1
        return self._read(
            self._line_end_pos[lineno] + 1 - start_pos,
            start=start_pos,
            reset_pointer=True,
        )

    def get_line_by_pos(self, pos: int) -> str:
        """Get the content of a line a given position is on."""
        lineno, _ = self.get_lineno_colno(pos)
        return self.get_line_by_lineno(lineno)

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
                    self._move_pointer_absolute(old_pos)  # noqa
                return returned

            return wrapped

        return wrapper

    def _get_next_character(
        self,
        predicate: Callable[[str], bool] = lambda c: True,
        reset_pointer: bool = False,
    ) -> str:
        """Return the next desired character in file.

        An optional predicate can be specified to get the next character
        meeting a certain criteria.

        If the end of file is reached, will return Scanner.EOF.

        Examples
        --------
        >>> self._get_next_character(predicate=lambda c: not c.isdigit())

        Parameters
        ----------
        predicate: Callable[[str], bool]
            Optional callable that accepts a character and return whether to
            it is the desired next character
        reset_pointer: bool
            Whether to reset the pointer to the initial position before this
            function call
        """

        @self._reset_pointer_wrapper(reset_pointer=reset_pointer)
        def inner():
            while True:
                next_char = self._read(1)
                if next_char is Scanner.EOF:
                    break
                if predicate(next_char):
                    return next_char
            return Scanner.EOF

        return inner()

    def _move_pointer_onto_next_character(
        self, predicate: Callable[[str], bool] = lambda c: True
    ) -> None:
        """Move pointer onto the next desired character.

        Note that the pointer will be on the character instead of after it,
        i.e. subsequent call to self.read(1) will return the desired character.
        """
        next_char = self._get_next_character(predicate=predicate)
        if next_char is not Scanner.EOF:
            self._move_pointer_relative(-1)

    def _move_pointer_after_next_match(self, target: str) -> None:
        """Move pointer after the specific target."""
        while True:
            next_chars = self._read(len(target), reset_pointer=True)
            if next_chars is Scanner.EOF:
                break
            if next_chars == target:
                self._move_pointer_relative(len(target))
                return
            self._move_pointer_relative(1)

    def _get_next_non_whitespace_character(self, reset_pointer=False) -> str:
        """Return the next non-whitespace character in file."""
        return self._get_next_character(
            predicate=lambda c: not c.isspace(), reset_pointer=reset_pointer
        )

    def _move_pointer_skip_whitespace_characters(self) -> None:
        """Move pointer onto the next character that is not a whitespace."""
        self._move_pointer_onto_next_character(
            predicate=lambda c: not c.isspace()
        )

    def _get_next_chunk(
        self,
        start_predicate: Callable[[str], bool],
        end_predicate: Callable[[str], bool],
        reset_pointer=False,
    ) -> str:
        """Get the next chunk of characters from the file.

        The start_predicate is a callable returning a bool, which specifies
        when the chunk starts. The chunk is returned upto when the
        end_predicate returns True (not including the character making
        end_predicate True). The chunk is at least one character long, i.e.
        only characters after the chunk starting character are passed to
        end_predicate.

        Parameters
        ----------
        start_predicate: Callable[[str], bool]
            A callable that accepts a character and returns whether to start
            the chunk
        end_predicate: Callable[[str], bool]
            A callable that accepts a character and returns whether to end the
            chunk. The input character causing a True return is not included
            in the chunk
        reset_pointer: bool
            Whether to reset the pointer to initial position before this
            function call. Default to False.
        """

        @self._reset_pointer_wrapper(reset_pointer=reset_pointer)
        def inner():
            self._move_pointer_onto_next_character(predicate=start_predicate)
            chunk_start = self._pointer_pos
            self._move_pointer_onto_next_character(predicate=end_predicate)
            chunk_end = self._pointer_pos

            return self._read(chunk_end - chunk_start, start=chunk_start)

        return inner()

    def _get_next_number(self, reset_pointer=False) -> str:
        """Return the next number in file.

        Number strings can start with "0"s.
        """
        return self._get_next_chunk(
            start_predicate=methodcaller("isdigit"),
            end_predicate=lambda c: not c.isdigit(),
            reset_pointer=reset_pointer,
        )

    def _get_next_name(self, reset_pointer=False) -> str:
        """Return the next name string in file.

        A name is defined as a sequence of characters that starts with a letter
        and is followed by a mixture of letters and numbers.
        """
        return self._get_next_chunk(
            start_predicate=lambda c: c.isalpha() or c == "_",
            end_predicate=lambda c: not (c.isalnum() or c == "_"),
            reset_pointer=reset_pointer,
        )

    def get_symbol(self) -> Union[Symbol, None]:
        """Translate the next sequence of characters into a symbol.

        If the end of file is reached, None will be returned instead of a
        Symbol instance.
        """
        self._move_pointer_skip_whitespace_characters()
        current_character = self._get_next_character(reset_pointer=True)
        if current_character is Scanner.EOF:  # EOF
            return None

        # line comment
        if current_character == Scanner.LINE_COMMENT_IDENTIFIER[0]:
            if (
                self._read(
                    len(Scanner.LINE_COMMENT_IDENTIFIER), reset_pointer=True
                )
                == Scanner.LINE_COMMENT_IDENTIFIER
            ):
                self._move_pointer_onto_next_character(
                    predicate=lambda c: c == "\n"
                )
                return self.get_symbol()
        # block comment
        if current_character == Scanner.BLOCK_COMMENT_IDENTIFIERS[0][0]:
            if (
                self._read(
                    len(Scanner.BLOCK_COMMENT_IDENTIFIERS[0]),
                    reset_pointer=True,
                )
                == Scanner.BLOCK_COMMENT_IDENTIFIERS[0]
            ):
                self._move_pointer_after_next_match(
                    target=Scanner.BLOCK_COMMENT_IDENTIFIERS[1]
                )
                return self.get_symbol()

        if current_character.isalpha() or current_character == "_":  # name
            symbol_string = self._get_next_name()

        elif current_character.isdigit():  # number
            symbol_string = self._get_next_number()

        elif (
            current_character in Scanner._reserved_symbol_values_set
        ):  # operator
            symbol_string = self._get_next_character()

        else:  # not a valid character
            # throw error
            if Scanner.TREAT_INVALID_CHAR_AS_ERROR:
                error = SyntaxErrors.UnexpectedToken(_("Invalid character"))
                symbol_lineno, symbol_colno = self.get_lineno_colno(
                    self._pointer_pos
                )
                error.symbol = Symbol(
                    symbol_type=ExternalSymbolType.IDENTIFIER,
                    symbol_id=-1,
                    lineno=symbol_lineno,
                    colno=symbol_colno,
                )
                self.errors.add_error(
                    error=error,
                    show_end_of_word=False,
                    parse_entry_func_name="get_symbol",
                    base_depth=0,
                )

            # not just use self.move_pointer_relative(1) to prevent reaching
            # recursion depth limit
            if current_character in (
                Scanner.LINE_COMMENT_IDENTIFIER[0],
                Scanner.BLOCK_COMMENT_IDENTIFIERS[0][0],
            ):
                self._move_pointer_relative(1)
            else:
                # use set to speed up predicate test
                self._move_pointer_onto_next_character(
                    predicate=lambda c: c.isalnum()
                    or c in Scanner._valid_char_not_comment_set
                )
            return self.get_symbol()

        [symbol_id] = self.names.lookup([symbol_string])
        symbol_type = self.names.get_name_type(symbol_id)
        symbol_lineno, symbol_colno = self.get_lineno_colno(
            self._pointer_pos - len(symbol_string)
        )
        return Symbol(symbol_type, symbol_id, symbol_lineno, symbol_colno)
