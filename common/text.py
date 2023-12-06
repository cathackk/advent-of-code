from typing import Any, Iterator
from typing import Iterable

from common.iteration import single_value
from common.iteration import slidingw


class ParseError(Exception):
    pass


def parse_line(line: str, pattern: str) -> tuple[str, ...]:
    r"""
        >>> parse_line("Dogs have four paws.", "Dogs have $ paws.")
        ('four',)
        >>> parse_line("Humans have two eyes and four limbs.", "Humans have $ eyes and $ limbs.")
        ('two', 'four')
        >>> parse_line("1,2:3x4", "$,$:$x$")
        ('1', '2', '3', '4')
    """
    fixes = pattern.split('$')
    if len(fixes) >= 2:
        return _parse_line_fixes(line, *fixes)
    else:
        return tuple()


def _parse_line_fixes(line: str, *fixes: str) -> tuple[str, ...]:
    assert len(fixes) >= 2

    results = []

    for fix1, fix2 in slidingw(fixes, 2):
        if not line.startswith(fix1):
            raise ParseError(
                f"expected input to start with {fix1!r}, instead starts with {line[:len(fix1)]!r}"
            )

        line = line[len(fix1):]
        if fix2:
            try:
                pos2 = line.index(fix2)
            except ValueError as exc:
                raise ValueError(f"substring {fix2!r} not found in {line!r}") from exc
            results.append(line[:pos2])
            line = line[pos2:]
        else:
            results.append(line)
            line = ''

    if line != fixes[-1]:
        raise ParseError(f"expected: {fixes[-1]!r}, got: {line!r}")

    return tuple(results)


def strip_line(line: str, prefix: str, suffix: str) -> str:
    """
    >>> strip_line("What is love?", "What is ", "?")
    'love'
    """
    return single_value(_parse_line_fixes(line, prefix, suffix))


def join_english(items: Iterable[Any], conj=" and "):
    """
        >>> join_english([1, 2, 3])
        '1, 2 and 3'
        >>> join_english(['John', 'Paul', 'George', 'Ringo'])
        'John, Paul, George and Ringo'
        >>> join_english(('Zelda', 'Zoe'))
        'Zelda and Zoe'
        >>> join_english(['Bob'])
        'Bob'
        >>> join_english([])
        ''
    """
    items_list = list(items)
    if len(items_list) > 1:
        return ", ".join(str(v) for v in items_list[:-1]) + conj + str(items_list[-1])
    else:
        return ", ".join(str(v) for v in items_list)


def join_and(items: Iterable[Any], oxford_comma=False) -> str:
    """
        >>> join_and(["spam", "spam", "spam", "bacon", "eggs"])
        'spam, spam, spam, bacon and eggs'
        >>> join_and(["Michael", "Franklin", "Trevor"], oxford_comma=True)
        'Michael, Franklin, and Trevor'
    """
    return join_english(items, conj=", and " if oxford_comma else " and ")


def join_or(items: Iterable[Any], oxford_comma=False) -> str:
    """
        >>> join_or([1, True, "cheddar"])
        '1, True or cheddar'
        >>> join_or(["Eric", "Stan", "Kyle"], oxford_comma=True)
        'Eric, Stan, or Kyle'
    """
    return join_english(items, conj=", or " if oxford_comma else " or ")


def line_groups(lines: Iterable[str], lstrip: bool = True) -> Iterator[list[str]]:
    r"""
    Separate stream of lines into groups of whitespace-stripped lines.
    Empty line (containing only whitespace) serves as separator.

        >>> list(line_groups(["aaa\n", "bbb\n", "\n", "ccc\n", "ddd"]))
        [['aaa', 'bbb'], ['ccc', 'ddd']]
        >>> list(line_groups(["aaa"]))
        [['aaa']]
        >>> list(line_groups(["aaa\n"]))
        [['aaa']]
        >>> list(line_groups(["aaa\n", "\n", "\n", "bbb\n"]))
        [['aaa'], [], ['bbb']]
        >>> list(line_groups(["\n"]))
        [[]]
    """
    buffer = []

    for line in lines:
        if (line_stripped := line.strip()):
            buffer.append(line_stripped if lstrip else line)
        else:
            yield buffer
            buffer = []

    if buffer:
        yield buffer


def abc_rot(letter: str, diff: int) -> str:
    """
        >>> abc_rot('A', 1)
        'B'
        >>> abc_rot('B', 2)
        'D'
        >>> abc_rot('X', 3)
        'A'
        >>> abc_rot('a', 4)
        'e'
        >>> abc_rot('t', 5)
        'y'
        >>> abc_rot('y', 6)
        'e'
        >>> abc_rot('B', -1)
        'A'
        >>> abc_rot('B', -2)
        'Z'
        >>> abc_rot('q', -3)
        'n'
        >>> abc_rot('c', -4)
        'y'
    """
    assert len(letter) == 1

    if letter.islower():
        first_letter = 'a'
    elif letter.isupper():
        first_letter = 'A'
    else:
        raise ValueError(letter)

    return chr((ord(letter) - ord(first_letter) + diff) % 26 + ord(first_letter))
