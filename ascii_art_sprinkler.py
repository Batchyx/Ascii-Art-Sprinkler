#!/usr/bin/python3

import re
import sys
import random
import argparse
from dataclasses import dataclass
from typing import TextIO, Iterable, Tuple, Callable, List, Dict, Union
from typing import NoReturn, TypeVar


@dataclass
class Rect:
    """Yet another rectangle class.

    This rectangle spans from x = x_start to x_end (exclusive)
    and from y = y_start to y_end (exclusive)

    As a result, a Rect can have a zero-size"""
    x_start: int
    x_end: int
    y_start: int
    y_end: int

    def width(self) -> int:
        """Width of the rectangle"""
        return self.x_end - self.x_start

    def height(self) -> int:
        """Height of the rectangle"""
        return self.y_end - self.y_start

    def x_axis(self) -> Tuple[int, int]:
        """Return (x_start, x_end), which is the projection on the x_axis"""
        return (self.x_start, self.x_end)

    def y_axis(self) -> Tuple[int, int]:
        """Return (y_start, y_end), which is the projection on the x_axis"""
        return (self.y_start, self.y_end)

    def shift_y(self, shift_y: int) -> "Rect":
        """Shift the y coordinate by this amount."""
        self.y_start += shift_y
        self.y_end += shift_y
        return self

    def resize_y(self, new_size_y: int, keep_y_end: bool = False) -> "Rect":
        """Change the height of the rectangle.

        If keep_y_end is false, this keeps y_start, so only the bottom of the
        rectangle changes.

        If keep_y_end is true, this keeps y_end, so only the top changes."""
        assert new_size_y >= 0
        if keep_y_end:
            self.y_start = self.y_end - new_size_y
        else:
            self.y_end = self.y_start + new_size_y
        return self

    def clone(self) -> "Rect":
        """Clone this rectangle"""
        return Rect(self.x_start, self.x_end, self.y_start, self.y_end)

    def intersect(self, other: "Rect") -> "Union[Rect, None]":
        """Return the intersection between this rectangle and another.

        Returns None if there is no intersection."""
        x_start = max(self.x_start, other.x_start)
        x_end = min(self.x_end, other.x_end)
        y_start = max(self.y_start, other.y_start)
        y_end = min(self.y_end, other.y_end)
        if x_start < x_end and y_start < y_end:
            return Rect(x_start, x_end, y_start, y_end)
        return None


def random_subrectangle(rect: Rect, new_size_x: int, new_size_y: int,
                        rand: random.Random) -> Rect:
    """Given a rectangle, randomly select a smaller rectangle inside it

    The smaller subrectangle will have size (new_size_x, new_size_y)
    """
    x_start = rand.randint(rect.x_start, rect.x_end - new_size_x)
    y_start = rand.randint(rect.y_start, rect.y_end - new_size_y)
    return Rect(x_start, x_start + new_size_x, y_start, y_start + new_size_y)


