import functools
import os
import sys
import time
from itertools import chain
from itertools import combinations
from math import sqrt
from typing import Any
from typing import Callable
from typing import Generator
from typing import Iterable
from typing import Optional
from typing import Sized
from typing import TypeVar


# TODO: split utils into math, iteration, text, ...


T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
R = TypeVar('R')


# TODO: move to common.math
def gcd2(a: int, b: int) -> int:
    if a == 0 or b == 0:
        raise ZeroDivisionError("integer division or modulo by zero")
    a, b = abs(a), abs(b)
    if a == b:
        return a
    if a < b:
        a, b = b, a
    while a % b > 0:
        a, b = b, a % b
    return b


# TODO: move to common.math
def gcd(*xs: int) -> Optional[int]:
    result = None
    for x in xs:
        result = gcd2(result, x) if result is not None else x
    return result


# TODO: move to common.math
def lcm2(a: int, b: int) -> int:
    return abs(a * b) // gcd2(a, b)


# TODO: move to common.math
def lcm(*xs: int) -> Optional[int]:
    result = None
    for x in xs:
        result = lcm2(result, x) if result is not None else x
    return result


# TODO: move to common.math
def modular_inverse(x: int, m: int) -> int:
    t, newt = 0, 1
    r, newr = m, x % m
    while newr != 0:
        quotient = r // newr
        t, newt = newt, t - quotient * newt
        r, newr = newr, r - quotient * newr
    if r > 1:
        raise ValueError(f"no modular inverse for 1/{x} mod {m}")
    return t % m


# TODO: move to common.math
def triangular_root(t: int) -> int:
    """
    Given a number `t`, find `n` such that `tr(n) <= t < tr(n+1)`.

    Perfect roots:

        >>> triangular_root(10)
        4
        >>> triangular_root(15)
        5
        >>> triangular_root(5050)
        100

    Close roots:

    tr(4) = 10 <= 12 < 15 = tr(4+1)

        >>> triangular_root(12)
        4

    tr(44) = 990 <= 1000 < 1035 = tr(44+1)

        >>> triangular_root(1000)
        44
        >>> triangular_root(990)
        44
        >>> triangular_root(1034)
        44
        >>> triangular_root(1035)
        45
    """

    # (n+1) * (n/2) = t
    # (n^2 + n) / 2 = t
    #     4n^2 + 4n = 8t
    # 4n^2 + 4n + 1 = 8t + 1
    #    (2n + 1)^2 = 8t + 1
    #        2n + 1 = sqrt(8t + 1)
    #            2n = sqrt(8t + 1) - 1
    #             n = (sqrt(8t + 1) - 1) / 2

    return int((sqrt(8 * t + 1) - 1) / 2)


# TODO: move to common.math
def sgn(x) -> int:
    """
    >>> sgn(-15)
    -1
    >>> sgn(1/3)
    1
    >>> sgn(0)
    0
    >>> sgn(0.0)
    0
    """
    if x > 0:
        return +1
    elif x < 0:
        return -1
    else:
        return 0


# TODO: move to common.iteration
def first(items: Iterable[T], default: T = None) -> Optional[T]:
    return next(iter(items), default)


# TODO: move to common.iteration
def last(items: Iterable[T], default: T = None) -> Optional[T]:
    last_item = default
    for item in items:
        last_item = item
    return last_item


# TODO: move to common.iteration
def single_value(items: Iterable[T]) -> T:
    """
    Return the first element of an iterable if it has exactly one element:

        >>> single_value(['cat'])
        'cat'
        >>> single_value((x for x in range(10) if x % 7 == 5))
        5
        >>> single_value({'x': 4}.items())
        ('x', 4)

    If the iterable has more than one element, error is raised:

        >>> single_value(['cat', 'dog'])
        Traceback (most recent call last):
        ...
        ValueError: items contain 2 elements (expected 1)
        >>> single_value((x for x in range(10) if x % 7 == 1))
        Traceback (most recent call last):
        ...
        ValueError: items contain more than one element

    If it has no elements, error is also raised:

        >>> single_value([])
        Traceback (most recent call last):
        ...
        ValueError: items contain 0 elements (expected 1)
        >>> single_value((x for x in range(10) if x % 13 == 12))
        Traceback (most recent call last):
        ...
        ValueError: items contain no elements
    """
    if isinstance(items, Sized):
        if len(items) != 1:
            raise ValueError(f"items contain {len(items)} elements (expected 1)")
        return next(iter(items))

    else:
        iterator = iter(items)
        try:
            element1 = next(iterator)
        except StopIteration as stop:
            raise ValueError("items contain no elements") from stop

        try:
            next(iterator)
        except StopIteration:
            # that's ok! we didn't actually expect another element
            return element1
        else:
            raise ValueError("items contain more than one element")


