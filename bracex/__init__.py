"""
A Bash like brace expander.

Licensed under MIT
Copyright (c) 2018 Isaac Muse <isaacmuse@gmail.com>

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
import itertools
import re
from .pep562 import Pep562
import sys
import warnings
from .__meta__ import __version_info__, __version__

__all__ = ('expand', 'iexpand')

_alpha = [chr(x) if x != 0x5c else '' for x in range(ord('A'), ord('z') + 1)]
_nalpha = list(reversed(_alpha))

RE_INT_ITER = re.compile(r'(-?\d+)\.{2}(-?\d+)(?:\.{2}(-?\d+))?(?=\})')
RE_CHR_ITER = re.compile(r'([A-Za-z])\.{2}([A-Za-z])(?:\.{2}(-?\d+))?(?=\})')

PY37 = (3, 7) <= sys.version_info

__deprecated__ = {
    "version": ("__version__", __version__),
    "version_info": ("__version_info__", __version_info__)
}


def expand(string, keep_escapes=False):
    """Expand braces."""

    return list(iexpand(string, keep_escapes))


def iexpand(string, keep_escapes=False):
    """Expand braces and return an iterator."""

    if isinstance(string, bytes):
        is_bytes = True
        string = string.decode('latin-1')

    else:
        is_bytes = False

    if is_bytes:
        return (entry.encode('latin-1') for entry in ExpandBrace(keep_escapes).expand(string))

    else:
        return (entry for entry in ExpandBrace(keep_escapes).expand(string))


class StringIter(object):
    """Preprocess replace tokens."""

    def __init__(self, string):
        """Initialize."""

        self._string = string
        self._index = 0

    def __iter__(self):
        """Iterate."""

        return self

    def __next__(self):
        """Python 3 iterator compatible next."""

        return self.iternext()

    def match(self, pattern):
        """Perform regex match at index."""

        m = pattern.match(self._string, self._index)
        if m:
            self._index = m.end()
        return m

    @property
    def index(self):
        """Get current index."""

        return self._index

    def previous(self):  # pragma: no cover
        """Get previous char."""

        return self._string[self._index - 1]

    def advance(self, count):
        """Advanced the index."""

        self._index += count

    def rewind(self, count):
        """Rewind index."""

        if count > self._index:  # pragma: no cover
            raise ValueError("Can't rewind past beginning!")

        self._index -= count

    def iternext(self):
        """Iterate through characters of the string."""

        try:
            char = self._string[self._index]
            self._index += 1
        except IndexError:  # pragma: no cover
            raise StopIteration

        return char


class ExpandBrace(object):
    """Expand braces like in Bash."""

    def __init__(self, keep_escapes=False):
        """Initialize."""

        self.detph = 0
        self.expanding = False
        self.keep_escapes = keep_escapes

    def set_expanding(self):
        """Set that we are expanding a sequence, and return whether a release is required by the caller."""

        status = not self.expanding
        if status:
            self.expanding = True
        return status

    def is_expanding(self):
        """Get status of whether we are expanding."""

        return self.expanding

    def release_expanding(self, release):
        """Release the expand status."""

        if release:
            self.expanding = False

    def get_escape(self, c, i):
        """Get an escape."""

        try:
            escaped = next(i)
        except StopIteration:
            escaped = ''
        return c + escaped if self.keep_escapes else escaped

    def squash(self, a, b):
        """
        Returns a generator that squashes two iterables into one.

        ```
        ['this', 'that'], [[' and', ' or']] => ['this and', 'this or', 'that and', 'that or']
        ```
        """

        return ((''.join(x) if isinstance(x, tuple) else x) for x in itertools.product(a, b))

    def get_literals(self, c, i, depth):
        """
        Get a string literal.

        Gather all the literal chars up to opening curly or closing brace.
        Also gather chars between braces and commas within a group (is_expanding).
        """

        result = ['']
        is_dollar = False

        try:
            while c:
                ignore_brace = is_dollar
                is_dollar = False

                if c == '$':
                    is_dollar = True

                elif c == '\\':
                    c = [self.get_escape(c, i)]

                elif not ignore_brace and c == '{':
                    # Try and get the group
                    index = i.index
                    try:
                        seq = self.get_sequence(next(i), i, depth + 1)
                        if seq:
                            c = seq
                    except StopIteration:
                        # Searched to end of string
                        # and still didn't find it.
                        i.rewind(i.index - index)

                elif self.is_expanding() and c in (',', '}'):
                    # We are Expanding within a group and found a group delimiter
                    # Return what we gathered before the group delimiters.
                    i.rewind(1)
                    return (x for x in result)

                # Squash the current set of literals.
                result = self.squash(result, [c] if isinstance(c, str) else c)

                c = next(i)
        except StopIteration:
            if self.is_expanding():
                return None

        return (x for x in result)

    def combine(self, a, b):
        """A generator that combines two iterables."""

        for l in (a, b):
            for x in l:
                yield x

    def get_sequence(self, c, i, depth):
        """
        Get the sequence.

        Get sequence between `{}`, such as: `{a,b}`, `{1..2[..inc]}`, etc.
        It will basically crawl to the end or find a valid series.
        """

        result = []
        release = self.set_expanding()
        has_comma = False  # Used to indicate validity of group (`{1..2}` are an exception).
        is_empty = True  # Tracks whether the current slot is empty `{slot,slot,slot}`.

        # Detect numerical and alphabetic series: `{1..2}` etc.
        i.rewind(1)
        item = self.get_range(i)
        i.advance(1)
        if item is not None:
            self.release_expanding(release)
            return (x for x in item)

        try:
            while c:
                # Bash has some special top level logic. if `}` follows `{` but hasn't matched
                # a group yet, keep going except when the first 2 bytes are `{}` which gets
                # completely ignored.
                keep_looking = depth == 1 and not has_comma  # and i.index not in self.skip_index
                if (c == '}' and (not keep_looking or i.index == 2)):
                    # If there is no comma, we know the sequence is bogus.
                    if is_empty:
                        result = (x for x in self.combine(result, ['']))
                    if not has_comma:
                        result = ('{' + literal + '}' for literal in result)
                    self.release_expanding(release)
                    return (x for x in result)

                elif c == ',':
                    # Must be the first element in the list.
                    has_comma = True
                    if is_empty:
                        result = (x for x in self.combine(result, ['']))
                    else:
                        is_empty = True

                else:
                    if c == '}':
                        # Top level: If we didn't find a comma, we haven't
                        # completed the top level group. Request more and
                        # append to what we already have for the first slot.
                        if not result:
                            result = (x for x in self.combine(result, [c]))
                        else:
                            result = self.squash(result, [c])
                        value = self.get_literals(next(i), i, depth)
                        if value is not None:
                            result = self.squash(result, value)
                            is_empty = False
                    else:
                        # Lower level: Try to find group, but give up if cannot acquire.
                        value = self.get_literals(c, i, depth)
                        if value is not None:
                            result = (x for x in self.combine(result, value))
                            is_empty = False

                c = next(i)
        except StopIteration:
            self.release_expanding(release)
            raise

    def get_range(self, i):
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

        return None

    def format_value(self, value, padding):
        """Get padding adjusting for negative values."""

        # padding = padding - 1 if value < 0 and padding > 0 else padding
        # prefix = '-' if value < 0 else ''

        if padding:
            return "{:0{pad}d}".format(value, pad=padding)

        else:
            return str(value)

    def get_int_range(self, start, end, increment=None):
        """Get an integer range between start and end and increments of increment."""

        first, last = int(start), int(end)
        increment = int(increment) if increment is not None else 1
        max_length = max(len(start), len(end))

        # Zero doesn't make sense as an incrementer
        # but like bash, just assume one
        if increment == 0:
            increment = 1

        if start[0] == '-':
            start = start[1:]

        if end[0] == '-':
            end = end[1:]

        if (len(start) > 1 and start[0] == '0') or (len(end) > 1 and end[0] == '0'):
            padding = max_length

        else:
            padding = 0

        if first < last:
            r = range(first, last + 1, -increment if increment < 0 else increment)

        else:
            r = range(first, last - 1, increment if increment < 0 else -increment)

        return (self.format_value(value, padding) for value in r)

    def get_char_range(self, start, end, increment=None):
        """Get a range of alphabetic characters."""

        increment = int(increment) if increment else 1
        if increment < 0:
            increment = -increment

        # Zero doesn't make sense as an incrementer
        # but like bash, just assume one
        if increment == 0:
            increment = 1

        inverse = start > end
        alpha = _nalpha if inverse else _alpha

        start = alpha.index(start)
        end = alpha.index(end)

        if start < end:
            return (c for c in alpha[start:end + 1:increment])

        else:
            return (c for c in alpha[end:start + 1:increment])

    def expand(self, string):
        """Expand."""

        self.expanding = False
        empties = []
        found_literal = False
        if string:
            i = iter(StringIter(string))
            for x in self.get_literals(next(i), i, 0):
                # We don't want to return trailing empty strings.
                # Store empty strings and output only when followed by a literal.
                if not x:
                    empties.append(x)
                    continue
                found_literal = True
                while empties:
                    yield empties.pop(0)
                yield x
        empties = []

        # We found no literals so return an empty string
        if not found_literal:
            yield ""


def __getattr__(name):  # noqa: N807
    """Get attribute."""

    deprecated = __deprecated__.get(name)
    if deprecated:
        warnings.warn(
            "'{}' is deprecated. Use '{}' instead.".format(name, deprecated[0]),
            category=DeprecationWarning,
            stacklevel=(3 if PY37 else 4)
        )
        return deprecated[1]
    raise AttributeError("module '{}' has no attribute '{}'".format(__name__, name))


if not PY37:
    Pep562(__name__)