class AsciiCanvas:
    "A canvas for ASCII art."
    def __init__(self, width: int, height: int):
        self._width: int = width
        # lines internally have a dynamic width, still below self.width
        self._lines: List[str] = ["" for x in range(height)]

    def width(self) -> int:
        """Return the width of the canvas"""
        return self._width

    def height(self) -> int:
        """Return the height of the canvas"""
        return len(self._lines)

    def line(self, y: int, justified: bool = True) -> str:
        """Return a line of the canvas as a string.

        The canvas is numbered from line 0 to height()-1, from top to bottom.

        if justified is true, then the string will have length = width(),
        else, it may be shorter.
        """
        if justified:
            return self._lines[y].ljust(self._width)
        return self._lines[y]

    def rectangle_in_canvas(self, rect: Rect) -> bool:
        """Returns true if this rectangle fits in the canvas.

        This only looks at the size of the canvas and the position of the rect
        """
        x_fit = (0 <= rect.x_start and rect.x_end <= self._width)
        y_fit = (0 <= rect.y_start and rect.y_end <= len(self._lines))
        return x_fit and y_fit

    def is_rectangle_free(self, rect: Rect) -> bool:
        """Returns true if the rectangle consist of white space.

        If this canvas contains anything but space characters inside the
        rectangle, or if the rectangle does not fit in the canvas, then return
        False.
        """

        if not self.rectangle_in_canvas(rect):
            return False
        for y in range(rect.y_start, rect.y_end):
            line = self._lines[y]
            x_start = rect.x_start
            if x_start > len(line):
                continue
            x_end = min(rect.x_end, len(line))
            if line[x_start:x_end] != " "*(x_end - x_start):
                return False
        return True

    def clone(self) -> "AsciiCanvas":
        """Create a deep clone of this object"""
        ret = AsciiCanvas(self._width, 0)
        ret._lines = self._lines[:]
        return ret

    @classmethod
    def from_line_list(cls, lines: List[str]) -> "AsciiCanvas":
        """Create a canvas from a list of lines

        The list of lines should not contains characters of width != 1
        (e.g. no tab or newlines)"""
        width = max((len(line) for line in lines), default=0)
        ret = cls(width, 0)
        ret._lines = list(lines)
        return ret

    @classmethod
    def from_text(cls, text: str) -> "AsciiCanvas":
        """Create a canvas from multiline text"""
        return cls.from_line_list(text.strip("\n").split("\n"))

    def mirror_x(self, map_function: Callable[[str], str]) -> None:
        """Mirror the content by the y axis, i.e. left-to-right

        map_function is a function called for each character in the art.
        The function can thus attempt to find mirrored characters"""
        def invert_line(line: str) -> str:
            inverted = "".join(map_function(c) for c in line[::-1])
            prefix = " " * (self._width - len(line))
            return "{}{}".format(prefix, inverted.rstrip(" "))

        for y, line in enumerate(self._lines):
            self._lines[y] = invert_line(line)

    def mirror_y(self, map_function: Callable[[str], str]) -> None:
        """Mirror the content by the x axis, i.e. top-to-bottom

        map_function is a function called for each character in the art,
        allowing each character to be mirrored."""
        self._lines.reverse()
        for y, line in enumerate(self._lines):
            self._lines[y] = "".join(map_function(c) for c in line)

    def blit(self, src: "AsciiCanvas", dest_x: int, dest_y: int) -> None:
        """Copy src at position (dest_x, dest_y).

        This will overwrite any character at this location.  Trying to
        blit art outside of the canvas is an error."""
        if not self.rectangle_in_canvas(Rect(dest_x, dest_x + src.width(),
                                             dest_y, dest_y + src.height())):
            raise IndexError("Coordinates out of bounds")
        for y in range(src.height()):
            line = self._lines[dest_y + y]
            line = line.ljust(dest_x)
            left = line[:dest_x]
            right = line[dest_x + src.width():]
            middle = src.line(y, justified=bool(right))
            line = "{}{}{}".format(left, middle, right)
            self._lines[dest_y + y] = line

    def increase_size(self, width: int, height: int) -> None:
        """Increase the size of the canvas by padding on the bottom right

        Trying to reduce the size using this method is an error."""
        if width < self.width() or height < self.height():
            raise IndexError("New size is smaller than old size")
        self._width = width
        self._lines.extend("" for y in range(height - self.height()))

    def remove_lines_at_top(self, height: int) -> "AsciiCanvas":
        """Remove n lines from the top and return them as a new canvas"""
        assert height <= self.height()
        ret = AsciiCanvas(self._width, 0)
        ret._lines = self._lines[:height]
        self._lines = self._lines[height:]
        return ret

    def add_line(self, line: str, allow_resize_width: bool) -> None:
        """Add a line to the bottom of the canvas.

        if allow_resize_width is True and the line is longer than the
        width of this canvas, then resize the canvas.  Otherwise, an exception
        will be thrown in that case."""

        if len(line) > self._width:
            if allow_resize_width:
                self._width = len(line)
            else:
                raise ValueError("Line is too long")
        self._lines.append(line)

    def add_margin(self, margin: int) -> None:
        """Add a given amount of margin on all four borders"""

        assert margin >= 0
        self._width += margin * 2
        prefix = " " * margin
        for y, line in enumerate(self._lines):
            self._lines[y] = prefix + line
        for _ in range(margin):
            self._lines.insert(0, "")
        self._lines.extend("" for i in range(margin))

    def write(self, output: TextIO) -> None:
        """Print the content of this canvas to a file-like object"""

        for line in self._lines:
            print(line.rstrip(), file=output)

    def __repr__(self) -> str:
        return "AsciiCanvas({}, {}) containing \"\"\"\n{}\n\"\"\"".format(
                self._width, len(self._lines), "\n".join(self._lines))


