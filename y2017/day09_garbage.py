from typing import Generator
from typing import Tuple

from utils import exhaust

Group = Tuple[int, int, int]


def find_groups(text: str) -> Generator[Group, None, int]:
    """
    >>> list(find_groups('{}'))
    [(0, 1, 1)]
    >>> list(find_groups('{{{}}}'))
    [(2, 3, 3), (1, 4, 2), (0, 5, 1)]
    >>> list(find_groups('{{},{}}'))
    [(1, 2, 2), (4, 5, 2), (0, 6, 1)]
    >>> list(find_groups('{{{},{},{{}}}}'))
    [(2, 3, 3), (5, 6, 3), (9, 10, 4), (8, 11, 3), (1, 12, 2), (0, 13, 1)]
    >>> list(find_groups('{<{},{},{{}}>}'))
    [(0, 13, 1)]
    >>> list(find_groups('{<a>,<a>,<a>,<a>}'))
    [(0, 16, 1)]
    >>> list(find_groups('{{<a>},{<a>},{<a>},{<a>}}'))
    [(1, 5, 2), (7, 11, 2), (13, 17, 2), (19, 23, 2), (0, 24, 1)]
    >>> list(find_groups('{{<!>},{<!>},{<!>},{<a>}}'))
    [(1, 23, 2), (0, 24, 1)]
    >>> list(find_groups('{{<a!>},{<a!>},{<a!>},{<ab>}}'))
    [(1, 27, 2), (0, 28, 1)]
    >>> list(find_groups('{{<!!>},{<!!>},{<!!>},{<!!>}}'))
    [(1, 6, 2), (8, 13, 2), (15, 20, 2), (22, 27, 2), (0, 28, 1)]
    """

    starts_buffer = []
    in_garbage = False
    ignore_next = False
    garbage_collected = 0

    for k, c in enumerate(text):
        if not in_garbage:
            # outside of garbage
            if c == '{':
                starts_buffer.append(k)
            elif c == '}':
                depth = len(starts_buffer)
                start = starts_buffer.pop()
                end = k
                yield (start, end, depth)
            elif c == '<':
                in_garbage = True
        else:
            # in garbage
            if ignore_next:
                ignore_next = False
            elif c == '>':
                in_garbage = False
            elif c == '!':
                ignore_next = True
            else:
                garbage_collected += 1

    return garbage_collected


def group_score(text: str) -> int:
    """
    >>> group_score('{}')
    1
    >>> group_score('{{{}}}')
    6
    >>> group_score('{{},{}}')
    5
    >>> group_score('{{{},{},{{}}}}')
    16
    >>> group_score('{<{},{},{{}}>}')
    1
    >>> group_score('{<a>,<a>,<a>,<a>}')
    1
    >>> group_score('{{<a>},{<a>},{<a>},{<a>}}')
    9
    >>> group_score('{{<!>},{<!>},{<!>},{<a>}}')
    3
    >>> group_score('{{<a!>},{<a!>},{<a!>},{<ab>}}')
    3
    >>> group_score('{{<!!>},{<!!>},{<!!>},{<!!>}}')
    9
    """
    return sum(depth for _, _, depth in find_groups(text))


def count_garbage(text: str) -> int:
    """
    >>> count_garbage('<>')
    0
    >>> count_garbage('<random characters>')
    17
    >>> count_garbage('<<<<>')
    3
    >>> count_garbage('<{!>}>')
    2
    >>> count_garbage('<!!>')
    0
    >>> count_garbage('<{o"i!a,<{i<a>')
    10
    """
    return exhaust(find_groups(text))


if __name__ == '__main__':
    text_ = open("data/09-input.txt").readline().strip()
    print(f"part 1: total group score is {group_score(text_)}")
    print(f"part 2: {count_garbage(text_)} garbage collected")