# TODO: move to common.iteration
def exhaust(gen: Generator[Any, Any, T]) -> T:
    try:
        while True:
            next(gen)
    except StopIteration as exc:
        return exc.value


# TODO: move to common.iteration
def dgroupby(
        items: Iterable[T],
        key: Callable[[T], K],
        value: Callable[[T], V] = lambda t: t
) -> dict[K, list[V]]:
    d: dict[K, list[V]] = {}

    for item in items:
        item_key, item_value = key(item), value(item)
        if item_key not in d:
            d[item_key] = []
        d[item_key].append(item_value)

    return d


# TODO: move to common.iteration
def dgroupby_set(
        items: Iterable[T],
        key: Callable[[T], K],
        value: Callable[[T], V] = lambda t: t
) -> dict[K, set[V]]:
    d: dict[K, set[V]] = {}

    for item in items:
        item_key, item_value = key(item), value(item)
        if item_key not in d:
            d[item_key] = set()
        d[item_key].add(item_value)

    return d


# TODO: move to common.iteration
def dgroupby_pairs(items: Iterable[tuple[K, V]]) -> dict[K, list[V]]:
    d: dict[K, list[V]] = {}

    for item_key, item_value in items:
        if item_key not in d:
            d[item_key] = []
        d[item_key].append(item_value)

    return d


# TODO: move to common.iteration
def dgroupby_pairs_set(items: Iterable[tuple[K, V]]) -> dict[K, set[V]]:
    d: dict[K, set[V]] = {}

    for item_key, item_value in items:
        if item_key not in d:
            d[item_key] = set()
        d[item_key].add(item_value)

    return d


# TODO: move to common.iteration
def separate(values: Iterable[V], predicate: Callable[[V], bool]) -> tuple[list[V], list[V]]:
    """
    Returns two list:
    - the first one contains values that match the given `predicate`,
    - the second one contains values that don't.

        >>> animals = ['dog', 'cat', 'monkey', 'rat', 'ox']
        >>> has_three_letters = lambda x: len(x) == 3
        >>> three_lettered_animals, other_animals = separate(animals, has_three_letters)
        >>> three_lettered_animals
        ['dog', 'cat', 'rat']
        >>> other_animals
        ['monkey', 'ox']
    """
    matching_values, nonmatching_values = [], []

    for value in values:
        (matching_values if predicate(value) else nonmatching_values).append(value)

    return matching_values, nonmatching_values


# TODO: move to common.iteration
def ilen(items: Iterable) -> int:
    return sum(1 for _ in items)


# TODO: delete
def timeit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        eprint(f"{func.__name__} took {round(end-start, 4)} seconds")
        return result
    return wrapper


# TODO: move to common.iteration
def zip1(items: Iterable[T], wrap: bool = False) -> Iterable[tuple[T, T]]:
    """
    >>> list(zip1([1,2,3,4]))
    [(1, 2), (2, 3), (3, 4)]
    >>> list(zip1([1,2,3,4], wrap=True))
    [(1, 2), (2, 3), (3, 4), (4, 1)]
    >>> list(zip1([], wrap=True))
    []
    """
    first_item = None
    last_item = None
    yielded_count = 0

    for item in items:
        if last_item is not None:
            yield last_item, item
            yielded_count += 1
        else:
            first_item = item
        last_item = item

    if wrap and yielded_count > 0:
        yield last_item, first_item


# TODO: delete?
def diffs(items: Iterable[T]) -> Iterable[T]:
    return (b - a for a, b in zip1(items))


# TODO: move to common.iteration
def slidingw(items: Iterable[T], size: int, wrap: bool = False) -> Iterable[tuple[T, ...]]:
    """
    >>> list(slidingw([1,2,3,4], 2))
    [(1, 2), (2, 3), (3, 4)]
    >>> list(slidingw([1,2,3,4,5], 3))
    [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
    >>> list(slidingw([1,2,3], 3))
    [(1, 2, 3)]
    >>> list(slidingw([1,2,3], 4))
    []
    >>> list(slidingw([], 1))
    []

    >>> list(slidingw([1,2,3,4], 2, wrap=True))
    [(1, 2), (2, 3), (3, 4), (4, 1)]
    >>> list(slidingw([1,2,3,4,5], 3, wrap=True))
    [(1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 1), (5, 1, 2)]
    >>> list(slidingw([1,2,3], 3, wrap=True))
    [(1, 2, 3), (2, 3, 1), (3, 1, 2)]
    >>> list(slidingw([], 1, wrap=True))
    []
    """
    buffer = []
    first_items = None

    for item in items:
        buffer.append(item)
        if len(buffer) == size:
            yield tuple(buffer)
            del buffer[0]
        elif wrap and len(buffer) == size - 1:
            first_items = list(buffer)

    if wrap and first_items:
        for item in first_items:
            buffer.append(item)
            yield tuple(buffer)
            del buffer[0]