class ArtSyntaxError(Exception):
    """Syntax error for the ASCII Art definition file"""
    def __init__(self, error: str, line: Union[str, None], lineno: int):
        """Create an 'error' error message for 'line' at line lineno."""
        super().__init__()
        self.error: str = error
        self.line: Union[str, None] = line
        self.lineno: int = lineno


class ArtParser:
    """Parse an ASCII Art definition file"""

    STATE_BLANK = object()
    STATE_ASCII = object()
    STATE_META = object()

    COMMENT_CHAR = "#"
    COMMAND_CHAR = "##"

    def arts(self) -> List[AsciiCanvas]:
        """List of parsed ascii arts"""
        return self._arts

    def __init__(self) -> None:
        self._arts: List[AsciiCanvas] = []
        self._next_width: Union[None, int] = None
        self._next_height: Union[None, int] = None
        self._transpose_x: Dict[str, str] = {}
        self._transpose_y: Dict[str, str] = {}
        self._state = self.STATE_BLANK
        self._current_art: List[str] = []
        self._lineno = 0
        self._margin = 1

    def make_transpose_dictionnary(self, definition: str) -> Dict[str, str]:
        """Make a dictionary from str to str from a mirror_* definition"""
        ret = {" ": " "}

        def add(map_from: str, map_to: str) -> None:
            if map_from in ret:
                err = f"Character {repr(map_from)} defined more than once"
                self._error(err, definition)
            ret[map_from] = map_to

        for define in definition.split(" "):
            if len(define) == 1:
                add(define, define)
            elif len(define) == 2:
                add(define[0], define[1])
                add(define[1], define[0])

        return ret

    def _error(self, error: str, context: Union[str, None]) -> NoReturn:
        """Raise an error at the current line number"""
        raise ArtSyntaxError(error, context, self._lineno)

    def _parse_int_option(self, option_name: str, line: str,
                          minimum: int = 0) -> Union[int, None]:
        """Parse an integer option at the current line position

        If the line does not contain an "option_name=value", then return None
        Else, return the value parsed as an integer"""
        if not line.startswith(f"{option_name}="):
            return None
        line = line[len(option_name) + 1:]
        try:
            ret = int(line)
            if ret < minimum:
                self._error("Expected an integer above {minimum}", line)
            return ret
        except ValueError:
            self._error(f"'{line}' value is not an integer", line)

    def interpret_command(self, command: str) -> None:
        """Interpret the given command"""
        if (val := self._parse_int_option("width", command, 1)) is not None:
            if self._next_width is not None:
                self._error("width is already defined", command)
            self._next_width = val
        elif (val := self._parse_int_option("height", command, 1)) is not None:
            if self._next_height is not None:
                self._error("height is already defined", command)
            self._next_height = val
        elif (val := self._parse_int_option("margin", command, 0)) is not None:
            self._margin = val
        elif command.startswith("mirror_x:"):
            command = command[len("mirror_x:"):].lstrip(" ")
            self._transpose_x = self.make_transpose_dictionnary(command)
        elif command.startswith("mirror_y:"):
            command = command[len("mirror_y:"):].lstrip(" ")
            self._transpose_y = self.make_transpose_dictionnary(command)
        else:
            self._error("Unknown command", command)

    def _state_blank(self, line: str) -> None:
        """Handle a line in state BLANK

        The blank state is both the initial state and the state entered
        after encountering a blank line."""

        if line.startswith(self.COMMENT_CHAR):
            self._state = self.STATE_META
            self._state_meta(line)
        elif line:
            self._state = self.STATE_ASCII
            self._state_ascii(line)
        else:
            self._error("More than one blank line in separator", line)

    def _state_meta(self, line: str) -> None:
        """Handle a line in state META

        META state parses a meta block.
        It is entered when a line starts with '#' on state BLANK
        """

        if line.startswith(self.COMMAND_CHAR):
            self.interpret_command(line[2:].strip())
        elif line.startswith(self.COMMENT_CHAR):
            pass
        elif line:
            self._error("Found non-comment or command in meta block", line)
        else:
            self._state = self.STATE_BLANK
            if self._next_height is not None:
                self._state = self.STATE_ASCII

    def _state_ascii(self, line: str) -> None:
        """Handle a line in state ASCII

        ASCII state is entered by encountering a line not starting with #
        or after a meta block specifying a height.
        """

        if self._next_height is not None:
            self._next_height -= 1
            if self._next_height == -1:
                if line:
                    self._error("Expected blank line after fixed-height art",
                                line)
                self._next_height = None

        if line or self._next_height is not None:
            self._current_art.append(line)
        else:
            self._add_art()
            self._next_width = None
            self._next_height = None
            self._state = self.STATE_BLANK
            self._current_art.clear()

    def _add_art(self) -> None:
        """Add the currently-parsed art to the collection"""
        art = AsciiCanvas.from_line_list(self._current_art)
        if art.width() == 0 or art.height() == 0:
            self._error("Art has zero-width or zero-height", None)

        if self._next_width is not None:
            if art.width() > self._next_width:
                err = "Specified width ({}) but art is {} wide"
                err = err.format(self._next_width, art.width())
                longest_line = max(self._current_art, key=len)
                self._error(err, longest_line)
            else:
                art.increase_size(self._next_width, art.height())

        art.add_margin(self._margin)

        self._arts.append(art)
        self._try_add_mirrored_art(art)

    def _try_add_mirrored_art(self, art: AsciiCanvas) -> None:
        """Try to mirror the art horizontally, vertically and both"""
        if self._transpose_x:
            x_mirror = art.clone()
            try:
                x_mirror.mirror_x(self._transpose_x.__getitem__)
                self._arts.append(x_mirror)
                if self._transpose_y:
                    y_mirror = x_mirror.clone()
                    y_mirror.mirror_y(self._transpose_y.__getitem__)
            except KeyError:
                pass
        if self._transpose_y:
            y_mirror = art.clone()
            try:
                y_mirror.mirror_y(self._transpose_y.__getitem__)
                self._arts.append(y_mirror)
            except KeyError:
                pass

    def _handle_line(self, line: str) -> None:
        """Parse this line according to the current state"""
        line = line.expandtabs().rstrip()
        self._lineno += 1
        {
                self.STATE_BLANK: self._state_blank,
                self.STATE_META: self._state_meta,
                self.STATE_ASCII: self._state_ascii
        }[self._state](line)

    @classmethod
    def parse_file(cls, file_stream: TextIO) -> List[AsciiCanvas]:
        """Parse the given file."""
        self = cls()
        for line in file_stream:
            self._handle_line(line)

        if self._next_height is not None and self._next_height > 0:
            miss = self._next_height
            err = "Expected {} more line for fixed-height art".format(miss)
            self._error(err, None)
        if self._state is self.STATE_ASCII:
            self._add_art()
            self._next_width = None
        if self._next_width is not None:
            self._error("Expected one more art after width= definition", None)
        return self.arts()

