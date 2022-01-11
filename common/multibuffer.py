from typing import Callable
from typing import Iterable
from typing import TypeVar


T = TypeVar('T')


class MultiBuffer:
    """
    Multiple buffers by given criteria.

    For example by length:

        >>> mb = MultiBuffer(len)
        >>> mb.append('dog')
        >>> mb.extend(['cat', 'monkey', 'antelope', 'ox', 'spider'])
        >>> len(mb)
        6

    Give me the shortest:

        >>> mb.pop_min()
        'ox'
        >>> mb.pop_min()
        'cat'
        >>> len(mb)
        4

    Give me the longest:

        >>> mb.pop_max()
        'antelope'
        >>> len(mb)
        3

    Etc ...

        >>> mb.pop_min()
        'dog'
        >>> mb.pop_min()
        'spider'
        >>> len(mb)
        1
        >>> bool(mb)
        True

        >>> mb.pop_min()
        'monkey'
        >>> len(mb)
        0
        >>> bool(mb)
        False
    """
    def __init__(self, scoring: Callable[[T], int], items: Iterable[T] = None):
        self._scoring = scoring
        self._buffers: dict[int, list[T]] = {}
        self._items_count = 0
        if items is not None:
            self.extend(items)

    def __len__(self):
        return self._items_count

    def __bool__(self):
        return bool(len(self))

    def __iter__(self) -> Iterable[tuple[int, T]]:
        return (
            (score, item)
            for score, items in self._buffers.items()
            for item in items
        )

    def max_key(self) -> int:
        return max(self._buffers.keys())

    def min_key(self) -> int:
        return min(self._buffers.keys())

    def pop(self, index: int = -1) -> T:
        return self.pop_max(index)

    def pop_max(self, index: int = -1) -> T:
        return self.pop_by_score(self.max_key(), index)

    def pop_min(self, index: int = -1) -> T:
        return self.pop_by_score(self.min_key(), index)

    def pop_by_score(self, score: int, index: int = -1) -> T:
        buffer = self._buffers[score]
        item = buffer.pop(index)
        if not buffer:
            del self._buffers[score]
        self._items_count -= 1
        return item

    def append(self, item: T):
        score = self._scoring(item)
        if score not in self._buffers:
            self._buffers[score] = []
        self._buffers[score].append(item)
        self._items_count += 1

    def extend(self, items: Iterable[T]):
        for item in items:
            self.append(item)