# TODO: move to common.iteration
def minmax(values: Iterable[T], key: Callable[[T], K] = None) -> tuple[T, T]:
    """
        >>> minmax([1,4,8,10,4,-4,15,-2])
        (-4, 15)
        >>> minmax(["cat", "dog", "antelope"])
        ('antelope', 'dog')
        >>> minmax(["cat", "dog", "antelope"], key=len)
        ('cat', 'antelope')
        >>> minmax([4,4,4])
        (4, 4)
        >>> minmax([3])
        (3, 3)
        >>> minmax([])
        Traceback (most recent call last):
        ...
        ValueError: minmax() arg is an empty sequence
    """
    min_k, max_k = None, None
    min_v, max_v = None, None
    any_value = False

    for value in values:
        k = key(value) if key is not None else value
        if min_k is None or k < min_k:
            min_k, min_v = k, value
        if max_k is None or k > max_k:
            max_k, max_v = k, value
        any_value = True

    if any_value:
        return min_v, max_v
    else:
        raise ValueError("minmax() arg is an empty sequence")


# TODO: move to common.iteration
def maxk(values: Iterable[T], key: Callable[[T], V]) -> tuple[T, V]:
    """
        >>> maxk(["dog", "cat", "monkey"], key=len)
        ('monkey', 6)
        >>> maxk([1, 5, 10, 20], key=str)
        (5, '5')
        >>> maxk([], key=lambda x: 1)
        Traceback (most recent call last):
        ...
        ValueError: maxk() arg is an empty sequence
    """
    max_k = None
    max_v = None
    any_value = False

    for value in values:
        k = key(value)
        if max_k is None or k > max_k:
            max_k, max_v = k, value
        any_value = True

    if any_value:
        return max_v, max_k
    else:
        raise ValueError("maxk() arg is an empty sequence")


# TODO: move to common.iteration
def mink(values: Iterable[T], key: Callable[[T], V]) -> tuple[T, V]:
    """
        >>> mink(["dog", "zebra", "monkey"], key=len)
        ('dog', 3)
        >>> mink([5, 6, 8, 10, 12], key=str)
        (10, '10')
        >>> mink([], key=lambda x: 1)
        Traceback (most recent call last):
        ...
        ValueError: mink() arg is an empty sequence
    """
    min_k = None
    min_v = None
    any_value = False

    for value in values:
        k = key(value)
        if min_k is None or k < min_k:
            min_k, min_v = k, value
        any_value = True

    if any_value:
        return min_v, min_k
    else:
        raise ValueError("mink() arg is an empty sequence")


# TODO: move to common.iteration
def min_all(values: Iterable[T], key: Callable[[T], V] = None) -> list[T]:
    """
        >>> min_all([1,2,3,1,2,3,1,2,3])
        [1, 1, 1]
        >>> min_all(["dog", "cat", "monkey", "antelope", "snake", "ant"], key=len)
        ['dog', 'cat', 'ant']
        >>> min_all(["dog", "cat", "monkey", "antelope", "snake", "ant"], key=lambda s: s[0])
        ['antelope', 'ant']
        >>> min_all([1, 2, 3])
        [1]
        >>> min_all([1])
        [1]
        >>> min_all([])
        Traceback (most recent call last):
        ...
        ValueError: min_all() arg is an empty sequence
    """
    min_k = None
    min_vs = None

    for value in values:
        k = key(value) if key else value
        if min_k is None or k < min_k:
            min_k = k
            min_vs = [value]
        elif k == min_k:
            min_vs.append(value)

    if min_vs is not None:
        return min_vs
    else:
        raise ValueError("min_all() arg is an empty sequence")


