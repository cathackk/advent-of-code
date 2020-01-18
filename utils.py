import functools
import time
from typing import Any
from typing import Callable
from typing import Collection
from typing import Dict
from typing import Generator
from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Set
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
    return next(items, default)


def last(items: Iterable[T], default: T = None) -> Optional[T]:
    last_item = default
    for item in items:
        last_item = item
    return last_item


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
        item_key = key(item)
        item_value = value(item)
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
        item_key = key(item)
        item_value = value(item)
        if item_key not in d:
            d[item_key] = set()
        d[item_key].add(item_value)

    return d


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


def minmax(items: Iterable[T], key: Callable[[T], K] = None) -> Tuple[T, T]:
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
    min_item, max_item = None, None
    min_value, max_value = None, None
    any_item = False

    for item in items:
        value = key(item) if key is not None else item
        if min_value is None or value < min_value:
            min_item, min_value = item, value
        if max_value is None or value > max_value:
            max_item, max_value = item, value
        any_item = True

    if any_item:
        return min_item, max_item
    else:
        raise ValueError("minmax() arg is an empty sequence")


def maxk(items: Iterable[T], key: Callable[[T], V]) -> Tuple[T, V]:
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
    max_item = None
    max_value = None
    any_item = False

    for item in items:
        value = key(item)
        if max_value is None or value > max_value:
            max_item, max_value = item, value
        any_item = True

    if any_item:
        return max_item, max_value
    else:
        raise ValueError("maxk() arg is an empty sequence")


def mink(items: Iterable[T], key: Callable[[T], V]) -> Tuple[T, V]:
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
    min_item = None
    min_value = None
    any_item = False

    for item in items:
        value = key(item)
        if min_value is None or value < min_value:
            min_item, min_value = item, value
        any_item = True

    if any_item:
        return min_item, min_value
    else:
        raise ValueError("mink() arg is an empty sequence")


def min_all(items: Iterable[T], key: Callable[[T], V] = None) -> List[T]:
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
    min_value = None
    min_items = None

    for item in items:
        value = key(item) if key else item
        if min_value is None or value < min_value:
            min_value = value
            min_items = [item]
        elif value == min_value:
            min_items.append(item)

    if min_items is not None:
        return min_items
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


def single_value(items: Collection[T]) -> T:
    if len(items) == 1:
        return next(iter(items))
    elif len(items) == 0:
        raise ValueError("empty items")
    else:
        raise ValueError(f"more than one item ({len(items)})")


def only_value(items: Iterable[T]) -> T:
    distincts = set(items)
    if len(distincts) == 1:
        return distincts.pop()
    elif len(distincts) == 0:
        raise ValueError("empty items")
    else:
        raise ValueError(f"more than one distinct value: {distincts}")


def parse_line(line: str, *fixes: str) -> Tuple[str, ...]:
    """
    >>> parse_line("Dogs have four paws.", "Dogs have ", " paws.")
    ('four',)
    >>> parse_line("Humans have two eyes and four limbs.", "Humans have ", " eyes and ", " limbs.")
    ('two', 'four')
    >>> parse_line("1,2:3x4\\n", '', ',', ':', 'x', '\\n')
    ('1', '2', '3', '4')
    """
    if len(fixes) < 2:
        raise ValueError(f"must supply at least two fixes (was {len(fixes)})")

    results = []

    for f1, f2 in slidingw(fixes, 2):
        assert line.startswith(f1)
        line = line[len(f1):]
        pos2 = line.index(f2)
        results.append(line[:pos2])
        line = line[pos2:]

    assert line == fixes[-1]
    return tuple(results)


def strip_line(line: str, prefix: str, suffix: str) -> str:
    """
    >>> strip_line("What is love?", "What is ", "?")
    'love'
    """
    return parse_line(line, prefix, suffix)[0]