Iterated = TypeVar("Iterated")
def drain_if(a_list: List[Iterated]
            ) -> Iterable[Tuple[Iterated, Callable[[], None]]]:
    """Iterate a list while removing some of its elements

    yields (element, function_to_delete_element)

    If function_to_delete_element is called, the element will be removed
    on the next iteration.
    """
    index = 0

    delete = False

    def delete_this(do_it: bool = True) -> None:
        nonlocal delete
        delete = do_it

    while index < len(a_list):
        delete = False
        yield a_list[index], delete_this
        if delete:
            a_list.pop(index)
        else:
            index += 1


class BlankFinder:
    """Find whitespace in a stream and provide a way to fill them

    This object maintains a buffer of text and use it to find blank rectangles
    consisting either of white space or available space at end of lines.

    While iterating, it maintains two set of blank rectangles:
    - rectangles that extends up to the last line, which may be extended if
      the following lines have more whitespace at the same location
    - rectangles that are fully encased in text, which cannot be extended
      further.

    Note that both of these sets include overlapping rectangles
    """
    def __init__(self,
                 soft_max_width: int,
                 minimum_blank_width: int,
                 maximum_blank_height: int):
        """Create a new BlankFinder.

        soft_max_width controls the length of lines that the output supports.
        It will not truncate input lines, but will not find blanks after
        the soft_max_width column.

        minimum_blank_width controls the minimum blank width to report.
        Increasing it improves performance, as setting it to 1 will make it
        report every space in a text

        maximum_blank_height controls the maximum blank height to find.
        If a larger blank is found, it will be truncated.  This also controls
        the maximum height of the buffer"""
        # Blanks from the previous line, sorted by x_start
        # It is unknown whether they can be continued or not.
        self._current_blanks : List[Rect] = []
        # Blanks that cannot be made larger.
        self._max_blanks : List[Rect] = []
        self._canvas = AsciiCanvas(soft_max_width, 0)
        self._current_line_no = 0
        self._soft_max_width = 80
        self._minimum_blank_width = minimum_blank_width
        self._maximum_blank_height = maximum_blank_height

    blank_re = re.compile(" +")

    def _get_blanks_ranges(self, line: str) -> Iterable[Tuple[int, int]]:
        """Looks for blanks in the current line

        yield (x_start, x_end) for each blank of size >= minimum_blank_width.

        If the line length is shorter than soft_max_width, then it will also
        yield a blank for the remaining space after the end of line.
        """

        for match in self.blank_re.finditer(line[:self._soft_max_width]):
            candidate = (match.start(), match.end())
            if candidate[0] + self._minimum_blank_width <= candidate[1]:
                yield candidate

        if len(line) + self._minimum_blank_width <= self._soft_max_width:
            yield (len(line), self._soft_max_width)

    @staticmethod
    def _add_rect_to_dict(dict_of_pair_to_rect: Dict[Tuple[int, int], Rect],
                          rect: Rect) -> None:
        """Add a rectangle to a list of rectangle indexed by their x_axis()

        If a rectangle already exist, then the one with the highest height is
        assigned to the position."""

        if rect.x_axis() in dict_of_pair_to_rect:
            if dict_of_pair_to_rect[rect.x_axis()].height() >= rect.height():
                return
        dict_of_pair_to_rect[rect.x_axis()] = rect

    def _handle_blank_in_current_line(self, x_start: int, x_end: int,
                                      last_blanks: List[Rect],
                                      blanks: Dict[Tuple[int, int], Rect]
                                     ) -> None:
        """Extend the current blanks with the blank of the current line

        Assuming that there is a blank at [x_start, x_end) in the current line,
        grow the blanks in last_blanks (which are assumed to end at the
        previous line) and fill the 'blanks' structure.

        This method will remove blanks from last_blanks as an optimisation.
        Assuming that blanks in the current line are browsed from left to
        right, then blanks in last_blanks that ends before x_end will be
        removed, as later blanks cannot intersect with them

        blanks are blanks whose y_end is at the current line.  They are
        indexed by their x_axis()"""
        line_rect = Rect(x_start, x_end, self._current_line_no,
                         self._current_line_no + 1)
        # this may result in both a over-height and a non-over-height rect
        # to be added.  Not a big deal.
        self._add_rect_to_dict(blanks, line_rect)
        for last, delete_last in drain_if(last_blanks):
            if x_end <= last.x_start:
                #    **
                # **
                break

            intersect = (max(x_start, last.x_start), min(x_end, last.x_end))
            if intersect == last.x_axis():
                #   **   **   ****   **
                # ****** **** **** ****
                delete_last()
                last.resize_y(last.height() + 1)
                self._add_rect_to_dict(blanks, last)
                continue
            if intersect[0] + self._minimum_blank_width <= intersect[1]:
                #   **** ****   **** ****** ****
                # ****     **** **     **     **
                self._add_rect_to_dict(blanks, Rect(intersect[0], intersect[1],
                                                    last.y_start,
                                                    line_rect.y_end))
            if last.x_end <= x_end:
                # **     ****   ***
                #    **    ****  **
                delete_last()
                self._max_blanks.append(last)

    def add_line(self, line: str) -> None:
        """Add a line to the canvas to search for blanks

        This also triggers extending current blanks automatically.
        After this method is called, new blanks may be available in
        drain_fillable_blanks().
        """
        self._current_line_no += 1
        self._canvas.add_line(line, True)

        last_blanks = self._current_blanks
        blanks : Dict[Tuple[int, int], Rect] = {}
        for x_start, x_end in self._get_blanks_ranges(line):
            self._handle_blank_in_current_line(x_start, x_end, last_blanks,
                                               blanks)

        self._max_blanks.extend(last_blanks)
        self._current_blanks.clear()
        for blank in blanks.values():
            if blank.height() >= self._maximum_blank_height:
                self._max_blanks.append(blank.clone())
                blank.resize_y(self._maximum_blank_height - 1, True)
            self._current_blanks.append(blank)
        self._current_blanks.sort(key=lambda r: r.x_start)

    def end_of_file(self) -> None:
        """Indicate that the end of the file/stream was reached.

        This indicates that blanks that extends up to the current line cannot
        be extended further."""
        self._max_blanks.extend(self._current_blanks)
        self._current_blanks.clear()

    def try_fill_blank(self, rect: Rect, art: AsciiCanvas) -> bool:
        """Try to fill a blank with an art.

        Return False if the rect is not empty (e.g. it has been filled through
        this method or the rect was not blank in the first place)

        Return True on success"""
        assert rect.width() == art.width() and rect.height() == art.height()
        rect = rect.clone()
        rect.shift_y(self._canvas.height() - 1 - self._current_line_no)
        if not self._canvas.is_rectangle_free(rect):
            return False
        self._canvas.blit(art, rect.x_start, rect.y_start)
        return True

    @staticmethod
    def get_first_line_of_rects(rects: Iterable[Rect], default: int) -> int:
        """Return the first line number occupied by a rectangle.

        If rects is empty, then return "default"."""
        top_rect = min(rects, key=lambda rect: rect.y_start, default=None)
        if top_rect is None:
            return default
        return top_rect.y_start

    def drain_fillable_blanks(self) -> Iterable[Rect]:
        """Drain blanks which are known to exist and are the largest possible

        This will yield Rect objects.  The object will no longer reference
        these blanks afterward"""

        min_line = self.get_first_line_of_rects(self._current_blanks,
                                                self._current_line_no + 1)
        canvas_start = self._current_line_no - (self._canvas.height() - 1)
        if min_line == canvas_start:
            return

        assert canvas_start <= min_line
        for blank, delete_blank in drain_if(self._max_blanks):
            if blank.y_end <= min_line:
                delete_blank()
                yield blank

    def flush_canvas(self, output: TextIO) -> None:
        """Drain lines which are not covered by blanks to the given output
        """
        next_line = self._current_line_no + 1
        min_largest_line = self.get_first_line_of_rects(self._max_blanks,
                                                        next_line)
        min_current_line = self.get_first_line_of_rects(self._current_blanks,
                                                        next_line)
        min_line = min(min_largest_line, min_current_line)
        canvas_start = self._current_line_no - (self._canvas.height() - 1)
        if canvas_start >= min_line:
            return
        flushable = self._canvas.remove_lines_at_top(min_line - canvas_start)
        flushable.write(output)


