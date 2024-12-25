"""
Advent of Code 2024
Day 25: Code Chronicle
https://adventofcode.com/2024/day/25
"""

from typing import Iterable

from common.file import relative_path
from common.text import line_groups


def part_1(locks: list['Lock'], keys: list['Key']) -> int:
    """
    Out of ideas and time, The Historians agree that they should go back to check the **Chief
    Historian's office** one last time, just in case he went back there without you noticing.

    When you get there, you are surprised to discover that the door to his office is **locked**!
    You can hear someone inside, but knocking yields no response. The locks on this floor are all
    fancy, expensive, virtual versions of five-pin tumbler locks, so you contact North Pole security
    to see if they can help open the door.

    Unfortunately, they've lost track of which locks are installed and which keys go with them, so
    the best they can do is send over **schematics of every lock and every key** for the floor
    you're on (your puzzle input).

    The schematics are in a cryptic file format, but they do contain manufacturer information,
    so you look up their support number.

    "Our Virtual Five-Pin Tumbler product? That's our most expensive model! Way more secure than--"
    You explain that you need to open a door and don't have a lot of time.

    "Well, you can't know whether a key opens a lock without actually trying the key in the lock
    (due to quantum hidden variables), but you **can** rule out some of the key/lock combinations."

    "The virtual system is complicated, but part of it really is a crude simulation of a five-pin
    tumbler lock, mostly for marketing reasons. If you look at the schematics, you can figure out
    whether a key could possibly fit in a lock."

    He transmits you some example schematics:

        >>> example_locks, example_keys = input_from_text('''
        ...     #####
        ...     .####
        ...     .####
        ...     .####
        ...     .#.#.
        ...     .#...
        ...     .....
        ...
        ...     #####
        ...     ##.##
        ...     .#.##
        ...     ...##
        ...     ...#.
        ...     ...#.
        ...     .....
        ...
        ...     .....
        ...     #....
        ...     #....
        ...     #...#
        ...     #.#.#
        ...     #.###
        ...     #####
        ...
        ...     .....
        ...     .....
        ...     #.#..
        ...     ###..
        ...     ###.#
        ...     ###.#
        ...     #####
        ...
        ...     .....
        ...     .....
        ...     .....
        ...     #....
        ...     #.#..
        ...     #.#.#
        ...     #####
        ... ''')

    "The locks are schematics that have the top row filled (`#`) and the bottom row empty (`.`);
    the keys have the top row empty and the bottom row filled. If you look closely, you'll see that
    each schematic is actually a set of columns of various heights, either extending downward from
    the top (for locks) or upward from the bottom (for keys)."

        >>> len(example_locks)
        2
        >>> len(example_keys)
        3

    "For locks, those are the pins themselves; you can convert the pins in schematics to a list of
    heights, one per column. For keys, the columns make up the shape of the key where it aligns with
    pins; those can also be converted to a list of heights."

    "So, you could say the first lock has pin heights `0,5,3,4,3`:"

        >>> example_locks[0]
        (0, 5, 3, 4, 3)

    "Or, that the first key has heights `5,0,2,1,3`:"

        >>> example_keys[0]
        (5, 0, 2, 1, 3)

    "These seem like they should fit together; in the first four columns, the pins and key don't
    overlap. However, this key **cannot** be for this lock: in the rightmost column, the lock's pin
    overlaps with the key, which you know because in that column the sum of the lock height and key
    height is more than the available space."

    "So anyway, you can narrow down the keys you'd need to try by just testing each key with each
    lock, which means you would have to check... wait, you have **how** many locks? But the only
    installation **that** size is at the North--" You disconnect the call.

    In this example, converting both locks to pin heights produces:

        >>> example_locks
        [(0, 5, 3, 4, 3), (1, 2, 0, 5, 3)]
        >>> lock_0, lock_1 = example_locks

    Converting all three keys to heights produces:

        >>> example_keys
        [(5, 0, 2, 1, 3), (4, 3, 4, 0, 2), (3, 0, 2, 0, 1)]
        >>> key_0, key_1, key_2 = example_keys

    Then, you can try every key with every lock:

        >>> fit(lock_0, key_0)  # (overlap in the last column)
        False
        >>> fit(lock_0, key_1)  # (overlap in the second column)
        False
        >>> fit(lock_0, key_2)
        True
        >>> fit(lock_1, key_0)  # (overlap in the first column)
        False
        >>> fit(lock_1, key_1)
        True
        >>> fit(lock_1, key_2)
        True

    So, in this example, the number of unique lock/key pairs that fit together without overlapping
    in any column is **`3`**.

    Analyze your lock and key schematics.
    **How many unique lock/key pairs fit together without overlapping in any column?**

        >>> part_1(example_locks, example_keys)
        part 1: there are 3 fitting lock/key pairs
        3
    """

    result = sum(1 for lock in locks for key in keys if fit(lock, key))

    print(f"part 1: there are {result} fitting lock/key pairs")
    return result


Lock = tuple[int, ...]
Key = tuple[int, ...]

LK_WIDTH = 5
LK_HEIGHT = 5


def fit(lock: Lock, key: Key) -> bool:
    return all(lock_h + key_h <= LK_HEIGHT for lock_h, key_h in zip(lock, key))


def input_from_file(fn: str) -> tuple[list[Lock], list[Key]]:
    return input_from_lines(open(relative_path(__file__, fn)))


def input_from_text(text: str) -> tuple[list[Lock], list[Key]]:
    return input_from_lines(text.strip().splitlines())


def input_from_lines(lines: Iterable[str]) -> tuple[list[Lock], list[Key]]:
    locks: list[Lock] = []
    keys: list[Key] = []

    for group in line_groups(lines):
        [group_width] = {len(line) for line in group}
        assert group_width == LK_WIDTH

        first_line, *payload, last_line = group
        assert len(payload) == LK_HEIGHT
        assert first_line != last_line

        heights = tuple(sum(1 for ch in col if ch == '#') for col in zip(*payload))

        [first_line_char] = set(first_line)
        match first_line_char:
            case '#':
                locks.append(heights)
            case '.':
                keys.append(heights)
            case _:
                raise ValueError(f"unexpected input char {first_line_char!r}")

    return locks, keys


def main(input_fn: str = 'data/25-input.txt') -> tuple[int]:
    locks, keys = input_from_file(input_fn)
    result_1 = part_1(locks, keys)
    return (result_1,)


if __name__ == '__main__':
    main()