# TODO: move to common.iteration
def max_all(values: Iterable[T], key: Callable[[T], V] = None) -> list[T]:
    """
        >>> max_all([1,2,3,1,2,3,1,2,3])
        [3, 3, 3]
        >>> max_all(["dog", "cat", "monkey", "donkey", "snake", "ant"], key=len)
        ['monkey', 'donkey']
        >>> max_all([1, 2, 3])
        [3]
        >>> max_all([1])
        [1]
        >>> max_all([])
        Traceback (most recent call last):
        ...
        ValueError: max_all() arg is an empty sequence
    """
    max_k = None
    max_vs = None

    for value in values:
        k = key(value) if key else value
        if max_k is None or k > max_k:
            max_k = k
            max_vs = [value]
        elif k == max_k:
            max_vs.append(value)

    if max_vs is not None:
        return max_vs
    else:
        raise ValueError("max_all() arg is an empty sequence")


# TODO: move to common.iteration
def picking(items: Iterable[T]) -> Iterable[tuple[T, list[T]]]:
    """
    >>> list(picking('ABC'))
    [('A', ['B', 'C']), ('B', ['A', 'C']), ('C', ['A', 'B'])]
    >>> list(picking(range(1, 6)))
    [(1, [2, 3, 4, 5]), (2, [1, 3, 4, 5]), (3, [1, 2, 4, 5]), (4, [1, 2, 3, 5]), (5, [1, 2, 3, 4])]
    >>> list(picking([1]))
    [(1, [])]
    >>> list(picking([]))
    []
    """
    items = list(items)
    for k, item in enumerate(items):
        yield item, items[:k]+items[k+1:]


# TODO: move to common.iteration
def following(items: Iterable[T]) -> Iterable[tuple[T, list[T]]]:
    """
    >>> list(following('ABC'))
    [('A', ['B', 'C']), ('B', ['C']), ('C', [])]
    >>> list(following(range(1, 6)))
    [(1, [2, 3, 4, 5]), (2, [3, 4, 5]), (3, [4, 5]), (4, [5]), (5, [])]
    >>> list(following([1]))
    [(1, [])]
    >>> list(following([]))
    []
    """
    items = list(items)
    for k, item in enumerate(items):
        yield item, items[k+1:]


# TODO: move to common.iteration
def subsequences(items: T) -> Iterable[T]:
    """
    >>> list(subsequences('AB'))
    ['AB', 'B', 'A', '']
    >>> list(subsequences([1,2,3]))
    [[1, 2, 3], [2, 3], [1, 3], [3], [1, 2], [2], [1], []]
    >>> list(subsequences(tuple(range(2))))
    [(0, 1), (1,), (0,), ()]
    """
    if items:
        for subseq in subsequences(items[1:]):
            yield items[:1] + subseq
            yield subseq
    else:
        yield items


# TODO: move to common.iteration
def powerset(items: Iterable[T]) -> Iterable[tuple[T, ...]]:
    """
    >>> list(powerset([1, 2, 3]))
    [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
    """
    items = list(items)
    return chain.from_iterable(
        combinations(items, r)
        for r in range(len(items) + 1)
    )


# TODO: move to common.logging?
def ilog(
        items: Iterable[T],
        formatter: Callable[[int, T], str] = None,
        every: int = 1
) -> Iterable[T]:
    for index, item in enumerate(items):
        if index % every == 0:
            if formatter:
                eprint(formatter(index, item))
            else:
                eprint('>', index, item)
        yield item


# TODO: move to common.math
def constrained(value, min_value, max_value):
    if value < min_value:
        return min_value
    elif max_value < value:
        return max_value
    else:
        return value


# TODO: delete
def until_repeat(values: Iterable[T]) -> Generator[T, None, T | None]:
    """
        >>> nums = [1, 4, 2, 5, 3, 6, 4, 7, 5, 1]
        >>> list(until_repeat(nums))
        [1, 4, 2, 5, 3, 6]
    """
    seen: set[T] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            yield value
        else:
            return value

    return None


# TODO: move to common.iteration
def first_repeat(values: Iterable[T]) -> T | None:
    """
        >>> first_repeat([1, 3, 5, 4, 6, 2, 3, 7])
        3
        >>> first_repeat('mississippi')
        's'
        >>> first_repeat('abcd') is None
        True
    """
    return exhaust(until_repeat(values))


# TODO: move to common.iteration
def unique(values: Iterable[T]) -> Iterable[T]:
    """
    Like set, but retains order:

        >>> list(unique(['dog', 'cat', 'dog', 'elephant', 'elephant', 'cat', 'ox', 'dog']))
        ['dog', 'cat', 'elephant', 'ox']
    """
    seen: set[T] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            yield value


# TODO: delete?
def count_ones(bytes_: bytes) -> int:
    return sum(bin(byte).count('1') for byte in bytes_)


