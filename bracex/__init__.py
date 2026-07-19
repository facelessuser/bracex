"""
A Bash like brace expander.

Licensed under MIT
Copyright (c) 2018 - 2020 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""
from __future__ import annotations
import itertools
import math
import re
from typing import Iterator, Pattern, Match, Iterable, AnyStr, Any
from . import __meta__

__all__ = ('expand', 'iexpand')

__version__ = __meta__.__version__
__version_info__ = __meta__.__version_info__

_alpha = [chr(x) if x != 0x5c else '' for x in range(ord('A'), ord('z') + 1)]
_nalpha = list(reversed(_alpha))

RE_INT_ITER = re.compile(r'(-?\d+)\.{2}(-?\d+)(?:\.{2}(-?\d+))?(?=\})')
RE_CHR_ITER = re.compile(r'([A-Za-z])\.{2}([A-Za-z])(?:\.{2}(-?\d+))?(?=\})')

DEFAULT_LIMIT = 1000


class Sentinel(str):
    """A sentinel string value."""


EMPTY = Sentinel('')


class ExpansionLimitException(Exception):
    """Brace expansion limit exception."""


def truncate_digits(value: str, limit: int = 19) -> str:
    """Truncate a string of digits."""

    return value[:limit + (1 if value and value[0] == '-' else 0)]


def expand(
    string: AnyStr,
    keep_escapes: bool = False,
    limit: int = DEFAULT_LIMIT,
    return_empty: bool = False
) -> list[AnyStr]:
    """Expand braces."""

    return list(iexpand(string, keep_escapes, limit, return_empty))


def iexpand(
    string: AnyStr,
    keep_escapes: bool = False,
    limit: int = DEFAULT_LIMIT,
    return_empty: bool = False
) -> Iterator[AnyStr]:
    """Expand braces and return an iterator."""

    if isinstance(string, bytes):
        for entry in ExpandBrace(keep_escapes, limit, return_empty).expand(string.decode('latin-1')):
            yield entry.encode('latin-1')
    else:
        for entry in ExpandBrace(keep_escapes, limit, return_empty).expand(string):
            yield entry


class StringIter:
    """Preprocess replace tokens."""

    def __init__(self, string: str) -> None:
        """Initialize."""

        self._string = string
        self._index = 0

    def __iter__(self) -> "StringIter":  # pragma: no cover
        """Iterate."""

        return self

    def __next__(self) -> str:
        """Python 3 iterator compatible next."""

        return self.iternext()

    def match(self, pattern: Pattern[str]) -> Match[str] | None:
        """Perform regex match at index."""

        m = pattern.match(self._string, self._index)
        if m:
            self._index = m.end()
        return m

    @property
    def index(self) -> int:
        """Get current index."""

        return self._index

    def previous(self) -> str:  # pragma: no cover
        """Get previous char."""

        return self._string[self._index - 1]

    def advance(self, count: int) -> None:
        """Advanced the index."""

        self._index += count

    def rewind(self, count: int) -> None:
        """Rewind index."""

        if count > self._index:  # pragma: no cover
            raise ValueError("Can't rewind past beginning!")

        self._index -= count

    def iternext(self) -> str:
        """Iterate through characters of the string."""

        try:
            char = self._string[self._index]
            self._index += 1
        except IndexError as e:  # pragma: no cover
            raise StopIteration from e

        return char


class ExpandBrace:
    """Expand braces like in Bash."""

    def __init__(
        self,
        keep_escapes: bool = False,
        limit: int = DEFAULT_LIMIT,
        return_empty: bool = False
    ) -> None:
        """Initialize."""

        self.max_limit = limit
        self.expanding = False
        self.keep_escapes = keep_escapes
        self.return_empty = return_empty

    def account(self, count: int) -> int:
        """Ensure count is not exceeding the expectation."""

        if self.max_limit > 0 and count > self.max_limit:
            raise ExpansionLimitException(
                f'Brace expansion has exceeded the limit of {self.max_limit:d}'
            )
        return count

    def set_expanding(self) -> bool:
        """Set that we are expanding a sequence, and return whether a release is required by the caller."""

        status = not self.expanding
        if status:
            self.expanding = True
        return status

    def is_expanding(self) -> bool:
        """Get status of whether we are expanding."""

        return self.expanding

    def release_expanding(self, release: bool) -> None:
        """Release the expand status."""

        if release:
            self.expanding = False

    def get_escape(self, c: str, i: StringIter) -> str:
        """Get an escape."""

        try:
            escaped = next(i)
        except StopIteration:
            escaped = ''
        return c + escaped if self.keep_escapes else escaped

    def squash(self, a: Iterable[str], b: Iterable[str]) -> Iterator[str]:
        """
        Returns a generator that squashes two iterables into one.

        ```
        ['this', 'that'], [[' and', ' or']] => ['this and', 'this or', 'that and', 'that or']
        ```
        """

        for x in itertools.product(a, b):
            if all(i is EMPTY for i in x):
                yield EMPTY
            else:
                yield ''.join(x)

    def chain(self, *iterables: Any) -> Iterator[str]:
        """Chain iterables."""

        for iterable in iterables:
            yield from iterable

    def flatten(self, iterables: Any) -> Iterator[str]:
        """Flatten out results."""

        for item in iterables:
            if isinstance(item, list):
                yield from self.flatten(item)
                continue
            yield item

    def get_literals(
        self,
        c: str,
        i: StringIter,
        depth: int,
        ignore_end: bool = False
    ) -> tuple[list[str | Iterator[str]], int]:
        """
        Get a string literal.

        Gather all the literal chars up to opening curly or closing brace.
        Also gather chars between braces and commas within a group (is_expanding).
        """

        result = []  # type: list[str | Iterator[str]]
        is_dollar = False
        count = 1
        literal = ''

        try:
            while c:
                ignore_brace = is_dollar
                is_dollar = False

                if c == '$':
                    is_dollar = True
                    literal += c

                elif c == '\\':
                    literal += self.get_escape(c, i)

                elif not ignore_brace and c == '{':

                    if literal:
                        result.append(literal)
                        literal = ''

                    # Try and get the group
                    try:
                        seq, scount = self.get_sequence(next(i), i, depth + 1)
                        count *= scount
                        result.append(seq)
                    except StopIteration:
                        # There are no characters after `{`
                        # Save `{` and stop parsing.
                        literal += c
                        raise

                elif self.is_expanding() and (c == ',' or (c == '}' and not ignore_end)):
                    # We are Expanding within a group and found a group delimiter
                    # Return what we gathered before the group delimiters.

                    ignore_end = False

                    if literal:
                        result.append(literal)

                    i.rewind(1)
                    break
                else:
                    literal += c

                c = next(i)
        except StopIteration:
            # Ensure we store any remaining literals
            if literal:
                result.append(literal)

        return result, self.account(count)

    def get_sequence(self, c: str, i: StringIter, depth: int) -> tuple[Iterator[str], int]:
        """
        Get the sequence.

        Get sequence between `{}`, such as: `{a,b}`, `{1..2[..inc]}`, etc.
        It will basically crawl to the end or find a valid series.
        """

        result = []  # type: list[str | Iterator[str] | Iterable[str | Iterator[str]]]
        release = self.set_expanding()
        has_comma = False  # Used to indicate validity of group (`{1..2}` are an exception).
        is_empty = True  # Tracks whether the current slot is empty `{slot,slot,slot}`.
        counts = []

        # Detect numerical and alphabetic series: `{1..2}` etc.
        i.rewind(1)
        item, count = self.get_range(i)
        i.advance(1)
        if item is not None:
            self.release_expanding(release)
            return item, self.account(count)

        try:
            while True:
                # Bash has some special top level logic. if `}` follows `{` but hasn't matched
                # a group yet, keep going except when the first 2 bytes are `{}` which gets
                # completely ignored.
                keep_looking = depth == 1 and not has_comma
                if (c == '}' and (not keep_looking or i.index == 2)):
                    self.release_expanding(release)

                    # Handle empty slot
                    if is_empty:
                        result.append(EMPTY)
                        if has_comma:
                            counts.append(1)

                    # Sequence is not valid
                    if not has_comma:
                        count = 1
                        temp = iter(['{'])
                        for r in self.flatten(result):
                            temp = self.squash(temp, [r] if isinstance(r, str) else r)
                        temp = self.squash(temp, ['}'])
                        return temp, self.account(math.prod(counts, start=1))

                    # Format return for a sequence
                    fin = iter([])  # type: Iterator[str]
                    start = 0
                    l = len(result)
                    for e, x in enumerate(result):
                        if not isinstance(x, str):
                            if e != start:
                                fin = self.chain(fin, result[start:e])
                            if isinstance(x, list):
                                temp = iter([EMPTY])
                                for y in x:
                                    temp = self.squash(temp, [y] if isinstance(y, str) else y)
                                fin = self.chain(fin, temp)
                            else:
                                fin = self.chain(fin, result[e])
                            start = e + 1
                    if start < l:
                        fin = self.chain(fin, result[start:])
                    return fin, self.account(sum(counts))

                elif c == ',':
                    # Must be the first element in the list.
                    has_comma = True
                    if is_empty:
                        result.append(EMPTY)
                        counts.append(1)
                    else:
                        is_empty = True

                else:
                    # Lower level: Try to find group, but give up if cannot acquire.
                    value, lcount = self.get_literals(c, i, depth, keep_looking)
                    counts.append(lcount)
                    if value is not None:
                        if len(value) > 1:
                            result.append(value)
                        else:
                            result.extend(value)
                        is_empty = False

                c = next(i)

        except StopIteration:
            self.release_expanding(release)

        # Sequence is not valid
        temp2 = iter(['{'])  # type: Iterator[str]
        l = len(result)
        last_str = False
        for r in self.flatten(result):
            is_str = isinstance(r, str)
            temp2 = self.squash(temp2, [(',' if last_str else '') + r] if is_str else r)
            last_str = is_str
        return temp2, self.account(math.prod(counts, start=1))

    def get_range(self, i: StringIter) -> tuple[Iterator[str] | None, int]:
        """
        Check and retrieve range if value is a valid range.

        Here we are looking to see if the value is series or range.
        We look for `{1..2[..inc]}` or `{a..z[..inc]}` (negative numbers are fine).
        """

        try:
            m = i.match(RE_INT_ITER)
            if m:
                return self.get_int_range(*m.groups())

            m = i.match(RE_CHR_ITER)
            if m:
                return self.get_char_range(*m.groups())
        except Exception:  # pragma: no cover
            # TODO: We really should never fail here,
            # but if we do, assume the sequence range
            # was invalid. This catch can probably
            # be removed in the future with more testing.
            pass

        return None, 0

    def format_values(self, values: Iterable[int], padding: int) -> Iterator[str]:
        """Get padding adjusting for negative values."""

        for value in values:
            yield "{:0{pad}d}".format(value, pad=padding) if padding else str(value)

    def get_int_range(self, start: str, end: str, increment: str | None = None) -> tuple[Iterator[str], int]:
        """Get an integer range between start and end and increments of increment."""

        # Truncate really big numbers to 19 digits
        start = truncate_digits(start)
        end = truncate_digits(end)
        if increment is not None:
            increment = truncate_digits(increment)

        first, last = int(start), int(end)
        inc = int(increment) if increment is not None else 1
        max_length = max(len(start), len(end))

        # Zero doesn't make sense as an incrementer
        # but like bash, just assume one
        if inc == 0:
            inc = 1

        if start[0] == '-':
            start = start[1:]

        if end[0] == '-':
            end = end[1:]

        if (len(start) > 1 and start[0] == '0') or (len(end) > 1 and end[0] == '0'):
            padding = max_length

        else:
            padding = 0

        if first < last:
            span = abs((last + 1) - first)
            ainc = abs(inc)
            count = math.ceil(span / ainc) if ainc <= span else 1
            r = range(first, last + 1, -inc if inc < 0 else inc)
        else:
            span = abs((first + 1) - last)
            ainc = abs(inc)
            count = math.ceil(span / ainc) if ainc <= span else 1
            r = range(first, last - 1, inc if inc < 0 else -inc)

        return self.format_values(r, padding), count

    def get_char_range(self, start: str, end: str, increment: str | None = None) -> tuple[Iterator[str], int]:
        """Get a range of alphabetic characters."""

        # Truncate really big numbers to 19 digits
        if increment is not None:
            increment = truncate_digits(increment)

        inc = int(increment) if increment else 1
        if inc < 0:
            inc = -inc

        # Zero doesn't make sense as an incrementer
        # but like bash, just assume one
        if inc == 0:
            inc = 1

        inverse = start > end
        alpha = _nalpha if inverse else _alpha

        first = alpha.index(start)
        last = alpha.index(end)

        if first < last:
            span = (last + 1) - first
            count = math.ceil(span / inc) if abs(inc) <= abs(span) else 1
            return (alpha[r] for r in range(first, last + 1, -inc if inc < 0 else inc)), count
        span = (first + 1) - last
        count = math.ceil(span / inc) if abs(inc) <= abs(span) else 1
        return (alpha[r] for r in range(first, last - 1, inc if inc < 0 else -inc)), count

    def expand_str(self, string: str) -> Iterator[str]:
        """Expand the string."""

        i = StringIter(string)
        values, _ = self.get_literals(next(i), i, 0)

        # Squash the nested list by calculating the combinations
        results = iter([EMPTY])  # type: Iterator[str]
        for v in values:
            results = self.squash(results, [v] if isinstance(v, str) else v)
        return results

    def expand(self, string: str) -> Iterator[str]:
        """Expand."""

        self.expanding = False
        found_literal = False
        if string:
            for x in self.expand_str(string):
                if x is EMPTY:
                    continue
                found_literal = True
                yield x

        if not found_literal and self.return_empty:
            yield ""
