"""
Working with spiral numbers:

    >>> print(drawn(range(50)))
    36  35  34  33  32  31  30
    37  16  15  14  13  12  29
    38  17   4   3   2  11  28
    39  18   5 [ 0]  1  10  27
    40  19   6   7   8   9  26
    41  20  21  22  23  24  25
    42  43  44  45  46  47  48  49
    >>> to_pos(13)
    (1, -2)
    >>> from_pos((3, 2))
    25
"""

import math
from textwrap import dedent
from typing import Iterable

from common.math import triangular_root

Pos = tuple[int, int]


def layer_index(number: int) -> int:
    """
    In what layer is the given number present?

        >>> layer_index(0)
        0
        >>> layer_index(1)
        1
        >>> layer_index(8)
        1
        >>> layer_index(9)
        2
        >>> layer_index(24)
        2
        >>> layer_index(25)
        3
        >>> layer_index(48)
        3
        >>> layer_index(49)
        4
    """

    assert number >= 0
    if number == 0:
        return 0

    return triangular_root(math.ceil(number / 8) - 1) + 1


def layer_offset(layer_number: int) -> int:
    """
    Returns the first number present in given layer:

        >>> [layer_offset(ln) for ln in range(6)]
        [0, 1, 9, 25, 49, 81]
    """

    return (2 * layer_number - 1) ** 2 if layer_number > 0 else 0


def to_pos(number: int) -> Pos:
    """
    Return coordinates of given number in the spiral:

        >>> to_pos(0)
        (0, 0)
        >>> [to_pos(n) for n in range(1, 9)]
        [(1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]
        >>> [to_pos(n) for n in range(9, 27, 3)]
        [(2, 1), (2, -2), (-1, -2), (-2, 0), (-1, 2), (2, 2)]
        >>> [to_pos(n) for n in [25, 33, 34, 42, 44, 50]]
        [(3, 2), (0, -3), (-1, -3), (-3, 3), (-1, 3), (4, 2)]
    """

    assert number >= 0
    if number == 0:
        return 0, 0

    layer = layer_index(number)
    index_in_layer = number - layer_offset(layer)
    side = index_in_layer // (2 * layer)
    index_in_side = index_in_layer - (2 * layer * side) + 1

    if side == 0:  # right
        return layer, layer - index_in_side
    elif side == 1:  # up
        return layer - index_in_side, -layer
    elif side == 2:  # left
        return -layer, index_in_side - layer
    elif side == 3:  # down
        return index_in_side - layer, layer
    else:
        raise ValueError(side)


def from_pos(pos: Pos) -> int:
    """
    Returns spiral number for given position.

        >>> [n for n in range(1, 100) if from_pos(to_pos(n)) != n]
        []
    """
    if pos == (0, 0):
        return 0

    x, y = pos
    layer = max(abs(x), abs(y))
    offset = layer_offset(layer)

    if x == layer and y < layer:
        # right: (x=3, y=2..-3)
        return offset + layer - y - 1
    elif x < layer and y == -layer:
        # up:    (x=2..-3, y=-3)
        return offset + 3 * layer - x - 1
    elif x == -layer and y > -layer:
        # left:  (x=-3, y=-2..3)
        return offset + 5 * layer + y - 1
    elif x > -layer and y == layer:
        # down:  (x=-2..3, y=3)
        return offset + 7 * layer + x - 1
    else:
        raise ValueError(pos)


def drawn(values: Iterable) -> str:
    values = [str(value) for value in values]
    last_layer = layer_index(len(values) - 1)
    max_width = max(len(value) for value in values)
    empty = " " * (max_width + 2)

    def num_f(pos) -> str:
        index = from_pos(pos)
        if index < len(values):
            value = values[index].rjust(max_width)
            return f"[{value}]" if index == 0 else f" {value} "
        else:
            return empty

    range_ = range(-last_layer, last_layer + 1)

    return dedent(
        "\n".join(
            line
            for y in range_
            if (line := "".join(num_f((x, y)) for x in range_).rstrip())
        )
    )