def sprinkle_art(blank_finder: BlankFinder, arts: List[AsciiCanvas],
                 rand: random.Random) -> None:
    """Randomly sprinkle art from 'arts' to blanks found by BlankFinder

    rand is the random generator to use.

    The art is mostly randomly sprinkled using a Monte-Carlo-like approach,
    where possibly overlapping blanks found by BlankFinder are sprinkled with
    random art as long as it fits, until a maximum amount of tries is reached.
    """
    fillable = list(blank_finder.drain_fillable_blanks())
    fillable.sort(key=lambda rect: -rect.width() * rect.height())

    for maybe_blank in fillable:
        fittable_arts = [art for art in arts
                         if (art.width() <= maybe_blank.width() and
                             art.height() <= maybe_blank.height())]
        if not fittable_arts:
            continue
        max_tries = 5
        for _ in range(max_tries):
            art = rand.choice(fittable_arts)
            rect = random_subrectangle(maybe_blank, art.width(),
                                       art.height(), rand)
            blank_finder.try_fill_blank(rect, art)


def sprinkle_art_on_stream(input_stream: TextIO, output_stream: TextIO,
                           arts: List[AsciiCanvas],
                           rand: random.Random,
                           soft_max_width: int = 80) -> None:
    """Read the input stream, sprinkle arts and write to the output stream

    soft_max_width controls the expected """
    min_width = min(arts, key=lambda art: art.width()).width()
    max_height = max(arts, key=lambda art: art.height()).height()

    finder = BlankFinder(soft_max_width, min_width, max_height * 5)

    for lineno, line in enumerate(input_stream):
        finder.add_line(line.rstrip("\n").expandtabs())
        if lineno % max_height == 0:
            sprinkle_art(finder, arts, rand)
            finder.flush_canvas(output_stream)

    finder.end_of_file()
    sprinkle_art(finder, arts, rand)
    finder.flush_canvas(output_stream)


