import itertools
from typing import Any
from typing import Callable
from typing import Generator
from typing import Iterable
from typing import Sized
from typing import TypeVar

from common.utils import some

T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')


NotSet = object()


def first(items: Iterable[T], default: T = NotSet) -> T:  # type: ignore
    """
        >>> first(x for x in range(40, 100) if x % 13 == 9)
        48
        >>> first("hello!")
        'h'
        >>> first((x for x in range(10) if x % 11 == 10))
        Traceback (most recent call last):
        ...
        ValueError: first() arg is an empty sequence
        >>> first((x for x in range(10) if x % 11 == 10), -1)
        -1
    """
    first_item = next(iter(items), default)

    if first_item is NotSet:
        raise ValueError("first() arg is an empty sequence")

    return first_item


def last(items: Iterable[T], default: T = NotSet) -> T:  # type: ignore
    """
        >>> last(x for x in range(100) if x % 3 == x % 5)
        92
        >>> last("hello!")
        '!'
        >>> last((x for x in range(10) if x % 11 == 10))
        Traceback (most recent call last):
        ...
        ValueError: last() arg is an empty sequence
        >>> last((x for x in range(10) if x % 11 == 10), default=-1)
        -1
    """
    last_item = default
    for item in items:
        last_item = item

    if last_item is NotSet:
        raise ValueError("last() arg is an empty sequence")

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


def exhaust(gen: Generator[Any, Any, T]) -> T:
    try:
        while True:
            next(gen)
    except StopIteration as exc:
        return exc.value


def dgroupby(
        items: Iterable[T],
        key: Callable[[T], K],
        value: Callable[[T], V]
) -> dict[K, list[V]]:
    d: dict[K, list[V]] = {}

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
) -> dict[K, set[V]]:
    d: dict[K, set[V]] = {}

    for item in items:
        item_key, item_value = key(item), value(item)
        if item_key not in d:
            d[item_key] = set()
        d[item_key].add(item_value)

    return d


def dgroupby_pairs(items: Iterable[tuple[K, V]]) -> dict[K, list[V]]:
    d: dict[K, list[V]] = {}

    for item_key, item_value in items:
        if item_key not in d:
            d[item_key] = []
        d[item_key].append(item_value)

    return d


def dgroupby_pairs_set(items: Iterable[tuple[K, V]]) -> dict[K, set[V]]:
    d: dict[K, set[V]] = {}

    for item_key, item_value in items:
        if item_key not in d:
            d[item_key] = set()
        d[item_key].add(item_value)

    return d


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
    matching_values: list[V] = []
    nonmatching_values: list[V] = []

    for value in values:
        (matching_values if predicate(value) else nonmatching_values).append(value)

    return matching_values, nonmatching_values


def ilen(items: Iterable) -> int:
    return sum(1 for _ in items)


def ifind(values: Iterable[T], sub: Iterable[T]) -> int:
    """
        >>> ifind([1, 1, 1, 1, 2, 1, 1, 2, 3, 1, 1, 2, 1, 2, 3], (1, 2, 3))
        6
        >>> ifind((0, 5, 3, 5, 4, 2, 1, 8), [5, 4])
        3
        >>> ifind((0, 5, 3, 5, 4, 2, 1, 8), [9, 4])
        -1
        >>> from itertools import count
        >>> ifind((x * x for x in count(0)), [100, 121, 144])
        10
    """

    sub_list = list(sub)
    matched_count = 0
    for pos, value in enumerate(values):
        if value == sub_list[matched_count]:
            matched_count += 1
        elif value == sub_list[0]:
            matched_count = 1
        else:
            matched_count = 0
        if matched_count == len(sub_list):
            return pos - matched_count + 1
    else:
        return -1


def zip1(items: Iterable[T], wrap: bool = False) -> Iterable[tuple[T, T]]:
    """
        >>> list(zip1([1, 2, 3, 4]))
        [(1, 2), (2, 3), (3, 4)]
        >>> list(zip1([1, 2, 3, 4], wrap=True))
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
        yield some(last_item), some(first_item)


def slidingw(items: Iterable[T], size: int, wrap: bool = False) -> Iterable[tuple[T, ...]]:
    """
        >>> list(slidingw([1, 2, 3, 4], 2))
        [(1, 2), (2, 3), (3, 4)]
        >>> list(slidingw([1, 2, 3, 4, 5], 3))
        [(1, 2, 3), (2, 3, 4), (3, 4, 5)]
        >>> list(slidingw([1, 2, 3], 3))
        [(1, 2, 3)]
        >>> list(slidingw([1, 2, 3], 4))
        []
        >>> list(slidingw([], 1))
        []

        >>> list(slidingw([1, 2, 3, 4], 2, wrap=True))
        [(1, 2), (2, 3), (3, 4), (4, 1)]
        >>> list(slidingw([1, 2, 3, 4, 5], 3, wrap=True))
        [(1, 2, 3), (2, 3, 4), (3, 4, 5), (4, 5, 1), (5, 1, 2)]
        >>> list(slidingw([1, 2, 3], 3, wrap=True))
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


