import functools
import sys
import time
from itertools import chain
from itertools import combinations
from typing import Any
from typing import Callable
from typing import Dict
from typing import Generator
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Set
from typing import Sized
from typing import Tuple
from typing import TypeVar


T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')
R = TypeVar('R')


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


def gcd(*xs: int) -> Optional[int]:
    result = None
    for x in xs:
        result = gcd2(result, x) if result is not None else x
    return result


def lcm2(a: int, b: int) -> int:
    g = gcd2(a, b)
    return abs(a * b) // g


def lcm(*xs: int) -> Optional[int]:
    result = None
    for x in xs:
        result = lcm2(result, x) if result is not None else x
    return result


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


def first(items: Iterable[T], default: T = None) -> Optional[T]:
    return next(iter(items), default)


def last(items: Iterable[T], default: T = None) -> Optional[T]:
    last_item = default
    for item in items:
        last_item = item
    return last_item


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
        ValueError: items contains 2 elements (expected 1)
        >>> single_value((x for x in range(10) if x % 7 == 1))
        Traceback (most recent call last):
        ...
        ValueError: items contains more than one element

    If it has no elements, error is also raised:

        >>> single_value([])
        Traceback (most recent call last):
        ...
        ValueError: items contains 0 elements (expected 1)
        >>> single_value((x for x in range(10) if x % 13 == 12))
        Traceback (most recent call last):
        ...
        ValueError: items contains no elements
    """
    if isinstance(items, Sized):
        if len(items) != 1:
            raise ValueError(f"items contains {len(items)} elements (expected 1)")
        return next(iter(items))

    else:
        iterator = iter(items)
        try:
            element1 = next(iterator)
        except StopIteration:
            raise ValueError("items contains no elements")

        try:
            next(iterator)
        except StopIteration:
            # that's ok! we didn't actually expect another element
            return element1
        else:
            raise ValueError("items contains more than one element")


def exhaust(g: Generator[Any, Any, T]) -> T:
    try:
        while True:
            next(g)
    except StopIteration as exc:
        return exc.value


def dgroupby(
        items: Iterable[T],
        key: Callable[[T], K],
        value: Callable[[T], V]
) -> Dict[K, List[V]]:
    d: Dict[K, List[V]] = dict()

    for item in items:
        item_key, item_value = key(item), value(item)
        if item_key not in d:
            d[item_key] = []
        d[item_key].append(item_value)

    return d


def dgroupby_set(
        items: Iterable[T],
        key: Callable[[T], K],
        value: Callable[[T], V]
) -> Dict[K, Set[V]]:
    d: Dict[K, Set[V]] = dict()

    for item in items:
        item_key, item_value = key(item), value(item)
        if item_key not in d:
            d[item_key] = set()
        d[item_key].add(item_value)

    return d


def dgroupby_pairs(items: Iterable[Tuple[K, V]]) -> Dict[K, List[V]]:
    d: Dict[K, List[V]] = dict()

    for item_key, item_value in items:
        if item_key not in d:
            d[item_key] = []
        d[item_key].append(item_value)

    return d


def dgroupby_pairs_set(items: Iterable[Tuple[K, V]]) -> Dict[K, Set[V]]:
    d: Dict[K, Set[V]] = dict()

    for item_key, item_value in items:
        if item_key not in d:
            d[item_key] = set()
        d[item_key].add(item_value)

    return d


def count(items: Iterable) -> int:
    return sum(1 for _ in items)


def nextn(g: Iterator[T], n: int) -> Iterable[T]:
    for _ in range(n):
        yield next(g)


def timeit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {round(end-start, 4)} seconds")
        return result
    return wrapper


def zip1(items: Iterable[T], wrap: bool = False) -> Iterable[Tuple[T, T]]:
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


def diffs(items: Iterable[T]) -> Iterable[T]:
    return (b - a for a, b in zip1(items))


def slidingw(items: Iterable[T], size: int, wrap: bool = False) -> Iterable[Tuple[T, ...]]:
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


def minmax(values: Iterable[T], key: Callable[[T], K] = None) -> Tuple[T, T]:
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


def maxk(values: Iterable[T], key: Callable[[T], V]) -> Tuple[T, V]:
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


def mink(values: Iterable[T], key: Callable[[T], V]) -> Tuple[T, V]:
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


def min_all(values: Iterable[T], key: Callable[[T], V] = None) -> List[T]:
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


def picking(items: Iterable[T]) -> Iterable[Tuple[T, List[T]]]:
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
    for k in range(len(items)):
        yield items[k], items[:k]+items[k+1:]


def following(items: Iterable[T]) -> Iterable[Tuple[T, List[T]]]:
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
    for k in range(len(items)):
        yield items[k], items[k+1:]


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
        for ss in subsequences(items[1:]):
            yield items[:1] + ss
            yield ss
    else:
        yield items


def powerset(items: Iterable[T]) -> Iterable[Tuple[T, ...]]:
    """
    >>> list(powerset([1, 2, 3]))
    [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
    """
    s = list(items)
    return chain.from_iterable(
        combinations(s, r)
        for r in range(len(s) + 1)
    )

def ilog(
        items: Iterable[T],
        format: Callable[[int, T], str] = None,
        every: int = 1
) -> Iterable[T]:
    for index, item in enumerate(items):
        if index % every == 0:
            if format:
                print(format(index, item))
            else:
                print('>', index, item)
        yield item


def product(numbers, start=1):
    """
    >>> product(range(1, 5))
    24
    >>> product([4, 7, 10])
    280
    >>> product([2])
    2
    >>> product([10, 0, 8])
    0
    >>> product([1.4, 1.2, 1.6])
    2.688
    """
    prod = start
    for number in numbers:
        prod *= number
    return prod


def constrained(value, min_value, max_value):
    if value < min_value:
        return min_value
    elif max_value < value:
        return max_value
    else:
        return value


def until_repeat(g: Generator[T, None, None]) -> Generator[T, None, T]:
    seen: Set[T] = set()
    for state in g:
        if state not in seen:
            seen.add(state)
            yield state
        else:
            return state


def count_ones(bs: bytes) -> int:
    return sum(bin(b).count('1') for b in bs)


def create_logger(debug: bool = False) -> Callable[[Any], None]:
    if debug:
        def log(o):
            print(o)
        return log
    else:
        def nolog(o):
            pass
        return nolog


def parse_line(line: str, pattern: str) -> Tuple[str, ...]:
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


def _parse_line_fixes(line: str, *fixes: str) -> Tuple[str, ...]:
    assert len(fixes) >= 2

    results = []

    for f1, f2 in slidingw(fixes, 2):
        assert line.startswith(f1)
        line = line[len(f1):]
        if f2:
            pos2 = line.index(f2)
            results.append(line[:pos2])
            line = line[pos2:]
        else:
            results.append(line)
            line = ''

    assert line == fixes[-1], f"{line!r} != {fixes[-1]!r}"
    return tuple(results)


def strip_line(line: str, prefix: str, suffix: str) -> str:
    """
    >>> strip_line("What is love?", "What is ", "?")
    'love'
    """
    return single_value(_parse_line_fixes(line, prefix, suffix))


def memoized(func):
    func._memoized_cache = dict()

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        key = tuple(args), tuple(sorted(kwargs.items()))
        if key in func._memoized_cache:
            return func._memoized_cache[key]
        else:
            result = func(*args, **kwargs)
            func._memoized_cache[key] = result
            return result

    return wrapped


# reading order -> y matters more than x
def ro(pos: Tuple[int, int]) -> Tuple[int, int]:
    x, y = pos
    return y, x


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


def line_groups(lines: Iterable[str]) -> Iterable[List[str]]:
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


def eprint(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)