# TODO: move to common.logging
def create_logger(debug: bool = False) -> Callable[[Any], None]:
    if debug:
        def log(*args, **kwargs):
            eprint(*args, **kwargs)
        return log
    else:
        def nolog(_):
            pass
        return nolog


# TODO: move to common.text
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


# TODO: move to common.text
def _parse_line_fixes(line: str, *fixes: str) -> tuple[str, ...]:
    assert len(fixes) >= 2

    results = []

    for fix1, fix2 in slidingw(fixes, 2):
        assert line.startswith(fix1), (line, fix1)
        line = line[len(fix1):]
        if fix2:
            pos2 = line.index(fix2)
            results.append(line[:pos2])
            line = line[pos2:]
        else:
            results.append(line)
            line = ''

    assert line == fixes[-1], f"{line!r} != {fixes[-1]!r}"
    return tuple(results)


# TODO: move to common.text?
def strip_line(line: str, prefix: str, suffix: str) -> str:
    """
    >>> strip_line("What is love?", "What is ", "?")
    'love'
    """
    return single_value(_parse_line_fixes(line, prefix, suffix))


# TODO: move to common.iteration?
# pylint: disable=invalid-name
def ro(pos: tuple[int, int]) -> tuple[int, int]:
    # reading order -> y matters more than x
    x, y = pos
    return y, x


# TODO: move to common.text
def string_builder(delimiter: str = "\n"):
    """
    >>> @string_builder(" + ")
    ... def the_beatles():
    ...     yield "John"
    ...     yield "Paul"
    ...     yield "George"
    ...     for _ in range(3):
    ...         yield "Ringo"
    >>> the_beatles()
    'John + Paul + George + Ringo + Ringo + Ringo'
    """

    def decorator(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs) -> str:
            return delimiter.join(fn(*args, **kwargs))

        return wrapped

    return decorator


# TODO: move to common.text
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


# TODO: move to common.text
def join_and(items: Iterable[Any], oxford_comma=False) -> str:
    """
    >>> join_and(["spam", "spam", "spam", "bacon", "eggs"])
    'spam, spam, spam, bacon and eggs'
    >>> join_and(["Michael", "Franklin", "Trevor"], oxford_comma=True)
    'Michael, Franklin, and Trevor'
    """
    return join_english(items, conj=", and " if oxford_comma else " and ")


# TODO: move to common.text
def join_or(items: Iterable[Any], oxford_comma=False) -> str:
    """
    >>> join_or([1, True, "cheddar"])
    '1, True or cheddar'
    >>> join_or(["Eric", "Stan", "Kyle"], oxford_comma=True)
    'Eric, Stan, or Kyle'
    """
    return join_english(items, conj=", or " if oxford_comma else " or ")


# TODO: move to common.text ... may be utilized in more places?
def line_groups(lines: Iterable[str]) -> Iterable[list[str]]:
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
        if line.strip():
            buffer.append(line.strip())
        else:
            yield buffer
            buffer = []

    if buffer:
        yield buffer


# TODO: move to common.logging
def eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


def assert_single_not_none(**kwargs: T) -> tuple[str, T]:
    """
        >>> assert_single_not_none(x=1, y=None, z=None)
        ('x', 1)
        >>> assert_single_not_none(x=1, y=2, z=None)
        Traceback (most recent call last):
        ...
        AssertionError: multiple keys were not None: x=1, y=2
        >>> assert_single_not_none(x=None, y=None, z=None)
        Traceback (most recent call last):
        ...
        AssertionError: all keys were None: x=None, y=None, z=None
    """
    not_none_count = sum(v is not None for v in kwargs.values())

    if not_none_count == 1:
        return single_value((k, v) for k, v in kwargs.items() if v is not None)
    elif not_none_count == 0:
        items_text = ", ".join(f"{k}=None" for k in kwargs)
        raise AssertionError(f"all keys were None: {items_text}")
    else:  # not_none_count > 1
        items_text = ", ".join(f"{k}={v!r}" for k, v in kwargs.items() if v is not None)
        raise AssertionError(f"multiple keys were not None: {items_text}")


def relative_path(file: str, *path: str) -> str:
    location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(file)))
    return os.path.join(location, *path)


def sorted_keys(d: dict[str, Any]) -> dict[str, Any]:
    """
    Useful in doctests:

        >>> sorted_keys({'x': 1, 'a': 2, 'y': 3, 'b': 4, 'w':5})
        {'a': 2, 'b': 4, 'w': 5, 'x': 1, 'y': 3}
    """

    return dict(sorted((k, v) for k, v in d.items()))


# TODO: move to common.text
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