def chunks(
    values: Iterable[T],
    chunk_size: int,
    include_leftover: bool = True
) -> Iterable[list[T]]:
    """
        >>> list(chunks(range(10), chunk_size=3))
        [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
        >>> list(chunks(range(10), chunk_size=3, include_leftover=False))
        [[0, 1, 2], [3, 4, 5], [6, 7, 8]]
    """

    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1")

    current_chunk = []
    for value in values:
        current_chunk.append(value)
        if len(current_chunk) >= chunk_size:
            yield current_chunk
            current_chunk = []

    if include_leftover and current_chunk:
        yield current_chunk


def minmax(values: Iterable[T], key: Callable[[T], K] = None) -> tuple[T, T]:
    """
        >>> minmax([1, 4, 8, 10, 4, -4, 15, -2])
        (-4, 15)
        >>> minmax(["cat", "dog", "antelope"])
        ('antelope', 'dog')
        >>> minmax(["cat", "dog", "antelope"], key=len)
        ('cat', 'antelope')
        >>> minmax([4, 4, 4])
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
        return some(min_v), some(max_v)
    else:
        raise ValueError("minmax() arg is an empty sequence")


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
        return some(max_v), some(max_k)
    else:
        raise ValueError("maxk() arg is an empty sequence")


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
        return some(min_v), some(min_k)
    else:
        raise ValueError("mink() arg is an empty sequence")


def min_all(values: Iterable[T], key: Callable[[T], V] = None) -> list[T]:
    """
        >>> min_all([1, 2, 3, 1, 2, 3, 1, 2, 3])
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


def max_all(values: Iterable[T], key: Callable[[T], V] = None) -> list[T]:
    """
        >>> max_all([1, 2, 3, 1, 2, 3, 1, 2, 3])
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


def picking(items: Iterable[T]) -> Iterable[tuple[T, list[T]]]:
    """
        >>> list(picking('ABC'))
        [('A', ['B', 'C']), ('B', ['A', 'C']), ('C', ['A', 'B'])]
        >>> list(picking(range(1, 6)))  # doctest: +NORMALIZE_WHITESPACE
        [(1, [2, 3, 4, 5]),
         (2, [1, 3, 4, 5]),
         (3, [1, 2, 4, 5]),
         (4, [1, 2, 3, 5]),
         (5, [1, 2, 3, 4])]
        >>> list(picking([1]))
        [(1, [])]
        >>> list(picking([]))
        []
    """
    items = list(items)
    for k, item in enumerate(items):
        yield item, items[:k]+items[k+1:]


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


def powerset(items: Iterable[T]) -> Iterable[tuple[T, ...]]:
    """
        >>> list(powerset([1, 2, 3]))
        [(), (1,), (2,), (3,), (1, 2), (1, 3), (2, 3), (1, 2, 3)]
    """
    items = list(items)
    return itertools.chain.from_iterable(
        itertools.combinations(items, r)
        for r in range(len(items) + 1)
    )


def first_repeat(values: Iterable[T]) -> T | None:
    """
        >>> first_repeat([1, 3, 5, 4, 6, 2, 3, 7])
        3
        >>> first_repeat('mississippi')
        's'
        >>> first_repeat('abcd') is None
        True
    """
    seen: set[T] = set()

    for value in values:
        if value not in seen:
            seen.add(value)
        else:
            return value

    return None


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


def sorted_dict(items: dict[K, V] | Iterable[tuple[K ,V]]) -> dict[K, V]:
    """
    Can be useful in doctests where you need to have the dict in a deterministic order:

        >>> sorted_dict({'x': 1, 'a': 2, 'y': 3, 'b': 4, 'w':5})
        {'a': 2, 'b': 4, 'w': 5, 'x': 1, 'y': 3}
        >>> sorted_dict([(1, 'x'), (10, 'y'), (5, 'z'), (3, 'q')])
        {1: 'x', 3: 'q', 5: 'z', 10: 'y'}
        >>> sorted_dict([])
        {}
    """

    items_iterable = items.items() if isinstance(items, dict) else items
    return dict(sorted((k, v) for k, v in items_iterable))