def main() -> None:
    """Parse command line arguments and run the art sprinkler"""
    parser = argparse.ArgumentParser(
            description="sprinkle ASCII Art to standard input")
    parser.add_argument("--soft-max-width", metavar="soft_max_width", type=int,
                        default=80,
                        help="""Expected width of the text.  Art will be
                              sprinkled from column 1 up to soft_max_width.
                              Lines larger than this width will not be
                              truncated.""")
    parser.add_argument("--seed", metavar="seed", type=int,
                        help="""Seed the random generator with this value, to
                        always produce the same output.""")
    parser.add_argument("art_file", metavar="<ASCII Art definition file>",
                        type=str,
                        help="""Path to a file containing the ASCII Art to
                        sprinkle.  See the example files for documentation.""")
    args = parser.parse_args()
    arts = None
    try:
        with open(args.art_file, 'r') as config_file:
            arts = ArtParser.parse_file(config_file)
    except OSError as err:
        print(f"Cannot read file '{args.art_file}':", err, file=sys.stderr)
        sys.exit(1)
    except ArtSyntaxError as err:
        print("Syntax error in", args.art_file, f"line {err.lineno}:",
              err.error, file=sys.stderr)
        if err.line is not None:
            print(err.line, file=sys.stderr)
        sys.exit(1)

    rand = random.Random()
    if "seed" in args:
        rand.seed(args.seed)

    sprinkle_art_on_stream(sys.stdin, sys.stdout, arts, rand,
                           args.soft_max_width)


if __name__ == "__main__":
    main()
